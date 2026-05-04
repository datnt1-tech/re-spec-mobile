"""coverage_check — find clickable elements that were never tapped.

For each JSON dump under <profile.dumps_root>/<feature>/, walk the a11y tree,
collect every clickable node, and cross-reference with the feature's nav_graph.

A clickable is **covered** if EITHER:
  - its centre coord (midpoint of bounds) matches a `tap:(X,Y)` action recorded
    in any edge (within ±30 px tolerance), OR
  - its label appears verbatim (substring, case-insensitive) in any edge label.

Blocklist (from profile) filters destructive / test-unsafe targets BEFORE
coverage check, so they never appear in the MISS report.

Optional scope-aware mode (`--scope`): also load `<feature>_scope.md` and
report MISS items grouped by `must_visit`, `optional`, `out_of_scope`,
`unscoped` so the agent + PM can prioritize.

Usage:
    python coverage_check.py <feature>
    python coverage_check.py <feature> --json
    python coverage_check.py <feature> --scope         # bucket by scope status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from re_spec_mobile.nav_graph import load as load_graph
from re_spec_mobile.profile_loader import load_profile
from re_spec_mobile.scope_loader import load_scope, Scope


_TAP_RE = re.compile(r"tap:?\(\s*(\d+)\s*,\s*(\d+)\s*\)")
_BOUNDS_TOLERANCE_PX = 30


def _iter_clickables(nodes: Iterable[dict[str, Any]]):
    for n in nodes:
        if n.get("clickable"):
            yield n
        kids = n.get("children") or []
        if kids:
            yield from _iter_clickables(kids)


def _label_of(node: dict[str, Any]) -> str:
    text = (node.get("text") or "").strip()
    desc = (node.get("content_description") or node.get("content-desc") or "").strip()
    rid_full = node.get("resource_id") or node.get("resource-id") or ""
    rid = rid_full.split("/")[-1]
    return text or desc or rid or ""


def _bounds_dict(node: dict[str, Any]) -> dict[str, int] | None:
    b = node.get("bounds")
    if isinstance(b, dict):
        return {"left": int(b.get("left", 0)), "top": int(b.get("top", 0)),
                "right": int(b.get("right", 0)), "bottom": int(b.get("bottom", 0))}
    if isinstance(b, (list, tuple)) and len(b) == 4:
        return {"left": int(b[0]), "top": int(b[1]), "right": int(b[2]), "bottom": int(b[3])}
    return None


def _bounds_str(node: dict[str, Any]) -> str:
    b = _bounds_dict(node)
    if not b:
        return ""
    return f'[{b["left"]},{b["top"]}][{b["right"]},{b["bottom"]}]'


def _centre(b: dict[str, int]) -> tuple[int, int]:
    return ((b["left"] + b["right"]) // 2, (b["top"] + b["bottom"]) // 2)


def _extract_tap_coords(edges: list[dict[str, Any]]) -> list[tuple[int, int]]:
    coords: list[tuple[int, int]] = []
    for e in edges:
        for fld in ("action", "label"):
            v = e.get(fld) or ""
            for m in _TAP_RE.finditer(v):
                coords.append((int(m.group(1)), int(m.group(2))))
    return coords


def _extract_edge_labels(edges: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for e in edges:
        for fld in ("action", "label"):
            v = (e.get(fld) or "").strip()
            if v:
                labels.append(v.lower())
    return labels


def _is_covered(
    clickable_label: str,
    clickable_centre: tuple[int, int] | None,
    tap_coords: list[tuple[int, int]],
    edge_labels_lower: list[str],
) -> tuple[bool, str]:
    """Returns (covered, reason). reason explains WHY covered (for debug)."""
    if clickable_centre is not None:
        cx, cy = clickable_centre
        for tx, ty in tap_coords:
            if abs(tx - cx) <= _BOUNDS_TOLERANCE_PX and abs(ty - cy) <= _BOUNDS_TOLERANCE_PX:
                return True, f"tap@({tx},{ty}) within ±{_BOUNDS_TOLERANCE_PX}px of centre"
    if clickable_label:
        ll = clickable_label.lower()
        # require full label appears as substring — much stricter than word-token match
        for el in edge_labels_lower:
            if ll in el:
                return True, f"label substring match in edge: {el[:50]!r}"
    return False, ""


def _scope_status_of(label: str, anchor_hint: str, scope) -> str:
    """Best-effort: classify a clickable's owning anchor as must_visit/optional/out_of_scope/unscoped.
    `anchor_hint` is the screen anchor where this clickable lives (not the clickable itself)."""
    if scope is None:
        return "unscoped"
    if anchor_hint in scope.all_must_visit():
        return "must_visit_screen"
    if anchor_hint in scope.all_optional_visit():
        return "optional_screen"
    if anchor_hint in scope.out_of_scope_anchors():
        return "out_of_scope_screen"
    return "unscoped"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--json", action="store_true", help="emit machine-readable report")
    ap.add_argument("--scope", action="store_true",
                    help="bucket MISS items by scope status (requires <feature>_scope.md)")
    args = ap.parse_args()

    try:
        profile = load_profile()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    blocklist_re = profile.blocklist_re
    g = load_graph(args.feature, profile=profile)
    edges = g.data.get("edges", [])
    tap_coords = _extract_tap_coords(edges)
    edge_labels = _extract_edge_labels(edges)

    scope = None
    if args.scope and load_scope is not None:
        try:
            scope = load_scope(args.feature, profile=profile)
        except FileNotFoundError:
            print(f"WARN: --scope flag set but no scope file; continuing without bucketing", file=sys.stderr)
        except Exception as e:
            print(f"WARN: scope load failed: {e}", file=sys.stderr)

    dumps_dir = profile.feature_dumps_dir(args.feature)
    if not dumps_dir.exists():
        print(f"No dumps dir at {dumps_dir}", file=sys.stderr)
        return 1

    # capture_label -> screen anchor mapping (best-effort)
    label_to_screen_anchor: dict[str, str] = {}
    for sid, s in g.data.get("screens", {}).items():
        for cap in s.get("captures", []) or []:
            # screen anchor isn't directly stored in nav_graph (declared in observations frontmatter)
            # so we just key by capture label; scope bucketing uses naming convention
            label_to_screen_anchor[cap] = f"{args.feature}/screen/{cap.replace('screen_', '').lstrip('0123456789_')}"

    report: dict[str, list[dict[str, Any]]] = {}
    bucketed: dict[str, list[dict[str, Any]]] = {
        "must_visit_screen": [], "optional_screen": [],
        "out_of_scope_screen": [], "unscoped": [],
    }

    for jpath in sorted(dumps_dir.glob("*.json")):
        state = json.loads(jpath.read_text(encoding="utf-8"))
        tree = state.get("a11y_tree", []) or []
        seen_here: list[dict[str, Any]] = []

        screen_anchor_hint = label_to_screen_anchor.get(jpath.stem, "")

        for node in _iter_clickables(tree):
            label = _label_of(node)
            if not label:
                continue
            if len(label) > 60:
                continue  # likely body content, not a button label
            if blocklist_re.search(label):
                continue

            bounds_d = _bounds_dict(node)
            centre = _centre(bounds_d) if bounds_d else None
            covered, _why = _is_covered(label, centre, tap_coords, edge_labels)
            if covered:
                continue

            item = {
                "label": label,
                "bounds": _bounds_str(node),
                "centre": list(centre) if centre else None,
                "class": node.get("class_name") or node.get("class") or "",
                "resource_id": node.get("resource_id") or node.get("resource-id") or "",
                "in_screen": jpath.stem,
                "screen_anchor_hint": screen_anchor_hint,
            }
            if scope is not None:
                bucket = _scope_status_of(label, screen_anchor_hint, scope)
                item["scope_status"] = bucket
                bucketed[bucket].append(item)
            seen_here.append(item)

        if seen_here:
            report[jpath.stem] = seen_here

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    if args.json:
        out: dict[str, Any] = {
            "feature": args.feature,
            "tap_coords_recorded": len(tap_coords),
            "edge_labels_recorded": len(edge_labels),
            "miss_by_screen": report,
        }
        if scope is not None:
            out["miss_by_scope"] = bucketed
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    if not report:
        print(f"[OK] all clickables in feature '{args.feature}' are covered by the nav graph")
        if scope is not None:
            unmet = scope.all_must_visit() - {label_to_screen_anchor.get(c, "") for s in g.data.get("screens", {}).values() for c in s.get("captures", [])}
            if unmet:
                print(f"[SCOPE WARN] {len(unmet)} must_visit screens have no capture yet:")
                for a in sorted(unmet):
                    print(f"  - {a}")
        return 0

    total = sum(len(v) for v in report.values())
    print(f"[MISS] {total} clickable(s) not yet explored across {len(report)} capture(s):\n")
    print(f"  (matched against {len(tap_coords)} tap coords + {len(edge_labels)} edge labels)\n")

    if scope is not None:
        print("=== Bucketed by scope status ===")
        for bucket_name in ["must_visit_screen", "optional_screen", "out_of_scope_screen", "unscoped"]:
            items = bucketed[bucket_name]
            if not items:
                continue
            print(f"\n[{bucket_name}] {len(items)} item(s):")
            for it in items[:20]:
                rid = f'  (#{it["resource_id"].split("/")[-1]})' if it["resource_id"] else ""
                print(f"  - {it['label']!r}  in:{it['in_screen']}  {it['bounds']}{rid}")
            if len(items) > 20:
                print(f"  ... +{len(items) - 20} more")
        print()

    print("=== By capture ===")
    for cap, items in report.items():
        print(f"\n[{cap}]")
        for it in items:
            rid = f'  (#{it["resource_id"].split("/")[-1]})' if it["resource_id"] else ""
            print(f"  - {it['label']!r}  {it['bounds']}  {it['class']}{rid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
