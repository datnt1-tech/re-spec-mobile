"""scope_loader.py — load + validate <feature>_scope.md.

The scope file is the PM contract that gates the capture loop. The
app-explorer agent reads it via this module to know which screens are
must_visit, which clusters to skip, and which open questions block the start.

Usage (Python):
    from scope_loader import load_scope, ScopeNotSignedOff
    try:
        s = load_scope("explore_create")
    except FileNotFoundError:
        # auto-approve path: small features can skip Gate 1
        proceed_without_scope()
    except ScopeNotSignedOff as e:
        # PM hasn't signed off yet; capture phase must wait
        report_to_user(str(e))

Usage (CLI):
    python scope_loader.py <feature>            # show parsed scope as JSON
    python scope_loader.py <feature> --check    # exit 1 if not signed_off
    python scope_loader.py <feature> --gates    # show open questions blocking
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from re_spec_mobile.profile_loader import Profile, load_profile


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ANCHOR_RE = re.compile(r"^[a-z][a-z0-9_]*/[a-z_]+/[a-z0-9_]+$")


class ScopeNotSignedOff(Exception):
    """Raised when scope file exists but status != signed_off."""


class ScopeBlockedByQuestions(Exception):
    """Raised when scope has unresolved questions (no PM answer in body)."""


@dataclass
class Cluster:
    id: str
    name: str
    in_scope: bool
    must_visit: list[str] = field(default_factory=list)
    optional_visit: list[str] = field(default_factory=list)
    reason: str = ""

    def all_required(self) -> set[str]:
        return set(self.must_visit)


@dataclass
class ScopeQuestion:
    id: str
    summary: str
    answered: bool = False
    answer_text: str = ""


@dataclass
class Scope:
    feature: str
    file_path: Path
    status: str                          # draft | signed_off | revising
    signed_off_by: str
    signed_off_at: str
    scope_version: int

    clusters: list[Cluster] = field(default_factory=list)
    questions: list[ScopeQuestion] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)

    raw: dict[str, Any] = field(default_factory=dict)

    # ---- convenience ----
    def in_scope_clusters(self) -> list[Cluster]:
        return [c for c in self.clusters if c.in_scope]

    def out_of_scope_clusters(self) -> list[Cluster]:
        return [c for c in self.clusters if not c.in_scope]

    def all_must_visit(self) -> set[str]:
        out: set[str] = set()
        for c in self.in_scope_clusters():
            out.update(c.must_visit)
        return out

    def all_optional_visit(self) -> set[str]:
        out: set[str] = set()
        for c in self.in_scope_clusters():
            out.update(c.optional_visit)
        return out

    def out_of_scope_anchors(self) -> set[str]:
        out: set[str] = set()
        for c in self.out_of_scope_clusters():
            out.update(c.must_visit)
            out.update(c.optional_visit)
        return out

    def unresolved_questions(self) -> list[ScopeQuestion]:
        return [q for q in self.questions if not q.answered]

    def is_capture_ready(self) -> tuple[bool, str]:
        """Returns (ready, reason). Ready = signed_off AND no unresolved questions."""
        if self.status != "signed_off":
            return False, f"scope status is '{self.status}', need 'signed_off'"
        unresolved = self.unresolved_questions()
        if unresolved:
            qs = ", ".join(f"{q.id}: {q.summary[:40]}" for q in unresolved)
            return False, f"{len(unresolved)} unresolved question(s) — {qs}"
        return True, "ready"


# ---------- parsing --------------------------------------------------------


def scope_path(feature: str, profile: Profile) -> Path:
    return profile.feature_dir(feature) / f"{feature}_scope.md"


def load_scope(feature: str, profile: Profile | None = None) -> Scope:
    """Load and parse the scope file for a feature.

    Raises:
        FileNotFoundError if scope file doesn't exist (caller decides whether
            to auto-approve for small features or block).
    """
    p = profile or load_profile()
    path = scope_path(feature, p)
    if not path.exists():
        raise FileNotFoundError(
            f"No scope contract at {path}. "
            f"Either bootstrap one (`/re-spec-mobile scope <feature>`) or "
            f"auto-approve if feature is small (<5 screens)."
        )
    return parse_scope(path, feature)


def parse_scope(path: Path, feature: str) -> Scope:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]

    if fm.get("feature") != feature:
        raise ValueError(
            f"{path}: frontmatter feature='{fm.get('feature')}' ≠ requested '{feature}'"
        )
    if fm.get("layer") != "scope":
        raise ValueError(f"{path}: layer must be 'scope', got '{fm.get('layer')}'")

    clusters: list[Cluster] = []
    for c in fm.get("clusters") or []:
        cid = c.get("id", "")
        if not ANCHOR_RE.match(cid):
            raise ValueError(f"{path}: invalid cluster anchor '{cid}'")
        clusters.append(Cluster(
            id=cid,
            name=c.get("name", ""),
            in_scope=bool(c.get("in_scope", True)),
            must_visit=list(c.get("must_visit") or []),
            optional_visit=list(c.get("optional_visit") or []),
            reason=str(c.get("reason", "")),
        ))

    questions: list[ScopeQuestion] = []
    for q in fm.get("questions") or []:
        qid = q.get("id", "")
        summary = q.get("summary", "")
        # detect "PM answer" in body — naive but explicit
        answered, answer_text = _detect_answer(body, qid)
        questions.append(ScopeQuestion(
            id=qid, summary=summary, answered=answered, answer_text=answer_text,
        ))

    return Scope(
        feature=feature,
        file_path=path,
        status=str(fm.get("status", "draft")),
        signed_off_by=str(fm.get("signed_off_by", "")),
        signed_off_at=str(fm.get("signed_off_at", "")),
        scope_version=int(fm.get("scope_version", 1)),
        clusters=clusters,
        questions=questions,
        acceptance=list(fm.get("acceptance_capture") or []),
        raw=fm,
    )


_ANCHOR_HEADING_RE = re.compile(r"^(#{2,4})\s.*\{#(?P<anchor>[a-z][a-z0-9_/]+)\}", re.MULTILINE)
_PM_ANSWER_RE = re.compile(r"\*\*PM answer\*\*:\s*(?P<answer>.+?)(?=\n\n|\Z)", re.DOTALL)


def _detect_answer(body: str, question_anchor: str) -> tuple[bool, str]:
    """Find the heading carrying `{#<question_anchor>}`, then look ONLY within
    that section (until the next same-or-higher heading) for `**PM answer**:`.
    Returns (True, text) if a non-empty answer found that isn't `_(fill in)_`.
    """
    headings = list(_ANCHOR_HEADING_RE.finditer(body))
    for i, m in enumerate(headings):
        if m.group("anchor") != question_anchor:
            continue
        section_start = m.end()
        section_end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = body[section_start:section_end]
        am = _PM_ANSWER_RE.search(section)
        if not am:
            return False, ""
        text = am.group("answer").strip()
        if text and "_(fill in)_" not in text:
            return True, text
        return False, ""
    return False, ""


# ---------- CLI ------------------------------------------------------------


def _summary(s: Scope) -> dict[str, Any]:
    return {
        "feature": s.feature,
        "file_path": str(s.file_path),
        "status": s.status,
        "scope_version": s.scope_version,
        "signed_off_by": s.signed_off_by,
        "signed_off_at": s.signed_off_at,
        "clusters": {
            "in_scope": [{"id": c.id, "name": c.name,
                          "must_visit": len(c.must_visit),
                          "optional_visit": len(c.optional_visit)}
                         for c in s.in_scope_clusters()],
            "out_of_scope": [{"id": c.id, "name": c.name, "reason": c.reason}
                             for c in s.out_of_scope_clusters()],
        },
        "must_visit_total": len(s.all_must_visit()),
        "optional_visit_total": len(s.all_optional_visit()),
        "questions": {
            "answered": sum(1 for q in s.questions if q.answered),
            "unresolved": len(s.unresolved_questions()),
            "details": [{"id": q.id, "summary": q.summary, "answered": q.answered}
                        for q in s.questions],
        },
        "acceptance_criteria": s.acceptance,
        "is_capture_ready": s.is_capture_ready()[0],
        "block_reason": s.is_capture_ready()[1],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("feature")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if scope not signed_off OR has unresolved questions")
    ap.add_argument("--gates", action="store_true",
                    help="print blocking conditions only (terse)")
    args = ap.parse_args()

    profile = load_profile()
    try:
        s = load_scope(args.feature, profile=profile)
    except FileNotFoundError as e:
        if args.check:
            print(f"NO_SCOPE {args.feature}", file=sys.stderr)
            return 1
        print(f"NO_SCOPE {args.feature}: {e}", file=sys.stderr)
        return 0
    except ValueError as e:
        print(f"INVALID {args.feature}: {e}", file=sys.stderr)
        return 1

    ready, reason = s.is_capture_ready()

    if args.gates:
        if ready:
            print(f"OK {args.feature}: ready (scope_version={s.scope_version})")
            return 0
        print(f"BLOCKED {args.feature}: {reason}")
        return 1

    if args.check:
        if ready:
            return 0
        print(f"BLOCKED {args.feature}: {reason}", file=sys.stderr)
        return 1

    print(json.dumps(_summary(s), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
