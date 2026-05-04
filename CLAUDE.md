# CLAUDE.md

This file is read automatically by Claude Code at the start of every conversation
in the `re-spec-mobile` repo.

## Project Purpose

**Spec-first reverse-engineering toolkit for Android apps.** Drives a connected
device, captures every screen of a feature, then produces a 3-layer markdown
spec corpus (observations + flow + implementation) that engineers can rebuild
the feature from without ever running the original app.

App-agnostic by design: every app-specific value (package, viewport, blocklist,
nav tabs, paths, reference style) lives in a per-project `.spec-profile.yml`.

## Origin

Extracted from `bible-agent/spec/tools/` (a sibling repo). bible-agent is the
source material — **do NOT edit it from this repo**. All toolkit changes belong
in `src/re_spec_mobile/`. See `docs/MIGRATION.md` for the relationship.

## Key Facts

- **Stack:** Python 3.10+ (pip-installable, src-layout per PEP 518)
- **Required deps:** `pyyaml>=6.0`
- **Optional:** `droidrun>=0.3,<0.6` via `pip install re-spec-mobile[device]`
- **Build:** `python -m build` (needs venv — system pip is PEP 668 blocked)
- **CLI:** 13 console scripts on PATH after install (`re-spec-*`)
- **Distribution:** wheel + sdist in `dist/`, install via `INSTALL.sh`

## Repo Layout (3 buckets, 3 install mechanisms)

```
src/re_spec_mobile/          ← PIP install (Python package)
  ├── *.py                    13 modules — actual code
  └── _data/                  Bundled via package_data + importlib.resources
      ├── templates/          7 .tmpl files (scope, observations, spec, ...)
      ├── canonical/          5 reference files (sample specs, schema)
      └── _shell/             3 shell scripts (setup_portal, register-mcp, version)

skills/re-spec-mobile/       ← SYMLINK to ~/.claude/skills/ (Claude Code reads)
  └── SKILL.md               10-phase orchestrator + 3 PM gates

agents/                      ← SYMLINK to ~/.claude/agents/ (Claude Code reads)
  ├── app-explorer.md        Sub-agent: device capture (sonnet)
  └── spec-writer.md         Sub-agent: prose generation (opus)

docs/                        ← Operations + dogfood report + roadmap
examples/                    ← Sample .spec-profile.yml (bible-agent)
INSTALL.sh                   ← pip install + symlink in one shot
pyproject.toml               ← Package metadata + 13 entry_points
```

**Rule:** `src/` is the single source of truth for Python code AND bundled data.
Never duplicate templates/canonical into `skills/` — Claude Code does not need
them; the Python tools resolve them via `re-spec-paths`.

## Common Commands

```bash
# Install in dev mode (editable) — recommended while developing
bash INSTALL.sh                    # pip install -e + symlink skill+agents

# Build wheel + sdist for distribution
.venv/bin/python -m build          # outputs to dist/
# or: python3 -m venv /tmp/venv && /tmp/venv/bin/pip install build && /tmp/venv/bin/python -m build

# Test the installed CLI
re-spec-paths                      # show bundled data file inventory
re-spec-profile                    # validate .spec-profile.yml in CWD
re-spec-mcp-server                 # start spec-graph MCP server (stdio)

# Smoke test against bible-agent baseline
cd ../bible-agent && re-spec-build-graph && re-spec-validate
# Should match: 164 nodes, 208 edges, 48 validate errors (legacy schema gaps)
```

## Where to make changes

| You want to... | Edit this | NOT this |
|---|---|---|
| Add/change Python tool logic | `src/re_spec_mobile/<name>.py` | `bible-agent/spec/tools/` (origin, frozen) |
| Add a new CLI command | `pyproject.toml` `[project.scripts]` + new `src/re_spec_mobile/<name>.py` | — |
| Update spec template | `src/re_spec_mobile/_data/templates/<name>.md.tmpl` | `templates/` (doesn't exist — was deleted) |
| Update reference style | `src/re_spec_mobile/_data/canonical/<name>.sample.md` | `canonical/` (doesn't exist) |
| Update Portal setup script | `src/re_spec_mobile/_data/_shell/setup_portal.sh` | — |
| Update orchestrator workflow | `skills/re-spec-mobile/SKILL.md` | inside src/ (Claude Code can't see) |
| Update sub-agent behaviour | `agents/{app-explorer,spec-writer}.md` | inside src/ |
| Update install flow | `INSTALL.sh` | — |

After editing bundled `_data/` files: rebuild wheel (`python -m build`) +
reinstall (`pip install --force-reinstall dist/*.whl`) before testing CLI.
For Python code changes: `pip install -e .` makes them live without rebuild.

## Console scripts (13)

```
re-spec-init               re-spec-build-graph        re-spec-coverage-report
re-spec-profile            re-spec-validate           re-spec-render-nav
re-spec-scope              re-spec-query              re-spec-observations
re-spec-capture            re-spec-mcp-server         re-spec-coverage-check
re-spec-paths              # bundled data file inventory + lookup
```

All are declared in `pyproject.toml` `[project.scripts]`. Adding a new one:
add the entry, rerun `pip install -e .`.

## Workflow (10 phases, 3 PM gates)

The skill orchestrator in `skills/re-spec-mobile/SKILL.md` walks through:

1. **Phase 0** — bootstrap (init project, validate profile)
2. **Phase 1** — kickoff with PM (Gate 1: scope contract sign-off)
3. **Phase 2** — capture (delegated to `app-explorer` agent)
4. **Phase 3** — reset handoff
5. **Phase 4** — coverage check
6. **Phase 4.5** — coverage report (Gate 2: PM audits coverage_report.md)
7. **Phase 5** — write specs (delegated to `spec-writer` agent)
8. **Phase 5.5** — Gate 3: PM reviews spec narrative
9. **Phase 6** — graph rebuild + validate
10. **Phase 7** — commit

Gates exist because PM ↔ AI scope drift is the #1 failure mode of
auto-capture. Never skip Gate 1.

## Conventions

- **Naming:** console scripts use `re-spec-*` (hyphenated). Python modules use
  snake_case. Anchor IDs use `<feature>/<type>/<name>` (slashes).
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `chore:`,
  `refactor:`, `test:`, `docs:`).
- **Branch naming:** `feat/`, `fix/`, `chore/`, `refactor/`, `test/`, `docs/`.
- **Imports:** always `from re_spec_mobile.X import Y` (never bare `import X`
  or `sys.path.insert(...)` — was the old pre-package style, all converted).
- **Bundled data access:** always via `re_spec_mobile.paths.{template,canonical,shell}(name)`
  — never hardcode paths to `_data/` (breaks when installed to site-packages).
- **No comments unless WHY is non-obvious** (matches Claude Code default).

## Testing

There is no formal test suite yet (v1.0.0). Smoke tests:

1. Build wheel in fresh venv → install → run `re-spec-paths` → verify inventory.
2. Run against `bible-agent/` (sibling repo, has live `.spec-profile.yml`):
   - `re-spec-build-graph` → expect 164 nodes / 208 edges
   - `re-spec-validate` → expect 48 errors (legacy schema gaps, not regressions)
3. Start MCP server: `re-spec-mcp-server <<<'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'`
   → expect handshake response.

## Versioning

Bumped in `pyproject.toml` `[project.version]`. Current: 1.0.0 (extracted from
bible-agent on 2026-05-04). See `README.md` versioning table for changelog.

## What NOT to do

- ❌ Edit `bible-agent/spec/tools/*.py` from this repo — that's the origin, frozen.
- ❌ Add Python files outside `src/re_spec_mobile/` (won't be packaged).
- ❌ Add data files outside `_data/` (won't be bundled).
- ❌ Use `sys.path.insert(...)` (regression to pre-package style).
- ❌ Hardcode paths like `templates/x.md` (use `paths.template("x.md")`).
- ❌ Run `pip install` outside a venv (PEP 668 blocks system pip on this machine).
- ❌ Duplicate skill/agent markdown into `src/` (Claude Code can't see `site-packages/`).
