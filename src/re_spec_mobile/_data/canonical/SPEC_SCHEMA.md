---
name: SPEC_SCHEMA
description: Schema canonical cho file spec. Định nghĩa YAML frontmatter + anchor ID convention cho 4 layer (scope, observations, flow, implementation, coverage_report). Source of truth cho tool build_graph / spec_query / validate_spec.
version: 1
last_updated: 2026-04-20
---

# Spec Schema — re-spec-mobile

> Đây là **schema bắt buộc** cho mọi file spec trong `spec/feature/<feature>/`.
> Tool `validate_spec.py` sẽ reject file không tuân thủ. Agent + viz + graph
> builder đều dựa vào schema này.
>
> **Ngôn ngữ output**: prose tiếng Việt, technical term + identifier giữ tiếng
> Anh (xem `docs/I18N_GLOSSARY.md`).

---

## 1. Folder layout

```
spec/
├── SPEC_SCHEMA.md                      # file này
├── feature/
│   ├── <feature>/
│   │   ├── <feature>_observations.md  # layer 1 — raw capture
│   │   ├── <feature>_spec.md          # layer 2 — flow spec
│   │   ├── <feature>_feature_spec.md  # layer 3 — implementation-ready
│   │   ├── <feature>_nav.md           # optional — Mermaid nav graph (auto)
│   │   └── <sub>_spec.md              # optional — sub-features (vd explore_create_spec.md)
│   └── app_overview_spec.md           # cross-cluster overview
├── _graph/                            # auto: nodes.json, edges.json, index.json
├── _contracts/                        # auto: openapi/, kotlin/
└── tools/                             # python toolkit
```

**Rule**: tên feature trong frontmatter PHẢI match tên folder `spec/feature/<feature>/`.

---

## 2. Anchor ID convention

**Format**: `<feature>/<type>/<name>` — slash-separated, lowercase-snake.

### Allowed types

| Type | Nghĩa | Layer thường xuất hiện |
|---|---|---|
| `screen` | 1 màn UI riêng biệt (activity / composable root / bottom sheet) | observations, flow, implementation |
| `block` | 1 block logic trong flow (A, B, C…) | flow |
| `component` | UI component reusable (session_reader, chapter_reader…) | implementation |
| `api` | 1 endpoint trong API contract | implementation |
| `data_model` | 1 Kotlin-like data class | implementation |
| `criterion` | 1 acceptance criterion có ID | implementation |
| `question` | 1 open question chờ verify | implementation, **scope** (PM unknowns) |
| `invariant` | 1 cross-screen invariant | implementation |
| `state` | 1 state trong state machine | flow |
| `cluster` | 1 cụm screens cùng functional purpose (PM-defined boundary) | **scope** |

### Ví dụ hợp lệ

```
today/screen/landing
today/screen/verse_reader
today/block/a
today/component/session_reader
today/api/get_today
today/data_model/today_session_content
today/criterion/ac_01
today/invariant/session_reader_reuse
today/state/progress_complete
explore/screen/plan_detail_read
explore_create/screen/wizard_step_3
```

### Rules

- **Lowercase + snake_case** cho `<name>`; dùng `_` không dùng `-`
- `<feature>` = tên folder (dùng `explore_create` không phải `explore/create`)
- `<type>` thuộc enum cố định ở trên
- Anchor phải **unique toàn repo**

---

## 3. Frontmatter chung (mọi layer)

Tất cả file spec BẮT BUỘC có YAML frontmatter mở đầu file:

```yaml
---
feature: <feature_name>            # required, match folder
layer: scope|observations|flow|implementation|coverage_report|overview   # required
anchor: <feature>/<layer>/root     # required, root anchor của file
title: <human title>               # required
last_updated: 2026-04-20           # required, ISO 8601
app_version: 4.3.10                # optional — capture session version
device: 8A5X0M2H8                  # optional
locale: vi-VN                      # optional
status: draft|signed_off|approved|stale|revising  # required cho scope + implementation + overview
related: [<anchor>, ...]           # optional, cross-references tới file khác
---
```

### Layer ordering (workflow)

Workflow Phase ↔ Layer mapping:

| Phase | Layer | File | Owner |
|---|---|---|---|
| 1.5 | `scope` | `<feature>_scope.md` | PM signs off; agent reads |
| 2 | (no file) | nav_graph.json + dumps | app-explorer agent |
| 4.5 | `coverage_report` | `<feature>_coverage_report.md` | coverage_report.py + PM review |
| 5 | `observations` | `<feature>_observations.md` | spec-writer agent |
| 5 | `flow` | `<feature>_spec.md` | spec-writer agent |
| 5 | `implementation` | `<feature>_feature_spec.md` | spec-writer agent |
| — | `overview` | `app_overview_spec.md` | manual cross-cluster doc |

**Layer `overview`** = cross-cluster document (vd `app_overview_spec.md`). Feature = `app`. Body không bắt buộc 9-section structure. Chủ yếu chứa `references` tới các feature spec khác.

---

## 3.5. Layer 0 — `<feature>_scope.md` (Gate 1 — PM contract)

**Mục đích**: chốt scope giữa PM ↔ Claude TRƯỚC khi capture. Mặc định mọi
feature phải có scope file; bỏ qua chỉ cho feature < 5 màn (auto-approve).

### Frontmatter

```yaml
---
feature: explore_create
layer: scope
anchor: explore_create/scope/root
title: Explore Create — Scope Contract
last_updated: 2026-05-04
status: signed_off                 # draft | signed_off | revising
signed_off_by: pm@team.com         # required when status=signed_off
signed_off_at: 2026-05-04          # required when status=signed_off
scope_version: 1                   # bump on each PM-approved revision

clusters:
  - id: explore_create/cluster/wizard_quiz
    name: Wizard Quiz Steps
    section_line: 30
    in_scope: true
    must_visit:                    # mỗi anchor MUST have a capture
      - explore_create/screen/wizard_intro
      - explore_create/screen/wizard_q1
      - explore_create/screen/wizard_q2
    optional_visit:                # capture nếu agent có thời gian
      - explore_create/screen/wizard_q1_back

  - id: explore_create/cluster/paywall_purchase
    name: Paywall Purchase Confirmation
    section_line: 60
    in_scope: false                # explicitly out
    reason: "billing flow, không safe to auto-test"

questions:                         # PM unknowns cần clarify trước capture
  - id: explore_create/question/scope_q_01
    section_line: 80
    summary: "Wizard có A/B variant không?"

acceptance_capture:                # done = all true
  - "Tất cả must_visit có 1 dump JSON + 1 PNG"
  - "Coverage check báo 0 MISS sau khi exclude blocklist + out_of_scope"
  - "Mỗi cluster in_scope có ≥ 1 transition edge"

related:
  - explore_create/observations/root
---
```

### Body structure

- `## 1. In scope` — list cluster IN, mỗi cluster `### Cluster: <name> {#<feature>/cluster/<slug>}`
  với must_visit + optional_visit
- `## 2. Out of scope` — list cluster OUT, mỗi cluster với reason
- `## 3. Unknowns` — PM questions chưa trả lời, mỗi question
  `### Q-NN: <text> {#<feature>/question/scope_q_nn}`
- `## 4. Acceptance criteria for capture phase` — bullet list
- `## 5. Sign-off log` — history của các revision

### Anchor type

- `cluster` = nhóm screens cùng functional purpose. Anchor: `<feature>/cluster/<slug>`
- Cluster KHÔNG phải block. Block (layer flow) = post-capture interpretation;
  cluster (layer scope) = pre-capture PM intent. 1 cluster có thể map sang nhiều block, hoặc ngược lại.

### Status lifecycle

```
draft  ──── PM review ────►  signed_off  ──── coverage gap or new req ────►  revising
                                  │                                              │
                                  └────────── capture phase reads ────────────────┘
```

Capture phase (Phase 2) refuses to start unless `status=signed_off` (or
`scope.md` doesn't exist for small features <5 screens — explicit auto-approve).

---

## 4. Layer 1 — `<feature>_observations.md`

### Frontmatter

```yaml
---
feature: today
layer: observations
anchor: today/observations/root
title: Today Tab — Raw Observations
last_updated: 2026-04-16
app_version: 4.3.10
device: 8A5X0M2H8
locale: vi-VN
package: com.basmo.BibleChat
screens:
  - anchor: today/screen/landing
    label: Today Landing
    activity: com.bookvitals.bibleChat.main.DashboardActivity
    hash: sha1:abcd1234...
    capture_file: spec/screens/today/screen_01_landing.png
    dump_file: spec/ui_dumps/today/screen_01_landing.json
    section_line: 12
  - anchor: today/screen/profile_drawer
    label: Profile Drawer
    activity: com.bookvitals.bibleChat.main.DashboardActivity
    hash: sha1:efgh5678...
    capture_file: spec/screens/today/screen_02_profile_drawer.png
    dump_file: spec/ui_dumps/today/screen_02_profile_drawer.json
    section_line: 113
---
```

### Body structure

- Mỗi screen = 1 `## Screen NN — <label>` section
- Phải có **bảng bounds** (5 cột: `Class | Bounds | Clickable | Text | Content-desc`)
- Phải có section `### Hành vi quan sát` + `### Observed transitions`
- Section `## Cross-screen invariants` ở cuối (optional)

### Section anchor convention

Header của mỗi screen section PHẢI có inline anchor marker để graph builder tìm được:

```markdown
## Screen 01 — Today Landing {#today/screen/landing}
```

Marker format: `{#<anchor>}` cuối header line. `build_graph.py` parse marker này để map file+line → anchor.

---

## 5. Layer 2 — `<feature>_spec.md`

### Frontmatter

```yaml
---
feature: today
layer: flow
anchor: today/flow/root
title: Today Tab — Flow Spec
last_updated: 2026-04-16
status: approved
blocks:
  - id: today/block/a
    letter: A
    name: Today Landing
    section_line: 62
    screens: [today/screen/landing]
  - id: today/block/b
    letter: B
    name: Profile Drawer
    section_line: 121
    screens: [today/screen/profile_drawer]
nav_edges:
  - from: today/screen/landing
    to: today/screen/profile_drawer
    trigger: "tap avatar"
    block: today/block/b
  - from: today/screen/landing
    to: explore/screen/overlay
    trigger: "tap sparkle icon"
    block: today/block/c
    external: true         # edge tới feature khác
states:
  - id: today/state/progress_incomplete
    section_line: 428
  - id: today/state/progress_complete
    section_line: 440
related:
  - today/observations/root
  - today/implementation/root
---
```

### Body structure

- `## 1. Tổng Quan`
- `## 2. Hard facts before anything else`
- `## 3. Block A — <name> {#today/block/a}`
- ... block B, C, D
- `## <N>. Navigation graph` — paste output Mermaid từ `render_nav.py`
- `## <N+1>. State machine` — Mermaid flowchart cho lifecycle
- `## <N+2>. Bug / quirk đã quan sát`

### Anchor rules trong body

- Block header: `## N. Block X — <name> {#<feature>/block/<letter>}`
- State section: dùng marker `{#<feature>/state/<name>}` cạnh định nghĩa state

---

## 6. Layer 3 — `<feature>_feature_spec.md`

### Frontmatter

```yaml
---
feature: today
layer: implementation
anchor: today/implementation/root
title: Today Feature Cluster Spec (Implementation-Ready)
last_updated: 2026-04-16
status: approved
app_version: 4.3.10
components:
  - id: today/component/session_reader
    name: SessionReader
    section_line: 364
    screens: [today/screen/verse_reader, today/screen/devotional_reader, today/screen/prayer_reader]
    reuse_key: session_reader          # key để match cross-feature reuse
  - id: today/component/week_strip
    name: WeekStrip
    section_line: 150
    screens: [today/screen/landing]
apis:
  - id: today/api/get_today
    method: GET
    path: /v1/today
    section_line: 650
    returns: today/data_model/today_payload
  - id: today/api/post_session_complete
    method: POST
    path: /v1/today/session/complete
    section_line: 720
data_models:
  - id: today/data_model/today_session_content
    name: TodaySessionContent
    section_line: 810
  - id: today/data_model/today_payload
    name: TodayPayload
    section_line: 820
reuses:
  - component: today/component/session_reader
    used_by: [bible/screen/reader, explore/screen/plan_day_reader]
criteria:
  - id: today/criterion/ac_01
    section_line: 878
    summary: "Landing renders in <1s on cold start"
  - id: today/criterion/ac_02
    section_line: 882
    summary: "Streak pill increments at 00:00 local"
invariants:
  - id: today/invariant/progress_persists
    section_line: 606
questions:
  - id: today/question/q_01
    section_line: 865
related:
  - today/observations/root
  - today/flow/root
---
```

### Body structure (9 section chuẩn)

1. `## 1. Metadata` — bảng metadata
2. `## 2. Tổng Quan` — goal + KPI + flow + metric
3. `## 3. Chi Tiết Từng Screen` — per-screen component + state + data dependency. Mỗi screen dùng anchor `{#<feature>/screen/<name>}`
4. `## 4. Cross-screen invariants` — mỗi invariant `### <name> {#<feature>/invariant/<name>}`
5. `## 5. API contract draft` — mỗi API `### <METHOD> <path> {#<feature>/api/<name>}` + **fenced block JSON Schema với ```json annotation**
6. `## 6. Data model summary` — mỗi model `### <ClassName> {#<feature>/data_model/<name>}` + **fenced block Kotlin ```kotlin**
7. `## 7. Open questions` — mỗi question `- Q-NN {#<feature>/question/q_nn}: <text>`
8. `## 8. Acceptance criteria` — mỗi AC `- AC-NN {#<feature>/criterion/ac_nn}: <text>`
9. `## 9. References` — link

### Code block rule (quan trọng cho Phase 6)

- **API**: dùng ` ```json` với field `$schema`, `type`, `properties` để `extract_contracts.py` parse thành OpenAPI
- **Data model**: dùng ` ```kotlin` với keyword `data class` để `extract_contracts.py` copy nguyên block sang `spec/_contracts/kotlin/`

---

## 6.5. Layer 4 — `<feature>_coverage_report.md` (Gate 2 — capture audit)

**Mục đích**: tự động diff `scope.md` vs nav_graph + dumps SAU khi capture xong.
PM review report TRƯỚC khi spec-writer chạy. File auto-generated bởi
`coverage_report.py`; PM chỉ append `decisions:` block khi review.

### Frontmatter

```yaml
---
feature: explore_create
layer: coverage_report
anchor: explore_create/coverage_report/root
title: Explore Create — Coverage Report
last_updated: 2026-05-04
generated_at: 2026-05-04T15:30:00Z
generated_by: coverage_report.py v1
scope_version: 1                 # snapshot từ scope.md tại thời điểm sinh
status: draft                    # draft | reviewed | sign_off_pass | sign_off_fail

captured:
  count: 12
  anchors:
    - explore_create/screen/wizard_intro
    - explore_create/screen/wizard_q1

gaps:                            # IN scope nhưng CHƯA capture
  - anchor: explore_create/screen/wizard_q3
    reason: "agent timed out at q2; need re-run"
  - anchor: explore_create/screen/paywall_dismiss
    reason: "modal trapped BACK, swipe-down failed"

drift:                           # CAPTURED nhưng KHÔNG declared in scope
  - capture_label: screen_05_unexpected_dialog
    hash: abc123
    cluster_guess: explore_create/cluster/wizard_quiz
    reason_guess: "modal triggered by Q4 selection"

unknowns_resolved:               # PM trả lời sau review (manual append)
  - id: explore_create/question/scope_q_01
    answer: "Có A/B; capture variant B làm baseline"

decisions:                       # PM action items sau review (manual append)
  - "Re-capture wizard_q3 với extended timeout"
  - "Add unexpected_dialog vào scope as new must_visit"
  - "Drop paywall_dismiss — modal là known limitation"

related:
  - explore_create/scope/root
  - explore_create/observations/root
---
```

### Body structure

- `## 1. Summary` — tóm tắt 3 con số: matched / gap / drift counts
- `## 2. Captured (matches scope)` — bullet list anchors + capture file path
- `## 3. Gaps` — must_visit anchors thiếu, mỗi cái có reason + suggested fix
- `## 4. Drift` — captures ngoài scope, mỗi cái có cluster_guess + reason_guess
- `## 5. PM review` — section trống cho PM fill (decisions + answers)

### Status lifecycle

```
draft  ──── PM review ────►  sign_off_pass  ──── spec-writer reads ───►
                       └──►  sign_off_fail  ──── re-capture loop  ────┘
```

`spec-writer` agent refuses to start unless `status=sign_off_pass` OR
`coverage_report.md` doesn't exist (small features auto-approve, mirror scope).

---

## 7. Cross-feature references

Khi spec reference feature khác (vd Today mention Explore overlay):

- Dùng anchor đầy đủ của feature kia: `explore/screen/overlay`
- Edge trong `nav_edges` set flag `external: true`
- Field `related` trong frontmatter list mọi file spec khác được reference

---

## 8. Edge types trong spec graph

`build_graph.py` sinh edges với các type:

| Edge type | Từ | Tới | Ghi chú |
|---|---|---|---|
| `navigates_to` | screen | screen | từ `nav_edges` trong layer flow |
| `belongs_to_block` | screen | block | từ `blocks.screens` |
| `belongs_to_cluster` | screen | cluster | từ `clusters[].must_visit` (scope) |
| `belongs_to_feature` | any | feature node | auto |
| `renders_component` | screen | component | từ `components.screens` |
| `reuses_component` | component | component | từ `reuses` |
| `triggers_api` | screen | api | optional, từ scan markdown body |
| `returns_model` | api | data_model | từ `apis.returns` |
| `verified_by` | screen | criterion | optional |
| `references` | any | any | cross-ref generic từ `related` |
| `has_state` | feature | state | từ `states` |
| `out_of_scope` | feature | cluster | cluster với `in_scope: false` (scope) |
| `gap` | scope | screen | screen must_visit chưa capture (coverage_report) |
| `drift` | coverage_report | screen | screen capture ngoài scope (coverage_report) |
| `verifies_scope` | coverage_report | scope | report verify scope version (coverage_report) |

---

## 9. Status values

| Status | Layer | Nghĩa |
|---|---|---|
| `draft` | mọi layer | đang viết, có thể thay đổi |
| `signed_off` | scope | PM duyệt, capture phase được phép start |
| `revising` | scope | PM yêu cầu update sau coverage_report fail |
| `sign_off_pass` | coverage_report | PM duyệt capture đủ, spec-writer được phép chạy |
| `sign_off_fail` | coverage_report | PM yêu cầu re-capture, blocked spec-writer |
| `approved` | implementation, overview | user/PM duyệt, dev có thể code |
| `stale` | mọi layer | spec cũ hơn capture gần nhất, cần re-verify |

---

## 10. Validation rule (enforce bởi `validate_spec.py`)

1. Frontmatter YAML parse được
2. `feature` match tên folder
3. `layer` ∈ `{scope, observations, flow, implementation, coverage_report, overview}`
4. `anchor` unique toàn repo — **trừ anchor screen cross-layer cùng feature**
   (obs + impl của cùng feature có thể khai cùng `<feature>/screen/x`,
   `build_graph.py` merge 2 khai báo thành 1 node)
5. `last_updated` ISO 8601 date
6. Mọi anchor reference (`screens[].anchor`, `nav_edges.from/to`, `related`,
   `reuses.*`, `returns`…) phải tồn tại trong graph (sau khi build)
7. Mọi header `## X {#anchor}` phải có anchor ID hợp lệ (format slash)
8. Layer implementation + overview phải có `status`
9. Không duplicate anchor trong cùng file

---

## 11. Ví dụ file skeleton

### observations skeleton

```markdown
---
feature: bible
layer: observations
anchor: bible/observations/root
title: Bible Tab — Raw Observations
last_updated: 2026-04-16
app_version: 4.3.10
device: 8A5X0M2H8
locale: vi-VN
package: com.basmo.BibleChat
screens:
  - anchor: bible/screen/reader
    label: Chapter Reader
    activity: com.bookvitals.bibleChat.main.DashboardActivity
    hash: sha1:...
    capture_file: spec/screens/bible/screen_01_reader.png
    dump_file: spec/ui_dumps/bible/screen_01_reader.json
    section_line: 12
---

# Bible — Raw Observations

## Screen 01 — Chapter Reader {#bible/screen/reader}

| Class | Bounds | Clickable | Text | Content-desc |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### Observed behaviour

...

### Transitions

...
```

### flow skeleton

```markdown
---
feature: bible
layer: flow
anchor: bible/flow/root
title: Bible Tab — Flow Spec
last_updated: 2026-04-16
status: approved
blocks:
  - id: bible/block/a
    letter: A
    name: Chapter Reader
    section_line: 30
    screens: [bible/screen/reader]
nav_edges:
  - from: bible/screen/reader
    to: bible/screen/book_picker
    trigger: "tap chapter chip"
    block: bible/block/b
related:
  - bible/observations/root
  - bible/implementation/root
---

# Bible — Flow Spec

## 1. Overview

...

## 3. Block A — Chapter Reader {#bible/block/a}

...
```

### implementation skeleton

```markdown
---
feature: bible
layer: implementation
anchor: bible/implementation/root
title: Bible Feature Cluster Spec
last_updated: 2026-04-16
status: approved
app_version: 4.3.10
components:
  - id: bible/component/chapter_reader
    name: ChapterReader
    section_line: 150
    screens: [bible/screen/reader]
    reuse_key: chapter_reader
apis:
  - id: bible/api/get_chapter
    method: GET
    path: /v1/bible/{translation}/{book}/{chapter}
    section_line: 400
    returns: bible/data_model/chapter
data_models:
  - id: bible/data_model/chapter
    name: Chapter
    section_line: 500
reuses:
  - component: today/component/session_reader
    used_by: [bible/screen/reader]
criteria:
  - id: bible/criterion/ac_01
    section_line: 600
    summary: "Chapter loads offline if cached"
related:
  - bible/observations/root
  - bible/flow/root
---

# Bible — Feature Spec

...
```

---

## 12. Migration path

Xem `spec/tools/migrate_frontmatter.py` — chạy auto-infer frontmatter từ
content cũ, Claude review sửa tay phần infer sai (screen anchor names,
reuse_key matching…).

---

## 13. Version history

| Version | Date | Change |
|---|---|---|
| 1 | 2026-04-20 | Initial schema — 3 layer frontmatter + slash anchors + 10 edge types |
