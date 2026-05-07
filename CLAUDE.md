# CLAUDE.md

This file is read automatically by Claude Code at the start of every conversation
in the `re-spec-mobile` repo.

## Project Purpose

**Spec-first reverse-engineering toolkit for Android apps.** Drives a connected
device, captures every screen of a feature, then produces a 5-layer markdown
spec corpus (scope + observations + flow + implementation + coverage_report)
plus 1 app-level overview (Layer 5 platform-agnostic) that engineers can
rebuild the feature from without ever running the original app.

**Output dùng cho cả iOS + Android rebuild.** Layer 3 implementation contract
(Kotlin syntax illustrative — coding agent dịch sang Swift/TS/Dart). Layer 5
app overview platform-agnostic — pass linter cấm token framework-specific.

App-agnostic by design: every app-specific value (package, viewport, blocklist,
nav tabs, paths, reference style, **Telegram bridge**) lives in a per-project
`.spec-profile.yml`.

## Origin

Extracted from `bible-agent/spec/tools/` (a sibling repo). bible-agent is the
source material — **do NOT edit it from this repo**. All toolkit changes belong
in `src/re_spec_mobile/`. See `docs/MIGRATION.md` for the relationship.

## Key Facts

- **Stack:** Python 3.10+ (pip-installable, src-layout per PEP 518)
- **Required deps:** `pyyaml>=6.0` (Telegram bridge dùng stdlib `urllib`, KHÔNG thêm dep)
- **Optional:** `droidrun>=0.3,<0.6` via `pip install re-spec-mobile[device]`
- **Build:** `python -m build` (needs venv — system pip is PEP 668 blocked trên máy datnt)
- **CLI:** **19 console scripts** on PATH after install (`re-spec-*`)
- **Distribution:** wheel + sdist in `dist/`, install via `INSTALL.sh`
- **Current version:** `1.1.0` trong pyproject.toml (chưa bump cho v1.2 features
  app_overview + pm_doc_lint — bump khi release)

## Repo Layout (3 buckets, 3 install mechanisms)

```
src/re_spec_mobile/          ← PIP install (Python package)
  ├── *.py                    16 modules — actual code
  └── _data/                  Bundled via package_data + importlib.resources
      ├── templates/          8 .tmpl files (scope, observations, spec,
      │                       feature_spec, coverage_report, app_overview, profile)
      ├── canonical/          6 reference files (5 sample + SPEC_SCHEMA)
      └── _shell/             3 shell scripts (setup_portal, register-mcp, version)

skills/re-spec-mobile/       ← SYMLINK to ~/.claude/skills/ (Claude Code reads)
  └── SKILL.md               11-phase orchestrator + 3 PM gates + Telegram bridge

agents/                      ← SYMLINK to ~/.claude/agents/ (Claude Code reads)
  ├── app-explorer.md        Sub-agent: device capture + stuck handoff (sonnet)
  └── spec-writer.md         Sub-agent: prose generation (opus)

docs/                        ← Operations + dogfood report + roadmap
examples/                    ← Sample .spec-profile.yml (bible-agent)
INSTALL.sh                   ← pip install + symlink in one shot
pyproject.toml               ← Package metadata + 19 entry_points
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

# Test the installed CLI
re-spec-paths                      # show bundled data file inventory
re-spec-profile                    # validate .spec-profile.yml in CWD
re-spec-mcp-server                 # start spec-graph MCP server (stdio)

# Smoke test against bible-agent baseline
cd ../bible-agent && re-spec-build-graph && re-spec-validate
# Should match: 164 nodes, 208 edges, 48 validate errors (legacy schema gaps)

# Telegram bridge live test (cần TELEGRAM_BOT_TOKEN env)
re-spec-pm-init                    # lấy chat_id
re-spec-pm-ask <feature> --gate scope
re-spec-pm-sync <feature>

# App overview synthesis (sau khi ≥ 2 feature đã commit)
re-spec-build-graph
re-spec-app-overview               # render/refresh spec/app_overview.md
re-spec-app-overview --check       # lint forbidden platform token

# PM doc linter (apply cho doc PM bất kỳ, không bind 9-section)
re-spec-pm-doc-lint <file_or_dir>
re-spec-pm-doc-lint <path> --strict   # exit 1 nếu warning (CI)
```

## Where to make changes

| You want to... | Edit this | NOT this |
|---|---|---|
| Add/change Python tool logic | `src/re_spec_mobile/<name>.py` | `bible-agent/spec/tools/` (origin, frozen) |
| Add a new CLI command | `pyproject.toml` `[project.scripts]` + new `src/re_spec_mobile/<name>.py` | — |
| Update spec template | `src/re_spec_mobile/_data/templates/<name>.md.tmpl` | top-level `templates/` (không tồn tại) |
| Update reference style | `src/re_spec_mobile/_data/canonical/<name>.sample.md` | top-level `canonical/` |
| Update Portal setup script | `src/re_spec_mobile/_data/_shell/setup_portal.sh` | — |
| Update orchestrator workflow | `skills/re-spec-mobile/SKILL.md` | inside `src/` (Claude Code không thấy `site-packages/`) |
| Update sub-agent behaviour | `agents/{app-explorer,spec-writer}.md` | inside `src/` |
| Update install flow | `INSTALL.sh` | — |
| Update SPEC_SCHEMA convention | `src/re_spec_mobile/_data/canonical/SPEC_SCHEMA.md` | — |
| Update PM doc linter rule | `src/re_spec_mobile/pm_doc_lint.py` (FORBIDDEN_TOKENS, CHECK_FNS, etc.) | — |
| Add new gate / Telegram kind | `src/re_spec_mobile/pm_channel.py` (KIND_*, parser, ask_*, sync handler) | — |

After editing bundled `_data/` files: rebuild wheel (`python -m build`) +
reinstall (`pip install --force-reinstall dist/*.whl`) trước khi test CLI.
For Python code changes: `pip install -e .` makes them live without rebuild.

## Console scripts (19)

Grouped by purpose:

```
# Core spec lifecycle (13)
re-spec-init               re-spec-build-graph        re-spec-coverage-report
re-spec-profile            re-spec-validate           re-spec-render-nav
re-spec-scope              re-spec-query              re-spec-observations
re-spec-capture            re-spec-mcp-server         re-spec-coverage-check
re-spec-paths              # bundled data file inventory + lookup

# Telegram PM bridge (4 — v1.1)
re-spec-pm-init            # 1 lần / project — lấy chat_id từ /start
re-spec-pm-ask             # post Open Question / signoff prompt (gate scope/coverage/spec)
re-spec-pm-ask-stuck       # Phase 3 reset handoff khi capture stuck
re-spec-pm-sync            # long-poll, fold reply vào file / .stuck_log.json

# App overview synthesis (1 — v1.2)
re-spec-app-overview       # render/refresh spec/app_overview.md (10 auto + 5 prose)

# PM doc linter (1 — v1.2)
re-spec-pm-doc-lint        # 6 check: ANCHOR / RFC2119 / AC / PLATFORM / OPENQ / FM
```

All declared in `pyproject.toml` `[project.scripts]`. Adding new: thêm entry,
rerun `pip install -e .`.

## Workflow (11 phases, 3 PM gates)

The skill orchestrator in `skills/re-spec-mobile/SKILL.md` walks through:

```
Phase 0     Bootstrap (re-spec-init)                   [1 lần / project]
Phase 1     Kickoff
Phase 1.5 ━━ GATE 1 scope ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Telegram-aware (kind=question)
Phase 2     Capture loop (→ app-explorer agent)
Phase 3     Reset handoff khi stuck                    Telegram-aware (kind=stuck_help)
                                                      4 verdict: action / manual / skip / abort
                                                      Auto-skip threshold mặc định 3 lần
Phase 4     Coverage check
Phase 4.5 ━━ GATE 2 coverage ━━━━━━━━━━━━━━━━━━━━━━━━━ Telegram-aware (kind=coverage_signoff)
                                                      Reply pass/fail → flip status
Phase 5     Spec writing (→ spec-writer agent)        Sinh 3 file: observations / spec / feature_spec
Phase 5.5 ━━ GATE 3 spec Q&A ━━━━━━━━━━━━━━━━━━━━━━━━━ Telegram-aware (kind=question §7)
Phase 6     Build graph + validate
Phase 7     Commit (thủ công)
Phase 8     App overview synthesis                    [≥2 feature, không gate, idempotent rerun]
                                                      10 auto section + 5 prose
                                                      HTML marker preserve prose
                                                      Linter platform-agnostic
```

Gates exist because PM ↔ AI scope drift is the #1 failure mode of auto-capture.
Never skip Gate 1 trong production session.

## Telegram PM bridge (4 kind)

Module `pm_channel.py` (~700 dòng, stdlib-only). Inbox state ở
`<feature>/.pm_inbox.json`, stuck event log ở `<feature>/.stuck_log.json`
(both gitignored).

| Kind | Khi nào | CLI ask | Reply format | Fold target |
|---|---|---|---|---|
| `question` | Gate 1, Gate 3 | `re-spec-pm-ask --gate scope/spec` | text tự do | `**PM answer**:` dưới `{#<anchor>}` |
| `coverage_signoff` | Gate 2 | `re-spec-pm-ask --gate coverage` | `pass <r>` / `fail <r>` | flip `status:` + append `decisions:` |
| `stuck_help` | Phase 3 | `re-spec-pm-ask-stuck --screen-label X --reason Y --options Z` | `action: ...` / `manual: ...` / `skip` / `abort` | `.stuck_log.json` |

Auth: token từ env `TELEGRAM_BOT_TOKEN`, chat_id trong profile. **Token KHÔNG
bao giờ vào yml**.

## App overview Layer 5 (Phase 8)

Module `app_overview.py` (~570 dòng). Render `<spec_root>/app_overview.md`
platform-agnostic, dùng cho cả iOS rebuild + stake-holder non-tech.

10 auto section (bọc `<!-- AUTO:KEY START/END -->`):
- IDENTITY, INVENTORY, SITEMAP, CROSS_NAV, **REUSE_MAP** (auto-detect ứng viên design system),
  API_SURFACE, DATA_MODELS, INVARIANTS, OPEN_QUESTIONS, ACCEPTANCE

5 prose section (designer/PM viết, ngoài marker → preserve khi rerun):
- A Mục tiêu sản phẩm, B Navigation model, C UX state pattern, D Content rules,
  E Cross-cutting decisions

Linter forbidden token (warn-only ngoài code fence): `Compose / Kotlin /
@Composable / Activity / Fragment / SwiftUI / UIView / UIViewController /
Storyboard / ViewModel / KMM / ...`. `--strict` cho CI.

## PM doc linter (`re-spec-pm-doc-lint`)

Module `pm_doc_lint.py` (~400 dòng). Linter cho doc PM **bất kỳ** — KHÔNG bind
9-section feature_spec. Apply technique từ workflow vào doc PM-written.

6 check (warn-only, `--strict` cho CI):

| Check | Trigger |
|---|---|
| `ANCHOR` | `{#...}` không match `<feature>/<type>/<slug>` snake_case |
| `RFC2119` | Section "rule/behavior/policy" thiếu MUST/SHOULD/MAY |
| `AC` | AC bullet thiếu số + đơn vị (chars/ms/s/%/p95) |
| `PLATFORM` | Token framework-specific ngoài code fence |
| `OPENQ` | Question heading thiếu `**PM answer**:` non-empty |
| `FM` | Frontmatter (nếu có) thiếu status/version/last_updated |

CLI: `re-spec-pm-doc-lint <file_or_dir> [--strict] [--check ANCHOR] [--json]`

## Conventions

- **Naming:** console scripts dùng `re-spec-*` (hyphenated). Python modules
  snake_case. Anchor IDs `<feature>/<type>/<name>` (slashes, snake_case).
- **Anchor types known** (xem `pm_doc_lint.ANCHOR_KNOWN_TYPES`): feature, screen,
  block, component, api, data_model, criterion, invariant, question, state,
  cluster, conversation, turn, rule, policy, metric, flow, scope, observations,
  implementation, coverage_report, overview, stuck.
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `chore:`,
  `refactor:`, `test:`, `docs:`). Scope optional (`feat(pm-channel):`).
- **Branch naming:** `feat/`, `fix/`, `chore/`, `refactor/`, `test/`, `docs/`.
- **Imports:** always `from re_spec_mobile.X import Y` (never bare `import X`
  hay `sys.path.insert(...)`).
- **Bundled data access:** always via
  `re_spec_mobile.paths.{template,canonical,shell}(name)` — never hardcode paths.
- **Layer 3 Kotlin = illustrative**: §3 state class + §6 data model dùng Kotlin
  cho gọn; coding agent rebuild iOS/TS/Dart **tự dịch syntax** (xem
  `SPEC_SCHEMA.md` §6 mapping table). KHÔNG đổi sang JSON Schema cho data
  model — `extract_contracts.py` depend ` ```kotlin` annotation.
- **Output spec tiếng Việt** + technical term tiếng Anh (xem `docs/I18N_GLOSSARY.md`).
- **No comments unless WHY is non-obvious** (matches Claude Code default).
- **Token Telegram chỉ qua env**, không bao giờ vào yml. Nếu user paste vào chat
  → cảnh báo, đừng dùng, recommend `/revoke` qua @BotFather.

## Recovery / resume

Workflow filesystem-based + idempotent → crash giữa chừng safe:

| Phase crashed | State on disk | Resume |
|---|---|---|
| 1.5 Gate 1 | `<feature>_scope.md` | PM continue editing hoặc `re-spec-pm-sync` |
| 2 Capture | screens/, dumps/, nav_graph.json per file | `re-spec-coverage-check` biết thiếu screen nào |
| 3 Stuck | `.stuck_log.json` + `.pm_inbox.json` | `re-spec-pm-sync` |
| 4.5 Gate 2 | `<feature>_coverage_report.md` | PM tiếp tục review |
| 5 Spec-writer | partial md files | spec-writer mode=revise (rẻ hơn draft) |
| 5.5 Gate 3 | Open Q §7 + .pm_inbox.json | `re-spec-pm-sync` |
| 6 Build graph | `_graph/*.json` | rerun `re-spec-build-graph` (idempotent) |
| 8 Overview | app_overview.md với HTML marker | rerun `re-spec-app-overview` (preserve prose) |

**Recommend**: commit checkpoint sau mỗi phase quan trọng (Phase 1.5, 4.5, 7, 8).

## Testing

Chưa có formal test suite. Smoke tests:

1. Build wheel in fresh venv → install → `re-spec-paths` → verify inventory.
2. Run against `bible-agent/` (sibling repo, có live `.spec-profile.yml`):
   - `re-spec-build-graph` → expect 164 nodes / 208 edges
   - `re-spec-validate` → expect 48 errors (legacy schema gaps, không phải regression)
3. Start MCP server: `re-spec-mcp-server <<<'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'`
   → expect handshake response.
4. PM doc lint: `re-spec-pm-doc-lint <any.md>` — should not crash, có warning thì giải thích cụ thể.
5. App overview idempotent: render → edit prose → re-render → verify prose preserved.

## Versioning + commit history

Bumped in `pyproject.toml` `[project.version]`. Current version trong file: `1.1.0`.
Nếu release v1.2 cho app_overview + pm_doc_lint, bump `1.1.0` → `1.2.0`.

| Commit | Highlight |
|---|---|
| `974c629` | v1.0.0 — initial extract từ bible-agent, 13 CLI, 3 PM gate (PM sửa file tay) |
| `035b1a0` | i18n — translate skill + agents + templates sang tiếng Việt |
| `73a2ced` | i18n — translate canonical samples sang tiếng Việt |
| `a9c2067` | v1.1 — Telegram Q&A bridge cho 3 gate (3 CLI: pm-init/ask/sync) |
| `5c173a6` | v1.2-pre — Layer 5 app_overview synthesis (1 CLI, idempotent rerun, linter) |
| `f674b9f` | docs(layer3) — Kotlin syntax = illustrative cho cross-platform handoff |
| `525233a` | feat(pm-channel) — stuck-help handoff via Telegram (Phase 3, 4 verdict) |
| `ccdd672` | v1.2-pre — PM doc linter (6 check: ANCHOR/RFC2119/AC/PLATFORM/OPENQ/FM) |

## What NOT to do

- ❌ Edit `bible-agent/spec/tools/*.py` từ repo này — origin, frozen.
- ❌ Add Python files outside `src/re_spec_mobile/` (won't be packaged).
- ❌ Add data files outside `_data/` (won't be bundled).
- ❌ Use `sys.path.insert(...)` (regression to pre-package style).
- ❌ Hardcode paths như `templates/x.md` (use `paths.template("x.md")`).
- ❌ Run `pip install` outside a venv (PEP 668 blocks system pip trên máy này).
- ❌ Duplicate skill/agent markdown vào `src/` (Claude Code can't see `site-packages/`).
- ❌ Commit secret (token Telegram) vào yml hay code — luôn dùng env var.
- ❌ Đổi Layer 3 §6 data model từ ` ```kotlin` sang JSON Schema —
  `extract_contracts.py` depend kotlin annotation. Convention "Kotlin =
  illustrative" đã document đầy đủ trong SPEC_SCHEMA.md §6.
- ❌ Auto-commit từ skill orchestrator — Phase 7 commit luôn manual.
- ❌ Auto `pm clear` package hay force-restart app — phá state silent. Stuck =
  trả BLOCKED hoặc Telegram pm-ask-stuck.
- ❌ Bump `pyproject.toml` version trừ khi user yêu cầu rõ.

## Future improvement candidates (không bắt buộc)

Nếu tiếp tục cải tiến, các hướng đáng cân nhắc (xem chat history v1.2 session):

1. **Conversation flow template variant** — feature có chat/dialog (như SubTrack
   AI Chat) không fit 9-section per-screen. Thêm template + anchor type
   `<feature>/conversation/<flow>` + `<feature>/turn/<id>`. Estimate ~400 dòng.
2. **Behavioral rules section** trong feature_spec.md — anchor type
   `<feature>/rule/<slug>` + `<feature>/policy/<slug>` cho RFC 2119 MUST/SHOULD.
   Estimate ~150 dòng.
3. **Metrics tracking → table với anchor** — mở rộng §2.3 hiện placeholder
   prose-only. Anchor `<feature>/metric/<event>`. Estimate ~80 dòng.
4. **iOS path** — capture bằng xcrun simctl + Accessibility Inspector + idb.
   Module mới ~600 dòng + iOS profile schema. **Big lift.**
5. **Hybrid app a11y enhanced parser** — Flutter / RN / WebView a11y tree thưa.
   Cải tiến `capture.py` parser. Estimate ~200 dòng.
6. **`ux_research` profile style** — skip Layer 3 cho competitor research mode
   (nếu user không cần handoff coding agent). Estimate ~150 dòng.

User đã chốt KHÔNG làm (1)-(3) trong session này — defer khi cần thật. (4)-(6)
chưa đụng đến.
