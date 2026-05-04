# Canonical reference samples

These files are the **gold-standard 3-layer specs** the `spec-writer` agent
uses as a style + structure reference when drafting specs for a brand-new app
that has no prior `canonical_feature` of its own.

| File | Purpose | Layer | Lines |
|---|---|---|---|
| `observations.sample.md` | Raw bounds tables + transitions, behaviour notes | observations | ~700 |
| `spec.sample.md` | Block-by-block flow + state machine + nav graph | flow | ~535 |
| `feature_spec.sample.md` | 9-section impl spec (metadata → KPI → API → AC) | implementation | ~975 |
| `SPEC_SCHEMA.md` | Schema contract for frontmatter + anchors + edge types | — | ~490 |

**Origin:** copied from the `bible-agent` project's Today feature (the most
mature spec at the time the skill was packaged). The Today tab was chosen
because it exercises every layer's hardest case:

- Observations: 17 distinct UI states with sticky-header / scroll-segment table
- Flow: 12 functional blocks with cross-cluster navigation + state machine
- Implementation: 5 reusable components + 6 KPI metrics + 12 acceptance criteria

**How the writer agent uses them:**

1. If `profile.reference.canonical_feature` is set, read that feature's 3 files
   from the user's project as primary reference.
2. Otherwise, read these files. Mimic the section ordering, table density,
   bullet voice (header English, commentary Vietnamese), Mermaid usage, anchor
   marker `{#feature/type/name}` placement, code-block fences (json/kotlin).
3. Never paraphrase UI strings — wrap verbatim in backticks like the samples do.

**Do not edit these files** unless updating the canonical baseline for all
future apps that use the skill. To replace with a different sample, swap the
files in place and bump the SKILL.md version.
