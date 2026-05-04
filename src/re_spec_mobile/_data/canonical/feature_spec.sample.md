---
feature: today
layer: implementation
anchor: today/implementation/root
title: BibleChat — Today Feature Cluster Spec (Implementation-Ready)
last_updated: '2026-04-20'
locale: vi-VN
status: approved
screens:
- anchor: today/screen/today_landing
  letter: A
  name: Today Landing
  section_line: 101
- anchor: today/screen/profile_drawer
  letter: B
  name: Profile Drawer
  section_line: 213
- anchor: today/screen/explore_overlay
  letter: C
  name: Explore Overlay
  section_line: 245
- anchor: today/screen/calendar
  letter: D
  name: Calendar
  section_line: 278
- anchor: today/screen/subtitle_info_tooltip
  letter: E
  name: Subtitle / Info Tooltip
  section_line: 313
- anchor: today/screen/today_empty_states
  letter: F
  name: Day-State Empty Screens
  section_line: 339
- anchor: today/screen/change_reminder_bottom_sheet_time_picker
  letter: G
  name: Reminder Editor
  section_line: 366
- anchor: today/screen/today_tab_paywall
  letter: H
  name: Today-tab Paywall
  section_line: 409
- anchor: today/screen/verse_session_reader
  letter: I
  name: Session Reader
  section_line: 454
- anchor: today/screen/day_complete_celebration
  letter: J
  name: Day-Complete Celebration
  section_line: 512
- anchor: today/screen/peace_and_calm_bottom_sheet
  letter: K
  name: Peace and Calm Bottom Sheet
  section_line: 541
- anchor: today/screen/available_points
  letter: L
  name: Available Points
  section_line: 567
components:
- id: today/component/session_reader
  name: SessionReader
  section_line: 480
  screens:
  - today/screen/verse_session_reader
  - today/screen/devotional_reader
  - today/screen/prayer_reader
  reuse_key: session_reader
- id: today/component/week_strip
  name: WeekStrip
  section_line: 168
- id: today/component/exclusive_deal_banner
  name: ExclusiveDealBanner
  section_line: 220
- id: today/component/light_points_badge
  name: LightPointsBadge
  section_line: 175
- id: today/component/day_cell
  name: DayCell
  section_line: 195
apis:
- id: today/api/get_journey
  method: GET
  path: /v1/journey/{date}
  section_line: 657
  returns: today/data_model/today_payload
- id: today/api/post_session_complete
  method: POST
  path: /v1/journey/{date}/cards/{cardId}/complete
  section_line: 712
  returns: today/data_model/session_complete_response
- id: today/api/get_promo
  method: GET
  path: /v1/promo/active
  section_line: 728
  returns: today/data_model/promo_payload
- id: today/api/get_user
  method: GET
  path: /v1/user
  section_line: 743
  returns: today/data_model/user_payload
- id: today/api/put_reminder
  method: PUT
  path: /v1/user/reminder
  section_line: 758
  returns: today/data_model/reminder_payload
- id: today/api/get_store_lp
  method: GET
  path: /v1/store/light-points
  section_line: 768
  returns: today/data_model/store_payload
data_models:
- id: today/data_model/today_payload
  name: TodayPayload
  section_line: 657
- id: today/data_model/today_session_content
  name: SessionContent
  section_line: 482
- id: today/data_model/today_state
  name: TodayState
  section_line: 805
- id: today/data_model/daily_reminder
  name: DailyReminder
  section_line: 396
- id: today/data_model/wallet
  name: Wallet
  section_line: 595
reuses:
- component: today/component/session_reader
  used_by:
  - today/screen/verse_session_reader
  - today/screen/devotional_reader
  - today/screen/prayer_reader
criteria:
- id: today/criterion/ac_01
  section_line: 882
  summary: Cold launch lands on Today tab
- id: today/criterion/ac_02
  section_line: 884
  summary: Header sticky behaviour
- id: today/criterion/ac_03
  section_line: 886
  summary: Week strip renders 7 days of current week
- id: today/criterion/ac_04
  section_line: 887
  summary: Tap past day with content opens reader
- id: today/criterion/ac_05
  section_line: 888
  summary: Calendar opens via streak pill
- id: today/criterion/ac_06
  section_line: 889
  summary: Subtitle and i icon open same tooltip
- id: today/criterion/ac_07
  section_line: 890
  summary: Light Points badge displays balance
- id: today/criterion/ac_08
  section_line: 891
  summary: Single-expansion invariant
- id: today/criterion/ac_09
  section_line: 892
  summary: Reading session marks complete
- id: today/criterion/ac_10
  section_line: 893
  summary: Completing last session triggers Day-Complete
- id: today/criterion/ac_11
  section_line: 894
  summary: F1 empty state interpolation
- id: today/criterion/ac_12
  section_line: 895
  summary: Change reminder opens sheet + picker
- id: today/criterion/ac_13
  section_line: 896
  summary: Exclusive Deal countdown live + opens paywall
- id: today/criterion/ac_14
  section_line: 897
  summary: Profile Drawer pre-fills from server
- id: today/criterion/ac_15
  section_line: 898
  summary: Tooltip Popup focusable false
- id: today/criterion/ac_16
  section_line: 899
  summary: Currency consistent thousands separator
- id: today/criterion/ac_17
  section_line: 900
  summary: Bottom nav visibility rules
invariants:
- id: today/invariant/session_reader_reuse
  section_line: 619
- id: today/invariant/single_expansion
  section_line: 624
- id: today/invariant/progress_denominator
  section_line: 628
- id: today/invariant/sticky_header
  section_line: 633
- id: today/invariant/lp_vs_chat_questions
  section_line: 637
- id: today/invariant/bottom_nav_visibility
  section_line: 644
- id: today/invariant/date_state_machine
  section_line: 651
questions:
- id: today/question/q_01
  section_line: 870
- id: today/question/q_02
  section_line: 871
- id: today/question/q_03
  section_line: 872
- id: today/question/q_04
  section_line: 873
- id: today/question/q_05
  section_line: 874
- id: today/question/q_06
  section_line: 875
- id: today/question/q_07
  section_line: 876
- id: today/question/q_08
  section_line: 877
related:
- today/observations/root
- today/flow/root
---

# BibleChat — Today Feature Cluster Spec (Implementation-Ready)

> **⚠️ CANONICAL — REFERENCE STRUCTURE.**
> Mọi spec MỚI viết bằng tiếng Việt với technical term tiếng Anh — xem
> `docs/I18N_GLOSSARY.md`. Mimic frontmatter shape (screens, components, apis,
> data_models, reuses, criteria, invariants, questions, related) + 9 section
> body chuẩn (Metadata / Tổng Quan / Chi Tiết Từng Screen / Cross-screen
> invariants / API contract / Data model / Open questions / Acceptance criteria
> / References).
>
> Mọi thông tin trích từ reverse-engineering app thật (`com.basmo.BibleChat`
> v4.3.10) trên device `8A5X0M2H8` (Pixel, Android, locale `vi-VN`).
> Engineer đọc file này phải có đủ thông tin để rebuild toàn bộ Today feature mà
> KHÔNG cần chạy app gốc.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| **App Name** | BibleChat |
| **Package** | `com.basmo.BibleChat` |
| **Feature Cluster** | Today (Daily Journey home tab) |
| **Bottom-nav resource-id** | `navigation_daily_journey` |
| **Platform** | Android (Kotlin + Jetpack Compose embedded inside Fragment) |
| **Min SDK** | 26 (Android 8.0) |
| **Target SDK** | 34 |
| **App version captured** | 4.3.10 |
| **Author** | Auto-generated từ reverse spec |
| **Last Updated** | 2026-04-16 |
| **Status** | Approved — Ready for Development |
| **Related specs** | `onboarding_feature_spec.md`, `chat_feature_spec.md`, `community_feature_spec.md`, `today_observations.md`, `today_spec.md` |

---

## 2. Tổng Quan Today Feature

### 2.1. Mục Tiêu

| Mục tiêu | Mô tả | KPI |
|-----------|--------|-----|
| **Daily activation** | User mở app mỗi ngày và hoàn thành ít nhất 1 session | DAU/MAU ≥ 35% |
| **Streak retention** | User duy trì streak 3-day (mở khoá `33 free questions`) rồi 7-day | D7 streak ≥ 25% of installers |
| **Content engagement** | User mở cả 3 sessions (Verse / Devotional / Prayer) trong ngày → progress = 100% | Day-complete rate ≥ 50% of DAU |
| **Cross-cluster funnel** | "Chat to learn more" pre-loads context và đẩy user vào Chat cluster | Chat-from-reader rate ≥ 20% of session opens |
| **Monetization** | Paywall (Exclusive Deal) + Light Points store quy đổi USD/VND | Trial start rate (paywall) ≥ 5% of taps; Light Points ARPU theo dõi riêng |
| **Personalisation transparency** | Tooltip "Tailored just for you" giải thích nguồn dữ liệu plan → giảm churn nghi ngờ AI | Settings Privacy taps stay flat after release |

### 2.2. Flow Tổng Quan

```
APP START
  │
  ▼
DashboardActivity (tab mặc định = navigation_daily_journey)
  │
  ▼
  ┌────────────────────────────────────────────────────────────────┐
  │  TODAY LANDING (Block A)                                        │
  │  ┌──────────── Sticky header ────────────┐                       │
  │  │ Avatar · Title · Sparkle · Streak pill │                       │
  │  │ Subtitle theme · Info i · Light Points │                       │
  │  │ Week strip (M T W T F S S, 7 cell)     │                       │
  │  │ Progress today / N%                    │                       │
  │  └────────────────────────────────────────┘                       │
  │  Card (scrollable, 5 cố định):                                    │
  │    1. Exclusive Deal banner (countdown)                           │
  │    2. YOUR VERSE (1 MIN)        ──┐                               │
  │    3. PERSONALIZED DEVOTIONAL (3 MIN) ├─ session card             │
  │    4. PRAYER OF THE DAY (2 MIN) ──┘                               │
  │    5. PEACE AND CALM (one-shot bottom sheet)                      │
  └────────────────────────────────────────────────────────────────────┘
   │
   ├── Avatar          → Profile Drawer (Block B)
   ├── Sparkle         → Explore overlay (Block C, directory cross-cluster)
   ├── Streak pill     → Calendar full-month (Block D)
   │                       └── day có content → Verse Reader (Block I read-only)
   ├── Subtitle / i    → Tooltip overlay (Block E)
   ├── Light Points    → Available Points / Light Points store (Block L)
   ├── Week-strip day  → switch day display (re-render Block A hoặc empty state F)
   ├── Empty state ──── Change reminder → Reminder sheet (Block G) → Material time picker
   ├── Exclusive Deal  → Paywall (Block H)
   ├── Verse Listen / Read / Chat   → Reader (Block I) → Chat cluster
   ├── Devotional Listen / Read / Chat
   ├── Prayer Listen / Read / Chat → on Done → Day-Complete (Block J)
   └── Peace and Calm  → Bottom sheet input (Block K)
```

### 2.3. Tóm Tắt Số Liệu

| Metric | Giá trị |
|--------|---------|
| Tổng UI states | **17** (1 landing + 4 day-state variants + 12 derivative screens) |
| Cards trên landing | **5** (1 marketing + 3 sessions counted toward progress + 1 side-channel exercise) |
| Sessions counted toward 100% | **3** (Verse, Devotional, Prayer) — 33.33% mỗi cái |
| Flow type | **Free Navigation** (không forced) |
| Back navigation | Cho phép tự do, dùng `KEYCODE_BACK` hoặc `X` close |
| Sticky header height | từ y=93 đến y=778 (~32% viewport) |
| Bottom-nav | luôn visible trừ khi drawer mở hoặc full-screen overlay |
| Paywall pricing | VND (₫), 2 plan: 7-day trial then `₫105,000/wk`, hoặc `₫880,000/yr` |
| Light Points tiers | 5 (100 → 10.000 points, ₫30k → ₫1.3M) |

---

## 3. Chi Tiết Từng Screen

---

### SCREEN A — Today Landing

#### Thông Tin Chung

| Field | Value |
|-------|-------|
| **Tên** | Today landing |
| **Đường dẫn** | Bottom-nav `Today` |
| **Activity** | `DashboardActivity` |
| **Fragment** | render bên trong `navHostFragmentContainerViewDashboard` |
| **Tech** | Compose (node semantic-only, không có resource-id) |
| **Backgrounds** | Header có gradient olive-mustard; vùng card là dark surface với background card image-aware (ocean cho Verse, hands cho Devotional/Prayer, leaf cho Peace) |

#### Layout structure

```
┌────────────────────────────────────────────┐  y=0
│ status bar (system)                         │  y=93
├────────────────────────────────────────────┤
│ HEADER                                      │
│  ┌─────┐  Today's Journey   ✨   🔥0       │  y=93..225
│  │  F  │                                    │
│  │     │  Starting Your Journey  ⓘ   ⊙30  │  y=218..350
│  └─────┘                                   │
│  ┌──┬──┬──┬──┬──┬──┬──┐                   │  y=393..545
│  │M │T │W │T │F │S │S │  weekday letters   │
│  │13│14│15│16│17│18│19│  numbers           │
│  └──┴──┴──┴──┴──┴──┴──┘                   │
│  Progress today                       75%  │  y=623..707
│  ████████████████░░░░░                     │  y=...
├────────────────────────────────────────────┤  y≈770 (top vùng cards)
│ CARDS (vertical scroll)                     │
│  ┌──────────────────────────────────────┐  │
│  │ 🎁 Exclusive Deal      23:58:20       │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ ✓ YOUR VERSE · 1 MIN          DONE   │  │
│  │   Isaiah 41:10                        │  │
│  │   [STRENGTH][COURAGE][SUPPORT]        │  │
│  │   [🎧 Listen]      [📖 Read]          │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ ✓ PERSONALIZED DEVOTIONAL · 3 MIN DONE│  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │   PRAYER OF THE DAY · 2 MIN     ⌄    │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ 🍃 PEACE AND CALM                     │  │
│  │   When life's too loud, listen within │  │
│  └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤  y=1808
│ BOTTOM NAV (Chat | Community |Today| Bible | Explore) │
└────────────────────────────────────────────┘  y=2028
```

#### Components & States

| Component | States | Behaviour |
|---|---|---|
| Header avatar | Static letter (ký tự đầu của nickname). Long-press: chưa test. | Tap → Profile Drawer (Screen B) |
| Title | `Today's Journey` nếu day đã chọn = today của system; ngược lại `MMM DD's Journey` (vd `Apr 15's Journey`) | Read-only |
| Sparkle icon | Luôn visible | Tap → Explore overlay (Screen C) |
| Streak pill | Hiện fire 🔥 + integer `currentStreak` | Tap → Calendar (Screen D) |
| Subtitle | String theme per-day (server cấp) | Tap → Tooltip (Screen E) |
| Icon Info `ⓘ` | Luôn visible | Tap → cùng Tooltip |
| Light Points badge | Circle vàng + integer `lightPointsBalance` | Tap → Available Points (Screen L) |
| Week-strip day cell | Mỗi cell: chữ weekday + số day-of-month; ring/fill visual encode status (today=filled, has-content=ring, dimmed=non-interactive) | Tap behaviour theo status (xem bảng dưới) |
| Progress bar | Linear progress, value `dayProgressPercent` (0..100), label `Progress today` (hoặc `Progress for MMM DD`), value render `N%` không có decimal | Read-only |
| Card: Exclusive Deal | 1 visual: gift icon + label + countdown timer (mm:ss không dùng; format `HH:mm:ss` server cấp hoặc compute từ `dealEndsAt - now`) | Tap → Paywall (Screen H) |
| Card: session (Verse/Devotional/Prayer) | 2 state: collapsed (header strip với chip `DONE` khi complete, chevron `⌄` khi chưa) và expanded (title + tag pill + Listen + Read) | Tap header → toggle expand (invariant single-expansion). Tap Listen / Read trong → Reader (Screen I) |
| Card: Peace and Calm | Card one-shot — không có expand state | Tap → Bottom sheet (Screen K) |

#### Quy tắc tap day-cell Week-strip

| Status cell | Visual | Behaviour tap |
|---|---|---|
| Today (system date) | Circle fill, số trắng | Switch sang content today (hoặc empty state F.1 nếu lock) |
| Quá khứ **có session hoàn thành** | Ring quanh số | Switch sang content reader của day đó (mode re-read) |
| Quá khứ **chưa start** | Xám dim, không ring | No-op (silent) |
| Tương lai | Outline, text bình thường | Switch sang empty state F.2 (`Check back tomorrow`) |
| Đang selected | Ring/fill vàng | (re-tap = no-op) |

#### Data dependencies

| Field | Source | Refresh trigger |
|---|---|---|
| `nickname` | `User.nickname` | Khi edit profile |
| `currentStreak` | `User.streak.current` | Sau Day-Complete |
| `longestStreak` | `User.streak.longest` | Sau Day-Complete |
| `lightPointsBalance` | `User.wallet.lightPoints` | Sau session complete, sau store purchase, sau Day-Complete |
| `selectedDate` | local UI state (mặc định = today system) | Khi tap day-strip / calendar |
| `weekDays[]` | compute từ `selectedDate` (Mon..Sun của tuần đó) | Khi selectedDate vượt biên tuần |
| `dayPlan(selectedDate)` | `GET /journey/{date}` | Khi selectedDate đổi |
| `dayPlan.theme` | server | per `dayPlan` |
| `dayPlan.progressPercent` | server (thường 0/33/67/100) | per event session-complete |
| `dayPlan.cards[]` | server | per `dayPlan` |
| `exclusiveDeal` | `GET /promo/active` | App launch + khi Today open; countdown render local từ `endsAt` |

#### Empty states

| Khi nào | Render |
|---|---|
| `selectedDate == today AND !todayUnlocked` | Screen F.1 |
| `selectedDate > today` | Screen F.2 |
| `selectedDate < today AND !pastStarted` | (cell không tappable; state đáng ra unreachable) |

---

### SCREEN B — Profile Drawer

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap avatar trên header (118, 213) |
| **Container** | `DrawerLayout` (Material) slide từ trái |
| **Width** | ~92% viewport (`[0,0][990,2028]`); phải `[990,1080]` là scrim với `desc=Close navigation menu` |
| **Dismiss** | `KEYCODE_BACK` hoặc tap scrim |
| **Tech** | đa số Compose trong drawer |

#### Sections (list dọc, single column scrollable)

| Section header | Items | Notes |
|---|---|---|
| (không — block header) | Avatar, EditText nickname, Current Streak, Longest Streak | EditText `clickable=true` và editable inline |
| `Friends` | Row Friends (`You have 0 friends`) | Ngoài scope ở đây — có khả năng mở list Friends |
| `Limited Special Offer` | Row `Exclusive Deal` (timer mirror Today landing) | Cùng destination với banner trên Today landing (Screen H) |
| `My Space` | `Explore all features`, `Limit screen time`, `Personalize your conversations`, `Widget selection`, `Daily Bible Verse Wallpaper` (Material switch, OFF mặc định) | Mỗi row navigate sang screen settings riêng — ngoài scope cho Today |
| `Personal Details` | `Age range` (`55+`), `Email`, `Denomination` (`Pentecostal`), `Church` | Tất cả editable; pre-fill từ onboarding quiz |
| `Subscription` | `Membership` (`Free`), `Upgrade to Premium`, `Restore purchases` | Upgrade có khả năng re-open paywall |
| `About` | `Contact us`, `Terms of use`, `Privacy policy` | Link standard legal/support |
| `Account` | `Link account data` (Google), `Manage your reminders`, `Change language` (`English`) | Reminders → reuse Screen G |
| Footer | `App version: 4.3.10`, `UID:` (rỗng cho guest) | Static |

#### Note implementation

Profile Drawer **shared qua tab** (luôn mở từ avatar header bất kỳ). Implement
1 lần như fragment singleton host bởi `DashboardActivity` và inflate vào
`DrawerLayout`.

---

### SCREEN C — Explore Overlay (sparkle icon)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap sparkle icon trên Today header (752, 159) |
| **Container** | Compose overlay full-screen (không thấy tab dưới) |
| **Dismiss** | `KEYCODE_BACK` |

#### Layout

- H1: `Explore`
- Sub-line: `Discover everything BibleChat has to offer`
- Filter chip (ngang, single-select): `Personalize` (selected mặc định) ·
  `Bible Study` · `Community` · `Journey`
- Body: grid 2-cột group theo section (PERSONALIZE, BIBLE STUDY, COMMUNITY,
  JOURNEY, LEISURE)

#### Sections & items

| Section | Items (label + glyph) |
|---|---|
| `PERSONALIZE` | Lockscreen, App Widget, Affirmations |
| `BIBLE STUDY` | Study Plans, Chat, Voice Chat, Reading, Bible Stories, Animations, Kids' Stories |
| `COMMUNITY` | Groups, Friends, Live Prayer, My Prayers, World Events |
| `JOURNEY` | Daily Plan, Calendar, The Bible, Screen Time, Meditation |
| `LEISURE` | Word Guesser, Bible Trivia |

#### Note implementation

Đây là 1 **directory feature global** alias các destination cũng reach được
qua bottom-nav (Chat, Community, Bible, Explore tab) và Profile Drawer. Treat
như 1 cluster tách và link đến spec cluster tương ứng khi implement mỗi item.

---

### SCREEN D — Calendar (full-month grid)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap streak/calendar pill trên Today header (921, 159) |
| **Container** | Overlay full-screen |
| **Dismiss** | `X` close (top-right) hoặc `KEYCODE_BACK` |
| **Tech** | Compose, custom month grid |

#### Layout

- Title: tên tháng + năm (vd `April 2026`)
- Close `X`: top-right
- Day-of-week header row: `MON TUE WED THU FRI SAT SUN`
- Body: month grid (5–6 row × 7 cell), mỗi cell `132×118 px` (`@440 dpi`)
- Multi-month render inline — label tháng hiện tại `April` (vàng), rồi grid
  full; dưới, label `May` + grid (không có chevron pagination)

#### Visual state cell

| State | Visual |
|---|---|
| Mặc định (day bất kỳ trong tháng) | Circle outline kèm số day |
| Quá khứ có session hoàn thành | Ring vàng (proportional với `dayProgressPercent`) |
| Today | Circle fill dark, số trắng (hơi to / bold hơn) |
| Tương lai | Giống mặc định outline |
| Quá khứ chưa start | Outline mờ hơn (opacity thấp) |

#### Quy tắc tap

Giống quy tắc week-strip Today landing — quá khứ chưa start = no-op silent;
day có content navigate sang session reader của day đó (mode re-read).

---

### SCREEN E — Subtitle / Info Tooltip

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap text subtitle (441, 284) HOẶC icon info `i` (733, 284) |
| **Container** | Overlay Compose `Popup` (**không** xuất hiện trong `uiautomator dump`) |
| **Dismiss** | Button `X` trên tooltip HOẶC tap ngoài |

#### Content

| Element | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close | `X` (top-right tooltip) |

#### Note implementation

Render như `Popup` anchor trên progress bar. Backdrop dim ~20%. Auto-dismiss
khi tap ngoài.

**Caveat testing**: text node của overlay này vắng mặt khỏi dump uiautomator.
Test Espresso/UIAutomator phải match bằng **resource ID assign cho container
popup** (nếu có) hoặc dùng **node accessibility TalkBack**, không phải text
matcher.

---

### SCREEN F — Empty Screen Day-State

#### F.1 — Today lock sau reminder

| Field | Value |
|---|---|
| **Entry** | `selectedDate == today AND !todayUnlocked` |
| **Headline** | `Not quite time yet.\nCheck back <Weekday>, <DD MMMM> for your Daily Plan session` (interpolate với `selectedDate`) |
| **Sub** | `Your reminder is set for <HH:mm>.\n Would you like to update it?` (interpolate với `User.reminder.time`) |
| **CTA** | `Change reminder` (link text vàng) → mở Screen G |
| **Progress bar** | render `0%` |

#### F.2 — Day tương lai

| Field | Value |
|---|---|
| **Entry** | `selectedDate > today` |
| **Headline** | `Not quite time yet.\nCheck back tomorrow for your Daily Plan session` |
| **Sub** | (không có) |
| **CTA** | (không có) |

#### F.3 — Quá khứ chưa start (lý thuyết)

Day không selectable từ strip/calendar, nên state này unreachable thực tế.
Không có gì để render.

---

### SCREEN G — Reminder Editor

#### G.1 — Reminder Bottom Sheet

| Field | Value |
|---|---|
| **Entry** | Tap link `Change reminder` trong F.1 HOẶC tap `Manage your reminders` trong Profile Drawer |
| **Container** | Material `BottomSheetDialog` (modal) |
| **Dismiss** | `X` close, swipe down trên drag handle, `KEYCODE_BACK`, tap scrim |

| Element | Text / spec |
|---|---|
| Hit-zone drag-handle | `[44,110][1036,242]` |
| Close `X` | `[915,110][1047,242]` |
| Bell illustration | bell vàng, centred top |
| Title | `Connect with God Daily` |
| Body | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Label time-chip | `We'll remind you at...` |
| Time chip | hiện time hiện tại `HH:mm` (mặc định `09:00`); chevron phải; tap → G.2 |
| Label days | `On these days` |
| Day toggles | 7 cell `M T W T F S S`; mỗi cái = `View` chứa chữ + circle checkable. Mặc định = cả 7 enable. |
| CTA | `Update reminder` (vàng, full-width) — persist state và dismiss sheet |

#### G.2 — Material 3 Time Picker

`TimePicker` Material 3 chuẩn (mode 24h). Hour input active mặc định. Bottom
dialog vẫn show day toggles + CTA `Update reminder` — tức picker là **inline**
trên bottom sheet, không phải dialog tách che toàn screen.

`KEYCODE_BACK` đóng picker (về G.1); back lần 2 đóng G.1.

#### Data model

```kotlin
data class DailyReminder(
    val time: LocalTime,        // mặc định 09:00
    val days: Set<DayOfWeek>,   // mặc định cả 7
    val enabled: Boolean,       // implicit true; toggle off = ?
)
```

Persistence: `SharedPreferences` cho client-side scheduling
(`AlarmManager.setExactAndAllowWhileIdle`) + sync sang backend
`PUT /user/reminder`.

---

### SCREEN H — Today-tab Paywall (Exclusive Deal)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap banner `Exclusive Deal` (Today landing HOẶC Profile drawer) |
| **Container** | Activity/fragment full-screen với backdrop tối và illustration chim bồ câu góc phải trên |
| **Dismiss** | `X` (top-left) hoặc `KEYCODE_BACK` |

#### Components

| Element | Spec |
|---|---|
| Headline | `Never Miss a Moment of Faith` |
| Bullet 1 | `Widget with Personalized Daily Verses` |
| Bullet 2 | `Bring the Bible to your Home Screen` |
| Bullet 3 | `Personalized Audio Daily Devotionals` |
| Toggle | label `I want to try the app for free`, Material switch, mặc định ON |
| Plan A card (selected khi toggle ON) | `7 Days Free Trial` · badge `SAVE 36%` · `Then ₫158,549.98 → ₫105,000 per week. No payment now` |
| Plan B label | `Best Price of the Year` |
| Plan B card | `12-Month Access` · `Billed yearly at ₫880,000` |
| Disclaimer | `Cancel anytime before <today + 7 days>.\nNo risks, no charges.` |
| CTA | `Try for Free →` (pill vàng, full-width) |
| Footer | `Terms of use` · `Privacy policy` · `Restore` |

#### Behaviour

- Toggle ON → Plan A pre-selected. Toggle OFF → Plan B pre-selected (giả định,
  chưa verify).
- CTA trigger flow Google Play Billing với SKU tương ứng plan đã chọn.
- Timer countdown là **global** (1 `dealEndsAt` per user); chạy bất kể user ở
  screen nào.

#### Pricing data

| Plan | Display | SKU pattern (giả định) |
|---|---|---|
| 7-day trial → weekly | `₫105,000/week` (sau strikethrough `₫158,549.98`) | `weekly_premium_intro` |
| 12-month annual | `₫880,000/year` | `yearly_premium` |

#### Bug QA biết

Giá strikethrough render thành `158549.98` (không có thousand separator),
trong khi line promo dùng `₫105,000` (format đúng). Dùng cùng `NumberFormat`
cho cả 2.

---

### SCREEN I — Session Reader (Verse / Devotional / Prayer)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap `Listen` hoặc `Read` trên 1 session card; HOẶC tap day đã hoàn thành trong Calendar/week-strip |
| **Container** | Full-screen, image background bind theme session |
| **Dismiss** | `X` (top-right) đóng thẳng, về Today landing cùng `selectedDate`. Back arrow (top-left) xuất hiện khi entry qua Chat sub-screen |

#### Shell chung

| Region | Element | Spec |
|---|---|---|
| Top | Back arrow (trái, khi applicable) · title `Your Journey` (centre) · `X` close (phải) | static |
| Dưới top | `Progress for <MMM DD>` + `<N>%` (vàng) | reflect `dayProgressPercent` hiện tại |
| Body header | Label card type small caps + duration (vd `YOUR VERSE · 1 MIN`) | static per session type |
| Body | Text long-form (verse / devotional / prayer); scroll dọc khi overflow | server cấp |
| Body footer | Citation màu vàng (vd `Isaiah 41:10`) — có trên Verse và Devotional, vắng trên Prayer | optional |
| Bottom action bar | trái: thumbs-down · giữa: `Chat to learn more` · phải: arrow `→` (intermediate) HOẶC pill `Done` (last incomplete) | dynamic |

#### Read vs Listen

`Read` — bottom action bar như trên (text-only).
`Listen` — bottom action bar thay bằng audio toolbar:

| Slot | Element |
|---|---|
| Top | linear audio progress bar |
| Trái | time hiện tại (`MM:SS`) |
| Phải | track length (`MM:SS`) |
| Buttons | Share · Previous · Play/Pause · Next · Replay |

Tap `Listen` auto-play. Tap `Read` mở view text static; user switch sang audio
được qua icon riêng (chưa verify).

#### "Chat to learn more" → Chat cluster

Navigate sang `Chat` (đã spec trong `chat_feature_spec.md`) với text session
**pre-load như 1 bubble context**. Bubble expose thumbs-up / thumbs-down /
`Copy` / `Share`. Composer ở dưới.

#### Data model

```kotlin
data class SessionContent(
    val type: SessionType,          // VERSE | DEVOTIONAL | PRAYER
    val durationMinutes: Int,       // 1 | 3 | 2
    val title: String,              // vd "Strengthened by His Righteous Hand"
    val tags: List<String>,         // vd ["FAITH", "OVERCOMING CHALLENGES"]
    val body: String,               // multi-paragraph
    val citation: String?,          // vd "Isaiah 41:10" — null cho Prayer
    val audioUrl: String?,          // null khi audio không available
    val backgroundImageUrl: String, // image theme
)
```

Session-completion register khi reader **mở** (Read hoặc Listen). Track
per-session completion server-side; recompute `dayProgressPercent` và
broadcast về Today landing.

---

### SCREEN J — Day-Complete Celebration

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Hoàn thành session incomplete cuối day (thường tap `Done` trên reader thứ 3) |
| **Container** | Overlay full-screen |
| **Dismiss** | Tap `Continue` (về Today landing cùng day) |
| **Reuse** | Cùng screen với Block N của onboarding |

#### Layout

| Element | Text / spec |
|---|---|
| Fire illustration | flame gradient vàng, centred top |
| Counter | `<currentStreak>` (numeral vàng cỡ lớn) |
| Label | `day streak` (vàng) |
| Streak progress 3-dot | dot 1..3 — fill / outline dựa trên `currentStreak / 3` (cap 3) |
| Sub | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` (static — nhưng bonus chỉ deliver khi đạt 3-day streak) |
| Mini week strip | 7 day cell `Mo Tu We Th Fr Sa Su` với số tuần hiện tại; cell today hiện icon fire |
| CTA | `Continue` (pill vàng) |

#### Bonus delivery

Khi `currentStreak` đạt `3`, append `33` vào `chatQuestionsAvailable` và
surface 1 toast/celebration variant "+33 free questions unlocked" (chưa quan
sát — để cho capture sau).

---

### SCREEN K — Peace and Calm Bottom Sheet

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap card `PEACE AND CALM` |
| **Container** | Bottom sheet full-screen với backdrop tối |
| **Dismiss** | Hit-zone top `desc=Close sheet` hoặc `KEYCODE_BACK` |

#### Layout

| Element | Text |
|---|---|
| Top hit-zone close | `[0,0][1080,122]` |
| Headline | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Privacy note | `Your privacy is guaranteed and your information will remain confidential.` |
| EditText | placeholder `Describe here`, multi-line |
| CTA `Continue` | xám/disabled đến khi `EditText` có content |

#### Behaviour (predicted, chưa verify)

Submit `Continue` có khả năng mở 1 screen "Moment of Grace" với
prayer/affirmation AI generate tailor input user. Card này **không** count
toward day-progress 100% (3 session Verse + Devotional + Prayer là đủ).

---

### SCREEN L — Available Points (Light Points store)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap Light Points badge trên Today header (950, 284) |
| **Container** | Full-screen, scrollable |
| **Dismiss** | `X` (top-left) hoặc `KEYCODE_BACK` |

#### Header

`Available Points : ⊙ <lightPointsBalance>` (glyph circle vàng + số)

#### Sections

| Section | Items |
|---|---|
| `Premium` | `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `5 Questions` · `⊙ 250` ; `25 Questions` · `⊙ 1000` ; `100 Questions` · `⊙ 2500` |
| `Light Points` (tier purchase, paid bằng VND) | `100 LP` · `₫30,000` · `500 LP` · `₫108,000` · `1.000 LP` · `₫198,000` · `2.500 LP` · `₫391,000` · `10.000 LP` · `₫1,300,000` |
| `Study Unlocks` | 20 study pack, mỗi cái `⊙ 250` (full list trong `today_observations.md` §15) |
| `Coming Soon` | `Special Study` (placeholder, không purchase được) |

#### Currency model

```kotlin
data class Wallet(
    val lightPoints: Int,       // earn + purchase
    val chatQuestionsLeft: Int, // counter tách, surface là badge ?N trong Chat header
)

enum class LpEarnSource { SESSION_COMPLETE, DAY_STREAK, PURCHASE, PROMOTIONAL }
```

#### Bug QA biết

Tier purchase Light Points dùng dot-as-thousand-separator (`1.000`, `2.500`,
`10.000`) trong khi giá VND dùng dấu phẩy (`30,000`, `1,300,000`). Cùng screen
— pick one.

---

## 4. Cross-screen invariants

### 4.1 Chrome session reader

Cả 3 reader (Verse / Devotional / Prayer) chia chung cùng shell chính xác —
implement 1 lần, parameterise theo `SessionContent`.

### 4.2 Invariant single-expansion

Chỉ 1 session card trên Today landing được expand mỗi lúc. Tap card collapsed
sẽ auto-collapse sibling đang expand.

### 4.3 Denominator progress

`dayProgressPercent` compute trên **3 session** (Verse + Devotional + Prayer).
Peace and Calm **không** count. Nhảy expected: `0% → 33% → 67% → 100%` (quan
sát: `75% → 100%` sau Prayer trong session này — tức percent display **rounded**
với `Verse + Devotional` đã count là `2/3 = 66.67% → round thành 75%`, suggest
custom rounding hoặc weighting khác; verify với engineer).

### 4.4 Sticky header

Header từ y=93 đến y=778 sticky. Cards scroll trong `[0, ~770][1080, 1808]`.

### 4.5 Light Points vs Chat Questions

Đây là **2 counter tách biệt**:
- **Light Points** (badge `⊙` trong Today header) → spent vào premium,
  wallpaper, Q-credit, study.
- **Chat Questions** (badge `?N` trong Chat header) → consume per AI question;
  replenish qua purchase Light Points, reward streak, premium subscription.

### 4.6 Visibility bottom-nav

Bottom nav giữ visible trên:
- Today landing (mọi variant)
- Profile drawer? — **Không**, drawer overlay nav
- Calendar, Paywall, Available Points, Session Reader, Day-Complete —
  **Không**, các cái này là overlay full-screen

### 4.7 State machine date

```
[ today date roll over lúc midnight ] ─▶ [ selectedDate auto-set sang today mới ]
[ user tap day quá khứ có content    ] ─▶ [ render reader cho day đó, KHÔNG đổi selectedDate ]
[ user tap day trong week strip      ] ─▶ [ nếu has content/today/future: switch selectedDate ]
                                          [ nếu past unstarted: no-op ]
```

---

## 5. API contract draft

### 5.1 `GET /journey/{date}`

```jsonc
// Request: GET /v1/journey/2026-04-15
// Response 200
{
  "date": "2026-04-15",
  "theme": "Starting Your Journey",
  "progressPercent": 100,
  "completedAt": "2026-04-16T05:32:14Z",
  "cards": [
    {
      "id": "verse_2026-04-15",
      "type": "VERSE",
      "durationMinutes": 1,
      "title": "Isaiah 41:10",
      "tags": ["STRENGTH", "COURAGE", "SUPPORT"],
      "body": "Fear not, for I am with you; Be not dismayed, for I am your God. I will strengthen you, Yes, I will help you, I will uphold you with My righteous right hand.",
      "citation": "Isaiah 41:10",
      "audioUrl": "https://cdn.basmo.app/aud/verse/v_isaiah_41_10_vi.mp3",
      "backgroundImageUrl": "https://cdn.basmo.app/img/ocean.jpg",
      "completed": true
    },
    {
      "id": "devotional_2026-04-15",
      "type": "DEVOTIONAL",
      "durationMinutes": 3,
      "title": "Strengthened by His Righteous Hand",
      "tags": ["FAITH", "OVERCOMING CHALLENGES"],
      "body": "In this verse, God provides a profound reassurance ...",
      "citation": "Isaiah 41:10",
      "audioUrl": "https://cdn.basmo.app/aud/dev/d_2026-04-15_vi.mp3",
      "backgroundImageUrl": "https://cdn.basmo.app/img/hands_purple.jpg",
      "completed": true
    },
    {
      "id": "prayer_2026-04-15",
      "type": "PRAYER",
      "durationMinutes": 2,
      "title": "Strength in God",
      "tags": [],
      "body": "Heavenly Father, I come before You with an open heart ...",
      "citation": null,
      "audioUrl": "https://cdn.basmo.app/aud/prayer/p_2026-04-15_vi.mp3",
      "backgroundImageUrl": "https://cdn.basmo.app/img/hands_silhouette.jpg",
      "completed": true
    },
    {
      "id": "peace_2026-04-15",
      "type": "PEACE_AND_CALM",
      "title": "PEACE AND CALM",
      "subtitle": "When life's too loud, listen within",
      "promptHeadline": "Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow",
      "privacyNote": "Your privacy is guaranteed and your information will remain confidential."
    }
  ]
}
```

### 5.2 `POST /journey/{date}/cards/{cardId}/complete`

```jsonc
// Request: POST /v1/journey/2026-04-15/cards/verse_2026-04-15/complete
{
  "completedAt": "2026-04-16T05:30:00Z",
  "mode": "READ"   // READ | LISTEN
}
// Response 200
{
  "card": { ... },                  // card đã update
  "dayProgressPercent": 100,
  "streakUpdated": true,
  "currentStreak": 1,
  "lightPointsAwarded": 70,
  "lightPointsBalance": 100,
  "milestoneUnlocked": null         // hoặc "STREAK_3" -> +33 chat questions
}
```

### 5.3 `GET /promo/active`

```jsonc
{
  "promoId": "exclusive_deal_24h_v3",
  "label": "Exclusive Deal",
  "endsAt": "2026-04-17T11:55:00Z",
  "destination": "PAYWALL",
  "paywall": {
    "headline": "Never Miss a Moment of Faith",
    "bullets": ["Widget with Personalized Daily Verses", "Bring the Bible to your Home Screen", "Personalized Audio Daily Devotionals"],
    "plans": [
      { "skuId": "weekly_premium_intro", "type": "TRIAL", "trialDays": 7, "weeklyPriceMicros": 105000000000, "originalWeeklyPriceMicros": 158549980000, "currency": "VND", "saveBadgePercent": 36 },
      { "skuId": "yearly_premium",       "type": "ANNUAL", "annualPriceMicros": 880000000000, "currency": "VND" }
    ]
  }
}
```

### 5.4 `GET /user`

```jsonc
{
  "uid": "guest_a3f9...",
  "nickname": "Faithfulness Traveler 3576",
  "membership": "FREE",
  "wallet": { "lightPoints": 100, "chatQuestionsLeft": 5 },
  "streak": { "current": 1, "longest": 1 },
  "reminder": { "time": "09:00", "days": ["MON","TUE","WED","THU","FRI","SAT","SUN"] },
  "personalDetails": { "ageRange": "55+", "denomination": "Pentecostal", "email": null, "church": null }
}
```

### 5.5 `PUT /user/reminder`

```jsonc
{
  "time": "08:30",
  "days": ["MON","TUE","WED","THU","FRI"]
}
```

### 5.6 `GET /store/light-points`

```jsonc
{
  "balance": 100,
  "premium":     [ { "id": "premium_1m",  "label": "1-Month Premium", "costPoints": 5000 } ],
  "appUnlocks":  [ { "id": "wallpaper_live", "label": "Live Wallpaper", "costPoints": 500 } ],
  "chatUnlocks": [
    { "id": "qpack_5",   "label": "5 Questions",   "costPoints": 250  },
    { "id": "qpack_25",  "label": "25 Questions",  "costPoints": 1000 },
    { "id": "qpack_100", "label": "100 Questions", "costPoints": 2500 }
  ],
  "purchaseTiers": [
    { "skuId": "lp_100",   "amount": 100,   "priceMicros":  30000000000, "currency": "VND" },
    { "skuId": "lp_500",   "amount": 500,   "priceMicros": 108000000000, "currency": "VND" },
    { "skuId": "lp_1000",  "amount": 1000,  "priceMicros": 198000000000, "currency": "VND" },
    { "skuId": "lp_2500",  "amount": 2500,  "priceMicros": 391000000000, "currency": "VND" },
    { "skuId": "lp_10000", "amount": 10000, "priceMicros": 1300000000000, "currency": "VND" }
  ],
  "studyUnlocks": [
    { "id": "study_loved_then_loving",  "label": "Loved, then loving",        "costPoints": 250 },
    { "id": "study_heart_thanksgiving", "label": "The Heart of Thanksgiving", "costPoints": 250 }
    // ... 18 cái khác (full list trong today_observations.md)
  ],
  "comingSoon": [ { "id": "study_special", "label": "Special Study" } ]
}
```

---

## 6. Data model summary

```kotlin
data class TodayState(
    val selectedDate: LocalDate,
    val systemToday: LocalDate,
    val nickname: String,
    val avatarLetter: Char,                    // ký tự đầu nickname
    val title: String,                         // "Today's Journey" hoặc "MMM DD's Journey"
    val theme: String,                         // subtitle dynamic per-day
    val streak: Int,
    val lightPoints: Int,
    val weekDays: List<DayCellState>,          // 7 cell tuần hiện tại
    val progressPercent: Int,
    val cards: List<CardState>,
    val emptyState: EmptyState?,               // non-null khi day bị gate
    val exclusiveDeal: ExclusiveDealState?,
)

sealed class CardState {
    data class Session(
        val id: String,
        val type: SessionType,                 // VERSE | DEVOTIONAL | PRAYER
        val durationMinutes: Int,
        val title: String,
        val tags: List<String>,
        val backgroundImageUrl: String,
        val completed: Boolean,
        val expanded: Boolean,                 // invariant single-expansion
    ) : CardState()
    data class PeaceAndCalm(
        val title: String,                     // "PEACE AND CALM"
        val subtitle: String,                  // "When life's too loud, listen within"
    ) : CardState()
    data class ExclusiveDeal(
        val label: String,                     // "Exclusive Deal"
        val countdown: Duration,
    ) : CardState()
}

data class DayCellState(
    val date: LocalDate,
    val weekdayLetter: Char,
    val dayNumber: Int,
    val status: DayCellStatus,                 // TODAY | HAS_CONTENT | DIM_PAST | FUTURE | SELECTED
)

enum class DayCellStatus { TODAY, HAS_CONTENT, DIM_PAST, FUTURE, SELECTED }

sealed class EmptyState {
    object TodayLockedByReminder : EmptyState()    // F.1
    object FutureDate : EmptyState()               // F.2
}

data class ExclusiveDealState(
    val label: String,
    val endsAt: Instant,
)
```

---

## 7. Open questions / để engineer verify

1. **Logic gating reminder** — plan Today unlock khi wall clock vượt time
   reminder, hay chỉ sau khi notification reminder được *acknowledge* (tap)?
   Capture timestamp `12:19` qua reminder `09:00` mà today vẫn lock.
2. **Listen completion** — mở `Listen` count là "completed", hay chỉ sau khi
   audio play through?
3. **Flow submit Peace and Calm** — gì xảy ra sau khi `Continue` enable và
   tap? Có khả năng 1 screen AI grace-moment — capture session sau.
4. **Bonus streak** — `33 free questions` promise ở 3-day streak. Capture UI
   delivery bonus thật.
5. **Rate award Light Points** — chính xác bao nhiêu point per session-complete
   / per Day-Complete? Đáng đo qua 5 day.
6. **Navigation past-month Calendar** — chỉ April + May render; user reach
   March hoặc trước đó thế nào? Có khả năng infinite-scroll up — chưa test.
7. **Row Profile Drawer** — đa số row chưa deep-test; behaviour `Limit screen
   time`, `Personalize your conversations`, `Widget selection`, toggle `Daily
   Bible Verse Wallpaper` đều cần micro-spec riêng.
8. **Pricing** — confirm source giá Plan A pre-strikethrough (`158549.98`
   trông như raw `priceMicros / 1e6` không round/format).

---

## 8. Acceptance criteria

1 implementation Today coi là **done** khi các điểm sau verify được end-to-end:

- [ ] Cold launch land trên tab Today; bottom nav `Today` show với style
  `large_label`.
- [ ] Behaviour sticky header: scroll cards không di chuyển header.
- [ ] Week strip render 7 day của tuần hiện tại; today highlight; day quá khứ
  có content show ring.
- [ ] Tap day quá khứ có content mở reader của day đó (mode re-read); day
  quá khứ chưa start là no-op.
- [ ] Calendar mở qua streak pill; 2 tháng render inline; quy tắc tap giống
  week strip.
- [ ] Subtitle và icon `i` cùng mở 1 tooltip; tooltip dismiss được qua `X` và
  tap ngoài.
- [ ] Light Points badge display balance hiện tại (handle multi-digit); tap
  mở page Available Points.
- [ ] Mỗi session card support state collapsed/expanded; chỉ 1 expand mỗi
  lúc; collapsed show chip `DONE` khi complete.
- [ ] Read hoặc listen 1 session mark complete và update `dayProgressPercent`
  ngay.
- [ ] Hoàn thành session cuối trigger Day-Complete; `Continue` về Today
  landing với mọi card `DONE` và streak +1.
- [ ] Khi today lock sau reminder, empty state F.1 render với interpolation
  đúng `<Weekday>, <DD MMMM>` và live `<HH:mm>`.
- [ ] `Change reminder` mở bottom sheet; time chip mở Material 3 TimePicker;
  `Update reminder` persist và dismiss.
- [ ] Countdown banner Exclusive Deal tick xuống real-time; tap mở paywall;
  CTA `Try for Free` trigger Play Billing.
- [ ] Profile Drawer slide từ trái; pre-fill nickname, age range, denomination
  từ payload server `User`.
- [ ] Tooltip overlay không block tương tác phần còn lại của screen (verify
  setting `Popup` `properties.focusable`).
- [ ] Mọi currency render bằng `₫` với thousand separator nhất quán (1 trong
  `,` hoặc `.` — pick và stick).
- [ ] Bottom nav giữ visible trên Today landing (mọi variant); ẩn trên
  overlay full-screen (Calendar, Paywall, Available Points, Session Reader,
  Day-Complete) và trên drawer.

---

## 9. References

- **Raw observations** (bounds & literal per-screen): `today_observations.md`
- **Flow spec** (transition block-by-block, state machine, bug QA):
  `today_spec.md`
- **Cross-cluster spec**:
  - Onboarding (setup reminder ban đầu, reuse Day-Complete):
    `onboarding_feature_spec.md`
  - Chat (entry từ "Chat to learn more"): `chat_feature_spec.md`
  - Community / Bible / Explore (sibling trong bottom nav):
    `community_feature_spec.md`, (Bible/Explore chưa spec)
- **Screenshot**: `spec/screens/today/screen_*.png`
- **UI dump**: `spec/ui_dumps/today/screen_*.xml`
