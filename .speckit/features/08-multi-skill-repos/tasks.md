# Feature 08: Multi-Skill Repository Support - Tasks

## Phase 8a: Bug Fix

### T1: Fix Hidden Directory Filter
- [x] Update `find_skills_in_repo()` to only skip `.git`
- [x] Use relative path checking instead of absolute path
- **DoD:** Skills in `.claude/skills/` and `.opencode/skills/` are discovered

**Files Changed:**
- `src/skilz/git_install.py:77-81`

## Phase 8b: --skill Flag

### T2: Add --skill CLI Argument
- [x] Add `--skill NAME` argument to install_parser
- [x] Pass `skill_filter_name` through install_cmd.py
- [x] Add filtering logic in git_install.py
- [x] Show available skills in error message if not found
- **DoD:** `skilz install -g <url> --skill <name>` works

**Files Changed:**
- `src/skilz/cli.py:148-152`
- `src/skilz/commands/install_cmd.py:74,84`
- `src/skilz/git_install.py:209,261-279`

## Phase 8c: Marketplace Support

### T3: Add Official Plugin Marketplace Support
- [x] Create `find_skills_from_marketplace()` function
- [x] Check `.claude-plugin/marketplace.json` first (official location)
- [x] Fall back to `marketplace.json` at repo root
- [x] Parse `plugins` array with `name` and `source` fields
- [x] Integrate with `install_from_git()` flow
- [x] Add validation for skill paths (SKILL.md must exist)
- **DoD:** Skills from official marketplace.json are discovered

**Files Changed:**
- `src/skilz/git_install.py:7,102-162,247-249`

## Phase 8d: Tests & Documentation

### T4: Add Unit Tests
- [x] Test hidden directory fix (skills in `.claude/skills/` discovered)
- [x] Test --skill flag success case
- [x] Test --skill flag not-found case (shows available skills)
- [x] Test `.claude-plugin/marketplace.json` discovery (official location)
- [x] Test `marketplace.json` at root fallback
- [x] Test marketplace with `plugins` array and `source` field parsing
- **DoD:** All new code paths have test coverage (aim for 80%+)

### T5: Update Documentation
- [ ] Update USER_MANUAL.md with --skill flag usage
- [ ] Add examples for multi-skill repositories
- [ ] Document marketplace.json support
- **DoD:** Documentation reflects new functionality

## Task Dependencies

```
T1 ────► T2 ────► T3 ────► T4
                    │
                    └─────► T5
```

## Estimated Complexity

| Task | Complexity | LOC |
|------|------------|-----|
| T1 (Bug Fix) | Low | ~5 |
| T2 (--skill Flag) | Medium | ~25 |
| T3 (Marketplace) | Medium | ~60 |
| T4 (Tests) | Medium | ~150 |
| T5 (Docs) | Low | ~50 |
| **Total** | | **~290** |

## Completion Status

- [x] T1: Fix Hidden Directory Filter
- [x] T2: Add --skill CLI Argument
- [x] T3: Add Official Plugin Marketplace Support
- [x] T4: Add Unit Tests
- [ ] T5: Update Documentation
