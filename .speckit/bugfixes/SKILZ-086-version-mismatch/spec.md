# SKILZ-086: Version Mismatch

## Status: COMPLETED

## Problem Statement

CLI `--version` shows wrong version. Version was defined in two places (`__init__.py` and `pyproject.toml`) which could get out of sync.

## Root Cause

The `__version__` in `src/skilz/__init__.py` was hardcoded as a string literal (e.g., `"1.7.0"`), while the canonical version is defined in `pyproject.toml`. These could drift apart during releases.

## Solution

Use `importlib.metadata.version()` to read the version from the installed package metadata, which is derived from `pyproject.toml`. This creates a single source of truth.

## Files Modified

- `src/skilz/__init__.py`
  - Replaced hardcoded `__version__ = "1.7.0"` with dynamic version lookup
  - Added fallback to `"0.0.0.dev"` for development installs

## Implementation Details

**Before**:
```python
__version__ = "1.7.0"
```

**After**:
```python
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("skilz")
except PackageNotFoundError:
    __version__ = "0.0.0.dev"
```

## Benefits

1. **Single source of truth**: Version only defined in `pyproject.toml`
2. **Automatic sync**: CLI `--version` always matches installed package
3. **Development friendly**: Falls back to dev version when not installed

## Acceptance Criteria

- [x] `__version__` uses `importlib.metadata.version()`
- [x] Fallback to "0.0.0.dev" for PackageNotFoundError
- [x] `skilz --version` shows correct version after `pip install -e .`
- [x] All existing tests pass
- [x] Type checking passes
