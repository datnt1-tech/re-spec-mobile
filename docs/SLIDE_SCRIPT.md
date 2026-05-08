# Script thuyết trình re-spec-mobile

**Mục đích**: text bạn đọc trong lúc trình bày 18 slide. Mỗi section ứng với 1 slide. Bao gồm giải thích thuật ngữ inline (đặt trong ngoặc đơn).

**Thời lượng dự kiến**: 30-40 phút nếu đọc đều, có dừng cho audience hỏi. Có thể rút gọn xuống 15-20 phút bằng cách bỏ phần "Giải thích thuật ngữ" cho audience đã quen technical.

**Tone**: chuyên nghiệp nhưng thân thiện. Có thể paraphrase, không cần đọc đúng từng chữ.

---

## Slide 1 — Title (1 phút)

> Xin chào mọi người. Hôm nay tôi muốn giới thiệu với mọi người một project tôi đang phát triển có tên **re-spec-mobile**. Đây là **toolkit reverse-engineering** cho app mobile — nói nôm na là một bộ công cụ giúp ta "moi" lại spec từ một app đã có sẵn.

> Với mọi người chưa quen, **reverse-engineering** trong context này không có nghĩa là đập app ra để lấy code. Mình KHÔNG đụng đến source code của app gốc. Cái mình làm là quan sát app từ phía người dùng — tap, swipe, đọc UI — rồi suy ra cấu trúc của nó.

> Output là **5 file markdown / feature** + **1 graph database queryable**. Engineer, designer, hoặc thậm chí 1 con AI agent đều có thể đọc và rebuild lại app trên cả iOS và Android, mà không cần chạy app gốc.

> Hôm nay tôi sẽ đi qua 18 slide trong khoảng 30 phút. Có gì thắc mắc anh em cứ ngắt giữa chừng nhé.

---

## Slide 2 — Vấn đề (2 phút)

> Trước khi vào giải pháp, chúng ta cần hiểu rõ vấn đề. Khi một team product cần spec lại 1 app — có thể là app đối thủ, có thể là app cũ team mình tự viết nhưng mất doc, có thể là app inspiration để học UX — chúng ta gặp 3 nỗi đau chính.

> **Pain thứ nhất — manual capture**. Cách truyền thống là mở app ra, screenshot từng màn, viết note vào Excel hay Notion. Vấn đề là note rời rạc, không trace được flow đầy đủ — kiểu user tap nút này thì đi đâu, swipe trái thì sao. Kết quả: 1 dev nhận task rebuild app sẽ tranh cãi với designer cả tháng vì hiểu khác nhau ở chỗ chưa được capture.

> **Pain thứ hai — PM với AI scope drift**. Đây là cái rất phổ biến khi team dùng AI để auto-test hoặc auto-spec. AI nó capture cái nó nghĩ là quan trọng, không phải cái Product Manager muốn. Sau 4 tiếng auto-test, mở ra xem thì 70% scope cần thì AI bỏ qua, còn 30% screen vô nghĩa thì capture đầy đủ. Đây là failure mode số 1.

> **Pain thứ ba — và đây là pain quan trọng nhất cho slide hôm nay** — doc cũ **không phải machine-readable**. Nghĩa là nếu sau khi PM viết spec xong, đưa cho 1 con coding agent — ví dụ Claude Code, Cursor, Copilot — để nó rebuild app, agent phải grep mò trong 50 trang prose tự do. Không có anchor để cross-link giữa screen và API. Acceptance criteria viết kiểu "AI gửi tin nhắn ngắn gọn" thì agent không gen test được. Spec với code không live cùng nhau, drift theo thời gian. Coding agent về cơ bản phải đoán mò.

> Để tôi giải thích thuật ngữ "**anchor**" cho anh em nào chưa quen — đó là cái ID duy nhất gắn vào mỗi heading trong markdown, ví dụ `feature/screen/landing`. Nó giống như cái mục lục cho phép tool tự động link từ chỗ A sang chỗ B trong doc, hoặc query "cho tôi mọi screen của feature today".

---

## Slide 3 — Giải pháp (2 phút)

> Giải pháp của chúng tôi gồm **4 trụ cột**.

> **Trụ thứ nhất — App-agnostic**. Nghĩa là toolkit này dùng được cho **bất kỳ app Android nào**, không hard-code cho 1 app cụ thể. Mọi giá trị riêng của app — tên package, viewport screen, blocklist các nút không được tap, bottom nav tab — đều ghi vào 1 file `.spec-profile.yml` đặt trong project root. Đổi app khác chỉ cần đổi profile.

> **Trụ thứ hai — PM-driven, async**. Workflow có 3 cổng kiểm duyệt — chúng tôi gọi là "gate" — do PM ký. Gate 1 chốt scope trước khi capture. Gate 2 audit coverage sau capture. Gate 3 review spec trước khi commit. Mỗi gate đều có **Telegram bridge** — nghĩa là PM không cần ngồi dán mặt vào Claude Code, có thể trả lời trực tiếp trong Telegram, tool tự fold câu trả lời ngược vào file spec.

> **Trụ thứ ba — Cross-platform**. Đây là phần tôi rất tự hào. Output của chúng tôi có 1 layer riêng tên là Layer 5 — app_overview — được thiết kế **platform-agnostic**, nghĩa là không nhắc framework cụ thể nào. Có 1 cái linter tự động cảnh báo nếu trong doc xuất hiện token như `Compose` của Android hay `SwiftUI` của iOS. Mục đích: team iOS đọc cùng 1 doc với team Android, không phải dịch lại.

> **Trụ thứ tư — và đây là điểm bán hàng mạnh nhất** — Agent-queryable spec graph. Spec không chỉ là markdown cho người đọc, mà còn được parse thành 1 cái **graph database**: nodes — là các screen, component, API, data model — và edges — là quan hệ giữa chúng. Plus **MCP server** — chúng ta sẽ giải thích MCP ở slide sau — expose 8 tool query lên graph này. Coding agent gọi API thay vì grep mò 50 trang md.

---

## Slide 4 — Architecture (2 phút)

> Về kiến trúc, project chia thành **3 bucket**, mỗi bucket có cơ chế cài đặt riêng.

> **Bucket thứ nhất — `src/`**. Đây là Python package thuần, cài qua `pip install`. Bao gồm 16 module Python — code chính của tool — cộng với thư mục `_data/` chứa template, canonical sample, shell script. Khi bạn chạy `pip install`, Python tự package luôn cả `_data/` vào wheel.

> **Bucket thứ hai — `skills/`**. Đây là thư mục chứa file `SKILL.md` — đây là một concept của Claude Code. Khi user gõ `/re-spec-mobile` trong Claude Code session, Claude tự load file SKILL.md này và làm theo workflow trong đó. File này dài khoảng 500 dòng, chứa toàn bộ logic 11 phase của workflow.

> Để giải thích **Claude Code** cho anh em nào chưa biết — đây là một CLI agent của Anthropic, chạy trong terminal, có thể đọc file, edit code, chạy lệnh shell. Nó có concept "skill" giống như plugin — file markdown đặc biệt mà Claude tự load và follow.

> **Bucket thứ ba — `agents/`**. Hai file markdown là `app-explorer.md` và `spec-writer.md`. Đây là **sub-agent** — concept nữa của Claude Code. Skill orchestrator chính có thể "gọi" sub-agent để delegate task. App-explorer phụ trách điều khiển device qua adb để capture screen. Spec-writer phụ trách viết prose markdown.

> Bucket 2 và 3 là **symlink** vào thư mục `~/.claude/` của user. Khi user `git pull` về phiên bản mới, skill và agent tự update mà không cần reinstall.

> Cuối cùng có file `INSTALL.sh` — chạy 1 lệnh là làm cả 3 bucket trong 1 phát.

---

## Slide 5 — Layer 0/1/2 — Foundation (3 phút)

> Bây giờ vào phần quan trọng nhất — **output của project**. Output là 5 layer markdown / feature, plus 1 layer / app. Slide này nói về 3 layer đầu — phase capture và observe.

> **Layer 0 — `scope.md`**. Đây là file PM viết **TRƯỚC khi capture**. Trong này PM định nghĩa cluster — là những nhóm màn hình cùng functional purpose. Mỗi cluster PM phân loại: `must_visit` — bắt buộc capture; `optional_visit` — capture nếu còn budget; `out_of_scope` — bỏ qua hoàn toàn. Plus PM ghi `Open Questions` — những thứ PM chưa rõ, cần answer trước khi capture chạy.

> File này có status flow: bắt đầu là `draft`, PM ký xong thành `signed_off`. Capture agent từ chối start nếu chưa `signed_off`. Đây là Gate 1 — chặn AI capture trượt scope.

> **Layer 1 — `observations.md`**. Đây là **transcript thô** của UI. Mỗi screen có 1 section. Trong section ghi: **bảng bounds** 5 cột — class, bounds, clickable, text, content-description. Bounds là tọa độ rectangle của element, ví dụ `[100, 200][980, 260]`. Sticky vs scrollable region — sticky là vùng giữ nguyên khi scroll, đọc bằng cách so bounds qua các capture `_a`, `_b`, `_c`. No-op silent — là tap vào element trông tương tác nhưng không dẫn đi đâu, không có visual change. Animation note. Variant A/B đã quan sát được. Accessibility trap — ví dụ Compose Popup invisible với a11y.

> Để giải thích **a11y** — viết tắt của accessibility, là "a" cộng 11 ký tự cộng "y". A11y tree là **cấu trúc cây dữ liệu mô tả UI** mà screen reader hoặc automation tool đọc được. Mỗi UI element trên Android sinh ra 1 a11y node với class, text, bounds, clickable... Project này dùng a11y tree làm source of truth — không có nó thì không capture được structure.

> **Layer 2 — `spec.md`**. Đây là **block-level structure**. Một feature thường có 5 đến 15 block. Ví dụ feature today của bible-agent có 12 block — Welcome, Calendar, Session Reader, Streak, etc. Mỗi block là 1 cluster screen cùng phục vụ 1 mục đích. File này chứa: nav_edges — các edge giữa screen, có cờ `external: true` cho edge cross-feature. Mermaid flowchart — chính là sơ đồ flow user thấy. State machine — vẽ bằng Mermaid stateDiagram cho lifecycle nếu feature có state ý nghĩa.

> Mermaid là 1 syntax để vẽ diagram bằng text — markdown render được trên GitHub, GitLab, Notion. Đây là cách rẻ nhất để có diagram **trong** file spec, không cần ảnh ngoài.

---

## Slide 6 — Layer 3/4/5 — Implementation & Overview (3 phút)

> Tiếp 3 layer sau — phase implementation và overview.

> **Layer 3 — `feature_spec.md`** — đánh dấu sao vì đây là **layer quan trọng nhất cho coding agent**. File này có structure cứng 9 section, không được skip section nào.

> - Section 1: Metadata — bảng app, package, version, status.
> - Section 2: Tổng quan — KPI sản phẩm, flow chart, metrics tracking event.
> - Section 3: Per-screen — mỗi screen có state class, components rendered, data dependency, interaction.
> - Section 4: Cross-screen invariants — invariant nghĩa là rule giữ nguyên qua nhiều màn, ví dụ "streak number không reset khi switch tab".
> - Section 5: API contract — đây là **JSON Schema**. Mỗi endpoint khai bằng `$schema`, `type`, `properties`. Có tool `extract_contracts.py` parse các block này thành OpenAPI sau.
> - Section 6: Data model — viết bằng Kotlin `data class`. Lưu ý: **Kotlin syntax là illustrative, không phải bắt buộc target Android**. Coding agent rebuild iOS sẽ tự dịch sang Swift `struct`. SPEC_SCHEMA có bảng mapping cụ thể.
> - Section 7: Open Questions — flag mọi mơ hồ, có anchor để cross-reference.
> - Section 8: Acceptance criteria — phải **measurable**, có số và đơn vị. Ví dụ "Landing render trong 1 giây cold start" — có số 1, có đơn vị giây.
> - Section 9: References — link đến observations và spec.

> **JSON Schema** là 1 format chuẩn hoá để mô tả shape của JSON data — required fields, nullable, type, format. Có codegen tool có sẵn cho mọi platform.

> **Layer 4 — `coverage_report.md`**. File này tự động sinh sau khi capture xong. Tool diff scope.md vs nav_graph thực tế và liệt: `gaps` — anchor in scope nhưng MISS capture; `drift` — capture được nhưng OUT-of-scope. Plus `decisions` — ghi action item của PM. Status flip từ `draft` sang `sign_off_pass` hoặc `sign_off_fail`. PM có thể flip status qua Telegram — chỉ cần reply `pass tốt rồi` hoặc `fail thiếu screen X`, tool tự update file.

> **Layer 5 — `app_overview.md`** — đánh dấu sao vì đây là layer **platform-agnostic** dùng cho cả iOS rebuild và stake-holder không tech. Có 1 file duy nhất / app, không phải / feature. Cấu trúc: 10 section auto-generated từ spec graph + 5 section prose designer/PM viết tay. Auto section bọc trong HTML marker — kiểu `<!-- AUTO:SITEMAP START -->` — để khi chạy lại tool, nó refresh phần auto mà preserve prose. Có **linter** cấm token framework-specific như Compose, SwiftUI, Activity, Storyboard ngoài code fence — đảm bảo doc thực sự agnostic.

---

## Slide 7 — Workflow (2-3 phút)

> Workflow gồm **11 phase**, **3 PM gate**. Tôi đi qua nhanh.

> **Phase 0** — bootstrap. Chạy 1 lần / project. Tạo file `.spec-profile.yml` skeleton, scaffold thư mục spec/.

> **Phase 1** — kickoff. PM nói cần spec feature gì.

> **Phase 1.5 — Gate 1 scope contract**. PM viết scope.md, ký. Telegram-aware: PM trả lời Open Questions trong chat thay vì sửa file tay.

> **Phase 2** — capture loop. Delegate cho sub-agent app-explorer. Agent điều khiển adb tap, swipe, gọi `re-spec-capture` để dump screen. adb là Android Debug Bridge — công cụ command-line giao tiếp với device qua USB.

> **Phase 3 — stuck handoff**. Khi capture loop bị stuck — ví dụ modal trap không dismiss được, captcha xuất hiện, paywall — agent post lên Telegram cho PM. PM reply 1 trong 4 verdict: `action` — chỉ thị tap, agent thực hiện; `manual` — yêu cầu user thao tác device; `skip` — bỏ qua; `abort` — dừng feature. Plus có **auto-skip threshold**: cùng 1 screen stuck 3 lần liên tiếp → tự auto-skip không spam PM.

> **Phase 4** — coverage check intermediate. Liệt clickable nào chưa cover.

> **Phase 4.5 — Gate 2 coverage report**. Tool sinh report, PM ký pass/fail qua Telegram.

> **Phase 5** — spec writing. Delegate cho sub-agent spec-writer. Agent đọc dump JSON + screenshot, viết Layer 1, 2, 3 cho feature.

> **Phase 5.5 — Gate 3 spec Q&A**. Spec có thể có Open Questions §7. PM trả lời inline qua Telegram, tool fold ngược vào file. Sau đó gọi spec-writer lại với mode=revise — rẻ hơn mode=draft — để fold câu trả lời vào sections liên quan.

> **Phase 6** — build graph + validate. Parse YAML frontmatter của tất cả md file, sinh nodes.json + edges.json + index.json. Validate broken refs.

> **Phase 7** — commit thủ công. Đây là điểm cuối cùng có human review. Workflow KHÔNG bao giờ tự `git commit`.

> **Phase 8** — app overview synthesis. Sau khi có ít nhất 2 feature đã commit, chạy `re-spec-app-overview` để sinh / refresh Layer 5. Idempotent — chạy lại bao nhiêu lần cũng OK, prose preserve.

> **Tại sao có 3 gate?** Vì PM-AI scope drift là failure mode #1. Nếu skip gate, AI sẽ capture cái nó nghĩ là cần, không phải cái team thật sự cần. 3 gate ép buộc reset alignment giữa người và AI tại 3 milestone quan trọng.

---

## Slide 8 — Spec Graph + MCP (3 phút)

> Đây là slide đặc biệt — differentiator chính của project so với mọi tool spec khác.

> **Spec graph là gì?** Khi tất cả 5 layer markdown đã viết xong, tool `re-spec-build-graph` parse YAML frontmatter của mọi file md, sinh ra 3 file JSON ở thư mục `_graph/`:

> - `nodes.json` — list mọi node. 11 type: feature, screen, block, component, api, data_model, criterion, invariant, question, state, cluster.
> - `edges.json` — list mọi quan hệ. 9 type: navigates_to, renders_component, reuses_component, returns_model, belongs_to_feature, references, etc.
> - `index.json` — fast lookup, map từ anchor sang `{type, feature, file, line, label}`.

> Output là **deterministic**, sorted — diff trên git readable. Idempotent — chạy lại không đổi gì nếu input không đổi.

> **MCP là gì?** MCP viết tắt của **Model Context Protocol**. Đây là 1 protocol mở do Anthropic publish năm 2024, cho phép AI agent — Claude, Cursor, Copilot, etc. — gọi tool external qua JSON-RPC 2.0 stdio. Nói cách khác, MCP là cái cho phép AI "nói chuyện" với database / file system / API external một cách standardized.

> Project chúng tôi có sẵn **MCP server** — file `re-spec-mcp-server` — expose **8 tool query** lên spec graph:

> - `spec_show(anchor)` — lấy chi tiết 1 node + edges in/out + file:line.
> - `spec_list(kind, feature?)` — list mọi node của 1 type, ví dụ "cho tôi mọi screen".
> - `spec_feature(name)` — summary 1 feature: bao nhiêu screen, component, AC.
> - `spec_reuses(key?)` — list component shared cross-feature. Đây là gold cho design system discovery.
> - `spec_path(src, dst, depth?)` — BFS tìm shortest path từ screen A đến screen B. BFS là Breadth-First Search, thuật toán tìm đường ngắn nhất.
> - `spec_acceptance(feature)` — mọi acceptance criterion của 1 feature.
> - `spec_search(query)` — substring match trên anchor và label.
> - `spec_stats()` — graph totals.

> **Cách dùng practical**: coding agent rebuild iOS gọi `spec_path('auth/screen/landing', 'today/screen/detail')` để biết flow đi qua đâu. Hoặc gọi `spec_reuses('session_reader')` để xem component này dùng ở feature nào — biết engineer rebuild 1 lần parameterise.

> Server **auto-rebuild** khi md file mtime mới hơn nodes.json — không cần manual refresh. Spec luôn fresh.

> Đây là điểm khác biệt mạnh: thay vì coding agent đọc 50 trang prose mò, nó **query precise**. Một câu hỏi `spec_path(...)` trả về JSON 5 dòng. Tiết kiệm context window, tăng accuracy.

---

## Slide 9 — Telegram bridge (2 phút)

> Telegram bridge là cách PM review async — không phải dán mặt vào Claude Code session.

> **Module** `pm_channel.py` viết hoàn toàn bằng Python stdlib `urllib`, **không thêm dependency mới**. Lý do: Telegram Bot API chỉ là REST + JSON, không cần SDK riêng.

> **3 kind message** tương ứng 3 use case:

> - `question` — cho Gate 1 scope và Gate 3 spec. Bot post mỗi Open Question lên Telegram. PM reply text tự do. Tool fold ngược vào dòng `**PM answer**:` dưới anchor `{#feature/question/q_NN}`.
> - `coverage_signoff` — cho Gate 2. Bot post tóm tắt §1 Summary của coverage_report. PM reply format `pass <ghi chú>` hoặc `fail <lý do>`. Tool flip status frontmatter và append vào `decisions:`.
> - `stuck_help` — cho Phase 3. Bot post mô tả screen stuck, lý do, 3 option. PM reply 1 trong 4 verdict: action, manual, skip, abort.

> **Auth model**: bot token đọc từ env variable `TELEGRAM_BOT_TOKEN`, KHÔNG bao giờ commit vào yml file. Chat ID lưu trong profile. Token nếu lộ vào git history thì coi như compromised — phải `/revoke` qua @BotFather và sinh token mới.

> **Auto-skip threshold**: cùng 1 screen_label đã skip 3 lần liên tiếp → ask_stuck_help tự return verdict=auto_skip không post lên Telegram nữa. Tránh spam PM cho stuck không cứu được.

> **State persist** ở 2 file gitignored:
> - `.pm_inbox.json` — mapping `telegram_message_id → anchor`. Để sync biết reply về câu nào.
> - `.stuck_log.json` — audit log mọi stuck event của feature.

---

## Slide 10 — App overview Layer 5 (2-3 phút)

> Layer 5 — app_overview — là layer cross-feature. 1 file duy nhất / app, **platform-agnostic**.

> **10 section auto-generated** từ spec graph:

> - **IDENTITY** — metadata app: tên, package, locale, viewport, stack.
> - **INVENTORY** — bảng feature × counts: screen, block, component, API, data model, etc.
> - **SITEMAP** — mọi screen, group by feature, kèm hash và capture file.
> - **CROSS_NAV** — Mermaid diagram chỉ các edge có cờ `external: true`, tức là cross-feature.
> - **REUSE_MAP** — đây là gem. Tool tự detect mọi `reuse_key` xuất hiện ở > 1 feature → list ra với note "candidate cho design system component". Engineer rebuild 1 lần, parameterise.
> - **API_SURFACE** — bảng mọi endpoint trong app, group by feature.
> - **DATA_MODELS** — mọi data class declared.
> - **INVARIANTS** — cross-screen invariant.
> - **OPEN_QUESTIONS** — roll-up mọi question chưa resolved.
> - **ACCEPTANCE** — roll-up mọi AC, group by feature.

> **5 section prose** designer/PM viết tay:

> - A. Mục tiêu sản phẩm + target user + KPI.
> - B. Navigation model abstract — tab structure conceptually, modal pattern, back behavior.
> - C. UX state pattern — empty, loading, error, paywall, gating — quy ước chung trên toàn app.
> - D. Content / copy rules — tone, locale, format.
> - E. Cross-cutting design decisions.

> **Idempotent re-render**. Auto section bọc trong HTML comment marker `<!-- AUTO:KEY START -->` ... `<!-- AUTO:KEY END -->`. Khi chạy lại tool, nó replace nội dung giữa marker, prose ngoài marker preserve nguyên. Designer viết prose 1 lần, sau này thêm feature mới rerun để refresh inventory không mất prose cũ.

> **Linter**. Chạy lệnh `re-spec-app-overview --check`. Tool flag warning khi gặp token framework-specific như `Compose`, `Kotlin`, `SwiftUI`, `UIView`, `Activity`, `Fragment`, `Storyboard`, `ViewModel` — ngoài code fence. Token trong code fence được skip, ví dụ ```kotlin``` block để quote ví dụ thì OK. Mục tiêu: doc thực sự agnostic, không "Android-with-iOS-fallback" trá hình.

---

## Slide 11 — PM doc linter (2 phút)

> Đây là **bonus tool** — apply technique của workflow vào doc PM bất kỳ.

> **Tại sao cần?** Doc PM truyền thống — kiểu doc bạn tự viết về app SubTrack — không bind cấu trúc 9-section feature_spec. PM viết tự do, có structure riêng. Nhưng doc PM viết tay cũng có pain: anchor format không đồng nhất, AC viết vague không testable, behavior rule viết prose mơ hồ.

> Module `pm_doc_lint.py` áp **6 check** vào file md bất kỳ:

> - **ANCHOR**: anchor `{#...}` phải đúng format `<feature>/<type>/<slug>` lowercase snake_case. Ví dụ `{#FEATURE/Screen/x}` sẽ bị flag — sai vì uppercase.

> - **RFC2119**: section heading có chữ "rule", "behavior", "policy" thì body phải có verb modal MUST / MUST NOT / SHOULD / MAY. Đây là **RFC 2119** — một chuẩn của IETF từ 1997 quy định cách viết requirement formal trong technical spec. Ví dụ "AI nên trả lời ngắn" sẽ bị flag — không phải MUST/SHOULD. Sửa thành "AI **MUST** message ≤ 280 chars".

> - **AC**: acceptance criteria phải có số và đơn vị đo được. "AI gửi tin nhắn ngắn gọn" bị flag. "AI message ≤ 280 chars cho ≥ 95% turn" pass.

> - **PLATFORM**: cùng list forbidden token như Layer 5 linter — Compose, SwiftUI, Activity, etc. ngoài code fence.

> - **OPENQ**: heading có anchor type `question` phải có dòng `**PM answer**:` với text non-empty. Placeholder `_(fill in)_` bị flag.

> - **FM**: nếu file có YAML frontmatter, phải có 3 key: `status`, `version`, `last_updated`.

> CLI: `re-spec-pm-doc-lint <file_or_dir>` — warn-only mặc định, exit 0. Flag `--strict` cho CI — exit 1 nếu có warning. Có thể chạy từng check riêng với `--check ANCHOR`, output JSON với `--json` cho automation.

> **Tested trên doc SubTrack thật của user — bắt đúng 3 warning**: §4.4 thiếu MUST/SHOULD, AC-01 và AC-02 không measurable. Đây là **dogfood** — chính tool được dùng để improve quy trình của chính PM.

---

## Slide 12 — Tech stack (1.5 phút)

> Một slide ngắn về tech stack. **Lean by design**.

> 4 con số đáng chú ý:
> - **1** required dependency: `pyyaml`. Đó là lib parse YAML.
> - **19** CLI command — console script — đăng ký lên PATH sau pip install.
> - **~5K** dòng Python tổng cộng, 16 module.
> - **0** dependency mới cho Telegram bridge — dùng stdlib `urllib` thuần.

> **Distribution**: Python 3.10+, src-layout theo PEP 518. INSTALL.sh chạy 1 phát: pip install editable + symlink skill và agents vào `~/.claude/`. Bundled data — template, canonical sample, shell script — access qua `importlib.resources` để work cả khi chạy từ source lẫn từ wheel cài đặt vào `site-packages/`.

> **Integrations**:
> - **droidrun Portal v0.6** — app Android cài trên device, expose a11y tree qua content provider.
> - **adb** — Android Debug Bridge, công cụ chính để giao tiếp device.
> - **Claude Code** — CLI agent của Anthropic. Skill và sub-agent của project được Claude Code load tự động.
> - **MCP server** — đã giải thích slide 8.
> - **Telegram Bot API** — long-poll mode, không cần webhook server hay public URL có TLS.

---

## Slide 13 — Real numbers (1.5 phút)

> Slide này show **đã chạy thật**, không phải project ảo.

> Baseline là project `bible-agent` — app dogfood của chúng tôi.

> - **164 graph nodes** — gồm 63 screen, 18 block, 27 component, 12 API, 19 data model, 8 invariant, 10 question, 7 criterion.
> - **208 graph edges** — bao gồm 95 navigates_to, 47 renders_component, 31 reuses_component, etc.
> - **5 feature đã spec** end-to-end: today, chat, community, bible, explore.
> - **63 screen captured** kèm a11y dump JSON và screenshot PNG.

> Tested live trong session phát triển:
> - Telegram bridge end-to-end — post Open Question → PM reply → fold vào file.
> - Stuck-help với 4 verdict — tested manually + auto-skip threshold.
> - App overview idempotent rerun — preserve prose.
> - PM doc lint trên doc SubTrack thật — bắt đúng 3 warning.

---

## Slide 14 — Use cases (2 phút)

> 4 use case chính của project.

> **Use case 1 — Competitor research**. Spec lại app đối thủ để team product/design phân tích UX pattern. Output đủ cho non-tech reader: Layer 5 app overview prose + Layer 1 observations per-screen. PM/designer đọc trong 1 buổi sáng, hiểu app đối thủ structure, navigation, pattern.

> **Use case 2 — Handoff coding agent**. Đây là use case mạnh nhất vì AI coding agent ngày càng giỏi. Spec output đủ structured: Layer 3 implementation contract + Layer 5 overview platform-agnostic + screenshot reference. Coding agent đọc, hiểu, rebuild. Cross-platform: 1 spec, build cả iOS lẫn Android.

> **Use case 3 — UX research baseline**. Document app hiện có để track UX evolution qua thời gian. Mỗi version capture 1 lần, diff observations.md để phát hiện UI drift. Engineer maintain regression baseline, designer track design system evolution.

> **Use case 4 — Spec-first cho team mình**. Đây là mode đảo ngược. Thay vì RE app đối thủ, team dùng cho chính app mình đang build. PM viết scope.md trước → AI capture flow + sinh implementation contract → engineer rebuild. Workflow này đảm bảo spec **authoritative trước code**, không phải code trước rồi viết spec sau.

---

## Slide 15 — Design agent integration (3 phút)

> Đây là slide nói về cách output của project này feed vào **AI design tool** đang phổ biến năm 2025-2026.

> **Claude Design** — của Anthropic Labs, launched April 2026. Powered by Claude Opus 4.7. Generate prototype HTML/CSS/JS từ text prompt. Đặc biệt: có thể đọc codebase và Figma file để **tự extract design system**, apply vào project mới.

> Re-spec-mobile feed gì cho Claude Design? Layer 3 feature_spec section 3 (state) và section 6 (data model). Layer 5 app_overview prose A đến E (mục tiêu, navigation, UX pattern, content rules, design decisions). Plus thư mục `spec/screens/` chứa screenshot reference. Claude Design đọc 3 input này → output: prototype HTML deploy được.

> **Google Stitch** — của Google Labs, launched Google I/O 2025 May. Powered by Gemini AI, mode Thinking dùng Gemini 2.5 Pro cho output cao nhất. Input format đa dạng: text prompt, image upload, voice. 4 mode: Ideate cho early exploration, Flash cho generation nhanh, Thinking cho final polish, Redesign cho transform UI có sẵn.

> Stitch đặc biệt mạnh ở Redesign mode — bạn upload screenshot UI cũ, nó rebuild variant mới. Re-spec-mobile feed: observations.md prose mô tả UI behavior + spec/screens/*.png upload làm image primary input + app_overview section B navigation model làm UX context. Stitch sẽ output Figma file hoặc HTML/CSS code.

> **nexu-io / open-design** — repo open-source trên GitHub, Apache 2.0 license. Self-host được, local-first, không cloud lock-in. Tự nhận là **alternative** cho Claude Design. Có 16 coding agent integration — Claude Code, Cursor, Gemini CLI, GitHub Copilot, Codex, etc. detect tự động trên PATH, swap qua dropdown. 31 built-in skill — web prototype, mobile app, dashboard, deck, mỗi skill là folder theo Claude Code SKILL.md convention. **129 design system** bundled dưới dạng `DESIGN.md` portable Markdown file — Linear, Stripe, Vercel, Apple, Notion, Tesla.

> Cái fit nhất với project chúng tôi: **DESIGN.md là Markdown** — same format với output re-spec-mobile. Mapping: Layer 5 app_overview.md → DESIGN.md (reuse_map = component design system, prose UX pattern). scope.md → discovery form input. feature_spec.md → input cho mobile_app skill.

> **Tóm lại — tại sao re-spec-mobile output fit cho design agent?**

> 1. **Layer 5 platform-agnostic** match philosophy DESIGN.md của Stitch và Open-design.
> 2. **Reuse map auto-detect** sẵn list component candidate cho design system.
> 3. **Layer 3 implementation contract** — coding agent downstream rebuild có shape rõ.
> 4. **Anchor cross-link** — design agent query precise qua MCP, không grep mò.

> Re-spec-mobile output là **agent-ready format**. Workflow tự nhiên: capture device → spec markdown → design agent generate → coding agent rebuild → ship cả iOS và Android.

---

## Slide 16 — Limitations (2 phút)

> Honesty slide. Workflow chuẩn cho 1 lớp app, không phải mọi app.

> **3 cột**:

> **Cột xanh — Xử được tốt v1.x hiện tại**: Android native (Compose, View XML, mixed). A11y tree đọc được. Navigation chuẩn — bottom nav, drawer, top tabs. App lành tính với automation. PM sẵn sàng tham gia 3 gate.

> **Cột giữa — Có path, chưa tích hợp** (đây là roadmap, không phải dead end):
> - **iOS** — kỹ thuật khả thi qua xcrun simctl, Accessibility Inspector, idb. Chưa develop module — estimate 600 dòng + iOS profile schema. Roadmap candidate.
> - **Flutter, React Native, WebView** — a11y tree thưa nhưng có thể nâng parser hiểu WebView role và Hermes a11y. Estimate 200 dòng.
> - **UX research mode** — skip Layer 3 cho competitor research mode, profile style mới. Estimate 150 dòng.

> **Cột phải — Hạn chế cần human / test build** (cái này thực sự khó tránh):
> - **Game Unity/Unreal** — UI render qua Canvas, a11y tree rỗng hoàn toàn. Chỉ screenshot được.
> - **Banking production** — Frida detect, FLAG_SECURE → cần dev build app-side, toolkit không fix được.
> - **Captcha, 2FA, OTP** — cần human qua được. Phase 3 stuck handoff design cho case này.
> - **Paywall thật** — cần test account trước khi capture.

> **Effort estimate**: mỗi app cần **2 ngày tuning profile** — fill blocklist custom, modals back-traps, navigation tabs sau capture đầu. Lần đầu spec 1 feature ~ 4-8 giờ. Lần thứ 2 cùng app ~ 2-4 giờ. Không expect auto 100% — Phase 3 reset handoff là norm chứ không phải edge case.

---

## Slide 17 — Future / Roadmap (2 phút)

> 6 hướng cải tiến đang cân nhắc. Tôi nói nhanh.

> **1. Conversation flow template variant** — feature có chat hoặc dialog (như SubTrack AI Chat) không fit format 9-section per-screen. Cần template mới với anchor type `conversation` và `turn`. Estimate 400 dòng.

> **2. Behavioral rules section** trong feature_spec — anchor type `rule` và `policy` cho RFC 2119 MUST/SHOULD. Tách biệt với cross-screen invariant. Estimate 150 dòng.

> **3. Metrics tracking → table với anchor**. Mở rộng section 2.3 hiện đang prose-only thành table format có anchor `metric/<event>`. Cross-feature metric roll-up trong app_overview. Estimate 80 dòng.

> **4. iOS path** — đây là big lift. Capture qua xcrun simctl và Accessibility Inspector và idb. Module mới + iOS profile schema. Estimate 600 dòng.

> **5. Hybrid app a11y enhanced parser** — Flutter, RN, WebView a11y tree thưa. Cải tiến parser hiểu WebView role + Hermes a11y. Estimate 200 dòng.

> **6. ux_research profile style** — skip Layer 3 cho competitor research mode khi user không cần handoff coding agent. Estimate 150 dòng.

> Trong số này, ưu tiên có thể là (1) Conversation flow vì gap rõ với app dạng AI chat đang phổ biến, hoặc (4) iOS path vì market demand cao. Nhưng đó là quyết định tùy use case.

---

## Slide 18 — Recap & Q&A (1 phút)

> Tóm lại trong 1 câu: **Spec-first, PM-driven, Cross-platform**.

> Workflow capture device Android → 5 layer markdown structured → handoff iOS và Android coding agent. 11 phase với 3 PM gate. Telegram bridge cho async review. Layer 5 platform-agnostic.

> 3 con số quan trọng: **19 CLI command**, **5 layer / feature**, **1 dependency thật sự cần** — `pyyaml`.

> Source code public ở **github.com/datnt1-tech/re-spec-mobile**. License internal, dùng nội bộ team.

> Cảm ơn mọi người đã lắng nghe. Bây giờ là phần Q&A — anh em có câu hỏi gì cứ hỏi nhé.

---

## Phụ lục — thuật ngữ tổng hợp

Tham khảo nhanh khi audience hỏi:

| Thuật ngữ | Giải thích ngắn |
|---|---|
| **A11y** | Accessibility — viết tắt: a + 11 ký tự + y. A11y tree là cấu trúc dữ liệu mô tả UI cho screen reader / automation. |
| **adb** | Android Debug Bridge — CLI giao tiếp Android device qua USB. |
| **Anchor** | ID duy nhất cho heading markdown, format `<feature>/<type>/<slug>`. Cho phép cross-link và query. |
| **AC** | Acceptance Criteria — tiêu chí pass/fail testable. Phải có số + đơn vị. |
| **API contract** | Mô tả formal về endpoint: method, path, request, response shape. |
| **BFS** | Breadth-First Search — thuật toán tìm shortest path. |
| **CLI** | Command-Line Interface — tool chạy trong terminal. |
| **Coding agent** | AI agent có khả năng đọc/viết code. Vd Claude Code, Cursor, Copilot. |
| **Design agent** | AI agent sinh UI/UX design. Vd Claude Design, Stitch, Open Design. |
| **Droidrun Portal** | App Android expose a11y tree qua content provider. |
| **Frontmatter** | Block YAML đầu file Markdown, giữa 2 dòng `---`. Chứa metadata. |
| **Gate** | Cổng kiểm duyệt trong workflow. PM phải ký trước khi tiếp. |
| **HTML marker** | Comment `<!-- AUTO:KEY START -->` ... `<!-- AUTO:KEY END -->` để bookmark phần auto-generated. |
| **Idempotent** | Chạy lại nhiều lần cho cùng kết quả, không phá state. |
| **JSON Schema** | Format chuẩn mô tả shape của JSON data. |
| **MCP** | Model Context Protocol — protocol open của Anthropic cho AI agent gọi tool external. |
| **Mermaid** | Syntax vẽ diagram bằng text trong markdown. |
| **PEP 518** | Python Enhancement Proposal — chuẩn về `pyproject.toml` build system. |
| **PM** | Product Manager. |
| **RE** | Reverse Engineering — moi cấu trúc từ artifact đã có. |
| **RFC 2119** | IETF spec 1997 về verb modal: MUST / SHOULD / MAY trong technical doc. |
| **Scope** | Phạm vi feature — what's in, what's out. |
| **SDK** | Software Development Kit. |
| **Skill** | Concept Claude Code: file SKILL.md mô tả workflow Claude follow. |
| **Sub-agent** | AI agent con được skill orchestrator gọi để delegate task cụ thể. |
| **YAML** | Human-readable data format, dùng cho frontmatter và config. |
