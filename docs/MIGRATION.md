# Migration — bible-agent → re-spec-mobile adapter pattern

The `bible-agent` repository was the source material for this skill: its
`spec/tools/` is what got generalized into `~/.claude/skills/re-spec-mobile/tools/`,
and its `today_*.md` is the canonical reference style.

This doc explains how to switch `bible-agent` to use the skill **without
breaking the existing workflow**. The migration is non-destructive: existing
tools stay in place, you add a `.spec-profile.yml`, and start using the skill
in parallel. After a few capture sessions confirm the skill works, you can
optionally delete the duplicated `spec/tools/` files.

## Step 1 — Install the skill on your machine

```bash
cd /path/to/re-spec-mobile
bash INSTALL.sh
```

That symlinks `~/.claude/skills/re-spec-mobile` and `~/.claude/agents/{app-explorer,spec-writer}.md`.

## Step 2 — Drop the bible-agent profile

```bash
cd /home/datnt/py.repo/bible-agent
cp /path/to/re-spec-mobile/examples/bible-agent.spec-profile.yml .spec-profile.yml
```

The sample profile mirrors the hard-coded constants in the original
`bible-agent/spec/tools/` scripts:

| Original constant | Where | New location |
|---|---|---|
| `REPO_ROOT = parent.parent.parent` | every Python tool | `profile.project_root` (auto from .spec-profile.yml location) |
| `SPEC_ROOT = REPO_ROOT / "spec"` | every Python tool | `profile.spec_root` |
| `BLOCKLIST_PATTERNS = [...]` | `coverage_check.py` | `profile.blocklist` (defaults + custom) |
| `com.basmo.BibleChat` | implicit everywhere | `profile.app.package` |
| Bottom-nav coords (108, 1918) etc. | implicit (memorized) | `profile.navigation.tabs[].center` |
| Pixel viewport `1080x2160` | implicit | `profile.device.viewport` |
| Locale `vi-VN` | implicit | `profile.device.locale` |
| Compose `v01` BACK trap | comment in checkpoint.md | `profile.modals.back_traps` |
| Floating overlay → mép trái swipe | comment in checkpoint.md | `profile.scroll.edge_swipe_x` |

Validate:

```bash
python ~/.claude/skills/re-spec-mobile/tools/profile_loader.py --validate
```

## Step 3 — Verify the skill sees the existing specs

The skill points at the same paths the original tools used (`spec/feature/`,
`spec/screens/`, etc.), so existing artifacts work as-is:

```bash
# Build the spec graph using the skill's build_graph.py against the existing specs
python ~/.claude/skills/re-spec-mobile/tools/build_graph.py --stats

# Should show roughly the same node/edge counts as before — onboarding/today/chat/community/explore features
```

If the counts match the existing `spec/_graph/nodes.json`, the migration is
working. If they differ, diff the two outputs and check whether the new
`build_graph.py` is missing some legacy heuristic.

## Step 4 — Set up Portal (if not already)

bible-agent has its own `setup_portal.sh`; you can keep using it. The skill's
copy is byte-identical except it doesn't print bible-agent-specific paths.
Either works.

## Step 5 — Try one feature with the skill

Pick a small upcoming feature (e.g. one of the Profile drawer sub-screens that
isn't fully spec'd yet) and run the skill workflow:

```
/re-spec-mobile
> "spec feature widget_selection — starting state: Profile drawer open at row 'Widget selection'"
```

The orchestrator drives Phase 0 (skip — profile exists), Phase 1 (kickoff),
delegates Phase 2 to `app-explorer`, runs Phase 4 coverage, delegates Phase 5
to `spec-writer`, runs Phase 6 graph rebuild + validate, and waits for your OK
on Phase 7 commit.

Compare the output (`spec/feature/widget_selection/widget_selection_*.md`)
against the existing `today_*.md` style. They should be indistinguishable in
structure; only content differs.

## Step 6 — (Optional) Remove duplicated bible-agent tools

After 2-3 capture sessions confirm the skill works, you can delete the
duplicated tools:

```bash
cd /home/datnt/py.repo/bible-agent

# Things to delete (all replaced by skill):
rm -r spec/tools/{capture.py,capture.sh,coverage_check.py,nav_graph.py,observations_tmpl.py,render_nav.py,build_graph.py,validate_spec.py,spec_query.py,mcp_server.py,extract_contracts.py,migrate_frontmatter.py,setup_portal.sh,setup-hooks.sh,register-mcp-user.sh,portal_version.txt,README.md,__pycache__}

# Things to keep (bible-agent specific, no skill equivalent):
# - spec/tools/demo_recorder.sh    (demo video orchestrator)
# - spec/tools/demo_merge.sh       (demo chunk merger)
```

Then update `bible-agent/CLAUDE.md` to point at the skill's tool paths instead
of `spec/tools/`. The .mcp.json should also be updated:

```bash
# Old: command = python3, args = [/abs/path/bible-agent/spec/tools/mcp_server.py]
# New:
cat > .mcp.json <<'EOF'
{
  "mcpServers": {
    "spec-graph": {
      "command": "python3",
      "args": ["${HOME}/.claude/skills/re-spec-mobile/tools/mcp_server.py"]
    }
  }
}
EOF
```

The skill's `mcp_server.py` walks up from CWD looking for `.spec-profile.yml`,
so it auto-targets bible-agent's spec graph when invoked from inside that repo.

## Step 7 — Tell teammates

Add to `bible-agent/CLAUDE.md`:

```markdown
## Spec workflow

This project uses the `re-spec-mobile` skill (install:
~/.claude/skills/re-spec-mobile/). Adapter config: `.spec-profile.yml` at
repo root. To capture/write specs for a new feature: in Claude Code,
say `/re-spec-mobile spec feature <name>` or just describe the feature
to spec — the skill auto-triggers.
```

## Risks + how to back out

The migration is reversible at every step:

- **Step 2 only writes `.spec-profile.yml`** — delete to revert.
- **Step 6 removes duplicated tools** — `git checkout HEAD -- spec/tools/` to
  restore.
- **`.mcp.json` change** — `git checkout HEAD -- .mcp.json` to revert.

The skill's tools are designed to coexist with the originals; running both in
parallel doesn't conflict (they read+write the same files in the same paths).

## Tradeoffs of the migration

| Pro | Con |
|---|---|
| Single source of truth for tools (skill) | Skill must be installed on every dev machine |
| Generic across N apps | Slight indirection overhead reading profile per-call |
| Profile makes adapter assumptions explicit | Anyone reading old code sees hard-coded constants the new code doesn't reflect |
| Can iterate skill independently of project | Skill version drift between machines if not pinned |

## Pinning a skill version

If you want all teammates on the same skill version:

```bash
# In the re-spec-mobile repo:
git tag v1.0.0
# In bible-agent:
echo "v1.0.0" > .spec-profile.skill-version
```

Then in bible-agent CLAUDE.md, instruct: "Run
`cd ~/repos/re-spec-mobile && git checkout $(cat /home/datnt/py.repo/bible-agent/.spec-profile.skill-version) && bash INSTALL.sh`
before working on this project."

(Auto-enforcement would require a hook — not in v1.)
