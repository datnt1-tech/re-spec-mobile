# OPERATIONS — Vận hành workflow re-spec-mobile

> **Audience**: dev/PM thực sự chạy workflow để spec một feature mobile.
> Đọc file này từ đầu đến cuối là biết cách vận hành end-to-end, không cần
> đọc thêm chỗ khác (trừ khi cần chi tiết từng tool — xem `SKILL.md` hoặc
> `SPEC_SCHEMA.md`).

Workflow chia 3 phần:

- **Phần A** — Setup máy (1 lần per machine, ~5 phút)
- **Phần B** — Setup project mới (1 lần per app, ~15 phút)
- **Phần C** — Vận hành 1 feature (loop N lần per feature, 1-3h tùy size)

---

## Phần A — Setup máy (one-time, ~5 phút)

```bash
git clone <re-spec-mobile-repo> ~/repos/re-spec-mobile
cd ~/repos/re-spec-mobile
bash INSTALL.sh                                              # symlink skill + agents vào ~/.claude/
bash skills/re-spec-mobile/tools/register-mcp-user.sh        # optional: spec-graph MCP user-scope
```

`INSTALL.sh` mặc định symlink (live updates từ repo). Dùng `--copy` cho production (offline / pinned version).

Verify: mở 1 Claude Code session bất kỳ, gõ `/` thấy `re-spec-mobile` trong list skill.

### Dependencies cần có sẵn trên máy

| Tool | Mục đích | Cài thế nào |
|---|---|---|
| `python3` ≥ 3.10 | Toolkit + MCP server | hệ điều hành mặc định |
| `pyyaml` | Parse profile + scope + frontmatter | `pip install pyyaml` |
| `adb` | Drive Android device | brew/apt/winget Android platform-tools |
| `claude` CLI | Đăng ký MCP user-scope | từ Anthropic |
| Git Bash hoặc WSL (Win) | Chạy shell scripts | optional |

### Uninstall

```bash
rm ~/.claude/skills/re-spec-mobile
rm ~/.claude/agents/{app-explorer,spec-writer}.md
claude mcp remove spec-graph -s user 2>/dev/null || true
```

---

## Phần B — Setup project mới (one-time per app, ~15 phút)

```bash
cd /path/to/your-app-spec-repo                               # hoặc mkdir mới
adb devices                                                  # chắc chắn 1 device cắm
adb shell am start -n <pkg>/<MainActivity>                   # mở app target

# Bootstrap profile + spec dirs + .mcp.json
python ~/.claude/skills/re-spec-mobile/tools/init_project.py
# → tự detect viewport + focused app, fill template

$EDITOR .spec-profile.yml                                    # confirm package + main_activity + tabs
python ~/.claude/skills/re-spec-mobile/tools/profile_loader.py --validate

# Cài Portal lên device (one-time per device)
bash ~/.claude/skills/re-spec-mobile/tools/setup_portal.sh
# → nếu fail ở §4: enable Accessibility manually trong Settings, rerun
# → nếu screenshot dính bounding box: tap toggle Overlay trong Portal app (1 lần)
```

Sau bước này, repo có:

```
your-app-spec-repo/
├── .spec-profile.yml                                        # adapter config
├── .mcp.json                                                # spec-graph MCP pointer
└── spec/
    ├── feature/                                             # outputs sẽ vào đây
    ├── screens/                                             # PNG captures
    ├── ui_dumps/                                            # JSON+XML a11y dumps
    ├── _raw/                                                # nav_graph.json per feature
    ├── _graph/                                              # nodes/edges/index sau build
    └── _contracts/                                          # API/Kotlin extracts
```

### Checklist sau khi setup B

- [ ] `python tools/profile_loader.py --validate` → OK
- [ ] `adb devices` → 1 device "device" state
- [ ] `adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80` → chứa `"status":"success"`
- [ ] `adb shell dumpsys window | grep mCurrentFocus` → focus đúng package target
- [ ] Capture test 1 screen → screenshot không có bounding box overlay

Nếu có item fail → mở `SKILL.md` mục "Failure modes + recovery" cho remediation.

---

## Phần C — Vận hành 1 feature (loop N lần)

10 phase với 3 PM gate. PM = product manager hoặc người quyết định scope; Claude = AI orchestrator + 2 sub-agent (`app-explorer` + `spec-writer`).

### Workflow swimlane

| Phase | PM | Claude (orchestrator) | Device | Artifact mới |
|---|---|---|---|---|
| **1** Kickoff | "spec feature X" | TaskList 10 task; hỏi starting state | mở app tab tương ứng | TaskList |
| **1.5 GATE 1** Scope | Đọc scope draft → sửa must_visit/out_of_scope; trả lời Open Q; set `status: signed_off`, fill `signed_off_by`+`at` | Reconnaissance 1-2 màn → propose `<feature>_scope.md` draft → wait sign-off | reco capture | `<feature>_scope.md` (draft → signed_off) |
| **2** Capture | (idle) | invoke `app-explorer` agent | tap/swipe/back theo must_visit | `nav_graph.json` + N×{png,json,xml} |
| **3** Reset handoff | reset app khi agent BLOCKED | request reset với template cụ thể | physical reset | (none) |
| **4** Coverage check | (idle) | `coverage_check.py --scope` mid-loop | (idle) | console MISS report bucketed |
| **4.5 GATE 2** Coverage | Đọc report → quyết định re-capture/drop/revise; set `status: sign_off_pass` | `coverage_report.py` → generate report | (idle) | `<feature>_coverage_report.md` (draft → sign_off_pass) |
| **5** Write specs draft | (idle) | invoke `spec-writer mode=draft` | (idle) | 3 file draft |
| **5.5 GATE 3** Spec review | Trả lời Open Q §7 inline; set `status: approved` khi xong | wait PM, sau đó invoke `spec-writer mode=revise` | (idle) | 3 file finalized |
| **6** Graph rebuild | (idle) | `build_graph --check` + `validate_spec` | (idle) | `_graph/{nodes,edges,index}.json` |
| **7** Commit | duyệt commit | propose commit message, `git commit` | (idle) | git commit |

### Trigger câu lệnh (PM-facing)

PM chỉ cần biết 4 câu, không cần dùng terminal:

```
1. "spec feature <name>"                         # khởi động — Phase 1
2. "scope OK, sign-off"                          # sau Gate 1 — Phase 2 start
3. "coverage report OK, sign-off pass"           # sau Gate 2 — Phase 5 start
4. "open questions reviewed, ready to commit"    # sau Gate 3 — Phase 7 start
```

Claude tự suy diễn workflow position, run đúng tool tương ứng (set frontmatter `status:`, invoke agent next, etc.).

### Branching khi không happy path

| Tình huống | Phase | Action |
|---|---|---|
| PM bận, chưa sign-off scope | 1.5 | Claude pause, hiển thị "blocked: scope draft awaiting PM" |
| Agent capture xong, có gap | 4.5 | PM set `sign_off_fail` → loop back Phase 2 với gap list làm targets |
| PM thấy capture đủ nhưng cần thêm 1 cluster sau khi review | 4.5 | Bump `scope_version` 1→2 trong scope.md, re-sign-off, loop back Phase 2 |
| Spec draft thiếu detail PM cần | 5.5 | PM thêm Open Q mới vào §7 → spec-writer revise pick up |
| Open Q không trả lời được | 5.5 | PM viết `**PM answer**: WONTFIX` → spec-writer drop khỏi spec, ghi vào `decisions:` của coverage_report |
| Test lại feature đã spec sau update app | mọi phase | Bump `scope_version`, status `approved` → `revising`, run lại từ Phase 2 |
| Portal die giữa capture | 2 | Agent return BLOCKED; PM rerun `setup_portal.sh §5-6` |
| Compose `v01` modal trap KEYCODE_BACK | 2 | Agent dùng swipe-down dismiss; ghi activity vào `profile.modals.back_traps` để skip lần sau |

### Time estimate per feature

| Feature size | Total time | Bottleneck |
|---|---|---|
| Nhỏ (3-5 màn, no scope) | 30-45 phút | Capture loop |
| Vừa (10-15 màn, full gate) | 1.5-2.5h | PM review (2 lần ≈ 30 phút) |
| Lớn (20+ màn, multi-cluster) | 3-5h | Capture loop + Gate 2 re-capture có thể loop 2-3 lần |

PM time/feature ≈ 30-45 phút (tổng 3 gate review). Claude time ≈ phần còn lại.

### Auto-approve exception (skip gate cho feature nhỏ)

Skip Gate 1 + Gate 2 khi ALL of:
- Feature ước tính < 5 màn
- User explicitly nói "skip scope" hoặc "auto"
- No PM in the loop (solo dev mode)

Trong auto-approve, Claude:
- Set `bypass_scope=true` cho `app-explorer`
- Skip generate `coverage_report.md`
- spec-writer chạy ngay sau capture với mode=draft
- Spec status sẽ là `draft` thay vì `approved` (cảnh báo trong commit message)

---

## Per-phase detail (advanced)

### Phase 1.5 — GATE 1 detailed flow

1. Check existence của `<feature_root>/<feature>/<feature>_scope.md`
2. Nếu không có → Claude propose draft:
   - Quick reconnaissance capture (1-2 màn landing)
   - `spec_search <feature>` qua MCP để tìm related specs
   - Q&A với PM:
     - "Feature này gồm những cluster nào? (vd Wizard / Plan Detail / Paywall)"
     - "Cluster nào IN scope, cluster nào OUT?"
     - "Có ràng buộc gì với cluster IN? (vd 'phải capture cả back press', 'A/B variant')"
     - "Câu hỏi nào cần PM trả lời trước khi capture?"
   - Generate scope.md từ `templates/scope.md.tmpl`, fill answers, set `status: draft`
3. PM review:
   - Đọc scope.md, sửa `must_visit` / `optional_visit` / `out_of_scope` clusters
   - Trả lời Open Q inline: dưới mỗi `### Q-NN ... {#anchor}`, viết:
     ```markdown
     **PM answer**: <text trả lời>
     ```
     Hoặc `**PM answer**: WONTFIX` nếu drop câu hỏi
   - Set `status: signed_off`, fill `signed_off_by` + `signed_off_at`
   - Bump `scope_version` nếu revising sau lần sign-off trước
4. Verify:
   ```bash
   python <skill_tools>/scope_loader.py <feature> --check
   ```
   Exit 0 → continue Phase 2. Exit 1 → tell PM what's blocking.

### Phase 4.5 — GATE 2 detailed flow

1. Generate report:
   ```bash
   python <skill_tools>/coverage_report.py <feature>
   ```
   Tạo `<feature_root>/<feature>/<feature>_coverage_report.md` với 5 section:
   - §1 Summary metrics
   - §2 Captured (matches scope)
   - §3 Gaps (must_visit miss)
   - §4 Drift (capture ngoài scope)
   - §5 PM review (template trống)
2. PM review:
   - Đọc §1-4, quyết định mỗi gap + drift item
   - Append `decisions:` vào frontmatter (action items)
   - Append `unknowns_resolved:` nếu có Open Q còn sót
   - Set `status: sign_off_pass` HOẶC `sign_off_fail`
3. Branch:
   - `sign_off_pass` → Phase 5
   - `sign_off_fail` → loop back Phase 2 với gap/drift làm targets, bump `scope_version`

### Phase 5.5 — GATE 3 detailed flow

1. Spec-writer mode=draft return `DONE-PENDING-REVIEW` với explicit list Open Q
2. Claude tell PM:
   - "Spec draft ready. Open `<feature_root>/<feature>/<feature>_feature_spec.md`"
   - "Tập trung §7 Open Questions — N câu cần bạn trả lời inline"
3. PM annotate inline trong §7:
   - Dưới mỗi `### Q-NN`, viết `**PM answer**: <text>` hoặc `WONTFIX`
   - Optionally tweak §3 (per-screen) + §8 (acceptance) trực tiếp
4. PM signal "OK reviewed" → Claude reinvoke spec-writer mode=revise
5. spec-writer:
   - Re-read §7, find answered questions
   - Fold answer vào section liên quan (§3/§4/§5/§6/§8)
   - Remove resolved questions từ §7
   - Return `DONE` với `remaining_open_questions: <count>`
6. Loop:
   - `remaining_open_questions == 0` → Phase 6
   - Else → tell PM, loop back step 3

---

## Self-verify checklist (chạy đầu mỗi session)

```bash
# 1. Profile valid
python <skill_tools>/profile_loader.py --validate

# 2. Device connected
adb devices

# 3. Portal alive
adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80

# 4. App focused
adb shell dumpsys window | grep mCurrentFocus | head -1

# 5. Existing specs (reference style)
ls $(python <skill_tools>/profile_loader.py | python -c 'import json,sys; print(json.load(sys.stdin)["paths"]["feature_root"])')
```

Pass tất cả 5 → ready. Fail → check `SKILL.md` mục "Failure modes".

---

## Common gotchas (đã chứng kiến trong dogfood + bible-agent)

### Capture phase

- **Floating overlay nuốt swipe**: audio mini-player, FAB → swipe ở `edge_swipe_x` (default 200) với `long_swipe_duration_ms` (default 1200)
- **Tab strip horizontal scrollable**: chỉ 3/5 tab visible → h-swipe `(800,Y)→(100,Y)` để reveal hidden tabs
- **Sticky header above sub-tabs**: swipe origin y < sticky band → page scrolls, tab strip không. Origin y phải dưới sticky.
- **Compose `v01` modal trap BACK**: Wizard sheet, font sheet — dùng swipe-down (top→bottom). Add activity vào `profile.modals.back_traps`.
- **Audio mini-player invisible to a11y**: visible trong screenshot only; document trong notes.
- **Portal accessibility die qua đêm**: device sleep lâu → Portal service unbound. Rerun `setup_portal.sh §5-6`.

### Coverage check

- **Word-match heuristic OLD bug** (đã fix): label "Tap to chat" matched edge "tap:(540,1100) Verse" → false positive covered. Fix: bounds-uniqueness ±30px + exact label substring.
- **Bottom-nav cross-feature taps appear as MISS**: tabs (Chat/Today/Bible/etc.) trong landing là clickable nhưng không nằm trong feature scope. PM khai báo "navigation/tabs" cluster as `out_of_scope`.
- **Re-visit captures (`round2_*`, `step_*`)** appear as drift: same screen, different label. Heuristic chưa dedup theo screen_id. Workaround: PM mark drop trong coverage_report.

### Spec writer

- **Forward-ref `[V6]` errors** trong validate_spec là EXPECTED ngay sau Gate 1+2 — scope.md + coverage_report.md ref đến screens/observations chưa tồn tại. Sẽ resolve sau Phase 5.
- **Component reuse detection** trước khi declare component mới: `grep -r "reuse_key:" <feature_root>/`. Match → dùng `reuses:` block, không tạo component mới.
- **Open Q "carry over"**: question chưa trả lời trong scope.md hoặc coverage_report.md PHẢI appear lại trong feature_spec §7 với traceability `(carried from <feature>/question/scope_q_NN)`.

---

## File system reference

```
project_root/                                                # repo bạn đang spec
├── .spec-profile.yml                                        # adapter config (bạn edit)
├── .mcp.json                                                # MCP server pointer (auto)
└── spec/
    ├── feature/<feature>/
    │   ├── <feature>_scope.md                  ← Layer 0 (Gate 1, PM signs)
    │   ├── <feature>_observations.md           ← Layer 1 (writer agent)
    │   ├── <feature>_spec.md                   ← Layer 2 (writer agent)
    │   ├── <feature>_feature_spec.md           ← Layer 3 (writer agent)
    │   ├── <feature>_coverage_report.md        ← Layer 4 (Gate 2, PM signs)
    │   └── <feature>_nav.md                    ← auto from render_nav.py
    ├── screens/<feature>/screen_*.png          ← capture.py output
    ├── ui_dumps/<feature>/screen_*.{json,xml}  ← capture.py output
    ├── _raw/<feature>/nav_graph.json           ← capture.py mutated
    ├── _graph/{nodes,edges,index}.json         ← build_graph.py output
    └── _contracts/{kotlin,openapi}/            ← extract_contracts.py output
```

---

## Cross-references

- **Workflow contract** (10 phase + 3 gate): `skills/re-spec-mobile/SKILL.md`
- **Schema** (frontmatter + anchors + edges): `skills/re-spec-mobile/canonical/SPEC_SCHEMA.md`
- **Agent contract** (capture / write): `agents/{app-explorer,spec-writer}.md`
- **Sample profile**: `examples/bible-agent.spec-profile.yml`
- **Migration cũ → mới**: `docs/MIGRATION.md`
- **Dogfood test result** (verify gate work end-to-end): `docs/DOGFOOD_REPORT.md`
- **Plan cho non-tech user** (T0/T1/T2): `docs/ROADMAP_NONTECH.md`
