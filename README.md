# re-spec-mobile

Spec-first reverse-engineering toolkit for Android apps. Drives a connected
device, captures every screen of a feature, and produces a 3-layer markdown
spec corpus (observations + flow + implementation) that engineers can rebuild
the feature from without ever running the original app.

App-agnostic: every app-specific value (package, viewport, blocklist,
navigation tabs, paths, reference style) lives in a per-project
`.spec-profile.yml` adapter file. Drop the skill once on your machine, drop a
profile in each app project, then run.

## What's in this package

```
re-spec-mobile/
├── pyproject.toml                          # pip-installable Python package
├── INSTALL.sh                              # pip install + symlink skill+agents
├── README.md                               # this file
├── docs/                                   # OPERATIONS, DOGFOOD_REPORT, ROADMAP_NONTECH, MIGRATION
├── examples/
│   └── bible-agent.spec-profile.yml        # sample profile for BibleChat
├── src/
│   └── re_spec_mobile/                     # Python package
│       ├── __init__.py                     # public API exports
│       ├── paths.py                        # locate bundled data via importlib.resources
│       ├── profile_loader.py               # load + validate .spec-profile.yml
│       ├── scope_loader.py                 # Gate 1 PM contract reader
│       ├── init_project.py                 # Phase 0 bootstrap
│       ├── nav_graph.py                    # graph data model
│       ├── capture.py                      # Phase 2 screen snapshot
│       ├── coverage_check.py               # Phase 4 uncovered clickables
│       ├── coverage_report.py              # Phase 4.5 Gate 2 audit
│       ├── observations_tmpl.py            # Phase 5 boilerplate
│       ├── render_nav.py                   # Phase 5 Mermaid nav
│       ├── build_graph.py                  # Phase 6 graph builder
│       ├── validate_spec.py                # Phase 6 schema enforcement
│       ├── spec_query.py                   # ad-hoc graph query
│       ├── mcp_server.py                   # spec-graph MCP server
│       └── _data/                          # bundled package_data
│           ├── templates/                  # 7 templates (profile/scope/coverage_report/...)
│           ├── canonical/                  # gold-standard reference style
│           └── _shell/                     # setup_portal.sh + register-mcp-user.sh
├── skills/
│   └── re-spec-mobile/
│       └── SKILL.md                        # 10-phase orchestrator (3 PM gates)
└── agents/
    ├── app-explorer.md                     # Phase 2 capture (sonnet)
    └── spec-writer.md                      # Phase 5 prose generation (opus)
```

## Architecture (3 layers, mirrors the original architecture diagram)

```
LAYER 1 — Reusable engine (this package, install once)
pip install re-spec-mobile          # 13 console scripts on PATH
~/.claude/skills/re-spec-mobile/    # SKILL.md (orchestrator instructions)
~/.claude/agents/                   # app-explorer + spec-writer

LAYER 2 — Per-app adapter (one .spec-profile.yml per project)
<your-app-repo>/.spec-profile.yml   # app + device + navigation + blocklist + paths

LAYER 3 — Per-feature output (loop N times per app)
<your-app-repo>/spec/feature/<feat>/<feat>_{scope,observations,spec,feature_spec,coverage_report}.md
<your-app-repo>/spec/{screens,ui_dumps,_raw}/<feat>/
<your-app-repo>/spec/_graph/{nodes,edges,index}.json
```

## Install (5 minutes, one-time per machine)

```bash
bash INSTALL.sh                    # pip install -e + symlink skill+agents (default)
# or
bash INSTALL.sh --copy             # pip + copy skill (production)
bash INSTALL.sh --no-pip           # only symlink skill (assume pip already done)
bash INSTALL.sh --user-pip         # use pip install --user (no venv)
bash INSTALL.sh --no-skill         # only pip install, skip ~/.claude/ link
```

After install, 13 `re-spec-*` console scripts are on PATH:

```
re-spec-init               re-spec-build-graph        re-spec-coverage-report
re-spec-profile            re-spec-validate           re-spec-render-nav
re-spec-scope              re-spec-query              re-spec-observations
re-spec-capture            re-spec-mcp-server         re-spec-coverage-check
re-spec-paths              # show bundled data file paths
```

Optional: register the spec-graph MCP at user scope:

```bash
bash $(re-spec-paths --shell register-mcp-user.sh)
```

## Use (per app project)

```bash
# 1. From your app project root, scaffold the profile + spec dirs
re-spec-init

# 2. Edit .spec-profile.yml — fill app.package, app.main_activity, navigation.tabs
$EDITOR .spec-profile.yml

# 3. Set up droidrun Portal on your connected device (one-time per device)
bash $(re-spec-paths --shell setup_portal.sh)

# 4. In Claude Code (cd into the project), invoke:
#    /re-spec-mobile
# or just say:
#    "spec feature <name>"
#    "auto-test the explore tab"
```

The skill orchestrator walks through the 7 phases (0 init / 1 kickoff / 2
capture / 3 reset handoff / 4 coverage / 5 write specs / 6 graph rebuild / 7
commit), delegating Phase 2 to `app-explorer` and Phase 5 to `spec-writer`.

## Key design decisions

| # | Decision | Why |
|---|---|---|
| 1 | Skill at user-scope (`~/.claude/skills/`) | Portable across N projects, install once |
| 2 | Tools bundled with skill | Single source of truth, version with skill |
| 3 | Profile per-project as `.spec-profile.yml` | Clean separation: engine/adapter/output |
| 4 | YAML profile (not JSON/TOML) | Comments allowed, easy to read |
| 5 | Built-in canonical fallback + per-project override | First feature of a new app still has reference |
| 6 | Skill name `re-spec-mobile` (not `-android`) | iOS support can land later without rename |
| 7 | Two subagents (capture + writer) | Split contexts; sonnet drives device, opus writes prose |
| 8 | Universal-safe blocklist defaults | Subscribe/Logout/Buy never tapped even if user forgets to configure |
| 9 | Auto-rebuild graph in MCP server | Spec writers don't have to remember `build_graph.py` |
| 10 | Cross-feature reuse via `reuse_key` | Engineer rebuilds 1 component, parameterises across N screens |

## Limitations (v1.0.0)

- **Android only.** droidrun supports iOS but it's not wired through `capture.py` yet.
- **One device at a time.** No fleet-mode for parallel feature capture.
- **Compose obfuscated activity names** can't disambiguate similar bottom-sheets
  by activity alone — the agent uses title-text heuristics as fallback.
- **Custom Canvas widgets** (audio mini-player, animation views) are invisible
  to the Portal a11y tree — agent documents them as "screenshot only".
- **Screen hash collisions** possible if 2 different screens share the first 6
  text/desc signatures — bump `profile.capture.hash_window` to disambig.
- **No retry/self-heal** in capture.py — single Portal error = script exit;
  agent treats it as BLOCKED and asks orchestrator to re-run setup_portal.sh.

## Migrating an existing bible-agent project

See `docs/MIGRATION.md` — the bible-agent repo's `spec/tools/` was the source
material for this skill. Migration is non-destructive: keep the existing tools
in place, drop a `.spec-profile.yml`, and start using the skill in parallel.
After confidence builds, the duplicated tools can be removed.

## Versioning

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-05-04 | Initial release. Extracted from bible-agent/spec/tools/ + canonical from BibleChat Today feature. |

## License

Internal use, no license declared. See repository root for any future LICENSE.
