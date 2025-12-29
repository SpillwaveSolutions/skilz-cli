# Feature 08: Multi-Skill Repository Support

## Feature Summary

Enable installing skills from git repositories containing multiple skills,
with support for `--skill` flag to select specific skills and improved
discovery of skills in `.claude/` and `.opencode/` directories.

## Target Agents

| Agent | Skills Directory |
|-------|------------------|
| Claude Code | `~/.claude/skills/` (user) or `.claude/skills/` (project) |
| OpenCode | `~/.config/opencode/skills/` |
| Universal | Installs to all detected agents |

## User Stories

### US-1: Install from Multi-Skill Repository
**As a** developer
**I want to** run `skilz install -g <repo-url>`
**So that** I can select which skill(s) to install from a repository with many skills

**Acceptance Criteria:**
- Skills in `.claude/skills/` directories are discovered
- Skills in `.opencode/skills/` directories are discovered
- Interactive menu shows all available skills
- Can select individual skills or all

### US-2: Direct Skill Selection
**As a** developer who knows which skill I want
**I want to** run `skilz install -g <repo-url> --skill <name>`
**So that** I can install a specific skill without the menu

**Acceptance Criteria:**
- Skill is found by matching name from SKILL.md frontmatter
- Error message lists available skills if not found
- Works with both single and multi-skill repositories

### US-3: Official Plugin Marketplace Discovery
**As a** plugin repository maintainer
**I want to** use official `.claude-plugin/marketplace.json` to define available skills
**So that** users can discover skills using the official Claude Code plugin format

**Acceptance Criteria:**
- `.claude-plugin/marketplace.json` is checked first (official location per Claude Code docs)
- Falls back to `marketplace.json` at repo root for compatibility
- Falls back to recursive SKILL.md search if no marketplace file
- `plugins` array with `name` and `source` fields are parsed
- Only local `source` paths (starting with "./") are processed
- Skill paths from marketplace are validated for SKILL.md presence

## Functional Requirements

### FR-1: Fixed Hidden Directory Filter
- Only exclude `.git/` directory from skill search
- Include `.claude/` and `.opencode/` in skill search
- Use relative path checking to avoid false positives

### FR-2: --skill Flag
- Add `--skill NAME` argument to install command
- Filter discovered skills by name match
- Show helpful error with available names if not found

### FR-3: Official Plugin Marketplace Support
- Check `.claude-plugin/marketplace.json` first (official location)
- Fall back to `marketplace.json` at repo root for compatibility
- Parse official schema: `plugins` array with `name` and `source` fields
- Handle local `source` paths (e.g., `"./plugins/skill-name"`)
- Skip remote sources (GitHub refs, URLs) - not applicable for local install
- Validate that resolved skill paths contain SKILL.md files
- Reference: https://code.claude.com/docs/en/plugin-marketplaces

## Non-Functional Requirements

### NFR-1: Performance
- Marketplace.json lookup should be O(1) file read
- Recursive SKILL.md search as fallback (may be slower for large repos)

### NFR-2: Compatibility
- Must work with existing single-skill repos (no breaking changes)
- Must work with both HTTPS and SSH git URLs

## Out of Scope

- Remote marketplace sources (GitHub refs, external URLs)
- Skill dependency resolution
- Automatic skill updates based on marketplace changes

## Schema: Official Marketplace.json

Per Claude Code docs (https://code.claude.com/docs/en/plugin-marketplaces):

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Your Name",
    "email": "user@example.com"
  },
  "description": "Description",
  "strict": true,
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/name",
      "description": "...",
      "keywords": ["tag1", "tag2"]
    }
  ]
}
```

## Success Metrics

- `skilz install -g https://github.com/The1Studio/theone-training-skills` discovers 38+ skills
- `skilz install -g <url> --skill theone-cocos-standards` installs specific skill
- All existing tests continue to pass
- New functionality has 80%+ test coverage
