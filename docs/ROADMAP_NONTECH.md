# ROADMAP — Hạ ngưỡng cho non-tech user

> **Audience**: founder/lead/PM muốn plan cách mở rộng workflow này cho user
> không phải dev. Đây là **plan**, chưa execute. Đọc xong là biết scope effort,
> trade-off, và milestone next.

**Status**: Proposed (2026-05-04). Không trong scope v1.0.0 của re-spec-mobile.

---

## 1. Reality check — định nghĩa "non-tech"

"Non-tech 100%" cho workflow RE Android **không khả thi** — RE flow nhất thiết
cần USB debugging + adb + accessibility permissions. Đó là dev-mode features,
không có cách bypass.

Nhưng có thể hạ ngưỡng từ **"cần biết bash/Python/git"** → **"biết cài app +
làm theo wizard"**. Đó là target khả thi.

### Phân khúc user

| Tier | Mô tả | Khả thi? | Notes |
|---|---|---|---|
| **T0** Zero tech | Chỉ biết mở app, không biết Settings → Developer | ❌ | RE flow không thể — workflow bị chặn ở USB debugging |
| **T1** Light tech | Cài được app, làm theo screenshot tutorial, chấp nhận paste 1-2 lệnh | ✅ | **Target chính của roadmap này** |
| **T2** Tech | Biết git/terminal/Python | ✅ | Đã hỗ trợ trong v1.0.0 với INSTALL.sh hiện tại |

**Decision**: target T1. Investment effort cho T0 không justify (return-on-effort thấp do bottleneck Android dev mode).

---

## 2. Plan tổng thể — 6 phase

| # | Phase | Goal | Effort | Deliverable |
|---|---|---|---|---|
| 1 | Distribution | User lấy được skill về máy mà không git clone | 6h | installer/{install.sh, install.ps1, get.sh} |
| 2 | Bootstrap skill | Skill tự cài dependencies (adb, droidrun, Portal) | 5h | skills/mobile-spec-bootstrap/SKILL.md + check_deps.py |
| 3 | Wizard UX | Profile gen qua chat conversation thay vì YAML edit | 4h | tools/wizard.py + skill instructions cho AskUserQuestion |
| 4 | Conversational layer | Natural language → workflow phase mapping | 2h | SKILL.md intent table + ví dụ dialogue |
| 5 | Packaging + materials | Screencast, GIF, troubleshooting page | 7h | docs/quickstart.md + media/ |
| 6 | Acceptance test | Test với T1 user thật + iterate | 1 ngày | feedback notes + iteration backlog |

**Total**: ~3 ngày focus work + 1 ngày user test.

---

## 3. Phase 1 — Distribution (6h)

User chưa biết git clone, không thể follow current INSTALL.sh flow. Cần
distribution channel "1-line" hoặc better.

### 3 option (ưu tiên ↓)

| Option | UX | Effort | Notes |
|---|---|---|---|
| **1A** Claude Code plugin marketplace | `/plugin install re-spec-mobile` | High (manifest + publish + Anthropic review wait) | Best UX nhưng phụ thuộc Anthropic timeline |
| **1B** One-line installer URL | `curl -fsSL <url>/get.sh \| bash` (Mac/Linux); PowerShell tương đương Win | Medium | Hoạt động ngay, accept shell |
| **1C** Manual copy-paste tutorial | Screenshots step-by-step | Low | Fallback cuối cho T1 boundary case |

**Recommend**: ship **1B** trước, theo dõi **1A** parallel. **1C** mặc định trong README làm fallback.

### Output cần build

- `installer/install.sh` — Linux/Mac install script (detect OS, brew/apt, download skill, INSTALL.sh)
- `installer/install.ps1` — Windows PowerShell tương đương
- `installer/get.sh` — 1-liner entrypoint host ở github raw URL: `curl ... | bash`
- (1A) Plugin manifest + Anthropic submission

### Risk

- `curl | bash` security concern → checksum verify + signed installer
- Windows users không có WSL → cần PS1 hoặc bundle WSL setup
- Anthropic plugin review chờ vài tuần

---

## 4. Phase 2 — Bootstrap skill (5h)

Hiện tại user phải tự cài Python + pyyaml + adb + droidrun. Quá nhiều cho T1.

### New skill: `mobile-spec-bootstrap`

Tách biệt với `re-spec-mobile` chính. Trigger lần đầu user mở Claude Code.

```
1. Detect OS (linux/mac/win) + arch
2. Check `adb`:
   - missing → đề xuất:
     - Mac: brew install android-platform-tools
     - Win: winget install Google.AndroidStudio
     - Linux: apt/pacman/dnf
   - confirm trước khi run
3. Check Python 3.10+:
   - install pyyaml + droidrun via pipx (isolated env)
4. Pair device:
   - "Bạn cắm device USB rồi đáp 'usb', hoặc dùng wireless ADB rồi đáp 'wireless'"
   - USB: hướng dẫn enable USB debugging (1 screenshot per Android version 8/9/10/11/12/13/14)
   - Wireless: hướng dẫn QR code (Android 11+) hoặc IP+port (older)
5. Run setup_portal.sh tự động
6. Trigger main skill `/re-spec-mobile`
```

**Tools needed**:
- `tools/check_deps.py` — cross-platform dep detection (uses `shutil.which`)
- Skill SKILL.md với AskUserQuestion để chia thành câu hỏi rời

### Risk

- Auto-install dep tạo trojan vector → sign installer + print mọi command trước run
- Corp laptop không có sudo → bundle portable adb binary
- Older Android (< 11) không có wireless ADB → fallback USB

---

## 5. Phase 3 — Wizard UX (4h)

Hiện tại `init_project.py` scaffold + bỏ user lại với YAML phải tự edit. T1 user
không chịu nổi YAML.

### Conversational profile gen

```
Claude: "App bạn muốn spec tên gì?"
User:   "Tinder"

Claude: "Mở app Tinder trên device giúp mình, đáp 'open' khi xong"
User:   "open"

[autodetect package + main_activity từ adb dumpsys]
Claude: "Mình thấy package là `com.tinder`, main activity là
        `com.tinder.feature.intro.activities.IntroActivity`. Đúng không?"
User:   "yes"

Claude: "App có bottom navigation không?"
User:   "có"

Claude: "Tap vào từng tab giúp mình, rồi đáp 'done' khi xong tab cuối..."
[capture mỗi tab → autodetect resource_id + center coords]

Claude: "Mình tìm thấy 5 tab: Home, Likes, Boost, Messages, Profile.
        Tab nào là default khi mở app?"
User:   "Home"

Claude: "OK, profile xong. Có muốn add blocklist patterns gì không? Mặc định
        đã có Subscribe/Buy/Logout. App có CTA destructive nào khác không?"
User:   "Có Pay-to-Match"

Claude: "Add `Pay-to-Match` vào blocklist. Done. Bắt đầu spec tab nào trước?"
```

**Tools needed**:
- `tools/wizard.py` — orchestrate Q&A, write profile.yml progressively
- Skill instructions để dùng `AskUserQuestion` step-by-step (mỗi câu 1 message)

### Output

- Profile được generate hoàn toàn qua chat, user không bao giờ phải open YAML
- Validation chạy ngay sau mỗi answer
- Autodetect tận dụng adb shell + Portal hết mức có thể

---

## 6. Phase 4 — Conversational layer (2h)

User chỉ nói tiếng người, không type slash command. Skill phải hiểu intent.

### Intent table

| User nói | Workflow trigger |
|---|---|
| "spec app này" / "tạo spec cho app" | Phase 0 init |
| "tab Profile có gì" / "spec màn Profile" | Phase 1 + invoke explorer trên Profile tab |
| "thử bấm nút Settings xem sao" | Capture màn settings (single-screen) |
| "xong rồi, viết spec" / "tạo spec đi" | Phase 5 spec-writer |
| "mở file spec ra cho tôi xem" | Read + present feature_spec.md |
| "scope OK" / "duyệt scope" | Phase 1.5 sign-off + start Phase 2 |
| "coverage OK" / "đủ rồi" | Phase 4.5 sign-off pass + start Phase 5 |
| "ready commit" | Phase 7 |

### Output

- Edit `SKILL.md` thêm intent table
- Add ví dụ dialogue Vietnamese để Claude pattern-match tốt hơn
- Optional: thêm shortcut commands (vd `/spec scope`, `/spec coverage`) cho user thích bàn phím

---

## 7. Phase 5 — Packaging + materials (7h)

T1 user cần visual onboarding + troubleshooting tự-serve.

### Materials cần produce

| Artifact | Mục đích | Effort |
|---|---|---|
| 5-min screencast | "From zero to first spec in 5 minutes" | 3h record + edit |
| README.md với GIF | Visual onboarding (animated demo) | 2h |
| Troubleshooting page | Top 10 errors + plain-text fix | 1h |
| 1-page quick start PDF | Print-friendly, in tay user | 30min |
| FAQ | Common questions | 30min |

### Optional: Discord/Slack channel

Hỗ trợ realtime — quy mô nhỏ ban đầu, anyone-can-join.

### Risk

- Screencast outdated khi tool changes → ghi version trong video, plan re-record per major release
- Troubleshooting page rot → encourage user contribute

---

## 8. Phase 6 — Acceptance test với real T1 user (1 ngày)

Tìm 1 PM/designer/QA non-dev thực sự làm thử end-to-end. Ngồi cạnh, ghi
**tất cả pain point**, không hint.

### Test protocol

1. User chỉ có URL + 5-min screencast làm reference
2. Goal: spec 1 feature nhỏ của Instagram (vd Profile tab)
3. Time-box: 2 giờ
4. Observe + ghi:
   - Mỗi pause > 30 giây = pain point
   - Mỗi câu hỏi user = doc gap
   - Mỗi error message họ không hiểu = UX bug
5. KHÔNG hint trừ khi user stuck > 5 phút

### Iterate 3 vòng

- **Vòng 1**: fix critical pain points (UX bugs, broken instructions)
- **Vòng 2**: fix doc gaps + error messages
- **Vòng 3**: polish + edge case

Mục tiêu: vòng 3, T1 user spec xong feature trong 90 phút mà không cần hỏi anyone.

---

## 9. Risk matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User trên Windows không có Android Studio → adb missing | High | Block toàn flow | `winget install` auto từ bootstrap; fallback link tải zip |
| Wireless ADB chỉ Android 11+ | Medium | Cũ hơn cần USB | Detect Android version → fallback to USB instructions |
| User không có quyền sudo (corp laptop) | Medium | Không cài được brew/apt | Bundle portable adb binaries trong installer |
| Portal accessibility cần manual tap → user không tìm thấy | High | Stuck | Screenshot exact trên mỗi Android version (8-14) |
| App cần login mà user không có account | Medium | Block sau onboarding | Skill detect login screen → trả về "cần bạn login trước" |
| User đóng device giữa chừng | Medium | Capture loop fail | Heartbeat check; auto-pause khi mất connection |
| Marketplace plugin chờ Anthropic review | Low | Distribution chậm | Dual-track 1A + 1B |
| Bootstrap auto-install dep = trojan vector | Low | Security | Sign installer + checksum verify; print mọi command trước run |
| User không đọc tutorial, dùng sai workflow | High | Spec chất lượng kém | Wizard force step-by-step, không cho skip |
| User edit profile.yml sai format | High (T1) | Tool crash | Wizard write profile, user không bao giờ touch YAML |

---

## 10. Critical decisions cần pick trước khi build

| # | Quyết định | Default đề xuất | Rationale |
|---|---|---|---|
| 1 | Target tier | **T1 (light tech)** | T0 không khả thi |
| 2 | Distribution channel | **1B + 1A song song** | Ship 1B trước, 1A sau khi marketplace approve |
| 3 | Bootstrap skill — tách riêng vs gộp vào re-spec-mobile? | **Tách riêng** | Skill scope rõ; T2 không cần bootstrap |
| 4 | Wizard ngôn ngữ | **Vietnamese mặc định** + English fallback flag trong profile | Match audience hiện tại |
| 5 | Output dir cho user | **`~/Documents/AppSpecs/<app>/`** thay vì `~/specs/` | Win/Mac convention; visible trong file explorer |
| 6 | Bundle adb portable hay ép cài system-wide? | **Bundle portable** trong tool dir | Đỡ permission issue ở corp laptop |
| 7 | Acceptance test với ai? | TBD — user pick 1 PM/designer thật trong team | Phải là người chưa dùng tool |

---

## 11. Milestones + go/no-go

| Milestone | Date target | Go/no-go criteria |
|---|---|---|
| M1 — Phase 1 (Distribution 1B) ship | +1 tuần | Installer test pass trên Mac/Linux/Win VM |
| M2 — Phase 2 (Bootstrap) ship | +2 tuần | Bootstrap skill chạy end-to-end trên 1 fresh machine |
| M3 — Phase 3 (Wizard) ship | +2.5 tuần | Profile gen qua chat hoàn toàn, không touch YAML |
| M4 — Phase 4 (Conversational) ship | +3 tuần | 8+ intent verified |
| M5 — Phase 5 (Packaging) ship | +4 tuần | Screencast + README + troubleshoot page |
| M6 — Phase 6 (Acceptance test) | +5 tuần | T1 user spec 1 feature trong 90 phút |
| **GA T1** | +6 tuần | Iterate 3 vòng acceptance test pass |

---

## 12. Cross-references

- **Current operations** (cho T2): `docs/OPERATIONS.md`
- **Workflow contract**: `skills/re-spec-mobile/SKILL.md`
- **Test result confirming v1.0.0 works**: `docs/DOGFOOD_REPORT.md`
- **Architecture diagram**: `bible-agent/demo/architecture.html` (4-layer pipeline)

---

## 13. Decision log (track changes to this roadmap)

| Date | Decision | Owner |
|---|---|---|
| 2026-05-04 | Initial draft, target T1 chốt, 6 phase + 6-week timeline | (TBD pick owner) |
