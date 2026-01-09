# Known Bugs and Solutions

This document tracks bugs encountered during development and their solutions.

---

## Active Bugs

*(No active bugs at this time)*

---

## Resolved Bugs

### BUG-001: Codex Agent Not Auto-Detected

**Date Discovered:** 2026-01-08
**Date Resolved:** 2026-01-08
**Severity:** Medium
**Related Issue:** SKILZ-49 implementation review

**Symptoms:**
- Users with OpenAI Codex (`.codex/` or `~/.codex/`) must manually specify `--agent codex`
- Auto-detection skips over Codex even when directory markers are present
- Error-prone workflow: `skilz install skill` fails to detect Codex agent

**Root Cause:**
- Detection logic in `src/skilz/agents.py:detect_agent()` does not check for `.codex/` directories
- Codex is configured in `agent_registry.py` with proper paths, but detection function never looks for them

**Current Detection Order:**
```python
1. .claude/ (project)
2. .gemini/ (project)
3. ~/.claude/ (user)
4. ~/.gemini/ (user)
5. ~/.config/opencode/ (user)
6. Default to "claude"
```

**Expected Detection Order:**
```python
1. .claude/ (project)
2. .gemini/ (project)
3. .codex/ (project)        ← MISSING
4. ~/.claude/ (user)
5. ~/.gemini/ (user)
6. ~/.codex/ (user)         ← MISSING
7. ~/.config/opencode/ (user)
8. Default to "claude"
```

**Solution:**
Added Codex detection after Gemini in priority order in `src/skilz/agents.py` (lines 127-197):

```python
# Check for .codex in project directory
codex_project = project_dir / ".codex"
if codex_project.exists():
    return "codex"

# Later, after user-level Claude/Gemini checks:
codex_user = Path.home() / ".codex"
if codex_user.exists():
    return "codex"
```

**Tests Added:**
- `tests/test_agents.py::test_detect_codex_from_project_dir` (line 84)
- `tests/test_agents.py::test_detect_codex_from_user_dir` (line 97)
- `tests/test_agents.py::test_detect_gemini_priority_over_codex` (line 110)

**Test Results:** ✅ 605 tests passing (added 3 new tests)

**Prevention:**
- ✅ Added test coverage for Codex detection (3 tests)
- ✅ Verified all agents with `home_dir`/`project_dir` are included in detection
- Future: Add integration test to ensure all registry agents are covered by detection logic

---

### BUG-002: [Template]

**Date Discovered:** YYYY-MM-DD
**Date Resolved:** YYYY-MM-DD
**Severity:** Critical | High | Medium | Low

**Symptoms:**
- What the user experiences

**Root Cause:**
- Technical explanation of why it happens

**Solution:**
```python
# Code fix or configuration change
```

**Prevention:**
- How to prevent this in the future

---

## Bug Template

```markdown
### BUG-XXX: [Short Description]

**Date Discovered:** YYYY-MM-DD
**Date Resolved:** YYYY-MM-DD (or "In Progress")
**Severity:** Critical | High | Medium | Low

**Symptoms:**
- [Observable behavior]

**Root Cause:**
- [Technical explanation]

**Solution:**
[Code or config fix]

**Prevention:**
- [Testing, linting, or process changes]
```
