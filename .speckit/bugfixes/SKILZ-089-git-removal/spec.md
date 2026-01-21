# SKILZ-089: .git Removal on Local Install

## Status: COMPLETED

## Problem Statement

When installing a local skill that contains a `.git` directory, the `.git` directory is copied to the target location. This causes nested repository issues and can confuse Git operations.

## Root Cause

The `shutil.copytree()` calls in `installer.py` and `link_ops.py` did not have an `ignore` parameter to exclude the `.git` directory.

## Solution

Add `ignore=shutil.ignore_patterns('.git')` to all `shutil.copytree()` calls that copy skill directories.

## Files Modified

- `src/skilz/installer.py`
  - Updated `copy_skill_files()` function to exclude `.git`
- `src/skilz/link_ops.py`
  - Updated `copy_skill()` function to exclude `.git`

## Implementation Details

**installer.py - copy_skill_files() (~line 80)**:
```python
# SKILZ-089: Exclude .git directory to prevent nested repo issues
shutil.copytree(
    source_dir,
    target_dir,
    symlinks=True,
    ignore_dangling_symlinks=True,
    ignore=shutil.ignore_patterns(".git"),
)
```

**link_ops.py - copy_skill() (~line 78)**:
```python
# SKILZ-089: Exclude .git directory to prevent nested repo issues
shutil.copytree(
    source,
    target,
    symlinks=True,
    ignore_dangling_symlinks=True,
    ignore=shutil.ignore_patterns(".git"),
)
```

## Benefits

1. **No nested repos**: Installed skills don't contain `.git` directories
2. **Cleaner installs**: Reduces installed skill size
3. **No Git confusion**: Parent repo operations work correctly

## Acceptance Criteria

- [x] `installer.py` copytree excludes `.git`
- [x] `link_ops.py` copytree excludes `.git`
- [x] Local skill installs don't copy `.git` directory
- [x] All existing tests pass
- [x] Type checking passes
