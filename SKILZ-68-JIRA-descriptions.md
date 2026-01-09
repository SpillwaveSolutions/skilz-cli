# SKILZ-68 List Command Issues - JIRA Ticket Descriptions

## SKILZ-68-A: Only two agents when --agent omitted

### Observed
When running `skilz list` without `--agent`, only skills from 2 agents are shown (claude, opencode), despite having 14+ agents in the registry.

### Expected
`skilz list` should scan all agents in the registry and show skills from all installed agents.

### Repro Steps
1. Install skills for multiple agents (e.g., claude, gemini, opencode)
2. Run `skilz list` (no --agent flag)
3. Only see skills from 2 agents instead of all agents

### Root Cause
Scanner uses hardcoded `AGENT_PATHS.keys()` which only contains ["claude", "opencode"], instead of `registry.list_agents()` which returns all 14+ agents.

### Notes
- Spec requires scanning all agents when --agent omitted
- Registry has 14+ agents but scanner only checks 2
- Affects user experience - users can't see all their installed skills

---

## SKILZ-68-B: Duplicate rows when --agent omitted

### Observed
When running `skilz list` without `--agent`, the same skill appears multiple times in the output.

### Expected
Each skill should appear only once, with an "Agent" column showing which agent it belongs to.

### Repro Steps
1. Install same skill for multiple agents
2. Run `skilz list` (no --agent flag)
3. See duplicate entries for the same skill

### Root Cause
- No "Agent" column in table output
- Scanner scans overlapping directories (same skill in .claude/skills/ and .gemini/skills/)
- No deduplication logic

### Notes
- Table format needs Agent column
- JSON output already includes "agent" field
- Spec shows table without Agent column, but this causes confusion

---

## SKILZ-68-C: Home installs not reliably discovered

### Observed
`skilz list` doesn't find skills installed at user-level for some agents (e.g., ~/.claude/skills/).

### Expected
`skilz list` should find all skills installed at user-level for all agents.

### Repro Steps
1. Install skill for claude: `skilz install skill --agent claude`
2. Run `skilz list` (no --agent flag)
3. Skill may not appear in list

### Root Cause
- Agent home dir mapping may not match actual on-disk layouts
- Scanner may only scan project-level paths unless explicitly told otherwise
- Path resolution issues between registry config and actual filesystem

### Notes
- Works for some agents but not others
- May be related to config overrides or path resolution
- Affects discoverability of installed skills

---

## SKILZ-68-D: Status always unknown

### Observed
Status column always shows "unknown" for all skills in `skilz list` output.

### Expected
Status should show "up-to-date", "outdated", or "unknown" based on registry comparison.

### Repro Steps
1. Install any skill
2. Run `skilz list`
3. Status column shows "unknown" for all skills

### Root Cause
- Status logic depends on registry identity via `lookup_skill(skill.skill_id)`
- For git installs, `skill_id` is "git/skill-name" which doesn't exist in registry
- Should use `skill.manifest.skill_id` (the original registry ID) instead

### Notes
- Registry skills should show proper status
- Git-installed skills should show "unknown" (not in registry)
- Spec shows status working, but implementation doesn't match