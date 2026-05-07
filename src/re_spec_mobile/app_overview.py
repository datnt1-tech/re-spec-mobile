"""app_overview.py — sinh + refresh `spec/app_overview.md` (Layer 5 app-level).

Doc tổng app-level platform-agnostic, dùng được cho cả iOS rebuild. 10 section
auto-generated từ spec graph + 5 section prose do PM/designer điền.

CLI:
    re-spec-app-overview                   # render to spec/app_overview.md
    re-spec-app-overview --output <path>   # custom output
    re-spec-app-overview --check           # lint only, exit 1 nếu có forbidden token
    re-spec-app-overview --section <key>   # debug: render 1 section ra stdout

Idempotent re-render — auto section bọc trong HTML marker:

    <!-- AUTO:KEY START -->
    ... auto-generated content ...
    <!-- AUTO:KEY END -->

Re-render chỉ thay phần giữa marker; prose ngoài marker preserve. File mới hoàn
toàn → render full skeleton kèm marker.

Linter: cảnh báo (warn) khi gặp token framework-specific (Compose, Kotlin,
Activity, SwiftUI, ...). KHÔNG block — designer note "iOS-only ..." là OK.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from re_spec_mobile.profile_loader import Profile, load_profile
from re_spec_mobile.spec_query import load_graph


# ---------------- Marker primitives ----------------------------------------

MARKER_START = "<!-- AUTO:{key} START -->"
MARKER_END = "<!-- AUTO:{key} END -->"

# Order = display order in the file.
SECTION_KEYS = [
    "IDENTITY",
    "INVENTORY",
    "SITEMAP",
    "CROSS_NAV",
    "REUSE_MAP",
    "API_SURFACE",
    "DATA_MODELS",
    "INVARIANTS",
    "OPEN_QUESTIONS",
    "ACCEPTANCE",
]


def marker_block(key: str, body: str) -> str:
    return f"{MARKER_START.format(key=key)}\n{body.rstrip()}\n{MARKER_END.format(key=key)}"


def replace_marker(text: str, key: str, new_body: str) -> tuple[str, bool]:
    """Replace content between AUTO markers. Returns (new_text, found)."""
    start = MARKER_START.format(key=key)
    end = MARKER_END.format(key=key)
    pattern = re.compile(
        re.escape(start) + r"\n.*?\n" + re.escape(end),
        re.DOTALL,
    )
    if not pattern.search(text):
        return text, False
    return pattern.sub(marker_block(key, new_body), text, count=1), True


# ---------------- Linter ---------------------------------------------------

# Token framework-specific. Match whole-word, case-sensitive (case-sensitive
# vì lowercase "activity" = từ tiếng Anh thông thường, "Activity" mới là Android).
FORBIDDEN_TOKENS: list[str] = [
    # Android
    r"\bCompose\b",
    r"\bJetpack\b",
    r"\b@Composable\b",
    r"\bActivity\b",
    r"\bFragment\b",
    r"\bfindViewById\b",
    r"\bR\.id\b",
    r"\bKotlin\b",
    r"\bAndroidView\b",
    r"\bEspresso\b",
    r"\bRecyclerView\b",
    r"\bViewModel\b",
    # iOS
    r"\bSwiftUI\b",
    r"\bUIView\b",
    r"\bUIViewController\b",
    r"\bStoryboard\b",
    r"\bUIKit\b",
    r"\bXCTest\b",
    r"\bSwift\b",
    r"\bObjective-C\b",
    # Cross
    r"\bKMM\b",
    r"\bXML layout\b",
]

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _strip_code_fences(text: str) -> str:
    return CODE_FENCE_RE.sub("", text)


def lint(text: str) -> list[tuple[int, str, str]]:
    """Return list of (line_no, token, line_text) — bỏ qua token nằm trong code fence."""
    stripped = _strip_code_fences(text)
    out: list[tuple[int, str, str]] = []
    for ln_no, line in enumerate(stripped.splitlines(), start=1):
        for pat in FORBIDDEN_TOKENS:
            m = re.search(pat, line)
            if m:
                out.append((ln_no, m.group(0), line.strip()))
    return out


# ---------------- Section generators (auto) --------------------------------


def _filter_nodes(nodes: dict[str, dict], type_: str) -> list[dict]:
    return [n for n in nodes.values() if n.get("type") == type_]


def _group_by_feature(items: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for n in items:
        out[n.get("feature") or "(unknown)"].append(n)
    return dict(sorted(out.items()))


def section_identity(profile: Profile, _nodes, _edges, _index) -> str:
    rows = [
        ("App", profile.app_name),
        ("Package (Android)", f"`{profile.package}`"),
        ("Locale chính", profile.locale),
        ("Viewport capture", f"{profile.viewport[0]}×{profile.viewport[1]} px"),
        ("Stack ghi nhận", profile.stack),
        ("Profile path", str(profile.profile_path.relative_to(profile.project_root))),
    ]
    body = "| Field | Value |\n|---|---|\n"
    body += "\n".join(f"| **{k}** | {v} |" for k, v in rows)
    return body


def section_inventory(profile: Profile, nodes, edges, index) -> str:
    """Bảng feature × counts."""
    features = _filter_nodes(nodes, "feature")
    if not features:
        return "_(không có feature nào — chạy `re-spec-build-graph` trước.)_"

    counts: dict[str, dict[str, int]] = {}
    for n in nodes.values():
        f = n.get("feature")
        t = n.get("type")
        if not f or not t or t in ("feature", "layer"):
            continue
        counts.setdefault(f, defaultdict(int))[t] += 1

    head = "| Feature | Screens | Blocks | Components | APIs | Data models | Invariants | Open Q | AC |"
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines = [head, sep]
    for f in sorted(counts):
        c = counts[f]
        lines.append(
            f"| `{f}` | {c.get('screen', 0)} | {c.get('block', 0)} | "
            f"{c.get('component', 0)} | {c.get('api', 0)} | "
            f"{c.get('data_model', 0)} | {c.get('invariant', 0)} | "
            f"{c.get('question', 0)} | {c.get('criterion', 0)} |"
        )
    return "\n".join(lines)


def section_sitemap(profile: Profile, nodes, edges, index) -> str:
    """Liệt kê mọi screen, group by feature."""
    screens = _filter_nodes(nodes, "screen")
    if not screens:
        return "_(0 screen)_"
    grouped = _group_by_feature(screens)
    out: list[str] = []
    for feat, scrs in grouped.items():
        out.append(f"### {feat}\n")
        out.append("| Anchor | Label | Hash | Capture |")
        out.append("|---|---|---|---|")
        for s in sorted(scrs, key=lambda n: n.get("anchor", "")):
            anchor = s.get("anchor", "")
            label = (s.get("label") or "").replace("|", "\\|")
            hsh = (s.get("hash") or "")[:12]
            cap = s.get("capture_file") or ""
            out.append(f"| `{anchor}` | {label} | `{hsh}` | `{cap}` |")
        out.append("")
    return "\n".join(out).rstrip()


def section_cross_nav(profile: Profile, nodes, edges, index) -> str:
    """Mermaid diagram chỉ các edge external=true (cross-feature)."""
    nav = [
        e for e in edges
        if e.get("type") == "navigates_to"
        and (e.get("attrs") or {}).get("external")
    ]
    if not nav:
        return "_(không có cross-feature edge nào — `nav_edges[].external: true` chưa được khai trong feature spec.)_"

    # Aggregate src_feature → dst_feature (label = trigger)
    cross: list[tuple[str, str, str]] = []
    for e in nav:
        src_feat = (nodes.get(e["from"]) or {}).get("feature") or "?"
        dst_feat = (nodes.get(e["to"]) or {}).get("feature") or "?"
        if src_feat == dst_feat:
            continue
        trig = (e.get("attrs") or {}).get("trigger") or ""
        cross.append((src_feat, dst_feat, trig))

    if not cross:
        return "_(không có edge nào thực sự cross-feature dù external=true.)_"

    lines = ["```mermaid", "flowchart LR"]
    seen_pairs: set[tuple[str, str]] = set()
    for src, dst, trig in sorted(set(cross)):
        if (src, dst) in seen_pairs:
            continue
        seen_pairs.add((src, dst))
        label = trig[:30].replace('"', '')
        if label:
            lines.append(f'    {src} -->|"{label}"| {dst}')
        else:
            lines.append(f"    {src} --> {dst}")
    lines.append("```")
    return "\n".join(lines)


def section_reuse_map(profile: Profile, nodes, edges, index) -> str:
    """Component có cùng reuse_key xuất hiện ở >1 feature → ứng viên design system."""
    components = _filter_nodes(nodes, "component")
    by_key: dict[str, list[dict]] = defaultdict(list)
    for c in components:
        key = c.get("reuse_key")
        if key:
            by_key[key].append(c)

    shared = {
        k: comps for k, comps in by_key.items()
        if len({c.get("feature") for c in comps}) > 1
    }
    if not shared:
        return "_(chưa có component reuse_key nào dùng chéo >1 feature.)_"

    lines = ["| reuse_key | Used by features | Count | Anchors |",
             "|---|---|---:|---|"]
    for key in sorted(shared):
        comps = shared[key]
        feats = sorted({c.get("feature") for c in comps if c.get("feature")})
        anchors = ", ".join(f"`{c.get('anchor')}`" for c in comps[:3])
        if len(comps) > 3:
            anchors += f", … (+{len(comps) - 3})"
        lines.append(f"| `{key}` | {', '.join(feats)} | {len(comps)} | {anchors} |")
    note = (
        "\n\n> **Designer note**: mỗi reuse_key trên là ứng viên cho 1 component "
        "design system thực sự — engineer rebuild 1 lần, parameterise."
    )
    return "\n".join(lines) + note


def section_api_surface(profile: Profile, nodes, edges, index) -> str:
    apis = _filter_nodes(nodes, "api")
    if not apis:
        return "_(0 API endpoint khai báo trong spec.)_"
    lines = ["| Method | Path | Feature | Returns | Anchor |",
             "|---|---|---|---|---|"]
    for a in sorted(apis, key=lambda n: (n.get("feature") or "", n.get("path") or "")):
        method = a.get("method") or "?"
        path = a.get("path") or "?"
        feat = a.get("feature") or "?"
        # find returns_model edge
        ret = next(
            (e["to"] for e in edges if e["from"] == a["anchor"] and e["type"] == "returns_model"),
            "—",
        )
        ret_disp = f"`{ret}`" if ret != "—" else ret
        lines.append(f"| `{method}` | `{path}` | `{feat}` | {ret_disp} | `{a['anchor']}` |")
    return "\n".join(lines)


def section_data_models(profile: Profile, nodes, edges, index) -> str:
    models = _filter_nodes(nodes, "data_model")
    if not models:
        return "_(0 data model khai báo trong spec.)_"
    lines = ["| Anchor | Name | Feature |", "|---|---|---|"]
    for m in sorted(models, key=lambda n: n.get("anchor") or ""):
        lines.append(
            f"| `{m['anchor']}` | {m.get('label') or '?'} | `{m.get('feature') or '?'}` |"
        )
    return "\n".join(lines)


def section_invariants(profile: Profile, nodes, edges, index) -> str:
    invs = _filter_nodes(nodes, "invariant")
    if not invs:
        return "_(0 cross-screen invariant khai báo.)_"
    lines = ["| Anchor | Feature | File:line |", "|---|---|---|"]
    for iv in sorted(invs, key=lambda n: n.get("anchor") or ""):
        loc = f"{iv.get('file') or ''}:{iv.get('line') or ''}".rstrip(":")
        lines.append(f"| `{iv['anchor']}` | `{iv.get('feature') or '?'}` | `{loc}` |")
    return "\n".join(lines)


def section_open_questions(profile: Profile, nodes, edges, index) -> str:
    """List mọi question node chưa resolved (heuristic: không có **PM answer** non-empty trong file)."""
    qs = _filter_nodes(nodes, "question")
    if not qs:
        return "_(0 open question còn lại — toàn bộ spec đã clean.)_"

    PM_ANSWER_RE = re.compile(
        r"\*\*PM answer\*\*:\s*(?P<ans>.+?)(?=\n\n|\n#{1,4}\s|\Z)",
        re.DOTALL,
    )
    ANCHOR_HEADING_RE = re.compile(
        r"^(?P<hashes>#{2,4})\s+(?P<title>.+?)\s*\{#(?P<a>[a-z][a-z0-9_/]+)\}\s*$",
        re.MULTILINE,
    )

    unresolved: list[tuple[str, str, str]] = []
    for q in qs:
        f = q.get("file") or ""
        if not f:
            continue
        path = profile.project_root / f
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Find section under this anchor
        headings = list(ANCHOR_HEADING_RE.finditer(text))
        section = ""
        title = ""
        for i, h in enumerate(headings):
            if h.group("a") != q["anchor"]:
                continue
            title = h.group("title").strip()
            start = h.end()
            stop = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            section = text[start:stop]
            break
        am = PM_ANSWER_RE.search(section)
        ans = (am.group("ans").strip() if am else "")
        if ans and "_(fill in)_" not in ans:
            continue
        unresolved.append((q["anchor"], q.get("feature") or "?", title))

    if not unresolved:
        return "_(mọi question đã được PM answer — clean.)_"
    lines = ["| Anchor | Feature | Question |", "|---|---|---|"]
    for a, f, t in sorted(unresolved):
        t_safe = (t or "").replace("|", "\\|")[:120]
        lines.append(f"| `{a}` | `{f}` | {t_safe} |")
    return "\n".join(lines)


def section_acceptance(profile: Profile, nodes, edges, index) -> str:
    crit = _filter_nodes(nodes, "criterion")
    if not crit:
        return "_(0 acceptance criterion.)_"
    lines = ["| Anchor | Feature | Summary |", "|---|---|---|"]
    for c in sorted(crit, key=lambda n: n.get("anchor") or ""):
        label = (c.get("label") or "").replace("|", "\\|")[:120]
        lines.append(f"| `{c['anchor']}` | `{c.get('feature') or '?'}` | {label} |")
    return "\n".join(lines)


SectionFn = Callable[[Profile, dict, list, dict], str]
SECTION_GENERATORS: dict[str, SectionFn] = {
    "IDENTITY": section_identity,
    "INVENTORY": section_inventory,
    "SITEMAP": section_sitemap,
    "CROSS_NAV": section_cross_nav,
    "REUSE_MAP": section_reuse_map,
    "API_SURFACE": section_api_surface,
    "DATA_MODELS": section_data_models,
    "INVARIANTS": section_invariants,
    "OPEN_QUESTIONS": section_open_questions,
    "ACCEPTANCE": section_acceptance,
}


# ---------------- Skeleton (file mới) --------------------------------------


SKELETON_TEMPLATE = """\
---
layer: app_overview
anchor: app/overview/root
title: {app_name} — App Overview (Platform-Agnostic)
last_updated: '{date_iso}'
generated_at: '{generated_at}'
generator: re-spec-app-overview v1
---

# {app_name} — App Overview

> **Layer 5 / 5 — app-level platform-agnostic spec.** Doc này tổng hợp mọi
> feature thành 1 nguồn truyền đạt sản phẩm dùng cho **cả iOS và Android** (và
> stake-holder không kỹ thuật). KHÔNG nhắc framework cụ thể — designer/PM viết
> prose mô tả pattern abstract.
>
> Section auto-generated bọc trong `<!-- AUTO:KEY START/END -->`. Re-render
> bằng `re-spec-app-overview` chỉ refresh phần auto, prose ngoài marker
> preserve.

---

## 1. App identity

{IDENTITY}

---

## A. Mục tiêu sản phẩm — _(prose, designer/PM viết)_

_(fill in: target user, use case chính, value prop, KPI sản phẩm)_

---

## 2. Feature inventory

{INVENTORY}

---

## 3. Sitemap

{SITEMAP}

---

## 4. Cross-feature navigation

{CROSS_NAV}

---

## B. Navigation model — _(prose)_

_(fill in: tab structure conceptually, modal/sheet pattern, back behavior,
deep-link strategy. Mô tả abstract — không đề cập framework cụ thể.)_

---

## 5. Component reuse map (auto-detect ứng viên design system)

{REUSE_MAP}

---

## C. UX state pattern — _(prose)_

_(fill in: empty state / loading / error / offline / paywall / gating —
quy ước trên toàn app. Vd "Empty state có illustration + 1 primary CTA;
loading dùng skeleton 200ms+, không spinner".)_

---

## 6. API surface

{API_SURFACE}

---

## 7. Data models

{DATA_MODELS}

---

## D. Content / copy rules — _(prose)_

_(fill in: rule cho tone, locale, format ngày/tiền, plural, RTL handling.)_

---

## 8. Cross-feature invariants

{INVARIANTS}

---

## 9. Open questions roll-up

{OPEN_QUESTIONS}

---

## 10. Acceptance criteria roll-up

{ACCEPTANCE}

---

## E. Cross-cutting design decisions — _(prose)_

_(fill in: quyết định kiến trúc cấp app — vd "auth dùng SSO duy nhất",
"audio mini-player persist khi nav cross feature", "theme switch instant
không reload"...)_
"""


def render_skeleton(profile: Profile, nodes, edges, index) -> str:
    """Generate a fresh app_overview.md from scratch with every AUTO marker
    populated from current graph state."""
    fields: dict[str, str] = {
        "app_name": profile.app_name,
        "date_iso": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    for key in SECTION_KEYS:
        body = SECTION_GENERATORS[key](profile, nodes, edges, index)
        fields[key] = marker_block(key, body)
    return SKELETON_TEMPLATE.format(**fields)


def refresh_existing(text: str, profile: Profile, nodes, edges, index) -> tuple[str, list[str]]:
    """Replace AUTO marker contents in an existing file. Returns (new_text, missing_keys)."""
    new_text = text
    missing: list[str] = []
    for key in SECTION_KEYS:
        body = SECTION_GENERATORS[key](profile, nodes, edges, index)
        new_text, found = replace_marker(new_text, key, body)
        if not found:
            missing.append(key)
    # also bump last_updated in frontmatter if present
    new_text = re.sub(
        r"^last_updated:.*$",
        f"last_updated: '{datetime.now(timezone.utc).strftime('%Y-%m-%d')}'",
        new_text,
        count=1,
        flags=re.MULTILINE,
    )
    new_text = re.sub(
        r"^generated_at:.*$",
        f"generated_at: '{datetime.now(timezone.utc).isoformat(timespec='seconds')}'",
        new_text,
        count=1,
        flags=re.MULTILINE,
    )
    return new_text, missing


# ---------------- Render orchestrator --------------------------------------


def render(profile: Profile, output: Path) -> dict[str, Any]:
    nodes, edges, index = load_graph(profile)
    if output.exists():
        existing = output.read_text(encoding="utf-8")
        new_text, missing_keys = refresh_existing(existing, profile, nodes, edges, index)
        mode = "refresh"
    else:
        new_text = render_skeleton(profile, nodes, edges, index)
        missing_keys = []
        mode = "create"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(new_text, encoding="utf-8")

    warnings = lint(new_text)
    return {
        "mode": mode,
        "output": str(output.relative_to(profile.project_root)),
        "missing_markers": missing_keys,
        "lint_warnings": [
            {"line": ln, "token": tok, "context": ctx} for ln, tok, ctx in warnings
        ],
        "graph_stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "features": len([n for n in nodes.values() if n.get("type") == "feature"]),
        },
    }


# ---------------- CLI ------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="Render/refresh spec/app_overview.md.")
    ap.add_argument("--output", type=Path,
                    help="output path (default: <spec_root>/app_overview.md)")
    ap.add_argument("--check", action="store_true",
                    help="lint only — exit 1 nếu có forbidden token")
    ap.add_argument("--section", choices=list(SECTION_GENERATORS.keys()),
                    help="debug: render 1 section ra stdout, không ghi file")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 nếu lint warning (mặc định warn-only)")
    args = ap.parse_args()

    try:
        profile = load_profile()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.section:
        nodes, edges, index = load_graph(profile)
        body = SECTION_GENERATORS[args.section](profile, nodes, edges, index)
        print(body)
        return 0

    output = args.output or (profile.spec_root / "app_overview.md")

    if args.check:
        if not output.exists():
            print(f"NO_OVERVIEW {output}", file=sys.stderr)
            return 1
        warnings = lint(output.read_text(encoding="utf-8"))
        if not warnings:
            print(f"OK {output} (0 forbidden token)")
            return 0
        print(f"WARN {output}: {len(warnings)} forbidden token(s)")
        for ln, tok, ctx in warnings[:30]:
            print(f"  L{ln}: {tok!r} — {ctx[:100]}")
        if len(warnings) > 30:
            print(f"  ... +{len(warnings) - 30} more")
        return 1

    try:
        result = render(profile, output)
    except FileNotFoundError as e:
        print(f"ERROR: {e}\n(chạy `re-spec-build-graph` trước.)", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["lint_warnings"]:
        print(f"\n[lint] {len(result['lint_warnings'])} warning(s) — "
              "doc này nên platform-agnostic (xem `--check` để rà).",
              file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
