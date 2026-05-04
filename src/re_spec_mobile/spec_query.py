"""spec_query.py — query the spec graph at <profile.graph_root>/.

Commands:
    show <anchor>                       node detail + edges + file:line
    list <type> [--feature F]           list nodes of type
    feature <feature>                   summary of a feature (counts + children)
    reuses [<reuse_key>]                components sharing reuse_key
    path <from> <to> [--depth N]        BFS shortest path via navigates_to
    acceptance <feature>                list criteria of a feature
    search <query>                      substring match on anchor+label
    stats                               graph totals

Flags:
    --json        machine-readable output
    --limit N     cap list output

Run `python build_graph.py` first to refresh the graph.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from re_spec_mobile.profile_loader import Profile, load_profile


# ---------- graph loading ---------------------------------------------------


def load_graph(profile: Profile | None = None) -> tuple[dict[str, dict], list[dict], dict]:
    p = profile or load_profile()
    nodes_doc = json.loads((p.graph_root / "nodes.json").read_text(encoding="utf-8"))
    edges_doc = json.loads((p.graph_root / "edges.json").read_text(encoding="utf-8"))
    index_doc = json.loads((p.graph_root / "index.json").read_text(encoding="utf-8"))
    nodes = {n["anchor"]: n for n in nodes_doc["nodes"]}
    return nodes, edges_doc["edges"], index_doc["anchors"]


def outgoing(edges: list[dict], src: str) -> list[dict]:
    return [e for e in edges if e["from"] == src]


def incoming(edges: list[dict], dst: str) -> list[dict]:
    return [e for e in edges if e["to"] == dst]


# ---------- output ----------------------------------------------------------


def emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                print(_fmt_node(item))
            else:
                print(item)
    elif isinstance(payload, dict):
        _print_dict(payload)
    else:
        print(payload)


def _fmt_node(n: dict) -> str:
    anchor = n.get("anchor") or n.get("from") or ""
    t = n.get("type") or ""
    label = n.get("label") or ""
    file_ = n.get("file") or ""
    line = n.get("line")
    loc = f"{file_}:{line}" if file_ and line else file_ or ""
    return f"{anchor:<50} [{t:<11}] {label}  {loc}"


def _print_dict(d: dict, indent: int = 0) -> None:
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{pad}{k} ({len(v)}):")
            for item in v:
                if isinstance(item, dict):
                    print(f"{pad}  - {_fmt_node(item)}")
                else:
                    print(f"{pad}  - {item}")
        elif isinstance(v, dict):
            print(f"{pad}{k}:")
            _print_dict(v, indent + 1)
        else:
            print(f"{pad}{k}: {v}")


# ---------- commands --------------------------------------------------------


def cmd_show(nodes, edges, anchor: str) -> dict:
    n = nodes.get(anchor)
    if not n:
        sys.exit(f"anchor not found: {anchor}")
    outs = [{"type": e["type"], "to": e["to"], **e.get("attrs", {})} for e in outgoing(edges, anchor)]
    ins = [{"type": e["type"], "from": e["from"], **e.get("attrs", {})} for e in incoming(edges, anchor)]
    return {"node": n, "outgoing": outs, "incoming": ins}


def cmd_list(nodes, kind: str, feature: str | None, limit: int) -> list[dict]:
    out = [n for n in nodes.values() if n.get("type") == kind]
    if feature:
        out = [n for n in out if n.get("feature") == feature]
    out.sort(key=lambda n: n["anchor"])
    return out[:limit]


def cmd_feature(nodes, edges, feature: str) -> dict:
    members = [n for n in nodes.values() if n.get("feature") == feature]
    by_type: dict[str, list[dict]] = defaultdict(list)
    for n in members:
        by_type[n.get("type", "?")].append(n)
    for lst in by_type.values():
        lst.sort(key=lambda n: n["anchor"])
    return {
        "feature": feature,
        "total": len(members),
        "counts": {t: len(v) for t, v in sorted(by_type.items())},
        "children": {t: v for t, v in sorted(by_type.items())},
    }


def cmd_reuses(nodes, edges, reuse_key: str | None) -> dict:
    comps = [n for n in nodes.values() if n.get("type") == "component" and n.get("reuse_key")]
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in comps:
        groups[c["reuse_key"]].append(c)
    if reuse_key:
        groups = {reuse_key: groups.get(reuse_key, [])}
    reuse_edges = [e for e in edges if e["type"] == "reuses_component"]
    return {
        "by_reuse_key": {k: sorted(v, key=lambda n: n["anchor"]) for k, v in groups.items()},
        "reuse_edges": reuse_edges,
    }


def cmd_path(edges, src: str, dst: str, max_depth: int) -> list[str] | None:
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for e in edges:
        if e["type"] == "navigates_to":
            adj[e["from"]].append((e["to"], e.get("attrs", {}).get("trigger", "")))
    seen = {src: None}
    q = deque([(src, 0)])
    while q:
        cur, depth = q.popleft()
        if cur == dst:
            path: list[str] = []
            x: str | None = cur
            while x is not None:
                path.append(x)
                x = seen[x]
            return list(reversed(path))
        if depth >= max_depth:
            continue
        for nxt, _ in adj.get(cur, []):
            if nxt not in seen:
                seen[nxt] = cur
                q.append((nxt, depth + 1))
    return None


def cmd_acceptance(nodes, feature: str) -> list[dict]:
    crits = [n for n in nodes.values() if n.get("type") == "criterion" and n.get("feature") == feature]
    crits.sort(key=lambda n: n["anchor"])
    return crits


def cmd_search(nodes, query: str, limit: int) -> list[dict]:
    q = query.lower()
    matches = [
        n for n in nodes.values()
        if q in n["anchor"].lower() or q in (n.get("label") or "").lower()
    ]
    matches.sort(key=lambda n: (0 if q in n["anchor"].lower() else 1, n["anchor"]))
    return matches[:limit]


def cmd_stats(nodes, edges) -> dict:
    by_type: dict[str, int] = defaultdict(int)
    for n in nodes.values():
        by_type[n.get("type", "?")] += 1
    edge_types: dict[str, int] = defaultdict(int)
    for e in edges:
        edge_types[e["type"]] += 1
    return {
        "nodes": len(nodes), "edges": len(edges),
        "node_types": dict(sorted(by_type.items())),
        "edge_types": dict(sorted(edge_types.items())),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=500)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show"); s.add_argument("anchor")
    s = sub.add_parser("list"); s.add_argument("kind"); s.add_argument("--feature")
    s = sub.add_parser("feature"); s.add_argument("name")
    s = sub.add_parser("reuses"); s.add_argument("key", nargs="?")
    s = sub.add_parser("path"); s.add_argument("src"); s.add_argument("dst"); s.add_argument("--depth", type=int, default=8)
    s = sub.add_parser("acceptance"); s.add_argument("feature")
    s = sub.add_parser("search"); s.add_argument("query")
    sub.add_parser("stats")

    args = ap.parse_args()

    profile = load_profile()
    if not profile.graph_root.exists():
        sys.exit(f"no graph at {profile.graph_root} — run `python build_graph.py` first")
    nodes, edges, _index = load_graph(profile)

    if args.cmd == "show":
        emit(cmd_show(nodes, edges, args.anchor), args.json)
    elif args.cmd == "list":
        emit(cmd_list(nodes, args.kind, args.feature, args.limit), args.json)
    elif args.cmd == "feature":
        emit(cmd_feature(nodes, edges, args.name), args.json)
    elif args.cmd == "reuses":
        emit(cmd_reuses(nodes, edges, args.key), args.json)
    elif args.cmd == "path":
        path = cmd_path(edges, args.src, args.dst, args.depth)
        if path is None:
            sys.exit(f"no path (depth ≤ {args.depth})")
        emit({"path": path, "length": len(path) - 1}, args.json)
    elif args.cmd == "acceptance":
        emit(cmd_acceptance(nodes, args.feature), args.json)
    elif args.cmd == "search":
        emit(cmd_search(nodes, args.query, args.limit), args.json)
    elif args.cmd == "stats":
        emit(cmd_stats(nodes, edges), args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
