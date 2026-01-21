# SKILZ-086: Version Mismatch - Tasks

## Status: COMPLETED

## Tasks

- [x] Import `version` and `PackageNotFoundError` from `importlib.metadata`
- [x] Replace hardcoded version with `version("skilz")` call
- [x] Add try/except for PackageNotFoundError
- [x] Set fallback version to "0.0.0.dev"
- [x] Run existing tests to verify no regressions
- [x] Run type checking (mypy)
- [x] Run linting (ruff)

## Verification

```bash
# Reinstall package
pip install -e .

# Check version
skilz --version

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
