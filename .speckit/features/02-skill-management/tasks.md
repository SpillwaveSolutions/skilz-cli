# Phase 2: Tasks

## Phase 2a: List Command

### T1: Scanner Module
- [x] Create `src/skilz/scanner.py`
- [x] Implement `InstalledSkill` dataclass
- [x] Implement `scan_installed_skills(agent, project_level)`
- [x] Scan for `.skilz-manifest.yaml` files
- [x] Parse manifests into InstalledSkill objects
- [x] Add unit tests in `tests/test_scanner.py`

**Definition of Done**: Can scan a skills directory and return list of installed skills ✓

### T2: List Command Implementation
- [x] Create `src/skilz/commands/__init__.py`
- [x] Create `src/skilz/commands/list_cmd.py`
- [x] Implement `cmd_list(args)` function
- [x] Add status detection (compare to registry)
- [x] Format table output
- [x] Add `--json` output option
- [x] Add unit tests

**Definition of Done**: `skilz list` shows installed skills with status ✓

### T3: Wire List to CLI
- [x] Add `list` subparser to `cli.py`
- [x] Add `--agent`, `--project`, `--json` flags
- [x] Dispatch to `cmd_list`
- [x] Test end-to-end

**Definition of Done**: `skilz list --project` works correctly ✓

---

## Phase 2b: Update Command

### T4: Update Command Implementation
- [x] Create `src/skilz/commands/update_cmd.py`
- [x] Implement `cmd_update(args)` function
- [x] Scan installed skills
- [x] Compare SHAs to registry
- [x] Call `install_skill` for outdated
- [x] Implement `--dry-run` option
- [x] Add unit tests

**Definition of Done**: `skilz update` updates outdated skills ✓

### T5: Wire Update to CLI
- [x] Add `update` subparser to `cli.py`
- [x] Add `skill_id` optional positional
- [x] Add `--agent`, `--project`, `--dry-run` flags
- [x] Dispatch to `cmd_update`
- [x] Test end-to-end

**Definition of Done**: `skilz update --dry-run` shows what would update ✓

---

## Phase 2c: Remove Command

### T6: Remove Command Implementation
- [x] Create `src/skilz/commands/remove_cmd.py`
- [x] Implement `cmd_remove(args)` function
- [x] Find skill by name/id
- [x] Implement confirmation prompt
- [x] Remove directory with shutil.rmtree
- [x] Add `--yes` flag to skip confirmation
- [x] Add unit tests

**Definition of Done**: `skilz remove skill-id` removes the skill ✓

### T7: Wire Remove to CLI
- [x] Add `remove` subparser to `cli.py`
- [x] Add `skill_id` required positional
- [x] Add `--agent`, `--project`, `--yes` flags
- [x] Dispatch to `cmd_remove`
- [x] Test end-to-end

**Definition of Done**: `skilz remove plantuml --yes` works correctly ✓

---

## Phase 2d: Polish

### T8: Error Handling
- [x] Handle "no skills installed" gracefully
- [x] Handle "skill not found" for remove
- [x] Handle registry not found for status
- [x] Consistent exit codes

**Definition of Done**: All error paths have clear messages ✓

### T9: Documentation
- [x] Update README with new commands
- [x] Add usage examples for list/update/remove
- [x] Document --json output format

**Definition of Done**: README documents all commands ✓

---

## Task Dependencies

```
T1 (scanner) ──► T2 (list cmd) ──► T3 (wire list)
     │
     └──────────► T4 (update cmd) ──► T5 (wire update)
     │
     └──────────► T6 (remove cmd) ──► T7 (wire remove)
                                            │
                                            ▼
                              T8 (errors) ──► T9 (docs)
```

## Estimated Complexity

| Task | Complexity | Lines of Code |
|------|------------|---------------|
| T1   | Medium     | ~80           |
| T2   | Medium     | ~100          |
| T3   | Low        | ~30           |
| T4   | Medium     | ~80           |
| T5   | Low        | ~30           |
| T6   | Low        | ~60           |
| T7   | Low        | ~30           |
| T8   | Low        | ~40           |
| T9   | Low        | Docs only     |

**Total**: ~450 lines of code
