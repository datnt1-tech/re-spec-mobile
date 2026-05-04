"""capture.py — take a Portal-backed snapshot of the current device screen.

Usage (via capture.sh):
    python capture.py <feature> <name> [--from <parent_label_or_id>] [--via <action>]
                                        [--settle-ms 800] [--block <letter>]
                                        [--serial <adb_serial>]

Outputs (paths from .spec-profile.yml):
    <screens_root>/<feature>/<name>.png   # screencap (overlay must be off)
    <dumps_root>/<feature>/<name>.json    # normalized Portal a11y_tree + phone_state
    <dumps_root>/<feature>/<name>.xml     # uiautomator-compat XML projection
    <raw_root>/<feature>/nav_graph.json   # updated nav graph

Why bypass droidrun.AdbTools.get_state():
    Portal v0.6.x returns {"status":"success","result":"<json>"} where the
    inner JSON has fields like {"className","resourceId","bounds":"x,y,x,y"}.
    droidrun 0.3.x parses against the older {"data":...} envelope with
    {"class_name","resource_id","bounds":{...}} → version mismatch errors.

We do raw `adb shell content query --uri content://com.droidrun.portal/state`
+ in-process normalisation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from re_spec_mobile.nav_graph import NavGraph, load as load_graph, screen_hash
from re_spec_mobile.profile_loader import load_profile


def _ensure_dirs(profile, feature: str) -> tuple[Path, Path, Path]:
    screens_dir = profile.feature_screens_dir(feature)
    dumps_dir = profile.feature_dumps_dir(feature)
    raw_dir = profile.feature_raw_dir(feature)
    for d in (screens_dir, dumps_dir, raw_dir):
        d.mkdir(parents=True, exist_ok=True)
    return screens_dir, dumps_dir, raw_dir


def _adb(args: list[str], *, serial: str | None = None) -> bytes:
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    return subprocess.check_output(cmd)


def _portal_state(serial: str | None = None) -> dict[str, Any]:
    raw = _adb(
        ["shell", "content query --uri content://com.droidrun.portal/state"],
        serial=serial,
    ).decode("utf-8", errors="replace")

    m = re.search(r"result=(.*)", raw, re.DOTALL)
    if not m:
        raise RuntimeError(f"Unexpected Portal response (no 'result='): {raw[:200]!r}")
    outer = json.loads(m.group(1).strip())
    if outer.get("status") != "success":
        raise RuntimeError(f"Portal returned non-success: {outer}")
    inner_str = outer.get("result")
    if not inner_str:
        raise RuntimeError(f"Portal envelope missing 'result' field: {outer!r}")
    inner = json.loads(inner_str)

    raw_tree = inner.get("a11y_tree") or []
    raw_phone = inner.get("phone_state") or {}

    return {
        "phone_state": _normalize_phone(raw_phone),
        "a11y_tree": [_normalize_node(n) for n in raw_tree],
    }


def _normalize_phone(p: dict[str, Any]) -> dict[str, Any]:
    return {
        "current_app": p.get("currentApp", ""),
        "current_package": p.get("packageName", ""),
        "current_activity": p.get("activityName", ""),
        "keyboard_visible": p.get("keyboardVisible", False),
        "is_editable": p.get("isEditable", False),
        "focused_element": p.get("focusedElement") or {},
    }


_BOUNDS_RE = re.compile(r"\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*")


def _normalize_node(n: dict[str, Any]) -> dict[str, Any]:
    cls = n.get("className", "") or ""
    text = n.get("text", "") or ""
    real_text = "" if text == cls else text
    rid = n.get("resourceId", "") or ""

    bounds_raw = n.get("bounds", "") or ""
    m = _BOUNDS_RE.match(bounds_raw)
    if m:
        x1, y1, x2, y2 = (int(g) for g in m.groups())
        bounds = {"left": x1, "top": y1, "right": x2, "bottom": y2}
    else:
        bounds = bounds_raw

    has_real_signal = bool(real_text) or bool(rid)

    return {
        "index": n.get("index"),
        "class_name": cls,
        "resource_id": rid,
        "text": real_text,
        "content_description": "" if real_text else (text if text and text != cls else ""),
        "clickable": has_real_signal,
        "bounds": bounds,
        "children": [_normalize_node(c) for c in (n.get("children") or [])],
    }


def _to_xml(state: dict[str, Any]) -> str:
    tree = state.get("a11y_tree") or []
    phone = state.get("phone_state") or {}
    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<hierarchy rotation="0" activity="{_esc(phone.get("current_activity", ""))}" package="{_esc(phone.get("current_package", ""))}">',
    ]

    def walk(nodes: Iterable[dict[str, Any]], depth: int) -> None:
        indent = "  " * (depth + 1)
        for n in nodes:
            cls = n.get("class_name") or "View"
            text = n.get("text") or ""
            desc = n.get("content_description") or ""
            rid = n.get("resource_id") or ""
            clickable = "true" if n.get("clickable") else "false"
            bounds = n.get("bounds") or ""
            if isinstance(bounds, dict):
                b = bounds
                bstr = f'[{b.get("left", 0)},{b.get("top", 0)}][{b.get("right", 0)},{b.get("bottom", 0)}]'
            elif isinstance(bounds, (list, tuple)) and len(bounds) == 4:
                bstr = f'[{bounds[0]},{bounds[1]}][{bounds[2]},{bounds[3]}]'
            else:
                bstr = str(bounds)
            kids = n.get("children") or []
            tag = (
                f'{indent}<node class="{_esc(str(cls))}" text="{_esc(str(text))}" '
                f'content-desc="{_esc(str(desc))}" resource-id="{_esc(str(rid))}" '
                f'clickable="{clickable}" bounds="{_esc(bstr)}"'
            )
            if kids:
                lines.append(tag + ">")
                walk(kids, depth + 1)
                lines.append(f"{indent}</node>")
            else:
                lines.append(tag + "/>")

    walk(tree, 0)
    lines.append("</hierarchy>")
    return "\n".join(lines) + "\n"


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _resolve_screen_ref(g: NavGraph, ref: str) -> str | None:
    screens = g.data.get("screens", {})
    if ref in screens:
        return ref
    s = g.screen_by_label(ref)
    return s["id"] if s else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("name", help="filename stem, e.g. screen_01_landing")
    ap.add_argument("--from", dest="from_ref", help="parent screen_id or label")
    ap.add_argument("--via", dest="action", help="action text, e.g. 'tap:(540,1100) Verse card'")
    ap.add_argument("--settle-ms", type=int, default=None, help="sleep between action and capture (default: profile.settle.default_ms)")
    ap.add_argument("--block", help="optional block letter/number for subgraph clustering")
    ap.add_argument("--serial", help="adb serial (overrides profile.device.serial)")
    ap.add_argument("--no-edge", action="store_true", help="record screen only, skip edge")
    args = ap.parse_args()

    if (args.from_ref and not args.action) or (args.action and not args.from_ref):
        print("ERROR: --from and --via must be given together (or both omitted).", file=sys.stderr)
        return 2

    try:
        profile = load_profile()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    serial = args.serial or (profile.serial or None)
    settle_ms = args.settle_ms if args.settle_ms is not None else profile.settle["default_ms"]

    _ensure_dirs(profile, args.feature)
    g = load_graph(args.feature, profile=profile)

    time.sleep(settle_ms / 1000.0)

    try:
        state = _portal_state(serial=serial)
    except Exception as exc:
        print(f"ERROR: Portal state read failed: {exc}", file=sys.stderr)
        return 1

    try:
        png_bytes = _adb(["exec-out", "screencap", "-p"], serial=serial)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: screencap failed: {e}", file=sys.stderr)
        return 1

    screens_dir = profile.feature_screens_dir(args.feature)
    dumps_dir = profile.feature_dumps_dir(args.feature)

    png_path = screens_dir / f"{args.name}.png"
    json_path = dumps_dir / f"{args.name}.json"
    xml_path = dumps_dir / f"{args.name}.xml"

    png_path.write_bytes(png_bytes)
    json_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    xml_path.write_text(_to_xml(state), encoding="utf-8")

    sid = screen_hash(state, window=int(profile.capture.get("hash_window", 6)))
    phone = state.get("phone_state") or {}
    g.add_screen(
        sid,
        label=args.name,
        activity=str(phone.get("current_activity", "")),
        fragment="",
        block=args.block,
    )

    edge_info = ""
    if args.from_ref and args.action and not args.no_edge:
        parent_id = _resolve_screen_ref(g, args.from_ref)
        if parent_id is None:
            print(f"WARN: parent '{args.from_ref}' not in graph yet; recording edge with literal ref", file=sys.stderr)
            parent_id = args.from_ref
        g.add_edge(parent_id, sid, action=args.action, label=args.action)
        edge_info = f"EDGE {parent_id} -> {sid} via {args.action}"

    g.save()

    print(f"CAPTURED {args.name}")
    print(f"SCREEN_ID {sid}")
    print(f"ACTIVITY {phone.get('current_activity', '')}")
    print(f"PNG {png_path}")
    print(f"JSON {json_path}")
    print(f"XML {xml_path}")
    if edge_info:
        print(edge_info)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
