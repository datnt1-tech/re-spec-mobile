# I18N Glossary — Vietnamese translation guide

When translating skill instructions, agent prompts, templates, schema, and
canonical samples to Vietnamese, **keep the following terms in English** to
preserve technical precision.

## Code-level identifiers (NEVER translate)

YAML frontmatter keys, anchor IDs, file paths, JSON schema field names,
function/CLI names, log messages.

```
feature, layer, anchor, title, last_updated, app_version, device, package,
status, screens, edges, nodes, blocks, capture_file, dump_file, section_line,
hash, parent, via, label, activity, reuses, reuse_key, blockers
```

```
re-spec-init, re-spec-capture, re-spec-build-graph, ... (all CLI scripts)
.spec-profile.yml, _data, _shell, _graph, _raw, screens, ui_dumps
```

## Process / methodology terms (keep English)

These are project vocabulary that engineers + PM share across docs:

| English | Why keep | Vietnamese gloss (for first mention only) |
|---|---|---|
| scope | YAML field + workflow concept | phạm vi |
| sign-off | PM gate verb | duyệt |
| gate | Phase gate (Gate 1/2/3) | cổng kiểm duyệt |
| coverage | Coverage check / report | độ phủ |
| coverage_check / coverage_report | filename + concept | — |
| drift | Items captured outside scope | lệch phạm vi |
| gap | Must_visit not captured | thiếu sót |
| must_visit / optional_visit / out_of_scope | scope cluster types | — |
| anchor | Stable ID `<feature>/<type>/<name>` | định danh |
| frontmatter | YAML block at top of MD | — |
| block letter (A/B/C) | Subgraph cluster | nhóm con |
| screen | Captured screen | màn hình |
| flow | Layer 2 spec | luồng |
| observations | Layer 1 spec | quan sát |
| implementation | Layer 3 spec | hiện thực |
| feature | Top-level unit | tính năng |
| reuse_key | Cross-feature component reuse marker | khoá tái sử dụng |
| acceptance criteria | Layer 3 verification list | tiêu chí nghiệm thu |

## Tooling / device terms (keep English)

```
adb, droidrun, Portal, accessibility service, a11y tree, viewport,
emulator, device, USB debugging, content provider, broadcast, intent,
APK, install, reinstall, package manager, pm clear, monkey, am start,
input tap/swipe/keyevent, KEYCODE_*, dumpsys, settings put/get
```

## UI / interaction terms (keep English)

```
tap, swipe, scroll, long-press, drag, pinch, fling
button, link, icon, label, hint, placeholder, divider
card, list, grid, tab, sub-tab, chip, badge, pill
sheet, modal, dialog, drawer, overlay, tooltip, popover, menu
toast, snackbar, banner, ribbon, FAB (floating action button)
header, footer, sticky, app-bar, bottom-bar, status-bar
input, text-field, search-bar, slider, switch, checkbox, radio
swipe-to-dismiss, swipe-to-refresh, pull-to-refresh, infinite scroll
viewport, bounds, coordinates, x/y, padding, margin, gutter
hit-area, tappable, clickable
keyboard, IME, soft-keyboard, hardware-back, system-back
loading, skeleton, shimmer, spinner, progress, empty state, error state
```

## Engineering / architecture terms (keep English)

```
API, endpoint, request, response, payload, header, body, status code
GET/POST/PUT/DELETE, REST, GraphQL, WebSocket, gRPC, SSE
DTO, schema, contract, model, entity, repository, datasource
async, sync, callback, coroutine, suspend, Flow, StateFlow, LiveData
cache, retry, fallback, debounce, throttle, batch
JWT, token, refresh, OAuth, session, cookie, header, bearer
deep-link, intent-filter, branch link, dynamic link, universal link
analytics, event, property, funnel, cohort
A/B test, experiment, feature flag, kill-switch, remote config
push notification, FCM, payload, silent push
in-app purchase, subscription, paywall, billing, SKU, entitlement
```

## File formats / data formats (keep English)

```
YAML, JSON, JSONL, XML, HTML, CSS, SVG, PNG, JPEG, MP4
markdown, frontmatter, code-fence, inline-code, blockquote
regex, glob, sed, awk, grep, find
```

## Project-specific abbreviations (keep English)

```
MCP (Model Context Protocol), MCP server, JSON-RPC, stdio
PM (Product Manager), QA, RE (reverse engineering), CTA (call-to-action)
PoC, MVP, GA, LTS
SKILL, agent, sub-agent, orchestrator, swimlane
PEP 518, src-layout, package_data, importlib.resources, pyproject.toml
```

## Translation style

- Tone: **trực tiếp, ngắn gọn**, dùng "bạn" cho instruction, **không dùng "chúng ta"** cho directive.
- Verbs: imperative (e.g., "Đọc file", "Chạy lệnh", "Trả về DONE"), không phải ("Hãy đọc file", "Vui lòng chạy lệnh").
- Code blocks, file paths, CLI commands: **giữ nguyên 100%** — không dịch.
- Markdown structure (heading levels, table columns, list bullets): giữ nguyên.
- Comments trong code blocks: dịch nếu là explanation, giữ English nếu là log message thực tế.
- "should / must / never" → "cần / phải / không bao giờ".
- "DO NOT" → "KHÔNG".
- "BLOCKED / DONE / DONE-PARTIAL" status strings: **giữ English** (chúng là enum, return value).

## When in doubt

If a term appears in code (frontmatter key, CLI arg, function name) → English.
If a term appears in PM-facing prose → translate to Vietnamese with English in
parens on first mention: "phạm vi (scope)", "cổng kiểm duyệt (gate)".
After first mention, you can drop the parens.
