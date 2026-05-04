"""validate_spec.py — enforce SPEC_SCHEMA rules on per-project spec files.

Usage:
    python validate_spec.py                  # validate all under <profile.feature_root>
    python validate_spec.py <file>...        # validate specific files
    python validate_spec.py --changed        # only files changed vs HEAD
    python validate_spec.py --quiet

Exit codes:
    0 = clean
    1 = validation errors

Checks (see SPEC_SCHEMA.md §10 in canonical/):
    V1  frontmatter YAML parseable + present
    V2  feature matches folder
    V3  layer ∈ {observations, flow, implementation, overview}
    V4  anchor unique across project (except cross-layer same-feature screen anchors)
    V5  last_updated is ISO-8601 date
    V6  anchor references resolve
    V7  inline `{#anchor}` markers follow slash format
    V8  implementation + overview layer must have status
    V9  no duplicate anchor inside same file
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from re_spec_mobile.profile_loader import Profile, load_profile


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ANCHOR_RE = re.compile(r"^[a-z][a-z0-9_]*/[a-z_]+/[a-z0-9_]+$")
INLINE_ANCHOR_RE = re.compile(r"\{#([^}]+)\}")

VALID_LAYERS = {"scope", "observations", "flow", "implementation", "coverage_report", "overview"}


class ValidationError:
    __slots__ = ("file", "rule", "message", "line", "project_root")

    def __init__(self, file: Path, rule: str, message: str, project_root: Path, line: int | None = None):
        self.file = file
        self.rule = rule
        self.message = message
        self.line = line
        self.project_root = project_root

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line else ""
        try:
            rel = self.file.relative_to(self.project_root)
        except ValueError:
            rel = self.file
        return f"{rel}{loc}  [{self.rule}]  {self.message}"


def load_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str, int]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text, 0
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise RuntimeError(f"yaml parse error: {e}") from e
    fm_lines = m.group(0).count("\n")
    return data, text[m.end():], fm_lines


def expected_feature(path: Path, profile: Profile) -> str | None:
    try:
        rel = path.relative_to(profile.feature_root)
        parts = rel.parts
        if len(parts) >= 2:
            return parts[0]
        if path.name.startswith("app_"):
            return "app"
    except ValueError:
        # legacy single-file specs (eg. spec/observations.md from older bible-agent) —
        # don't enforce a folder match; trust the frontmatter feature field as-is.
        return None
    return None


def collect_anchors_from_fm(fm: dict[str, Any], file: Path) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if fm.get("anchor"):
        out.append((fm["anchor"], 1))

    for key in ("screens", "blocks", "clusters", "components", "apis", "data_models",
                "criteria", "invariants", "questions", "states"):
        for item in fm.get(key) or []:
            a = item.get("anchor") or item.get("id")
            if a:
                out.append((a, item.get("section_line") or 1))
    return out


def collect_references_from_fm(fm: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for ne in fm.get("nav_edges") or []:
        if ne.get("from"):
            refs.append((ne["from"], "nav_edges.from"))
        if ne.get("to"):
            refs.append((ne["to"], "nav_edges.to"))
    for b in fm.get("blocks") or []:
        for s in b.get("screens") or []:
            refs.append((s, "blocks[].screens"))
    for cl in fm.get("clusters") or []:
        for s in cl.get("must_visit") or []:
            refs.append((s, "clusters[].must_visit"))
        for s in cl.get("optional_visit") or []:
            refs.append((s, "clusters[].optional_visit"))
    for c in fm.get("components") or []:
        for s in c.get("screens") or []:
            refs.append((s, "components[].screens"))
    for api in fm.get("apis") or []:
        if api.get("returns"):
            refs.append((api["returns"], "apis[].returns"))
    for r in fm.get("reuses") or []:
        if r.get("component"):
            refs.append((r["component"], "reuses[].component"))
        for u in r.get("used_by") or []:
            refs.append((u, "reuses[].used_by"))
    for g in fm.get("gaps") or []:
        if g.get("anchor"):
            refs.append((g["anchor"], "gaps[].anchor"))
    for d in fm.get("drift") or []:
        a = d.get("anchor_inferred") or d.get("anchor")
        if a:
            refs.append((a, "drift[].anchor_inferred"))
    for rel in fm.get("related") or []:
        refs.append((rel, "related"))
    return refs


def gather_all_known_anchors(files: list[Path]) -> set[str]:
    known: set[str] = set()
    for p in files:
        try:
            fm, _, _ = load_frontmatter(p)
        except RuntimeError:
            continue
        if not fm:
            continue
        for a, _ in collect_anchors_from_fm(fm, p):
            known.add(a)
    features_seen = {fm.get("feature") for p in files if (fm := _peek_fm(p))}
    for f in features_seen:
        if f:
            known.add(f"{f}/feature/root")
    return known


def _peek_fm(path: Path) -> dict[str, Any] | None:
    try:
        fm, _, _ = load_frontmatter(path)
        return fm
    except Exception:
        return None


def validate_file(
    path: Path,
    known_anchors: set[str],
    global_anchor_to_file: dict[str, Path],
    profile: Profile,
) -> list[ValidationError]:
    errs: list[ValidationError] = []

    try:
        fm, body, fm_lines = load_frontmatter(path)
    except RuntimeError as e:
        errs.append(ValidationError(path, "V1", f"frontmatter yaml error: {e}", profile.project_root, 1))
        return errs

    if fm is None:
        errs.append(ValidationError(path, "V1", "missing YAML frontmatter (expected leading `---`)", profile.project_root, 1))
        return errs

    feature = fm.get("feature")
    expected = expected_feature(path, profile)
    if expected and feature != expected:
        errs.append(ValidationError(path, "V2", f"feature '{feature}' ≠ folder '{expected}'", profile.project_root, 2))

    layer = fm.get("layer")
    if layer not in VALID_LAYERS:
        errs.append(ValidationError(path, "V3", f"layer '{layer}' not in {sorted(VALID_LAYERS)}", profile.project_root, 2))

    lu = fm.get("last_updated")
    if not _valid_iso_date(lu):
        errs.append(ValidationError(path, "V5", f"last_updated '{lu}' is not ISO-8601 date", profile.project_root, 2))

    if layer in ("implementation", "overview"):
        if fm.get("status") not in ("draft", "approved", "stale"):
            errs.append(ValidationError(path, "V8", f"status missing or invalid for layer={layer}", profile.project_root, 2))
    if layer == "scope":
        if fm.get("status") not in ("draft", "signed_off", "revising", "stale"):
            errs.append(ValidationError(path, "V8", f"scope status invalid: {fm.get('status')!r} (need draft|signed_off|revising|stale)", profile.project_root, 2))
        # if signed_off, require signed_off_by + signed_off_at
        if fm.get("status") == "signed_off":
            if not fm.get("signed_off_by"):
                errs.append(ValidationError(path, "V8", "scope status=signed_off but signed_off_by is empty", profile.project_root, 2))
            if not fm.get("signed_off_at"):
                errs.append(ValidationError(path, "V8", "scope status=signed_off but signed_off_at is empty", profile.project_root, 2))
    if layer == "coverage_report":
        if fm.get("status") not in ("draft", "sign_off_pass", "sign_off_fail", "stale"):
            errs.append(ValidationError(path, "V8", f"coverage_report status invalid: {fm.get('status')!r}", profile.project_root, 2))

    decl_list = collect_anchors_from_fm(fm, path)
    seen: dict[str, int] = {}
    for a, line in decl_list:
        if a in seen:
            errs.append(ValidationError(path, "V9", f"duplicate anchor '{a}' (also at line {seen[a]})", profile.project_root, line))
        else:
            seen[a] = line

    for a, line in decl_list:
        if a in global_anchor_to_file and global_anchor_to_file[a] != path:
            other = global_anchor_to_file[a]
            other_fm = _peek_fm(other)
            if other_fm and other_fm.get("feature") == feature:
                if a.startswith(f"{feature}/screen/"):
                    continue
            errs.append(ValidationError(
                path, "V4",
                f"anchor '{a}' also declared in {other.relative_to(profile.project_root)}",
                profile.project_root, line,
            ))

    for ref, field in collect_references_from_fm(fm):
        if ref not in known_anchors and not ref.startswith("external:"):
            errs.append(ValidationError(path, "V6", f"unresolved ref '{ref}' ({field})", profile.project_root, 2))

    for lineno, line in enumerate(body.splitlines(), start=fm_lines + 1):
        for m in INLINE_ANCHOR_RE.finditer(line):
            a = m.group(1)
            if not ANCHOR_RE.match(a):
                errs.append(ValidationError(
                    path, "V7",
                    f"invalid inline anchor '{a}' (expected <feature>/<type>/<name>)",
                    profile.project_root, lineno,
                ))

    for a, line in decl_list:
        if not ANCHOR_RE.match(a):
            errs.append(ValidationError(path, "V7", f"invalid anchor format '{a}'", profile.project_root, line))

    return errs


def _valid_iso_date(v: Any) -> bool:
    if isinstance(v, (date, datetime)):
        return True
    if not isinstance(v, str):
        return False
    try:
        datetime.fromisoformat(v)
        return True
    except ValueError:
        return False


def discover_spec_files(profile: Profile) -> list[Path]:
    files: list[Path] = []
    if profile.feature_root.exists():
        for p in profile.feature_root.rglob("*.md"):
            if p.name.endswith("_nav.md"):
                continue
            files.append(p)
    legacy = profile.spec_root / "observations.md"
    if legacy.exists():
        files.append(legacy)
    return sorted(files)


def changed_spec_files(profile: Profile) -> list[Path]:
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
            cwd=profile.project_root, check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    out: list[Path] = []
    for line in res.stdout.splitlines():
        p = profile.project_root / line.strip()
        if not p.exists() or p.suffix != ".md":
            continue
        try:
            p.relative_to(profile.spec_root)
        except ValueError:
            continue
        if p.name.endswith("_nav.md"):
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--changed", action="store_true", help="only files changed vs HEAD")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    profile = load_profile()
    all_files = discover_spec_files(profile)

    if args.files:
        target = []
        for p in args.files:
            p = p if p.is_absolute() else (Path.cwd() / p).resolve()
            target.append(p)
    elif args.changed:
        target = changed_spec_files(profile)
    else:
        target = all_files

    if not target:
        if not args.quiet:
            print("no spec files to validate")
        return 0

    known_anchors = gather_all_known_anchors(all_files)
    anchor_to_file: dict[str, Path] = {}
    for p in all_files:
        fm = _peek_fm(p)
        if not fm:
            continue
        for a, _ in collect_anchors_from_fm(fm, p):
            anchor_to_file.setdefault(a, p)

    errors: list[ValidationError] = []
    for f in target:
        errors.extend(validate_file(f, known_anchors, anchor_to_file, profile))

    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"\nFAIL — {len(errors)} error(s) in {len({e.file for e in errors})} file(s)", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"OK — validated {len(target)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
