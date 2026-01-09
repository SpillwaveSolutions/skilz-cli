# Tasks: Skill Path Fallback Discovery

**Input**: Design documents from `.speckit/features/11-skill-path-fallback/`
**Prerequisites**: specify.md (required), plan.md (required)

## Phase 1: Setup

- [x] T001 Create feature directory `.speckit/features/11-skill-path-fallback/`
- [x] T002 Create specify.md
- [x] T003 Create plan.md
- [x] T004 Create tasks.md

---

## Phase 2: User Story 1 - Path Fallback with Warning (Priority: P1)

**Goal**: Add user-visible warning when skill path differs from expected

**Independent Test**: Install skill with mismatched path, verify warning appears

### Tests for User Story 1

- [x] T005 [P] [US1] Add test `test_install_skill_warns_on_path_change` in `tests/test_installer.py`
- [x] T006 [P] [US1] Add test `test_install_skill_no_warning_when_path_matches` in `tests/test_installer.py`
- [x] T007 [P] [US1] Add test `test_install_skill_warning_goes_to_stderr` in `tests/test_installer.py`

### Implementation for User Story 1

- [x] T008 [US1] Modify warning logic in `src/skilz/installer.py` (lines 437-441)
  - Change from `if verbose:` to always print warning
  - Add `file=sys.stderr` to print statement
  - Use minimal message format: `Warning: Skill 'X' found at different path than expected`
  - Keep verbose details (expected/found paths) behind `if verbose:`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 3: Polish & Documentation

- [x] T009 Update `CHANGELOG.md` with enhancement description
- [x] T010 Run full test suite to verify no regressions (expect 620+ tests)
- [x] T011 Run `task check` (lint + typecheck + test)

---

## Phase 4: Feature 12 Placeholder

- [x] T012 Create `.speckit/features/12-marketplace-submission/specify.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (US1)**: Depends on Phase 1
  - Tests (T005-T007) can run in parallel
  - Implementation (T008) can start after tests are written
- **Phase 3 (Polish)**: Depends on Phase 2

### Parallel Opportunities

```bash
# Launch tests in parallel:
T005: test_install_skill_warns_on_path_change
T006: test_install_skill_no_warning_when_path_matches  
T007: test_install_skill_warning_goes_to_stderr
```

---

## Notes

- Total new tests: 3
- Total lines changed: ~15-20
- Estimated time: 30-45 minutes
