"""pm_channel.py — Telegram bridge để PM trả lời Open Question 3 gate qua chat.

Module này KHÔNG chạy daemon. CLI on-demand:

    re-spec-pm-init                            # giúp PM lấy chat_id lần đầu
    re-spec-pm-ask <feature> --gate scope      # post Open Question lên Telegram
    re-spec-pm-ask <feature> --gate coverage   # post xin sign_off pass/fail
    re-spec-pm-ask <feature> --gate spec       # post Open Question §7 feature_spec
    re-spec-pm-sync <feature>                  # long-poll getUpdates, fold reply vào file

Cơ chế:
- Bot Telegram post 1 message / câu hỏi (kèm anchor marker `[<anchor>]` ở đầu).
- PM reply trực tiếp vào message bot (Telegram hỗ trợ `reply_to_message_id`).
- Sync poll `getUpdates`, match reply theo `reply_to_message_id`, fold text vào
  đúng file/đúng `Q-NN` (ghi `**PM answer**: <text>` thay placeholder
  `_(fill in)_`).
- State persist ở `<feature_root>/<feature>/.pm_inbox.json` (idempotent).

Token bot lấy từ env (`profile.pm_channel.token_env`, default `TELEGRAM_BOT_TOKEN`).
Chat ID lưu trong profile (`pm_channel.chat_id`). Stdlib `urllib` only — không
thêm dependency.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from re_spec_mobile.profile_loader import Profile, load_profile


TELEGRAM_API = "https://api.telegram.org"

GATE_SCOPE = "scope"
GATE_COVERAGE = "coverage"
GATE_SPEC = "spec"

KIND_QUESTION = "question"
KIND_COVERAGE_SIGNOFF = "coverage_signoff"

# Anchor heading: "### Q-01: <text> {#feature/question/q_01}"
ANCHOR_HEADING_RE = re.compile(
    r"^(#{2,4})\s+(?P<title>.+?)\s*\{#(?P<anchor>[a-z][a-z0-9_/]+)\}\s*$",
    re.MULTILINE,
)
PM_ANSWER_RE = re.compile(
    r"(?P<lead>\*\*PM answer\*\*:\s*)(?P<body>.+?)(?=\n\n|\n#{1,4}\s|\Z)",
    re.DOTALL,
)
FRONTMATTER_RE = re.compile(r"^(---\n)(?P<body>.*?)(\n---\n)", re.DOTALL)


# ---------------- Telegram client ------------------------------------------


class TelegramError(RuntimeError):
    pass


@dataclass
class TelegramAPI:
    token: str
    timeout_s: int = 30

    def _post(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{TELEGRAM_API}/bot{self.token}/{method}"
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s + 10) as r:
                payload = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise TelegramError(f"{method} HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise TelegramError(f"{method} network error: {e}") from e
        if not payload.get("ok"):
            raise TelegramError(f"{method} api error: {payload}")
        return payload["result"]

    def send_message(
        self, chat_id: str, text: str, *, reply_to: int | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if reply_to is not None:
            params["reply_to_message_id"] = reply_to
            params["allow_sending_without_reply"] = True
        return self._post("sendMessage", params)

    def get_updates(self, offset: int = 0) -> list[dict[str, Any]]:
        return self._post(
            "getUpdates",
            {"offset": offset, "timeout": self.timeout_s, "allowed_updates": ["message"]},
        )

    def get_me(self) -> dict[str, Any]:
        return self._post("getMe", {})


def telegram_from_profile(profile: Profile) -> TelegramAPI:
    pm = profile.raw.get("pm_channel") or {}
    if pm.get("type") != "telegram":
        raise SystemExit(
            "pm_channel.type != 'telegram' — chỉ Telegram được support hiện tại."
        )
    env_var = pm.get("token_env") or "TELEGRAM_BOT_TOKEN"
    token = os.environ.get(env_var, "").strip()
    if not token:
        raise SystemExit(
            f"thiếu bot token — set env var ${env_var} (lấy từ @BotFather)."
        )
    timeout = int(pm.get("poll_timeout_s") or 30)
    return TelegramAPI(token=token, timeout_s=timeout)


def chat_id_from_profile(profile: Profile) -> str:
    pm = profile.raw.get("pm_channel") or {}
    cid = pm.get("chat_id")
    if cid in (None, "", 0):
        raise SystemExit(
            "thiếu pm_channel.chat_id trong .spec-profile.yml — chạy "
            "`re-spec-pm-init` để lấy."
        )
    return str(cid)


def message_prefix(profile: Profile, feature: str) -> str:
    pm = profile.raw.get("pm_channel") or {}
    tmpl = pm.get("message_prefix") or "[re-spec/<feature>]"
    return tmpl.replace("<feature>", feature)


# ---------------- Inbox persistence ----------------------------------------


def inbox_path(profile: Profile, feature: str) -> Path:
    return profile.feature_dir(feature) / ".pm_inbox.json"


def load_inbox(profile: Profile, feature: str) -> dict[str, Any]:
    p = inbox_path(profile, feature)
    if not p.exists():
        return {"feature": feature, "messages": [], "last_update_id": 0}
    return json.loads(p.read_text(encoding="utf-8"))


def save_inbox(profile: Profile, feature: str, inbox: dict[str, Any]) -> None:
    p = inbox_path(profile, feature)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(inbox, indent=2, ensure_ascii=False), encoding="utf-8")


def find_inbox_entry(
    inbox: dict[str, Any], *, anchor: str | None = None, message_id: int | None = None
) -> dict[str, Any] | None:
    for m in inbox["messages"]:
        if anchor is not None and m.get("anchor") == anchor:
            return m
        if message_id is not None and m.get("message_id") == message_id:
            return m
    return None


# ---------------- Question discovery ---------------------------------------


@dataclass
class Question:
    anchor: str           # "<feature>/question/q_01"
    title: str            # "Q-01: <text>"
    summary: str          # phần text sau "Q-NN:"
    file: Path
    has_pm_answer: bool


def _section_text(body: str, anchor: str) -> str:
    """Return text of the section whose heading carries `{#<anchor>}`,
    bounded by the next heading of equal-or-lesser depth.
    """
    headings = list(ANCHOR_HEADING_RE.finditer(body))
    for i, m in enumerate(headings):
        if m.group("anchor") != anchor:
            continue
        section_start = m.end()
        section_end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        return body[section_start:section_end]
    return ""


def _has_pm_answer(section: str) -> bool:
    am = PM_ANSWER_RE.search(section)
    if not am:
        return False
    text = am.group("body").strip()
    return bool(text) and "_(fill in)_" not in text


def discover_questions(md_path: Path, feature: str) -> list[Question]:
    """Scan a markdown file for Open Question anchors `<feature>/question/<slug>`."""
    if not md_path.exists():
        return []
    text = md_path.read_text(encoding="utf-8")
    out: list[Question] = []
    seen: set[str] = set()
    prefix = f"{feature}/question/"
    for m in ANCHOR_HEADING_RE.finditer(text):
        anchor = m.group("anchor")
        if not anchor.startswith(prefix) or anchor in seen:
            continue
        seen.add(anchor)
        title = m.group("title").strip()
        # summary: drop "Q-NN:" prefix if present
        summary = re.sub(r"^Q-?\d+\s*[:\-]\s*", "", title).strip()
        section = _section_text(text, anchor)
        out.append(Question(
            anchor=anchor,
            title=title,
            summary=summary or title,
            file=md_path,
            has_pm_answer=_has_pm_answer(section),
        ))
    return out


# ---------------- Coverage report helpers ----------------------------------


def _coverage_summary(coverage_md: Path) -> str:
    """Extract a short summary block from `## 1. Summary` table for Telegram."""
    if not coverage_md.exists():
        return "(coverage_report.md missing)"
    text = coverage_md.read_text(encoding="utf-8")
    m = re.search(r"##\s+1\.\s+Summary\s*\n(.*?)(?=\n##\s)", text, re.DOTALL)
    if not m:
        return "(no §1 Summary section found)"
    return m.group(1).strip()


def _coverage_status(coverage_md: Path) -> str:
    if not coverage_md.exists():
        return "missing"
    fm = FRONTMATTER_RE.match(coverage_md.read_text(encoding="utf-8"))
    if not fm:
        return "no-frontmatter"
    for line in fm.group("body").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()
    return "draft"


# ---------------- Reply folding (write back to spec file) ------------------


def _fold_question_reply(md_path: Path, anchor: str, reply_text: str) -> bool:
    """Replace `**PM answer**: _(fill in)_` (or empty) under the section of
    `{#<anchor>}` with the PM's text. Returns True if the file changed.
    """
    text = md_path.read_text(encoding="utf-8")
    headings = list(ANCHOR_HEADING_RE.finditer(text))
    for i, m in enumerate(headings):
        if m.group("anchor") != anchor:
            continue
        section_start = m.end()
        section_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section = text[section_start:section_end]

        # try to replace existing `**PM answer**:` block
        new_section, n = PM_ANSWER_RE.subn(
            lambda mm: f"{mm.group('lead')}{reply_text.strip()}",
            section,
            count=1,
        )
        if n == 0:
            # no placeholder — append a fresh PM answer at end of section
            sep = "" if section.endswith("\n\n") else ("\n" if section.endswith("\n") else "\n\n")
            new_section = section + f"{sep}**PM answer**: {reply_text.strip()}\n"
        if new_section == section:
            return False
        new_text = text[:section_start] + new_section + text[section_end:]
        md_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def _fold_coverage_signoff(coverage_md: Path, reply_text: str) -> tuple[bool, str]:
    """Parse PM reply for coverage signoff. First word `pass` / `fail`
    (case-insensitive) drives `status:` flip; rest = reason appended to
    `decisions:`. Returns (changed, decision: 'pass'|'fail'|'unknown').
    """
    text = coverage_md.read_text(encoding="utf-8")
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        return False, "unknown"

    head_first = reply_text.strip().split(maxsplit=1)
    if not head_first:
        return False, "unknown"
    verdict_word = head_first[0].lower()
    if verdict_word.startswith("pass"):
        verdict = "pass"
    elif verdict_word.startswith("fail"):
        verdict = "fail"
    else:
        return False, "unknown"
    reason = head_first[1].strip() if len(head_first) > 1 else ""

    new_status = f"sign_off_{verdict}"
    fm_body = fm.group("body")
    if re.search(r"^status:\s*", fm_body, re.MULTILINE):
        fm_body_new = re.sub(
            r"^status:.*$", f"status: {new_status}", fm_body, count=1, flags=re.MULTILINE
        )
    else:
        fm_body_new = fm_body + f"\nstatus: {new_status}"

    decision_line = (
        f"  - at: '{datetime.now(timezone.utc).isoformat(timespec='seconds')}'\n"
        f"    by: telegram_pm\n"
        f"    decision: {verdict}\n"
        f"    reason: {json.dumps(reason, ensure_ascii=False)}\n"
    )
    if re.search(r"^decisions:\s*\[\]\s*$", fm_body_new, re.MULTILINE):
        fm_body_new = re.sub(
            r"^decisions:\s*\[\]\s*$",
            "decisions:\n" + decision_line.rstrip(),
            fm_body_new,
            count=1,
            flags=re.MULTILINE,
        )
    elif re.search(r"^decisions:\s*$", fm_body_new, re.MULTILINE):
        fm_body_new = re.sub(
            r"^decisions:\s*$",
            "decisions:\n" + decision_line.rstrip(),
            fm_body_new,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        fm_body_new = fm_body_new + f"\ndecisions:\n{decision_line.rstrip()}"

    new_text = text[: fm.start("body")] + fm_body_new + text[fm.end("body"):]
    coverage_md.write_text(new_text, encoding="utf-8")
    return True, verdict


# ---------------- Ask flow -------------------------------------------------


def _gate_files(profile: Profile, feature: str, gate: str) -> list[Path]:
    fdir = profile.feature_dir(feature)
    if gate == GATE_SCOPE:
        return [fdir / f"{feature}_scope.md"]
    if gate == GATE_COVERAGE:
        return [fdir / f"{feature}_coverage_report.md"]
    if gate == GATE_SPEC:
        return [fdir / f"{feature}_feature_spec.md"]
    raise ValueError(f"unknown gate '{gate}' (use scope|coverage|spec)")


def ask_for_gate(
    profile: Profile, feature: str, gate: str, *, force: bool = False
) -> dict[str, Any]:
    """Post Open Question (or coverage signoff prompt) of `gate` to Telegram.
    Idempotent: skip anchors already posted (unless --force)."""
    api = telegram_from_profile(profile)
    chat_id = chat_id_from_profile(profile)
    inbox = load_inbox(profile, feature)
    prefix = message_prefix(profile, feature)
    posted: list[dict[str, Any]] = []
    skipped: list[str] = []

    if gate == GATE_COVERAGE:
        files = _gate_files(profile, feature, gate)
        coverage_md = files[0]
        if not coverage_md.exists():
            raise SystemExit(f"file thiếu: {coverage_md}")
        anchor = f"{feature}/coverage_report/root"
        existing = find_inbox_entry(inbox, anchor=anchor)
        if existing and not force:
            skipped.append(anchor)
        else:
            summary = _coverage_summary(coverage_md)
            text = (
                f"{prefix} GATE 2 — Coverage report\n"
                f"File: {coverage_md.name}\n\n"
                f"{summary}\n\n"
                "Reply: `pass <ghi chú>` HOẶC `fail <lý do>` để ký Gate 2."
            )
            res = api.send_message(chat_id, text)
            entry = {
                "message_id": res["message_id"],
                "anchor": anchor,
                "gate": gate,
                "kind": KIND_COVERAGE_SIGNOFF,
                "file": str(coverage_md.relative_to(profile.project_root)),
                "asked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "answered": False,
                "reply_text": None,
            }
            if existing:
                existing.update(entry)
            else:
                inbox["messages"].append(entry)
            posted.append(entry)
        save_inbox(profile, feature, inbox)
        return {"gate": gate, "posted": posted, "skipped": skipped}

    # GATE_SCOPE or GATE_SPEC: question by question
    md = _gate_files(profile, feature, gate)[0]
    if not md.exists():
        raise SystemExit(f"file thiếu: {md}")
    questions = discover_questions(md, feature)
    if not questions:
        return {"gate": gate, "posted": [], "skipped": [], "note": "0 question discovered"}

    for q in questions:
        if q.has_pm_answer:
            skipped.append(q.anchor + " (already answered)")
            continue
        existing = find_inbox_entry(inbox, anchor=q.anchor)
        if existing and not force:
            skipped.append(q.anchor + " (already posted)")
            continue
        body = (
            f"{prefix} GATE — {gate}\n"
            f"[{q.anchor}]\n\n"
            f"{q.title}\n\n"
            f"{q.summary}\n\n"
            "Reply để Claude fold câu trả lời vào spec."
        )
        res = api.send_message(chat_id, body)
        entry = {
            "message_id": res["message_id"],
            "anchor": q.anchor,
            "gate": gate,
            "kind": KIND_QUESTION,
            "file": str(md.relative_to(profile.project_root)),
            "asked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "answered": False,
            "reply_text": None,
        }
        if existing:
            existing.update(entry)
        else:
            inbox["messages"].append(entry)
        posted.append(entry)

    save_inbox(profile, feature, inbox)
    return {"gate": gate, "posted": posted, "skipped": skipped}


# ---------------- Sync flow -------------------------------------------------


def sync_replies(profile: Profile, feature: str) -> dict[str, Any]:
    """Long-poll getUpdates once; fold any reply matching an inbox entry into
    the corresponding spec file. Returns summary dict."""
    api = telegram_from_profile(profile)
    inbox = load_inbox(profile, feature)
    last = int(inbox.get("last_update_id") or 0)

    updates = api.get_updates(offset=last + 1 if last else 0)
    folded: list[dict[str, Any]] = []
    ignored: list[dict[str, Any]] = []
    new_last = last

    for upd in updates:
        new_last = max(new_last, int(upd.get("update_id") or 0))
        msg = upd.get("message")
        if not msg:
            continue
        reply_to = (msg.get("reply_to_message") or {}).get("message_id")
        if not reply_to:
            ignored.append({"reason": "no reply_to", "update_id": upd.get("update_id")})
            continue
        entry = find_inbox_entry(inbox, message_id=int(reply_to))
        if not entry:
            ignored.append({"reason": "reply_to not in inbox", "reply_to": reply_to})
            continue
        if entry.get("answered"):
            ignored.append({"reason": "already answered", "anchor": entry["anchor"]})
            continue
        text = (msg.get("text") or "").strip()
        if not text:
            ignored.append({"reason": "empty text", "anchor": entry["anchor"]})
            continue
        target = profile.project_root / entry["file"]
        if not target.exists():
            ignored.append({"reason": "target file missing", "anchor": entry["anchor"]})
            continue

        if entry["kind"] == KIND_QUESTION:
            changed = _fold_question_reply(target, entry["anchor"], text)
            if not changed:
                ignored.append({"reason": "anchor not found in file", "anchor": entry["anchor"]})
                continue
            entry["answered"] = True
            entry["reply_text"] = text
            entry["reply_chat_message_id"] = msg.get("message_id")
            entry["replied_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            folded.append({"anchor": entry["anchor"], "file": entry["file"], "kind": "question"})
        elif entry["kind"] == KIND_COVERAGE_SIGNOFF:
            changed, verdict = _fold_coverage_signoff(target, text)
            if not changed:
                ignored.append({
                    "reason": "could not parse pass/fail (need `pass <reason>` or `fail <reason>`)",
                    "anchor": entry["anchor"],
                    "got": text[:80],
                })
                continue
            entry["answered"] = True
            entry["reply_text"] = text
            entry["reply_chat_message_id"] = msg.get("message_id")
            entry["replied_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            entry["verdict"] = verdict
            folded.append({
                "anchor": entry["anchor"], "file": entry["file"],
                "kind": "coverage_signoff", "verdict": verdict,
            })

    inbox["last_update_id"] = new_last
    save_inbox(profile, feature, inbox)

    pending = [m for m in inbox["messages"] if not m.get("answered")]
    return {
        "feature": feature,
        "folded": folded,
        "ignored": ignored,
        "pending_count": len(pending),
        "pending": [{"anchor": m["anchor"], "kind": m["kind"]} for m in pending],
        "last_update_id": new_last,
    }


# ---------------- CLI: re-spec-pm-init -------------------------------------


def main_init() -> int:
    """Help PM grab a chat_id by polling getUpdates and dumping latest chat."""
    ap = argparse.ArgumentParser(
        description="Lấy chat_id Telegram lần đầu. Người dùng nhắn 1 tin /start "
        "tới bot trước rồi chạy command này."
    )
    ap.add_argument("--token-env", default="TELEGRAM_BOT_TOKEN",
                    help="env var chứa bot token (default: TELEGRAM_BOT_TOKEN)")
    ap.add_argument("--timeout", type=int, default=30, help="long-poll timeout (s)")
    args = ap.parse_args()

    token = os.environ.get(args.token_env, "").strip()
    if not token:
        print(f"thiếu env var ${args.token_env} (lấy bot token từ @BotFather).",
              file=sys.stderr)
        return 1

    api = TelegramAPI(token=token, timeout_s=args.timeout)
    try:
        me = api.get_me()
    except TelegramError as e:
        print(f"getMe fail: {e}", file=sys.stderr)
        return 1
    print(f"bot     : @{me.get('username')} ({me.get('first_name')})")
    print(f"polling : {args.timeout}s — gửi /start tới bot từ Telegram của bạn now.")

    deadline = time.time() + args.timeout + 5
    offset = 0
    while time.time() < deadline:
        try:
            updates = api.get_updates(offset=offset)
        except TelegramError as e:
            print(f"getUpdates fail: {e}", file=sys.stderr)
            return 1
        for upd in updates:
            offset = max(offset, int(upd.get("update_id") or 0) + 1)
            msg = upd.get("message") or {}
            chat = msg.get("chat") or {}
            if not chat:
                continue
            print(f"\nDetected chat_id: {chat.get('id')}")
            print(f"  type    : {chat.get('type')}")
            print(f"  title   : {chat.get('title') or chat.get('username') or chat.get('first_name')}")
            print(f"\nPaste vào .spec-profile.yml:")
            print(f"  pm_channel:")
            print(f"    type: telegram")
            print(f"    chat_id: {chat.get('id')}")
            print(f"    token_env: {args.token_env}")
            return 0
    print("không nhận được message nào trong timeout — gửi /start tới bot rồi rerun.",
          file=sys.stderr)
    return 1


# ---------------- CLI: re-spec-pm-ask --------------------------------------


def main_ask() -> int:
    ap = argparse.ArgumentParser(description="Post Open Question / signoff prompt lên Telegram.")
    ap.add_argument("feature")
    ap.add_argument("--gate", required=True, choices=[GATE_SCOPE, GATE_COVERAGE, GATE_SPEC])
    ap.add_argument("--force", action="store_true",
                    help="repost dù đã có entry trong inbox (debug only)")
    args = ap.parse_args()

    try:
        profile = load_profile()
        result = ask_for_gate(profile, args.feature, args.gate, force=args.force)
    except SystemExit:
        raise
    except (TelegramError, FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    if not result.get("posted") and not result.get("skipped"):
        print("\n(không có Open Question nào để post)", file=sys.stderr)
    return 0


# ---------------- CLI: re-spec-pm-sync -------------------------------------


def main_sync() -> int:
    ap = argparse.ArgumentParser(
        description="Long-poll getUpdates, fold reply PM vào spec file."
    )
    ap.add_argument("feature")
    args = ap.parse_args()

    try:
        profile = load_profile()
        result = sync_replies(profile, args.feature)
    except SystemExit:
        raise
    except (TelegramError, FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    if result["pending_count"] > 0 and not result["folded"]:
        return 2  # signal: "no replies yet" — orchestrator can poll again
    return 0


if __name__ == "__main__":
    sys.exit(main_ask())
