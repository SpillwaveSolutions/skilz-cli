# Phase 3: Developer Experience

## Overview

Improve developer experience for contributors and users through better tooling, documentation, and installation options.

## Goals

1. **Test Coverage** - Achieve 80%+ code coverage with testable architecture
2. **Task Automation** - Provide standardized development commands via Taskfile
3. **Installation Documentation** - Clear instructions for pip, poetry, and GitHub checkout
4. **PyPI Publishing** - Enable `pip install skilz` for end users

## Requirements

### 3.1 Test Coverage & Testability

**Problem**: CLI and installer modules had low test coverage (0% and 13% respectively).

**Solution**:
- Refactor `cli.py` to move `cmd_install` to `commands/install_cmd.py`
- Follow existing command pattern for consistency
- Add comprehensive unit tests with mocking
- Target 80%+ overall coverage

**Acceptance Criteria**:
- [ ] `cli.py` coverage >= 80%
- [ ] `installer.py` coverage >= 80%
- [ ] `install_cmd.py` coverage >= 90%
- [ ] All 150+ tests pass
- [ ] Overall coverage >= 80%

### 3.2 Task Automation (Taskfile)

**Problem**: Developers must remember various `PYTHONPATH=src python -m ...` commands.

**Solution**: Create `Taskfile.yml` with standardized tasks.

**Required Tasks**:
- `task install` - Install in development mode
- `task test` - Run all tests
- `task coverage` - Run tests with coverage
- `task lint` - Run ruff linter
- `task format` - Format code with ruff
- `task typecheck` - Run mypy
- `task build` - Build distribution packages
- `task clean` - Remove build artifacts
- `task ci` - Run full CI pipeline locally
- `task publish` - Publish to PyPI
- `task publish:test` - Publish to TestPyPI

**Acceptance Criteria**:
- [ ] `Taskfile.yml` exists in project root
- [ ] `task --list` shows all available tasks
- [ ] `task test` runs successfully
- [ ] `task coverage` shows 80%+ coverage
- [ ] `task ci` runs full pipeline

### 3.3 Installation Documentation

**Problem**: USER_MANUAL.md has broken/incomplete installation instructions.

**Solution**: Update documentation with clear installation paths.

**Installation Methods**:

1. **From PyPI** (future - when published):
   ```bash
   pip install skilz
   ```

2. **From GitHub with pip**:
   ```bash
   pip install git+https://github.com/spillwave/skilz-cli.git
   ```

3. **Development install**:
   ```bash
   git clone https://github.com/spillwave/skilz-cli.git
   cd skilz-cli
   pip install -e ".[dev]"
   ```

4. **With Task (recommended for development)**:
   ```bash
   git clone https://github.com/spillwave/skilz-cli.git
   cd skilz-cli
   task install
   ```

**Acceptance Criteria**:
- [ ] README.md has clear installation section
- [ ] USER_MANUAL.md installation instructions work
- [ ] Development setup instructions are complete
- [ ] All installation methods tested

### 3.4 PyPI Publishing (Future)

**Problem**: Users cannot `pip install skilz` directly.

**Solution**: Publish to PyPI when ready for release.

**Prerequisites**:
- [ ] Version 0.1.0 stable
- [ ] Documentation complete
- [ ] Tests passing
- [ ] License confirmed (MIT)
- [ ] PyPI account configured

**Publishing Process**:
1. `task release:check` - Run all checks
2. `task release:build` - Build artifacts
3. `task publish:test` - Test on TestPyPI
4. `task publish` - Publish to PyPI

## Non-Goals

- Poetry support (using hatchling/pip instead)
- Conda packaging (future consideration)
- Pre-commit hooks (optional, not required)

## Dependencies

- Requires Phase 1 & 2 complete
- Requires Task CLI installed for development
