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
  section_line: 210
- anchor: today/screen/explore_overlay
  letter: C
  name: Explore Overlay (sparkle icon)
  section_line: 242
- anchor: today/screen/calendar
  letter: D
  name: Calendar (full-month grid)
  section_line: 275
- anchor: today/screen/subtitle_info_tooltip
  letter: E
  name: Subtitle / Info Tooltip
  section_line: 310
- anchor: today/screen/day_state_empty_screens
  letter: F
  name: Day-State Empty Screens
  section_line: 336
- anchor: today/screen/reminder_editor
  letter: G
  name: Reminder Editor
  section_line: 363
- anchor: today/screen/today_tab_paywall
  letter: H
  name: Today-tab Paywall (Exclusive Deal)
  section_line: 406
- anchor: today/screen/session_reader
  letter: I
  name: Session Reader (Verse / Devotional / Prayer)
  section_line: 451
- anchor: today/screen/day_complete_celebration
  letter: J
  name: Day-Complete Celebration
  section_line: 509
- anchor: today/screen/peace_and_calm_bottom_sheet
  letter: K
  name: Peace and Calm Bottom Sheet
  section_line: 538
- anchor: today/screen/available_points
  letter: L
  name: Available Points (Light Points store)
  section_line: 564
components: []
apis: []
data_models: []
reuses: []
criteria: []
related:
- today/flow/root
- today/observations/root
---

# BibleChat — Today Feature Cluster Spec (Implementation-Ready)

> **⚠️ CANONICAL — REFERENCE STRUCTURE, KHÔNG PHẢI TEMPLATE NGÔN NGỮ.**
> File này gốc từ project BibleChat (gen trước khi enforce policy "output
> tiếng Việt thuần"). Mọi spec MỚI phải viết bằng tiếng Việt với technical term
> tiếng Anh — xem `docs/I18N_GLOSSARY.md`.
>
> Khi reference file này, agent `spec-writer` PHẢI mimic:
> - Frontmatter shape (screens, components, apis, data_models, reuses,
>   criteria, invariants, questions, related)
> - 9 section body chuẩn: Metadata / Tổng Quan / Chi Tiết Từng Screen /
>   Cross-screen invariants / API contract draft / Data model summary /
>   Open questions / Acceptance criteria / References
> - Anchor marker `{#feature/<type>/<name>}` sau heading mỗi node graph
> - Code fence ` ```json ` cho API JSON Schema, ` ```kotlin ` cho data class
> - Component `reuse_key` + list `reuses` nếu phát hiện cross-feature reuse
>
> Mọi thông tin trích từ reverse-engineering app thật (`com.basmo.BibleChat` v4.3.10)
> trên device `8A5X0M2H8` (Pixel, Android, locale `vi-VN`).
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
| **Author** | Auto-generated from reverse spec |
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
DashboardActivity (default tab = navigation_daily_journey)
  │
  ▼
  ┌────────────────────────────────────────────────────────────────┐
  │  TODAY LANDING (Block A)                                        │
  │  ┌──────────── Sticky header ────────────┐                       │
  │  │ Avatar · Title · Sparkle · Streak pill │                       │
  │  │ Subtitle theme · Info i · Light Points │                       │
  │  │ Week strip (M T W T F S S, 7 cells)    │                       │
  │  │ Progress today / N%                    │                       │
  │  └────────────────────────────────────────┘                       │
  │  Cards (scrollable, 5 fixed):                                     │
  │    1. Exclusive Deal banner (countdown)                           │
  │    2. YOUR VERSE (1 MIN)        ──┐                               │
  │    3. PERSONALIZED DEVOTIONAL (3 MIN) ├─ session cards            │
  │    4. PRAYER OF THE DAY (2 MIN) ──┘                               │
  │    5. PEACE AND CALM (one-shot bottom sheet)                      │
  └────────────────────────────────────────────────────────────────────┘
   │
   ├── Avatar          → Profile Drawer (Block B)
   ├── Sparkle         → Explore overlay (Block C, cross-cluster directory)
   ├── Streak pill     → Calendar full-month (Block D)
   │                       └── day with content → Verse Reader (Block I read-only)
   ├── Subtitle / i    → Tooltip overlay (Block E)
   ├── Light Points    → Available Points / Light Points store (Block L)
   ├── Week-strip day  → switch displayed day (re-renders Block A or its empty state F)
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
| **Tech** | Compose (semantic-only nodes, no resource-ids) |
| **Backgrounds** | Header có gradient olive-mustard; cards area là dark surface với card backgrounds image-aware (ocean cho Verse, hands cho Devotional/Prayer, leaf cho Peace) |

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
├────────────────────────────────────────────┤  y≈770 (top of cards)
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
| Header avatar | Static letter (1st char of nickname). Long-press: not tested. | Tap → Profile Drawer (Screen B) |
| Title | `Today's Journey` if selected day = system today; otherwise `MMM DD's Journey` (e.g. `Apr 15's Journey`) | Read-only |
| Sparkle icon | Always visible | Tap → Explore overlay (Screen C) |
| Streak pill | Shows fire 🔥 + integer `currentStreak` | Tap → Calendar (Screen D) |
| Subtitle | Per-day theme string (server-supplied) | Tap → Tooltip (Screen E) |
| Info `ⓘ` icon | Always visible | Tap → same Tooltip |
| Light Points badge | Yellow circle + integer `lightPointsBalance` | Tap → Available Points (Screen L) |
| Week-strip day cells | Each cell: weekday letter + day-of-month number; visual ring/fill encodes status (today=filled, has-content=ring, dimmed=non-interactive) | Tap behaviour per status (see table below) |
| Progress bar | Linear progress, value `dayProgressPercent` (0..100), label `Progress today` (or `Progress for MMM DD`), value rendered as `N%` with no decimal | Read-only |
| Card: Exclusive Deal | Single visual: gift icon + label + countdown timer (mm:ss not used; format `HH:mm:ss` server-supplied or computed from `dealEndsAt - now`) | Tap → Paywall (Screen H) |
| Card: session (Verse/Devotional/Prayer) | Two states: collapsed (header strip with `DONE` chip when complete, `⌄` chevron when not) and expanded (title + tag pills + Listen + Read) | Tap header → toggle expand (single-expansion invariant). Tap Listen / Read inside → Reader (Screen I) |
| Card: Peace and Calm | One-shot card — no expand state | Tap → Bottom sheet (Screen K) |

#### Week-strip day-cell tap rules

| Cell status | Visual | Tap behaviour |
|---|---|---|
| Today (system date) | Filled circle, white number | Switch to today's content (or empty state F.1 if locked) |
| Past **with completed sessions** | Ring around number | Switch to that day's reader content (re-read mode) |
| Past **never started** | Dimmed grey, no ring | No-op (silent) |
| Future | Outlined, normal text | Switch to empty state F.2 (`Check back tomorrow`) |
| Currently selected | Yellow ring/fill | (re-tap = no-op) |

#### Data dependencies

| Field | Source | Refresh trigger |
|---|---|---|
| `nickname` | `User.nickname` | On profile edit |
| `currentStreak` | `User.streak.current` | After Day-Complete |
| `longestStreak` | `User.streak.longest` | After Day-Complete |
| `lightPointsBalance` | `User.wallet.lightPoints` | After session complete, after store purchase, after Day-Complete |
| `selectedDate` | local UI state (defaults to system today) | On day-strip / calendar tap |
| `weekDays[]` | computed from `selectedDate` (Mon..Sun of that week) | When selectedDate crosses a week boundary |
| `dayPlan(selectedDate)` | `GET /journey/{date}` | On selectedDate change |
| `dayPlan.theme` | server | per `dayPlan` |
| `dayPlan.progressPercent` | server (0/33/67/100 typically) | per session-complete event |
| `dayPlan.cards[]` | server | per `dayPlan` |
| `exclusiveDeal` | `GET /promo/active` | App launch + when Today opens; countdown rendered locally from `endsAt` |

#### Empty states

| When | Render |
|---|---|
| `selectedDate == today AND !todayUnlocked` | Screen F.1 |
| `selectedDate > today` | Screen F.2 |
| `selectedDate < today AND !pastStarted` | (cell isn't tappable; state shouldn't be reachable) |

---

### SCREEN B — Profile Drawer

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap avatar on header (118, 213) |
| **Container** | `DrawerLayout` (Material) sliding in from left |
| **Width** | ~92% of viewport (`[0,0][990,2028]`); right `[990,1080]` is scrim with `desc=Close navigation menu` |
| **Dismiss** | `KEYCODE_BACK` or tap scrim |
| **Tech** | mostly Compose inside the drawer |

#### Sections (vertical list, single scrollable column)

| Section header | Items | Notes |
|---|---|---|
| (none — header block) | Avatar, EditText nickname, Current Streak, Longest Streak | EditText is `clickable=true` and editable inline |
| `Friends` | Friends row (`You have 0 friends`) | Out of scope here — likely opens Friends list |
| `Limited Special Offer` | `Exclusive Deal` row (timer mirrors Today landing) | Same destination as the Today-landing banner (Screen H) |
| `My Space` | `Explore all features`, `Limit screen time`, `Personalize your conversations`, `Widget selection`, `Daily Bible Verse Wallpaper` (Material switch, OFF default) | Each row navigates to its own settings screen — out of scope for Today |
| `Personal Details` | `Age range` (`55+`), `Email`, `Denomination` (`Pentecostal`), `Church` | All editable; pre-filled from onboarding quiz |
| `Subscription` | `Membership` (`Free`), `Upgrade to Premium`, `Restore purchases` | Upgrade likely re-opens paywall |
| `About` | `Contact us`, `Terms of use`, `Privacy policy` | Standard legal/support links |
| `Account` | `Link account data` (Google), `Manage your reminders`, `Change language` (`English`) | Reminders → reuse Screen G |
| Footer | `App version: 4.3.10`, `UID:` (empty for guest) | Static |

#### Implementation note

The Profile Drawer is **shared across tabs** (always opened from any header avatar). Implement once as a singleton fragment hosted by `DashboardActivity` and inflate into `DrawerLayout`.

---

### SCREEN C — Explore Overlay (sparkle icon)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap sparkle icon on Today header (752, 159) |
| **Container** | Full-screen Compose overlay (no underlying tab visible behind) |
| **Dismiss** | `KEYCODE_BACK` |

#### Layout

- H1: `Explore`
- Sub-line: `Discover everything BibleChat has to offer`
- Filter chips (horizontal, single-select): `Personalize` (selected default) · `Bible Study` · `Community` · `Journey`
- Body: 2-column grid grouped by section (PERSONALIZE, BIBLE STUDY, COMMUNITY, JOURNEY, LEISURE)

#### Sections & items

| Section | Items (label + glyph) |
|---|---|
| `PERSONALIZE` | Lockscreen, App Widget, Affirmations |
| `BIBLE STUDY` | Study Plans, Chat, Voice Chat, Reading, Bible Stories, Animations, Kids' Stories |
| `COMMUNITY` | Groups, Friends, Live Prayer, My Prayers, World Events |
| `JOURNEY` | Daily Plan, Calendar, The Bible, Screen Time, Meditation |
| `LEISURE` | Word Guesser, Bible Trivia |

#### Implementation note

This is a **global feature directory** that aliases destinations also reachable via bottom-nav (Chat, Community, Bible, Explore tab) and Profile Drawer. Treat it as a separate cluster and link to the relevant cluster's spec when implementing each item.

---

### SCREEN D — Calendar (full-month grid)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap streak/calendar pill on Today header (921, 159) |
| **Container** | Full-screen overlay |
| **Dismiss** | `X` close (top-right) or `KEYCODE_BACK` |
| **Tech** | Compose, custom month grid |

#### Layout

- Title: month name + year (e.g. `April 2026`)
- Close `X`: top-right
- Day-of-week header row: `MON TUE WED THU FRI SAT SUN`
- Body: month grid (5–6 rows of 7 cells), each cell `132×118 px` (`@440 dpi`)
- Multiple months render inline — current month label `April` (yellow), then full grid; below, `May` label + grid (no pagination chevrons)

#### Cell visual states

| State | Visual |
|---|---|
| Default (any day in month) | Outlined circle with day number |
| Past with completed sessions | Yellow ring (proportional to `dayProgressPercent`) |
| Today | Filled dark circle, white number (slightly larger or bolder) |
| Future | Same as default outlined |
| Past unstarted | Dimmer outline (less opacity) |

#### Tap rules

Same as Today landing's week-strip rules — past unstarted = silent no-op; days with content navigate to that day's session reader (re-read mode).

---

### SCREEN E — Subtitle / Info Tooltip

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap subtitle text (441, 284) OR info `i` icon (733, 284) |
| **Container** | Compose `Popup` overlay (does **not** appear in `uiautomator dump`) |
| **Dismiss** | `X` button on tooltip OR tap outside |

#### Content

| Element | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close | `X` (top-right of tooltip) |

#### Implementation note

Render as `Popup` anchored above the progress bar. Backdrop dim ~20%. Auto-dismiss on outside tap.

**Testing caveat**: this overlay's text nodes are absent from the uiautomator dump. Espresso/UIAutomator tests must match by **resource ID assigned to the popup container** (if any) or use **TalkBack accessibility nodes**, not text matchers.

---

### SCREEN F — Day-State Empty Screens

#### F.1 — Today locked behind reminder

| Field | Value |
|---|---|
| **Entry** | `selectedDate == today AND !todayUnlocked` |
| **Headline** | `Not quite time yet.\nCheck back <Weekday>, <DD MMMM> for your Daily Plan session` (interpolated with `selectedDate`) |
| **Sub** | `Your reminder is set for <HH:mm>.\n Would you like to update it?` (interpolated with `User.reminder.time`) |
| **CTA** | `Change reminder` (yellow text link) → opens Screen G |
| **Progress bar** | renders `0%` |

#### F.2 — Future day

| Field | Value |
|---|---|
| **Entry** | `selectedDate > today` |
| **Headline** | `Not quite time yet.\nCheck back tomorrow for your Daily Plan session` |
| **Sub** | (none) |
| **CTA** | (none) |

#### F.3 — Past unstarted (theoretical)

The day is not selectable from the strip/calendar, so this state is unreachable in practice. Nothing to render.

---

### SCREEN G — Reminder Editor

#### G.1 — Reminder Bottom Sheet

| Field | Value |
|---|---|
| **Entry** | Tap `Change reminder` link in F.1 OR tap `Manage your reminders` in Profile Drawer |
| **Container** | Material `BottomSheetDialog` (modal) |
| **Dismiss** | `X` close, swipe down on drag handle, `KEYCODE_BACK`, scrim tap |

| Element | Text / spec |
|---|---|
| Drag-handle hit-zone | `[44,110][1036,242]` |
| Close `X` | `[915,110][1047,242]` |
| Bell illustration | yellow bell, centred top |
| Title | `Connect with God Daily` |
| Body | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Time-chip label | `We'll remind you at...` |
| Time chip | shows current time `HH:mm` (default `09:00`); chevron right; tap → G.2 |
| Days label | `On these days` |
| Day toggles | 7 cells `M T W T F S S`; each = `View` containing letter + checkable circle. Default = all 7 enabled. |
| CTA | `Update reminder` (yellow, full-width) — persists state and dismisses sheet |

#### G.2 — Material 3 Time Picker

Standard Material 3 `TimePicker` (24h mode). Hour input active by default. Bottom of dialog still shows the day toggles + `Update reminder` CTA — i.e. the picker is **inline** above the bottom sheet, not a separate dialog covering the whole screen.

`KEYCODE_BACK` closes the picker (returns to G.1); second back closes G.1.

#### Data model

```kotlin
data class DailyReminder(
    val time: LocalTime,        // default 09:00
    val days: Set<DayOfWeek>,   // default all 7
    val enabled: Boolean,       // implicit true; toggle off = ?
)
```

Persistence: `SharedPreferences` for client-side scheduling (`AlarmManager.setExactAndAllowWhileIdle`) + sync to backend `PUT /user/reminder`.

---

### SCREEN H — Today-tab Paywall (Exclusive Deal)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap `Exclusive Deal` banner (Today landing OR Profile drawer) |
| **Container** | Full-screen activity/fragment with darkened backdrop and dove illustration in upper-right |
| **Dismiss** | `X` (top-left) or `KEYCODE_BACK` |

#### Components

| Element | Spec |
|---|---|
| Headline | `Never Miss a Moment of Faith` |
| Bullet 1 | `Widget with Personalized Daily Verses` |
| Bullet 2 | `Bring the Bible to your Home Screen` |
| Bullet 3 | `Personalized Audio Daily Devotionals` |
| Toggle | label `I want to try the app for free`, Material switch, default ON |
| Plan A card (selected when toggle ON) | `7 Days Free Trial` · `SAVE 36%` badge · `Then ₫158,549.98 → ₫105,000 per week. No payment now` |
| Plan B label | `Best Price of the Year` |
| Plan B card | `12-Month Access` · `Billed yearly at ₫880,000` |
| Disclaimer | `Cancel anytime before <today + 7 days>.\nNo risks, no charges.` |
| CTA | `Try for Free →` (yellow pill, full-width) |
| Footer | `Terms of use` · `Privacy policy` · `Restore` |

#### Behaviour

- Toggle ON → Plan A pre-selected. Toggle OFF → Plan B pre-selected (assumed, not verified).
- CTA triggers Google Play Billing flow with the SKU corresponding to selected plan.
- Countdown timer is **global** (single `dealEndsAt` per user); it runs regardless of which screen the user is on.

#### Pricing data

| Plan | Display | SKU pattern (assumed) |
|---|---|---|
| 7-day trial → weekly | `₫105,000/week` (after `₫158,549.98` strikethrough) | `weekly_premium_intro` |
| 12-month annual | `₫880,000/year` | `yearly_premium` |

#### Known QA bug

The strikethrough price renders as `158549.98` (no thousands separators), while the promo line uses `₫105,000` (correctly formatted). Use the same `NumberFormat` for both.

---

### SCREEN I — Session Reader (Verse / Devotional / Prayer)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap `Listen` or `Read` on a session card; OR tap a completed day in Calendar/week-strip |
| **Container** | Full-screen, image background tied to the session theme |
| **Dismiss** | `X` (top-right) closes outright, returns to Today landing for the same `selectedDate`. Back arrow (top-left) appears when entered via Chat sub-screen |

#### Common shell

| Region | Element | Spec |
|---|---|---|
| Top | Back arrow (left, when applicable) · `Your Journey` title (centre) · `X` close (right) | static |
| Below top | `Progress for <MMM DD>` + `<N>%` (yellow) | reflects current `dayProgressPercent` |
| Body header | Card type label small caps + duration (e.g. `YOUR VERSE · 1 MIN`) | static per session type |
| Body | Long-form text (verse / devotional / prayer); scroll vertical when overflows | server-supplied |
| Body footer | Citation in yellow (e.g. `Isaiah 41:10`) — present on Verse and Devotional, absent on Prayer | optional |
| Bottom action bar | left: thumbs-down · middle: `Chat to learn more` · right: `→` arrow (intermediate) OR `Done` pill (last incomplete) | dynamic |

#### Read vs Listen

`Read` — bottom action bar as above (text-only).
`Listen` — bottom action bar replaced with audio toolbar:

| Slot | Element |
|---|---|
| Top | linear audio progress bar |
| Left | current time (`MM:SS`) |
| Right | track length (`MM:SS`) |
| Buttons | Share · Previous · Play/Pause · Next · Replay |

Tapping `Listen` auto-plays. Tapping `Read` opens the static text view; user can switch to audio via separate icon (not verified).

#### "Chat to learn more" → Chat cluster

Navigates to `Chat` (already specced in `chat_feature_spec.md`) with the session text **pre-loaded as a context bubble**. The bubble exposes thumbs-up / thumbs-down / `Copy` / `Share`. Composer is below.

#### Data model

```kotlin
data class SessionContent(
    val type: SessionType,          // VERSE | DEVOTIONAL | PRAYER
    val durationMinutes: Int,       // 1 | 3 | 2
    val title: String,              // e.g. "Strengthened by His Righteous Hand"
    val tags: List<String>,         // e.g. ["FAITH", "OVERCOMING CHALLENGES"]
    val body: String,               // multi-paragraph
    val citation: String?,          // e.g. "Isaiah 41:10" — null for Prayer
    val audioUrl: String?,          // null when audio not available
    val backgroundImageUrl: String, // theme image
)
```

Session-completion is registered when the reader is **opened** (Read or Listen). Track per-session completion server-side; recompute `dayProgressPercent` and broadcast back to Today landing.

---

### SCREEN J — Day-Complete Celebration

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Complete the last incomplete session of the day (typically tapping `Done` on the third reader) |
| **Container** | Full-screen overlay |
| **Dismiss** | Tap `Continue` (returns to Today landing for the same day) |
| **Reuse** | Same screen as onboarding's Block N |

#### Layout

| Element | Text / spec |
|---|---|
| Fire illustration | yellow gradient flame, centred top |
| Counter | `<currentStreak>` (large yellow numeral) |
| Label | `day streak` (yellow) |
| 3-dot streak progress | dot 1..3 — filled / outline based on `currentStreak / 3` (capped at 3) |
| Sub | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` (static — but the bonus is delivered upon hitting 3-day streak) |
| Mini week strip | 7 day cells `Mo Tu We Th Fr Sa Su` with current week numbers; today's cell shows fire icon |
| CTA | `Continue` (yellow pill) |

#### Bonus delivery

When `currentStreak` reaches `3`, append `33` to `chatQuestionsAvailable` and surface a "+33 free questions unlocked" toast/celebration variant (not observed yet — left for future capture).

---

### SCREEN K — Peace and Calm Bottom Sheet

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap `PEACE AND CALM` card |
| **Container** | Full-screen bottom sheet with darkened backdrop |
| **Dismiss** | `desc=Close sheet` top hit-zone or `KEYCODE_BACK` |

#### Layout

| Element | Text |
|---|---|
| Top close hit-zone | `[0,0][1080,122]` |
| Headline | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Privacy note | `Your privacy is guaranteed and your information will remain confidential.` |
| EditText | placeholder `Describe here`, multi-line |
| `Continue` CTA | greyed/disabled until `EditText` has content |

#### Behaviour (predicted, not verified)

Submitting `Continue` likely opens a "Moment of Grace" screen with an AI-generated prayer/affirmation tailored to the user's input. The card itself does **not** count toward the 100% day-progress (the 3 sessions Verse + Devotional + Prayer suffice).

---

### SCREEN L — Available Points (Light Points store)

#### Thông Tin Chung

| Field | Value |
|---|---|
| **Entry** | Tap Light Points badge on Today header (950, 284) |
| **Container** | Full-screen, scrollable |
| **Dismiss** | `X` (top-left) or `KEYCODE_BACK` |

#### Header

`Available Points : ⊙ <lightPointsBalance>` (yellow circle glyph + number)

#### Sections

| Section | Items |
|---|---|
| `Premium` | `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `5 Questions` · `⊙ 250` ; `25 Questions` · `⊙ 1000` ; `100 Questions` · `⊙ 2500` |
| `Light Points` (purchase tiers, paid in VND) | `100 LP` · `₫30,000` · `500 LP` · `₫108,000` · `1.000 LP` · `₫198,000` · `2.500 LP` · `₫391,000` · `10.000 LP` · `₫1,300,000` |
| `Study Unlocks` | 20 study packs, each `⊙ 250` (full list in `today_observations.md` §15) |
| `Coming Soon` | `Special Study` (placeholder, not purchasable) |

#### Currency model

```kotlin
data class Wallet(
    val lightPoints: Int,       // earned + purchased
    val chatQuestionsLeft: Int, // separate counter, surfaced as ?N badge in Chat header
)

enum class LpEarnSource { SESSION_COMPLETE, DAY_STREAK, PURCHASE, PROMOTIONAL }
```

#### Known QA bug

Light Points purchase tiers use dot-as-thousands-separator (`1.000`, `2.500`, `10.000`) while VND prices use comma (`30,000`, `1,300,000`). Same screen — pick one.

---

## 4. Cross-screen invariants

### 4.1 Session reader chrome

All three readers (Verse / Devotional / Prayer) share the exact same shell — implement once, parameterise on `SessionContent`.

### 4.2 Single-expansion invariant

Only one session card on the Today landing can be expanded at a time. Tapping a collapsed card auto-collapses any expanded sibling.

### 4.3 Progress denominator

`dayProgressPercent` is computed over **3 sessions** (Verse + Devotional + Prayer). Peace and Calm is **not** counted. Expected jumps: `0% → 33% → 67% → 100%` (observed: `75% → 100%` after the Prayer in this session — so the displayed percent is **rounded** with `Verse + Devotional` already counting as `2/3 = 66.67% → rounded to 75%`, suggesting custom rounding or a different weighting; verify with engineer).

### 4.4 Sticky header

Header from y=93 to y=778 is sticky. Cards scroll inside `[0, ~770][1080, 1808]`.

### 4.5 Light Points vs Chat Questions

These are **two separate counters**:
- **Light Points** (`⊙` badge in Today header) → spent on premium, wallpaper, Q-credits, studies.
- **Chat Questions** (`?N` badge in Chat header) → consumed per AI question; replenished via Light Points purchases, streak rewards, premium subscription.

### 4.6 Bottom-nav visibility

Bottom nav stays visible on:
- Today landing (all variants)
- Profile drawer? — **No**, drawer overlays nav
- Calendar, Paywall, Available Points, Session Reader, Day-Complete — **No**, these are full-screen overlays

### 4.7 Date-state machine

```
[ today date rolls over at midnight ] ─▶ [ selectedDate auto-set to new today ]
[ user taps past day with content   ] ─▶ [ render reader for that day, do NOT change selectedDate ]
[ user taps day in week strip       ] ─▶ [ if has content/today/future: switch selectedDate ]
                                          [ if past unstarted: no-op ]
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
  "card": { ... },                  // updated card
  "dayProgressPercent": 100,
  "streakUpdated": true,
  "currentStreak": 1,
  "lightPointsAwarded": 70,
  "lightPointsBalance": 100,
  "milestoneUnlocked": null         // or "STREAK_3" -> +33 chat questions
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
    // ... 18 more (full list in today_observations.md)
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
    val avatarLetter: Char,                    // first char of nickname
    val title: String,                         // "Today's Journey" or "MMM DD's Journey"
    val theme: String,                         // dynamic per-day subtitle
    val streak: Int,
    val lightPoints: Int,
    val weekDays: List<DayCellState>,          // 7 cells of current week
    val progressPercent: Int,
    val cards: List<CardState>,
    val emptyState: EmptyState?,               // non-null when day is gated
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
        val expanded: Boolean,                 // single-expansion invariant
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

## 7. Open questions / left for engineer to verify

1. **Reminder gating logic** — does the Today plan unlock when the wall clock passes the reminder time, or only after the reminder notification is *acknowledged* (tapped)? Capture timestamp `12:19` was past the `09:00` reminder yet today was still locked.
2. **Listen completion** — does opening `Listen` count as "completed", or only after audio plays through?
3. **Peace and Calm submit flow** — what happens after `Continue` is enabled and tapped? Likely an AI grace-moment screen — capture next session.
4. **Streak bonus** — `33 free questions` promised at 3-day streak. Capture the actual bonus delivery UI.
5. **Light Points award rate** — exactly how many points per session-complete / per Day-Complete? Worth measuring across 5 days.
6. **Calendar past-month navigation** — only April + May rendered; how does the user reach March or earlier? Possibly infinite-scroll up — not tested.
7. **Profile Drawer rows** — most rows not deep-tested; `Limit screen time`, `Personalize your conversations`, `Widget selection`, `Daily Bible Verse Wallpaper` toggle behaviour all need their own micro-specs.
8. **Pricing** — confirm Plan A pre-strikethrough price source (`158549.98` looks like raw `priceMicros / 1e6` without rounding/formatting).

---

## 8. Acceptance criteria

A Today implementation is considered **done** when the following can be verified end-to-end:

- [ ] Cold launch lands on Today tab; bottom nav `Today` shown with `large_label` style.
- [ ] Header sticky behaviour: scrolling cards does not move the header.
- [ ] Week strip renders the 7 days of the current week; today highlighted; past day with content shows ring.
- [ ] Tapping a past day with content opens that day's reader (re-read mode); past unstarted day is no-op.
- [ ] Calendar opens via streak pill; 2 months render inline; tap rules same as week strip.
- [ ] Subtitle and `i` icon both open the same tooltip; tooltip dismissable via `X` and outside tap.
- [ ] Light Points badge displays current balance (multi-digit handled); tap opens Available Points page.
- [ ] Each session card supports collapsed/expanded states; only one expanded at a time; collapsed shows `DONE` chip when complete.
- [ ] Reading or listening to a session marks it complete and updates `dayProgressPercent` immediately.
- [ ] Completing the last session triggers Day-Complete; `Continue` returns to Today landing with all cards `DONE` and streak +1.
- [ ] When today is locked behind reminder, F.1 empty state renders with correct `<Weekday>, <DD MMMM>` interpolation and live `<HH:mm>`.
- [ ] `Change reminder` opens bottom sheet; time chip opens Material 3 TimePicker; `Update reminder` persists and dismisses.
- [ ] Exclusive Deal banner countdown ticks down in real time; tap opens paywall; CTA `Try for Free` triggers Play Billing.
- [ ] Profile Drawer slides in from left; pre-fills nickname, age range, denomination from server `User` payload.
- [ ] Tooltip overlay does not block interaction with the rest of the screen (verify `Popup` `properties.focusable` setting).
- [ ] All currency rendered in `₫` with consistent thousands separator (one of `,` or `.` — choose and stick).
- [ ] Bottom nav stays visible on Today landing (all variants); hides on full-screen overlays (Calendar, Paywall, Available Points, Session Reader, Day-Complete) and on drawer.

---

## 9. References

- **Raw observations** (per-screen bounds & literals): `today_observations.md`
- **Flow spec** (block-by-block transitions, state machines, QA bugs): `today_spec.md`
- **Cross-cluster specs**:
  - Onboarding (initial reminder setup, Day-Complete reuse): `onboarding_feature_spec.md`
  - Chat (entry from "Chat to learn more"): `chat_feature_spec.md`
  - Community / Bible / Explore (siblings in bottom nav): `community_feature_spec.md`, (Bible/Explore not yet specced)
- **Screenshots**: `spec/screens/today/screen_*.png`
- **UI dumps**: `spec/ui_dumps/today/screen_*.xml`