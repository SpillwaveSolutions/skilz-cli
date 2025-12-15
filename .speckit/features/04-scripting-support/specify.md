# Phase 4: Scripting Support

## Overview

Add global `-y, --yes-all` flag to enable non-interactive mode for bash scripting and automated installations.

## Goals

1. **Non-Interactive Mode** - Skip all confirmation prompts when `-y` or `--yes-all` is passed
2. **Scripting-Friendly** - Enable reliable use in bash scripts, CI/CD pipelines, and automation
3. **Backwards Compatible** - Existing command-specific `--yes` flags continue to work

## User Stories

### US-1: Batch Install Scripts
**As a** DevOps engineer
**I want to** run `skilz -y install skill1 && skilz -y install skill2`
**So that** I can automate skill installation in CI/CD pipelines

**Acceptance Criteria:**
- Global `-y` flag skips all prompts
- Works with install, update, and remove commands
- Exit codes are reliable for scripting (0=success, 1=error)

### US-2: Automated Updates
**As a** developer
**I want to** run `skilz -y update` in a cron job
**So that** my skills stay updated automatically

**Acceptance Criteria:**
- No interactive prompts during update
- Works without TTY attached
- Logs to stdout for capture

### US-3: Cleanup Scripts
**As a** developer
**I want to** run `skilz -y remove skill-id` in scripts
**So that** I can automate skill cleanup without confirmation prompts

**Acceptance Criteria:**
- Removes skill without confirmation
- Same behavior as existing `skilz remove skill-id --yes`

## Functional Requirements

### FR-1: Global Yes Flag
```
skilz [-y|--yes-all] <command> [options]
```

**Behavior:**
- When `-y` or `--yes-all` is passed at the global level:
  - All confirmation prompts are automatically answered "yes"
  - No interactive input is required
  - Commands proceed immediately

### FR-2: Flag Precedence
```
skilz -y remove skill-id        # Global flag - skips prompt
skilz remove skill-id --yes     # Command flag - skips prompt (existing)
skilz remove skill-id           # No flag - prompts user
```

Both the global `-y` and command-specific `--yes` flags should work identically.

### FR-3: Command Compatibility

| Command | Prompts Affected |
|---------|------------------|
| `install` | None currently (future: overwrite confirmation) |
| `list` | None (read-only) |
| `update` | None currently (future: batch update confirmation) |
| `remove` | Confirmation prompt (existing --yes flag) |

## Technical Notes

### Implementation Approach

1. Add `-y, --yes-all` to the global parser (before subcommand)
2. Pass the flag value to all command handlers via `args.yes_all`
3. Update `cmd_remove` to check both `args.yes` and `args.yes_all`
4. Future commands can check `args.yes_all` for skip prompts

### CLI Structure
```python
parser.add_argument(
    "-y", "--yes-all",
    action="store_true",
    help="Enable for bash scripting and installs (skip all prompts)"
)
```

## Success Metrics

Phase 4 is complete when:
1. `skilz -y remove skill-id` removes without prompt
2. Global flag works consistently across all commands
3. Existing `--yes` flags continue to work
4. Tests cover scripting scenarios
5. Documentation updated with scripting examples
