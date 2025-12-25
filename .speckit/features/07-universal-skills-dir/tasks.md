# Phase 7: Tasks - Universal Skills Directory

## Status Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 7a: Link Operations Module | ⬜ Pending | - |
| 7b: Manifest Extensions | ⬜ Pending | - |
| 7c: Scanner Updates | ⬜ Pending | - |
| 7d: Installer Updates | ⬜ Pending | - |
| 7e: CLI Updates | ⬜ Pending | - |
| 7f: Command Updates | ⬜ Pending | - |
| 7g: Tests & Validation | ⬜ Pending | - |
| **Total** | **⬜ Pending** | **0 tests** |

---

## Phase 7a: Link Operations Module

- [ ] Create `src/skilz/link_ops.py`
- [ ] Implement `create_symlink(source: Path, target: Path) -> None`
- [ ] Implement `copy_skill(source: Path, target: Path) -> None`
- [ ] Implement `is_symlink(path: Path) -> bool`
- [ ] Implement `get_symlink_target(path: Path) -> Path | None`
- [ ] Implement `is_broken_symlink(path: Path) -> bool`
- [ ] Implement `validate_skill_source(path: Path) -> tuple[bool, str | None]`
- [ ] Implement `determine_install_mode(explicit: str | None, default: str) -> str`
- [ ] Create `tests/test_link_ops.py`
- [ ] Test symlink creation on supported platforms
- [ ] Test copy operation
- [ ] Test broken symlink detection
- [ ] Test skill source validation

**Files:** `src/skilz/link_ops.py`, `tests/test_link_ops.py`

**Estimated:** 2 hours

---

## Phase 7b: Manifest Extensions

- [ ] Add `install_mode: Literal["copy", "symlink"]` field to `SkillManifest`
- [ ] Add `canonical_path: str | None` field to `SkillManifest`
- [ ] Update `to_dict()` to include new fields
- [ ] Update `from_dict()` to parse new fields
- [ ] Ensure backward compatibility (missing fields default to `"copy"`, `None`)
- [ ] Update existing tests to cover new fields

**Files:** `src/skilz/manifest.py`, `tests/test_manifest.py`

**Estimated:** 1 hour

---

## Phase 7c: Scanner Updates

- [ ] Import link_ops functions in scanner.py
- [ ] Add `install_mode` field to `InstalledSkill` dataclass
- [ ] Add `canonical_path: Path | None` field to `InstalledSkill`
- [ ] Add `is_broken_symlink: bool` field to `InstalledSkill`
- [ ] Update `scan_skill_directory()` to detect symlinks
- [ ] Handle broken symlinks gracefully (warn, don't crash)
- [ ] Read manifest from canonical path for symlinked skills
- [ ] Update `InstalledSkill.to_dict()` to include new fields
- [ ] Add tests for symlink scanning
- [ ] Add tests for broken symlink detection

**Files:** `src/skilz/scanner.py`, `tests/test_scanner.py`

**Estimated:** 1.5 hours

---

## Phase 7d: Installer Updates

- [ ] Add `mode: Literal["copy", "symlink"] | None` parameter to `install_skill()`
- [ ] Add `source_path: Path | None` parameter for `-f` flag
- [ ] Add `git_url: str | None` parameter for `-g` flag
- [ ] Implement `clone_git_repo(url: str) -> Path` (clone to temp dir)
- [ ] Implement `ensure_canonical_copy(source: Path, name: str) -> Path`
- [ ] Update installation flow:
  - [ ] If symlink mode: ensure canonical exists, create symlink
  - [ ] If copy mode: copy directly to target
- [ ] Pass `install_mode` and `canonical_path` to manifest creation
- [ ] Clean up temp directory after git clone
- [ ] Add tests for symlink installation
- [ ] Add tests for copy installation
- [ ] Add tests for filesystem source installation
- [ ] Add tests for git URL installation

**Files:** `src/skilz/installer.py`, `tests/test_installer.py`

**Estimated:** 3 hours

---

## Phase 7e: CLI Updates

- [ ] Add `--copy` flag to install subparser
  ```python
  install_parser.add_argument("--copy", action="store_true")
  ```
- [ ] Add `--symlink` flag to install subparser
  ```python
  install_parser.add_argument("--symlink", action="store_true")
  ```
- [ ] Add `--global` flag to install subparser
  ```python
  install_parser.add_argument("--global", action="store_true", dest="global_install")
  ```
- [ ] Add `-f/--file` option to install subparser
  ```python
  install_parser.add_argument("-f", "--file", metavar="PATH")
  ```
- [ ] Add `-g/--git` option to install subparser
  ```python
  install_parser.add_argument("-g", "--git", metavar="URL")
  ```
- [ ] Validate mutually exclusive: `--copy` and `--symlink`
- [ ] Validate mutually exclusive: skill_id, `-f`, and `-g`
- [ ] Update help text with new options
- [ ] Add CLI argument tests

**Files:** `src/skilz/cli.py`, `tests/test_cli.py`

**Estimated:** 1 hour

---

## Phase 7f: Command Updates

### List Command
- [ ] Update output format to show `[copy]` or `[symlink]`
- [ ] Show symlink target path for symlinked skills
- [ ] Show `[ERROR]` for broken symlinks with warning
- [ ] Update summary line with mode counts
- [ ] Add tests for new output format

### Remove Command
- [ ] Check if skill is symlink before removal
- [ ] If symlink: `unlink()` the symlink, don't touch target
- [ ] If copy: `shutil.rmtree()` as before
- [ ] Warn if removing canonical that has symlinks (optional)
- [ ] Add tests for symlink removal
- [ ] Add tests for copy removal

### Update Command
- [ ] Detect if skill is symlinked
- [ ] If symlinked: update the canonical source
- [ ] If copy: update the copy directly
- [ ] Symlinks automatically reflect updates
- [ ] Add tests for updating symlinked skills
- [ ] Add tests for updating copied skills

**Files:**
- `src/skilz/commands/list_cmd.py`, `tests/test_list_cmd.py`
- `src/skilz/commands/remove_cmd.py`, `tests/test_remove_cmd.py`
- `src/skilz/commands/update_cmd.py`, `tests/test_update_cmd.py`

**Estimated:** 2 hours

---

## Phase 7g: Tests & Validation

### Unit Tests
- [ ] 90%+ coverage on `link_ops.py`
- [ ] Test all symlink edge cases
- [ ] Test broken symlink handling
- [ ] Test cross-platform compatibility (where possible)

### Integration Tests
- [ ] Full workflow: `install --symlink` → `list` → `update` → `remove`
- [ ] Full workflow: `install --copy` → `list` → `update` → `remove`
- [ ] Full workflow: `install -f /path` → `list` → `remove`
- [ ] Error cases: broken symlinks, missing sources

### Coverage
- [ ] Run `task coverage` and verify 90%+ on new code
- [ ] Run `task test` and verify all tests pass
- [ ] Run `task lint` and verify no errors

**Files:** All test files

**Estimated:** 2 hours

---

## Verification Checklist

Before marking complete:

- [ ] `skilz install pdf --symlink` creates symlink to ~/.skilz/skills/pdf
- [ ] `skilz install pdf --copy` creates copy in agent directory
- [ ] `skilz install pdf --global` installs to ~/.skilz/skills/
- [ ] `skilz install -f ~/my-skills/pdf` works
- [ ] `skilz install -g https://github.com/user/skill` works
- [ ] `skilz list` shows `[copy]` or `[symlink]` for each skill
- [ ] `skilz list` shows symlink target for symlinked skills
- [ ] `skilz remove symlinked-skill` only removes symlink
- [ ] `skilz update symlinked-skill` updates canonical source
- [ ] Broken symlinks shown as warnings, not crashes
- [ ] All existing tests still pass
- [ ] 90%+ coverage on link_ops.py
- [ ] Code passes `task lint`
- [ ] Code passes `task check`

---

## Estimated Total Time

| Phase | Time |
|-------|------|
| 7a: Link Operations Module | 2h |
| 7b: Manifest Extensions | 1h |
| 7c: Scanner Updates | 1.5h |
| 7d: Installer Updates | 3h |
| 7e: CLI Updates | 1h |
| 7f: Command Updates | 2h |
| 7g: Tests & Validation | 2h |
| **Total** | **~12-13 hours** |

---

## GitHub Issues to Create

| Issue | Title |
|-------|-------|
| #10 | [Phase 7a] Create link_ops.py module |
| #11 | [Phase 7b] Add install_mode to manifest |
| #12 | [Phase 7c] Update scanner for symlinks |
| #13 | [Phase 7d] Add symlink/copy to installer |
| #14 | [Phase 7e] Add CLI flags for install modes |
| #15 | [Phase 7f] Update list/remove/update commands |
| #16 | [Phase 7g] Tests and validation |
