# Phase 2: Implementation Plan

## Architecture

### New Modules

```
src/skilz/
├── cli.py              # Add list, update, remove subcommands
├── commands/
│   ├── __init__.py
│   ├── list_cmd.py     # List command implementation
│   ├── update_cmd.py   # Update command implementation
│   └── remove_cmd.py   # Remove command implementation
└── scanner.py          # Scan for installed skills
```

### Component Design

```
┌─────────────┐
│   cli.py    │  Dispatch to command modules
└─────┬───────┘
      │
      ├──────────►┌──────────────┐
      │           │ list_cmd.py  │──► scanner.py ──► manifest.py
      │           └──────────────┘
      │
      ├──────────►┌──────────────┐
      │           │ update_cmd.py│──► scanner.py ──► installer.py
      │           └──────────────┘
      │
      └──────────►┌──────────────┐
                  │ remove_cmd.py│──► scanner.py ──► shutil.rmtree
                  └──────────────┘
```

## Key Design Decisions

### D1: Scanner Module
**Decision**: Create dedicated scanner to find installed skills

```python
def scan_installed_skills(
    agent: AgentType | None = None,
    project_level: bool = False,
) -> list[InstalledSkill]:
    """Scan skills directories for installed skills with manifests."""
```

**Rationale**: Reusable across list, update, remove commands

### D2: InstalledSkill Dataclass
**Decision**: New dataclass to represent an installed skill

```python
@dataclass
class InstalledSkill:
    skill_id: str
    skill_name: str
    path: Path
    manifest: SkillManifest
    agent: AgentType
    project_level: bool

    @property
    def status(self) -> str:
        """Compare to registry, return 'up-to-date', 'outdated', or 'unknown'."""
```

### D3: Command Module Pattern
**Decision**: Each command in its own module

**Rationale**:
- Cleaner separation of concerns
- Easier to test individual commands
- CLI dispatch remains simple

### D4: Confirmation for Remove
**Decision**: Require confirmation unless `--yes` flag

```python
def confirm_remove(skill: InstalledSkill) -> bool:
    response = input(f"Remove {skill.skill_id}? [y/N] ")
    return response.lower() in ("y", "yes")
```

## Implementation Details

### List Command Flow
1. Get skills directory for agent (user or project level)
2. Scan for directories containing `.skilz-manifest.yaml`
3. Parse each manifest into InstalledSkill
4. Load registry to determine status (if available)
5. Format and output table or JSON

### Update Command Flow
1. Scan installed skills (same as list)
2. Load registry
3. For each skill:
   - Compare manifest.git_sha to registry.git_sha
   - If different, mark for update
4. If --dry-run, just print what would update
5. Otherwise, call install_skill for each outdated skill
6. Report summary

### Remove Command Flow
1. Find skill by name/id in skills directory
2. Confirm with user (unless --yes)
3. Remove directory with shutil.rmtree
4. Print confirmation

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No skills installed | Print "No skills installed" |
| Skill not in registry | Show status as "unknown" in list |
| Remove nonexistent skill | Print error, exit 1 |
| Update fails mid-way | Continue with others, report failures |
| Registry not found | List shows all as "unknown" status |

## CLI Additions

```python
# In cli.py create_parser()

# List command
list_parser = subparsers.add_parser("list", help="List installed skills")
list_parser.add_argument("--agent", choices=["claude", "opencode"])
list_parser.add_argument("--project", action="store_true")
list_parser.add_argument("--json", action="store_true")

# Update command
update_parser = subparsers.add_parser("update", help="Update installed skills")
update_parser.add_argument("skill_id", nargs="?", help="Specific skill to update")
update_parser.add_argument("--agent", choices=["claude", "opencode"])
update_parser.add_argument("--project", action="store_true")
update_parser.add_argument("--dry-run", action="store_true")

# Remove command
remove_parser = subparsers.add_parser("remove", help="Remove an installed skill")
remove_parser.add_argument("skill_id", help="Skill to remove")
remove_parser.add_argument("--agent", choices=["claude", "opencode"])
remove_parser.add_argument("--project", action="store_true")
remove_parser.add_argument("--yes", "-y", action="store_true")
```

## Testing Strategy

### Unit Tests
- `test_scanner.py`: Scan logic with mock directories
- `test_list_cmd.py`: Output formatting
- `test_update_cmd.py`: Update logic, dry-run
- `test_remove_cmd.py`: Remove logic, confirmation

### Integration Tests
- Install skill → list → verify in output
- Install skill → update (no-op) → verify message
- Install skill → remove → verify deleted
