"""build_graph.py — parse SPEC_SCHEMA frontmatter from all spec files and emit
<profile.graph_root>/{nodes.json, edges.json, index.json}.

Usage:
    python build_graph.py             # writes graph
    python build_graph.py --stats     # print node/edge counts
    python build_graph.py --check     # exit 1 if graph has broken anchor refs

Idempotent: deterministic output (sorted), safe to rerun.

Node types: feature, layer, screen, block, component, api, data_model,
            criterion, invariant, question, state
Edge types: belongs_to_feature, belongs_to_block, navigates_to,
            renders_component, reuses_component, returns_model, has_state,
            has_layer, references
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from re_spec_mobile.profile_loader import Profile, load_profile


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def load_frontmatter(path: Path, project_root: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"[yaml error] {path.relative_to(project_root)}: {e}", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        return None
    data["__file"] = str(path.relative_to(project_root))
    return data


def discover_specs(profile: Profile) -> list[Path]:
    paths: list[Path] = []
    if profile.feature_root.exists():
        for md in profile.feature_root.rglob("*.md"):
            if md.name.endswith("_nav.md"):
                continue
            paths.append(md)
    legacy = profile.spec_root / "observations.md"
    if legacy.exists():
        paths.append(legacy)
    return sorted(paths)


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.broken_refs: list[tuple[str, str, str]] = []

    def add_node(self, anchor: str, **attrs: Any) -> None:
        if anchor in self.nodes:
            existing = self.nodes[anchor]
            for k, v in attrs.items():
                if v is not None and existing.get(k) in (None, ""):
                    existing[k] = v
            return
        self.nodes[anchor] = {"anchor": anchor, **{k: v for k, v in attrs.items() if v is not None}}

    def add_edge(self, src: str, dst: str, etype: str, **attrs: Any) -> None:
        edge = {"from": src, "to": dst, "type": etype}
        if attrs:
            edge["attrs"] = attrs
        self.edges.append(edge)

    def validate_refs(self) -> None:
        known = set(self.nodes)
        for e in self.edges:
            if e["to"] not in known:
                self.broken_refs.append((e["from"], e["type"], e["to"]))


def build(graph: Graph, docs: list[dict[str, Any]]) -> None:
    # Pass 1: feature + layer + nested entity nodes.
    for fm in docs:
        feature = fm.get("feature")
        layer = fm.get("layer")
        root_anchor = fm.get("anchor")
        file_ = fm["__file"]
        if not feature or not layer or not root_anchor:
            continue

        feature_anchor = f"{feature}/feature/root"
        graph.add_node(feature_anchor, type="feature", feature=feature, label=feature)

        graph.add_node(
            root_anchor, type="layer", layer=layer, feature=feature, file=file_,
            title=fm.get("title"), status=fm.get("status"),
            last_updated=str(fm.get("last_updated", "")),
            app_version=fm.get("app_version"),
            scope_version=fm.get("scope_version"),
            signed_off_by=fm.get("signed_off_by"),
            signed_off_at=str(fm.get("signed_off_at", "")),
            generated_at=str(fm.get("generated_at", "")),
        )
        graph.add_edge(feature_anchor, root_anchor, "has_layer", layer=layer)

        # ---- scope layer: clusters + must_visit/optional/out_of_scope edges ----
        for cl in fm.get("clusters") or []:
            cid = cl.get("id")
            if not cid:
                continue
            graph.add_node(
                cid, type="cluster", feature=feature, label=cl.get("name"),
                in_scope=bool(cl.get("in_scope", True)),
                file=file_, line=cl.get("section_line"),
                reason=cl.get("reason"),
            )
            graph.add_edge(feature_anchor, cid, "belongs_to_feature")
            for screen_anchor in cl.get("must_visit") or []:
                graph.add_edge(screen_anchor, cid, "belongs_to_cluster", required="must")
            for screen_anchor in cl.get("optional_visit") or []:
                graph.add_edge(screen_anchor, cid, "belongs_to_cluster", required="optional")
            if not cl.get("in_scope", True):
                graph.add_edge(feature_anchor, cid, "out_of_scope",
                               reason=cl.get("reason"))

        # ---- coverage_report layer: gap + drift edges + verifies_scope ----
        if layer == "coverage_report":
            for gap in fm.get("gaps") or []:
                a = gap.get("anchor")
                if a:
                    graph.add_edge(root_anchor, a, "gap", reason=gap.get("reason"))
            for d in fm.get("drift") or []:
                a = d.get("anchor_inferred") or d.get("anchor")
                if a:
                    graph.add_edge(root_anchor, a, "drift",
                                   captures=d.get("captures"),
                                   cluster_guess=d.get("cluster_guess"))
            scope_root = f"{feature}/scope/root"
            graph.add_edge(root_anchor, scope_root, "verifies_scope",
                           scope_version=fm.get("scope_version"))

        for s in fm.get("screens") or []:
            a = s.get("anchor")
            if not a:
                continue
            graph.add_node(
                a, type="screen", feature=feature, label=s.get("label") or s.get("name"),
                file=file_, line=s.get("section_line"), activity=s.get("activity"),
                hash=s.get("hash"), capture_file=s.get("capture_file"), dump_file=s.get("dump_file"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")

        for b in fm.get("blocks") or []:
            a = b.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="block", feature=feature, label=b.get("name"),
                letter=b.get("letter"), file=file_, line=b.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")
            for screen_anchor in b.get("screens") or []:
                graph.add_edge(screen_anchor, a, "belongs_to_block")

        for c in fm.get("components") or []:
            a = c.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="component", feature=feature, label=c.get("name"),
                reuse_key=c.get("reuse_key"), file=file_, line=c.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")
            for screen_anchor in c.get("screens") or []:
                graph.add_edge(screen_anchor, a, "renders_component")

        for api in fm.get("apis") or []:
            a = api.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="api", feature=feature,
                label=f"{api.get('method','?')} {api.get('path','?')}",
                method=api.get("method"), path=api.get("path"),
                file=file_, line=api.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")
            if ret := api.get("returns"):
                graph.add_edge(a, ret, "returns_model")

        for dm in fm.get("data_models") or []:
            a = dm.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="data_model", feature=feature, label=dm.get("name"),
                file=file_, line=dm.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")

        for cr in fm.get("criteria") or []:
            a = cr.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="criterion", feature=feature, label=cr.get("summary"),
                file=file_, line=cr.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")

        for iv in fm.get("invariants") or []:
            a = iv.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="invariant", feature=feature, file=file_,
                line=iv.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")

        for q in fm.get("questions") or []:
            a = q.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="question", feature=feature, file=file_,
                line=q.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "belongs_to_feature")

        for st in fm.get("states") or []:
            a = st.get("id")
            if not a:
                continue
            graph.add_node(
                a, type="state", feature=feature, file=file_,
                line=st.get("section_line"),
            )
            graph.add_edge(feature_anchor, a, "has_state")

    # Pass 2: nav_edges, reuses, related (cross-references).
    for fm in docs:
        feature = fm.get("feature")
        root_anchor = fm.get("anchor")
        if not feature or not root_anchor:
            continue

        for ne in fm.get("nav_edges") or []:
            src, dst = ne.get("from"), ne.get("to")
            if not src or not dst:
                continue
            graph.add_edge(
                src, dst, "navigates_to", trigger=ne.get("trigger"),
                block=ne.get("block"), external=bool(ne.get("external", False)),
            )

        for reuse in fm.get("reuses") or []:
            comp = reuse.get("component")
            if not comp:
                continue
            for used_by in reuse.get("used_by") or []:
                graph.add_edge(used_by, comp, "reuses_component")

        for ref in fm.get("related") or []:
            graph.add_edge(root_anchor, ref, "references")


def emit(graph: Graph, profile: Profile) -> None:
    profile.graph_root.mkdir(parents=True, exist_ok=True)

    nodes_sorted = sorted(graph.nodes.values(), key=lambda n: n["anchor"])
    edges_sorted = sorted(graph.edges, key=lambda e: (e["from"], e["to"], e["type"]))

    index = {
        n["anchor"]: {
            "type": n.get("type"), "feature": n.get("feature"),
            "file": n.get("file"), "line": n.get("line"), "label": n.get("label"),
        }
        for n in nodes_sorted
    }

    (profile.graph_root / "nodes.json").write_text(
        json.dumps({"version": 1, "nodes": nodes_sorted}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (profile.graph_root / "edges.json").write_text(
        json.dumps({"version": 1, "edges": edges_sorted}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (profile.graph_root / "index.json").write_text(
        json.dumps({"version": 1, "anchors": index}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if broken refs")
    args = ap.parse_args()

    profile = load_profile()
    paths = discover_specs(profile)
    docs = [fm for p in paths if (fm := load_frontmatter(p, profile.project_root))]

    graph = Graph()
    build(graph, docs)
    graph.validate_refs()
    emit(graph, profile)

    if args.stats or args.check:
        by_type: dict[str, int] = {}
        for n in graph.nodes.values():
            by_type[n.get("type", "?")] = by_type.get(n.get("type", "?"), 0) + 1
        edge_by_type: dict[str, int] = {}
        for e in graph.edges:
            edge_by_type[e["type"]] = edge_by_type.get(e["type"], 0) + 1

        print(f"nodes: {len(graph.nodes)}")
        for t, c in sorted(by_type.items()):
            print(f"  {t:<12} {c}")
        print(f"edges: {len(graph.edges)}")
        for t, c in sorted(edge_by_type.items()):
            print(f"  {t:<20} {c}")
        print(f"broken refs: {len(graph.broken_refs)}")
        for src, field, dst in graph.broken_refs[:20]:
            print(f"  {src}  --{field}-->  {dst}   (target missing)")
        if len(graph.broken_refs) > 20:
            print(f"  ... +{len(graph.broken_refs) - 20} more")

    if args.check and graph.broken_refs:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
