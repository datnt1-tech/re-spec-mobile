"""render_nav — emit a Mermaid flowchart from a feature's nav_graph.json.

Usage:
    python render_nav.py <feature>                 # prints Mermaid to stdout
    python render_nav.py <feature> -o graph.md     # writes fenced markdown block
    python render_nav.py <feature> --style LR      # TD (default) | LR | TB | RL | BT

Clustering: screens with `block` set are grouped into Mermaid subgraphs.
Screens without a block land in an implicit "Unassigned" cluster.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from re_spec_mobile.nav_graph import load as load_graph
from re_spec_mobile.profile_loader import load_profile


_SANITIZE = re.compile(r"[^A-Za-z0-9_]")


def _nid(screen_id: str) -> str:
    return "s_" + _SANITIZE.sub("_", screen_id)[:16]


def _esc_label(s: str) -> str:
    return '"' + s.replace('"', "'").replace("\n", " ") + '"'


def render(feature: str, style: str = "TD") -> str:
    profile = load_profile()
    g = load_graph(feature, profile=profile)
    screens = g.data.get("screens", {})
    edges = g.data.get("edges", [])

    lines: list[str] = []
    lines.append(f"flowchart {style}")
    lines.append(f"  %% Feature: {feature}   ({len(screens)} screens, {len(edges)} edges)")

    by_block: dict[str, list[dict]] = {}
    for s in screens.values():
        key = s.get("block") or "_"
        by_block.setdefault(key, []).append(s)

    sorted_keys = sorted(by_block.keys(), key=lambda k: (k == "_", k))

    for key in sorted_keys:
        cluster_label = f"Block {key}" if key != "_" else "Unassigned"
        if len(by_block) > 1:
            lines.append(f'  subgraph blk_{_SANITIZE.sub("_", key)}["{cluster_label}"]')
            lines.append("    direction TB")
        for s in by_block[key]:
            node_label = s.get("label") or s["id"]
            lines.append(f'    {_nid(s["id"])}[{_esc_label(node_label)}]')
        if len(by_block) > 1:
            lines.append("  end")

    for e in edges:
        frm = _nid(e["from"])
        to = _nid(e["to"])
        action = e.get("label") or e.get("action") or ""
        if action:
            lines.append(f'  {frm} -- {_esc_label(action)} --> {to}')
        else:
            lines.append(f"  {frm} --> {to}")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("-o", "--out", help="write fenced markdown to this path instead of stdout")
    ap.add_argument("--style", default="TD", choices=["TD", "LR", "TB", "RL", "BT"])
    args = ap.parse_args()

    body = render(args.feature, style=args.style)

    if args.out:
        fenced = "```mermaid\n" + body + "```\n"
        Path(args.out).write_text(fenced, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
