#!/usr/bin/env bash
# Register the spec-graph MCP server at USER scope so every Claude Code
# session on this machine (regardless of cwd) can query the per-project spec
# graph found by walking up from CWD looking for .spec-profile.yml.
#
# Idempotent: safe to rerun. Uninstall: `claude mcp remove spec-graph -s user`.

set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  echo "✗ 'claude' CLI not found in PATH"
  exit 1
fi

if ! command -v re-spec-mcp-server >/dev/null 2>&1; then
  echo "✗ re-spec-mcp-server not on PATH — run 'pip install re-spec-mobile' first"
  exit 1
fi

# Remove any stale user-scope entry first so path updates propagate cleanly.
claude mcp remove spec-graph -s user 2>/dev/null || true

# Use the installed console script directly. Works regardless of where pip
# put the package (system / user / venv).
claude mcp add spec-graph --scope user -- re-spec-mcp-server

echo
echo "✓ spec-graph registered at user scope → re-spec-mcp-server"
echo "  Verify in any directory: claude mcp list | grep spec-graph"
echo "  Remove:                  claude mcp remove spec-graph -s user"
echo
echo "Note: each session resolves .spec-profile.yml by walking up from CWD."
echo "      Set SPEC_PROFILE=<path> env var to override."
