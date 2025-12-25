# Phase 7: Implementation Plan - Universal Skills Directory

## Architecture Overview

### New Files
| File | Purpose |
|------|---------|
| `src/skilz/link_ops.py` | Symlink/copy operations, validation, broken link handling |
| `tests/test_link_ops.py` | Link operations unit tests |

### Modified Files
| File | Change |
|------|--------|
| `src/skilz/installer.py` | Add `--copy`, `--symlink`, `-f`, `-g` support |
| `src/skilz/scanner.py` | Detect symlinks, resolve canonical paths |
| `src/skilz/manifest.py` | Add `install_mode`, `canonical_path` fields |
| `src/skilz/cli.py` | Add new flags to install subparser |
| `src/skilz/commands/install_cmd.py` | Pass mode flags, handle -f/-g sources |
| `src/skilz/commands/list_cmd.py` | Show symlink status in output |
| `src/skilz/commands/remove_cmd.py` | Handle symlink vs copy removal |
| `src/skilz/commands/update_cmd.py` | Update canonical sources |

## Design Decisions

### D1: Link Operations as Separate Module
**Decision:** Create dedicated `link_ops.py` for all symlink/copy operations
**Rationale:** Single responsibility, easier testing, platform abstraction

### D2: Mode Flag Priority
**Decision:** Explicit flags override agent defaults
**Rationale:** User intent should always win

### D3: Universal as Canonical Source
**Decision:** Symlinks always point to `.skilz/skills/` or `~/.skilz/skills/`
**Rationale:** Single source of truth for shared skills

### D4: Manifest Tracks Mode
**Decision:** Store `install_mode` and `canonical_path` in manifest
**Rationale:** Enables proper handling in list/update/remove

### D5: Graceful Broken Symlink Handling
**Decision:** Report broken symlinks as warnings, don't crash
**Rationale:** User may be in process of setting up or moved files

## Component Details

### Link Operations Module (`link_ops.py`)

```python
"""Symlink and copy operations for skill installation."""

from pathlib import Path
import shutil
from typing import Literal

InstallMode = Literal["copy", "symlink"]

def create_symlink(source: Path, target: Path) -> None:
    """Create a symbolic link from target to source.

    Args:
        source: The skill directory to link to (canonical location)
        target: Where to create the symlink (agent's skills dir)

    Raises:
        FileExistsError: If target already exists
        OSError: If symlink creation fails (permissions, Windows without dev mode)
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source, target_is_directory=True)

def copy_skill(source: Path, target: Path) -> None:
    """Copy skill directory from source to target.

    Args:
        source: Source skill directory
        target: Destination directory
    """
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=False)

def is_symlink(path: Path) -> bool:
    """Check if path is a symbolic link."""
    return path.is_symlink()

def get_symlink_target(path: Path) -> Path | None:
    """Get the target of a symlink, or None if not a symlink."""
    if path.is_symlink():
        return path.resolve()
    return None

def is_broken_symlink(path: Path) -> bool:
    """Check if path is a broken symbolic link."""
    return path.is_symlink() and not path.exists()

def validate_skill_source(path: Path) -> tuple[bool, str | None]:
    """Validate that a path contains a valid skill.

    Returns:
        (is_valid, error_message)
    """
    if not path.exists():
        return False, f"Path does not exist: {path}"
    if not path.is_dir():
        return False, f"Path is not a directory: {path}"
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return False, f"Missing SKILL.md in: {path}"
    return True, None

def determine_install_mode(
    explicit_mode: InstallMode | None,
    agent_default: InstallMode,
) -> InstallMode:
    """Determine installation mode based on flags and defaults.

    Priority: explicit flag > agent default
    """
    if explicit_mode is not None:
        return explicit_mode
    return agent_default
```

### CLI Changes (`cli.py`)

Add to install subparser:
```python
install_parser.add_argument(
    "--copy",
    action="store_true",
    help="Force copy mode (duplicate files)",
)
install_parser.add_argument(
    "--symlink",
    action="store_true",
    help="Force symlink mode (create symbolic link)",
)
install_parser.add_argument(
    "--global",
    action="store_true",
    dest="global_install",
    help="Install to ~/.skilz/skills/ (universal directory)",
)
install_parser.add_argument(
    "-f", "--file",
    metavar="PATH",
    help="Install from local filesystem path",
)
install_parser.add_argument(
    "-g", "--git",
    metavar="URL",
    help="Install from git repository URL",
)
```

### Installer Changes (`installer.py`)

```python
def install_skill(
    skill_id: str,
    agent: str,
    project_level: bool = False,
    mode: InstallMode | None = None,  # NEW
    source_path: Path | None = None,  # NEW: for -f
    git_url: str | None = None,       # NEW: for -g
) -> InstallResult:
    """Install a skill with copy or symlink mode."""

    # Determine source
    if source_path:
        source = source_path
    elif git_url:
        source = clone_to_temp(git_url)
    else:
        source = download_from_registry(skill_id)

    # Validate source
    is_valid, error = validate_skill_source(source)
    if not is_valid:
        raise InstallError(error)

    # Determine mode
    agent_config = get_agent_config(agent)
    install_mode = determine_install_mode(mode, agent_config.default_mode)

    # Get target directory
    target = get_skills_dir(agent, project_level) / skill_name

    # Install
    if install_mode == "symlink":
        # Ensure canonical copy exists
        canonical = ensure_canonical_copy(source, skill_name)
        create_symlink(canonical, target)
    else:
        copy_skill(source, target)

    # Update manifest
    save_manifest(target, install_mode=install_mode, canonical_path=str(canonical) if install_mode == "symlink" else None)
```

### Manifest Changes (`manifest.py`)

```python
@dataclass
class SkillManifest:
    skill_id: str
    name: str
    version: str
    installed_at: str
    agent: str
    git_sha: str | None = None
    install_mode: Literal["copy", "symlink"] = "copy"  # NEW
    canonical_path: str | None = None  # NEW: target if symlink
```

### Scanner Changes (`scanner.py`)

```python
@dataclass
class InstalledSkill:
    # ... existing fields ...
    install_mode: Literal["copy", "symlink"] = "copy"
    canonical_path: Path | None = None
    is_broken_symlink: bool = False

def scan_skill_directory(skill_dir: Path) -> InstalledSkill | None:
    """Scan a skill directory, handling symlinks."""
    # Check for broken symlink first
    if is_broken_symlink(skill_dir):
        return InstalledSkill(
            ...,
            is_broken_symlink=True,
        )

    # Check if symlink
    if is_symlink(skill_dir):
        canonical = get_symlink_target(skill_dir)
        # Read manifest from canonical location
        manifest = load_manifest(canonical)
        return InstalledSkill(
            ...,
            install_mode="symlink",
            canonical_path=canonical,
        )

    # Normal copy
    manifest = load_manifest(skill_dir)
    return InstalledSkill(..., install_mode="copy")
```

### List Command Changes (`list_cmd.py`)

Output format:
```
Installed Skills (Claude Code - User Level):

  pdf                v1.2.0    [copy]     2024-12-25
  xlsx               v1.0.0    [symlink]  ~/.skilz/skills/xlsx  2024-12-25
  broken-skill       v?        [ERROR]    Broken symlink

Total: 3 skills (1 copy, 1 symlink, 1 error)
```

### Remove Command Changes (`remove_cmd.py`)

```python
def remove_skill(skill_name: str, agent: str, project_level: bool) -> bool:
    """Remove a skill, handling symlinks appropriately."""
    skill_dir = find_skill_directory(skill_name, agent, project_level)

    if is_symlink(skill_dir):
        # Just remove the symlink, not the target
        skill_dir.unlink()
    else:
        # Remove the directory
        shutil.rmtree(skill_dir)

    return True
```

## Implementation Phases

### Phase 7a: Link Operations Module
- [ ] Create `src/skilz/link_ops.py`
- [ ] Implement `create_symlink()`, `copy_skill()`
- [ ] Implement `is_symlink()`, `get_symlink_target()`
- [ ] Implement `is_broken_symlink()`
- [ ] Implement `validate_skill_source()`
- [ ] Implement `determine_install_mode()`
- [ ] Create `tests/test_link_ops.py`

### Phase 7b: Manifest Extensions
- [ ] Add `install_mode` field to `SkillManifest`
- [ ] Add `canonical_path` field to `SkillManifest`
- [ ] Update manifest serialization/deserialization
- [ ] Ensure backward compatibility with existing manifests

### Phase 7c: Scanner Updates
- [ ] Add symlink detection to `scan_skill_directory()`
- [ ] Add `install_mode`, `canonical_path` to `InstalledSkill`
- [ ] Add `is_broken_symlink` detection
- [ ] Update tests

### Phase 7d: Installer Updates
- [ ] Add `mode` parameter to `install_skill()`
- [ ] Add `source_path` parameter for `-f` flag
- [ ] Add `git_url` parameter for `-g` flag
- [ ] Implement `ensure_canonical_copy()`
- [ ] Update installation logic for symlink mode
- [ ] Update tests

### Phase 7e: CLI Updates
- [ ] Add `--copy` flag to install
- [ ] Add `--symlink` flag to install
- [ ] Add `--global` flag to install
- [ ] Add `-f/--file` option to install
- [ ] Add `-g/--git` option to install
- [ ] Validate mutually exclusive options

### Phase 7f: Command Updates
- [ ] Update list command to show mode/target
- [ ] Update remove command for symlinks
- [ ] Update update command for canonical sources
- [ ] Add broken symlink warnings

### Phase 7g: Tests & Validation
- [ ] 90%+ coverage on link_ops.py
- [ ] Integration tests for symlink workflow
- [ ] Cross-platform symlink tests (if CI supports)
- [ ] Broken symlink handling tests

## Test Coverage Target

| Test File | Tests Expected |
|-----------|----------------|
| test_link_ops.py | ~20 |
| test_installer.py (additions) | ~10 |
| test_scanner.py (additions) | ~5 |
| test_list_cmd.py (additions) | ~5 |
| test_remove_cmd.py (additions) | ~3 |
| **Total New** | **~43** |

## Verification Checklist

Before marking complete:

- [ ] `skilz install pdf --symlink` creates symlink
- [ ] `skilz install pdf --copy` creates copy
- [ ] `skilz install pdf --global` installs to ~/.skilz/skills/
- [ ] `skilz install -f /path/to/skill` works
- [ ] `skilz list` shows install mode and symlink target
- [ ] `skilz remove` handles symlinks correctly
- [ ] Broken symlinks reported as warnings, not errors
- [ ] 90%+ test coverage on new code
- [ ] All existing tests still pass
