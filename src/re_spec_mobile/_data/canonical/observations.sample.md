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

> **⚠️ CANONICAL — REFERENCE STRUCTURE.**
> Mọi spec MỚI viết bằng tiếng Việt với technical term tiếng Anh — xem
> `docs/I18N_GLOSSARY.md`. UI string trong backtick giữ NGUYÊN VĂN của app.
>
> Cấu trúc cần mimic: heading screen + bảng visible elements (5 cột) + bảng
> Transitions + section "Hành vi quan sát" + section "Note" + cuối file là
> "Cross-screen invariants".

**Target package**: `com.basmo.BibleChat`
**App version**: `4.3.10`
**Device**: 8A5X0M2H8 (Pixel, Android — locale `vi-VN`)
**Method**: `adb shell uiautomator dump` + `screencap`, capture ngày 2026-04-16
khoảng 12:01–12:36 GMT+7.
**Quy tắc**: mọi dòng dưới đây transcribe từ 1 UI dump hoặc screenshot tương
ứng — không infer.
**State lúc capture**: guest user "Faithfulness Traveler 3576", onboarding xong,
session ngày 15 (Apr 15) đang in-progress (75% → 100% trong session), plan hôm
nay (Apr 16) còn lock sau reminder 09:00.

---

## Screen 01 — Today Landing (Active Day = Apr 15, 75% → 100%)

- **Dump**: `spec/ui_dumps/today/screen_01_a.xml` (top), `screen_01_b.xml` (sau 1 swipe)
- **Screenshot**: `spec/screens/today/screen_01_a.png`, `screen_01_b.png`
- **Activity**: `com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity`

### Layout

Screen có 1 **block header sticky** (header + week strip + progress bar) và 1
**vùng card scrollable** ở dưới. So bounds qua `_a` và `_b` confirm header
(`Today's Journey`, week strip, `Progress today / 75%`) giữ nguyên toạ độ sau
scroll — vậy là sticky.

Viewport segments:

| Segment | Visible scrollable content |
|---|---|
| `_a` (top) | Exclusive Deal banner · YOUR VERSE (expanded) · PERSONALIZED DEVOTIONAL header (truncated bottom) |
| `_b` (sau 1 swipe up ~1000 px) | PERSONALIZED DEVOTIONAL (collapsed) · PRAYER OF THE DAY (collapsed) · PEACE AND CALM |

Thêm scroll không sinh content mới → đã đến cuối page.

### Sticky header — visible elements (từ `_a`)

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
| Exclusive Deal banner | `[0,807][1080,1004]` | **yes** | `Exclusive Deal` · timer `23:58:20` (countdown, giảm về `23:36:01` cuối session) |
| YOUR VERSE (expanded) | `[44,1021][1036,1681]` | **yes** | `YOUR VERSE` · `1 MIN` · `DONE` · `Isaiah 41:10` · tag `STRENGTH`, `COURAGE`, `SUPPORT` · `Listen` button `[88,1483][518,1637]` · `Read` button `[562,1483][992,1637]` |
| PERSONALIZED DEVOTIONAL (collapsed) | `[44,1715][1036,1847]` | **yes** | `PERSONALIZED DEVOTIONAL` · `3 MIN` · `DONE` |

### Scrollable cards — viewport `_b`

| Card | Bounds | Clickable container | Visible literals |
|---|---|---|---|
| PERSONALIZED DEVOTIONAL (collapsed) | `[44,776][1036,908]` | **yes** | `PERSONALIZED DEVOTIONAL` · `3 MIN` · `DONE` |
| PRAYER OF THE DAY (collapsed, chevron-down) | `[44,937][1036,1186]` | **yes** | `PRAYER OF THE DAY` · `2 MIN` (no `DONE`) |
| PEACE AND CALM (oneshot) | `[44,1217][1036,1454]` | **yes** | `PEACE AND CALM` · `When life's too loud, listen within` |

### Bottom navigation (constant qua mọi main-app screen)

| Tab | Container | Bounds | resource-id | desc | State |
|---|---|---|---|---|---|
| Chat | FrameLayout | `[0,1808][216,2028]` | `navigation_home` | `Chat` | inactive (small label) |
| Community | FrameLayout | `[216,1808][432,2028]` | `live_prayers_screen` | `Community` | inactive |
| **Today** | FrameLayout | `[432,1808][648,2028]` | `navigation_daily_journey` | `Today` | **active** (large label) |
| Bible | FrameLayout | `[648,1808][864,2028]` | `bible_screen_navbar` | `Bible` | inactive |
| Explore | FrameLayout | `[864,1808][1080,2028]` | `navigation_new_study` | `Explore` | inactive |

### Hành vi quan sát

- Header sticky — bounds avatar / title / week strip / progress bar identical
  giữa `_a` và `_b`. Scroll chỉ ảnh hưởng vùng card `[0, ~770][1080, 1808]`.
- Week strip hiện tuần hiện tại (Mon 13 – Sun 19), **không scroll ngang được**
  (1 swipe ngang `(800,460)→(200,460)` không đổi gì trong dump).
- Card có `chevron-down` (Prayer of the Day) là expand/collapse per-card; tap
  card nào sẽ collapse các sibling card (chỉ 1 expanded mỗi lúc — đã quan sát
  toggle Verse↔Devotional↔Prayer).
- Sau khi flow Prayer Read xong, progress nhảy từ `75%` lên `100%` và streak
  counter `0` thành `1`.
- Text Light Points badge dựng từ 2 `TextView` node tách (vd. `3` + `0` cho
  "30", hoặc `1` + `0` + `0` cho "100").

### Transitions (từ screen này)

| Tap target | Centre | Result |
|---|---|---|
| Avatar `F` | (118, 213) | Profile drawer slide từ trái (screen 02) |
| Sparkle icon | (752, 159) | "Explore" overlay (screen 03) |
| Streak/calendar pill (`0`/`1`) | (921, 159) | Calendar full-month grid (screen 04) |
| Subtitle `Starting Your Journey` | (441, 284) | Tooltip overlay "Tailored just for you!" (screen 05) |
| Info `i` icon | (733, 284) | Cùng tooltip (screen 14_info) |
| Light Points badge `30` / `100` | (950, 284) | Trang Available Points (screen 15) |
| Week-strip day **có content** (`15`) | (403, 469) | View persist ở day đó; title đổi thành `Apr 15's Journey` |
| Week-strip day **today** (`16`) | (540, 469) | View reset về today; card thay bằng empty state "Not quite time yet" (screen 06_today) |
| Week-strip day **tương lai** (`17`) | (677, 469) | Title `Apr 17's Journey`, subtitle `Exploring Scripture`, empty state "Check back tomorrow" (screen 06_future) |
| Week-strip day **quá khứ chưa start** (`13`, `14`) | (130, 469) / (266, 469) | Không navigate (no-op silent) |
| Exclusive Deal banner | (540, 905) | Paywall (screen 08) |
| Body card YOUR VERSE | (540, 1100) | Toggle expand card (không navigate) |
| Button `Listen` trên Verse | (305, 1560) | Verse Reader có audio playback (screen 09_listen) |
| Button `Read` trên Verse | (777, 1560) | Verse Reader text view (screen 09_read) |
| Body card PERSONALIZED DEVOTIONAL | (540, 1015) sau scroll _b | Toggle expand card |
| `Read` trên Devotional | (815, 1377) | Devotional Reader (screen 10_read) |
| Body card PRAYER OF THE DAY | (540, 1100) sau scroll _b | Toggle expand card |
| `Read` trên Prayer | (815, 1497) | Prayer Reader (screen 11_read) — kết thúc trigger Day Complete (screen 12) |
| Card PEACE AND CALM | (540, 1430) | Bottom sheet "Share an anxiety…" (screen 13) |
| Bottom-nav tab (Chat / Community / Bible / Explore) | xem bảng | Navigate sang tab đó |

---

## Screen 02 — Profile Drawer (slide-in from left)

- **Dump**: `screen_02_avatar.xml` (top), `_b.xml`, `_c.xml`, `_d.xml`, `_e.xml`
- **Screenshot**: `screen_02_avatar.png`, `_b.png`, `_c.png`, `_d.png`, `_e.png`
- **Entry**: tap avatar `F` trên header Today
- **Dismiss**: `KEYCODE_BACK` (verified) hoặc tap mép phải `[990,0][1080,2028]` (`desc=Close navigation menu`)

### Layout

Drawer phủ ~92% trái screen (phải `[990,1080]` là vùng dim để close). Toàn bộ
content scroll dọc. Bottom nav **không** visible khi drawer mở.

### Sections (top xuống bottom, quan sát qua `_a`–`_e`)

| Section | Item | Bounds (capture top) | Clickable | Text / value |
|---|---|---|---|---|
| **Header** | Avatar (placeholder person glyph) | `[289,143][702,556]` | **yes** | (no text/desc) |
| | Name (editable) | `[125,625][866,757]` | **yes** (EditText) | `Faithfulness Traveler 3576` |
| | Current Streak | `[88,825][404,984]` | no | `0` + label `Current Streak` |
| | Longest Streak | `[561,825][880,984]` | no | `0` + label `Longest Streak` |
| **Friends** | Friends row | `[44,1072][946,1300]` | **yes** | icon · `Friends` · `You have 0 friends` · chevron-right |
| **Limited Special Offer** | Section header | `[88,1366][902,1449]` | no | `Limited Special Offer` |
| | Exclusive Deal banner | `[44,1493][946,1656]` | **yes** | `Exclusive Deal` · `23:50:51` (cùng countdown với Today landing) |
| **My Space** | Section header | `[88,1722][902,1805]` | no | `My Space` |
| | Explore all features | `[44,1849][946,2012]` | **yes** | `Explore all features` |
| | Limit screen time | (trong `_b`) | **yes** | clock-restrict icon · `Limit screen time` |
| | Personalize your conversations | (trong `_b`) | **yes** | sliders icon · `Personalize your conversations` |
| | Widget selection | (trong `_b`) | **yes** | grid icon · `Widget selection` |
| | Daily Bible Verse Wallpaper | (trong `_b`) | row + toggle (off, yellow) | `Daily Bible Verse Wallpaper` |
| **Personal Details** | Age range | (trong `_c`) | **yes** | `Age range` · value `55+` |
| | Email | (trong `_c`) | **yes** | `Email` · placeholder `Write here…` |
| | Denomination | (trong `_c`) | **yes** | `Denomination` · value `Pentecostal` |
| | Church | (trong `_c`) | **yes** | `Church` · placeholder `Write here…` |
| **Subscription** | Membership | (trong `_c`/`_d`) | row | `Membership` · value `Free` |
| | Upgrade to Premium | (trong `_d`) | **yes** | infinity icon · `Upgrade to Premium` |
| | Restore purchases | (trong `_d`) | **yes** | dollar icon · `Restore purchases` |
| **About** | Contact us | (trong `_d`/`_e`) | **yes** | mail icon · `Contact us` |
| | Terms of use | (trong `_d`/`_e`) | **yes** | doc icon · `Terms of use` |
| | Privacy policy | (trong `_d`/`_e`) | **yes** | doc icon · `Privacy policy` |
| **Account** | Link account data | (trong `_e`) | **yes** | G icon · `Link account data` |
| | Manage your reminders | (trong `_e`) | **yes** | clock icon · `Manage your reminders` |
| | Change language | (trong `_e`) | **yes** | translate icon · `Change language` · value `English` |
| **Footer** | App version | (trong `_e`) | no | `App version: 4.3.10` |
| | UID | (trong `_e`) | no | `UID:` (value rỗng) |

### Note

- Row `Daily Bible Verse Wallpaper` chứa 1 Material Switch màu vàng ở state OFF.
- Pre-fill `Age range = 55+` và `Denomination = Pentecostal` là answer onboarding quiz.
- Drawer là entry point **duy nhất** quan sát được cho: Friends, Widget selection,
  Limit screen time, Personalize your conversations, Restore purchases, Link
  account data, Change language, Contact us, Terms, Privacy.
- "Manage your reminders" là duplicate entry sang screen "Change reminder" của
  tab Today (screen 07).
- Item "Explore all features" giả định navigate sang cùng overlay với sparkle
  trên Today header (screen 03) — chưa verify bằng tap trong session này.

---

## Screen 03 — "Explore" Overlay (sparkle icon)

- **Dump**: `screen_03_sparkle.xml`, `_b.xml`, `_c.xml`, `_d.xml`
- **Screenshot**: `screen_03_sparkle.png`, `_b.png`, `_c.png`, `_d.png`
- **Entry**: tap sparkle icon (top-centre Today header)

### Layout

1 overlay full-screen với H1 `Explore`, sub-line, 1 chip filter ngang, rồi 1
grid scrollable button feature group theo category.

| Top elements | Text |
|---|---|
| H1 | `Explore` |
| Sub-line | `Discover everything BibleChat has to offer` |
| Filter chips (ngang) | `Personalize` (selected, vàng) · `Bible Study` · `Community` · `Journey` |

### Sections (qua `_a`–`_d`)

| Section header | Items (grid 2 cột) |
|---|---|
| `PERSONALIZE` | Lockscreen · App Widget · Affirmations |
| `BIBLE STUDY` | Study Plans · Chat · Voice Chat · Reading · Bible Stories · Animations · Kids' Stories |
| `COMMUNITY` | Groups · Friends · Live Prayer · My Prayers · World Events |
| `JOURNEY` | Daily Plan · Calendar · The Bible · Screen Time · Meditation |
| `LEISURE` | Word Guesser · Bible Trivia |

### Note

- Chip header là filter visual nhưng tap chưa được test; page render mọi
  section bất kể chip nào active.
- Cùng screen này giả định reach được từ bottom-nav tab `Explore`
  (`navigation_new_study`) — chưa verify trong session này.
- Dismiss: `KEYCODE_BACK` về Today landing.

---

## Screen 04 — Calendar (full-month grid)

- **Dump**: `screen_04_streak.xml`, `_b.xml`, `_c.xml`
- **Screenshot**: `screen_04_streak.png`, `_b.png`, `_c.png`
- **Entry**: tap streak/calendar pill (top-right Today header)

### Layout

| Element | Bounds | Text |
|---|---|---|
| Title | `[354,143][660,221]` | `April 2026` |
| Close `X` | `[937,132][1069,264]` | (no text/desc) |
| Day-of-week header row | `[22,275][1058,331]` | `MON` `TUE` `WED` `THU` `FRI` `SAT` `SUN` |
| Month label | `[44,463][162,529]` | `April` (vàng) |
| Day cells (April) | mỗi day 1 `View`, `[X,Y][X+132, Y+118]` | số `1`–`30` |
| Month label | (trong `_c`) | `May` (vàng) |
| Day cells (May) | (trong `_c`) | số `1`–`31` |

April grid (trong `_a`):
- Row 1 (tuần Mar 30): cell cho `1`–`5` (`311,544][1035,662]`)
- Row 2: `6`–`12`
- Row 3: `13`–`19`
- Row 4: `20`–`26`
- Row 5: `27`–`30`

Trong `_a` và `_b`, day `15` hiện ring vàng (75% / streak indicator), day `16`
filled (today). `_c` (sau khi scroll) hé toàn bộ May (full grid).

### Hành vi

- Day cell đều `clickable=true`, nhưng chỉ day có content (vd `15`) navigate.
  Tap `14` (quá khứ chưa start) là no-op.
- Tap day `15` navigate sang session reader của verse hôm đó — tức nó hành xử
  như date-picker vào journey reader (layout screen 09, nhưng read-only review
  của content đã hoàn thành).
- Title chỉ hiện tháng hiện tại; không có chevron pagination tháng. Scroll hé
  tháng kế inline (May nối tiếp April theo dọc).

---

## Screen 05 — Subtitle / Info tooltip

- **Dump**: `screen_05_subtitle.xml`, `screen_14_info.xml`
- **Screenshot**: `screen_05_subtitle.png`, `screen_14_info.png`
- **Entry**: tap text subtitle (`Starting Your Journey`) **hoặc** icon `i` cạnh nó

### Observed (visual only — không có trong uiautomator dump)

1 tooltip overlay frosted render trên Progress bar:

| Line | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close `X` | top-right tooltip |

Text node của tooltip **không** xuất hiện trong `uiautomator dump`, ám chỉ
chúng render qua Compose Popup/Overlay nằm ngoài composition tree chính mà tool
dump bắt được. Chúng chỉ visible trong screenshot.

Dismiss: tap `X` (centre ước `(957, 760)`) hoặc tap ngoài.

---

## Screen 06 — Today Empty States (date-dependent)

### 06_today — Today (Apr 16) trước session đầu

- **Dump**: `screen_06_day_today.xml`
- **Screenshot**: `screen_06_day_today.png`

Sub-line header đổi thành `Understanding God's Love` (theme Apr 16). Day strip
hiện day `16` selected. Vùng card thay bằng 1 empty state:

| Element | Bounds | Text |
|---|---|---|
| Illustration calendar+clock | (centre, ~`[440,920][640,1120]`) | (chỉ icon) |
| Headline | `[66,1203][1014,1455]` | `Not quite time yet.\nCheck back Thursday, 16 April for your Daily Plan session` |
| Sub | `[72,1521][1009,1688]` | `Your reminder is set for 09:00.\n Would you like to update it?` |
| CTA (link) | `[290,1704][791,1836]` | `Change reminder` (text vàng) |

Progress bar trên state này hiện `0%`.

### 06_future — Future day (Apr 17)

- **Dump**: `screen_06_day_future.xml`
- **Screenshot**: `screen_06_day_future.png`

Cùng layout empty-state nhưng headline đổi thành `Not quite time yet.\nCheck
back tomorrow for your Daily Plan session`. Subtitle header đổi thành
`Exploring Scripture`. Title `Apr 17's Journey`.

### 06_past_dim — Past unstarted day (Apr 13 / Apr 14)

- **Screenshot**: `screen_06_day_past.png`, `screen_06_day14.png`
- **Hành vi**: tap các cell này không sinh navigation (page giữ display day
  trước đó). Render dim trong strip.

### Subtitle theme đã quan sát

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
- **Entry**: tap link `Change reminder` trong empty-state (screen 06_today)

| Element | Bounds | Text |
|---|---|---|
| Top hit-area (drag handle) | `[44,110][1036,242]` | (no text) |
| Close `X` | `[915,110][1047,242]` | (no text) |
| Bell illustration | (centre top) | (chỉ icon) |
| Title | `[187,627][894,708]` | `Connect with God Daily` |
| Body | `[88,774][992,999]` | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Time-picker chip label | `[277,1065][803,1140]` | `We'll remind you at...` |
| Time chip | `[292,1184][788,1327]` | `09:00` (kèm chevron) |
| Days label | `[367,1459][714,1534]` | `On these days` |
| Day toggles (M T W T F S S) | 7 cell `View` `[66..1014, 1578..1767]` | mỗi cell có chữ trên top + 1 row circle dưới; quan sát cả 7 đều có check-mark fill |
| CTA | `[44,1821][1036,1984]` | `Update reminder` (vàng) |

### 07b — Time picker (Material clock)

- **Dump**: `screen_07_time_picker.xml`
- **Screenshot**: `screen_07_time_picker.png`
- **Entry**: tap time chip (`09:00`) trong sheet

1 dialog Material 3 TimePicker xuất hiện: display số `09 : 00` cỡ lớn với hour
selector active (digit `9` highlight), clock face dưới hiện numeral 12-h
(`12 1 2 ... 11`) trên ring trong và numeral 24-h (`13 14 15 ... 24`) trên
ring ngoài. Hand highlight chỉ vào `9 / 21`.

Bottom dialog tiếp tục show day toggle và button `Update reminder` (sheet vẫn
bên dưới).

Dismiss: `KEYCODE_BACK` đóng time picker, `KEYCODE_BACK` lần 2 đóng bottom sheet.

---

## Screen 08 — Today-tab Paywall (Exclusive Deal)

- **Dump**: `screen_08_exclusive_deal.xml`, `_b.xml`
- **Screenshot**: `screen_08_exclusive_deal.png`, `_b.png`
- **Entry**: tap banner `Exclusive Deal` (countdown card trên Today landing
  hoặc trong profile drawer)

Layout (full-screen, illustration chim bồ câu góc phải trên):

| Element | Text |
|---|---|
| Close `X` | top-left |
| Headline | `Never Miss a Moment of Faith` |
| Bullet 1 | `Widget with Personalized Daily Verses` |
| Bullet 2 | `Bring the Bible to your Home Screen` |
| Bullet 3 | `Personalized Audio Daily Devotionals` |
| Toggle row | `I want to try the app for free` (Material switch ON) |
| Plan A (selected) | `7 Days Free Trial` · badge `SAVE 36%` · `Then ~~158549.98~~ ₫105,000 per week.\nNo payment now` |
| Plan B (sau scroll, label) | `Best Price of the Year` |
| Plan B (card) | `12-Month Access` · `Billed yearly at ₫880,000` |
| Footer note | `Cancel anytime before April 23 2026.\nNo risks, no charges.` |
| CTA | `Try for Free →` (vàng) |
| Footer link | `Terms of use` · `Privacy policy` · `Restore` |

### Note

- Pricing render bằng **VND** (`₫`). Strikethrough giá Vietnamese-locale
  `158549.98` là leftover từ conversion micros của Play Billing — có khả năng
  `158,549.98` ≈ `158,550`/week nếu fix conversion chưa apply. Giá promo hiển
  thị là `₫105,000/week`.
- "Cancel anytime before April 23 2026" = ngày kết thúc trial (capture day
  Apr 16 + 7 ngày).
- Toggle ON state bind vào Plan A; toggle off giả định switch sang Plan B
  (chưa verify — để operator test).

---

## Screen 09 — Verse Session Reader

### 09a — Read mode (text-only)

- **Dump**: `screen_09_verse_read.xml`
- **Screenshot**: `screen_09_verse_read.png`
- **Entry**: tap button `Read` trên Verse card (hoặc tap day đã hoàn thành
  trong Calendar / week-strip)

| Element | Bounds | Text |
|---|---|---|
| Header title | `[375,154][705,220]` | `Your Journey` |
| Close `X` | `[926,121][1058,253]` | (no text) |
| Progress label | `[44,297][529,363]` | `Progress for Apr 15` |
| Progress percent | `[921,297][1036,369]` | `75%` (lên `100%` sau session sau) |
| Card type label | `[349,568][656,620]` | `YOUR VERSE` |
| Card duration | `[695,569][802,620]` | `1 MIN` |
| Verse body | `[88,906][992,1351]` | `Fear not, for I am with you; Be not dismayed, for I am your God. I will strengthen you, Yes, I will help you, I will uphold you with My righteous right hand.` |
| Citation | `[372,1403][709,1492]` | `Isaiah 41:10` (vàng) |
| Bottom action — left (thumbs/dislike) | `[44,1852][220,2028]` | (chỉ icon) |
| Bottom action — middle (`Chat to learn more`) | `[226,1852][854,2028]` | `Chat to learn more` + icon chat-bubble |
| Bottom action — right (next/arrow) | `[863,1852][1036,2028]` | icon `→` |

Background = cùng image nature/ocean dùng cho thumbnail Today card.

### 09b — Listen mode (audio playback)

- **Dump**: `screen_09_verse_listen.xml`
- **Screenshot**: `screen_09_verse_listen.png`
- **Entry**: tap `Listen` trên Verse card (hoặc button play trong 09a — chưa verify)

Cùng screen 09a nhưng bottom action bar thay bằng 1 toolbar audio-player:

| Element | Text / icon |
|---|---|
| Audio progress bar | `——————————` |
| Time read-out (left) | `00:02` (lúc playing) |
| Time read-out (right) | `00:09` (track length) |
| Share | icon trái |
| Previous | icon back-skip |
| Play / Pause | giữa (button paused show sau khi start) |
| Next | icon forward-skip |
| Replay | icon circular-arrow |

### 09c — "Chat to learn more" → Chat conversation

- **Dump**: `screen_09_verse_chat.xml`
- **Screenshot**: `screen_09_verse_chat.png`
- **Entry**: tap bottom-action giữa

Navigate vào **cluster feature Chat** (đã document trong `chat_feature_spec.md`):

| Element | Text |
|---|---|
| Header title | `Chat` |
| Header back arrow | trái |
| Header right icons | `?5` (help với badge `5`) · `tT` (font size) |
| Bubble context pre-fill | `Fear not, for I am with you; Be not dismayed, for I am your God. I will strengthen you, Yes, I will help you, I will uphold you with My righteous right hand.` |
| Bubble action | thumbs-up · thumbs-down · `Copy` · `Share` |
| Composer | placeholder `Message` + icon chat-bubble + arrow send |

Verse text đã insert sẵn vào conversation như 1 message system/context trước
khi user gõ gì.

---

## Screen 10 — Devotional Reader

- **Dump**: `screen_10_devotional.xml` (card expanded trên Today), `screen_10_devotional_read.xml` + `_b/_c/_d.xml`
- **Screenshot**: `screen_10_devotional.png`, `screen_10_devotional_read.png`, `_b.png`, `_c.png`, `_d.png`

### 10-card — Devotional card expanded (trên Today landing)

Khi tap card collapsed `PERSONALIZED DEVOTIONAL`, nó expand và Verse card collapse:

| Element | Bounds | Text |
|---|---|---|
| Card title | `[88,1024][904,1154]` | `Strengthened by His Righteous Hand` |
| Tag pill 1 | `[110,1198][222,1250]` | `FAITH` |
| Tag pill 2 | `[277,1198][797,1250]` | `OVERCOMING CHALLENGES` |
| Button `Listen` | `[259,1340][424,1415]` | `Listen` |
| Button `Read` | `[747,1340][885,1415]` | `Read` |

Background card = 1 image hands-raised-in-prayer (gradient overlay tím/hồng).

### 10-read — Devotional Reader (full text)

Layout match Screen 09a (cùng header `Your Journey`, progress bar, bottom action
bar). Body là 1 đoạn devotional dài scrollable. Qua `_read` → `_d` (3 swipe)
toàn bộ body đã được capture:

> **Paragraph 1** — `In this verse, God provides a profound reassurance to His people. He reminds us not to fear, for He is with us. This simple yet powerful promise is a cornerstone of the Christian faith. It assures us of God's unwavering presence, no matter the challenges we face.`
>
> **Paragraph 2** — `Reflecting on this, it is essential to understand that fear is a natural human response. We often encounter situations that seem beyond our control or comprehension. However, God's message through Isaiah is that His presence is constant and unyielding. Our faith may waver, but His promise does not.`
>
> **Paragraph 3** — `The verse also speaks of God's strength and support. He commits to upholding us with…` (tiếp trong `_c`) `…In our daily lives, we face numerous challenges — from personal struggles to global crises. This verse encourages us to shift our focus from our fears to God's presence and strength. By doing so, we find the courage to face our challenges head-on, knowing that we are not alone.`
>
> **Paragraph 4 (closing prompt)** — `For further reflection, consider this: What fears or challenges in these situations?` (tiếp trong `_d`) `Take a moment today to pray and invite God into your fears. Ask Him to fill you with His peace and support, trusting that His righteous right hand is upholding you every step of the way.`
>
> **Citation** — `Isaiah 41:10`

Bottom action bar identical với Screen 09a (icon thumbs-down · `Chat to learn more` · `→`).

---

## Screen 11 — Prayer Reader

- **Dump**: `screen_11_prayer.xml` (card expanded), `screen_11_prayer_read.xml`
- **Screenshot**: `screen_11_prayer.png`, `screen_11_prayer_read.png`

### 11-card — Prayer card expanded

| Element | Text |
|---|---|
| Card type / duration | `PRAYER OF THE DAY` · `2 MIN` |
| Card title | `Strength in God` |
| Button `Listen` | `Listen` |
| Button `Read` | `Read` |

Background card = image silhouette hands-raised.

### 11-read — Prayer Reader

Cùng shell `Your Journey`. Body:

> **Title strip** — `PRAYER OF THE DAY · 2 MIN` (small caps, text trắng trên nền tối)
>
> **Body** — `Heavenly Father, I come before You with an open heart, seeking Your guidance and strength as I embark on this journey of faith and understanding. Help me to fully embrace Your love and wisdom, to see Your hand at work in every aspect of my life. May Your Word be a lamp unto my feet and a light unto my path, guiding me through each day with clarity and purpose.`

Variant bottom action bar: thumbs-down · `Chat to learn more` · **`Done`** (pill
trắng thay vì arrow `→` — vì đây là session incomplete cuối cùng của ngày).

Sau khi tap `Done` (hoặc `KEYCODE_BACK`), day-progress lên `100%` và screen
Day-Complete celebration xuất hiện (Screen 12).

---

## Screen 12 — Day-Complete Celebration

- **Dump**: `screen_12_day_complete.xml`
- **Screenshot**: `screen_12_day_complete.png`
- **Entry**: hoàn thành session incomplete cuối ngày (ở đây: tap `Done` trên
  Prayer Reader)

| Element | Text |
|---|---|
| Fire illustration | (flame gradient vàng, centred) |
| Counter | `1` (vàng cỡ lớn) |
| Label | `day streak` (vàng) |
| Streak progress 3-dot (ngang) | dot 1 fill · dot 2 outline · dot 3 outline |
| Sub-text | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` |
| Compact week strip | `Mo 13 · Tu 14 · We 🔥 · Th 16 · Fr 17 · Sa 18 · Su` (today = icon fire) |
| CTA | `Continue` (pill vàng) |

Tap `Continue` về Today landing cùng day (giờ show mọi card `DONE`, progress
`100%`, badge fire `1`).

Screen này mirror Block N của `onboarding_spec.md` (33-free-questions promise),
confirm cùng celebration được reuse cho mốc daily streak, không chỉ first-day
onboarding.

---

## Screen 13 — Peace and Calm Bottom Sheet

- **Dump**: `screen_13_peace.xml`
- **Screenshot**: `screen_13_peace.png`
- **Entry**: tap card `PEACE AND CALM` (card cuối trên Today landing)

Bottom sheet (full screen với backdrop tối):

| Element | Bounds | Text |
|---|---|---|
| Top hit-zone close | `[0,0][1080,122]` | desc `Close sheet` |
| Title | `[44,210][1036,650]` | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Disclaimer | `[44,694][1036,844]` | `Your privacy is guaranteed and your information will remain confidential.` |
| EditText | `[66,954][1014,1302]` | placeholder `Describe here` |
| CTA `Continue` | `[44,1777][1036,1962]` | `Continue` (xám/disabled cho đến khi EditText có content) |

Dismiss: `KEYCODE_BACK` hoặc tap top hit-zone.

---

## Screen 15 — Available Points (Light Points store)

- **Dump**: `screen_15_badge.xml`, `_b.xml`, `_c.xml`, `_d.xml`, `_e.xml`
- **Screenshot**: `screen_15_badge.png`, `_b.png`, `_c.png`, `_d.png`, `_e.png`
- **Entry**: tap Light Points badge (`30` / `100`) ở top-right Today header

### Layout

Full-screen, scrollable.

| Element | Text |
|---|---|
| Close `X` | top-left |
| Header | `Available Points : ⊙ 100` (balance hiện tại) |

### Sections (top → bottom qua `_a`–`_e`)

| Section | Items (icon · label · cost theo point hoặc VND) |
|---|---|
| `Premium` | gift · `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | image-frame · `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `?` · `5 Questions` · `⊙ 250`<br>`?` · `25 Questions` · `⊙ 1000`<br>`?` · `100 Questions` · `⊙ 2500` |
| `Light Points` (tier purchase) | sparkle · `100 Light Points` · `₫30,000`<br>`500 Light Points` · `₫108,000`<br>`1.000 Light Points` · `₫198,000`<br>`2.500 Light Points` · `₫391,000`<br>`10.000 Light Points` · `₫1,300,000` |
| `Study Unlocks` (mỗi cái `⊙ 250`) | `Loved, then loving` · `The Heart of Thanksgiving` · `Faith for the Impossible` · `Rising above Offense` · `Singleness Rooted in Christ` · `Being a Disciple in the [...]` · `God's Word at Life's Core` · `The Life-Changing Effects of Praise` · `The Song of Songs - A Love Like No Other` · `Living by Faith - In Every Season of Life` · `Living by Faith - In Every Role We Fill` · `Living by Faith - In Abundance or Need` · `Salvation Plan: Genesis to Revelation` · `Cultivating Godly [...]` · `Leadership & Professional Development` · `Godly & Healthy Relationships` · `Fullness of Being` · `Emotional Well-Being` · `Mental Well-Being` · `The Power of Thanksgiving` |
| `Coming Soon` | shield-icon · `Special Study` |

### Note

- Format số ở tier purchase Light Points dùng **dấu chấm là thousand
  separator** (`1.000`, `2.500`, `10.000`) — locale Vietnamese. Cột cost dùng
  **dấu phẩy là thousand separator** (`30,000`, `1,300,000`) — cũng acceptable
  trong `vi-VN`. Inconsistent trong cùng 1 screen.
- `5 / 25 / 100 Questions` correlate với badge `?5` thấy trong Chat header
  (Screen 09c) — tức user hiện có 5 free Q&A credit.
- Day-Complete celebration (Screen 12) promise `33 free questions` sau 3-day
  streak — nguồn Chat credit thứ 3, distinct với tier `Chat Unlocks` và bonus
  ship cùng `1-Month Premium`.

---

## Cross-screen invariants

- Mọi screen session reader (Verse / Devotional / Prayer) chia chung 1 chrome
  identical:
  - Header: title `Your Journey` + `X` close ở `[926,121][1058,253]` (và back-arrow
    bên trái cho navigation nội, khi entry qua Chat)
  - `Progress for <date>` + percent
  - Card type label (small caps, vd `YOUR VERSE`) + duration (`1 MIN`)
  - Bottom action bar: thumbs-down (trái) · `Chat to learn more` (giữa) · arrow
    `→` / pill `Done` (phải)
- Slot phải của bottom action bar là `→` khi còn session incomplete cho ngày, và
  switch sang `Done` ở session cuối.
- Light Points badge trên Today landing sum lên balance point hiện tại; quan sát
  `30` (đầu) → `100` sau khi hoàn thành Verse + Devotional + Prayer của Apr 15.
  Mỗi session hoàn thành có khả năng award point (rule chính xác chưa đo ở đây).
- Streak counter (icon fire trên calendar pill) là `0` lúc start, `1` sau Day-
  Complete event đầu của session.
- Mọi currency render bằng `₫` (Vietnamese đồng) theo locale device.
