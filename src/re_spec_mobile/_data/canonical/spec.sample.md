---
feature: today
layer: flow
anchor: today/flow/root
title: BibleChat — Today Tab Flow Specification
last_updated: '2026-04-20'
app_version: 4.3.10
device: Pixel
package: com.basmo.BibleChat
status: approved
blocks:
- id: today/block/a
  letter: A
  name: Today Landing
  section_line: 62
  screens: []
- id: today/block/b
  letter: B
  name: Profile Drawer
  section_line: 121
  screens: []
- id: today/block/c
  letter: C
  name: '"Explore" Overlay (sparkle icon)'
  section_line: 143
  screens: []
- id: today/block/d
  letter: D
  name: Calendar (full-month grid)
  section_line: 163
  screens: []
- id: today/block/e
  letter: E
  name: Subtitle / Info Tooltip
  section_line: 183
  screens: []
- id: today/block/f
  letter: F
  name: Day-State Empty Screens
  section_line: 203
  screens: []
- id: today/block/g
  letter: G
  name: Reminder Editor
  section_line: 235
  screens: []
- id: today/block/h
  letter: H
  name: Today-tab Paywall (Exclusive Deal)
  section_line: 269
  screens: []
- id: today/block/i
  letter: I
  name: Session Readers (Verse / Devotional / Prayer)
  section_line: 295
  screens: []
- id: today/block/j
  letter: J
  name: Day-Complete Celebration
  section_line: 327
  screens: []
- id: today/block/k
  letter: K
  name: Peace and Calm Bottom Sheet
  section_line: 349
  screens: []
- id: today/block/l
  letter: L
  name: Available Points (Light Points store)
  section_line: 367
  screens: []
nav_edges: []
related:
- today/implementation/root
- today/observations/root
---

# BibleChat — Today Tab Flow Specification

> **⚠️ CANONICAL — REFERENCE STRUCTURE, KHÔNG PHẢI TEMPLATE NGÔN NGỮ.**
> File này gốc từ project BibleChat (gen trước khi enforce policy "output
> tiếng Việt"). Mọi spec MỚI phải viết bằng tiếng Việt với technical term
> tiếng Anh — xem `docs/I18N_GLOSSARY.md`.
>
> Khi reference file này, agent `spec-writer` PHẢI mimic:
> - Frontmatter shape (blocks, nav_edges, states, related)
> - Body section ordering (1. Tổng Quan → 2. Hard facts → 3+. Block A/B/...
>   → N. Navigation graph → N+1. State machine → N+2. Bug / quirk)
> - Anchor marker `{#feature/block/x}` sau heading
> - Mermaid `flowchart TD` cho nav graph, `LR` cho state machine
> - Bảng interaction 3 cột (Tap target | Centre | Result)
>
> KHÔNG mimic:
> - Prose paragraph bằng tiếng Anh — luôn dịch sang tiếng Việt
> - Section heading "## 1. Overview" → ghi "## 1. Tổng Quan"
> - Section heading "## N. Observed bugs / quirks" → ghi "## N. Bug / quirk đã quan sát"

**Package**: `com.basmo.BibleChat`
**App version**: `4.3.10`
**Activity**: `com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity` → fragment `navigation_daily_journey`
**Device tested**: Pixel (`8A5X0M2H8`), Android, locale `vi-VN`
**Method**: every screen captured via `adb uiautomator dump` + `screencap`; every literal below is transcribed verbatim. See `today_observations.md` for raw per-screen tables.

---

## 1. Overview

The Today tab is the **post-onboarding daily-engagement hub** of BibleChat. It is the default landing tab after onboarding completes and after every cold start (the tab `navigation_daily_journey` ships pre-selected, with its `large_label` style applied while siblings remain `small_label`).

Once visible, Today is **not a forced linear flow** — unlike onboarding, the user can freely tap anywhere, skip cards, switch dates, or leave for another tab. The "force" of Today is implicit: you can't progress beyond the day-complete celebration unless the four content cards have been opened.

**Functional blocks** (17 distinct UI states across 9 functional groups):

| # | Block | States | Purpose |
|---|---|---|---|
| A | Today landing — sticky header + scrollable cards | screen_01_a, _b | Daily plan dashboard |
| B | Profile drawer (left slide-in) | screen_02_avatar_a–e | Account, settings, payment, language |
| C | "Explore" overlay (sparkle icon) | screen_03_sparkle_a–d | Feature directory by category |
| D | Calendar (full-month grid) | screen_04_streak, _b, _c | Date picker into past sessions |
| E | Subtitle/info tooltip | screen_05_subtitle, screen_14_info | Personalisation explainer |
| F | Day-state empty screens | screen_06_day_today, _future, _past | "Not quite time yet" gates |
| G | Reminder editor (sheet + Material time picker) | screen_07_change_reminder, _time_picker | Per-day reminder schedule |
| H | Today-tab paywall (Exclusive Deal) | screen_08_exclusive_deal, _b | 7-day-trial / 12-month upsell |
| I | Session readers — Verse / Devotional / Prayer (Read + Listen + Chat) | screen_09 / 10 / 11 family | Daily content consumption |
| J | Day-Complete celebration | screen_12_day_complete | Streak gamification |
| K | Peace and Calm bottom sheet | screen_13_peace | Free-text confession/release |
| L | Available Points (Light Points store) | screen_15_badge_a–e | Currency, rewards, IAP |

Total walk-through length observed in this session: **17 distinct UI states** + 30+ scroll segments. Header / day strip / progress bar are sticky across all variants of the landing.

---

## 2. Hard facts before anything else

- **Default tab on cold launch** = Today (`navigation_daily_journey`). Confirmed by `mFocusedApp` = DashboardActivity with the Today fragment rendered.
- **Per-day plan model**: each calendar day has its own *theme* (subtitle string), four content cards, and a 0–100% progress bar. Themes observed:
  - Apr 15 → `Starting Your Journey`
  - Apr 16 → `Understanding God's Love`
  - Apr 17 → `Exploring Scripture`
- **Time-gating**: today's plan is locked behind the **reminder time** (default `09:00`, all weekdays). The Today tab on `today_date` displays a "Not quite time yet — Check back Thursday, 16 April for your Daily Plan session" empty state until the reminder fires; the user can re-edit the time.
- **Past unstarted days are non-interactive**: tapping a dimmed past day in the week strip or in the calendar grid does nothing; only days that have at least one completed session (or today + future) navigate.
- **Single expanded card invariant**: only one card in the cards stack can be expanded at a time. Tapping a collapsed card auto-collapses its sibling.
- **Bottom-nav constants** (resource-ids):
  - `navigation_home` → Chat
  - `live_prayers_screen` → Community
  - `navigation_daily_journey` → **Today**
  - `bible_screen_navbar` → Bible
  - `navigation_new_study` → Explore
- **Currency**: `₫` (VND) for all paid items (paywall, Light Points purchase tiers, Live Wallpaper).
- **Localization**: static strings are **English** even on a `vi-VN` device; only system-managed strings (back button a11y, sheet drag-handle desc) and price formatting respect locale. Number-thousands separator inside Light Points page is **inconsistent** (`1.000` vs `30,000`).
- **Sticky header** = `App Bar Layout` style sticky region. Everything from the avatar row down to `Progress today / 75%` does not scroll.
- **Compose vs XML**: the cards stack and the session reader produce semantic Compose nodes (no `resource-id`, mostly anonymous `View` containers). The bottom navigation is the Material `BottomNavigationView` (real `resource-id`s). The tooltip overlay (Screen 05) is rendered through a Compose Popup that is **invisible to `uiautomator dump`** — only the screenshot proves it exists.
- **One-shot vs scrollable cards**: Verse / Devotional / Prayer expand-collapse; Peace and Calm is a single-tap that always opens a bottom sheet.

---

## 3. Block A — Today Landing

![Today landing — top viewport](../../screens/today/screen_01_a.png)
![Today landing — bottom viewport](../../screens/today/screen_01_b.png)

**Entry**: tap `Today` in bottom-nav, or cold-launch the app post-onboarding.

### Sticky header zone — `[0,93][1080,778]`

| Region | Element | Centre | Action |
|---|---|---|---|
| Top row | Avatar (initial of nickname, e.g. `F`) | (118, 213) | Open Profile drawer (Block B) |
| Top row | Title `Today's Journey` (or `Apr 15's Journey`) | (456, 158) | (no-op — pure text) |
| Top row | Sparkle / AI icon | (752, 159) | Open "Explore" overlay (Block C) |
| Top row | Streak/calendar pill (fire icon + count, e.g. `0` / `1`) | (921, 159) | Open Calendar (Block D) |
| Sub row | Subtitle `Starting Your Journey` (theme name, dynamic per day) | (441, 284) | Show "Tailored just for you!" tooltip (Block E) |
| Sub row | `i` info icon | (733, 284) | Same tooltip as above |
| Sub row | Light Points badge (yellow circle + count) | (950, 284) | Open Available Points / Light Points store (Block L) |
| Week strip | 7 day cells `M T W T F S S` with current week numbers | per cell | Switch the displayed day if it has content; otherwise no-op |
| Progress | `Progress today` label + numeric percent | n/a | Visual only (no tap target) |

The week strip is **not horizontally scrollable** (a horizontal swipe on it produces no change). Date navigation across weeks happens through the Calendar.

### Cards zone — scroll area `[0, ~770][1080, 1808]`

The cards area renders a fixed-order vertical list:

1. **Exclusive Deal banner** (countdown card)
2. **YOUR VERSE** (1 MIN, optional `DONE` chip)
3. **PERSONALIZED DEVOTIONAL** (3 MIN, optional `DONE` chip)
4. **PRAYER OF THE DAY** (2 MIN, optional `DONE` chip)
5. **PEACE AND CALM** (one-shot, no duration label)

Each of cards 2–4 has two states:

- **Collapsed**: header strip only (type · duration · DONE chip on right · chevron on right when not done).
- **Expanded**: shows title, optional tag pills, and `Listen` + `Read` buttons. Card background switches from solid dark to a themed image (ocean for Verse, hands for Devotional/Prayer).

Tapping a collapsed card expands it and collapses any other expanded card (single-expansion invariant). The expanded card is visually larger; the cards below shift down accordingly.

### Transitions

- Tap **Exclusive Deal** → Today-tab Paywall (Block H).
- Tap card body → toggle expand/collapse.
- Tap **Listen** on a card → enter Block I in audio mode (auto-play).
- Tap **Read** on a card → enter Block I in text mode.
- Tap **PEACE AND CALM** → Block K (bottom sheet).

### State variants of the landing (depending on selected day)

| Day kind | Header subtitle | Cards zone content |
|---|---|---|
| Today **before** reminder time | dynamic theme (e.g. `Understanding God's Love`) | Empty state with calendar+clock illustration, "Not quite time yet — Check back Thursday, 16 April for your Daily Plan session", "Your reminder is set for 09:00 — Change reminder" link |
| Today **after** reminder time / past completed day | dynamic theme | Five content cards as above |
| Future day | dynamic theme | Empty state with calendar+clock illustration, "Not quite time yet — Check back tomorrow for your Daily Plan session" (no Change-reminder link) |
| Past unstarted day | dynamic theme | Same empty state — but the day cell was never reached because it is not interactive in the strip/calendar |

---

## 4. Block B — Profile Drawer

![Profile drawer](../../screens/today/screen_02_avatar.png)

**Entry**: tap avatar `F`. **Dismiss**: `KEYCODE_BACK` or tap right-edge close zone (`Close navigation menu` at `[990,0][1080,2028]`).

A vertical-scroll drawer covering the left ~92% of the screen. Sections (top to bottom):

1. **Profile header** — avatar placeholder, editable nickname EditText (`Faithfulness Traveler 3576`), Current Streak (`0`), Longest Streak (`0`).
2. **Friends** — `Friends` row with `You have 0 friends` and chevron.
3. **Limited Special Offer** — `Exclusive Deal` countdown card (mirrors the one on Today landing; same global timer).
4. **My Space** — `Explore all features`, `Limit screen time`, `Personalize your conversations`, `Widget selection`, `Daily Bible Verse Wallpaper` (Material switch).
5. **Personal Details** — `Age range` (`55+`, value from quiz), `Email` (placeholder `Write here…`), `Denomination` (`Pentecostal`, value from quiz), `Church` (placeholder `Write here…`).
6. **Subscription** — `Membership` (`Free`), `Upgrade to Premium`, `Restore purchases`.
7. **About** — `Contact us`, `Terms of use`, `Privacy policy`.
8. **Account** — `Link account data` (Google), `Manage your reminders`, `Change language` (`English`).
9. **Footer** — `App version: 4.3.10`, `UID:` (empty for guest user).

Most rows were not deep-tapped in this session; their destinations are inferred from labels and out of scope for the Today spec.

---

## 5. Block C — "Explore" Overlay (sparkle icon)

![Explore overlay](../../screens/today/screen_03_sparkle.png)

**Entry**: tap sparkle icon (top-centre of header).

A full-screen overlay with `Explore — Discover everything BibleChat has to offer` and a horizontal chip filter (`Personalize` selected · `Bible Study` · `Community` · `Journey`). Below, a 2-column grid grouped by section:

| Section | Items |
|---|---|
| `PERSONALIZE` | Lockscreen · App Widget · Affirmations |
| `BIBLE STUDY` | Study Plans · Chat · Voice Chat · Reading · Bible Stories · Animations · Kids' Stories |
| `COMMUNITY` | Groups · Friends · Live Prayer · My Prayers · World Events |
| `JOURNEY` | Daily Plan · Calendar · The Bible · Screen Time · Meditation |
| `LEISURE` | Word Guesser · Bible Trivia |

This overlay aliases features that are also reachable through the bottom-nav tabs (Bible, Chat, Community, Explore) and the profile drawer. **Treat it as a global directory, not a Today-specific feature.**

---

## 6. Block D — Calendar (full-month grid)

![Calendar grid](../../screens/today/screen_04_streak.png)

**Entry**: tap streak/calendar pill (top-right of header).

Full-screen calendar:
- Title `April 2026` (current month, no chevrons to paginate; next month renders inline below).
- Close `X` (top-right).
- Day-of-week header `MON TUE WED THU FRI SAT SUN`.
- Two month grids visible after scroll (`April`, `May`).
- Day cells show the day number; today is filled, the previous day with completed sessions has a yellow ring (75% completion arc).

**Tap rules**:
- Day with completed sessions → opens the session reader for that day's verse (re-read mode).
- Today / future → opens the Today landing in the corresponding day state (cards or empty state).
- Past **unstarted** day → silent no-op.

---

## 7. Block E — Subtitle / Info Tooltip

![Subtitle tooltip](../../screens/today/screen_05_subtitle.png)

**Entry**: tap the subtitle text or the `i` icon next to it.

A small frosted overlay anchored above the progress bar:

| Line | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close | `X` (top-right of the tooltip itself) |

**Critical note**: this overlay is **rendered outside the uiautomator-visible composition tree** — its text nodes are absent from `screen_05_subtitle.xml` despite being clearly visible in the screenshot. Likely Compose `Popup` / `Window` overlay. Any UI test asserting on this string must use **screenshot OCR** or accessibility services (TalkBack), not `uiautomator`.

Dismiss: tap the small `X` or tap outside.

---

## 8. Block F — Day-State Empty Screens

Three sub-states are observed, all sharing the same `Calendar+clock` icon centred above the text block:

### F.1 — Today, locked behind reminder

![Today (Apr 16) locked](../../screens/today/screen_06_day_today.png)

| Element | Text |
|---|---|
| Headline | `Not quite time yet.\nCheck back Thursday, 16 April for your Daily Plan session` |
| Sub | `Your reminder is set for 09:00.\n Would you like to update it?` |
| Link | `Change reminder` (yellow) → opens Block G |

Progress bar shows `0%`.

### F.2 — Future day

![Future day (Apr 17)](../../screens/today/screen_06_day_future.png)

| Element | Text |
|---|---|
| Headline | `Not quite time yet.\nCheck back tomorrow for your Daily Plan session` |

No `Change reminder` link (no actionable nudge for future dates).

### F.3 — Past unstarted day

The cell is not navigable, so this state is technically unreachable from the strip; observed via attempted (unsuccessful) tap on Apr 13 / Apr 14.

---

## 9. Block G — Reminder Editor

### G.1 — Reminder bottom sheet

![Reminder sheet](../../screens/today/screen_07_change_reminder.png)

| Element | Text |
|---|---|
| Drag-handle hit-zone | `[44,110][1036,242]` (no visible label) |
| Close `X` | top-right |
| Bell illustration | (icon only) |
| Headline | `Connect with God Daily` |
| Body | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Time-chip label | `We'll remind you at...` |
| Time chip | `09:00` (with chevron) |
| Days label | `On these days` |
| Day toggles | seven cells `M T W T F S S`, each with a checkable circle |
| CTA | `Update reminder` (yellow) |

### G.2 — Material 3 Time Picker

![Time picker](../../screens/today/screen_07_time_picker.png)

Standard Material clock:
- Header: `09 : 00`, hour active.
- Clock face: 12-h numerals on inner ring (12 1 2 ... 11), 24-h numerals on outer ring (13 14 ... 24).
- Selected hand → 9 / 21.

Underlying sheet remains visible behind the picker.

Dismiss: `KEYCODE_BACK` closes the picker; second back closes the sheet.

---

## 10. Block H — Today-tab Paywall (Exclusive Deal)

![Paywall — top](../../screens/today/screen_08_exclusive_deal.png)
![Paywall — bottom](../../screens/today/screen_08_exclusive_deal_b.png)

**Entry**: tap the `Exclusive Deal` banner (Today landing OR Profile drawer; both share the same global countdown).

| Section | Text |
|---|---|
| Close | `X` (top-left) |
| Headline | `Never Miss a Moment of Faith` |
| Bullets | `Widget with Personalized Daily Verses` · `Bring the Bible to your Home Screen` · `Personalized Audio Daily Devotionals` |
| Toggle | `I want to try the app for free` (Material switch ON by default) |
| Plan A (selected) | `7 Days Free Trial` · badge `SAVE 36%` · `Then ~~158549.98~~ ₫105,000 per week.\nNo payment now` |
| Plan B label | `Best Price of the Year` |
| Plan B card | `12-Month Access` · `Billed yearly at ₫880,000` |
| Disclaimer | `Cancel anytime before April 23 2026.\nNo risks, no charges.` |
| CTA | `Try for Free →` (yellow) |
| Footer | `Terms of use` · `Privacy policy` · `Restore` |

Pricing format note: the strikethrough price `158549.98` lacks thousands separators (likely a raw `priceMicros / 1_000_000` conversion). The promo line uses `₫105,000` (correctly formatted). This inconsistency is a known UI bug surface; flag it for QA.

The countdown timer is **global** (not per-tap) and is also displayed on the Today landing and the Profile drawer.

---

## 11. Block I — Session Readers (Verse / Devotional / Prayer)

All three readers share a unified shell. They differ only in the body content and bottom CTA pill text.

### I.1 — Common shell

| Region | Element |
|---|---|
| Top | Back arrow (left) · `Your Journey` (centre title) · `X` close (right) |
| Below top | `Progress for <Mon DD>` label + percent (yellow) |
| Body header | Card type label (e.g. `YOUR VERSE` / `PERSONALIZED DEVOTIONAL` / `PRAYER OF THE DAY`) + duration (`1 MIN` / `3 MIN` / `2 MIN`) |
| Body | Verse text or devotional/prayer paragraphs (scrollable when long) |
| Body footer | Citation in yellow (e.g. `Isaiah 41:10`) — present on Verse / Devotional |
| Bottom action bar | Left: thumbs-down icon · Middle: `Chat to learn more` button · Right: `→` arrow OR `Done` pill |

The right slot is `→` for *intermediate* sessions and `Done` for the *last incomplete* session of the day. Tapping it advances or finalises and triggers Block J on completion.

### I.2 — Read vs Listen

`Read` opens the shell with text rendered statically. `Listen` opens the same shell but the bottom action bar is replaced by an **audio toolbar**:

| Element | Detail |
|---|---|
| Progress bar | `00:02 / 00:09` (track length is short for a 1-MIN verse) |
| Buttons | Share · Previous · Play/Pause · Next · Replay |

### I.3 — "Chat to learn more" → Chat

Navigates into the Chat feature cluster (`chat_feature_spec.md`) with the verse/devotional/prayer text **pre-loaded as a context bubble** in the conversation. The bubble exposes thumbs-up / thumbs-down / `Copy` / `Share`. The Chat header shows the back arrow, `Chat` title, a `?5` help-with-credits-badge, and a font-size icon. Composer is at the bottom.

---

## 12. Block J — Day-Complete Celebration

![Day Complete](../../screens/today/screen_12_day_complete.png)

**Entry**: tap `Done` on the last incomplete session of the day (here: Prayer Reader after Verse + Devotional were already done).

| Element | Text |
|---|---|
| Fire illustration | (centred) |
| Counter | `1` (large yellow) |
| Label | `day streak` |
| 3-dot streak progress | dot 1 filled · dot 2 outline · dot 3 outline |
| Sub | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` |
| Mini week strip | `Mo 13 · Tu 14 · We 🔥 · Th 16 · Fr 17 · Sa 18 · Su` |
| CTA | `Continue` |

Tapping `Continue` returns to the Today landing for the same day, now with `100%` progress, the streak pill incremented, all four cards `DONE`.

This is the **same screen** used in the onboarding's "Block N" (per `onboarding_spec.md`) — the 33-free-questions promise is reused outside onboarding, confirming it is a recurring milestone reward, not just a first-day artefact.

---

## 13. Block K — Peace and Calm Bottom Sheet

![Peace and Calm sheet](../../screens/today/screen_13_peace.png)

**Entry**: tap the `PEACE AND CALM` card.

| Element | Text |
|---|---|
| Top hit-zone | `desc=Close sheet` |
| Headline | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Privacy note | `Your privacy is guaranteed and your information will remain confidential.` |
| Input | `EditText` with placeholder `Describe here` |
| CTA | `Continue` (greyed/disabled until input has content) |

Outcome of `Continue` not tested in this session (would require submitting actual content). Likely opens a moment-of-grace screen or pipes input into the AI chat — left to operator.

---

## 14. Block L — Available Points (Light Points store)

![Available Points — top](../../screens/today/screen_15_badge.png)
![Available Points — bottom](../../screens/today/screen_15_badge_e.png)

**Entry**: tap the Light Points badge (the small yellow circle + number at top-right of the header).

Header: `Available Points : ⊙ <balance>` (here 100). Sections (top → bottom):

| Section | Item · cost |
|---|---|
| `Premium` | `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `5 Questions` · `⊙ 250` ; `25 Questions` · `⊙ 1000` ; `100 Questions` · `⊙ 2500` |
| `Light Points` (purchase tiers) | `100 Light Points` · `₫30,000` ; `500 Light Points` · `₫108,000` ; `1.000 Light Points` · `₫198,000` ; `2.500 Light Points` · `₫391,000` ; `10.000 Light Points` · `₫1,300,000` |
| `Study Unlocks` | 20 study titles each at `⊙ 250` (full list in `today_observations.md`) |
| `Coming Soon` | `Special Study` |

### Currency model

- **Light Points** is the in-app virtual currency.
- Earned: per completed session (precise rate not measured), per streak milestone (Day-Complete promises bonus questions).
- Purchased: 5 tiers from `100` to `10.000` priced in VND.
- Spent: unlock chat-question quotas, premium month, wallpapers, study packs.

The `?5` badge in the Chat header surfaces the *current available chat questions* (from `Chat Unlocks` purchases + Day-Complete bonuses + the 33 promised at 3-day streak). It is **not** a Light Points balance — those are two separate counters.

---

## 15. Navigation graph (Today-rooted)

```
Today landing (Block A)
├── Avatar (118,213)            → Profile Drawer (B)
├── Sparkle (752,159)           → Explore overlay (C)
├── Streak pill (921,159)       → Calendar (D)
│       └── Day with content    → Verse Session Reader (I.1, read-only)
├── Subtitle / info (441,284)   → Tooltip (E)
├── Light Points badge (950,284)→ Available Points (L)
├── Week-strip day cell
│   ├── Day with content        → switches landing to that day (still Block A, different content)
│   ├── Today                   → Block A.empty (F.1)
│   ├── Future day              → Block A.empty (F.2)
│   └── Past unstarted          → no-op
├── Empty-state Change reminder → Reminder sheet (G.1)
│                                  └── Time chip → Material time picker (G.2)
├── Exclusive Deal banner       → Paywall (H)
├── Verse / Devotional / Prayer card body
│   ├── (collapsed → expanded)  → no nav
│   ├── Listen                  → Reader audio mode (I.2)
│   ├── Read                    → Reader text mode (I.1/I.2)
│   │       └── Chat to learn   → Chat conversation (cross-cluster)
│   │       └── → / Done        → next session OR Day-Complete (J)
└── Peace and Calm card         → Bottom sheet (K)
                                  └── Continue (gated by input)  → not tested
```

Dismissal pattern is consistent: `KEYCODE_BACK` closes overlays/sheets/dialogs by one level; the `X` icon exists on full-screen overlays (Calendar, Paywall, Available Points, Session Reader) and dismisses them outright.

---

## 16. State machine — daily progress

```
[ Day not yet unlocked ] ── reminder fires at 09:00 ──▶ [ Cards visible, 0% ]
                                                        │ (Verse Read OR Listen)
[ Cards visible, 25% ] ◀──────────────────────────────┘
       │ (Devotional Read OR Listen)
       ▼
[ 50% ]
       │ (Prayer Read OR Listen)
       ▼
[ 75% ]
       │ (final session — order may differ; in this capture order was Verse → Devotional → Prayer)
       ▼
[ 100% ] ──────▶ [ Day-Complete celebration (Block J) ] ── Continue ─▶ [ Cards all DONE, streak +1, points +N ]
```

Notes:
- The **first** open of any session marks it as `DONE`; it is unclear whether `Listen` requires play-through or any open suffices (in this session, opening `Listen` was enough to register completion).
- The **`PEACE AND CALM`** card is **not part of the day-progress percent**: completing the other three already drove the bar to `100%`, so Peace and Calm appears to be a side-channel exercise (free-text journal, not a counted session).
- The exact percent step per session was 25% × 4? No — observed jumps were `75% → 100%` after Prayer alone, suggesting the bar already reflected Verse + Devotional `DONE` from before this capture (the user state showed both `DONE` chips on entry). The denominator is **3 sessions = 100%**, not 4.

---

## 17. Observed bugs / quirks (for QA backlog)

1. **Paywall price formatting** — strikethrough Plan A price renders as `158549.98` without thousands separators while the promo line below uses `₫105,000`. Inconsistent number formatter between the two prices.
2. **Light Points tier formatting** — purchase tiers use `1.000`, `2.500`, `10.000` (dot as thousands sep, vi-VN style) while the cost column uses `30,000`, `1,300,000` (comma). Same screen, two formats.
3. **Tooltip invisible to uiautomator** — the "Tailored just for you!" overlay is rendered through a Compose Popup that escapes the dump tree. Will break any espresso/uiautomator test that asserts on its strings.
4. **Time-of-day vs reminder enforcement** — at capture time `12:19` (well after the `09:00` reminder), Today (Apr 16) was still locked. The lock appears to be tied to **whether the reminder notification was acknowledged**, not the wall-clock crossing the reminder time. Worth confirming with the engineer.
5. **"Past unstarted" silent no-op** — tapping a dim past day (Apr 13 / Apr 14) gives zero feedback. Consider a toast or a tooltip explaining why the day is non-interactive.
6. **`UID:` empty in profile drawer footer** — the field renders the label but no value. For guest-mode users this should either be hidden or filled with the local install id for support purposes.