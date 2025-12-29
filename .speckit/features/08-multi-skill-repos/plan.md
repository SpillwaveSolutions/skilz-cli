# Feature 08: Multi-Skill Repository Support - Technical Plan

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Skill Discovery | Python pathlib | Efficient recursive file globbing |
| JSON Parsing | stdlib json | No external dependencies needed |
| CLI Extension | argparse | Consistent with existing CLI |

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                 │
│  ┌─────────────┐                                                │
│  │   cli.py    │ → --skill NAME argument                        │
│  └──────┬──────┘                                                │
│         │                                                        │
│  ┌──────▼──────────┐                                            │
│  │ install_cmd.py  │ → Pass skill_filter_name                   │
│  └──────┬──────────┘                                            │
└─────────┼────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                    Git Install Layer                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   git_install.py                            │ │
│  │  ┌──────────────────────┐  ┌─────────────────────────────┐ │ │
│  │  │ find_skills_from_    │  │ find_skills_in_repo()       │ │ │
│  │  │ marketplace()        │  │ (recursive SKILL.md search) │ │ │
│  │  │ (marketplace.json)   │  │                             │ │ │
│  │  └──────────┬───────────┘  └──────────────┬──────────────┘ │ │
│  │             │                              │                │ │
│  │             └──────────┬──────────────────┘                │ │
│  │                        │                                    │ │
│  │  ┌─────────────────────▼─────────────────────────────────┐ │ │
│  │  │              Skill Filter Logic                        │ │ │
│  │  │  if skill_filter_name → filter by name                 │ │ │
│  │  │  else → prompt_skill_selection()                       │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. CLI receives: skilz install -g <url> --skill <name>
                        │
2. install_cmd.py extracts skill_filter_name
                        │
3. install_from_git() clones repo to temp dir
                        │
4. Try find_skills_from_marketplace(temp_dir)
   │  ├─ Check .claude-plugin/marketplace.json (official)
   │  └─ Check marketplace.json at root (fallback)
   │
5. If no marketplace skills, find_skills_in_repo(temp_dir)
   │  └─ Recursive SKILL.md search (skip only .git/)
   │
6. Filter skills by skill_filter_name if provided
   │  └─ Show available skills in error if not found
   │
7. Install selected skill(s)
```

## Key Design Decisions

### D1: Only Skip .git Directory
**Decision:** Change hidden directory filter from "any dot-prefixed" to "only .git"

**Rationale:** Skills legitimately live in `.claude/` and `.opencode/` directories. The original filter was too aggressive.

**Code Change:**
```python
# Before
if any(part.startswith(".") for part in skill_md.parts):
    continue

# After
relative_parts = skill_md.relative_to(repo_path).parts
if ".git" in relative_parts:
    continue
```

### D2: Marketplace First, Recursive Fallback
**Decision:** Try marketplace.json before recursive search

**Rationale:** Marketplace provides explicit skill definitions with names; recursive search is slower and relies on frontmatter parsing.

### D3: Official Location Priority
**Decision:** Check `.claude-plugin/marketplace.json` before root `marketplace.json`

**Rationale:** Official Claude Code docs specify `.claude-plugin/` as the canonical location.

### D4: Filter vs Prompt
**Decision:** When `--skill` flag provided, skip interactive prompt

**Rationale:** Enables scripting and CI/CD usage without TTY interaction.

## Error Handling Strategy

| Error | Exit Code | Message |
|-------|-----------|---------|
| No skills found | 1 | "No skills found in repository. Skills must contain a SKILL.md file." |
| --skill not found | 1 | "Skill '<name>' not found in repository.\nAvailable skills: ..." |
| Git clone failed | 1 | "Git clone failed: <error>" |
| Invalid marketplace.json | - | Silent fallback to recursive search |

## Testing Strategy

### Unit Tests
- `test_find_skills_in_repo_claude_dir` - Skills in `.claude/skills/` discovered
- `test_find_skills_in_repo_git_dir_skipped` - `.git/` directory skipped
- `test_find_skills_from_marketplace_official` - `.claude-plugin/marketplace.json` parsed
- `test_find_skills_from_marketplace_root` - Root `marketplace.json` fallback
- `test_install_from_git_skill_filter` - `--skill` flag filtering
- `test_install_from_git_skill_not_found` - Error message with available skills

### Integration Tests
- Clone real multi-skill repo (theone-training-skills)
- Verify skill count and names discovered

## Implementation Phases

### Phase 8a: Bug Fix (Complete)
- [x] Fix hidden directory filter

### Phase 8b: --skill Flag (Complete)
- [x] Add CLI argument
- [x] Pass through install_cmd.py
- [x] Filter in git_install.py

### Phase 8c: Marketplace Support (Complete)
- [x] Add find_skills_from_marketplace()
- [x] Integrate with install_from_git()

### Phase 8d: Tests & Docs (In Progress)
- [ ] Add unit tests
- [ ] Update USER_MANUAL.md
