"""coverage_report.py — generate <feature>_coverage_report.md by diffing
scope.md (PM contract) vs nav_graph.json + dumps (capture reality).

Outputs a Markdown file at <feature_root>/<feature>/<feature>_coverage_report.md
with frontmatter ready for graph ingestion + body sections for PM review.

Usage:
    python coverage_report.py <feature>
    python coverage_report.py <feature> --json     # machine-readable to stdout
    python coverage_report.py <feature> --no-write # preview only, don't save md

Exit codes:
    0 = generated successfully (regardless of pass/fail audit)
    1 = error (no scope, no nav_graph, etc.)
    2 = audit FAIL (gaps exist) — useful for CI gating
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from re_spec_mobile.nav_graph import load as load_graph
from re_spec_mobile.profile_loader import Profile, load_profile
from re_spec_mobile.scope_loader import Cluster, Scope, load_scope


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _capture_to_screen_anchor(feature: str, capture_label: str) -> str:
    """Convention: capture label `screen_07_change_reminder` →
    anchor `<feature>/screen/change_reminder`. Strip `screen_NN_` prefix."""
    name = capture_label
    if name.startswith("screen_"):
        name = name[7:]
        # strip leading digits + underscore
        i = 0
        while i < len(name) and name[i].isdigit():
            i += 1
        if i < len(name) and name[i] == "_":
            i += 1
        name = name[i:]
    # strip trailing _b/_c (scroll segments)
    while name.endswith(("_b", "_c", "_d", "_e", "_f", "_g")):
        name = name[:-2]
    return f"{feature}/screen/{name}"


def _build_anchor_to_capture(graph_data: dict, feature: str) -> dict[str, list[str]]:
    """Reverse map: screen_anchor → list of capture labels representing it."""
    out: dict[str, list[str]] = {}
    for sid, s in graph_data.get("screens", {}).items():
        for cap in s.get("captures", []) or []:
            anchor = _capture_to_screen_anchor(feature, cap)
            out.setdefault(anchor, []).append(cap)
    return out


def diff_scope_vs_captures(scope: Scope, profile: Profile) -> dict[str, Any]:
    """Core diff. Returns dict with captured / gaps / drift / metrics."""
    g = load_graph(scope.feature, profile=profile)
    anchor_to_captures = _build_anchor_to_capture(g.data, scope.feature)
    all_captured_anchors = set(anchor_to_captures.keys())

    must_visit = scope.all_must_visit()
    optional_visit = scope.all_optional_visit()
    out_of_scope = scope.out_of_scope_anchors()
    declared_anchors = must_visit | optional_visit | out_of_scope

    # captured matches scope
    captured_in_scope = all_captured_anchors & (must_visit | optional_visit)
    must_captured = must_visit & all_captured_anchors
    optional_captured = optional_visit & all_captured_anchors

    # gaps: must_visit not captured
    gaps = sorted(must_visit - all_captured_anchors)

    # drift: captured but not declared
    drift_anchors = sorted(all_captured_anchors - declared_anchors)

    # for each cluster, compute completion %
    per_cluster: list[dict[str, Any]] = []
    for c in scope.clusters:
        if not c.in_scope:
            per_cluster.append({
                "cluster_id": c.id, "cluster_name": c.name, "in_scope": False,
                "reason": c.reason,
            })
            continue
        c_must = set(c.must_visit)
        c_opt = set(c.optional_visit)
        per_cluster.append({
            "cluster_id": c.id, "cluster_name": c.name, "in_scope": True,
            "must_total": len(c_must),
            "must_captured": len(c_must & all_captured_anchors),
            "optional_total": len(c_opt),
            "optional_captured": len(c_opt & all_captured_anchors),
            "missing": sorted(c_must - all_captured_anchors),
        })

    return {
        "feature": scope.feature,
        "scope_version": scope.scope_version,
        "captured": {
            "total": len(all_captured_anchors),
            "in_scope": sorted(captured_in_scope),
            "must_captured": sorted(must_captured),
            "optional_captured": sorted(optional_captured),
        },
        "gaps": [
            {"anchor": a, "reason": "not yet captured"} for a in gaps
        ],
        "drift": [
            {
                "anchor_inferred": a,
                "captures": anchor_to_captures.get(a, []),
                "cluster_guess": "",
                "reason_guess": "captured but not in scope clusters",
            }
            for a in drift_anchors
        ],
        "per_cluster": per_cluster,
        "metrics": {
            "must_total": len(must_visit),
            "must_captured": len(must_captured),
            "optional_total": len(optional_visit),
            "optional_captured": len(optional_captured),
            "drift_count": len(drift_anchors),
            "gap_count": len(gaps),
            "unknowns_unresolved": len(scope.unresolved_questions()),
        },
    }


def render_markdown(diff: dict[str, Any], scope: Scope, profile: Profile) -> str:
    """Render the full coverage_report.md (frontmatter + body)."""
    feature = diff["feature"]
    metrics = diff["metrics"]
    feature_title = feature.replace("_", " ").title()

    # ----- frontmatter -----
    fm_lines: list[str] = [
        "---",
        f"feature: {feature}",
        "layer: coverage_report",
        f"anchor: {feature}/coverage_report/root",
        f"title: {profile.app_name} — {feature_title} Coverage Report",
        f"last_updated: '{datetime.now(timezone.utc).date().isoformat()}'",
        f"generated_at: {_now_iso()}",
        "generated_by: coverage_report.py v1",
        f"scope_version: {scope.scope_version}",
        "status: draft",
        "captured:",
        f"  count: {diff['captured']['total']}",
        "  anchors:",
    ]
    for a in diff["captured"]["in_scope"]:
        fm_lines.append(f"    - {a}")
    fm_lines.append("gaps:")
    for g in diff["gaps"]:
        fm_lines.append(f"  - anchor: {g['anchor']}")
        fm_lines.append(f"    reason: \"{g['reason']}\"")
    fm_lines.append("drift:")
    for d in diff["drift"]:
        fm_lines.append(f"  - anchor_inferred: {d['anchor_inferred']}")
        fm_lines.append(f"    captures: {d['captures']}")
        fm_lines.append(f"    cluster_guess: \"{d['cluster_guess']}\"")
        fm_lines.append(f"    reason_guess: \"{d['reason_guess']}\"")
    fm_lines.append("unknowns_resolved: []")
    fm_lines.append("decisions: []")
    fm_lines.append("related:")
    fm_lines.append(f"  - {feature}/scope/root")
    fm_lines.append(f"  - {feature}/observations/root")
    fm_lines.append("---")

    # ----- body -----
    body: list[str] = [
        "",
        f"# {profile.app_name} — {feature_title} Coverage Report",
        "",
        "> **Auto-generated by `coverage_report.py`.** Diff giữa scope.md (PM contract)",
        "> vs nav_graph.json + dumps thực tế. PM review để quyết định re-capture vs revise scope.",
        "> Update `status: sign_off_pass` (cho phép spec-writer chạy) hoặc `sign_off_fail`.",
        "",
        "---",
        "",
        "## 1. Summary",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| Must-visit captured | {metrics['must_captured']} / {metrics['must_total']} |",
        f"| Optional captured | {metrics['optional_captured']} / {metrics['optional_total']} |",
        f"| Drift (out-of-scope captures) | {metrics['drift_count']} |",
        f"| Gap (in-scope misses) | {metrics['gap_count']} |",
        f"| Unknowns unresolved | {metrics['unknowns_unresolved']} |",
        "",
        "**Status**: _(PM fills after review)_ — `sign_off_pass` or `sign_off_fail`.",
        "",
        "---",
        "",
        "## 2. Captured (matches scope)",
        "",
    ]
    if diff["captured"]["in_scope"]:
        body.append("| Anchor | In-scope cluster |")
        body.append("|---|---|")
        cluster_of = {}
        for c in scope.clusters:
            for a in c.must_visit + c.optional_visit:
                cluster_of[a] = c.name
        for a in diff["captured"]["in_scope"]:
            body.append(f"| `{a}` | {cluster_of.get(a, '_(unknown)_')} |")
    else:
        body.append("_(none)_")
    body.append("")
    body.append("---")
    body.append("")

    # gaps
    body.append("## 3. Gaps (in scope but missing)")
    body.append("")
    if diff["gaps"]:
        for i, g in enumerate(diff["gaps"], start=1):
            body.append(f"### Gap {i}: `{g['anchor']}`")
            body.append("")
            body.append(f"- **Reason**: {g['reason']}")
            body.append("- **Suggested fix**: _(eg. re-run app-explorer with extended timeout)_")
            body.append("- **PM decision**: _(fill in: re-capture / revise scope / accept partial)_")
            body.append("")
    else:
        body.append("_(none — all must_visit captured ✅)_")
        body.append("")
    body.append("---")
    body.append("")

    # drift
    body.append("## 4. Drift (captured but not in scope)")
    body.append("")
    if diff["drift"]:
        for i, d in enumerate(diff["drift"], start=1):
            body.append(f"### Drift {i}: `{d['anchor_inferred']}`")
            body.append("")
            body.append(f"- **Captures**: `{', '.join(d['captures'])}`")
            body.append(f"- **Cluster guess**: {d['cluster_guess'] or '_(none)_'}")
            body.append(f"- **Reason guess**: {d['reason_guess']}")
            body.append("- **PM decision**: _(fill in: add to scope cluster X / drop / move to out_of_scope)_")
            body.append("")
    else:
        body.append("_(none — capture stayed in scope ✅)_")
        body.append("")
    body.append("---")
    body.append("")

    # PM review
    body.append("## 5. PM review")
    body.append("")
    unresolved = scope.unresolved_questions()
    if unresolved:
        body.append("### Open scope questions still unresolved")
        body.append("")
        for q in unresolved:
            body.append(f"- `{q.id}`: {q.summary}")
        body.append("")
    body.append("### Action items after review")
    body.append("")
    body.append("_(PM fill — these go into `decisions:` frontmatter list)_")
    body.append("")
    body.append("- [ ] _(action 1)_")
    body.append("- [ ] _(action 2)_")
    body.append("")
    body.append("### Final status")
    body.append("")
    body.append("After PM completes review, update frontmatter `status` to `sign_off_pass` or `sign_off_fail`.")
    body.append("If `sign_off_fail`, orchestrator loops back to capture phase with the gap list.")
    body.append("")

    return "\n".join(fm_lines) + "\n" + "\n".join(body)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("feature")
    ap.add_argument("--json", action="store_true", help="print diff as JSON to stdout (no md write)")
    ap.add_argument("--no-write", action="store_true", help="preview md only, don't write file")
    args = ap.parse_args()

    profile = load_profile()
    try:
        scope = load_scope(args.feature, profile=profile)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    diff = diff_scope_vs_captures(scope, profile)

    if args.json:
        print(json.dumps(diff, indent=2, ensure_ascii=False))
        return 0 if diff["metrics"]["gap_count"] == 0 else 2

    md = render_markdown(diff, scope, profile)

    if args.no_write:
        print(md)
    else:
        out_path = profile.feature_dir(args.feature) / f"{args.feature}_coverage_report.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        m = diff["metrics"]
        print(f"Wrote {out_path}")
        print(f"Summary: must={m['must_captured']}/{m['must_total']}  "
              f"opt={m['optional_captured']}/{m['optional_total']}  "
              f"gap={m['gap_count']}  drift={m['drift_count']}  unknowns={m['unknowns_unresolved']}")

    return 0 if diff["metrics"]["gap_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
