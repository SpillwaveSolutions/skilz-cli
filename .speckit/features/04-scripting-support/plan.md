# Phase 4: Plan

## Architecture Decisions

### 4.1 Global Flag Implementation

**Decision**: Add `-y, --yes-all` as a global flag in the main parser

**Rationale**:
- Consistent with `-v, --verbose` pattern already in use
- Single flag works for all commands
- Easy to extend to new commands in the future

**Location**: `src/skilz/cli.py` in `create_parser()`

```python
parser.add_argument(
    "-y", "--yes-all",
    action="store_true",
    help="Enable for bash scripting and installs (skip all prompts)"
)
```

### 4.2 Flag Propagation

**Decision**: Use `getattr(args, "yes_all", False)` pattern in command handlers

**Rationale**:
- Consistent with existing `verbose` and `project` patterns
- Backwards compatible (default to False if not present)
- Works with both global and command-specific flags

### 4.3 Remove Command Update

**Current behavior** (`remove_cmd.py`):
```python
if not args.yes:
    confirm = input(f"Remove {skill_id}? [y/N] ")
    if confirm.lower() != "y":
        return 0
```

**Updated behavior**:
```python
yes_all = getattr(args, "yes_all", False)
if not args.yes and not yes_all:
    confirm = input(f"Remove {skill_id}? [y/N] ")
    if confirm.lower() != "y":
        return 0
```

## Implementation Phases

### Phase 4a: CLI Changes
1. Add `-y, --yes-all` to global parser
2. Update `cmd_remove` to check both flags
3. Add tests for new flag

### Phase 4b: Documentation
1. Update USER_MANUAL.md with scripting section
2. Update README.md with scripting examples
3. Add examples to --help output

## Files to Modify

| File | Change |
|------|--------|
| `src/skilz/cli.py` | Add `-y, --yes-all` to global parser |
| `src/skilz/commands/remove_cmd.py` | Check `args.yes_all` in addition to `args.yes` |
| `tests/test_cli.py` | Add tests for global `-y` flag parsing |
| `tests/test_remove_cmd.py` | Add tests for `yes_all` behavior |
| `docs/USER_MANUAL.md` | Add Scripting section |
| `README.md` | Add scripting examples |

## Testing Strategy

### Unit Tests
```python
# test_cli.py
def test_parser_has_yes_all_flag():
    parser = create_parser()
    args = parser.parse_args(["-y", "remove", "skill-id"])
    assert args.yes_all is True

def test_yes_all_short_flag():
    parser = create_parser()
    args = parser.parse_args(["-y", "list"])
    assert args.yes_all is True

def test_yes_all_long_flag():
    parser = create_parser()
    args = parser.parse_args(["--yes-all", "list"])
    assert args.yes_all is True

# test_remove_cmd.py
def test_remove_with_global_yes_all_skips_prompt():
    # Mock input to verify it's never called
    args = mock_args(skill_id="test", yes=False, yes_all=True)
    with patch("builtins.input") as mock_input:
        result = cmd_remove(args)
        mock_input.assert_not_called()
```

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing `--yes` behavior | Keep both flags working independently |
| Accidental destructive operations | Require explicit `-y` flag (not default) |
| Confusion between flags | Document both options clearly |

## Future Considerations

- Add confirmation prompts to `update` command (update all without prompt when `-y`)
- Add overwrite confirmation to `install` (when skill exists, require `-y` or prompt)
- Consider `--dry-run` as complement to `-y` for testing scripts
