---
feature: today
layer: observations
anchor: today/observations/root
title: BibleChat — Today Tab Screen-by-Screen Observations
last_updated: '2026-04-20'
app_version: 4.3.10
device: 8A5X0M2H8
screens:
- anchor: today/screen/today_landing
  label: Today Landing (Active Day = Apr 15, 75% → 100%)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_01_today_landing.png
  dump_file: spec/ui_dumps/today/screen_01_today_landing.json
  section_line: 12
- anchor: today/screen/profile_drawer
  label: Profile Drawer (slide-in from left)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_02_profile_drawer.png
  dump_file: spec/ui_dumps/today/screen_02_profile_drawer.json
  section_line: 113
- anchor: today/screen/explore_overlay
  label: '"Explore" Overlay (sparkle icon)'
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_03_explore_overlay.png
  dump_file: spec/ui_dumps/today/screen_03_explore_overlay.json
  section_line: 167
- anchor: today/screen/calendar
  label: Calendar (full-month grid)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_04_calendar.png
  dump_file: spec/ui_dumps/today/screen_04_calendar.json
  section_line: 201
- anchor: today/screen/subtitle_info_tooltip
  label: Subtitle / Info tooltip
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_05_subtitle_info_tooltip.png
  dump_file: spec/ui_dumps/today/screen_05_subtitle_info_tooltip.json
  section_line: 236
- anchor: today/screen/today_empty_states
  label: Today Empty States (date-dependent)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_06_today_empty_states.png
  dump_file: spec/ui_dumps/today/screen_06_today_empty_states.json
  section_line: 258
- anchor: today/screen/change_reminder_bottom_sheet_time_picker
  label: Change Reminder Bottom Sheet + Time Picker
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_07_change_reminder_bottom_sheet_time_picker.png
  dump_file: spec/ui_dumps/today/screen_07_change_reminder_bottom_sheet_time_picker.json
  section_line: 298
- anchor: today/screen/today_tab_paywall
  label: Today-tab Paywall (Exclusive Deal)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_08_today_tab_paywall.png
  dump_file: spec/ui_dumps/today/screen_08_today_tab_paywall.json
  section_line: 333
- anchor: today/screen/verse_session_reader
  label: Verse Session Reader
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_09_verse_session_reader.png
  dump_file: spec/ui_dumps/today/screen_09_verse_session_reader.json
  section_line: 364
- anchor: today/screen/devotional_reader
  label: Devotional Reader
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_10_devotional_reader.png
  dump_file: spec/ui_dumps/today/screen_10_devotional_reader.json
  section_line: 428
- anchor: today/screen/prayer_reader
  label: Prayer Reader
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_11_prayer_reader.png
  dump_file: spec/ui_dumps/today/screen_11_prayer_reader.json
  section_line: 465
- anchor: today/screen/day_complete_celebration
  label: Day-Complete Celebration
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_12_day_complete_celebration.png
  dump_file: spec/ui_dumps/today/screen_12_day_complete_celebration.json
  section_line: 495
- anchor: today/screen/peace_and_calm_bottom_sheet
  label: Peace and Calm Bottom Sheet
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_13_peace_and_calm_bottom_sheet.png
  dump_file: spec/ui_dumps/today/screen_13_peace_and_calm_bottom_sheet.json
  section_line: 517
- anchor: today/screen/available_points
  label: Available Points (Light Points store)
  activity: com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity
  hash: TODO
  capture_file: spec/screens/today/screen_15_available_points.png
  dump_file: spec/ui_dumps/today/screen_15_available_points.json
  section_line: 537
related:
- today/flow/root
- today/implementation/root
---

# BibleChat — Today Tab Screen-by-Screen Observations

**Target package**: `com.basmo.BibleChat`
**App version**: `4.3.10`
**Device**: 8A5X0M2H8 (Pixel, Android — `vi-VN` locale)
**Method**: `adb shell uiautomator dump` + `screencap`, captured on 2026-04-16 ≈ 12:01–12:36 GMT+7.
**Rule**: every line below transcribed from a UI dump or its screenshot — nothing inferred.
**State at capture**: guest user "Faithfulness Traveler 3576", onboarding completed, day 15 (Apr 15) sessions in progress (75% → 100% during the session), today (Apr 16) plan still locked behind 09:00 reminder.

---

## Screen 01 — Today Landing (Active Day = Apr 15, 75% → 100%)

- **Dump**: `spec/ui_dumps/today/screen_01_a.xml` (top), `screen_01_b.xml` (after one swipe)
- **Screenshot**: `spec/screens/today/screen_01_a.png`, `screen_01_b.png`
- **Activity**: `com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity`

### Layout

The screen has a **sticky header block** (header + week strip + progress bar) and a **scrollable cards area** below. Bounds compared across `_a` and `_b` confirm the header (`Today's Journey`, week strip, `Progress today / 75%`) holds the same coordinates after scrolling — so it is sticky.

Viewport segments:

| Segment | Visible scrollable content |
|---|---|
| `_a` (top) | Exclusive Deal banner · YOUR VERSE (expanded) · PERSONALIZED DEVOTIONAL header (truncated bottom) |
| `_b` (after one swipe up of ~1000 px) | PERSONALIZED DEVOTIONAL (collapsed) · PRAYER OF THE DAY (collapsed) · PEACE AND CALM |

Further scroll attempts produced no new content → page bottom reached.

### Sticky header — visible elements (from `_a`)

| Element | Class | Bounds | Clickable | Text / desc |
|---|---|---|---|---|
| Avatar `F` (initial) | View > TextView | `[44,139][193,288]` | **yes** (container) | text `F` |
| Title | TextView | `[215,117][697,200]` | no | `Today's Journey` |
| Sparkle/AI icon | View | `[697,93][807,225]` | **yes** | (no text/desc) |
| Streak/calendar pill (left-half: fire icon) | View | `[807,93][1036,225]` | **yes** | text `0` (current streak count) |
| Subtitle | TextView | `[215,218][667,350]` | **yes** | `Starting Your Journey` |
| Info icon (i) | ImageView | `[667,218][799,350]` | **yes** | (no text/desc) |
| Light Points badge | View | `[874,218][1025,350]` | **yes** | text `3` + `0` (= "30") |
| Day cell — Mon 13 | View > TextView×2 | `[62,393][194,545]` | **yes** | `M` / `13` |
| Day cell — Tue 14 | View > TextView×2 | `[200,393][332,545]` | **yes** | `T` / `14` |
| Day cell — **Wed 15** (today, ring + dot) | View > TextView×2 | `[337,393][469,545]` | **yes** | `W` / `15` |
| Day cell — Thu 16 | View > TextView×2 | `[474,393][606,545]` | **yes** | `T` / `16` |
| Day cell — Fri 17 | View > TextView×2 | `[611,393][743,545]` | **yes** | `F` / `17` |
| Day cell — Sat 18 | View > TextView×2 | `[749,393][881,545]` | **yes** | `S` / `18` |
| Day cell — Sun 19 | View > TextView×2 | `[886,393][1018,545]` | **yes** | `S` / `19` |
| Progress label | TextView | `[44,623][506,707]` | no | `Progress today` |
| Progress percent | TextView | `[907,623][1036,707]` | no | `75%` |

### Scrollable cards — viewport `_a`

| Card | Bounds | Clickable container | Visible literals |
|---|---|---|---|
| Exclusive Deal banner | `[0,807][1080,1004]` | **yes** | `Exclusive Deal` · timer `23:58:20` (countdown, decreased to `23:36:01` over the session) |
| YOUR VERSE (expanded) | `[44,1021][1036,1681]` | **yes** | `YOUR VERSE` · `1 MIN` · `DONE` · `Isaiah 41:10` · tags `STRENGTH`, `COURAGE`, `SUPPORT` · `Listen` button `[88,1483][518,1637]` · `Read` button `[562,1483][992,1637]` |
| PERSONALIZED DEVOTIONAL (collapsed) | `[44,1715][1036,1847]` | **yes** | `PERSONALIZED DEVOTIONAL` · `3 MIN` · `DONE` |

### Scrollable cards — viewport `_b`

| Card | Bounds | Clickable container | Visible literals |
|---|---|---|---|
| PERSONALIZED DEVOTIONAL (collapsed) | `[44,776][1036,908]` | **yes** | `PERSONALIZED DEVOTIONAL` · `3 MIN` · `DONE` |
| PRAYER OF THE DAY (collapsed, chevron-down) | `[44,937][1036,1186]` | **yes** | `PRAYER OF THE DAY` · `2 MIN` (no `DONE`) |
| PEACE AND CALM (oneshot) | `[44,1217][1036,1454]` | **yes** | `PEACE AND CALM` · `When life's too loud, listen within` |

### Bottom navigation (constant across all main-app screens)

| Tab | Container | Bounds | resource-id | desc | State |
|---|---|---|---|---|---|
| Chat | FrameLayout | `[0,1808][216,2028]` | `navigation_home` | `Chat` | inactive (small label) |
| Community | FrameLayout | `[216,1808][432,2028]` | `live_prayers_screen` | `Community` | inactive |
| **Today** | FrameLayout | `[432,1808][648,2028]` | `navigation_daily_journey` | `Today` | **active** (large label) |
| Bible | FrameLayout | `[648,1808][864,2028]` | `bible_screen_navbar` | `Bible` | inactive |
| Explore | FrameLayout | `[864,1808][1080,2028]` | `navigation_new_study` | `Explore` | inactive |

### Observed behaviour

- Header sticky — bounds for avatar / title / week strip / progress bar are identical between `_a` and `_b`. Scroll affects only the cards area `[0, ~770][1080, 1808]`.
- Week strip shows current week (Mon 13 – Sun 19), **not horizontally scrollable** (a horizontal swipe `(800,460)→(200,460)` produced no change in the dump).
- The card with `chevron-down` (Prayer of the Day) is a per-card expand/collapse; tapping any card collapses sibling cards (only one expanded at a time — observed Verse↔Devotional↔Prayer toggling).
- After the Prayer Read flow completed, the progress jumped from `75%` to `100%` and the streak counter `0` became `1`.
- The Light Points badge text is constructed from two separate `TextView` nodes (e.g. `3` + `0` for "30", or `1` + `0` + `0` for "100").

### Transitions (from this screen)

| Tap target | Centre | Result |
|---|---|---|
| Avatar `F` | (118, 213) | Profile drawer slides from left (screen 02) |
| Sparkle icon | (752, 159) | "Explore" overlay (screen 03) |
| Streak/calendar pill (`0`/`1`) | (921, 159) | Calendar full-month grid (screen 04) |
| Subtitle `Starting Your Journey` | (441, 284) | "Tailored just for you!" tooltip overlay (screen 05) |
| Info `i` icon | (733, 284) | Same tooltip (screen 14_info) |
| Light Points badge `30` / `100` | (950, 284) | Available Points page (screen 15) |
| Week-strip day **with content** (`15`) | (403, 469) | View persists on that day; title becomes `Apr 15's Journey` |
| Week-strip day **today** (`16`) | (540, 469) | View resets to today; cards replaced by "Not quite time yet" empty state (screen 06_today) |
| Week-strip day **future** (`17`) | (677, 469) | Title `Apr 17's Journey`, subtitle `Exploring Scripture`, "Check back tomorrow" empty state (screen 06_future) |
| Week-strip day **past, never started** (`13`, `14`) | (130, 469) / (266, 469) | No navigation (silent no-op) |
| Exclusive Deal banner | (540, 905) | Paywall (screen 08) |
| YOUR VERSE card body | (540, 1100) | Card expand toggle (no navigation) |
| `Listen` button on Verse | (305, 1560) | Verse Reader with audio playback (screen 09_listen) |
| `Read` button on Verse | (777, 1560) | Verse Reader text view (screen 09_read) |
| PERSONALIZED DEVOTIONAL card body | (540, 1015) after _b scroll | Card expand toggle |
| `Read` on Devotional | (815, 1377) | Devotional Reader (screen 10_read) |
| PRAYER OF THE DAY card body | (540, 1100) after _b scroll | Card expand toggle |
| `Read` on Prayer | (815, 1497) | Prayer Reader (screen 11_read) — finishing it triggers Day Complete (screen 12) |
| PEACE AND CALM card | (540, 1430) | "Share an anxiety…" bottom sheet (screen 13) |
| Bottom-nav tab (Chat / Community / Bible / Explore) | per table | Navigates to that tab |

---

## Screen 02 — Profile Drawer (slide-in from left)

- **Dump**: `screen_02_avatar.xml` (top), `_b.xml`, `_c.xml`, `_d.xml`, `_e.xml`
- **Screenshot**: `screen_02_avatar.png`, `_b.png`, `_c.png`, `_d.png`, `_e.png`
- **Entry**: tap avatar `F` on Today header
- **Dismiss**: `KEYCODE_BACK` (verified) or tap right edge `[990,0][1080,2028]` (`desc=Close navigation menu`)

### Layout

A drawer covering the left ~92% of the screen (right `[990,1080]` is the dimmed close zone). Entire content vertically scrollable. Bottom nav is **not** visible while drawer is open.

### Sections (top to bottom, observed across `_a`–`_e`)

| Section | Item | Bounds (top capture) | Clickable | Text / value |
|---|---|---|---|---|
| **Header** | Avatar (placeholder person glyph) | `[289,143][702,556]` | **yes** | (no text/desc) |
| | Name (editable) | `[125,625][866,757]` | **yes** (EditText) | `Faithfulness Traveler 3576` |
| | Current Streak | `[88,825][404,984]` | no | `0` + label `Current Streak` |
| | Longest Streak | `[561,825][880,984]` | no | `0` + label `Longest Streak` |
| **Friends** | Friends row | `[44,1072][946,1300]` | **yes** | icon · `Friends` · `You have 0 friends` · chevron-right |
| **Limited Special Offer** | Section header | `[88,1366][902,1449]` | no | `Limited Special Offer` |
| | Exclusive Deal banner | `[44,1493][946,1656]` | **yes** | `Exclusive Deal` · `23:50:51` (same countdown as Today landing) |
| **My Space** | Section header | `[88,1722][902,1805]` | no | `My Space` |
| | Explore all features | `[44,1849][946,2012]` | **yes** | `Explore all features` |
| | Limit screen time | (in `_b`) | **yes** | clock-restrict icon · `Limit screen time` |
| | Personalize your conversations | (in `_b`) | **yes** | sliders icon · `Personalize your conversations` |
| | Widget selection | (in `_b`) | **yes** | grid icon · `Widget selection` |
| | Daily Bible Verse Wallpaper | (in `_b`) | row + toggle (off, yellow) | `Daily Bible Verse Wallpaper` |
| **Personal Details** | Age range | (in `_c`) | **yes** | `Age range` · value `55+` |
| | Email | (in `_c`) | **yes** | `Email` · placeholder `Write here…` |
| | Denomination | (in `_c`) | **yes** | `Denomination` · value `Pentecostal` |
| | Church | (in `_c`) | **yes** | `Church` · placeholder `Write here…` |
| **Subscription** | Membership | (in `_c`/`_d`) | row | `Membership` · value `Free` |
| | Upgrade to Premium | (in `_d`) | **yes** | infinity icon · `Upgrade to Premium` |
| | Restore purchases | (in `_d`) | **yes** | dollar icon · `Restore purchases` |
| **About** | Contact us | (in `_d`/`_e`) | **yes** | mail icon · `Contact us` |
| | Terms of use | (in `_d`/`_e`) | **yes** | doc icon · `Terms of use` |
| | Privacy policy | (in `_d`/`_e`) | **yes** | doc icon · `Privacy policy` |
| **Account** | Link account data | (in `_e`) | **yes** | G icon · `Link account data` |
| | Manage your reminders | (in `_e`) | **yes** | clock icon · `Manage your reminders` |
| | Change language | (in `_e`) | **yes** | translate icon · `Change language` · value `English` |
| **Footer** | App version | (in `_e`) | no | `App version: 4.3.10` |
| | UID | (in `_e`) | no | `UID:` (empty value) |

### Notes

- The `Daily Bible Verse Wallpaper` row hosts a yellow Material Switch in the OFF state.
- Pre-filled `Age range = 55+` and `Denomination = Pentecostal` reflect onboarding quiz answers.
- Drawer is the **only** entry point observed for: Friends, Widget selection, Limit screen time, Personalize your conversations, Restore purchases, Link account data, Change language, Contact us, Terms, Privacy.
- "Manage your reminders" is a duplicate entry to the Today-tab "Change reminder" screen (screen 07).
- "Explore all features" item is presumed to navigate to the same overlay as the Today header sparkle (screen 03) — not verified by tap in this session.

---

## Screen 03 — "Explore" Overlay (sparkle icon)

- **Dump**: `screen_03_sparkle.xml`, `_b.xml`, `_c.xml`, `_d.xml`
- **Screenshot**: `screen_03_sparkle.png`, `_b.png`, `_c.png`, `_d.png`
- **Entry**: tap sparkle icon (top-centre of Today header)

### Layout

A full-screen overlay with `Explore` H1, a sub-line, a horizontal chip filter, then a scrollable grid of feature buttons grouped by category.

| Top elements | Text |
|---|---|
| H1 | `Explore` |
| Sub-line | `Discover everything BibleChat has to offer` |
| Filter chips (horizontal) | `Personalize` (selected, yellow) · `Bible Study` · `Community` · `Journey` |

### Sections (across `_a`–`_d`)

| Section header | Items (2-column grid) |
|---|---|
| `PERSONALIZE` | Lockscreen · App Widget · Affirmations |
| `BIBLE STUDY` | Study Plans · Chat · Voice Chat · Reading · Bible Stories · Animations · Kids' Stories |
| `COMMUNITY` | Groups · Friends · Live Prayer · My Prayers · World Events |
| `JOURNEY` | Daily Plan · Calendar · The Bible · Screen Time · Meditation |
| `LEISURE` | Word Guesser · Bible Trivia |

### Notes

- The header chips are visual filters but tapping them was not tested; the page renders all sections regardless.
- This same screen is presumed to be reachable from the bottom-nav `Explore` tab (`navigation_new_study`) — not verified in this session.
- Dismiss: `KEYCODE_BACK` returns to Today landing.

---

## Screen 04 — Calendar (full-month grid)

- **Dump**: `screen_04_streak.xml`, `_b.xml`, `_c.xml`
- **Screenshot**: `screen_04_streak.png`, `_b.png`, `_c.png`
- **Entry**: tap streak/calendar pill (top-right of Today header)

### Layout

| Element | Bounds | Text |
|---|---|---|
| Title | `[354,143][660,221]` | `April 2026` |
| Close `X` | `[937,132][1069,264]` | (no text/desc) |
| Day-of-week header row | `[22,275][1058,331]` | `MON` `TUE` `WED` `THU` `FRI` `SAT` `SUN` |
| Month label | `[44,463][162,529]` | `April` (yellow) |
| Day cells (April) | individual `View` per day, `[X,Y][X+132, Y+118]` | numbers `1`–`30` |
| Month label | (in `_c`) | `May` (yellow) |
| Day cells (May) | (in `_c`) | numbers `1`–`31` |

April grid (in `_a`):
- Row 1 (week of Mar 30): cells for `1`–`5` (`311,544][1035,662]`)
- Row 2: `6`–`12`
- Row 3: `13`–`19`
- Row 4: `20`–`26`
- Row 5: `27`–`30`

In `_a` and `_b`, day `15` displays a yellow ring (75% / streak indicator), day `16` is filled (today). `_c` (after scrolling) reveals all of May (full grid).

### Behaviour

- Day cells are individually `clickable=true`, but only days with content (e.g. `15`) navigate. Tapping `14` (past, never started) was a no-op.
- Tapping day `15` navigates to a session reader for that day's verse — i.e. it acts as a date-picker into the journey reader (screen 09 layout, but read-only review of completed content).
- Title shows current month only; no month-pagination chevrons observed. Scroll reveals next month inline (May follows April vertically).

---

## Screen 05 — Subtitle / Info tooltip

- **Dump**: `screen_05_subtitle.xml`, `screen_14_info.xml`
- **Screenshot**: `screen_05_subtitle.png`, `screen_14_info.png`
- **Entry**: tap subtitle text (`Starting Your Journey`) **or** the `i` icon next to it

### Observed (visual only — not in uiautomator dump)

A frosted overlay tooltip rendered above the Progress bar:

| Line | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close `X` | top-right of tooltip |

The tooltip's text nodes do **not** appear in `uiautomator dump`, indicating they are rendered via a Compose Popup/Overlay outside the main composition tree captured by the dump tool. They are visible in the screenshot only.

Dismiss: tap `X` (estimated centre `(957, 760)`) or tap outside.

---

## Screen 06 — Today Empty States (date-dependent)

### 06_today — Today (Apr 16) before first session

- **Dump**: `screen_06_day_today.xml`
- **Screenshot**: `screen_06_day_today.png`

Header sub-line changes to `Understanding God's Love` (Apr 16's theme). Day strip shows day `16` selected. Card area replaced by an empty state:

| Element | Bounds | Text |
|---|---|---|
| Calendar+clock empty illustration | (centre, ~`[440,920][640,1120]`) | (icon only) |
| Headline | `[66,1203][1014,1455]` | `Not quite time yet.\nCheck back Thursday, 16 April for your Daily Plan session` |
| Sub | `[72,1521][1009,1688]` | `Your reminder is set for 09:00.\n Would you like to update it?` |
| CTA (link) | `[290,1704][791,1836]` | `Change reminder` (yellow text) |

Progress bar on this state shows `0%`.

### 06_future — Future day (Apr 17)

- **Dump**: `screen_06_day_future.xml`
- **Screenshot**: `screen_06_day_future.png`

Same empty-state layout but headline becomes `Not quite time yet.\nCheck back tomorrow for your Daily Plan session`. Header subtitle becomes `Exploring Scripture`. Title `Apr 17's Journey`.

### 06_past_dim — Past unstarted day (Apr 13 / Apr 14)

- **Screenshot**: `screen_06_day_past.png`, `screen_06_day14.png`
- Behaviour: tapping these cells produced no navigation (page kept displaying previously selected day). They render dimmed in the strip.

### Subtitle themes observed

| Date | Theme |
|---|---|
| Apr 15 (Wed) | `Starting Your Journey` |
| Apr 16 (Thu) | `Understanding God's Love` |
| Apr 17 (Fri) | `Exploring Scripture` |

---

## Screen 07 — Change Reminder Bottom Sheet + Time Picker

### 07a — Change reminder sheet

- **Dump**: `screen_07_change_reminder.xml`
- **Screenshot**: `screen_07_change_reminder.png`
- **Entry**: tap `Change reminder` link in the empty-state (screen 06_today)

| Element | Bounds | Text |
|---|---|---|
| Top hit-area (drag handle) | `[44,110][1036,242]` | (no text) |
| Close `X` | `[915,110][1047,242]` | (no text) |
| Bell illustration | (centred top) | (icon only) |
| Title | `[187,627][894,708]` | `Connect with God Daily` |
| Body | `[88,774][992,999]` | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Time-picker chip label | `[277,1065][803,1140]` | `We'll remind you at...` |
| Time chip | `[292,1184][788,1327]` | `09:00` (with chevron) |
| Days label | `[367,1459][714,1534]` | `On these days` |
| Day toggles (M T W T F S S) | seven `View` cells `[66..1014, 1578..1767]` | each cell has letter on top and a circle row below; observed all 7 with check-mark fill |
| CTA | `[44,1821][1036,1984]` | `Update reminder` (yellow) |

### 07b — Time picker (Material clock)

- **Dump**: `screen_07_time_picker.xml`
- **Screenshot**: `screen_07_time_picker.png`
- **Entry**: tap the time chip (`09:00`) in the sheet

A Material 3 TimePicker dialog appears: large `09 : 00` numeric display with hour selector active (digit `9` highlighted), clock face below showing 12-h numerals (`12 1 2 ... 11`) on the inner ring and 24-h numerals (`13 14 15 ... 24`) on the outer ring. Highlighted hand pointing to `9 / 21`.

Bottom of the dialog continues to show the day toggles and `Update reminder` button (sheet remains underneath).

Dismiss: `KEYCODE_BACK` closes the time picker, second `KEYCODE_BACK` closes the bottom sheet.

---

## Screen 08 — Today-tab Paywall (Exclusive Deal)

- **Dump**: `screen_08_exclusive_deal.xml`, `_b.xml`
- **Screenshot**: `screen_08_exclusive_deal.png`, `_b.png`
- **Entry**: tap the `Exclusive Deal` banner (countdown card on Today landing or in the profile drawer)

Layout (full-screen, dove illustration in upper-right corner):

| Element | Text |
|---|---|
| Close `X` | top-left |
| Headline | `Never Miss a Moment of Faith` |
| Bullet 1 | `Widget with Personalized Daily Verses` |
| Bullet 2 | `Bring the Bible to your Home Screen` |
| Bullet 3 | `Personalized Audio Daily Devotionals` |
| Toggle row | `I want to try the app for free` (Material switch ON) |
| Plan A (selected) | `7 Days Free Trial` · badge `SAVE 36%` · `Then ~~158549.98~~ ₫105,000 per week.\nNo payment now` |
| Plan B (after scroll, label) | `Best Price of the Year` |
| Plan B (card) | `12-Month Access` · `Billed yearly at ₫880,000` |
| Footer note | `Cancel anytime before April 23 2026.\nNo risks, no charges.` |
| CTA | `Try for Free →` (yellow) |
| Footer links | `Terms of use` · `Privacy policy` · `Restore` |

### Notes

- Pricing rendered in **VND** (`₫`). Strikethrough Vietnamese-locale price `158549.98` is a leftover from the underlying Play Billing micros conversion — likely `158,549.98` ≈ `158,550`/week if the conversion fix wasn't applied. The displayed promo price is `₫105,000/week`.
- "Cancel anytime before April 23 2026" = trial-end date (capture day Apr 16 + 7 days).
- The toggle ON state binds to Plan A; toggling off presumably switches to Plan B (not verified — left to operator).

---

## Screen 09 — Verse Session Reader

### 09a — Read mode (text-only)

- **Dump**: `screen_09_verse_read.xml`
- **Screenshot**: `screen_09_verse_read.png`
- **Entry**: tap `Read` button on the Verse card (or tap a completed day in Calendar / week-strip)

| Element | Bounds | Text |
|---|---|---|
| Header title | `[375,154][705,220]` | `Your Journey` |
| Close `X` | `[926,121][1058,253]` | (no text) |
| Progress label | `[44,297][529,363]` | `Progress for Apr 15` |
| Progress percent | `[921,297][1036,369]` | `75%` (rises to `100%` after later sessions) |
| Card type label | `[349,568][656,620]` | `YOUR VERSE` |
| Card duration | `[695,569][802,620]` | `1 MIN` |
| Verse body | `[88,906][992,1351]` | `Fear not, for I am with you; Be not dismayed, for I am your God. I will strengthen you, Yes, I will help you, I will uphold you with My righteous right hand.` |
| Citation | `[372,1403][709,1492]` | `Isaiah 41:10` (yellow) |
| Bottom action — left (thumbs/dislike) | `[44,1852][220,2028]` | (icon only) |
| Bottom action — middle (`Chat to learn more`) | `[226,1852][854,2028]` | `Chat to learn more` + chat-bubble icon |
| Bottom action — right (next/arrow) | `[863,1852][1036,2028]` | `→` icon |

Background = the same nature/ocean image used on the Today card thumbnail.

### 09b — Listen mode (audio playback)

- **Dump**: `screen_09_verse_listen.xml`
- **Screenshot**: `screen_09_verse_listen.png`
- **Entry**: tap `Listen` on the Verse card (or the play button in 09a — not verified)

Same screen as 09a but the bottom action bar is replaced by an audio-player toolbar:

| Element | Text / icon |
|---|---|
| Audio progress bar | `——————————` |
| Time read-out (left) | `00:02` (during playback) |
| Time read-out (right) | `00:09` (track length) |
| Share | left icon |
| Previous | back-skip icon |
| Play / Pause | centre (paused button shown after starting) |
| Next | forward-skip icon |
| Replay | circular-arrow icon |

### 09c — "Chat to learn more" → Chat conversation

- **Dump**: `screen_09_verse_chat.xml`
- **Screenshot**: `screen_09_verse_chat.png`
- **Entry**: tap the middle bottom-action

Navigates into the **Chat feature cluster** (already documented in `chat_feature_spec.md`):

| Element | Text |
|---|---|
| Header title | `Chat` |
| Header back arrow | left |
| Header right icons | `?5` (help with badge `5`) · `tT` (font size) |
| Pre-filled context bubble | `Fear not, for I am with you; Be not dismayed, for I am your God. I will strengthen you, Yes, I will help you, I will uphold you with My righteous right hand.` |
| Bubble actions | thumbs-up · thumbs-down · `Copy` · `Share` |
| Composer | `Message` placeholder + chat-bubble icon + send arrow |

The verse text is already inserted into the conversation as a system/context message before the user types anything.

---

## Screen 10 — Devotional Reader

- **Dump**: `screen_10_devotional.xml` (expanded card on Today), `screen_10_devotional_read.xml` + `_b/_c/_d.xml`
- **Screenshot**: `screen_10_devotional.png`, `screen_10_devotional_read.png`, `_b.png`, `_c.png`, `_d.png`

### 10-card — Devotional card expanded (on Today landing)

When tapping the collapsed `PERSONALIZED DEVOTIONAL` card, it expands and the Verse card collapses:

| Element | Bounds | Text |
|---|---|---|
| Card title | `[88,1024][904,1154]` | `Strengthened by His Righteous Hand` |
| Tag pill 1 | `[110,1198][222,1250]` | `FAITH` |
| Tag pill 2 | `[277,1198][797,1250]` | `OVERCOMING CHALLENGES` |
| `Listen` button | `[259,1340][424,1415]` | `Listen` |
| `Read` button | `[747,1340][885,1415]` | `Read` |

Card background = a hands-raised-in-prayer image (gradient purple/pink overlay).

### 10-read — Devotional Reader (full text)

Layout matches Screen 09a (same `Your Journey` header, progress bar, bottom action bar). The body is a long scrollable devotional text. Across `_read` → `_d` (3 swipes) the full body was captured:

> **Paragraph 1** — `In this verse, God provides a profound reassurance to His people. He reminds us not to fear, for He is with us. This simple yet powerful promise is a cornerstone of the Christian faith. It assures us of God's unwavering presence, no matter the challenges we face.`
>
> **Paragraph 2** — `Reflecting on this, it is essential to understand that fear is a natural human response. We often encounter situations that seem beyond our control or comprehension. However, God's message through Isaiah is that His presence is constant and unyielding. Our faith may waver, but His promise does not.`
>
> **Paragraph 3** — `The verse also speaks of God's strength and support. He commits to upholding us with…` (continues in `_c`) `…In our daily lives, we face numerous challenges — from personal struggles to global crises. This verse encourages us to shift our focus from our fears to God's presence and strength. By doing so, we find the courage to face our challenges head-on, knowing that we are not alone.`
>
> **Paragraph 4 (closing prompt)** — `For further reflection, consider this: What fears or challenges in these situations?` (continues in `_d`) `Take a moment today to pray and invite God into your fears. Ask Him to fill you with His peace and support, trusting that His righteous right hand is upholding you every step of the way.`
>
> **Citation** — `Isaiah 41:10`

Bottom action bar identical to Screen 09a (thumbs-down icon · `Chat to learn more` · `→`).

---

## Screen 11 — Prayer Reader

- **Dump**: `screen_11_prayer.xml` (expanded card), `screen_11_prayer_read.xml`
- **Screenshot**: `screen_11_prayer.png`, `screen_11_prayer_read.png`

### 11-card — Prayer card expanded

| Element | Text |
|---|---|
| Card type / duration | `PRAYER OF THE DAY` · `2 MIN` |
| Card title | `Strength in God` |
| `Listen` button | `Listen` |
| `Read` button | `Read` |

Card background = a hands-raised silhouette image.

### 11-read — Prayer Reader

Same `Your Journey` shell. Body:

> **Title strip** — `PRAYER OF THE DAY · 2 MIN` (small caps, white text on dark)
>
> **Body** — `Heavenly Father, I come before You with an open heart, seeking Your guidance and strength as I embark on this journey of faith and understanding. Help me to fully embrace Your love and wisdom, to see Your hand at work in every aspect of my life. May Your Word be a lamp unto my feet and a light unto my path, guiding me through each day with clarity and purpose.`

Bottom action bar variant: thumbs-down · `Chat to learn more` · **`Done`** (white pill instead of `→` arrow — because this is the last incomplete session of the day).

After tapping `Done` (or `KEYCODE_BACK`), the day-progress reaches `100%` and the Day-Complete celebration screen appears (Screen 12).

---

## Screen 12 — Day-Complete Celebration

- **Dump**: `screen_12_day_complete.xml`
- **Screenshot**: `screen_12_day_complete.png`
- **Entry**: complete the last incomplete session of the day (here: tap `Done` on Prayer Reader)

| Element | Text |
|---|---|
| Fire illustration | (yellow gradient flame, centred) |
| Counter | `1` (large yellow) |
| Label | `day streak` (yellow) |
| 3-dot streak progress (horizontal) | dot 1 filled · dot 2 outline · dot 3 outline |
| Sub-text | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` |
| Compact week strip | `Mo 13 · Tu 14 · We 🔥 · Th 16 · Fr 17 · Sa 18 · Su` (today = fire icon) |
| CTA | `Continue` (yellow pill) |

Tapping `Continue` returns to the Today landing for the same day (now showing all cards `DONE`, progress `100%`, fire badge `1`).

This screen mirrors Block N of `onboarding_spec.md` (33-free-questions promise), confirming the same celebration is reused for daily streak milestones, not just first-day onboarding.

---

## Screen 13 — Peace and Calm Bottom Sheet

- **Dump**: `screen_13_peace.xml`
- **Screenshot**: `screen_13_peace.png`
- **Entry**: tap `PEACE AND CALM` card (last card on Today landing)

Bottom sheet (full screen with darkened backdrop):

| Element | Bounds | Text |
|---|---|---|
| Top close hit-zone | `[0,0][1080,122]` | desc `Close sheet` |
| Title | `[44,210][1036,650]` | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Disclaimer | `[44,694][1036,844]` | `Your privacy is guaranteed and your information will remain confidential.` |
| EditText | `[66,954][1014,1302]` | placeholder `Describe here` |
| `Continue` CTA | `[44,1777][1036,1962]` | `Continue` (greyed/disabled until the EditText has content) |

Dismiss: `KEYCODE_BACK` or tap top hit-zone.

---

## Screen 15 — Available Points (Light Points store)

- **Dump**: `screen_15_badge.xml`, `_b.xml`, `_c.xml`, `_d.xml`, `_e.xml`
- **Screenshot**: `screen_15_badge.png`, `_b.png`, `_c.png`, `_d.png`, `_e.png`
- **Entry**: tap the Light Points badge (`30` / `100`) at top-right of Today header

### Layout

Full-screen, scrollable.

| Element | Text |
|---|---|
| Close `X` | top-left |
| Header | `Available Points : ⊙ 100` (current balance) |

### Sections (top → bottom across `_a`–`_e`)

| Section | Items (icon · label · cost in points or VND) |
|---|---|
| `Premium` | gift · `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | image-frame · `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `?` · `5 Questions` · `⊙ 250`<br>`?` · `25 Questions` · `⊙ 1000`<br>`?` · `100 Questions` · `⊙ 2500` |
| `Light Points` (purchase tiers) | sparkle · `100 Light Points` · `₫30,000`<br>`500 Light Points` · `₫108,000`<br>`1.000 Light Points` · `₫198,000`<br>`2.500 Light Points` · `₫391,000`<br>`10.000 Light Points` · `₫1,300,000` |
| `Study Unlocks` (each `⊙ 250`) | `Loved, then loving` · `The Heart of Thanksgiving` · `Faith for the Impossible` · `Rising above Offense` · `Singleness Rooted in Christ` · `Being a Disciple in the [...]` · `God's Word at Life's Core` · `The Life-Changing Effects of Praise` · `The Song of Songs - A Love Like No Other` · `Living by Faith - In Every Season of Life` · `Living by Faith - In Every Role We Fill` · `Living by Faith - In Abundance or Need` · `Salvation Plan: Genesis to Revelation` · `Cultivating Godly [...]` · `Leadership & Professional Development` · `Godly & Healthy Relationships` · `Fullness of Being` · `Emotional Well-Being` · `Mental Well-Being` · `The Power of Thanksgiving` |
| `Coming Soon` | shield-icon · `Special Study` |

### Notes

- Number formatting in the Light Points purchase tiers uses **dot as thousands separator** (`1.000`, `2.500`, `10.000`) — Vietnamese locale. The cost column uses **comma as thousands separator** (`30,000`, `1,300,000`) — also acceptable in `vi-VN`. Inconsistent within the same screen.
- `5 / 25 / 100 Questions` correlate to the `?5` badge seen in the Chat header (Screen 09c) — i.e. the user currently has 5 free Q&A credits.
- Day-Complete celebration (Screen 12) promises `33 free questions` after a 3-day streak — a third source of Chat credits, distinct from the `Chat Unlocks` tier and the bonus that ships with `1-Month Premium`.

---

## Cross-screen invariants

- All session reader screens (Verse / Devotional / Prayer) share an identical chrome:
  - Header: `Your Journey` title + `X` close at `[926,121][1058,253]` (and a back-arrow at left for inner navigation, when entered via Chat)
  - `Progress for <date>` + percent
  - Card type label (small caps, e.g. `YOUR VERSE`) + duration (`1 MIN`)
  - Bottom action bar: thumbs-down (left) · `Chat to learn more` (middle) · `→` arrow / `Done` pill (right)
- The bottom action bar's right slot is `→` while there are remaining incomplete sessions for the day, and switches to `Done` on the last session.
- The Today landing's Light Points badge sums to current point balance; observed values `30` (initial) → `100` after completing Verse + Devotional + Prayer of Apr 15. Each completed session likely awards points (precise rule not measured here).
- Streak counter (fire icon on the calendar pill) was `0` at start, `1` after the first Day-Complete event of the session.
- All currency rendered in `₫` (Vietnamese đồng) per device locale.