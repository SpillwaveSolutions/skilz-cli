# Phase 5: Configuration System & Scripting Support

## Feature Summary

Add a configuration system with `skilz config` command, global `-y, --yes-all` flag for scripting, customizable agent paths, and shell completion.

## User Stories

### US-1: Global Yes Flag for Scripting
**As a** DevOps engineer
**I want to** use `-y` or `--yes-all` to skip all confirmation prompts
**So that** I can use skilz in non-interactive scripts and CI/CD pipelines

**Acceptance Criteria:**
- Global `-y, --yes-all` flag available before any command
- Skips confirmation prompts in `remove` command
- Skips interactive prompts in `config --init`
- Works with all commands that might prompt

### US-2: Configuration File
**As a** developer
**I want to** set default values in a config file
**So that** I don't need to repeat `--agent opencode` on every command

**Acceptance Criteria:**
- Config file at `~/.config/skilz/settings.json`
- Settings: `claude_code_home`, `open_code_home`, `agent_default`
- Uses snake_case for JSON keys
- Only saves non-default values

### US-3: Environment Variable Overrides
**As a** developer
**I want to** override config with environment variables
**So that** I can customize behavior per-session or in CI/CD

**Acceptance Criteria:**
- `CLAUDE_CODE_HOME` overrides `claude_code_home`
- `OPEN_CODE_HOME` overrides `open_code_home`
- `AGENT_DEFAULT` overrides `agent_default`
- Invalid `AGENT_DEFAULT` values are ignored

### US-4: Config Command
**As a** developer
**I want to** run `skilz config` to see my configuration
**So that** I can understand what settings are in effect

**Acceptance Criteria:**
- Shows config file path
- Shows each setting with source (default, file, env, effective)
- Indicates when config file doesn't exist
- Suggests running `--init`

### US-5: Config Init Wizard
**As a** new user
**I want to** run `skilz config --init` for interactive setup
**So that** I can easily configure skilz without editing files

**Acceptance Criteria:**
- Prompts for Claude Code home (with default)
- Prompts for OpenCode home (with default)
- Prompts for default agent (claude/opencode/auto)
- Offers shell completion installation
- Creates config file with non-default values only

### US-6: Shell Completion
**As a** developer
**I want to** have tab completion for skilz commands
**So that** I can work more efficiently

**Acceptance Criteria:**
- Supports zsh completion
- Supports bash completion
- Installable via `config --init` wizard
- Completes commands, options, and agent choices

### US-7: Help Visibility
**As a** new user
**I want to** see `--agent` in the main help output
**So that** I understand agent selection is available

**Acceptance Criteria:**
- Epilog shows `--agent` examples
- Common options section explains available flags

## Functional Requirements

### FR-1: Configuration Priority
Configuration is resolved in this order (lowest to highest):
1. Default values (hardcoded)
2. Config file (`~/.config/skilz/settings.json`)
3. Environment variables
4. Command line arguments

### FR-2: Valid Agent Values
Only `claude` and `opencode` are valid for `agent_default`. Invalid values are ignored.

### FR-3: Backwards Compatibility
System must work correctly without config file (uses defaults).

## Non-Functional Requirements

### NFR-1: Performance
Config loading should add negligible overhead (<1ms).

### NFR-2: Security
Config file permissions should be standard user-only readable.

## Out of Scope

- GUI configuration
- Remote/cloud config sync
- Config file encryption
