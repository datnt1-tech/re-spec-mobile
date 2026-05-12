# PRD/SRS — iOS AUTHENTICATOR APP
**Version:** 1.0 — DRAFT  
**Ngày tạo:** 24/04/2026  
**Trạng thái:** Chờ PM review & confirm

---

# PHẦN A — TỔNG QUAN DỰ ÁN

## 1. Mục tiêu dự án

Phát triển một ứng dụng Authenticator trên nền tảng iOS, cung cấp giải pháp xác thực 2 bước (2FA/MFA) toàn diện, bảo mật cao và trải nghiệm người dùng vượt trội so với các đối thủ indie hiện tại trên thị trường.

Dự án hướng tới:
- Trở thành công cụ 2FA đáng tin cậy cho người dùng cá nhân và chuyên nghiệp tại thị trường US và global, với revenue target $200K+ monthly trong 6 tháng đầu.
- Cung cấp bộ tính năng bảo mật tích hợp (2FA + Password Manager + Private Browse + VPN) giúp người dùng không cần cài nhiều app riêng lẻ — đây là điểm khác biệt cốt lõi so với nhóm branded app (Google/Microsoft Authenticator).
- Xây dựng nền tảng khai thác subscription bền vững, tận dụng know-how màn IAP intro từ các app trong công ty.

## 2. Mô tả chung

Ứng dụng Authenticator cho phép người dùng:
- Tạo và quản lý mã OTP 6 chữ số theo chuẩn TOTP (Time-based One-Time Password) cho các tài khoản yêu cầu xác thực 2 bước.
- Import tài khoản 2FA qua QR Code, nhập thủ công, ảnh, CSV, hoặc migrate từ Google/Microsoft Authenticator.
- Backup và đồng bộ token an toàn giữa các thiết bị iOS, tránh mất mã khi đổi máy.
- Bảo mật app bằng Face ID / App Password, tránh truy cập trái phép.
- Mở rộng bảo mật cá nhân qua Private Browser, Password Manager và VPN tích hợp — tập trung hóa toàn bộ nhu cầu bảo mật vào một app.

Ứng dụng được phát triển cho nền tảng iOS (iPhone là primary, iPad và Apple Watch là secondary). Mac (macOS) là target mở rộng Phase 2.

## 3. Phạm vi triển khai

Dự án được chia thành 6 cụm tính năng chính cho MVP (Phase 1) và 3 cụm bổ sung cho Phase 2:

### MVP — Phase 1

**3.1. Cụm Generate 2FA Token**  
Tạo, import và quản lý mã OTP cho các tài khoản 2FA. Đây là core feature quyết định giá trị sản phẩm.

**3.2. Cụm Security Settings**  
Bảo mật truy cập app bằng App Password và Face ID/Touch ID, ngăn người lạ xem mã OTP.

**3.3. Cụm Sync & Transfer**  
Backup token lên cloud/local, chuyển dữ liệu sang thiết bị mới, đăng nhập bằng tài khoản để đồng bộ đa thiết bị.

**3.4. Cụm Private Browse**  
Trình duyệt ẩn danh tích hợp trong app, cho phép duyệt web không để lại dấu vết.

**3.5. Cụm Password Manager**  
Lưu trữ và quản lý mật khẩu, hỗ trợ Autofill iOS, kiểm tra data bị leak.

**3.6. Cụm VPN**  
Kết nối VPN để bảo vệ kết nối Internet, hỗ trợ chọn server, protocol và Kill Switch.

### Phase 2

**3.7. Cụm Others (Widget & Apple Watch)**  
Widget iOS và Apple Watch app để xem mã OTP nhanh mà không cần mở app.

**3.8. Cụm Secure Browsing**  
Chặn quảng cáo, nội dung người lớn và tracker khi duyệt web trong app.

**3.9. Cụm Security Hub**  
Kiểm tra mức độ an toàn của mật khẩu và email, cảnh báo khi phát hiện data bị rò rỉ.

**3.10. Cụm Dark Mode**  
Hỗ trợ Dark/Light mode theo tuỳ chọn hoặc theo theme hệ thống.

## 4. Đối tượng người dùng mục tiêu

**Primary Persona — Tech-Savvy Professional (25–44 tuổi)**
- Nam/nữ, làm việc trong ngành công nghệ hoặc văn phòng sử dụng nhiều dịch vụ online.
- Đã quen với khái niệm 2FA, OTP, end-to-end encryption.
- Đang dùng Google/Microsoft Authenticator nhưng bất tiện do thiếu backup, không đồng bộ đa thiết bị.
- Sẵn sàng trả $6–$50/năm nếu sản phẩm đáp ứng tốt nhu cầu bảo mật toàn diện.
- Ưa thích UI hiện đại, thao tác nhanh, UX đơn giản — không cần đọc hướng dẫn.

**Secondary Persona — Digital Native (18–24 tuổi)**
- Dân công nghệ trẻ, hay dùng app mới, sẵn sàng thử.
- Quan tâm bảo mật tài khoản gaming, social media, crypto.
- Nhạy cảm với giá — ưu tiên gói week trial hoặc lifetime nếu có deal tốt.

**Thị trường chính:** US (chiếm 60–80% revenue theo benchmark đối thủ), tiếp theo là UK, AU, DE, BR.

## 5. User Flow tổng quan (cấp dự án)

```
[Lần đầu mở app]
  ↓
[Màn Onboarding → Màn IAP Intro (3-day free trial)]
  ↓
[Màn Home — Danh sách token (trống nếu lần đầu)]
  ↓
[User thêm token: Scan QR / Manual Input / Import]
  ↓
[Token xuất hiện trong danh sách, hiển thị mã OTP + countdown]
  ↓
[User copy mã → dùng để đăng nhập tài khoản trên nền tảng khác]
  ↓
[Các luồng nhánh từ Home:]
  ├── [Tap Security Settings → Set Password / Face ID]
  ├── [Tap Private Browse → Trình duyệt ẩn danh]
  ├── [Tap Password Manager → Xem / thêm mật khẩu]
  ├── [Tap VPN → Kết nối VPN]
  └── [Tap Backup → Sync token lên cloud hoặc xuất file]
```

## 6. Các module và mối liên kết

| Module | Vai trò chính | Liên kết với |
|--------|---------------|-------------|
| Generate 2FA Token | Core — tạo và hiển thị mã OTP, entry point của app | Security Settings, Sync & Transfer, Widget |
| Security Settings | Kiểm soát truy cập app | Tất cả module (lock/unlock gate) |
| Sync & Transfer | Backup và phục hồi dữ liệu | Generate 2FA Token, Account (cloud) |
| Private Browse | Trình duyệt ẩn danh độc lập trong app | Secure Browsing (Phase 2) |
| Password Manager | Lưu mật khẩu, Autofill iOS | Security Hub (Phase 2) |
| VPN | Bảo vệ kết nối Internet | Private Browse |
| Widget & Apple Watch | Hiển thị token nhanh ngoài app | Generate 2FA Token |
| Secure Browsing | Chặn quảng cáo / tracker trong browser | Private Browse |
| Security Hub | Cảnh báo rò rỉ dữ liệu | Password Manager |

## 7. Tiêu chí thành công (Success Criteria)

**Về hiệu năng:**
- Khởi động app và hiển thị token: ≤ 1.5 giây
- Refresh OTP countdown đúng chuẩn TOTP: sai số ≤ 500ms so với server time
- Crash-free rate ≥ 99.5%
- App size ≤ 120MB (benchmark đối thủ: 97–181MB, target cạnh tranh ở mức nhẹ)

**Về trải nghiệm người dùng:**
- RR D7 ≥ 25% (Authenticator app có tần suất dùng hàng ngày — cao hơn mức chung của Utility)
- RR D30 ≥ 15%
- App Store Rating ≥ 4.5 trên App Store
- Thời gian từ lần đầu mở app đến token đầu tiên ≤ 3 phút (Time-to-Value)

**Về kinh doanh:**
- Trial conversion rate ≥ 3% (benchmark ngành Utility/Security iOS)
- Monthly Revenue ≥ $200K trong tháng 6 kể từ launch
- Gói Year là gói khai thác chính (target chiếm ≥ 60% revenue)

**Về kỹ thuật:**
- Mã OTP được tạo hoàn toàn on-device, không gửi secret key lên server
- End-to-end encryption cho cloud backup
- Hỗ trợ ≥ 8 ngôn ngữ: EN, ES, PT, DE, FR, KR, JP, VN
- Có hệ thống tracking event đầy đủ (token_added, backup_completed, vpn_connected, paywall_shown, subscribe_success...)

## 8. Định hướng phát triển

**Phase 1 — MVP (Q3/2026):**
Hoàn thiện 6 cụm core: 2FA Token, Security Settings, Sync & Transfer, Private Browse, Password Manager, VPN. Launch App Store với IAP intro week trial.

**Phase 2 — Growth (Q4/2026):**
Ra mắt Widget iOS, Apple Watch app, Secure Browsing (ad blocker), Dark Mode, Security Hub. A/B test thêm gói Year và Lifetime trên màn IAP.

**Phase 3 — Expansion (Q1/2027):**
[Giả định] Mở rộng sang macOS, cải thiện AI-powered password suggestion, tích hợp với corporate SSO/Identity Provider cho nhóm doanh nghiệp.

---

# PHẦN B — ĐẶC TẢ TỪNG CỤM TÍNH NĂNG

---

## CỤM 1: GENERATE 2FA TOKEN (AUTHENTICATOR)

**Mục tiêu:** Cung cấp khả năng tạo và quản lý mã OTP 6 chữ số chuẩn TOTP cho tất cả các tài khoản của người dùng — đây là lý do chính để cài app.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Hiển thị & quản lý danh sách token | Main | Màn chính hiển thị tất cả token, countdown, copy mã |
| Scan QR Code | Sub | Thêm token bằng camera quét QR Code từ website/service |
| Manual Input | Sub | Nhập thủ công tên tài khoản và secret key |
| Import from Photos | Sub | Quét QR Code từ ảnh đã chụp trong thư viện |
| Import CSV | Sub | Import nhiều token cùng lúc từ file .csv |
| Export CSV | Sub | Xuất tất cả token ra file .csv để lưu trữ |
| Import từ Google / Microsoft Authenticator | Sub | Migration từ app đối thủ bằng QR multi-account |
| Create Folder | Sub | Nhóm token theo thư mục để dễ quản lý |
| Set up Guide | Sub | Hướng dẫn in-app cách thêm token cho user mới |

---

### [Main] Hiển thị & Quản lý Danh sách Token

#### 1. Mô tả

Màn Home hiển thị toàn bộ danh sách token 2FA của người dùng. Mỗi token hiển thị tên tài khoản, logo/icon dịch vụ, mã OTP 6 chữ số và thanh countdown đếm ngược thời gian còn lại. Người dùng tap để copy mã, vuốt để xóa hoặc chỉnh sửa token.

#### 2. Vị trí màn hình

AUTH_HOME_01. Flow: Mở app → (nếu đã set Security) Nhập password / Face ID → Màn Home danh sách token.

#### 3. Input

- Danh sách token từ local database (secret key, issuer, account name)
- Server time (sync để tính TOTP đúng)
- Trạng thái security lock (đã xác thực hay chưa)
- Hành động user: tap copy, swipe delete, tap edit, tap add (+)

#### 4. Output

- Danh sách token hiển thị đúng thứ tự (gần nhất copy được ưu tiên lên đầu — [Giả định])
- Mã OTP tự refresh đúng mỗi 30 giây theo chuẩn TOTP
- Countdown bar thể hiện trực quan thời gian còn lại của mã hiện tại
- Tracking: `token_list_viewed`, `token_copied`, `token_deleted`

#### 5. Tiêu chuẩn chấp nhận

- Màn Home load và hiển thị token trong ≤ 1.5 giây sau khi vượt qua màn bảo mật
- Mã OTP refresh tự động đúng mỗi 30 giây, sai số ≤ 500ms so với TOTP server standard
- Countdown bar đếm ngược trực quan, không giật lag
- Khi user tap copy: mã được copy vào clipboard ngay lập tức, hiển thị toast "Đã copy" trong 2 giây
- Token mới thêm xuất hiện ngay trong list không cần reload
- Crash-free ≥ 99.5% trong session bình thường

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Không có token nào | Hiển thị màn empty state với CTA "Thêm tài khoản đầu tiên" |
| Thời gian thiết bị lệch > 30 giây | Cảnh báo "Đồng hồ thiết bị sai — mã OTP có thể không hợp lệ", gợi ý sync time |
| Xóa token | Hiển thị confirmation dialog, không xóa ngay khi swipe |
| App bị background > 5 phút | Yêu cầu xác thực lại bằng Face ID / Password khi mở lại (nếu đã bật) |

---

### [Sub] Scan QR Code

#### 1. Mô tả

Cho phép người dùng thêm token 2FA mới bằng cách dùng camera quét QR Code được hiển thị trên website/service trong quá trình setup 2FA. Đây là cách thêm token phổ biến và nhanh nhất.

#### 2. Vị trí màn hình

AUTH_ADD_01. Flow: Home → Tap nút (+) → Chọn "Scan QR Code" → Camera mở → Quét QR → Xác nhận thông tin → Token được thêm vào Home.

#### 3. Input

- Quyền truy cập Camera (camera permission iOS)
- QR Code chứa chuỗi `otpauth://totp/...` chuẩn RFC 6238
- Hành động user: đưa camera vào vùng QR Code

#### 4. Output

- Token được parse từ QR Code (issuer, account, secret key, algorithm, digits, period)
- Màn xác nhận thông tin token trước khi lưu
- Token được thêm vào local database và hiển thị ngay trên Home
- Tracking: `qr_scan_started`, `qr_scan_success`, `qr_scan_failed`, `token_added_qr`

#### 5. Tiêu chuẩn chấp nhận

- Camera mở trong ≤ 1 giây sau khi user chọn "Scan QR Code"
- Nhận diện và parse QR Code trong ≤ 500ms kể từ khi QR vào khung hình
- Token xuất hiện trên Home ngay sau khi user xác nhận, không cần restart app
- Hỗ trợ đúng format chuẩn `otpauth://totp/` và `otpauth://hotp/`

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Chưa cấp quyền camera | Hiển thị dialog xin quyền. Nếu từ chối: hướng dẫn vào Settings bật quyền |
| QR Code không đúng format otpauth | Toast lỗi: "Mã QR không hợp lệ. Vui lòng thử lại." |
| Ánh sáng quá tối / QR bị mờ | Gợi ý "Hãy thử nhập tay Secret Key" sau 5 giây không nhận diện được |
| Token đã tồn tại | Cảnh báo "Tài khoản này đã được thêm" + option Cập nhật hoặc Bỏ qua |

---

### [Sub] Manual Input

#### 1. Mô tả

Cho phép người dùng thêm token 2FA bằng cách nhập thủ công tên tài khoản (Account Name), tên dịch vụ (Issuer) và Secret Key. Dùng khi không thể quét QR Code hoặc khi muốn nhập từ nơi lưu trữ key.

#### 2. Vị trí màn hình

AUTH_ADD_02. Flow: Home → Tap (+) → Chọn "Enter Key Manually" → Điền form → Xác nhận → Token thêm vào Home.

#### 3. Input

- Hành động user: điền form (Account Name, Issuer, Secret Key, Algorithm — mặc định SHA1, Digits — mặc định 6, Period — mặc định 30s)
- Secret Key dạng Base32

#### 4. Output

- Token được tạo và lưu vào local database
- Hiển thị ngay trên Home với mã OTP hợp lệ
- Tracking: `token_added_manual`

#### 5. Tiêu chuẩn chấp nhận

- Validate Secret Key format Base32 real-time (gạch chân đỏ nếu sai)
- Không cho submit nếu Account Name hoặc Secret Key trống
- Token mới hiển thị mã OTP hợp lệ ngay sau khi thêm (không cần chờ 30 giây)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Secret Key sai format | Inline error: "Secret Key không hợp lệ — chỉ chấp nhận ký tự A-Z và 2-7" |
| Account Name trùng với token đã có | Cảnh báo trùng tên, cho phép tiếp tục nếu user xác nhận |
| Secret Key quá ngắn (< 16 ký tự) | Warning nhẹ, không block — một số service dùng key ngắn hơn |

---

### [Sub] Import from Photos

#### 1. Mô tả

Cho phép người dùng chọn ảnh chụp QR Code từ thư viện ảnh (Photos) để import token 2FA mà không cần camera trực tiếp. Hữu ích khi user đã lưu ảnh QR Code từ trước.

#### 2. Vị trí màn hình

AUTH_ADD_03. Flow: Home → Tap (+) → Chọn "Import from Photos" → Photo Picker mở → Chọn ảnh → Parse QR → Xác nhận → Token thêm vào Home.

#### 3. Input

- Quyền truy cập Photos (photo library permission iOS)
- Ảnh chứa QR Code (JPEG/PNG)
- Hành động user: chọn ảnh từ Photo Picker

#### 4. Output

- QR Code được detect và parse từ ảnh
- Màn xác nhận token trước khi lưu (giống luồng Scan QR)
- Tracking: `token_added_photo`

#### 5. Tiêu chuẩn chấp nhận

- Photo Picker mở trong ≤ 1 giây
- Detect QR Code từ ảnh trong ≤ 2 giây sau khi chọn
- Hỗ trợ ảnh có độ phân giải tối thiểu 200x200px

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Ảnh không chứa QR Code | Toast: "Không tìm thấy mã QR trong ảnh" |
| Chưa cấp quyền Photos | Dialog xin quyền, nếu từ chối: hướng dẫn vào Settings |
| Ảnh mờ / QR không nhận diện được | Gợi ý "Thử Scan QR Code trực tiếp hoặc nhập thủ công" |

---

### [Sub] Import CSV

#### 1. Mô tả

Cho phép người dùng import nhiều token cùng lúc từ file .csv theo format chuẩn (tương thích với export của đối thủ). Phục vụ người dùng muốn chuyển số lượng lớn tài khoản từ app khác hoặc từ bản sao lưu thủ công.

#### 2. Vị trí màn hình

AUTH_ADD_04. Flow: Home → Tap (+) hoặc Settings → Chọn "Import CSV" → File Picker mở → Chọn file → Preview danh sách → Xác nhận import → Tokens thêm vào Home.

#### 3. Input

- File .csv từ Files app hoặc iCloud Drive
- Quyền truy cập Files
- Format CSV tối thiểu cần có cột: `name`, `secret` (và optional: `issuer`, `algorithm`, `digits`, `period`)

#### 4. Output

- Preview danh sách token sẽ được import (tên tài khoản, issuer)
- Số lượng token import thành công / lỗi
- Token được thêm vào Home sau khi confirm
- Tracking: `csv_import_started`, `csv_import_success`, `csv_import_partial_fail`

#### 5. Tiêu chuẩn chấp nhận

- Parse file CSV ≤ 1000 token trong ≤ 3 giây
- Hiển thị preview đủ cột: Tên, Issuer, trạng thái (hợp lệ / lỗi)
- Import thành công ≥ 95% token hợp lệ trong file
- Token trùng với dữ liệu hiện có → cho phép user chọn Skip / Overwrite

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| File không đúng format | Hiển thị lỗi, link hướng dẫn format chuẩn |
| File trống | Toast: "File CSV không có dữ liệu token hợp lệ" |
| Một số row có secret key sai | Báo cáo rõ: "X token thành công, Y token bị lỗi" + cho phép export danh sách lỗi |

---

### [Sub] Export CSV

#### 1. Mô tả

Cho phép người dùng xuất toàn bộ danh sách token ra file .csv để lưu trữ ngoài app hoặc chuyển sang app khác. File xuất bao gồm đủ thông tin để import lại hoàn chỉnh.

#### 2. Vị trí màn hình

AUTH_SETTINGS_01. Flow: Settings → "Export CSV" → Xác nhận (biometric / password nếu đã set) → File .csv lưu vào Files / Share Sheet.

#### 3. Input

- Xác thực Security (Face ID hoặc App Password) trước khi export
- Hành động user: tap Export CSV → Confirm

#### 4. Output

- File `authenticator_export_YYYYMMDD.csv` chứa toàn bộ token (name, issuer, secret, algorithm, digits, period)
- Share Sheet iOS để user chọn lưu vào Files, iCloud, AirDrop...
- Tracking: `csv_export_triggered`, `csv_export_success`

#### 5. Tiêu chuẩn chấp nhận

- Bắt buộc xác thực Security trước khi export (nếu user đã set Security)
- Xuất file trong ≤ 2 giây với ≤ 500 token
- File CSV đúng format, import lại được vào chính app hoặc app đối thủ tương thích

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User chưa set Security | Cảnh báo "Bạn chưa đặt mật khẩu bảo vệ. Xác nhận xuất không có bảo mật?" + nút Đặt mật khẩu |
| Không có token nào | Toast: "Chưa có token để xuất" |
| Lỗi ghi file | Toast lỗi, không crash |

---

### [Sub] Import từ Google / Microsoft Authenticator

#### 1. Mô tả

Cho phép người dùng migrate toàn bộ token từ Google Authenticator hoặc Microsoft Authenticator sang app bằng cách quét QR Code multi-account mà app đối thủ cung cấp trong chức năng Export của họ.

#### 2. Vị trí màn hình

AUTH_ADD_05. Flow: Home → Tap (+) → Chọn "Import from Google/Microsoft Authenticator" → Hướng dẫn cách export từ app đối thủ → Camera mở → Quét QR multi-account → Xác nhận → Tokens thêm vào Home.

#### 3. Input

- Camera để quét QR Code dạng multi-account (có thể có nhiều QR cho > 10 accounts)
- Quyền camera
- QR Code từ Google/Microsoft Authenticator export flow

#### 4. Output

- Toàn bộ token được import vào app
- Báo cáo số lượng import thành công
- Tracking: `migration_started`, `migration_success`

#### 5. Tiêu chuẩn chấp nhận

- Hướng dẫn in-app rõ ràng (Step-by-step) cách export từ Google/Microsoft Authenticator
- Nhận diện và xử lý đúng format QR multi-account của Google Authenticator
- Import chính xác tất cả token trong QR Code

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| QR Code từ app khác không phải Google/Microsoft | Toast: "Định dạng không được hỗ trợ. Thử Import CSV" |
| Scan nhiều QR Code (batch) | Hỗ trợ scan tiếp QR tiếp theo sau khi parse QR trước |

---

### [Sub] Create Folder

#### 1. Mô tả

Cho phép người dùng nhóm các token vào thư mục theo chủ đề (Work, Personal, Crypto...) để dễ quản lý khi có nhiều tài khoản.

#### 2. Vị trí màn hình

AUTH_HOME_01 (long-press token → Move to Folder) hoặc (+) → Create Folder.

#### 3. Input

- Tên thư mục do user nhập
- Hành động user: long-press token → chọn folder đích

#### 4. Output

- Thư mục mới hiển thị trên Home
- Token được nhóm đúng vào folder
- Tracking: `folder_created`, `token_moved_to_folder`

#### 5. Tiêu chuẩn chấp nhận

- Tên folder tối đa 30 ký tự
- Token bên trong folder hiển thị OTP và countdown đầy đủ (không khác gì ở Home)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Xóa folder đang có token | Hỏi: "Chuyển token về Home hay xóa tất cả?" |
| Folder trùng tên | Cảnh báo, yêu cầu đổi tên |

---

### [Sub] Set up Guide

#### 1. Mô tả

Hướng dẫn in-app dành cho user mới, giải thích 2FA là gì và cách thêm token từ các dịch vụ phổ biến (Google, Facebook, GitHub, Coinbase...). Giảm friction onboarding và tăng activation rate.

#### 2. Vị trí màn hình

AUTH_HOME_01 (empty state CTA) hoặc Help → Setup Guide.

#### 3. Input

- Hành động user: tap "Tìm hiểu cách thêm tài khoản" trên empty state

#### 4. Output

- Màn hướng dẫn step-by-step với ảnh minh họa
- Link/deeplink đến màn Scan QR / Manual Input

#### 5. Tiêu chuẩn chấp nhận

- Hướng dẫn ít nhất 5 dịch vụ phổ biến: Google, Facebook, GitHub, Twitter/X, Coinbase
- Nội dung đúng, ảnh rõ ràng

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User skip guide | Không hiện lại, có thể tìm lại trong Help |

---

## CỤM 2: SECURITY SETTINGS

**Mục tiêu:** Bảo vệ app khỏi truy cập trái phép bằng App Password và Face ID/Touch ID — là lớp bảo mật đầu tiên, tăng trust với người dùng.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Set App Password | Main | Đặt mật khẩu PIN/Passcode riêng để mở app |
| Face ID / Touch ID Unlock | Sub | Dùng sinh trắc học để unlock app nhanh hơn |

---

### [Main] Set App Password

#### 1. Mô tả

Cho phép người dùng đặt mã PIN (4–6 chữ số) hoặc passcode riêng để bảo vệ truy cập app. Mỗi lần mở app hoặc sau thời gian background, user phải nhập đúng mã mới vào được. Tính năng là optional nhưng được khuyến khích ngay từ onboarding.

#### 2. Vị trí màn hình

SECURITY_01. Flow: Settings → Security → Set App Password → Nhập PIN (2 lần để confirm) → Bật thành công.

#### 3. Input

- Hành động user: nhập PIN 4–6 chữ số, xác nhận lần 2
- Trạng thái hiện tại: có/chưa có password

#### 4. Output

- App Password được lưu (hash, không lưu plaintext)
- Từ lần sau mở app: hiển thị màn nhập PIN trước khi vào Home
- Tracking: `security_password_set`, `security_password_unlock_success`, `security_password_unlock_failed`

#### 5. Tiêu chuẩn chấp nhận

- PIN phải nhập lại đúng lần 2 mới được lưu (mismatch → thông báo, nhập lại từ đầu)
- Sau 5 lần nhập sai: lock 30 giây, sau 10 lần: lock 5 phút [Giả định]
- Màn nhập PIN load trong ≤ 0.5 giây khi mở app

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User quên PIN | Option "Xóa toàn bộ dữ liệu app" sau 10 lần sai (cảnh báo rõ hậu quả) |
| User muốn đổi PIN | Phải nhập PIN cũ đúng trước khi đặt PIN mới |
| User tắt App Password | Phải xác thực PIN hiện tại + confirm |

---

### [Sub] Face ID / Touch ID Unlock

#### 1. Mô tả

Cho phép người dùng unlock app nhanh bằng Face ID (hoặc Touch ID trên thiết bị cũ hơn) thay vì nhập PIN mỗi lần mở. Tăng UX trong khi vẫn duy trì bảo mật cao.

#### 2. Vị trí màn hình

SECURITY_01. Flow: Settings → Security → Bật Face ID/Touch ID (yêu cầu App Password đã được set).

#### 3. Input

- App Password phải được set trước (Face ID là tính năng phụ, không thể bật độc lập)
- Sinh trắc học của thiết bị (LocalAuthentication framework iOS)

#### 4. Output

- Khi mở app: trigger Face ID tự động
- Unlock thành công → vào Home
- Unlock thất bại → fallback về màn nhập PIN
- Tracking: `faceid_unlock_success`, `faceid_unlock_failed`

#### 5. Tiêu chuẩn chấp nhận

- Face ID trigger trong ≤ 0.5 giây khi app foreground
- Fallback PIN xuất hiện ngay sau Face ID fail
- Không lưu dữ liệu sinh trắc học trong app (dùng Apple LocalAuthentication, không tự xử lý)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Thiết bị không hỗ trợ Face ID / Touch ID | Ẩn option này, chỉ hiện PIN |
| Face ID bị disable ở cấp hệ thống | Hiển thị thông báo, hướng dẫn vào Settings thiết bị để bật |

---

## CỤM 3: SYNC & TRANSFER

**Mục tiêu:** Đảm bảo người dùng không bao giờ mất mã 2FA khi đổi máy, cài lại app, hoặc muốn dùng trên nhiều thiết bị — đây là nỗi đau lớn nhất khi dùng Google/Microsoft Authenticator.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Backup Code (Cloud / Local) | Main | Sao lưu token lên iCloud hoặc local file |
| Code Transfer (Device Migration) | Sub | Chuyển token sang thiết bị mới qua QR Code |
| Account Sign-in | Sub | Đăng nhập bằng tài khoản để sync đa thiết bị |

---

### [Main] Backup Code (Cloud / Local)

#### 1. Mô tả

Cho phép người dùng sao lưu toàn bộ token 2FA lên iCloud (encrypted) hoặc xuất file backup local. Khi cài lại app hoặc đổi thiết bị, user có thể restore toàn bộ token từ backup mà không phải setup lại từ đầu.

#### 2. Vị trí màn hình

BACKUP_01. Flow: Settings → Backup & Sync → Chọn "Backup to iCloud" hoặc "Save Local Backup" → Xác thực Security → Backup thực hiện.

#### 3. Input

- Xác thực Security (Face ID / App Password)
- Danh sách token từ local database
- iCloud account (nếu chọn Cloud backup)
- Lựa chọn user: iCloud hoặc local file

#### 4. Output

- Backup file được mã hóa end-to-end trước khi lưu lên iCloud
- Thông báo backup thành công + thời gian backup gần nhất
- Tracking: `backup_triggered`, `backup_success`, `backup_failed`, `restore_triggered`, `restore_success`

#### 5. Tiêu chuẩn chấp nhận

- Dữ liệu backup phải được mã hóa end-to-end (secret key không được lưu plaintext)
- Backup ≤ 100 token lên iCloud trong ≤ 5 giây (wifi)
- Restore toàn bộ token thành công, không mất dữ liệu
- Hiển thị thời gian backup gần nhất trên màn Settings

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Không đăng nhập iCloud | Hướng dẫn đăng nhập iCloud qua Settings thiết bị |
| iCloud đầy | Thông báo lỗi, gợi ý export local thay thế |
| Restore ghi đè data hiện có | Cảnh báo rõ: "Toàn bộ token hiện tại sẽ bị thay thế" + xác nhận |
| Backup file bị corrupt | Thông báo lỗi, không crash, hướng dẫn tạo backup mới |

---

### [Sub] Code Transfer (Device Migration)

#### 1. Mô tả

Cho phép người dùng chuyển toàn bộ token sang thiết bị mới bằng cách quét QR Code transfer — thiết bị cũ hiển thị QR, thiết bị mới quét. Không cần internet, an toàn hơn cloud.

#### 2. Vị trí màn hình

BACKUP_02. Flow: Settings → Transfer → Chọn "This is Old Device" (hiển thị QR) hoặc "This is New Device" (scan QR).

#### 3. Input

- Xác thực Security trước khi bắt đầu transfer
- Kết nối Local Network hoặc Bluetooth [Giả định: dùng QR encoded data]

#### 4. Output

- QR Code chứa encrypted token data (thiết bị cũ)
- Token được import đầy đủ sang thiết bị mới sau khi quét
- Tracking: `transfer_initiated`, `transfer_success`

#### 5. Tiêu chuẩn chấp nhận

- Transfer ≤ 50 token trong ≤ 30 giây qua QR
- Data được mã hóa trong QR Code, không readable nếu không có app
- Sau transfer thành công: gợi ý xóa data trên thiết bị cũ

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| QR Code quá nhiều data (> 50 tokens) | Chia thành nhiều QR, hướng dẫn quét từng bước |
| Camera thiết bị mới không nhận QR | Fallback: hướng dẫn dùng Backup & Restore qua iCloud |

---

### [Sub] Account Sign-in

#### 1. Mô tả

Cho phép người dùng đăng nhập bằng tài khoản (email hoặc Apple Sign-in) để sync token tự động giữa nhiều thiết bị iOS. Token được lưu trên server với end-to-end encryption.

#### 2. Vị trí màn hình

ACCOUNT_01. Flow: Settings → Account → Sign in (Email / Sign in with Apple) → Sync tự động.

#### 3. Input

- Email + Password hoặc Apple ID
- Internet connection

#### 4. Output

- Token sync real-time giữa các thiết bị đã đăng nhập cùng tài khoản
- Badge hiển thị trạng thái sync (Last synced: X phút trước)
- Tracking: `account_signed_in`, `sync_triggered`, `sync_success`

#### 5. Tiêu chuẩn chấp nhận

- Đăng nhập thành công trong ≤ 3 giây (wifi)
- Token sync trong ≤ 10 giây sau khi thêm mới trên một thiết bị
- End-to-end encryption: server không có khả năng đọc secret key

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Mất internet khi sync | Ứng dụng vẫn hoạt động offline, queue sync khi có mạng trở lại |
| Conflict token giữa 2 thiết bị | Giữ bản mới nhất theo timestamp |
| Đăng xuất | Hỏi: "Xóa data local hay giữ lại offline?" |

---

## CỤM 4: PRIVATE BROWSE

**Mục tiêu:** Cung cấp trình duyệt ẩn danh tích hợp trong app, cho phép duyệt web mà không để lại lịch sử — tăng giá trị của subscription bằng cách bổ sung tính năng privacy.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Private Browser | Main | Trình duyệt ẩn danh tích hợp — không lưu lịch sử, cookies |
| Create New Tab / Multi-tab | Sub | Mở nhiều tab duyệt web cùng lúc |
| Browser Tools | Sub | Copy URL, bookmark, share, reload, điều hướng |

---

### [Main] Private Browser

#### 1. Mô tả

Trình duyệt web tích hợp hoạt động ở chế độ incognito mặc định: không lưu lịch sử duyệt web, cookies, cache sau khi đóng session. Giao diện tương tự Safari, thao tác quen thuộc, phù hợp để duyệt web nhanh khi cần bảo mật.

#### 2. Vị trí màn hình

BROWSER_01. Flow: Tab bar bottom → Tap "Private Browse" → Màn trình duyệt mở với thanh địa chỉ rỗng.

#### 3. Input

- URL user nhập hoặc keyword search
- Internet connection

#### 4. Output

- Trang web được load và hiển thị đầy đủ (WKWebView)
- Không có lịch sử, cookies, cache được lưu sau khi thoát browser
- Tracking: `browser_opened`, `browser_search`, `browser_closed`

#### 5. Tiêu chuẩn chấp nhận

- Trang web load trong ≤ 3 giây với mạng 4G tốt
- Xác nhận không lưu lịch sử: sau khi restart app, không có dấu vết duyệt web
- Search bar hỗ trợ cả URL lẫn keyword (tự detect và search Google nếu là keyword)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Không có internet | Hiển thị màn lỗi offline chuẩn WebView |
| Website yêu cầu JavaScript không khả dụng | Load bình thường, không can thiệp |
| Phishing / unsafe site (Google Safe Browsing) | [Giả định] Cảnh báo trước khi navigate |

---

### [Sub] Create New Tab / Multi-tab

#### 1. Mô tả

Cho phép mở nhiều tab duyệt web song song trong Private Browser, mỗi tab độc lập về session.

#### 2. Vị trí màn hình

BROWSER_01 toolbar. Flow: Tap icon Tabs → Tab overview → Tap (+) tạo tab mới.

#### 3. Input

- Hành động user: tap nút Tab, tap (+), tap tab để switch

#### 4. Output

- Tab mới được tạo với màn trống
- Switch giữa các tab không mất state trang đang load
- Tracking: `browser_tab_created`, `browser_tab_closed`

#### 5. Tiêu chuẩn chấp nhận

- Hỗ trợ tối đa 10 tab đồng thời [Giả định]
- Switch tab trong ≤ 300ms

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Đạt giới hạn 10 tab | Toast: "Đã đạt giới hạn tab, đóng tab cũ trước" |

---

### [Sub] Browser Tools

#### 1. Mô tả

Thanh công cụ trình duyệt cung cấp các thao tác tiêu chuẩn: copy URL, mở trang mới, bookmark trang, share, reload, điều hướng back/forward.

#### 2. Vị trí màn hình

BROWSER_01 bottom toolbar.

#### 3. Input

- Hành động user: tap từng icon trên toolbar

#### 4. Output

- Copy URL: URL vào clipboard + toast "Đã copy"
- Bookmark: Trang được lưu vào danh sách Bookmarks trong app
- Share: iOS Share Sheet mở
- Reload: trang reload
- Back/Forward: điều hướng đúng

#### 5. Tiêu chuẩn chấp nhận

- Bookmark lưu đúng URL và title trang
- Share Sheet mở trong ≤ 500ms

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Trang chưa load xong → tap share | Share URL hiện tại (có thể chưa phải final URL nếu redirect) |

---

## CỤM 5: PASSWORD MANAGER

**Mục tiêu:** Cho phép người dùng lưu và quản lý mật khẩu tập trung trong app, tích hợp iOS Autofill để dùng mật khẩu không cần nhớ — mở rộng giá trị subscription "all-in-one security".

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Add & Edit Passwords | Main | Thêm / sửa thông tin đăng nhập của các website, app |
| Autofill | Sub | Tích hợp iOS Credential Provider để Autofill mật khẩu |

---

### [Main] Add & Edit Passwords

#### 1. Mô tả

Cho phép người dùng thêm, xem, chỉnh sửa và xóa thông tin đăng nhập (website URL, username, password) trong Password Manager tích hợp. Dữ liệu được mã hóa on-device.

#### 2. Vị trí màn hình

PWD_01. Flow: Tab bar → Password Manager → Danh sách mật khẩu → Tap (+) → Điền form → Lưu.

#### 3. Input

- Xác thực Security (Face ID / App Password) khi vào Password Manager
- Hành động user: nhập Website URL, Username, Password
- Optional: Notes, Category

#### 4. Output

- Mật khẩu lưu vào encrypted local database
- Hiển thị trong danh sách Password Manager
- Tracking: `password_added`, `password_edited`, `password_deleted`, `password_viewed`

#### 5. Tiêu chuẩn chấp nhận

- Password field có nút show/hide (mặc định hidden)
- Có nút "Generate Strong Password" (tạo mật khẩu ngẫu nhiên mạnh)
- Copy username / copy password bằng tap

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| URL không hợp lệ | Warning nhẹ nhưng không block (user có thể lưu note tùy ý) |
| Trùng entry (same URL + username) | Cảnh báo trùng, cho phép tiếp tục |

---

### [Sub] Autofill

#### 1. Mô tả

Tích hợp iOS Credential Provider Extension để app xuất hiện như một nguồn Autofill khi user login vào website/app khác trên iPhone. User tap Autofill → chọn mật khẩu từ app → tự điền vào form.

#### 2. Vị trí màn hình

Nằm ngoài app, trong iOS Autofill menu (xuất hiện ở QuickType bar hoặc Passwords icon trên keyboard).

#### 3. Input

- URL của trang đang login (iOS truyền vào Extension)
- Xác thực Face ID / App Password trước khi cung cấp mật khẩu

#### 4. Output

- Danh sách mật khẩu phù hợp với URL hiển thị trong Autofill
- Mật khẩu điền tự động vào form sau khi user chọn
- Tracking: `autofill_triggered`, `autofill_success`

#### 5. Tiêu chuẩn chấp nhận

- Extension setup: hướng dẫn user bật trong Settings → Passwords → Password Options → chọn app
- Autofill list hiển thị đúng mật khẩu match với domain đang login
- Không cache mật khẩu ở nơi không an toàn ngoài app sandbox

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User chưa bật Autofill trong Settings iOS | In-app prompt hướng dẫn bật |
| Không có mật khẩu match domain | Hiển thị toàn bộ list để user chọn thủ công |

---

## CỤM 6: VPN

**Mục tiêu:** Cung cấp kết nối VPN để bảo vệ traffic internet của người dùng, đặc biệt khi dùng wifi công cộng — đây là tính năng premium quan trọng, có màn IAP riêng theo benchmark đối thủ.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Kết nối VPN | Main | Bật/tắt VPN, chọn server, xem trạng thái kết nối |
| Choose Server | Sub | Chọn quốc gia/server VPN để kết nối |
| Select Protocol | Sub | Chọn protocol kết nối VPN (IKEv2, WireGuard...) |
| Kill Switch | Sub | Tự động ngắt internet nếu VPN mất kết nối |

---

### [Main] Kết nối VPN

#### 1. Mô tả

Cho phép người dùng bật/tắt kết nối VPN bằng một nút duy nhất. Hiển thị trạng thái kết nối (Connected / Connecting / Disconnected), địa chỉ IP ảo và thời gian đã kết nối.

#### 2. Vị trí màn hình

VPN_01. Flow: Tab bar → VPN → Màn VPN với nút Connect lớn ở giữa.

#### 3. Input

- Hành động user: tap Connect / Disconnect
- Server đã chọn (mặc định: server tốt nhất tự động — [Giả định])
- Network permission (VPN configuration permission iOS)

#### 4. Output

- Kết nối VPN được thiết lập qua iOS NetworkExtension framework
- Badge "VPN" hiển thị trên status bar iOS
- Hiển thị: IP ảo, server location, uptime
- Tracking: `vpn_connect_triggered`, `vpn_connected`, `vpn_disconnected`, `vpn_connect_failed`

#### 5. Tiêu chuẩn chấp nhận

- Kết nối VPN thành công trong ≤ 5 giây (server gần)
- Hiển thị đúng IP ảo sau khi kết nối
- Ngắt kết nối sạch trong ≤ 2 giây

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Lần đầu dùng — chưa cấp VPN permission | iOS dialog xin quyền tự động xuất hiện |
| Kết nối thất bại | Retry tối đa 2 lần, sau đó hiển thị lỗi và gợi ý đổi server |
| Mất mạng khi đang kết nối VPN | Auto reconnect khi có mạng trở lại |
| Không phải user Premium | Trigger màn IAP VPN offer |

---

### [Sub] Choose Server

#### 1. Mô tả

Danh sách server VPN theo quốc gia, cho phép user chọn server để tối ưu tốc độ hoặc unlock nội dung địa lý cụ thể.

#### 2. Vị trí màn hình

VPN_01 → Tap "Server Location" → VPN_SERVER_01 (danh sách server).

#### 3. Input

- Tap vào server/quốc gia muốn kết nối

#### 4. Output

- Server được chọn, kết nối VPN sử dụng server này
- Hiển thị ping/latency của từng server (nếu có)

#### 5. Tiêu chuẩn chấp nhận

- Danh sách server load trong ≤ 2 giây
- Hỗ trợ tối thiểu 10 quốc gia [Giả định theo benchmark đối thủ]
- Server "Best / Auto" luôn là option đầu tiên

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Server đang bảo trì | Đánh dấu unavailable, không cho chọn |

---

### [Sub] Select Protocol

#### 1. Mô tả

Cho phép user chọn protocol kết nối VPN để tối ưu theo nhu cầu (tốc độ vs bảo mật). Option nâng cao, dành cho user tech-savvy.

#### 2. Vị trí màn hình

VPN_01 → Settings → VPN Protocol.

#### 3. Input

- Hành động user: chọn protocol từ dropdown

#### 4. Output

- Kết nối VPN sử dụng protocol đã chọn từ lần tiếp theo

#### 5. Tiêu chuẩn chấp nhận

- Hỗ trợ tối thiểu 2 protocol: IKEv2 và WireGuard [Giả định]
- Mặc định: Auto (chọn protocol tốt nhất)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| Protocol không hỗ trợ trên server đang chọn | Fallback sang Auto, thông báo user |

---

### [Sub] Kill Switch

#### 1. Mô tả

Tự động ngắt toàn bộ kết nối internet nếu VPN mất kết nối đột ngột, đảm bảo không có traffic nào bị lộ khi VPN drop. Tính năng bảo mật nâng cao cho user có yêu cầu privacy cao.

#### 2. Vị trí màn hình

VPN_01 → Settings → Kill Switch toggle.

#### 3. Input

- User bật/tắt Kill Switch toggle
- Sự kiện VPN drop

#### 4. Output

- Khi VPN drop + Kill Switch ON: internet bị block ngay lập tức
- Notification: "VPN mất kết nối — Kill Switch đang bảo vệ bạn"
- Khi VPN reconnect: internet hoạt động trở lại
- Tracking: `kill_switch_enabled`, `kill_switch_triggered`

#### 5. Tiêu chuẩn chấp nhận

- Internet bị block trong ≤ 1 giây sau khi VPN drop
- Notification xuất hiện trong ≤ 2 giây

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User tắt Kill Switch khi VPN đang mất kết nối | Internet khôi phục ngay |

---

## CỤM 7: OTHERS — WIDGET & APPLE WATCH

> [Giả định: Phase 2 theo roadmap — đặc tả sơ bộ để Dev chuẩn bị architecture]

**Mục tiêu:** Tăng tiện lợi truy cập mã OTP mà không cần mở app, cải thiện retention hàng ngày.

| Tính năng | Loại | Mô tả ngắn |
|-----------|------|-------------|
| Widget iOS | Main | Hiển thị mã OTP trên màn Home Screen / Lock Screen |
| Apple Watch App | Sub | Xem mã OTP trực tiếp trên Apple Watch |
| Support via User ID | Sub | Auto tạo User ID giúp team support tracking issue |

---

### [Main] Widget iOS

#### 1. Mô tả

Widget hiển thị mã OTP của token được pin sẵn trực tiếp trên Home Screen hoặc Lock Screen iOS (WidgetKit). User xem và copy mã mà không cần mở app — giảm friction rất lớn trong tình huống daily use.

#### 2. Vị trí màn hình

iOS Home Screen / Lock Screen (ngoài app). User thêm widget từ Widget Gallery của iOS.

#### 3. Input

- Token user chọn để hiển thị trên widget
- Cập nhật mã OTP mỗi 30 giây (WidgetKit timeline)

#### 4. Output

- Widget hiển thị: tên tài khoản, mã OTP, countdown
- Tap widget → mở app vào màn token tương ứng
- Tracking: `widget_added`, `widget_tapped`

#### 5. Tiêu chuẩn chấp nhận

- Mã OTP trên widget chính xác, sync đúng với mã trong app
- Widget hỗ trợ kích thước Small và Medium
- Refresh đúng mỗi 30 giây (do WidgetKit rate-limit, có thể delay ≤ 5 giây — chấp nhận được)

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| App bị uninstall | Widget hiển thị placeholder, không crash |
| Security lock đang bật | Widget hiển thị "Mở app để xem mã" thay vì OTP [Giả định — cần PM confirm về security policy cho widget] |

---

### [Sub] Apple Watch App

#### 1. Mô tả

App companion trên Apple Watch hiển thị danh sách token và mã OTP, cho phép user xem mã ngay từ cổ tay mà không cần lấy điện thoại ra.

#### 2. Vị trí màn hình

Trên Apple Watch (watchOS app). Sync data từ iPhone app qua WatchConnectivity.

#### 3. Input

- Danh sách token từ iPhone app (sync qua WatchConnectivity)
- Digital Crown để scroll danh sách

#### 4. Output

- Danh sách token và mã OTP hiển thị trên Watch
- Countdown ring quanh mã OTP
- Tracking: `watch_app_opened`, `watch_token_viewed`

#### 5. Tiêu chuẩn chấp nhận

- Sync token từ iPhone sang Watch trong ≤ 5 giây khi cả hai online
- Mã OTP đúng, countdown chính xác

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| iPhone không kết nối Watch | Watch hiển thị dữ liệu cached (có thể mã đã cũ — cảnh báo) |

---

### [Sub] Support via User ID

#### 1. Mô tả

App tự động tạo một User ID duy nhất (UUID) cho mỗi installation. User có thể chia sẻ ID này với team support khi gặp sự cố, giúp tracking log và debug nhanh hơn mà không cần user cung cấp thông tin cá nhân.

#### 2. Vị trí màn hình

Settings → Support → User ID (hiển thị UUID + nút Copy).

#### 3. Input

- Auto-generate khi cài app lần đầu
- Hành động user: tap Copy ID

#### 4. Output

- User ID được hiển thị và copy vào clipboard
- ID được gửi kèm trong mọi error log / analytics event

#### 5. Tiêu chuẩn chấp nhận

- User ID được generate một lần, không thay đổi trừ khi reinstall app
- ID là UUID v4 format

#### 6. Case ngoại lệ

| Case | Xử lý |
|------|--------|
| User reinstall app | Generate UUID mới (không khôi phục ID cũ) |

---

# GHI CHÚ CHO PM — ĐIỂM CẦN REVIEW

1. **Widget Security Policy:** Widget có hiển thị OTP khi màn hình khoá không? Cần PM confirm — ảnh hưởng đến UX và security trade-off.

2. **VPN Backend:** File chưa có thông tin về VPN provider (self-hosted hay 3rd-party như WireGuard Cloud?). Cần xác nhận trước khi đặc tả kỹ hơn phần AI Requirement / API.

3. **Phase Roadmap:** Sheet "Xác định tính năng" có cột MVP/Phase 2-4 nhưng chưa điền. Tài liệu này đang giả định Phase 1 = 6 cụm core (2FA, Security, Sync, Browser, Password, VPN) và Phase 2 = Widget, Secure Browsing, Security Hub, Dark Mode. PM xác nhận để update roadmap.

4. **API Google Check Password (ghi chú trong file):** Cần confirm a Cường xem API Google Safe Browsing / Leaked Password Check khả dụng không — ảnh hưởng đến phần "Check leaked data" trong Password Manager và Security Hub (Phase 2).

5. **Monetization IAP:** File nghiên cứu đề cập IAP intro cho VPN riêng (như benchmark đối thủ "Authenticator ·"). PM cần confirm cấu trúc IAP: 1 màn duy nhất cho toàn bộ premium hay có màn VPN offer riêng?

6. **Set up Guide:** Danh sách dịch vụ hướng dẫn (Google, Facebook, GitHub, Twitter/X, Coinbase) là giả định — PM có thể bổ sung hoặc điều chỉnh.
