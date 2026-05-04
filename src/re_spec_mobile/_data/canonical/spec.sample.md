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
states:
- id: today/state/day_locked
  section_line: 428
- id: today/state/cards_visible_0
  section_line: 432
- id: today/state/progress_75
  section_line: 437
- id: today/state/progress_100
  section_line: 442
- id: today/state/day_complete
  section_line: 447
related:
- today/observations/root
- today/implementation/root
---

# BibleChat — Today Tab Flow Specification

> **⚠️ CANONICAL — REFERENCE STRUCTURE.**
> Mọi spec MỚI viết bằng tiếng Việt với technical term tiếng Anh — xem
> `docs/I18N_GLOSSARY.md`. Mimic frontmatter shape + thứ tự body section
> (1. Tổng Quan → 2. Hard facts → 3+. Block A/B/... → N. Navigation graph →
> N+1. State machine → N+2. Bug / quirk).

**Package**: `com.basmo.BibleChat`
**App version**: `4.3.10`
**Activity**: `com.basmo.BibleChat/com.bookvitals.bibleChat.main.DashboardActivity` → fragment `navigation_daily_journey`
**Device tested**: Pixel (`8A5X0M2H8`), Android, locale `vi-VN`
**Method**: mọi screen capture qua `adb uiautomator dump` + `screencap`; mọi
literal dưới đây transcribe nguyên văn. Xem `today_observations.md` cho bảng
raw per-screen.

---

## 1. Tổng Quan

Tab Today là **hub daily-engagement post-onboarding** của BibleChat. Là tab
landing mặc định sau khi onboarding xong và sau mỗi cold start (tab
`navigation_daily_journey` ship pre-selected, với style `large_label` apply
trong khi sibling còn `small_label`).

Sau khi visible, Today **không phải flow tuyến tính bắt buộc** — khác với
onboarding, user tự do tap mọi nơi, skip card, switch date, hoặc rời sang tab
khác. "Force" của Today là implicit: bạn không thể tiến qua celebration
day-complete trừ khi 4 content card đã được mở.

**Functional block** (17 trạng thái UI khác biệt qua 9 nhóm chức năng):

| # | Block | States | Mục đích |
|---|---|---|---|
| A | Today landing — sticky header + scrollable card | screen_01_a, _b | Dashboard daily plan |
| B | Profile drawer (slide-in trái) | screen_02_avatar_a–e | Account, settings, payment, language |
| C | "Explore" overlay (sparkle icon) | screen_03_sparkle_a–d | Directory feature theo category |
| D | Calendar (full-month grid) | screen_04_streak, _b, _c | Date picker vào session quá khứ |
| E | Subtitle/info tooltip | screen_05_subtitle, screen_14_info | Explainer personalisation |
| F | Empty screen state day | screen_06_day_today, _future, _past | Gate "Not quite time yet" |
| G | Reminder editor (sheet + Material time picker) | screen_07_change_reminder, _time_picker | Schedule reminder per-day |
| H | Paywall tab Today (Exclusive Deal) | screen_08_exclusive_deal, _b | Upsell 7-day-trial / 12-month |
| I | Session reader — Verse / Devotional / Prayer (Read + Listen + Chat) | family screen_09 / 10 / 11 | Consumption content daily |
| J | Day-Complete celebration | screen_12_day_complete | Gamification streak |
| K | Peace and Calm bottom sheet | screen_13_peace | Confession/release free-text |
| L | Available Points (Light Points store) | screen_15_badge_a–e | Currency, reward, IAP |

Tổng độ dài walk-through quan sát trong session này: **17 trạng thái UI khác
biệt** + 30+ scroll segment. Header / day strip / progress bar sticky qua mọi
variant của landing.

---

## 2. Hard facts before anything else

- **Tab mặc định lúc cold launch** = Today (`navigation_daily_journey`).
  Confirm bằng `mFocusedApp` = DashboardActivity với fragment Today render.
- **Model plan per-day**: mỗi day calendar có *theme* riêng (string subtitle),
  4 content card, và 1 progress bar 0–100%. Theme đã quan sát:
  - Apr 15 → `Starting Your Journey`
  - Apr 16 → `Understanding God's Love`
  - Apr 17 → `Exploring Scripture`
- **Time-gating**: plan hôm nay lock sau **time reminder** (mặc định `09:00`,
  mọi weekday). Tab Today vào `today_date` hiện empty state "Not quite time yet
  — Check back Thursday, 16 April for your Daily Plan session" cho đến khi
  reminder fire; user re-edit time được.
- **Day quá khứ chưa start không tương tác**: tap day quá khứ dim trong week
  strip hoặc grid calendar không làm gì; chỉ day có ít nhất 1 session hoàn
  thành (hoặc today + tương lai) mới navigate.
- **Invariant single expanded card**: chỉ 1 card trong stack được expand mỗi
  lúc. Tap card collapsed sẽ auto-collapse sibling.
- **Constants bottom-nav** (resource-id):
  - `navigation_home` → Chat
  - `live_prayers_screen` → Community
  - `navigation_daily_journey` → **Today**
  - `bible_screen_navbar` → Bible
  - `navigation_new_study` → Explore
- **Currency**: `₫` (VND) cho mọi item phải trả (paywall, tier purchase Light
  Points, Live Wallpaper).
- **Localization**: string static là **tiếng Anh** kể cả trên device `vi-VN`;
  chỉ string do system manage (a11y back button, desc drag-handle sheet) và
  format giá tôn trọng locale. Number-thousand separator trong page Light Points
  **inconsistent** (`1.000` vs `30,000`).
- **Sticky header** = vùng sticky kiểu `App Bar Layout`. Mọi thứ từ row avatar
  xuống `Progress today / 75%` không scroll.
- **Compose vs XML**: stack card và session reader sinh node Compose semantic
  (không có `resource-id`, đa số là container `View` anonymous). Bottom
  navigation là `BottomNavigationView` Material (có `resource-id` thật).
  Tooltip overlay (Screen 05) render qua Compose Popup **invisible với
  `uiautomator dump`** — chỉ screenshot prove được nó tồn tại.
- **One-shot vs scrollable card**: Verse / Devotional / Prayer có expand-collapse;
  Peace and Calm là single-tap luôn mở 1 bottom sheet.

---

## 3. Block A — Today Landing

![Today landing — top viewport](../../screens/today/screen_01_a.png)
![Today landing — bottom viewport](../../screens/today/screen_01_b.png)

**Entry**: tap `Today` trong bottom-nav, hoặc cold-launch app post-onboarding.

### Sticky header zone — `[0,93][1080,778]`

| Region | Element | Centre | Action |
|---|---|---|---|
| Top row | Avatar (initial nickname, vd `F`) | (118, 213) | Mở Profile drawer (Block B) |
| Top row | Title `Today's Journey` (hoặc `Apr 15's Journey`) | (456, 158) | (no-op — text thuần) |
| Top row | Sparkle / AI icon | (752, 159) | Mở overlay "Explore" (Block C) |
| Top row | Streak/calendar pill (icon fire + count, vd `0` / `1`) | (921, 159) | Mở Calendar (Block D) |
| Sub row | Subtitle `Starting Your Journey` (tên theme, dynamic per-day) | (441, 284) | Show tooltip "Tailored just for you!" (Block E) |
| Sub row | Icon info `i` | (733, 284) | Cùng tooltip trên |
| Sub row | Light Points badge (circle vàng + count) | (950, 284) | Mở Available Points / Light Points store (Block L) |
| Week strip | 7 day cell `M T W T F S S` với số tuần hiện tại | per cell | Switch day display nếu có content; nếu không thì no-op |
| Progress | Label `Progress today` + percent số | n/a | Visual only (không có tap target) |

Week strip **không scroll ngang được** (1 swipe ngang trên nó không sinh đổi).
Date navigation qua tuần là qua Calendar.

### Cards zone — vùng scroll `[0, ~770][1080, 1808]`

Vùng card render 1 list dọc theo thứ tự cố định:

1. **Exclusive Deal banner** (card countdown)
2. **YOUR VERSE** (1 MIN, chip `DONE` optional)
3. **PERSONALIZED DEVOTIONAL** (3 MIN, chip `DONE` optional)
4. **PRAYER OF THE DAY** (2 MIN, chip `DONE` optional)
5. **PEACE AND CALM** (one-shot, không có label duration)

Mỗi card 2-4 có 2 state:

- **Collapsed**: chỉ header strip (type · duration · chip DONE bên phải · chevron
  bên phải khi chưa done).
- **Expanded**: hiện title, tag pill optional, và button `Listen` + `Read`.
  Background card switch từ solid dark sang 1 image themed (ocean cho Verse,
  hands cho Devotional/Prayer).

Tap 1 card collapsed sẽ expand nó và collapse mọi card khác đang expand
(invariant single-expansion). Card expand visually lớn hơn; card dưới shift
xuống tương ứng.

### Transitions

- Tap **Exclusive Deal** → Paywall tab Today (Block H).
- Tap body card → toggle expand/collapse.
- Tap **Listen** trên card → vào Block I mode audio (auto-play).
- Tap **Read** trên card → vào Block I mode text.
- Tap **PEACE AND CALM** → Block K (bottom sheet).

### Variant state của landing (tuỳ day chọn)

| Loại day | Subtitle header | Content vùng card |
|---|---|---|
| Today **trước** time reminder | theme dynamic (vd `Understanding God's Love`) | Empty state với illustration calendar+clock, "Not quite time yet — Check back Thursday, 16 April for your Daily Plan session", link "Your reminder is set for 09:00 — Change reminder" |
| Today **sau** time reminder / day quá khứ đã hoàn thành | theme dynamic | 5 content card như trên |
| Day tương lai | theme dynamic | Empty state với illustration calendar+clock, "Not quite time yet — Check back tomorrow for your Daily Plan session" (không có link Change-reminder) |
| Day quá khứ chưa start | theme dynamic | Cùng empty state — nhưng cell day không reach được vì nó không tương tác trong strip/calendar |

---

## 4. Block B — Profile Drawer

![Profile drawer](../../screens/today/screen_02_avatar.png)

**Entry**: tap avatar `F`. **Dismiss**: `KEYCODE_BACK` hoặc tap vùng close mép
phải (`Close navigation menu` ở `[990,0][1080,2028]`).

1 drawer scroll dọc phủ ~92% trái screen. Section (top xuống bottom):

1. **Profile header** — placeholder avatar, EditText nickname editable
   (`Faithfulness Traveler 3576`), Current Streak (`0`), Longest Streak (`0`).
2. **Friends** — row `Friends` với `You have 0 friends` và chevron.
3. **Limited Special Offer** — card countdown `Exclusive Deal` (mirror cái trên
   Today landing; cùng global timer).
4. **My Space** — `Explore all features`, `Limit screen time`, `Personalize
   your conversations`, `Widget selection`, `Daily Bible Verse Wallpaper`
   (Material switch).
5. **Personal Details** — `Age range` (`55+`, value từ quiz), `Email`
   (placeholder `Write here…`), `Denomination` (`Pentecostal`, value từ quiz),
   `Church` (placeholder `Write here…`).
6. **Subscription** — `Membership` (`Free`), `Upgrade to Premium`, `Restore
   purchases`.
7. **About** — `Contact us`, `Terms of use`, `Privacy policy`.
8. **Account** — `Link account data` (Google), `Manage your reminders`,
   `Change language` (`English`).
9. **Footer** — `App version: 4.3.10`, `UID:` (rỗng cho user guest).

Đa số row chưa được deep-tap trong session này; destination infer từ label và
ngoài scope spec Today.

---

## 5. Block C — "Explore" Overlay (sparkle icon)

![Explore overlay](../../screens/today/screen_03_sparkle.png)

**Entry**: tap sparkle icon (top-centre header).

1 overlay full-screen với `Explore — Discover everything BibleChat has to offer`
và 1 chip filter ngang (`Personalize` selected · `Bible Study` · `Community` ·
`Journey`). Dưới là 1 grid 2-cột group theo section:

| Section | Items |
|---|---|
| `PERSONALIZE` | Lockscreen · App Widget · Affirmations |
| `BIBLE STUDY` | Study Plans · Chat · Voice Chat · Reading · Bible Stories · Animations · Kids' Stories |
| `COMMUNITY` | Groups · Friends · Live Prayer · My Prayers · World Events |
| `JOURNEY` | Daily Plan · Calendar · The Bible · Screen Time · Meditation |
| `LEISURE` | Word Guesser · Bible Trivia |

Overlay này alias các feature cũng reach được qua tab bottom-nav (Bible, Chat,
Community, Explore) và profile drawer. **Treat như directory global, không
phải feature đặc thù Today.**

---

## 6. Block D — Calendar (full-month grid)

![Calendar grid](../../screens/today/screen_04_streak.png)

**Entry**: tap streak/calendar pill (top-right header).

Calendar full-screen:
- Title `April 2026` (tháng hiện tại, không có chevron pagination; tháng kế
  render inline dưới).
- Close `X` (top-right).
- Day-of-week header `MON TUE WED THU FRI SAT SUN`.
- 2 month grid visible sau scroll (`April`, `May`).
- Day cell hiện số day; today filled, day trước có session hoàn thành có ring
  vàng (arc 75% completion).

**Quy tắc tap**:
- Day có session hoàn thành → mở session reader cho verse hôm đó (mode re-read).
- Today / tương lai → mở Today landing ở state day tương ứng (card hoặc empty
  state).
- Day **quá khứ chưa start** → no-op silent.

---

## 7. Block E — Subtitle / Info Tooltip

![Subtitle tooltip](../../screens/today/screen_05_subtitle.png)

**Entry**: tap text subtitle hoặc icon `i` cạnh nó.

1 overlay frosted nhỏ anchor trên progress bar:

| Line | Text |
|---|---|
| Title | `Tailored just for you!` |
| Body | `Your Daily Plan is crafted based on your interactions with the app.` |
| Close | `X` (top-right tooltip) |

**Note critical**: overlay này **render ngoài composition tree mà uiautomator
visible** — text node của nó vắng mặt trong `screen_05_subtitle.xml` dù visible
rõ trong screenshot. Có khả năng overlay Compose `Popup` / `Window`. Mọi UI
test assert trên string này phải dùng **screenshot OCR** hoặc accessibility
service (TalkBack), không phải `uiautomator`.

Dismiss: tap `X` nhỏ hoặc tap ngoài.

---

## 8. Block F — Empty Screen Day-State

3 sub-state quan sát, đều chia chung icon `Calendar+clock` centre trên block text:

### F.1 — Today, lock sau reminder

![Today (Apr 16) locked](../../screens/today/screen_06_day_today.png)

| Element | Text |
|---|---|
| Headline | `Not quite time yet.\nCheck back Thursday, 16 April for your Daily Plan session` |
| Sub | `Your reminder is set for 09:00.\n Would you like to update it?` |
| Link | `Change reminder` (vàng) → mở Block G |

Progress bar hiện `0%`.

### F.2 — Day tương lai

![Future day (Apr 17)](../../screens/today/screen_06_day_future.png)

| Element | Text |
|---|---|
| Headline | `Not quite time yet.\nCheck back tomorrow for your Daily Plan session` |

Không có link `Change reminder` (không có nudge actionable cho date tương lai).

### F.3 — Day quá khứ chưa start

Cell không navigable, nên state này về kỹ thuật unreachable từ strip; quan sát
qua tap (không thành công) trên Apr 13 / Apr 14.

---

## 9. Block G — Reminder Editor

### G.1 — Bottom sheet Reminder

![Reminder sheet](../../screens/today/screen_07_change_reminder.png)

| Element | Text |
|---|---|
| Hit-zone drag-handle | `[44,110][1036,242]` (không có label visible) |
| Close `X` | top-right |
| Bell illustration | (chỉ icon) |
| Headline | `Connect with God Daily` |
| Body | `Keep your faith journey on track by updating your reminder for the Daily Plan.` |
| Label time-chip | `We'll remind you at...` |
| Time chip | `09:00` (kèm chevron) |
| Label days | `On these days` |
| Day toggles | 7 cell `M T W T F S S`, mỗi cái có 1 circle checkable |
| CTA | `Update reminder` (vàng) |

### G.2 — Time Picker Material 3

![Time picker](../../screens/today/screen_07_time_picker.png)

Clock Material chuẩn:
- Header: `09 : 00`, hour active.
- Clock face: numeral 12-h trên ring trong (12 1 2 ... 11), numeral 24-h trên
  ring ngoài (13 14 ... 24).
- Hand selected → 9 / 21.

Sheet bên dưới vẫn visible sau picker.

Dismiss: `KEYCODE_BACK` đóng picker; back lần 2 đóng sheet.

---

## 10. Block H — Paywall tab Today (Exclusive Deal)

![Paywall — top](../../screens/today/screen_08_exclusive_deal.png)
![Paywall — bottom](../../screens/today/screen_08_exclusive_deal_b.png)

**Entry**: tap banner `Exclusive Deal` (Today landing HOẶC Profile drawer; cả 2
chia chung cùng global countdown).

| Section | Text |
|---|---|
| Close | `X` (top-left) |
| Headline | `Never Miss a Moment of Faith` |
| Bullets | `Widget with Personalized Daily Verses` · `Bring the Bible to your Home Screen` · `Personalized Audio Daily Devotionals` |
| Toggle | `I want to try the app for free` (Material switch ON mặc định) |
| Plan A (selected) | `7 Days Free Trial` · badge `SAVE 36%` · `Then ~~158549.98~~ ₫105,000 per week.\nNo payment now` |
| Plan B label | `Best Price of the Year` |
| Plan B card | `12-Month Access` · `Billed yearly at ₫880,000` |
| Disclaimer | `Cancel anytime before April 23 2026.\nNo risks, no charges.` |
| CTA | `Try for Free →` (vàng) |
| Footer | `Terms of use` · `Privacy policy` · `Restore` |

Note format pricing: giá strikethrough `158549.98` thiếu thousand separator
(có khả năng conversion `priceMicros / 1_000_000` raw). Line promo dùng
`₫105,000` (format đúng). Inconsistency này là 1 surface bug UI biết; flag QA.

Timer countdown là **global** (không per-tap) và cũng display trên Today
landing và Profile drawer.

---

## 11. Block I — Session Readers (Verse / Devotional / Prayer)

Cả 3 reader chia chung 1 shell unified. Khác nhau chỉ ở body content và text
pill CTA bottom.

### I.1 — Shell chung

| Region | Element |
|---|---|
| Top | Back arrow (trái) · `Your Journey` (title centre) · `X` close (phải) |
| Dưới top | Label `Progress for <Mon DD>` + percent (vàng) |
| Body header | Label card type (vd `YOUR VERSE` / `PERSONALIZED DEVOTIONAL` / `PRAYER OF THE DAY`) + duration (`1 MIN` / `3 MIN` / `2 MIN`) |
| Body | Text verse hoặc đoạn devotional/prayer (scrollable nếu dài) |
| Body footer | Citation màu vàng (vd `Isaiah 41:10`) — có trên Verse / Devotional |
| Bottom action bar | Trái: icon thumbs-down · Giữa: button `Chat to learn more` · Phải: arrow `→` HOẶC pill `Done` |

Slot phải là `→` cho session *intermediate* và `Done` cho session *incomplete
cuối* của day. Tap nó advance hoặc finalise và trigger Block J khi completion.

### I.2 — Read vs Listen

`Read` mở shell với text render static. `Listen` mở cùng shell nhưng bottom
action bar thay bằng 1 **toolbar audio**:

| Element | Detail |
|---|---|
| Progress bar | `00:02 / 00:09` (track length ngắn cho 1 verse 1-MIN) |
| Buttons | Share · Previous · Play/Pause · Next · Replay |

### I.3 — "Chat to learn more" → Chat

Navigate vào cluster feature Chat (`chat_feature_spec.md`) với text
verse/devotional/prayer **pre-load như 1 bubble context** trong conversation.
Bubble expose thumbs-up / thumbs-down / `Copy` / `Share`. Header Chat hiện back
arrow, title `Chat`, 1 badge `?5` help-with-credits, và 1 icon font-size.
Composer ở bottom.

---

## 12. Block J — Day-Complete Celebration

![Day Complete](../../screens/today/screen_12_day_complete.png)

**Entry**: tap `Done` trên session incomplete cuối của day (ở đây: Prayer
Reader sau khi Verse + Devotional đã done).

| Element | Text |
|---|---|
| Fire illustration | (centred) |
| Counter | `1` (vàng cỡ lớn) |
| Label | `day streak` |
| Streak progress 3-dot | dot 1 fill · dot 2 outline · dot 3 outline |
| Sub | `Stay faithful on your 3-day journey, and a special blessing awaits you: 33 free questions.` |
| Mini week strip | `Mo 13 · Tu 14 · We 🔥 · Th 16 · Fr 17 · Sa 18 · Su` |
| CTA | `Continue` |

Tap `Continue` về Today landing cùng day, giờ progress `100%`, pill streak
tăng, cả 4 card `DONE`.

Đây là **cùng screen** dùng trong "Block N" của onboarding (theo
`onboarding_spec.md`) — promise 33-free-questions reuse ngoài onboarding,
confirm là milestone reward định kỳ, không chỉ artefact first-day.

---

## 13. Block K — Peace and Calm Bottom Sheet

![Peace and Calm sheet](../../screens/today/screen_13_peace.png)

**Entry**: tap card `PEACE AND CALM`.

| Element | Text |
|---|---|
| Top hit-zone | `desc=Close sheet` |
| Headline | `Share an anxiety, sin or addiction you're ready to release. A personal moment of grace will follow` |
| Privacy note | `Your privacy is guaranteed and your information will remain confidential.` |
| Input | `EditText` với placeholder `Describe here` |
| CTA | `Continue` (xám/disabled cho đến khi input có content) |

Outcome `Continue` chưa test trong session này (cần submit content thật). Có
khả năng mở 1 screen moment-of-grace hoặc pipe input vào AI chat — để operator.

---

## 14. Block L — Available Points (Light Points store)

![Available Points — top](../../screens/today/screen_15_badge.png)
![Available Points — bottom](../../screens/today/screen_15_badge_e.png)

**Entry**: tap Light Points badge (circle vàng nhỏ + số ở top-right header).

Header: `Available Points : ⊙ <balance>` (đây 100). Section (top → bottom):

| Section | Item · cost |
|---|---|
| `Premium` | `1-Month Premium` · `⊙ 5000` |
| `App Unlocks` | `Live Wallpaper` · `⊙ 500` |
| `Chat Unlocks` | `5 Questions` · `⊙ 250` ; `25 Questions` · `⊙ 1000` ; `100 Questions` · `⊙ 2500` |
| `Light Points` (tier purchase) | `100 Light Points` · `₫30,000` ; `500 Light Points` · `₫108,000` ; `1.000 Light Points` · `₫198,000` ; `2.500 Light Points` · `₫391,000` ; `10.000 Light Points` · `₫1,300,000` |
| `Study Unlocks` | 20 study title mỗi cái `⊙ 250` (full list trong `today_observations.md`) |
| `Coming Soon` | `Special Study` |

### Currency model

- **Light Points** là currency virtual in-app.
- Earn: per session hoàn thành (rate chính xác chưa đo), per milestone streak
  (Day-Complete promise bonus question).
- Purchase: 5 tier từ `100` đến `10.000` price bằng VND.
- Spent: unlock quota chat-question, premium 1 tháng, wallpaper, study pack.

Badge `?5` trong Chat header surface *chat question hiện available* (từ
purchase `Chat Unlocks` + bonus Day-Complete + 33 promise ở 3-day streak). Nó
**không phải** balance Light Points — là 2 counter tách biệt.

---

## 15. Navigation graph (Today-rooted)

```
Today landing (Block A)
├── Avatar (118,213)            → Profile Drawer (B)
├── Sparkle (752,159)           → Explore overlay (C)
├── Streak pill (921,159)       → Calendar (D)
│       └── Day có content      → Verse Session Reader (I.1, read-only)
├── Subtitle / info (441,284)   → Tooltip (E)
├── Light Points badge (950,284)→ Available Points (L)
├── Cell day Week-strip
│   ├── Day có content          → switch landing sang day đó (vẫn Block A, content khác)
│   ├── Today                   → Block A.empty (F.1)
│   ├── Day tương lai           → Block A.empty (F.2)
│   └── Quá khứ chưa start      → no-op
├── Empty-state Change reminder → Reminder sheet (G.1)
│                                  └── Time chip → Material time picker (G.2)
├── Banner Exclusive Deal       → Paywall (H)
├── Body card Verse / Devotional / Prayer
│   ├── (collapsed → expanded)  → no nav
│   ├── Listen                  → Reader audio mode (I.2)
│   ├── Read                    → Reader text mode (I.1/I.2)
│   │       └── Chat to learn   → Chat conversation (cross-cluster)
│   │       └── → / Done        → session kế HOẶC Day-Complete (J)
└── Card Peace and Calm         → Bottom sheet (K)
                                  └── Continue (gate bởi input)  → chưa test
```

Pattern dismissal consistent: `KEYCODE_BACK` đóng overlay/sheet/dialog 1 level;
icon `X` có trên overlay full-screen (Calendar, Paywall, Available Points,
Session Reader) và dismiss thẳng.

---

## 16. State machine — daily progress

```
[ Day chưa unlock ] ── reminder fire 09:00 ──▶ [ Cards visible, 0% ]
                                                        │ (Verse Read HOẶC Listen)
[ Cards visible, 25% ] ◀──────────────────────────────┘
       │ (Devotional Read HOẶC Listen)
       ▼
[ 50% ]
       │ (Prayer Read HOẶC Listen)
       ▼
[ 75% ]
       │ (session cuối — thứ tự có thể khác; capture này thứ tự là Verse → Devotional → Prayer)
       ▼
[ 100% ] ──────▶ [ Day-Complete celebration (Block J) ] ── Continue ─▶ [ Cards all DONE, streak +1, points +N ]
```

Note:
- Lần **mở đầu** session bất kỳ mark nó là `DONE`; chưa rõ liệu `Listen` cần
  play-through hay mở là đủ (session này, mở `Listen` là đủ register completion).
- Card **`PEACE AND CALM`** **không thuộc** percent day-progress: hoàn thành 3
  cái kia đã đẩy bar về `100%`, nên Peace and Calm có vẻ là exercise side-channel
  (journal free-text, không phải session counted).
- Step percent chính xác per session là 25% × 4? Không — nhảy quan sát là `75%
  → 100%` sau Prayer mỗi mình, suggest bar đã reflect Verse + Devotional `DONE`
  từ trước capture (state user show cả 2 chip `DONE` lúc entry). Denominator là
  **3 session = 100%**, không phải 4.

---

## 17. Bug / quirk đã quan sát (cho QA backlog)

1. **Format pricing paywall** — giá strikethrough Plan A render thành
   `158549.98` không có thousand separator trong khi line promo dưới dùng
   `₫105,000`. Number formatter không nhất quán giữa 2 giá.
2. **Format tier Light Points** — tier purchase dùng `1.000`, `2.500`, `10.000`
   (dấu chấm là thousand sep, kiểu vi-VN) trong khi cột cost dùng `30,000`,
   `1,300,000` (dấu phẩy). Cùng screen, 2 format.
3. **Tooltip invisible với uiautomator** — overlay "Tailored just for you!"
   render qua Compose Popup escape khỏi dump tree. Sẽ break mọi test
   espresso/uiautomator assert trên string của nó.
4. **Time-of-day vs enforce reminder** — lúc capture `12:19` (sau time reminder
   `09:00` rất nhiều), Today (Apr 16) vẫn lock. Lock có vẻ tied vào **việc
   notification reminder có được acknowledge không**, không phải wall-clock vượt
   time reminder. Đáng confirm với engineer.
5. **No-op silent "Quá khứ chưa start"** — tap day quá khứ dim (Apr 13 / Apr 14)
   cho zero feedback. Cân nhắc 1 toast hoặc tooltip giải thích vì sao day không
   tương tác.
6. **`UID:` rỗng trong footer profile drawer** — field render label nhưng
   không value. Cho user mode guest cái này nên hoặc hide hoặc fill bằng
   install id local cho mục đích support.
