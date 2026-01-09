# Implementation Plan: Skill Path Fallback Discovery

**Branch**: `11-skill-path-fallback` | **Date**: 2026-01-08 | **Spec**: specify.md

## Summary

Enhance the existing path fallback logic in `installer.py` to ALWAYS display a user-visible warning when a skill is found at a different path than expected. Currently, this information is only shown in verbose mode. This change improves user experience when marketplace/registry data becomes stale due to repository reorganizations.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: None (stdlib only)  
**Storage**: N/A  
**Testing**: pytest  
**Target Platform**: macOS, Linux, Windows  
**Project Type**: Single (CLI tool)  
**Performance Goals**: No measurable impact (single string comparison + print)  
**Constraints**: Warning must go to stderr, not stdout  
**Scale/Scope**: ~15-25 lines of code changes

## Constitution Check

- **Cross-Agent Universality**: This feature affects all agents equally
- **Reproducibility First**: No impact on reproducibility
- **Progressive Complexity**: Simple warning message, no new flags
- **Minimal Dependencies**: No new dependencies
- **Auditable by Default**: Improves auditability by informing user of path changes

## Project Structure

### Documentation (this feature)

```text
.speckit/features/11-skill-path-fallback/
├── specify.md         # This specification
├── plan.md            # This implementation plan
└── tasks.md           # Task breakdown
```

### Source Code (changes)

```text
src/skilz/
├── installer.py      # Add warning message (lines ~437-441)
└── (no other changes)

tests/
├── test_installer.py # Add tests for warning behavior
└── test_git_ops.py   # (existing tests sufficient)
```

**Structure Decision**: Minimal changes to existing structure. Single file modification + test additions.

## Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `src/skilz/installer.py` | Modify | Add always-visible warning when path differs (lines 437-441) |
| `tests/test_installer.py` | Add | Tests for warning visibility |
| `CHANGELOG.md` | Update | Document the enhancement |

## Code Changes (Detailed)

### `src/skilz/installer.py` (lines 437-441)

**Current Code:**
```python
if found_path:
    source_dir = found_path
    if verbose:
        rel_path = source_dir.relative_to(cache_path)
        print(f"  Using found location: {rel_path}")
```

**Proposed Code:**
```python
if found_path:
    source_dir = found_path
    # Always warn user about path change (not just verbose mode)
    print(
        f"Warning: Skill '{skill_info.skill_name}' found at different path than expected",
        file=sys.stderr,
    )
    if verbose:
        rel_path = source_dir.relative_to(cache_path)
        print(f"  Expected: {skill_info.skill_path}", file=sys.stderr)
        print(f"  Found at: {rel_path}", file=sys.stderr)
```

### Test Cases

1. `test_install_skill_warns_on_path_change` - Verify warning is printed when path differs
2. `test_install_skill_no_warning_when_path_matches` - Verify NO warning when path matches
3. `test_install_skill_warning_goes_to_stderr` - Verify warning goes to stderr, not stdout

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing tests | Low | Medium | Run full test suite before/after |
| Warning too verbose | Low | Low | Use minimal message format |
| Performance impact | None | None | Single print statement |

## Complexity Tracking

No constitution violations. This is a minimal, targeted change.
