# SKILZ-085: Default Agent Should Be Claude

## Status: COMPLETED

## Problem Statement

Default agent fallback is "gemini" instead of "claude". When no agent markers are found, the system should default to Claude Code as the primary supported agent.

## Root Cause

The `detect_agent()` function's final fallback was returning "claude" but without proper logging. The config.py already had the correct default, but explicit logging was needed for debugging.

## Solution

1. Ensure `detect_agent()` final return is "claude" with debug logging
2. Verify `config.py` has `DEFAULT_AGENT = "claude"` (already correct)

## Files Modified

- `src/skilz/agents.py`
  - Added debug logging before final "claude" return
  - Log message: `[SKILZ-085] No agent markers found, using default: claude`

## Implementation Details

```python
# In detect_agent() function, final fallback:
logger.debug("[SKILZ-085] No agent markers found, using default: claude")
return "claude"
```

## Acceptance Criteria

- [x] `detect_agent()` returns "claude" when no markers found
- [x] Debug logging added for traceability
- [x] `config.py` DEFAULT_AGENT is "claude"
- [x] All existing tests pass
- [x] Type checking passes
