# Canonical reference samples

Các file này là **bộ spec 3 layer chuẩn vàng** mà agent `spec-writer` dùng làm
reference style + structure khi draft spec cho 1 app hoàn toàn mới chưa có
`canonical_feature` riêng.

| File | Mục đích | Layer | Lines |
|---|---|---|---|
| `observations.sample.md` | Bảng bounds thô + transition + note hành vi | observations | ~700 |
| `spec.sample.md` | Flow block-by-block + state machine + nav graph | flow | ~535 |
| `feature_spec.sample.md` | Spec impl 9 section (metadata → KPI → API → AC) | implementation | ~975 |
| `SPEC_SCHEMA.md` | Schema contract cho frontmatter + anchor + edge type | — | ~490 |

**Origin:** copy từ feature Today của project `bible-agent` (spec mature nhất
lúc đóng gói skill). Tab Today được chọn vì exercise mọi case khó nhất của mỗi
layer:

- Observations: 17 trạng thái UI khác biệt với bảng sticky-header / scroll-segment
- Flow: 12 functional block với navigation cross-cluster + state machine
- Implementation: 5 component reusable + 6 KPI metric + 12 acceptance criterion

**Writer agent dùng chúng thế nào:**

1. Nếu `profile.reference.canonical_feature` đã set, đọc 3 file của feature đó
   từ project user làm primary reference.
2. Ngược lại, đọc các file này. Mimic thứ tự section, density bảng, voice
   bullet (heading tiếng Anh, prose tiếng Việt), cách dùng Mermaid, vị trí
   anchor marker `{#feature/type/name}`, code-block fence (json/kotlin).
3. Không bao giờ paraphrase UI string — wrap nguyên văn trong backtick như sample.

**Đừng edit các file này** trừ khi update canonical baseline cho mọi app
tương lai dùng skill. Để thay bằng sample khác, swap file tại chỗ và bump
version SKILL.md.

**Lưu ý ngôn ngữ**: canonical samples viết bằng tiếng Việt với technical term
tiếng Anh (xem `docs/I18N_GLOSSARY.md`). Nếu canonical override của user là
tiếng khác, writer agent ưu tiên ngôn ngữ của canonical user.
