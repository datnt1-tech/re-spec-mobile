"""pm_doc_lint.py — linter cho PM-facing markdown doc (KHÔNG bind structure
9-section của feature_spec). Apply technique từ workflow re-spec-mobile vào doc
PM bất kỳ: anchor ID convention, RFC 2119 verb modal, AC measurable, forbidden
platform token, Open Question có PM answer, frontmatter sanity.

CLI:
    re-spec-pm-doc-lint <file_or_dir>           # lint, warn-only (exit 0)
    re-spec-pm-doc-lint <path> --strict         # exit 1 nếu có warning
    re-spec-pm-doc-lint <path> --check ANCHOR   # chỉ chạy 1 check
    re-spec-pm-doc-lint <path> --json           # output JSON cho CI

6 check (mặc định chạy hết):

    ANCHOR    — anchor ID format `<feature>/<type>/<slug>` đúng convention
    RFC2119   — section behavior/rule/policy phải có MUST / SHOULD / MAY
    AC        — Acceptance criteria phải có số + unit (testable)
    PLATFORM  — forbidden token Compose / Kotlin / SwiftUI / Activity... ngoài code fence
    OPENQ     — Open Question phải có **PM answer** non-empty
    FM        — frontmatter (nếu có) phải có status / version / last_updated

Output format `<file>:<line>: [<check>] <severity>: <message> | <context>`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


CHECK_IDS = ("ANCHOR", "RFC2119", "AC", "PLATFORM", "OPENQ", "FM")
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"


@dataclass
class Finding:
    file: str
    line: int
    check: str
    severity: str
    message: str
    context: str = ""


# ---------------- Shared regex --------------------------------------------

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)
ANCHOR_INLINE_RE = re.compile(r"\{#(?P<anchor>[^}]+)\}")
HEADING_RE = re.compile(
    r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*(?:\{#(?P<a>[^}]+)\})?\s*$",
    re.MULTILINE,
)


def _strip_code_fences(text: str) -> str:
    return CODE_FENCE_RE.sub("", text)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


# ---------------- Check 1: ANCHOR ID format -------------------------------

ANCHOR_FORMAT_RE = re.compile(r"^[a-z][a-z0-9_]*(/[a-z][a-z0-9_]*)+$")
ANCHOR_KNOWN_TYPES = {
    "feature", "screen", "block", "component", "api", "data_model",
    "criterion", "invariant", "question", "state", "cluster", "conversation",
    "turn", "rule", "policy", "metric", "flow", "scope", "observations",
    "implementation", "coverage_report", "overview", "stuck",
}


def check_anchor_format(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []
    for m in ANCHOR_INLINE_RE.finditer(text):
        anchor = m.group("anchor")
        ln = _line_of(text, m.start())
        if not ANCHOR_FORMAT_RE.match(anchor):
            out.append(Finding(
                file=file, line=ln, check="ANCHOR", severity=SEVERITY_WARN,
                message=f"anchor `{anchor}` không match format `<feature>/<type>/<slug>` (lowercase snake_case, slash-separated)",
                context=f"{{#{anchor}}}",
            ))
            continue
        parts = anchor.split("/")
        if len(parts) >= 2 and parts[1] not in ANCHOR_KNOWN_TYPES:
            out.append(Finding(
                file=file, line=ln, check="ANCHOR", severity=SEVERITY_WARN,
                message=f"anchor type `{parts[1]}` không phải known type (xem ANCHOR_KNOWN_TYPES). Có thể OK nếu cố ý mở rộng.",
                context=f"{{#{anchor}}}",
            ))
    return out


# ---------------- Check 2: RFC 2119 modal in rule/behavior sections -------

RULE_SECTION_KEYWORDS = (
    "behavior", "behaviour", "rule", "policy", "guideline", "guidelines",
    "quy tắc", "quy định", "ràng buộc", "chính sách",
)
RFC_2119_MODALS = (
    r"\bMUST NOT\b", r"\bMUST\b", r"\bSHOULD NOT\b", r"\bSHOULD\b",
    r"\bMAY\b", r"\bSHALL NOT\b", r"\bSHALL\b", r"\bREQUIRED\b",
)
RFC_MODAL_RE = re.compile("|".join(RFC_2119_MODALS))


def _section_bounds(headings: list[re.Match], i: int, text_len: int) -> tuple[int, int]:
    """Return (start, end) char offsets of section i — body between heading i
    and the next heading of equal-or-higher level."""
    h = headings[i]
    cur_level = len(h.group("hashes"))
    start = h.end()
    end = text_len
    for j in range(i + 1, len(headings)):
        next_level = len(headings[j].group("hashes"))
        if next_level <= cur_level:
            end = headings[j].start()
            break
    return start, end


def check_rfc2119(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []
    stripped = _strip_code_fences(text)
    headings = list(HEADING_RE.finditer(stripped))
    for i, h in enumerate(headings):
        title = h.group("title").lower()
        if not any(kw in title for kw in RULE_SECTION_KEYWORDS):
            continue
        start, end = _section_bounds(headings, i, len(stripped))
        section_body = stripped[start:end]
        if not section_body.strip():
            continue
        if not RFC_MODAL_RE.search(section_body):
            ln = _line_of(text, h.start())
            out.append(Finding(
                file=file, line=ln, check="RFC2119", severity=SEVERITY_WARN,
                message=f"section behavior/rule '{h.group('title').strip()}' nhưng không có verb modal RFC 2119 (MUST / MUST NOT / SHOULD / MAY) — rule không formal sẽ ambiguous",
                context=h.group(0).strip()[:80],
            ))
    return out


# ---------------- Check 3: AC measurable ----------------------------------

# AC bullet: line bắt đầu bằng `- AC-NN` hoặc trong section Acceptance criteria
AC_BULLET_RE = re.compile(
    r"^\s*[-*+]\s*(?:\*\*)?\s*AC[-_]?\d+(?:\s*\{#[^}]+\})?\s*[:\-]?\s*(?P<body>.+)$",
    re.MULTILINE,
)
# Token số có ngữ nghĩa measurable
MEASURABLE_RE = re.compile(
    r"\d+\s*(?:%|ms|s|sec|seconds|phút|minute|minutes|hour|h|chars|char|kí tự|ký tự|"
    r"px|kb|mb|count|lần|times)|"
    r"[≤≥<>]=?\s*\d+|"
    r"\d+\s*[/]\s*\d+|"  # 95% style: "95/100"
    r"p\d{2,3}\b",  # p50, p95
    re.IGNORECASE,
)
AC_SECTION_KEYWORDS = ("acceptance criteria", "acceptance criterion", "tiêu chí nghiệm thu", "tiêu chí pass")


def check_ac_measurable(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []

    # 1. Direct AC-NN bullets anywhere
    for m in AC_BULLET_RE.finditer(text):
        body = m.group("body").strip()
        if not MEASURABLE_RE.search(body):
            ln = _line_of(text, m.start())
            out.append(Finding(
                file=file, line=ln, check="AC", severity=SEVERITY_WARN,
                message=f"AC không có số + đơn vị đo được (vd `≤ 280 chars`, `< 3s`, `≥ 95%`, `p95`) — không testable",
                context=body[:90],
            ))

    # 2. Bullets trong section heading có "Acceptance criteria" — same check
    headings = list(HEADING_RE.finditer(text))
    for i, h in enumerate(headings):
        title = h.group("title").lower()
        if not any(kw in title for kw in AC_SECTION_KEYWORDS):
            continue
        start, end = _section_bounds(headings, i, len(text))
        section = text[start:end]
        for line in section.splitlines():
            if not re.match(r"^\s*[-*+]\s+", line):
                continue
            if AC_BULLET_RE.match(line):
                continue  # đã catch ở (1)
            stripped_line = re.sub(r"^\s*[-*+]\s+", "", line).strip()
            if len(stripped_line) < 10:
                continue  # bullet quá ngắn — skip noise
            if not MEASURABLE_RE.search(stripped_line):
                # Find absolute line number
                ln_offset = section.index(line)
                ln = _line_of(text, start + ln_offset)
                out.append(Finding(
                    file=file, line=ln, check="AC", severity=SEVERITY_WARN,
                    message=f"bullet trong Acceptance criteria không có số + đơn vị đo được — không testable",
                    context=stripped_line[:90],
                ))
    return out


# ---------------- Check 4: Forbidden platform token -----------------------

FORBIDDEN_TOKENS: list[str] = [
    # Android
    r"\bCompose\b", r"\bJetpack\b", r"\b@Composable\b", r"\bActivity\b",
    r"\bFragment\b", r"\bfindViewById\b", r"\bR\.id\b", r"\bKotlin\b",
    r"\bAndroidView\b", r"\bEspresso\b", r"\bRecyclerView\b", r"\bViewModel\b",
    # iOS
    r"\bSwiftUI\b", r"\bUIView\b", r"\bUIViewController\b", r"\bStoryboard\b",
    r"\bUIKit\b", r"\bXCTest\b", r"\bSwift\b", r"\bObjective-C\b",
    # Cross
    r"\bKMM\b", r"\bXML layout\b",
]
FORBIDDEN_RE = re.compile("|".join(FORBIDDEN_TOKENS))


def check_platform(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []
    stripped = _strip_code_fences(text)
    for ln_no, line in enumerate(stripped.splitlines(), start=1):
        for m in FORBIDDEN_RE.finditer(line):
            out.append(Finding(
                file=file, line=ln_no, check="PLATFORM", severity=SEVERITY_WARN,
                message=f"token `{m.group(0)}` framework-specific — doc PM nên platform-agnostic (đặt vào code fence ` ```kotlin``` ` nếu cần quote)",
                context=line.strip()[:90],
            ))
    return out


# ---------------- Check 5: Open Questions có PM answer --------------------

PM_ANSWER_RE = re.compile(
    r"\*\*PM answer\*\*:\s*(?P<body>.+?)(?=\n\n|\n#{1,6}\s|\Z)",
    re.DOTALL,
)
QUESTION_ANCHOR_RE = re.compile(r"\{#[^}]*/question/[^}]+\}")


def check_open_questions(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []
    headings = list(HEADING_RE.finditer(text))
    for i, h in enumerate(headings):
        anchor = h.group("a") or ""
        title = h.group("title").lower()
        is_q_heading = "/question/" in anchor or re.match(r"^q-?\d+", title)
        if not is_q_heading:
            continue
        start, end = _section_bounds(headings, i, len(text))
        section = text[start:end]
        am = PM_ANSWER_RE.search(section)
        ln = _line_of(text, h.start())
        if not am:
            out.append(Finding(
                file=file, line=ln, check="OPENQ", severity=SEVERITY_WARN,
                message=f"Open Question '{h.group('title').strip()}' chưa có dòng `**PM answer**:` — engineering review không trace được decision",
                context=h.group(0).strip()[:80],
            ))
            continue
        ans = am.group("body").strip()
        if not ans or "_(fill in)_" in ans or ans.lower() in ("tbd", "todo", "?", "..."):
            out.append(Finding(
                file=file, line=ln, check="OPENQ", severity=SEVERITY_WARN,
                message=f"Open Question '{h.group('title').strip()}' có `**PM answer**:` nhưng rỗng / placeholder — chốt câu trả lời hoặc đánh dấu WONTFIX",
                context=f"answer: {ans[:60]!r}",
            ))
    return out


# ---------------- Check 6: Frontmatter sanity -----------------------------

FM_REQUIRED_KEYS = ("status", "version", "last_updated")
FM_VALID_STATUS = ("draft", "review", "approved", "deprecated", "signed_off",
                   "sign_off_pass", "sign_off_fail")


def check_frontmatter(text: str, file: str) -> list[Finding]:
    out: list[Finding] = []
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        # Frontmatter optional cho doc PM — không warn nếu không có
        return out
    body = fm.group("body")
    keys_present = set()
    status_value = ""
    for line in body.splitlines():
        m = re.match(r"^(?P<k>[a-z_]+)\s*:\s*(?P<v>.*)$", line)
        if not m:
            continue
        k = m.group("k")
        v = m.group("v").strip().strip("\"'")
        keys_present.add(k)
        if k == "status":
            status_value = v
    for req in FM_REQUIRED_KEYS:
        if req not in keys_present:
            out.append(Finding(
                file=file, line=1, check="FM", severity=SEVERITY_WARN,
                message=f"frontmatter thiếu key `{req}` (recommend: status / version / last_updated)",
            ))
    if status_value and status_value not in FM_VALID_STATUS:
        out.append(Finding(
            file=file, line=1, check="FM", severity=SEVERITY_WARN,
            message=f"frontmatter `status: {status_value}` không phải known value ({', '.join(FM_VALID_STATUS)})",
        ))
    return out


# ---------------- Orchestrator --------------------------------------------

CHECK_FNS = {
    "ANCHOR": check_anchor_format,
    "RFC2119": check_rfc2119,
    "AC": check_ac_measurable,
    "PLATFORM": check_platform,
    "OPENQ": check_open_questions,
    "FM": check_frontmatter,
}


def lint_file(path: Path, checks: tuple[str, ...] = CHECK_IDS) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    out: list[Finding] = []
    for c in checks:
        out.extend(CHECK_FNS[c](text, rel))
    return sorted(out, key=lambda f: (f.line, f.check))


def lint_path(target: Path, checks: tuple[str, ...] = CHECK_IDS) -> list[Finding]:
    if target.is_file():
        return lint_file(target, checks)
    if target.is_dir():
        out: list[Finding] = []
        for md in sorted(target.rglob("*.md")):
            out.extend(lint_file(md, checks))
        return out
    raise FileNotFoundError(f"{target}: not a file or directory")


# ---------------- CLI ------------------------------------------------------


def _format_finding(f: Finding) -> str:
    ctx = f" | {f.context}" if f.context else ""
    return f"{f.file}:{f.line}: [{f.check}] {f.severity}: {f.message}{ctx}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Linter cho doc PM markdown (anchor / RFC 2119 / AC measurable / platform-agnostic / open Q / frontmatter)."
    )
    ap.add_argument("path", type=Path, help="file .md hoặc directory chứa .md")
    ap.add_argument("--check", action="append", choices=list(CHECK_IDS),
                    help="chỉ chạy check này (lặp lại được). Default: all 6.")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 nếu có warning")
    ap.add_argument("--json", action="store_true",
                    help="output JSON thay vì text")
    args = ap.parse_args()

    checks = tuple(args.check) if args.check else CHECK_IDS

    try:
        findings = lint_path(args.path, checks)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "path": str(args.path),
            "checks": list(checks),
            "findings": [asdict(f) for f in findings],
            "total": len(findings),
        }, indent=2, ensure_ascii=False))
    else:
        if not findings:
            print(f"OK {args.path} (0 warning, checks: {', '.join(checks)})")
            return 0
        # Group by check for readability
        by_check: dict[str, list[Finding]] = {}
        for f in findings:
            by_check.setdefault(f.check, []).append(f)
        for c in CHECK_IDS:
            if c not in by_check:
                continue
            print(f"\n=== {c} ({len(by_check[c])}) ===")
            for f in by_check[c]:
                print(_format_finding(f))
        print(f"\nTotal: {len(findings)} warning(s) across {len(by_check)} check(s)")

    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
