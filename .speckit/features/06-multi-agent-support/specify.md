# Phase 6: Multi-Agent CLI Support - Agent Registry System

## Feature Summary

Replace hardcoded agent definitions with a configurable JSON-based agent registry, enabling support for 14+ AI coding assistants (Claude, OpenCode, Codex, Gemini, Copilot, Aider, Cursor, Windsurf, Qwen, Crush, Kimi, Plandex, Zed, Universal) following the agentskills.io open standard.

## Background

Currently, skilz-cli has hardcoded support for only Claude Code and OpenCode. The AI coding assistant landscape has expanded rapidly with many tools supporting similar skill/instruction patterns. This phase introduces a config-driven agent registry that allows:

1. Adding new agents without code changes
2. Customizing agent paths per user preference
3. Supporting both native skill support and config-file sync patterns

## User Stories

### US-1: Dynamic Agent Selection
**As a** developer using multiple AI assistants
**I want to** install skills for any supported agent using `--agent <name>`
**So that** I can use the same skills across Claude, Gemini, Cursor, and other tools

**Acceptance Criteria:**
- `skilz install pdf --agent gemini` works for Gemini CLI
- `skilz install pdf --agent cursor` works for Cursor
- `skilz list --agent codex` shows skills for OpenAI Codex
- All 14 agents in registry are valid `--agent` choices
- Auto-detection still works when `--agent` omitted

### US-2: Config-Based Agent Registry
**As a** developer
**I want to** customize agent paths in `~/.config/skilz/config.json`
**So that** I can override default locations or add custom agents

**Acceptance Criteria:**
- Registry loads from `~/.config/skilz/config.json` if exists
- Falls back to built-in defaults if no config file
- Custom agents can be added to the registry
- Existing `claude` and `opencode` agents continue working

### US-3: Native Skill Support Awareness
**As a** developer
**I want to** skilz to understand which agents have native skill support
**So that** it knows when to copy vs symlink and when to sync config files

**Acceptance Criteria:**
- Agents with `native_skill_support: "all"` use copy mode by default
- Agents with `native_skill_support: "none"` use symlink mode by default
- Agents with `native_skill_support: "none"` trigger config file sync
- Mode can be overridden with `--copy` or `--symlink` flags

### US-4: Default Skills Directory
**As a** developer
**I want to** configure a default skills directory for symlink sources
**So that** project-level installs can symlink back to my main skills location

**Acceptance Criteria:**
- `default_skills_dir` field in config specifies canonical location
- Defaults to `~/.claude/skills` if not set
- Used as symlink source for agents without native support

### US-5: Agent Display Names
**As a** user
**I want to** see human-friendly agent names in output
**So that** I understand which agent I'm working with

**Acceptance Criteria:**
- `skilz list` shows "Claude Code" not "claude"
- Error messages use display names
- Help text shows agent options with display names

### US-6: Backward Compatibility
**As an** existing user
**I want to** my existing claude/opencode installations to keep working
**So that** upgrading skilz doesn't break my workflow

**Acceptance Criteria:**
- All existing commands work without changes
- Default behavior unchanged (claude as primary, opencode supported)
- No migration required for existing users

## Functional Requirements

### FR-1: Agent Registry Structure
Each agent in the registry must have:
- `name` (string): Internal identifier (e.g., "claude", "gemini")
- `display_name` (string): Human-readable name (e.g., "Claude Code", "Gemini CLI")
- `home_dir` (string|null): User-level skills path (e.g., "~/.claude/skills")
- `project_dir` (string): Project-level skills path (e.g., ".claude/skills")
- `config_files` (array): Files to sync skill metadata (e.g., ["GEMINI.md"])
- `supports_home` (boolean): Whether agent supports user-level installation
- `default_mode` (string): "copy" or "symlink"
- `native_skill_support` (string): "all", "home", or "none"

Optional fields:
- `uses_folder_rules` (boolean): For folder-based rule systems (Cursor)
- `invocation` (string): How skills are invoked (documentation)

### FR-2: Registry Loading Priority
1. Load from `~/.config/skilz/config.json` if exists
2. Merge with built-in defaults (user config overrides)
3. Validate all required fields present
4. Make registry available throughout application

### FR-3: Built-in Agent Defaults
The following agents are built-in:
- claude, opencode, codex (home + project support)
- gemini, copilot, aider, cursor, windsurf, qwen, crush, kimi, plandex, zed (project only)
- universal (home + project, for cross-agent sharing)

### FR-4: Dynamic CLI Choices
The `--agent` argument must:
- Accept any agent name from the loaded registry
- Show all agents in help text
- Validate against registry at runtime

### FR-5: AgentConfig Dataclass
Create immutable dataclass for type-safe agent configuration:
```python
@dataclass(frozen=True)
class AgentConfig:
    name: str
    display_name: str
    home_dir: Path | None
    project_dir: Path
    config_files: tuple[str, ...]
    supports_home: bool
    default_mode: Literal["copy", "symlink"]
    native_skill_support: Literal["all", "home", "none"]
    uses_folder_rules: bool = False
    invocation: str | None = None
```

## Non-Functional Requirements

### NFR-1: Performance
Registry loading must add <10ms to startup time.

### NFR-2: Extensibility
Adding a new agent should require only JSON config, no code changes.

### NFR-3: Type Safety
All agent configuration must be fully typed with runtime validation.

### NFR-4: Test Coverage
Agent registry code must have 90%+ test coverage.

## Out of Scope

- Universal skills directory implementation (Phase 2)
- SKILL.md frontmatter parsing (Phase 3)
- `skilz read` command (Phase 4)
- `skilz sync` command (Phase 5)
- `skilz validate` command (Phase 6)
- `skilz manage` TUI (Phase 7)

## Dependencies

- Existing config.py module (will be extended)
- Existing agents.py module (will be refactored)
- Existing cli.py module (will be modified)

## Success Metrics

Phase 1 is successful when:
1. All 14 agents selectable via `--agent` flag
2. Registry loads from config file or defaults
3. Backward compatibility with existing claude/opencode usage
4. 90%+ test coverage on new code
5. No performance regression in CLI startup
