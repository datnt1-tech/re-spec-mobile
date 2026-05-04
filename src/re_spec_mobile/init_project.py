"""init_project.py — bootstrap a new app project for re-spec-mobile.

Phase 0 of the workflow. Run from the repo root of the app you want to spec:

    python init_project.py

What it does:
    1. Refuses if .spec-profile.yml already exists (delete it manually if you want to re-init)
    2. Writes a template .spec-profile.yml in CWD
    3. Tries to auto-detect device viewport via `adb shell wm size` and patches the template
    4. Creates the spec/ folder skeleton (feature/, screens/, ui_dumps/, _raw/, _graph/)
    5. Writes .mcp.json so Claude Code auto-loads the spec-graph MCP server in this repo
    6. Reminds the user to fill app.package + app.main_activity manually + run setup_portal.sh

Idempotent for steps 4-5; step 2 is one-shot.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

def _detect_viewport(serial: str | None = None) -> tuple[int, int] | None:
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += ["shell", "wm size"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
    except Exception:
        return None
    # output like: "Physical size: 1080x2400" or "Override size: ..."
    for line in out.splitlines():
        if "size:" in line.lower():
            try:
                w, h = line.split(":")[1].strip().split("x")
                return (int(w), int(h))
            except Exception:
                continue
    return None


def _detect_focused_app(serial: str | None = None) -> tuple[str, str] | None:
    """Return (package, activity) of currently focused app, if any."""
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += ["shell", "dumpsys window"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
    except Exception:
        return None
    for line in out.splitlines():
        if "mCurrentFocus" in line and "/" in line:
            # example: mCurrentFocus=Window{... com.example.app/com.example.app.MainActivity}
            try:
                tail = line.split()[-1].rstrip("}")
                pkg, act = tail.split("/")
                if act.startswith("."):
                    act = pkg + act
                return (pkg, act)
            except Exception:
                continue
    return None


def _write_profile(target: Path, viewport: tuple[int, int] | None,
                   focused: tuple[str, str] | None) -> None:
    from re_spec_mobile import paths
    try:
        template_path = paths.template("profile.template.yml")
        body = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # fallback to in-code bootstrap if template data missing
        from re_spec_mobile.profile_loader import BOOTSTRAP_TEMPLATE
        body = BOOTSTRAP_TEMPLATE

    if viewport is not None:
        body = body.replace("[1080, 2160]", f"[{viewport[0]}, {viewport[1]}]", 1)
    if focused is not None:
        pkg, act = focused
        body = body.replace("com.example.app", pkg)
        body = body.replace("com.example.app.MainActivity", act)

    target.write_text(body, encoding="utf-8")


def _scaffold_spec_dirs(root: Path) -> list[Path]:
    dirs = [
        root / "spec",
        root / "spec" / "feature",
        root / "spec" / "screens",
        root / "spec" / "ui_dumps",
        root / "spec" / "_raw",
        root / "spec" / "_graph",
        root / "spec" / "_contracts",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def _write_mcp_json(root: Path) -> Path:
    """Use the installed console script `re-spec-mcp-server` so .mcp.json
    works regardless of where the package was installed."""
    mcp_path = root / ".mcp.json"
    config = {
        "mcpServers": {
            "spec-graph": {
                "command": "re-spec-mcp-server",
                "args": [],
                "env": {},
            }
        }
    }
    mcp_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return mcp_path


def main() -> int:
    cwd = Path.cwd()
    profile_path = cwd / ".spec-profile.yml"
    if profile_path.exists():
        print(f"ERROR: {profile_path} already exists. Delete it first if you really want to re-init.", file=sys.stderr)
        return 1

    print(f"Initializing re-spec-mobile project at: {cwd}")

    print("\n[1/4] Detecting device state via adb (best effort)...")
    if not shutil.which("adb"):
        print("  WARN: `adb` not found on PATH. Continuing with template defaults.")
        viewport = None
        focused = None
    else:
        viewport = _detect_viewport()
        focused = _detect_focused_app()
        if viewport:
            print(f"  viewport = {viewport[0]}x{viewport[1]}")
        else:
            print("  viewport unknown (no device or wm-size failed)")
        if focused:
            print(f"  focused  = {focused[0]} / {focused[1]}")
        else:
            print("  focused app unknown (open the target app on device for autodetect)")

    print("\n[2/4] Writing .spec-profile.yml template...")
    _write_profile(profile_path, viewport, focused)
    print(f"  wrote {profile_path}")

    print("\n[3/4] Scaffolding spec/ directory tree...")
    for d in _scaffold_spec_dirs(cwd):
        rel = d.relative_to(cwd)
        print(f"  ensured {rel}/")

    print("\n[4/4] Writing .mcp.json (spec-graph MCP server pointer)...")
    if not shutil.which("re-spec-mcp-server"):
        print("  WARN: `re-spec-mcp-server` console script not on PATH; "
              ".mcp.json will be written but may not work until pip install completes.")
    path = _write_mcp_json(cwd)
    print(f"  wrote {path}")

    # Resolve bundled shell script paths so user can copy-paste
    try:
        from re_spec_mobile import paths
        setup_sh = str(paths.shell("setup_portal.sh"))
        register_sh = str(paths.shell("register-mcp-user.sh"))
    except Exception:
        setup_sh = "<bundled in package>/setup_portal.sh"
        register_sh = "<bundled in package>/register-mcp-user.sh"

    print(f"""
DONE. Next steps:

  1. Open .spec-profile.yml and:
     - confirm app.package + app.main_activity (autodetected if device was open)
     - fill navigation.tabs (id, label, center [x,y]) once the bottom-nav is mapped
     - add app-specific blocklist.custom patterns (paywall CTAs, destructive verbs)

  2. Verify the device + Portal:
     bash "{setup_sh}"

  3. (Optional) Register the MCP user-scope so other Claude sessions can also query:
     bash "{register_sh}"

  4. Trigger the workflow from Claude Code:
     /re-spec-mobile

  All Python tools are now console commands (no path needed):
     re-spec-init               re-spec-build-graph        re-spec-coverage-report
     re-spec-profile            re-spec-validate           re-spec-render-nav
     re-spec-scope              re-spec-query              re-spec-observations
     re-spec-capture            re-spec-mcp-server         re-spec-coverage-check
     re-spec-paths              (show bundled data file locations)
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
