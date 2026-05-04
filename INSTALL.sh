#!/usr/bin/env bash
# INSTALL.sh — install re-spec-mobile end-to-end:
#   1. pip install the Python package (provides 13 console scripts + bundled data)
#   2. Symlink (or copy) skill SKILL.md + agent .md files into ~/.claude/
#
# Modes:
#   --symlink   (default) symlink skill + agents into ~/.claude/ — git pull updates live
#   --copy      copy skill + agents (better for production / ship)
#   --no-pip    skip pip install (assume already installed)
#   --user-pip  use `pip install --user` instead of system/venv
#   --no-skill  skip skill+agent install (Python only)
#
# Idempotent: re-running replaces existing symlinks/copies. Files NOT managed
# by this installer are left alone.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/skills/re-spec-mobile"
AGENT_SRC_DIR="$SCRIPT_DIR/agents"
EXAMPLE_SRC_DIR="$SCRIPT_DIR/examples"

SKILL_DST="$HOME/.claude/skills/re-spec-mobile"
AGENT_DST_DIR="$HOME/.claude/agents"

MODE="symlink"
DO_PIP=1
USER_PIP=0
DO_SKILL=1
for arg in "$@"; do
  case "$arg" in
    --copy)     MODE="copy" ;;
    --symlink)  MODE="symlink" ;;
    --no-pip)   DO_PIP=0 ;;
    --user-pip) USER_PIP=1 ;;
    --no-skill) DO_SKILL=0 ;;
    --help|-h)  sed -n '2,18p' "$0"; exit 0 ;;
    *)          echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

banner() { printf "\n\033[1;36m=== %s ===\033[0m\n" "$*"; }
ok()     { printf "\033[1;32m✓\033[0m %s\n" "$*"; }
warn()   { printf "\033[1;33m!\033[0m %s\n" "$*"; }
fail()   { printf "\033[1;31m✗\033[0m %s\n" "$*"; exit 1; }

# ---------- 1. Python package via pip ----------
if [[ "$DO_PIP" == "1" ]]; then
  banner "1. pip install re-spec-mobile (editable)"
  command -v pip >/dev/null || command -v pip3 >/dev/null || \
    fail "pip not on PATH; install Python first or pass --no-pip"

  PIP_BIN=$(command -v pip3 || command -v pip)
  PIP_FLAGS="-e"
  if [[ "$USER_PIP" == "1" ]]; then
    PIP_FLAGS="$PIP_FLAGS --user"
  fi

  # Install editable so live edits in src/re_spec_mobile/ propagate.
  # User who wants pinned install can run: pip install <wheel> instead.
  "$PIP_BIN" install $PIP_FLAGS "$SCRIPT_DIR" 2>&1 | tail -5 || \
    fail "pip install failed; check error above"
  ok "Console scripts installed:"
  ls "$(dirname "$(command -v re-spec-init 2>/dev/null || echo /tmp/none)")" 2>/dev/null \
    | grep "^re-spec" | sed 's/^/    /' || warn "  re-spec-* not on PATH yet (may need shell reload)"
else
  warn "[1] pip install skipped (--no-pip)"
fi

# ---------- 2. Skill + agents into ~/.claude ----------
if [[ "$DO_SKILL" != "1" ]]; then
  banner "DONE (--no-skill)"
  exit 0
fi

banner "2. Skill SKILL.md → $SKILL_DST"
[[ -d "$SKILL_SRC" ]] || fail "missing $SKILL_SRC"
mkdir -p "$HOME/.claude/skills"
if [[ -e "$SKILL_DST" || -L "$SKILL_DST" ]]; then
  warn "removing existing $SKILL_DST"
  rm -rf "$SKILL_DST"
fi
if [[ "$MODE" == "symlink" ]]; then
  ln -s "$SKILL_SRC" "$SKILL_DST"
  ok "symlinked"
else
  cp -r "$SKILL_SRC" "$SKILL_DST"
  ok "copied"
fi

banner "3. Agents → $AGENT_DST_DIR"
[[ -d "$AGENT_SRC_DIR" ]] || fail "missing $AGENT_SRC_DIR"
mkdir -p "$AGENT_DST_DIR"
for agent_file in "$AGENT_SRC_DIR"/*.md; do
  [[ -f "$agent_file" ]] || continue
  agent_name=$(basename "$agent_file")
  dst="$AGENT_DST_DIR/$agent_name"
  if [[ -e "$dst" || -L "$dst" ]]; then
    warn "replacing $agent_name"
    rm -f "$dst"
  fi
  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$agent_file" "$dst"
  else
    cp "$agent_file" "$dst"
  fi
  ok "$agent_name"
done

banner "4. Example profiles"
ok "browse $EXAMPLE_SRC_DIR/ for sample .spec-profile.yml files"
ls "$EXAMPLE_SRC_DIR" | sed 's/^/    /'

# ---------- DONE ----------
banner "DONE"
cat <<EOF

Skill installed at  : $SKILL_DST
Agents installed at : $AGENT_DST_DIR
Python package      : pip install -e $SCRIPT_DIR

Console scripts (run from anywhere):
  re-spec-init               re-spec-build-graph        re-spec-coverage-report
  re-spec-profile            re-spec-validate           re-spec-render-nav
  re-spec-scope              re-spec-query              re-spec-observations
  re-spec-capture            re-spec-mcp-server         re-spec-coverage-check
  re-spec-paths              (show bundled data file locations)

Next steps for a new app project:

  1. cd into your target app project root
  2. Initialize:
       re-spec-init
  3. Edit the generated .spec-profile.yml
  4. Set up Portal on your device:
       bash \$(re-spec-paths --shell setup_portal.sh)
  5. Open Claude Code in the project + invoke:
       /re-spec-mobile

To register the spec-graph MCP at user-scope:
  bash \$(re-spec-paths --shell register-mcp-user.sh)

To uninstall:
  pip uninstall re-spec-mobile
  rm "$SKILL_DST"
  rm "$AGENT_DST_DIR/app-explorer.md" "$AGENT_DST_DIR/spec-writer.md"
  claude mcp remove spec-graph -s user 2>/dev/null || true

EOF
