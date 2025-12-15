# Phase 3: Tasks

## Phase 3a: Test Coverage

### T1: CLI Refactoring
- [x] Create `src/skilz/commands/install_cmd.py`
- [x] Implement `cmd_install(args)` function
- [x] Handle SkilzError and unexpected exceptions
- [x] Use `getattr` for optional attributes
- [x] Update `src/skilz/commands/__init__.py` with export
- [x] Update `src/skilz/cli.py` to import from commands

**Definition of Done**: CLI works identically after refactor ✓

### T2: CLI Tests
- [x] Create `tests/test_cli.py`
- [x] Test `create_parser()` - all commands and options
- [x] Test `main()` - command dispatch
- [x] Test flag passing (verbose, project, agent)

**Definition of Done**: `cli.py` coverage >= 80% ✓

### T3: Install Command Tests
- [x] Create `tests/test_install_cmd.py`
- [x] Test success path
- [x] Test SkilzError handling
- [x] Test unexpected error handling
- [x] Test missing attributes

**Definition of Done**: `install_cmd.py` coverage >= 90% ✓

### T4: Installer Tests
- [x] Create `tests/test_installer.py`
- [x] Test `copy_skill_files()` function
- [x] Test `install_skill()` with mocked dependencies
- [x] Test error paths (source not found, etc.)
- [x] Test verbose output

**Definition of Done**: `installer.py` coverage >= 80% ✓

### T5: Coverage Verification
- [x] Run `pytest --cov` and verify 80%+
- [x] All 159 tests pass
- [x] Overall coverage 92%

**Definition of Done**: Coverage report shows 80%+ ✓

---

## Phase 3b: Task Automation

### T6: Taskfile Creation
- [x] Create `Taskfile.yml` in project root
- [x] Add install tasks (`install`, `install:deps`)
- [x] Add build tasks (`build`, `clean`)
- [x] Add test tasks (`test`, `test:fast`, `coverage`)
- [x] Add quality tasks (`lint`, `format`, `typecheck`, `check`)
- [x] Add release tasks (`release:check`, `publish`)
- [x] Add CI task (`ci`)
- [x] Add convenience aliases (`t`, `c`, `l`, `f`)

**Definition of Done**: `task --list` shows all tasks ✓

### T7: Taskfile Verification
- [x] Verify `task test` runs tests
- [x] Verify `task coverage` shows coverage
- [x] Verify `task --list` works

**Definition of Done**: All tasks work correctly ✓

---

## Phase 3c: Documentation

### T8: README Installation Section
- [x] Add "Installation" section to README.md
- [x] Document pip install from PyPI (future)
- [x] Document pip install from GitHub
- [x] Document development install
- [x] Document Task-based workflow

**Definition of Done**: README has clear installation instructions ✓

### T9: USER_MANUAL.md Fixes
- [x] Review current USER_MANUAL.md
- [x] Fix broken/incomplete sections
- [x] Add complete installation guide
- [x] Add troubleshooting section (already existed)
- [x] Add Development section with Task commands

**Definition of Done**: USER_MANUAL.md is complete and accurate ✓

### T10: Development Setup Guide
- [x] Document prerequisites (Python 3.10+, Task)
- [x] Document clone + install workflow
- [x] Document running tests
- [x] Document code quality checks
- [x] Add manual commands (without Task)

**Definition of Done**: New developer can set up environment from docs ✓

---

## Phase 3d: PyPI Publishing

### T11: Pre-publish Checks
- [ ] Verify version is correct (0.1.0)
- [ ] Verify license (MIT)
- [ ] Verify README renders correctly
- [ ] Check PyPI name availability
- [ ] Set up PyPI/TestPyPI credentials

**Definition of Done**: All pre-publish checks pass

### T12: TestPyPI Publishing
- [ ] Run `task release:check`
- [ ] Run `task release:build`
- [ ] Run `task publish:test`
- [ ] Test install from TestPyPI

**Definition of Done**: Package installable from TestPyPI

### T13: PyPI Publishing
- [ ] Run `task publish`
- [ ] Verify `pip install skilz` works
- [ ] Update documentation with pip install

**Definition of Done**: Package available on PyPI

---

## Task Dependencies

```
T1 (refactor) ──► T2 (cli tests) ──► T5 (verify)
      │                                  ▲
      └──────────► T3 (install cmd) ─────┘
      │                                  ▲
      └──────────► T4 (installer) ───────┘

T6 (taskfile) ──► T7 (verify taskfile)

T8 (readme) ──► T9 (manual) ──► T10 (dev guide)
                                      │
                                      ▼
                    T11 (pre-publish) ──► T12 (testpypi) ──► T13 (pypi)
```

## Progress Summary

| Phase | Status | Completion |
|-------|--------|------------|
| 3a: Test Coverage | ✅ COMPLETE | 100% |
| 3b: Task Automation | ✅ COMPLETE | 100% |
| 3c: Documentation | ✅ COMPLETE | 100% |
| 3d: PyPI Publishing | ⏳ DEFERRED | 0% |

**Overall Phase 3**: 75% complete (PyPI deferred to future release)
