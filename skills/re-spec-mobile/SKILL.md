---
name: re-spec-mobile
description: |
  Reverse-engineer bất kỳ app Android nào thành bộ spec 3 layer
  (observations + flow + implementation) bằng droidrun Portal + adb +
  spec-graph MCP. Kích hoạt khi user nói "RE app", "spec feature X",
  "auto-test feature X", "tạo spec cho app này", "rebuild spec mobile",
  hoặc gọi trực tiếp `/re-spec-mobile`. Skill app-agnostic: mọi giá trị
  đặc thù app (package, viewport, blocklist, tabs, paths, reference style)
  đọc từ file `.spec-profile.yml` của project.
version: 1.0.0
---

# re-spec-mobile — Reverse-engineer mobile app thành spec

> **Skill này làm gì, gói trong 1 câu:** điều khiển 1 device Android được kết nối,
> capture mọi screen của 1 feature, sinh ra 3 file markdown (observations / flow
> / implementation) để engineer rebuild lại feature mà không cần chạy app gốc.

## Output: tiếng Việt + thuật ngữ tiếng Anh

**Mọi spec sinh ra phải viết bằng tiếng Việt**, riêng các thuật ngữ chuyên môn
giữ nguyên tiếng Anh (xem `docs/I18N_GLOSSARY.md`). Áp dụng cho:

- Mô tả prose trong observations / spec / feature_spec
- Section heading mang tính prose ("Mô tả", "Lý do", "Hành vi quan sát")
- Comment + Open Questions + PM answer
- Commit message + PR description

**Giữ nguyên tiếng Anh:**
- YAML frontmatter keys (`feature`, `layer`, `anchor`, ...) + values là enum/anchor
- Code block, CLI command, file path, function name
- UI string trích nguyên văn từ app (giữ ngôn ngữ gốc của app — kể cả tiếng Anh)
- Status string (`DONE`, `BLOCKED`, `DONE-PARTIAL`, `signed_off`, ...)
- Technical term: `tap`, `swipe`, `scroll`, `viewport`, `bounds`, `blocklist`,
  `scope`, `gate`, `must_visit`, `coverage`, `drift`, `gap`, `anchor`,
  `frontmatter`, `reuse_key`, `Portal`, `adb`, `MCP`, `acceptance criteria`, ...

## Khi nào dùng

Kích hoạt skill này khi user muốn:

- Spec 1 feature của app Android mà họ không sở hữu source code (research đối thủ,
  RE nội bộ cho methodology spec-first, tạo baseline regression).
- Auto-test 1 flow + lưu artifact (screenshot + a11y dump + nav graph).
- Bootstrap 1 project mới để bắt đầu spec (chỉ Phase 0 — xem dưới).
- Chạy lại capture với build app mới để phát hiện drift so với spec cũ.

**KHÔNG dùng** cho: implement app (dùng skill `implement-feature`); query spec
trên graph có sẵn (dùng agent `spec-graph`); RE nội tạng APK (dùng skill
`android-reverse-engineering`).

## Input phải xác lập trước Phase 1

1. **Có profile chưa?** — phải có `.spec-profile.yml` ở root project. Nếu thiếu
   → chạy **Phase 0** (init).
2. **Device sống chưa?** — đúng 1 device trong `adb devices` khớp với
   `device.serial` trong profile (hoặc bất kỳ device nếu serial bỏ trống).
3. **Portal sống chưa?** — `adb shell content query --uri content://com.droidrun.portal/state`
   trả về `"status":"success"`. Nếu không → `bash $(re-spec-paths --shell setup_portal.sh)`.
4. **App đang focus chưa?** — `adb shell dumpsys window | grep mCurrentFocus`
   phải hiện `app.package` của profile. Nếu không, yêu cầu user mở app.
5. **Scope feature?** — user phải đặt tên feature (vd `bible`, `explore_create`).
   Slug này sẽ thành tên folder + giá trị field `feature` trong frontmatter.

Nếu (2–4) thất bại, báo cụ thể lỗi nào cho user và đề xuất command fix chính xác.
Đừng đoán.

---

## Workflow — 10 phase (kèm 3 PM gate)

Workflow có **3 gate do PM kiểm soát** xen giữa các phase tự động. Mỗi gate
sinh ra 1 artifact markdown PM duyệt, agent kế tiếp từ chối chạy nếu chưa có
sign-off. Cách này chặn được failure mode "AI capture cái nó nghĩ, không phải
cái PM muốn".

```
Phase 0   Bootstrap (1 lần / project)
Phase 1   Kickoff
Phase 1.5 ━━━ GATE 1: Scope contract ━━━━━━━━━━ PM ký <feature>_scope.md
Phase 2   Capture loop (agent app-explorer)
Phase 3   Reset handoff (khi bị stuck)
Phase 4   Coverage check (giữa loop, tự động)
Phase 4.5 ━━━ GATE 2: Coverage report ━━━━━━━━━ PM ký <feature>_coverage_report.md
Phase 5   Viết draft spec (agent spec-writer, mode=draft)
Phase 5.5 ━━━ GATE 3: Spec review loop ━━━━━━━━ PM trả lời open question inline
Phase 6   Rebuild + validate spec graph
Phase 7   Commit (thủ công)
Phase 8   App overview synthesis (chạy sau ≥2 feature, không gate, idempotent)
```



### Phase 0 — Bootstrap (1 lần / project)

Khi `.spec-profile.yml` chưa tồn tại trong CWD hoặc parent nào.

```bash
re-spec-init
```

Lệnh này:
- Detect viewport device (`adb shell wm size`) + app đang focus, patch template
  với giá trị tìm được.
- Ghi template `.spec-profile.yml` vào CWD.
- Scaffold `spec/{feature,screens,ui_dumps,_raw,_graph,_contracts}/`.
- Ghi `.mcp.json` để spec-graph MCP server tự load trong repo này.

Sau đó **dừng và hỏi user**:
- Confirm `app.package` + `app.main_activity` (đã autodetect nếu device đang mở app).
- Điền `navigation.tabs` (làm sau khi Phase 2 đã capture được 1 screen để đọc).
- Thêm pattern `blocklist.custom` đặc thù app (paywall CTA, verb destructive).

Validate trước khi tiếp:

```bash
re-spec-profile --validate
```

Sau đó chạy `bash $(re-spec-paths --shell setup_portal.sh)` để bật Portal trên device.
User phải bật accessibility manually nếu script fail ở section 4 (hay gặp trên
Pixel/AOSP — in chính xác hướng dẫn từ setup_portal.sh).

### Phase 1 — Kickoff

Khi user nói "spec feature X":

1. Đọc `.spec-profile.yml`. Confirm `app.package`, `device.viewport`,
   `paths.spec_root` đã set; nếu thiếu thì từ chối.
2. Verify Portal sống (checklist 60-giây phía dưới).
3. Hỏi user (chỉ khi chưa nói rõ): feature nào? starting state (tab nào, screen
   nào)? cần reset không?
4. Tạo TaskList với ~10 task (1 task / phase, gồm 3 gate).
5. **Quyết định auto-approve:** nếu user báo "feature nhỏ, ~3 screen" HOẶC nói
   thẳng "skip scope" → set `bypass_scope=true`. Ngược lại tiếp Phase 1.5 (Gate 1).
6. Chờ user reply `ready, <feature>, <starting screen>`.

### Phase 1.5 — GATE 1: Scope contract (PM sign-off trước khi capture)

**Mục đích**: chốt scope giữa PM ↔ Claude TRƯỚC capture. Không để AI tự decide
"đi đâu là đủ" — đó là root cause #1 của "AI auto-test chưa đi hết các màn".

#### Workflow

1. Check xem `<feature_root>/<feature>/<feature>_scope.md` đã tồn tại chưa.
   - status=signed_off → skip qua Phase 2
   - status≠signed_off → tiếp tục từ chỗ PM còn dở
   - File thiếu → Claude propose draft (bước kế)

2. **Claude propose draft scope** bằng cách:
   - Capture trinh sát nhanh (1-2 screen của feature landing)
   - Đọc spec liên quan đã có (`spec_search <feature>` qua MCP)
   - Hỏi PM bằng Q&A ngắn:
     - "Feature này gồm những cluster nào? (vd Wizard / Plan Detail / Paywall)"
     - "Cluster nào IN scope, cluster nào OUT?"
     - "Có ràng buộc gì với cluster IN? (vd 'phải capture cả back press', 'A/B variant')"
     - "Câu hỏi nào cần PM trả lời trước khi capture?"
   - Sinh `<feature>_scope.md` từ `templates/scope.md.tmpl`, điền câu trả lời,
     set `status: draft`.

3. **PM review + sign-off**:
   - Đọc scope.md, sửa must_visit / optional / out_of_scope nếu cần
   - Trả lời Open Question inline (`**PM answer**: <text>` dưới mỗi `### Q-NN`)
   - Set `status: signed_off`, điền `signed_off_by` + `signed_off_at`
   - Tăng `scope_version` nếu sửa lại sau lần sign-off trước

4. Claude verify sign-off:
   ```bash
   re-spec-scope <feature> --check
   ```
   Exit 0 → tiếp Phase 2. Exit 1 → báo PM đang vướng gì.

#### Telegram bridge (nếu profile có `pm_channel`)

Nếu `.spec-profile.yml` có khai báo `pm_channel.type: telegram`, sau khi sinh
draft scope.md:

```bash
re-spec-pm-ask <feature> --gate scope     # post mỗi Open Question lên Telegram
```

Sau đó loop poll cho tới khi `re-spec-scope --check` xanh:

```bash
re-spec-pm-sync <feature>                 # long-poll 30s, fold reply → scope.md
```

`re-spec-pm-sync` exit code:
- `0` — có reply mới, đã fold vào file
- `2` — chưa có reply (timeout) — báo user "đợi PM rồi /re-spec-mobile lại"
- `1` — lỗi config / API

Khi PM trả lời mọi câu trong Telegram → file scope.md tự cập nhật `**PM answer**:`
inline → PM còn việc cuối: set `status: signed_off` + `signed_off_by/_at` (Telegram
KHÔNG tự động flip status — PM phải edit file). Lý do: status flip = commit-able
artifact, cần human review final state, không nên auto từ chat.

#### Trường hợp ngoại lệ — Auto-approve

Skip Gate 1 khi cả:
- Feature ước tính < 5 screen
- User nói thẳng "skip scope" hoặc "auto"
- Không có PM trong loop (mode solo dev)

Trong auto-approve, Claude tiếp với `bypass_scope=true`. Capture loop vẫn sinh
nav_graph + dump; coverage_report skip ở Gate 2.

### Phase 2 — Capture loop

Delegate cho **agent `app-explorer`** (subagent đi kèm package này). Agent chạy
tự động với quyền adb + Portal; bạn ở lại main context. Contract của agent:

- **Input:** feature slug, mô tả starting screen, đường dẫn profile.
- **Tools:** Bash + Read.
- **Output:** điền vào `<screens_root>/<feature>/`, `<dumps_root>/<feature>/`,
  `<raw_root>/<feature>/nav_graph.json`. Trả về status ngắn: số screen đã
  capture, số edge, blocker nếu có.

Driver loop (mỗi screen):

```bash
# Verify Portal sống
adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80
# → phải chứa '"status":"success"'

# Landing
re-spec-capture <feature> screen_01_landing

# Tap 1 element để đến sub-screen
adb shell input tap 540 1100
re-spec-capture <feature> screen_02_<name> \
  --from screen_01_landing --via "tap:(540,1100) <element label>"

# Scroll segment (dùng edge_swipe_x từ profile khi center bị overlay nuốt)
adb shell input swipe 540 1500 540 500 800

# Back
adb shell input keyevent KEYCODE_BACK
```

**Tip chống stuck loop** (đúc kết từ kinh nghiệm):

- Dùng `coverage_check.py <feature>` giữa loop để biết clickable nào còn sót.
- Swipe duration ≥ 600ms, < 1500ms (dài hơn = scroll, ngắn hơn = fling/tap).
- Nếu center swipe không kéo được content (floating overlay nuốt), dùng
  `profile.scroll.edge_swipe_x` (default 200) và `long_swipe_duration_ms`.
- Compose modal sheet `v01` đôi khi nuốt KEYCODE_BACK — list chúng vào
  `profile.modals.back_traps`. Dismiss bằng swipe-down (top→bottom).
- Parse toạ độ tap: đọc `<dumps_root>/<feature>/<screen>.json` rồi lấy `bounds`
  từ node clickable; centre = midpoint của bounds.

### Phase 3 — Reset handoff (khi stuck)

Tạm dừng và hỏi user theo template chuẩn:

```
Stuck ở <mô tả screen>. Cần bạn:
  1. <hành động vật lý cụ thể — vd force-close app, tap Settings, ...>
  2. <hành động kế>
Sau đó reply: ready, <feature>, <state mới>
```

**KHÔNG** tự động `pm clear` package. **KHÔNG** force-restart app bằng
`am start` — thường mất tab/scroll state. Chỉ user reset.

### Phase 4 — Coverage check (giữa loop, tự động)

```bash
re-spec-coverage-check <feature> --scope
```

Flag `--scope` phân loại MISS theo trạng thái scope (must_visit / optional /
out_of_scope / unscoped). Nếu còn MISS trong bucket `must_visit_screen` → loop
về Phase 2 với target ưu tiên. MISS out-of-scope thì bỏ qua (đã chốt skip ở
Gate 1).

Blocklist đọc từ `profile.blocklist` nên `Subscribe / Logout / Buy / Continue`
v.v. tự động bị filter.

### Phase 4.5 — GATE 2: Coverage report (PM audit trước khi viết)

**Mục đích**: PM verify rằng phase capture thực sự đã phủ scope contract trước
khi spec-writer tốn công sinh prose.

#### Workflow

1. Sinh report:
   ```bash
   re-spec-coverage-report <feature>
   ```
   Ghi `<feature_root>/<feature>/<feature>_coverage_report.md` với 5 section:
   summary metric / captured / gap / drift / template PM review.

2. **PM review**:
   - Đọc coverage_report.md section 1-4
   - Mỗi Gap: quyết định re-capture / sửa scope / chấp nhận partial
   - Mỗi Drift: quyết định thêm vào scope cluster X / bỏ / chuyển out_of_scope
   - Mỗi Open Question còn dở: trả lời inline
   - Append decision vào field `decisions:` trong frontmatter
   - Set `status: sign_off_pass` HOẶC `sign_off_fail`

3. Claude rẽ nhánh theo PM decision:
   - `sign_off_pass` → tiếp Phase 5
   - `sign_off_fail` → loop về Phase 2 với gap/drift action item làm target
     capture mới. Bump `scope_version` nếu PM sửa scope.

#### Telegram bridge (nếu profile có `pm_channel`)

Khác Gate 1: Gate 2 chỉ cần 1 message duy nhất xin PM ký pass/fail.

```bash
re-spec-pm-ask <feature> --gate coverage   # post tóm tắt §1 Summary + chờ verdict
re-spec-pm-sync <feature>                  # fold reply (pass/fail) vào frontmatter
```

PM reply format trong Telegram:
- `pass <ghi chú ngắn>` → `re-spec-pm-sync` tự set `status: sign_off_pass` +
  append vào `decisions:` trong frontmatter
- `fail <lý do>` → set `status: sign_off_fail` + append decision

Reply không bắt đầu bằng `pass`/`fail` bị ignore — PM nhắn lại đúng format.
Đây là khác biệt duy nhất so với gate khác: gate này tự flip status (an toàn vì
chỉ có 2 giá trị enum, audit-able qua `decisions:`).

#### Trường hợp ngoại lệ — Auto-approve

Nếu `bypass_scope=true` (feature nhỏ) → skip sinh coverage_report, đi thẳng
Phase 5.

### Phase 5 — Viết draft spec

Delegate cho **agent `spec-writer`** (subagent đi kèm package này). Contract:

- **Input:** feature slug, đường dẫn profile. Đọc từ
  `<dumps_root>/<feature>/`, `<raw_root>/<feature>/nav_graph.json`,
  `<screens_root>/<feature>/`, kèm canonical reference (hoặc
  `profile.reference.canonical_feature` nếu có set, hoặc
  `<skill_dir>/canonical/*.sample.md`).
- **Tools:** Read + Write + Grep + Bash.
- **Output:** 3 file trong `<feature_root>/<feature>/`:
  - `<feature>_observations.md` (Layer 1 — cấu trúc tự gen từ
    `observations_tmpl.py`, agent điền "Hành vi quan sát" + "Note" mỗi screen)
  - `<feature>_spec.md` (Layer 2 — agent viết từ đầu theo `spec.md.tmpl` +
    cấu trúc canonical)
  - `<feature>_feature_spec.md` (Layer 3 — cấu trúc 9 section từ
    `feature_spec.md.tmpl` + canonical)
- **Helper auto-gen** agent chạy đầu tiên:
  ```bash
  re-spec-observations <feature> -o <feature_root>/<feature>/<feature>_observations.md
  re-spec-render-nav        <feature> -o <feature_root>/<feature>/<feature>_nav.md
  ```
  Sinh boilerplate; agent chỉ viết prose + frontmatter + section còn thiếu.

Agent gọi với `mode=draft` → trả về `DONE-PENDING-REVIEW` kèm danh sách rõ
Open Question PM phải trả lời trong body spec (§7).

### Phase 5.5 — GATE 3: Spec review loop (PM trả lời open question inline)

**Mục đích**: bắt mọi mơ hồ trong spec TRƯỚC khi commit. PM đọc draft, trả lời
Open Question inline, spec-writer fold câu trả lời vào spec final.

#### Workflow

1. Claude báo user (PM) review:
   - "Spec draft sẵn sàng. Mở mọi file `<feature>_*.md` trong `<feature_root>/<feature>/`."
   - "Tập trung `<feature>_feature_spec.md` §7 Open Questions — N câu cần bạn trả lời inline."
   - Format: dưới mỗi `### Q-NN`, thêm `**PM answer**: <text>` (hoặc `WONTFIX` để bỏ câu hỏi).

2. PM annotate inline. Có thể chỉnh thêm §3 (per-screen) và §8 (acceptance) trực tiếp.

3. PM báo "OK reviewed" → Claude gọi lại spec-writer với `mode=revise`.

4. Spec-writer:
   - Đọc lại §7, tìm câu đã trả lời
   - Fold câu trả lời vào section liên quan (§3/§4/§5/§6/§8)
   - Xoá câu hỏi đã giải khỏi §7
   - Trả `DONE` với `remaining_open_questions: <count>`

5. Loop:
   - `remaining_open_questions == 0` → tiếp Phase 6
   - Ngược lại → báo PM "còn N câu, plz answer", loop về bước 1

#### Telegram bridge (nếu profile có `pm_channel`)

Sau khi spec-writer trả về `DONE-PENDING-REVIEW`:

```bash
re-spec-pm-ask <feature> --gate spec     # post mỗi Q-NN §7 lên Telegram
```

Loop sync cho tới khi mọi Open Question được PM trả lời:

```bash
re-spec-pm-sync <feature>                # fold reply → §7
```

Sau khi `pm-sync` báo `pending_count == 0`, gọi spec-writer mode=revise → writer
sẽ thấy mọi Q-NN đã có `**PM answer**:` body → fold vào section liên quan
(§3/§4/§5/§6/§8) → trả `DONE`.

`re-spec-pm-ask --gate spec` idempotent: chạy nhiều lần không repost câu đã
trong inbox; chỉ post Q-NN mới (khi spec-writer thêm câu mới ở round revise).

#### Trường hợp ngoại lệ — Auto-approve

Nếu `bypass_scope=true` VÀ không có PM trong loop → skip Gate 3. Spec-writer
trả `DONE-PENDING-REVIEW` và orchestrator commit kèm open question
documented (status: draft thay vì approved).

### Phase 6 — Rebuild + validate spec graph

```bash
re-spec-build-graph --stats
re-spec-validate <feature_root>/<feature>/
```

Fix mọi lỗi `[V*]` validator báo trước khi commit. MCP server auto-rebuild
mỗi lần gọi tool nên rebuild thủ công chủ yếu để hiển thị stats.

### Phase 7 — Commit (thủ công, không bao giờ auto)

Show cho user 1 draft commit message theo style sẵn có của project. Chỉ chạy
`git add` + `git commit` sau khi user duyệt rõ ràng. Style mặc định (theo
convention của bible-agent):

```
add <feature> feature specification document for implementation
```

Cho session lớn: kèm scope tag (`feat(spec):`, `chore(spec):`) và liệt kê các
phase đã chạy.

### Phase 8 — App overview synthesis (1 lần / app, idempotent rerun)

Sau khi ≥ 2 feature đã commit (Phase 7), sinh / refresh doc tổng app-level
**platform-agnostic** dùng được cho cả iOS rebuild + stake-holder không kỹ thuật.

```bash
re-spec-build-graph                  # đảm bảo graph fresh
re-spec-app-overview                 # render/refresh <spec_root>/app_overview.md
```

Doc gồm 10 section auto-generated (sitemap, cross-feature nav, **component
reuse map** = ứng viên design system, API surface, ...) + 5 section prose
designer/PM viết (mục tiêu sản phẩm, UX state pattern, navigation model abstract,
content rules, cross-cutting decisions).

#### Idempotent re-render

Auto section bọc trong HTML marker `<!-- AUTO:KEY START/END -->`. Mỗi lần
chạy lại `re-spec-app-overview`:
- Marker block: refresh từ graph mới
- Prose ngoài marker: **preserve nguyên** (không bao giờ overwrite)

Nghĩa là designer chỉ viết prose 1 lần; mỗi feature mới add → rerun để cập nhật
inventory + sitemap mà không mất prose cũ.

#### Linter platform-agnostic

```bash
re-spec-app-overview --check         # exit 1 nếu có forbidden token
```

Flag warning khi gặp `Compose / Kotlin / @Composable / Activity / Fragment /
SwiftUI / UIView / Storyboard / ...` ngoài code fence. Mục đích: doc dùng cho
cả 2 platform → KHÔNG đề cập framework cụ thể.

Mode default (không `--check`): chạy luôn lint, warn ra stderr, không block.
Mode `--strict` (CI): exit 1 nếu có warning.

#### Không gate

Khác Phase 1.5/4.5/5.5, Phase 8 KHÔNG có PM gate cứng. PM/designer review tự
do, commit khi hài lòng. Lý do: doc này iterate liên tục theo sản phẩm, gate
cứng = friction không cần thiết.

---

## Checklist tự verify 60-giây (chạy đầu mỗi session)

```bash
# 1. Profile có + valid
re-spec-profile --validate

# 2. Device đã connect
adb devices

# 3. Portal sống
adb shell "content query --uri content://com.droidrun.portal/state" | head -c 80
# Cần '"status":"success"' hoặc '"a11y_tree"'

# 4. App đang focus
adb shell dumpsys window | grep mCurrentFocus | head -1
# Cần package từ .spec-profile.yml

# 5. Spec đã có (làm reference style)
ls $(re-spec-profile | python -c 'import json,sys; print(json.load(sys.stdin)["paths"]["feature_root"])')
```

Pass cả 5 → sẵn sàng. Fail bất kỳ → dùng remediation tương ứng cho bước fail.

---

## Style convention (writer agent enforce)

Bất di bất dịch, định nghĩa trong `canonical/SPEC_SCHEMA.md`:

- **Heading tiếng Anh, prose tiếng Việt.** Ví dụ: `## 3. Block A — Welcome`,
  body "Đây là màn hình đầu tiên...".
- **String trích nguyên văn.** Wrap mọi UI text trong backtick. **KHÔNG**
  bao giờ dịch hay paraphrase. `Đăng nhập bằng Google` giữ nguyên.
- **Format bảng bounds** — 5 cột: `Class | Bounds | Clickable | Text | Content-desc`.
- **Mermaid flowchart với `subgraph`** theo block — `render_nav.py` tự làm.
- **Date tuyệt đối, ISO-8601** — `2026-04-21`, không bao giờ "yesterday" hay
  "tuần trước".
- **Không emoji** trừ khi user yêu cầu rõ.
- **Anchor marker** `{#<feature>/<type>/<name>}` sau mọi section heading khai
  báo node graph (screen / block / component / api / data_model / criterion /
  invariant).

---

## Subagent đi kèm skill này

| Agent | Khi orchestrator delegate | Model | Tools |
|---|---|---|---|
| `app-explorer` | Phase 2 capture loop — drive device, capture, build graph | sonnet | Bash, Read |
| `spec-writer` | Phase 5 sinh prose — điền 3 file markdown | opus | Read, Write, Grep, Bash |

Orchestrator (skill này) chỉ tự xử lý Phase 0 + 1 + 3 + 4 + 6 + 7. Phase 2 và
5 hoàn toàn của subagent để main context gọn.

---

## Failure mode + recovery

| Failure | Chẩn đoán | Action |
|---|---|---|
| `Portal not responding` | Portal accessibility service chết (sleep timeout) | Chạy lại `setup_portal.sh §5-6` |
| Screenshot hiện bounding box | Element-inspect overlay đang bật | Toggle overlay thủ công trong Portal app (hướng dẫn ở `setup_portal.sh §7`) |
| `screen_hash` đụng (2 screen khác nhau, cùng id) | Top-N text signature trùng | Bump `profile.capture.hash_window` từ 6 → 10, capture lại; hoặc override `--block <letter>` |
| Coverage MISS label trông giả | Heuristic word-match quá lỏng; hoặc label quá ngắn | Viết edge label mô tả hơn ở `--via` lúc capture |
| Validator V6 (broken refs) | Thiếu screen anchor đã khai trong nav_edges | Capture screen còn thiếu hoặc xoá edge dangling khỏi frontmatter |
| Tab strip scroll ngang, chỉ thấy 3 tab | Pattern Compose phổ biến | h-swipe `(800,Y)→(100,Y)` để hé tab giấu trước khi tap |
| `am start` reset tab state | Activity bị recreate | Dùng `monkey -p <pkg> -c LAUNCHER 1` để bring-to-front thay vì restart |
| BACK bị nuốt trên Compose modal | Có khả năng wizard step `v01` activity | Thêm tên activity vào `profile.modals.back_traps`; agent sẽ swipe-down |

---

## Anti-pattern (KHÔNG được làm)

- ❌ Đừng auto-`pm clear` app để "reset" — phá state onboarding của user.
- ❌ Đừng giả định toạ độ bottom-nav từ app khác — viewport mỗi app khác nhau.
- ❌ Đừng paraphrase UI text trong observations.md — nguyên văn hoặc bỏ.
- ❌ Đừng viết spec chỉ từ screenshot — luôn đọc JSON dump để lấy bounds + a11y.
- ❌ Đừng `git commit` tự động — user phải duyệt.
- ❌ Đừng tap blocklist universal (Subscribe / Logout / ...) kể cả khi user yêu
  cầu — giải thích rủi ro.
- ❌ Đừng broadcast `TOGGLE_OVERLAY` rồi giả định nó work — Portal v0.6.5 silent
  bỏ qua; nếu screenshot vẫn có box, làm theo fallback thủ công.
- ❌ Đừng move file spec ra khỏi `<profile.feature_root>/<feature>/` — graph
  builder + MCP server đều assume layout này.
- ❌ Đừng viết spec bằng tiếng Anh — output luôn là tiếng Việt (giữ technical
  term tiếng Anh, xem section đầu file này).

---

## Quick command reference

```bash
# Bootstrap project app mới (Phase 0)
re-spec-init

# Set up Portal trên device (1 lần / device)
bash $(re-spec-paths --shell setup_portal.sh)

# Capture 1 screen
re-spec-capture <feature> <screen_label>
re-spec-capture <feature> <screen_label> \
  --from <parent_label> --via "tap:(X,Y) <description>"

# Adb interaction
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

# App-level overview (Phase 8 — platform-agnostic)
re-spec-app-overview                             # render/refresh spec/app_overview.md
re-spec-app-overview --check                    # lint platform-specific tokens
re-spec-app-overview --section REUSE_MAP        # debug: 1 section ra stdout

# Telegram PM bridge (3 gate)
re-spec-pm-init                                  # 1 lần / project — lấy chat_id
re-spec-pm-ask <feature> --gate scope            # Gate 1: post Open Question
re-spec-pm-ask <feature> --gate coverage         # Gate 2: post xin pass/fail
re-spec-pm-ask <feature> --gate spec             # Gate 3: post Open Question §7
re-spec-pm-sync <feature>                        # poll reply, fold vào file

# MCP server (auto-load qua .mcp.json; register thủ công ở user scope:)
bash $(re-spec-paths --shell register-mcp-user.sh)
```

---

## Telegram PM bridge — setup 1 lần / project

Skill hỗ trợ Q&A 2 chiều với PM qua Telegram cho cả 3 gate. Nếu PM offline /
không dùng Telegram, skip section này — workflow vẫn chạy được, chỉ là PM phải
edit file `.md` trực tiếp.

### Setup

```bash
# 1. Tạo bot qua @BotFather → lấy bot token
# 2. Export token (KHÔNG commit vào yml)
export TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# 3. Add bot vào Telegram chat của bạn (DM hoặc group), gửi /start

# 4. Lấy chat_id
re-spec-pm-init
# → in ra chat_id, copy paste vào .spec-profile.yml:
#   pm_channel:
#     type: telegram
#     chat_id: <id từ output>
#     token_env: TELEGRAM_BOT_TOKEN

# 5. Validate
re-spec-profile --validate
```

Sau bước này, mỗi gate trong workflow tự động dùng Telegram nếu
`profile.pm_channel` có giá trị; bỏ qua nếu null/missing.

### Trạng thái persist

Mỗi feature có 1 file `<feature_root>/<feature>/.pm_inbox.json` lưu mapping
`telegram_message_id ↔ anchor` để `re-spec-pm-sync` biết reply nào fold vào
chỗ nào. File này **không commit** (đã có trong .gitignore mặc định, hoặc
add vào nếu chưa có).

### Troubleshooting

| Triệu chứng | Nguyên nhân | Fix |
|---|---|---|
| `thiếu bot token` | env var chưa export | `export TELEGRAM_BOT_TOKEN=...` |
| `getMe HTTP 401` | token sai hoặc revoke | regenerate qua @BotFather |
| `pm-init` không nhận message | bot chưa được add vào chat / chưa /start | gửi /start lại từ chat |
| `pm-sync` exit 2 mãi | PM chưa reply hoặc reply không vào message bot | nhắc PM reply đúng message bot (giữ thread) |
| Coverage reply ignore | text không bắt đầu bằng `pass`/`fail` | nhắc PM format: `pass <reason>` hoặc `fail <reason>` |
| Reply gone fold sai chỗ | inbox bị xoá giữa chừng | reset `.pm_inbox.json`, chạy lại `pm-ask --force` |

Mọi lệnh `re-spec-*` ở trên được cài bằng `pip install re-spec-mobile` (hoặc
`bash INSTALL.sh` chạy pip install + symlink luôn skill). Sau khi cài, lệnh
sẵn trên PATH global.

Shell script đi kèm (setup_portal.sh, register-mcp-user.sh) nằm trong package
đã cài; resolve path bằng `re-spec-paths --shell <script_name>`.
