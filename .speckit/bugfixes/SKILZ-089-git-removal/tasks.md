# SKILZ-089: .git Removal on Local Install - Tasks

## Status: COMPLETED

## Tasks

- [x] Update `copy_skill_files()` in `installer.py` to add ignore pattern
- [x] Update `copy_skill()` in `link_ops.py` to add ignore pattern
- [x] Add comment explaining SKILZ-089 fix
- [x] Run existing tests to verify no regressions
- [x] Run type checking (mypy)
- [x] Run linting (ruff)

## Verification

```bash
# All 640 tests pass
pytest -v

# Type checking passes
mypy src/skilz/

# Linting passes
ruff check src/skilz/
```

## Completion

- **Date**: 2026-01-20
- **PR**: https://github.com/SpillwaveSolutions/skilz-cli/pull/43
- **Commit**: fix/skilz-bugfixes-081-085-086-089
