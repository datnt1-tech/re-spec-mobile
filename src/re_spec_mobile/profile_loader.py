"""profile_loader.py — load and validate `.spec-profile.yml` for re-spec-mobile.

Walks up from CWD (or a provided start dir) to find `.spec-profile.yml`, parses
it, applies defaults from profile.schema.yml, resolves paths relative to the
project root (= dir containing the profile), and exposes a typed `Profile`
dataclass that all bundled tools import.

Usage (Python):
    from profile_loader import load_profile
    p = load_profile()
    p.spec_root      # Path
    p.blocklist_re   # compiled regex

Usage (CLI):
    python profile_loader.py                    # print resolved profile
    python profile_loader.py --validate         # exit 1 if invalid
    python profile_loader.py --validate <path>  # validate specific file
    python profile_loader.py --bootstrap        # write template profile to CWD
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------- universal-safe blocklist defaults ------------------------------
# These are the destructive / paywall / external-share patterns we never want
# the auto-test agent to tap. App-specific patterns are appended via
# profile.blocklist.custom; flip profile.blocklist.use_defaults to drop these.
DEFAULT_BLOCKLIST: list[str] = [
    r"\btry for free\b",
    r"\bsubscribe\b",
    r"\bbuy\b",
    r"\bpurchase\b",
    r"\bconfirm purchase\b",
    r"\bsend\b",
    r"\bsubmit\b",
    r"\bpost\b",
    r"\bdelete\b",
    r"\bremove\b",
    r"\blog ?out\b",
    r"\bsign ?out\b",
    r"\brestore\b",
    r"\bupgrade\b",
    r"\bstart trial\b",
    r"\bstart free trial\b",
    r"^continue$",
    r"^share$",
]


# ---------- defaults (mirror profile.schema.yml) ---------------------------
PATH_DEFAULTS: dict[str, str] = {
    "spec_root":       "spec",
    "feature_root":    "spec/feature",
    "screens_root":    "spec/screens",
    "dumps_root":      "spec/ui_dumps",
    "raw_root":        "spec/_raw",
    "graph_root":      "spec/_graph",
    "contracts_root":  "spec/_contracts",
}

SCROLL_DEFAULTS = {"default_swipe_duration_ms": 800, "long_swipe_duration_ms": 1200, "edge_swipe_x": 200}
SETTLE_DEFAULTS = {"default_ms": 800, "modal_ms": 1500, "ai_generation_ms": 10000}
CAPTURE_DEFAULTS = {"filename_pattern": "screen_{nn:02d}_{label}", "hash_window": 6}


@dataclass
class Tab:
    id: str
    label: str
    center: tuple[int, int]
    resource_id: str = ""
    default: bool = False


@dataclass
class Profile:
    project_root: Path
    profile_path: Path

    # app
    app_name: str
    package: str
    main_activity: str
    min_sdk: int = 0
    target_sdk: int = 0
    app_version: str = ""
    stack: str = "unknown"

    # device
    serial: str = ""
    viewport: tuple[int, int] = (1080, 1920)
    locale: str = "en-US"
    density: int = 0

    # navigation
    nav_type: str = "none"
    tabs: list[Tab] = field(default_factory=list)

    # blocklist
    blocklist_patterns: list[str] = field(default_factory=list)
    blocklist_re: re.Pattern[str] = field(default_factory=lambda: re.compile(""))

    # paths (all absolute)
    spec_root: Path = field(default_factory=Path)
    feature_root: Path = field(default_factory=Path)
    screens_root: Path = field(default_factory=Path)
    dumps_root: Path = field(default_factory=Path)
    raw_root: Path = field(default_factory=Path)
    graph_root: Path = field(default_factory=Path)
    contracts_root: Path = field(default_factory=Path)

    # reference style
    canonical_feature: str | None = None
    style: str = "opinionated"

    # tunables
    scroll: dict[str, int] = field(default_factory=lambda: dict(SCROLL_DEFAULTS))
    settle: dict[str, int] = field(default_factory=lambda: dict(SETTLE_DEFAULTS))
    capture: dict[str, Any] = field(default_factory=lambda: dict(CAPTURE_DEFAULTS))
    modals: dict[str, Any] = field(default_factory=dict)

    raw: dict[str, Any] = field(default_factory=dict)

    # ---- convenience ----
    def default_tab(self) -> Tab | None:
        for t in self.tabs:
            if t.default:
                return t
        return self.tabs[0] if self.tabs else None

    def tab_by_id(self, tab_id: str) -> Tab | None:
        for t in self.tabs:
            if t.id == tab_id:
                return t
        return None

    def feature_dir(self, feature: str) -> Path:
        return self.feature_root / feature

    def feature_screens_dir(self, feature: str) -> Path:
        return self.screens_root / feature

    def feature_dumps_dir(self, feature: str) -> Path:
        return self.dumps_root / feature

    def feature_raw_dir(self, feature: str) -> Path:
        return self.raw_root / feature


# ---------- discovery + parse ---------------------------------------------


def find_profile(start_dir: Path | None = None) -> Path | None:
    """Find profile path. Order:
       1. SPEC_PROFILE env var (explicit override)
       2. Walk up from start_dir / CWD looking for .spec-profile.yml
    Returns None if neither succeeds.
    """
    env_path = os.environ.get("SPEC_PROFILE")
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if candidate.is_file():
            return candidate
        return None  # explicit env var that doesn't exist = error, not fallback
    cur = (start_dir or Path.cwd()).resolve()
    for d in [cur, *cur.parents]:
        candidate = d / ".spec-profile.yml"
        if candidate.is_file():
            return candidate
    return None


def load_profile(start_dir: Path | None = None) -> Profile:
    """Find + parse profile. Raises FileNotFoundError if not present.
    Honors $SPEC_PROFILE env var as explicit override."""
    path = find_profile(start_dir)
    if path is None:
        env_hint = os.environ.get("SPEC_PROFILE")
        if env_hint:
            raise FileNotFoundError(
                f"$SPEC_PROFILE points at {env_hint} but that file doesn't exist."
            )
        raise FileNotFoundError(
            "No .spec-profile.yml found in CWD or any parent directory. "
            "Run `python tools/profile_loader.py --bootstrap` to create one, "
            "or `/re-spec-mobile init` from Claude. "
            "Or set $SPEC_PROFILE=<path> to point at a specific profile."
        )
    return parse_profile(path)


def parse_profile(path: Path) -> Profile:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected mapping at root, got {type(raw).__name__}")

    root = path.parent.resolve()

    # required block presence
    for key in ("app", "device", "navigation", "paths"):
        if key not in raw:
            raise ValueError(f"{path}: missing required top-level key `{key}`")

    app = raw["app"]
    device = raw["device"]
    nav = raw["navigation"]
    paths = raw.get("paths") or {}
    blk = raw.get("blocklist") or {}
    ref = raw.get("reference") or {}

    # blocklist
    use_defaults = bool(blk.get("use_defaults", True))
    custom = list(blk.get("custom") or [])
    pats = (DEFAULT_BLOCKLIST if use_defaults else []) + custom
    # Plain literals from `custom` are wrapped with case-insensitive substring match;
    # we accept regex too — heuristic: if a pattern contains regex metas, treat as-is.
    safe_pats: list[str] = []
    metas = set("\\^$.|?*+()[]{}")
    for p in pats:
        if any(c in metas for c in p):
            safe_pats.append(p)
        else:
            safe_pats.append(re.escape(p))
    blocklist_re = re.compile("|".join(safe_pats), re.IGNORECASE) if safe_pats else re.compile("$^")

    # tabs
    tabs: list[Tab] = []
    for raw_tab in nav.get("tabs") or []:
        center = raw_tab.get("center")
        if not center or len(center) != 2:
            raise ValueError(f"{path}: tab `{raw_tab.get('id', '?')}` missing valid center [x, y]")
        tabs.append(Tab(
            id=raw_tab["id"],
            label=raw_tab["label"],
            center=(int(center[0]), int(center[1])),
            resource_id=raw_tab.get("resource_id", ""),
            default=bool(raw_tab.get("default", False)),
        ))

    # path resolution
    def _p(key: str) -> Path:
        return (root / (paths.get(key) or PATH_DEFAULTS[key])).resolve()

    return Profile(
        project_root=root,
        profile_path=path,

        app_name=app.get("name") or app["package"],
        package=app["package"],
        main_activity=app["main_activity"],
        min_sdk=int(app.get("min_sdk") or 0),
        target_sdk=int(app.get("target_sdk") or 0),
        app_version=str(app.get("app_version") or ""),
        stack=app.get("stack", "unknown"),

        serial=str(device.get("serial", "")),
        viewport=(int(device["viewport"][0]), int(device["viewport"][1])),
        locale=device.get("locale", "en-US"),
        density=int(device.get("density") or 0),

        nav_type=nav["type"],
        tabs=tabs,

        blocklist_patterns=safe_pats,
        blocklist_re=blocklist_re,

        spec_root=_p("spec_root"),
        feature_root=_p("feature_root"),
        screens_root=_p("screens_root"),
        dumps_root=_p("dumps_root"),
        raw_root=_p("raw_root"),
        graph_root=_p("graph_root"),
        contracts_root=_p("contracts_root"),

        canonical_feature=ref.get("canonical_feature"),
        style=ref.get("style", "opinionated"),

        scroll={**SCROLL_DEFAULTS, **(raw.get("scroll") or {})},
        settle={**SETTLE_DEFAULTS, **(raw.get("settle") or {})},
        capture={**CAPTURE_DEFAULTS, **(raw.get("capture") or {})},
        modals=raw.get("modals") or {},

        raw=raw,
    )


# ---------- bootstrap a template profile -----------------------------------

BOOTSTRAP_TEMPLATE = """\
# .spec-profile.yml — re-spec-mobile project profile.
# Edit values then `bash skill_tools/setup_portal.sh` to verify device.
version: 1

app:
  name: "REPLACE_ME"                              # Human label, used in spec titles
  package: com.example.app                        # Android package id
  main_activity: com.example.app.MainActivity     # Fully qualified main Activity
  min_sdk: 24
  target_sdk: 34
  app_version: "1.0.0"
  stack: compose                                  # compose | view_xml | mixed | flutter | react_native | unknown

device:
  serial: ""                                      # Empty = auto-detect single device
  viewport: [1080, 2160]                          # px [w, h] — `adb shell wm size`
  locale: en-US
  density: 440                                    # optional, `adb shell wm density`

navigation:
  type: bottom_nav                                # bottom_nav | drawer | top_tabs | none | custom
  tabs: []                                        # fill after `init` discovers main activity layout
  # Example tab entry (centre = tap coordinate of the tab cell):
  #   - id: home
  #     label: Home
  #     resource_id: nav_home
  #     center: [216, 1918]
  #     default: true

blocklist:
  use_defaults: true                              # Include universal-safe patterns (Subscribe / Buy / Logout / ...)
  custom: []                                      # App-specific extras, literals or regex

paths:
  spec_root: spec
  feature_root: spec/feature
  screens_root: spec/screens
  dumps_root: spec/ui_dumps
  raw_root: spec/_raw
  graph_root: spec/_graph
  contracts_root: spec/_contracts

reference:
  canonical_feature: null                         # null → fall back to skill-bundled canonical/
  style: opinionated                              # opinionated (3-layer) | minimal (1-file)

scroll:
  default_swipe_duration_ms: 800
  long_swipe_duration_ms: 1200
  edge_swipe_x: 200                               # Mép trái x-coord when center is overlaid

settle:
  default_ms: 800
  modal_ms: 1500
  ai_generation_ms: 10000

capture:
  filename_pattern: "screen_{nn:02d}_{label}"
  hash_window: 6

modals:
  back_traps: []                                  # Activities where KEYCODE_BACK is trapped (use swipe-down)
  swipe_down_dismiss: true
"""


def bootstrap(target_dir: Path) -> Path:
    target = target_dir / ".spec-profile.yml"
    if target.exists():
        raise FileExistsError(f"{target} already exists; refuse to overwrite.")
    target.write_text(BOOTSTRAP_TEMPLATE, encoding="utf-8")
    return target


# ---------- CLI ------------------------------------------------------------


def _summary(p: Profile) -> dict[str, Any]:
    return {
        "project_root": str(p.project_root),
        "profile_path": str(p.profile_path),
        "app": {
            "name": p.app_name, "package": p.package, "main_activity": p.main_activity,
            "stack": p.stack, "version": p.app_version,
        },
        "device": {"serial": p.serial, "viewport": list(p.viewport), "locale": p.locale, "density": p.density},
        "navigation": {"type": p.nav_type, "tabs": [
            {"id": t.id, "label": t.label, "center": list(t.center), "default": t.default} for t in p.tabs
        ]},
        "blocklist": {"count": len(p.blocklist_patterns)},
        "paths": {
            "spec_root": str(p.spec_root),
            "feature_root": str(p.feature_root),
            "screens_root": str(p.screens_root),
            "dumps_root": str(p.dumps_root),
            "raw_root": str(p.raw_root),
            "graph_root": str(p.graph_root),
        },
        "reference": {"canonical_feature": p.canonical_feature, "style": p.style},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", nargs="?", const="__cwd__",
                    help="validate profile (optional path; defaults to discovered file)")
    ap.add_argument("--bootstrap", action="store_true",
                    help="write template .spec-profile.yml in CWD")
    ap.add_argument("--show", action="store_true", help="print resolved profile JSON (default)")
    args = ap.parse_args()

    if args.bootstrap:
        try:
            path = bootstrap(Path.cwd())
        except FileExistsError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"wrote {path}\nedit it then re-run: python tools/profile_loader.py --validate")
        return 0

    if args.validate is not None:
        try:
            if args.validate == "__cwd__":
                p = load_profile()
            else:
                p = parse_profile(Path(args.validate))
        except Exception as e:
            print(f"INVALID: {e}", file=sys.stderr)
            return 1
        print(f"OK   {p.profile_path}")
        print(f"     app    = {p.app_name} ({p.package})")
        print(f"     tabs   = {len(p.tabs)}")
        print(f"     specs  = {p.spec_root}")
        return 0

    # default: show
    try:
        p = load_profile()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(_summary(p), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
