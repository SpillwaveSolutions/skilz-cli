# SKILZ-081: Agent Lookup Order

## Status: COMPLETED

## Problem Statement

Agent detection lookup order is incorrect. The `detect_agent()` function is missing a parent directory check for the universal agent pattern (`../skilz/skills`).

## Root Cause

When a project is nested inside a directory that has a `skilz/skills` folder in its parent, the agent detection should recognize this as a "universal" agent pattern. This check was missing from the detection order.

## Solution

1. Add `_check_parent_skilz()` function to check for `../skilz/skills` directory
2. Update `detect_agent()` to call parent check after config override but before marker detection

## Files Modified

- `src/skilz/agents.py`
  - Added `_check_parent_skilz(project_dir: Path) -> str | None` function
  - Updated `detect_agent()` to include parent directory check in priority order

## Implementation Details

```python
def _check_parent_skilz(project_dir: Path) -> str | None:
    """Check for ../skilz/skills directory (universal agent pattern)."""
    parent = project_dir.parent
    parent_skilz = parent / "skilz" / "skills"
    if parent_skilz.exists() and parent_skilz.is_dir():
        logger.debug("[SKILZ-081] Found parent skilz/skills at %s", parent_skilz)
        return "universal"
    return None
```

## Detection Order (Updated)

1. Check config file for `agent_default` setting
2. **NEW: Check for `../skilz/skills` (parent directory universal pattern)**
3. Check for `.claude/` in project directory
4. Check for `.gemini/` in project directory
5. Check for `.codex/` in project directory
6. Check for `~/.claude/` (user has Claude Code installed)
7. Check for `~/.gemini/` (user has Gemini CLI)
8. Check for `~/.codex/` (user has OpenAI Codex)
9. Check for `~/.config/opencode/` (user has OpenCode)
10. Default to "claude"

## Acceptance Criteria

- [x] `_check_parent_skilz()` function added
- [x] `detect_agent()` calls parent check after config but before markers
- [x] Returns "universal" when parent skilz/skills exists
- [x] All existing tests pass
- [x] Type checking passes
