# Phase 4: Tasks

## Phase 4a: CLI Changes

### T1: Add Global Yes Flag to Parser
- [ ] Open `src/skilz/cli.py`
- [ ] Add `-y, --yes-all` argument to main parser (after `-v, --verbose`)
- [ ] Set `action="store_true"` and appropriate help text
- [ ] Verify `skilz --help` shows the new flag

**Definition of Done**: `skilz -y list` parses without error

### T2: Update Remove Command
- [ ] Open `src/skilz/commands/remove_cmd.py`
- [ ] Add `yes_all = getattr(args, "yes_all", False)`
- [ ] Update confirmation check: `if not args.yes and not yes_all:`
- [ ] Test manually: `skilz -y remove skill-id --project`

**Definition of Done**: `skilz -y remove` skips confirmation prompt

### T3: Add CLI Tests
- [ ] Open `tests/test_cli.py`
- [ ] Add `test_parser_has_yes_all_short_flag()` - tests `-y`
- [ ] Add `test_parser_has_yes_all_long_flag()` - tests `--yes-all`
- [ ] Add `test_yes_all_with_each_command()` - verify flag works with all commands

**Definition of Done**: All new tests pass

### T4: Add Remove Command Tests
- [ ] Open `tests/test_remove_cmd.py`
- [ ] Add `test_remove_with_global_yes_all_skips_prompt()`
- [ ] Add `test_remove_with_both_yes_flags()`
- [ ] Verify input() is never called when yes_all=True

**Definition of Done**: Remove command tests cover yes_all behavior

---

## Phase 4b: Documentation

### T5: Update USER_MANUAL.md
- [ ] Add "Scripting" section after "Examples"
- [ ] Document `-y, --yes-all` flag
- [ ] Add batch installation examples
- [ ] Add CI/CD pipeline examples
- [ ] Add cron job examples

**Definition of Done**: USER_MANUAL has comprehensive scripting section

### T6: Update README.md
- [ ] Add scripting examples to Quick Start or CLI Reference
- [ ] Show `-y` flag usage in examples
- [ ] Mention scripting support in features

**Definition of Done**: README shows scripting capability

### T7: Update CLI Help
- [ ] Review `--help` output for clarity
- [ ] Ensure `-y` flag is prominent in help text
- [ ] Add scripting example to epilog if appropriate

**Definition of Done**: `skilz --help` clearly shows scripting flag

---

## Task Dependencies

```
T1 (global flag) ──► T2 (remove cmd) ──► T3 (cli tests)
                                              │
                                              ▼
                                         T4 (remove tests)
                                              │
                                              ▼
T5 (user manual) ──► T6 (readme) ──► T7 (cli help)
```

## Progress Summary

| Phase | Status | Completion |
|-------|--------|------------|
| 4a: CLI Changes | ⏳ PENDING | 0% |
| 4b: Documentation | ⏳ PENDING | 0% |

**Overall Phase 4**: 0% complete
