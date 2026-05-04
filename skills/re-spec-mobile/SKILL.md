---
name: re-spec-mobile
description: |
  Reverse-engineer any Android app into a 3-layer spec corpus
  (observations + flow + implementation) using droidrun Portal + adb +
  spec-graph MCP. Trigger when the user says "RE app", "spec feature X",
  "auto-test feature X", "tạo spec cho app này", "rebuild spec mobile",
  or invokes `/re-spec-mobile` directly. The skill is app-agnostic: every
  app-specific value (package, viewport, blocklist, tabs, paths, reference
  style) is read from the project's `.spec-profile.yml` adapter file.
version: 1.0.0
---

# re-spec-mobile — Reverse-engineer mobile apps into specs

> **What this skill does, in one sentence:** drive a connected Android device,
> capture every screen of a feature, and produce 3 markdown files (observations
> / flow / implementation) that engineers can rebuild the feature from without
> ever running the original app.

## When to use

Trigger this skill when the user wants to:

- Spec a feature of an Android app they don't own the source of (competitor
  research, internal RE for spec-first methodology, regression baseline).
- Auto-test a flow + record artifacts (screenshots + a11y dumps + nav graph).
- Bootstrap a new project to start spec'ing (Phase 0 only — see below).
- Re-run capture against a new app build to detect drift vs prior spec.

**Do NOT use** for: app implementation (use `implement-feature` skill instead);
spec query against an existing graph (use `spec-graph` agent); generic Android
reverse-engineering of APK internals (use `android-reverse-engineering` skill).

## Inputs you must establish before Phase 1

1. **Profile present?** — there must be `.spec-profile.yml` at the project root.
   If absent → run **Phase 0** (init).
2. **Device alive?** — exactly one device on `adb devices` matching profile
   `device.serial` (or any device if serial blank).
3. **Portal alive?** — `adb shell content query --uri content://com.droidrun.portal/state`
   returns `"status":"success"`. If not → `bash $(re-spec-paths --shell setup_portal.sh)`.
4. **App focused?** — `adb shell dumpsys window | grep mCurrentFocus` shows the
   profile's `app.package`. Otherwise ask the user to open the app.
5. **Feature scope?** — user must name the feature (e.g. `bible`, `explore_create`).
   The slug becomes the folder name + frontmatter `feature` field.

If any of (2–4) fail, report the specific failure to the user and offer the
exact remediation command. Don't guess.

---

## Workflow — 10 phases (with 3 PM gates)

The workflow has **3 PM-controlled gates** between automation phases. Each
gate produces a markdown artifact PM signs off, and the next agent refuses to
start without sign-off. This prevents the "AI captured what it thought, not
what PM wanted" failure mode.

```
Phase 0   Bootstrap (one-time per project)
Phase 1   Kickoff
Phase 1.5 ━━━ GATE 1: Scope contract ━━━━━━━━━━ PM signs <feature>_scope.md
Phase 2   Capture loop (app-explorer agent)
Phase 3   Reset handoff (when stuck)
Phase 4   Coverage check (mid-loop, automated)
Phase 4.5 ━━━ GATE 2: Coverage report ━━━━━━━━━ PM signs <feature>_coverage_report.md
Phase 5   Write specs draft (spec-writer agent, mode=draft)
Phase 5.5 ━━━ GATE 3: Spec review loop ━━━━━━━━ PM annotates open questions inline
Phase 6   Spec graph rebuild + validate
Phase 7   Commit (manual)
```



### Phase 0 — Bootstrap (one-time per project)

When `.spec-profile.yml` doesn't exist in CWD or any parent.

```bash
re-spec-init
```

This:
- Detects device viewport (`adb shell wm size`) + currently focused app, patches
  the template with what it found.
- Writes `.spec-profile.yml` template to CWD.
- Scaffolds `spec/{feature,screens,ui_dumps,_raw,_graph,_contracts}/`.
- Writes `.mcp.json` so the spec-graph MCP server auto-loads in this repo.

Then **stop and ask the user** to:
- Confirm `app.package` + `app.main_activity` (autodetected if device was open).
- Fill `navigation.tabs` (do this after Phase 2 yields one capture you can read).
- Add app-specific `blocklist.custom` patterns (paywall CTAs, destructive verbs).

Validate before proceeding:

```bash
re-spec-profile --validate
```

Then run `bash $(re-spec-paths --shell setup_portal.sh)` to bring Portal up on the device.
The user must enable accessibility manually if the script fails at section 4
(common on Pixel/AOSP — print the exact instruction from setup_portal.sh).

### Phase 1 — Kickoff

When the user says "spec feature X":

1. Read `.spec-profile.yml`. Confirm `app.package`, `device.viewport`,
   `paths.spec_root` are set; refuse otherwise.
2. Verify Portal alive (60-second checklist below).
3. Ask the user (only if not stated): which feature? what's the starting state
   (which tab, which screen)? need a reset?
4. Create a TaskList with ~10 tasks (one per workflow phase including 3 gates).
5. **Decide auto-approve eligibility**: if user signals "small feature, ~3
   screens" OR explicitly says "skip scope" → set `bypass_scope=true`.
   Otherwise continue to Phase 1.5 (Gate 1).
6. Wait for user to reply `ready, <feature>, <starting screen>`.

### Phase 1.5 — GATE 1: Scope contract (PM sign-off before capture)

**Purpose**: chốt scope giữa PM ↔ Claude TRƯỚC capture. Không để AI tự decide
"đi đâu là đủ" — đó là root cause #1 của "AI auto-test chưa đi hết các màn".

#### Workflow

1. Check if `<feature_root>/<feature>/<feature>_scope.md` already exists.
   - status=signed_off → skip to Phase 2
   - status≠signed_off → continue from where PM left off
   - file missing → Claude proposes draft (next step)

2. **Claude proposes scope draft** by:
   - Quick reconnaissance capture (1-2 screens of the feature landing)
   - Reading any existing related specs (`spec_search <feature>` via MCP)
   - Asking PM via short Q&A:
     - "Feature này gồm những cluster nào? (vd Wizard / Plan Detail / Paywall)"
     - "Cluster nào IN scope, cluster nào OUT?"
     - "Có ràng buộc gì với cluster IN? (vd 'phải capture cả back press', 'A/B variant')"
     - "Câu hỏi nào cần PM trả lời trước khi capture?"
   - Generate `<feature>_scope.md` from `templates/scope.md.tmpl`,
     fill answers, set `status: draft`.

3. **PM reviews + signs off**:
   - Read scope.md, edit must_visit / optional / out_of_scope as needed
   - Answer Open Questions inline (`**PM answer**: <text>` under each `### Q-NN`)
   - Set `status: signed_off`, fill `signed_off_by` + `signed_off_at`
   - Bump `scope_version` if revising after a previous sign-off

4. Claude verifies sign-off:
   ```bash
   re-spec-scope <feature> --check
   ```
   Exit 0 → continue to Phase 2. Exit 1 → tell PM what's blocking.

#### Auto-approve exception

Skip Gate 1 when ALL of:
- Feature is < 5 screens (estimated)
- User explicitly says "skip scope" or "auto"
- No PM in the loop (solo dev mode)

In auto-approve, Claude proceeds with `bypass_scope=true`. Capture loop
still produces nav_graph + dumps; coverage_report skipped at Gate 2.

### Phase 2 — Capture loop

Delegate to the **`app-explorer` agent** (subagent in this package). It runs
autonomously with adb + Portal access; you stay in the main context. The agent's
contract:

- **Input:** feature slug, starting screen description, profile path.
- **Tools:** Bash + Read.
- **Output:** populated `<screens_root>/<feature>/`, `<dumps_root>/<feature>/`,
  `<raw_root>/<feature>/nav_graph.json`. Returns a short status: screens
  captured, edges, blockers if any.

Driver loop (per screen):

```bash
# Verify Portal alive
adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80
# → must contain '"status":"success"'

# Landing
re-spec-capture <feature> screen_01_landing

# Tap an element to reach a sub-screen
adb shell input tap 540 1100
re-spec-capture <feature> screen_02_<name> \
  --from screen_01_landing --via "tap:(540,1100) <element label>"

# Scroll segment (use edge_swipe_x from profile when center is overlaid)
adb shell input swipe 540 1500 540 500 800

# Back
adb shell input keyevent KEYCODE_BACK
```

**Tips that prevent stuck loops** (from accumulated experience):

- Use `coverage_check.py <feature>` mid-loop to know what clickables remain.
- Swipe duration ≥ 600ms, < 1500ms (longer = scroll, shorter = fling/tap).
- If center swipe doesn't move content (floating overlay nuốt), use
  `profile.scroll.edge_swipe_x` (default 200) and `long_swipe_duration_ms`.
- Compose `v01` modal sheets sometimes trap KEYCODE_BACK — list them in
  `profile.modals.back_traps`. Dismiss with swipe-down (top→bottom).
- Tap coordinate parsing: read `<dumps_root>/<feature>/<screen>.json` and
  pull `bounds` from clickable nodes; centre = midpoint of bounds.

### Phase 3 — Reset handoff (when stuck)

Pause and ask the user with a precise template:

```
Stuck at <screen description>. Need you to:
  1. <specific physical action — eg. force-close app, tap Settings, etc.>
  2. <next action>
Then reply: ready, <feature>, <new state>
```

**Do NOT** `pm clear` the package automatically. **Do NOT** force-restart the
app via `am start` — that often loses tab/scroll state. Only the user resets.

### Phase 4 — Coverage check (mid-loop, automated)

```bash
re-spec-coverage-check <feature> --scope
```

The `--scope` flag buckets MISS items by scope status (must_visit /
optional / out_of_scope / unscoped). If MISS in `must_visit_screen` bucket
remain → loop back to Phase 2 with prioritized targets. Out-of-scope MISS
are ignored (they're explicitly skipped per Gate 1 contract).

The blocklist is read from `profile.blocklist` so `Subscribe / Logout / Buy /
Continue` etc. are auto-filtered.

### Phase 4.5 — GATE 2: Coverage report (PM audit before write)

**Purpose**: PM verifies capture phase actually covered scope contract before
spec-writer spends time generating prose.

#### Workflow

1. Generate the report:
   ```bash
   re-spec-coverage-report <feature>
   ```
   Writes `<feature_root>/<feature>/<feature>_coverage_report.md` with 5 sections:
   summary metrics / captured / gaps / drift / PM review template.

2. **PM reviews**:
   - Read coverage_report.md sections 1-4
   - For each Gap: decide re-capture / revise scope / accept partial
   - For each Drift: decide add to scope cluster X / drop / move to out_of_scope
   - For each Open Question still unresolved: answer inline
   - Append decisions to frontmatter `decisions:` list
   - Set `status: sign_off_pass` OR `sign_off_fail`

3. Claude branches on PM decision:
   - `sign_off_pass` → proceed to Phase 5
   - `sign_off_fail` → loop back to Phase 2 with the gap/drift action items
     as new capture targets. Bump `scope_version` if PM revised scope.

#### Auto-approve exception

If `bypass_scope=true` (small feature) → skip coverage_report generation,
proceed to Phase 5 directly.

### Phase 5 — Write specs draft

Delegate to the **`spec-writer` agent** (subagent in this package). Contract:

- **Input:** feature slug, profile path. Reads from
  `<dumps_root>/<feature>/`, `<raw_root>/<feature>/nav_graph.json`,
  `<screens_root>/<feature>/`, plus the canonical reference (either
  `profile.reference.canonical_feature` if set, else
  `<skill_dir>/canonical/*.sample.md`).
- **Tools:** Read + Write + Grep + Bash.
- **Output:** 3 files in `<feature_root>/<feature>/`:
  - `<feature>_observations.md` (Layer 1 — structure auto from
    `observations_tmpl.py`, agent fills "Observed behaviour" + "Notes" per screen)
  - `<feature>_spec.md` (Layer 2 — agent writes from scratch following
    `spec.md.tmpl` + canonical structure)
  - `<feature>_feature_spec.md` (Layer 3 — 9-section structure from
    `feature_spec.md.tmpl` + canonical)
- **Auto-generated helpers** the agent runs first:
  ```bash
  re-spec-observations <feature> -o <feature_root>/<feature>/<feature>_observations.md
  re-spec-render-nav        <feature> -o <feature_root>/<feature>/<feature>_nav.md
  ```
  These produce the boilerplate; the agent only writes prose + frontmatter +
  the missing sections.

Agent invoked with `mode=draft` → returns `DONE-PENDING-REVIEW` with explicit
list of Open Questions PM must answer in the spec body (§7).

### Phase 5.5 — GATE 3: Spec review loop (PM annotates open questions)

**Purpose**: catch ambiguity in spec BEFORE it lands in commit history. PM
reads draft, answers Open Questions inline, spec-writer folds answers into
final spec.

#### Workflow

1. Claude tells the user (PM) to review:
   - "Spec draft ready. Open mọi file `<feature>_*.md` trong `<feature_root>/<feature>/`."
   - "Tập trung vào `<feature>_feature_spec.md` §7 Open Questions — N câu cần bạn trả lời inline."
   - Format: under each `### Q-NN`, add `**PM answer**: <text>` (or `WONTFIX` to drop the question).

2. PM annotates inline. May also tweak §3 (per-screen) and §8 (acceptance) directly.

3. PM signals "OK reviewed" → Claude reinvokes spec-writer with `mode=revise`.

4. Spec-writer:
   - Re-reads §7, finds answered questions
   - Folds each answer into the relevant section (§3/§4/§5/§6/§8)
   - Removes resolved questions from §7
   - Returns `DONE` with `remaining_open_questions: <count>`

5. Loop:
   - `remaining_open_questions == 0` → proceed to Phase 6
   - Else → tell PM "still N open, plz answer", loop back to step 1

#### Auto-approve exception

If `bypass_scope=true` AND PM not in loop → skip Gate 3. Spec-writer
returns `DONE-PENDING-REVIEW` and orchestrator commits with open questions
documented (status: draft instead of approved).

### Phase 6 — Spec graph rebuild + validate

```bash
re-spec-build-graph --stats
re-spec-validate <feature_root>/<feature>/
```

Fix any `[V*]` errors flagged by validator before commit. The MCP server
auto-rebuilds on each tool call so manual rebuild is mostly for stats display.

### Phase 7 — Commit (manual, never auto)

Show the user a draft commit message in the project's existing style. Only run
`git add` + `git commit` after explicit user approval. Default style (matches
bible-agent convention):

```
add <feature> feature specification document for implementation
```

For larger sessions: include scope tag (`feat(spec):`, `chore(spec):`) and
mention which phases ran.

---

## 60-second self-verify checklist (run at start of every session)

```bash
# 1. Profile present + valid
re-spec-profile --validate

# 2. Device connected
adb devices

# 3. Portal alive
adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80
# Want '"status":"success"' or '"a11y_tree"'

# 4. App focused
adb shell dumpsys window | grep mCurrentFocus | head -1
# Want the package from .spec-profile.yml

# 5. Existing specs (for reference style)
ls $(re-spec-profile | python -c 'import json,sys; print(json.load(sys.stdin)["paths"]["feature_root"])')
```

Pass all 5 → ready. Any fail → use the specific remediation per the failed step.

---

## Style conventions (enforced by writer agent)

These are non-negotiable and live in `canonical/SPEC_SCHEMA.md`:

- **Header English, commentary Vietnamese.** Example: `## 3. Block A — Welcome`,
  body "Đây là màn hình đầu tiên...".
- **Strings verbatim.** Wrap all UI text in backticks. **Never** translate or
  paraphrase. `Đăng nhập bằng Google` stays as-is.
- **Bounds table format** — 5 columns: `Class | Bounds | Clickable | Text | Content-desc`.
- **Mermaid flowchart with `subgraph`** by block — `render_nav.py` does this
  automatically.
- **Dates absolute, ISO-8601** — `2026-04-21`, never "yesterday" or "last week".
- **No emoji** unless user explicitly asks.
- **Anchor markers** `{#<feature>/<type>/<name>}` after every section header that
  declares a graph node (screen / block / component / api / data_model /
  criterion / invariant).

---

## Subagents bundled with this skill

| Agent | When the orchestrator delegates | Model | Tools |
|---|---|---|---|
| `app-explorer` | Phase 2 capture loop — drive device, capture, build graph | sonnet | Bash, Read |
| `spec-writer` | Phase 5 prose generation — fill 3 markdown files | opus | Read, Write, Grep, Bash |

The orchestrator (this skill) only handles Phase 0 + 1 + 3 + 4 + 6 + 7 directly.
Phase 2 and 5 are pure subagent work to keep main context lean.

---

## Failure modes + recovery

| Failure | Diagnosis | Action |
|---|---|---|
| `Portal not responding` | Portal accessibility service died (sleep timeout) | Re-run `setup_portal.sh §5-6` |
| Screenshot shows bounding boxes | Element-inspect overlay is on | Manual Portal app overlay toggle (instructions in `setup_portal.sh §7`) |
| `screen_hash` collision (2 different screens, same id) | Top-N text signatures collided | Bump `profile.capture.hash_window` from 6 → 10, re-capture; or override `--block <letter>` |
| Coverage MISS labels look spurious | Word-match heuristic too loose; or labels too short | Make edge labels more descriptive in capture `--via` text |
| Validator V6 (broken refs) | Missing screen anchor declared in nav_edges | Either capture the missing screen or remove the dangling edge from frontmatter |
| Tab strip horizontally scrollable, only 3 visible | Common Compose pattern | h-swipe `(800,Y)→(100,Y)` to reveal hidden tabs before tap |
| `am start` resets tab state | Activity recreated | Use `monkey -p <pkg> -c LAUNCHER 1` to bring-to-front instead |
| BACK trapped on a Compose modal | Likely `v01` activity wizard step | Add activity name to `profile.modals.back_traps`; agent uses swipe-down |

---

## Anti-patterns (do NOT do these)

- ❌ Don't auto-`pm clear` the app to "reset" — that destroys the user's onboarding state.
- ❌ Don't assume bottom-nav coords from another app — every app's viewport is different.
- ❌ Don't paraphrase UI text in observations.md — verbatim or omit.
- ❌ Don't write specs from screenshots alone — always read the JSON dump for bounds + a11y signals.
- ❌ Don't `git commit` automatically — user must duyệt.
- ❌ Don't tap the universal blocklist (Subscribe / Logout / etc.) even if user asks — explain the risk.
- ❌ Don't broadcast `TOGGLE_OVERLAY` and assume it worked — Portal v0.6.5 silently ignores it; if screenshots show boxes, follow the manual fallback.
- ❌ Don't move spec files out of `<profile.feature_root>/<feature>/` — graph builder + MCP server expect the layout.

---

## Quick command reference

```bash
# Bootstrap a new app project (Phase 0)
re-spec-init

# Set up Portal on the device (one-time per device)
bash $(re-spec-paths --shell setup_portal.sh)

# Capture a single screen
re-spec-capture <feature> <screen_label>
re-spec-capture <feature> <screen_label> \
  --from <parent_label> --via "tap:(X,Y) <description>"

# Adb interactions
adb shell input tap X Y
adb shell input swipe X1 Y1 X2 Y2 800
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_HOME

# Coverage + render
re-spec-coverage-check <feature>
re-spec-render-nav <feature> -o <feature_root>/<feature>/<feature>_nav.md
re-spec-observations <feature> -o <feature_root>/<feature>/<feature>_observations.md

# Spec graph
re-spec-build-graph --stats
re-spec-validate
re-spec-query feature <feature>
re-spec-query acceptance <feature>

# MCP server (auto-loaded by .mcp.json; manual register at user scope:)
bash $(re-spec-paths --shell register-mcp-user.sh)
```

All `re-spec-*` commands above are installed by `pip install re-spec-mobile` (or
`bash INSTALL.sh` which runs the pip install + symlinks the skill itself). After
install, the commands are on PATH globally.

Bundled shell scripts (setup_portal.sh, register-mcp-user.sh) live inside the
installed package; resolve their path with `re-spec-paths --shell <script_name>`.
