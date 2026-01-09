# Phase 2: Skill Management Commands

## Feature Summary

Add commands to manage installed skills:
- `skilz list` - Show installed skills
- `skilz update` - Update skills to latest registry SHA
- `skilz remove` - Uninstall a skill

## User Stories

### US-1: List Installed Skills
**As a** developer
**I want to** run `skilz list` to see all installed skills
**So that** I can audit what's installed and check versions

**Acceptance Criteria:**
- Lists all skills with manifest files
- Shows skill_id, git_sha (short), installed_at
- Indicates if skill is outdated vs registry
- Supports `--agent` flag to filter by agent
- Supports `--project` flag for project-level skills
- Clean tabular output

### US-2: Update Skills
**As a** developer
**I want to** run `skilz update` to update all skills to registry versions
**So that** I can keep skills current without manual reinstalls

**Acceptance Criteria:**
- `skilz update` updates ALL outdated skills
- `skilz update skill-id` updates specific skill
- Compares manifest SHA to registry SHA
- Shows what will be updated before doing it
- Skips already up-to-date skills
- Supports `--dry-run` to show what would change

### US-3: Remove Skills
**As a** developer
**I want to** run `skilz remove skill-id` to uninstall a skill
**So that** I can clean up skills I no longer need

**Acceptance Criteria:**
- Removes skill directory and all contents
- Confirms before removing (unless `--yes`)
- Works with partial skill names if unambiguous
- Shows what was removed
- Handles missing skill gracefully

## Functional Requirements

### FR-1: List Command
```
skilz list [--agent claude|opencode] [--project] [--json]
```
- Scan skills directories for manifest files
- Parse each manifest to extract metadata
- Compare to registry (if available) to detect outdated
- Format output as table or JSON

### FR-2: Update Command
```
skilz update [skill-id] [--agent claude|opencode] [--project] [--dry-run]
```
- If no skill-id, update all installed skills
- Load registry to get current SHAs
- Compare each installed skill's manifest SHA
- Re-run install for outdated skills
- Report: updated, skipped (up-to-date), failed

### FR-3: Remove Command
```
skilz remove <skill-id> [--agent claude|opencode] [--project] [--yes]
```
- Find skill directory by name
- Confirm with user (unless --yes)
- Remove directory recursively
- Report success/failure

## Output Formats

### List Output (Default)
```
Agent    Skill                          Version    Mode     Status
────────────────────────────────────────────────────────────────────────────
claude   spillwave/plantuml             f2489dcd   [copy]   up-to-date
gemini   anthropics/web-artifacts       00756142   [copy]   outdated
claude   spillwave/design-doc-mermaid   e1c29a38   [copy]   up-to-date
```

### List Output (JSON)
```json
[
  {
    "skill_id": "spillwave/plantuml",
    "skill_name": "plantuml",
    "agent": "claude",
    "git_sha": "f2489dcd...",
    "installed_at": "2025-01-15T14:32:00Z",
    "status": "up-to-date",
    "path": "/Users/.../.claude/skills/plantuml",
    "project_level": false
  }
]
```

### Update Output
```
Checking 3 installed skills...
  spillwave/plantuml: up-to-date (f2489dcd)
  anthropics/web-artifacts: updating 00756142 → a1b2c3d4
  spillwave/design-doc-mermaid: up-to-date (e1c29a38)

Updated 1 skill, 2 already up-to-date
```

### Remove Output
```
Remove spillwave/plantuml from Claude Code? [y/N] y
Removed: spillwave/plantuml
```

## Success Metrics

Phase 2 is complete when:
1. `skilz list` shows all installed skills with status
2. `skilz update` updates outdated skills
3. `skilz remove skill-id` uninstalls skills
4. All commands support --agent and --project flags
5. Tests cover all command paths
