"""nav_graph — persistent navigation graph for a feature crawl.

Storage: <profile.raw_root>/<feature>/nav_graph.json

    {
      "feature": "today",
      "screens": {
        "<screen_id>": {
          "id":         "<screen_id>",            # content hash
          "label":      "screen_01_landing",      # filename stem from capture
          "activity":   "MainActivity",
          "fragment":   "",                       # if exposed by Portal v0.6+
          "block":      "A",                      # optional, assigned later for clustering
          "first_seen": "2026-04-21T12:01:33Z",
          "captures":   ["screen_01_landing", "screen_01_landing_b"]
        }
      },
      "edges": [
        {"from": "<id>", "to": "<id>", "action": "tap:(540,905)",
         "label": "Verse card", "at": "..."}
      ]
    }

Idempotent: add_screen / add_edge can be called repeatedly with the same data
without duplication.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from re_spec_mobile.profile_loader import Profile, load_profile


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def screen_hash(state: dict[str, Any], window: int = 6) -> str:
    """Identity = sha1(package + activity + first <window> text/desc signatures).
    Stable across dynamic content (timers/avatars below the window). Override
    `window` via profile.capture.hash_window if needed.
    """
    phone = state.get("phone_state", {}) or {}
    activity = phone.get("current_activity", "") or phone.get("focusedWindow", "") or ""
    package = phone.get("current_package", "") or phone.get("focusedPackage", "") or ""

    tree = state.get("a11y_tree", []) or []
    sigs: list[str] = []

    def walk(nodes: Iterable[dict[str, Any]]) -> None:
        for n in nodes:
            txt = (n.get("text") or "").strip()
            desc = (n.get("content_description") or n.get("content-desc") or "").strip()
            if txt:
                sigs.append(f"T:{txt[:40]}")
            elif desc:
                sigs.append(f"D:{desc[:40]}")
            if len(sigs) >= window:
                return
            kids = n.get("children") or []
            if kids:
                walk(kids)
                if len(sigs) >= window:
                    return

    walk(tree)
    payload = "|".join([package, activity, *sigs])
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10]


class NavGraph:
    def __init__(self, feature: str, path: Path):
        self.feature = feature
        self.path = path
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = {"feature": feature, "screens": {}, "edges": []}
        self.data = data

    # --- screens ---
    def add_screen(
        self,
        screen_id: str,
        *,
        label: str,
        activity: str = "",
        fragment: str = "",
        block: str | None = None,
    ) -> dict[str, Any]:
        screens: dict[str, dict[str, Any]] = self.data.setdefault("screens", {})
        s = screens.get(screen_id)
        if s is None:
            s = {
                "id": screen_id,
                "label": label,
                "activity": activity,
                "fragment": fragment,
                "block": block,
                "first_seen": _now_iso(),
                "captures": [],
            }
            screens[screen_id] = s
        else:
            if block and not s.get("block"):
                s["block"] = block
            if activity and not s.get("activity"):
                s["activity"] = activity
            if fragment and not s.get("fragment"):
                s["fragment"] = fragment
        if label and label not in s["captures"]:
            s["captures"].append(label)
        return s

    def set_block(self, screen_id: str, block: str) -> None:
        s = self.data.setdefault("screens", {}).get(screen_id)
        if s:
            s["block"] = block

    # --- edges ---
    def add_edge(self, from_id: str, to_id: str, *, action: str, label: str = "") -> dict[str, Any]:
        edges: list[dict[str, Any]] = self.data.setdefault("edges", [])
        for e in edges:
            if e["from"] == from_id and e["to"] == to_id and e["action"] == action:
                return e
        edge = {"from": from_id, "to": to_id, "action": action, "label": label, "at": _now_iso()}
        edges.append(edge)
        return edge

    # --- persist ---
    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # --- queries ---
    def screen_by_label(self, label: str) -> dict[str, Any] | None:
        for s in self.data.get("screens", {}).values():
            if label in s.get("captures", []) or s.get("label") == label:
                return s
        return None

    def neighbors_out(self, screen_id: str) -> list[dict[str, Any]]:
        return [e for e in self.data.get("edges", []) if e["from"] == screen_id]

    def __repr__(self) -> str:
        n_screens = len(self.data.get("screens", {}))
        n_edges = len(self.data.get("edges", []))
        return f"NavGraph(feature={self.feature!r}, screens={n_screens}, edges={n_edges})"


def load(feature: str, profile: Profile | None = None) -> NavGraph:
    p = profile or load_profile()
    path = p.feature_raw_dir(feature) / "nav_graph.json"
    return NavGraph(feature, path)
