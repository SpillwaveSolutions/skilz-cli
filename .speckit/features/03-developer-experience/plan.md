# Phase 3: Plan

## Architecture Decisions

### 3.1 CLI Refactoring for Testability

**Decision**: Move `cmd_install` from `cli.py` to `commands/install_cmd.py`

**Rationale**:
- Follows existing pattern (`list_cmd.py`, `update_cmd.py`, `remove_cmd.py`)
- Enables isolated unit testing with mocks
- Separates argument parsing from command execution
- Late imports remain for `--help` performance

**Changes**:
```
cli.py
├── create_parser()     # Unchanged - testable
├── main()              # Updated - imports cmd_install from commands
└── cmd_install()       # REMOVED - moved to commands/

commands/
├── __init__.py         # Added cmd_install export
├── install_cmd.py      # NEW - contains cmd_install
├── list_cmd.py         # Unchanged
├── update_cmd.py       # Unchanged
└── remove_cmd.py       # Unchanged
```

### 3.2 Testing Strategy

**Approach**: Mock at function level using `unittest.mock.patch`

**Pattern** (from existing tests):
```python
with patch("skilz.installer.install_skill") as mock:
    mock.return_value = None  # or side_effect for errors
    result = cmd_install(args)
    assert result == 0
```

**Test Files**:
- `tests/test_cli.py` - Parser tests + main() dispatch tests
- `tests/test_install_cmd.py` - Install command handler tests
- `tests/test_installer.py` - Core installer logic tests

### 3.3 Taskfile Structure

**Approach**: Single `Taskfile.yml` with namespaced tasks

**Categories**:
- Installation: `install`, `install:deps`
- Build: `build`, `clean`
- Testing: `test`, `coverage`, `coverage:check`, `coverage:html`
- Quality: `lint`, `format`, `typecheck`, `check`
- Development: `run`, `version`, `help`
- Release: `release:check`, `release:build`, `publish`, `publish:test`
- CI: `ci` (runs full pipeline)

**Aliases**: `t` (test), `c` (coverage), `l` (lint), `f` (format)

### 3.4 Documentation Structure

**README.md** - Quick start, basic install
**docs/USER_MANUAL.md** - Complete usage guide
**docs/CONTRIBUTING.md** - Developer setup (optional)

## Implementation Phases

### Phase 3a: Test Coverage (COMPLETE)
1. Create `commands/install_cmd.py`
2. Update `commands/__init__.py`
3. Update `cli.py` to use new module
4. Create `tests/test_cli.py`
5. Create `tests/test_install_cmd.py`
6. Create `tests/test_installer.py`
7. Verify 80%+ coverage

### Phase 3b: Task Automation (COMPLETE)
1. Create `Taskfile.yml`
2. Add all standard tasks
3. Verify `task test` works
4. Verify `task coverage` works

### Phase 3c: Documentation (IN PROGRESS)
1. Fix README.md installation section
2. Fix docs/USER_MANUAL.md
3. Add development setup instructions
4. Test all installation methods

### Phase 3d: PyPI Publishing (PENDING)
1. Configure PyPI credentials
2. Test with TestPyPI
3. Publish to PyPI
4. Update documentation with pip install

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking CLI behavior | Keep exact function signatures |
| Test flakiness | Use temp_dir fixtures, mock external calls |
| PyPI name conflict | Check availability before publishing |
