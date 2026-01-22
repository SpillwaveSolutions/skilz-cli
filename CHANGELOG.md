# Changelog

All notable changes to Skilz CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.4] - 2026-01-21

### Added

- GitHub shorthand URL support for `-g/--git` flag
  - `skilz install -g owner/repo` now automatically converts to `https://github.com/owner/repo`
  - Enables easier installation from search results
  - Example: `skilz install -g tfriedel/claude-office-skills` works without full URL

## [1.9.3] - 2026-01-21

### Fixed

- Fix `skilz search` to return useful results
  - Changed query from `{query} skill OR skills` to `{query} claude`
  - Results sorted by stars (descending)
  - `skilz search docx` now returns 41 results
  - `skilz search excel` now returns 94 results

## [1.9.2] - 2026-01-21

### Fixed

- Fix OpenCode user-level skills directory path
  - Was incorrectly using `~/.config/opencode/skills` (plural)
  - Now correctly uses `~/.config/opencode/skill` (singular)
  - `skilz list --agent opencode` now finds installed skills

## [1.9.1] - 2026-01-21

### Fixed

- Fix usage notes only shown for agents without native skill support
  - Usage notes ("Only use skills listed..." ) no longer appear for Claude, OpenCode, Codex, Gemini
  - `--force-config` adds extended instructions but not usage notes for native agents
- Fix typo in agent registry: `.skills/skills` → `.skilz/skills`
  - Affected agents: aider, cursor, windsurf, qwen, crush, kimi, plandex, zed
  - Skills now correctly install to `.skilz/skills/` for non-native agents

## [1.9.0] - 2026-01-21

### Changed

- Documentation updates to match current feature set
  - Updated USER_MANUAL.md from v1.6.0 to v1.9.0
  - Fixed DEPLOY_PYPI.md version management documentation
  - Updated key_facts.md with version management notes

### Documentation

- Added version management section to key_facts.md
- Corrected DEPLOY_PYPI.md to reflect dynamic versioning
- USER_MANUAL.md now documents 1.7 and 1.8 features:
  - Gemini native support
  - NEW/LEGACY/SLUG format support
  - Universal agent custom config
  - List command with Agent column
  - `--all` flag for list command

## [1.8.0] - 2026-01-09

### Added

- **List Command Enhancements (SKILZ-68)**: Major improvements to `skilz list` command
  - Added "Agent" column showing user-friendly agent names (Claude Code, OpenAI Codex, etc.)
  - Added `--all` flag to scan all 14+ supported agents (default: top 5)
  - Fixed status logic to use correct `manifest.skill_id` for accurate up-to-date/outdated reporting
  - Improved home directory discovery with proper agent filtering
  - Enhanced JSON output with `agent_display_name` field

- **CLI Help Discoverability (SKILZ-66)**: Comprehensive improvements to `--help` output
  - Added examples for all commands (update, remove, read, config, etc.)
  - Improved command descriptions for better clarity
  - Complete coverage of available options and usage patterns
  - Enhanced user experience with comprehensive examples

### Fixed

- **Visit Command URL Format (SKILZ-70)**: Corrected marketplace URL generation
  - Fixed base URL: `skillzwave.ai/skill` → `skillzwave.ai/agent-skill`
  - Fixed slug format: removed `__SKILL` suffix, proper `owner__repo__skill` format
  - Added support for single skill names with spillwavesolutions organization
  - Example: `skilz visit sdd` now correctly opens `skillzwave.ai/agent-skill/spillwavesolutions__sdd__sdd`

### Changed

- **Agent Registry Integration**: Scanner now uses registry for agent discovery instead of hardcoded lists
- **Type Safety**: Updated AgentType to ExtendedAgentType for full agent support

## [1.7.0] - 2026-01-08

### Added

- **Gemini CLI Native Skill Support (SKILZ-49)**: Gemini now reads skills natively from `.gemini/skills/`
  - Project-level: Skills installed to `.gemini/skills/` (native location)
  - User-level: Skills installed to `~/.gemini/skills/` (native location)
  - No config file injection needed when using native directories
  - Requires Gemini CLI with `experimental.skills` plugin enabled
  - Auto-detects Gemini from `.gemini/` directory (project and user level)

- **Universal Agent Project-Level Support (SKILZ-50)**: Universal agent now supports project installations
  - Install to project: `skilz install <skill> --agent universal --project`
  - Default behavior: Updates `AGENTS.md` config file
  - Custom config support: `--config <filename>` flag to target specific config files
  - Legacy Gemini workflow: `skilz install <skill> --agent universal --project --config GEMINI.md`
  - Universal agent config updated: `config_files=("AGENTS.md",)` (was empty tuple)

- **NEW Install Format Support (SKILZ-FORMAT-001)**: Revolutionary new skill ID format with REST-first resolution
  - **NEW Format**: `skilz install owner/repo/skill` (intuitive GitHub-style format)
  - **LEGACY Format**: `skilz install owner_repo/skill` (backwards compatible)
  - **SLUG Format**: `skilz install owner__repo__skill` (direct Firestore doc ID)
  - **REST-First Resolution**: All formats try REST API before GitHub fallback
  - **Enhanced Logging**: Verbose mode shows format detection and resolution method
  - **Format Detection**: Automatic detection with `get_skill_id_format()` function
  - **100% Backwards Compatible**: All existing skill IDs continue to work unchanged

- **Custom Config File Targeting**: New `--config` flag for install command
  - Syntax: `skilz install <skill> --project --config <filename>`
  - Requires `--project` flag (only works with project-level installs)
  - Supports any filename: `GEMINI.md`, `CUSTOM_SKILLS.md`, etc.
  - Only updates specified file (overrides auto-detection)
  - Use case: Legacy Gemini users without `experimental.skills` plugin

- **Comprehensive Integration Tests**: Added 34 new tests across multiple areas
  - **NEW Format Tests**: 25 new API client tests for format detection and parsing
    - `TestParseSkillIdNewFormat`: Tests NEW format parsing (owner/repo/skill)
    - `TestParseSkillIdSlugFormat`: Tests SLUG format parsing (owner__repo__skill)
    - `TestIsMarketplaceSkillIdFormats`: Tests marketplace format recognition
    - `TestGetSkillIdFormat`: Tests automatic format detection
  - **Universal Agent Tests**: 9 integration tests for project-level support
    - Test default AGENTS.md creation
    - Test custom config file targeting
    - Test CLI validation (--config requires --project)
    - Test multiple skills with custom config
    - Test legacy Gemini workflow
    - Test arbitrary custom filenames
    - Test config file isolation (only target updated)
  - **Quality Metrics**: All 633 tests passing (100% success rate)

- **Enhanced E2E Test Suite**: Comprehensive end-to-end testing for 1.7.0
  - **REST Marketplace E2E Testing**: New comprehensive test suite (`scripts/test_rest_marketplace_e2e.sh`)
    - **API Endpoint Validation**: Tests REST API reachability and response format
    - **Format Detection Accuracy**: Validates NEW/LEGACY/SLUG format recognition
    - **Resolution Testing**: Tests successful installation for all supported formats
    - **Error Handling**: Validates 404/400 responses for non-existent skills
    - **Verbose Logging**: Verifies format detection and REST vs GitHub resolution logging
    - **Real-World Testing**: Uses live skillzwave.ai API with actual skills
  - **API Integration Testing**: New integration test suite (`scripts/test_api_integration.sh`)
    - Tests REST API endpoints with real marketplace data
    - Validates JSON response structure and required fields
    - Tests error handling for invalid requests
  - **Existing E2E Tests**: Updated for 1.7.0 features
    - Isolated test environment in `e2e/test_folder/` with mock Python project
    - New `test_gemini_native()` test for native `.gemini/skills/` support
    - New `test_universal_custom_config()` test for custom config workflows
    - Tests verify no GEMINI.md created for native agents
    - Tests verify custom config files work with arbitrary names

### Changed

- **API Client Architecture**: Major enhancements to `src/skilz/api_client.py`
  - **Replaced `parse_skill_id()`**: Now supports 3 formats (NEW/LEGACY/SLUG)
  - **Enhanced `is_marketplace_skill_id()`**: Recognizes all marketplace formats
  - **Added `get_skill_id_format()`**: Returns format type for any skill ID
  - **Improved Error Messages**: More descriptive error messages for invalid formats
  - **REST-First Resolution**: All marketplace formats try REST API before GitHub

- **Installer Logging**: Enhanced verbose output in `src/skilz/installer.py`
  - **Format Detection Logging**: Shows detected format type (NEW/LEGACY/SLUG/UNKNOWN)
  - **REST API Logging**: Shows when REST API lookup is attempted
  - **Success Logging**: Shows when REST API successfully resolves a skill
  - **Resolution Method**: Clear indication of REST vs GitHub resolution

- **Gemini Agent Config**: Updated to support native skill directories
  - `home_dir`: Changed from `None` to `Path.home() / ".gemini" / "skills"`
  - `project_dir`: Changed from `.skilz/skills` to `.gemini/skills`
  - `supports_home`: Changed from `False` to `True`
  - `native_skill_support`: Changed from "none" to "all"

- **Universal Agent Config**: Updated to enable project-level installations
  - `config_files`: Changed from empty tuple `()` to `("AGENTS.md",)`
  - Now supports both user-level (`~/.skilz/skills/`) and project-level (`.skilz/skills/`)

- **Config Sync Enhancement**: `sync_skill_to_configs()` now supports `target_files` parameter
  - When `target_files` specified, only those files are updated
  - Overrides auto-detection for explicit control
  - Enables custom config workflows for any agent

- **Agent Auto-Detection**: Enhanced detection to include Gemini
  - Priority order: config default → `.claude/` → `.gemini/` → `.codex/` → `~/.claude/` → `~/.gemini/` → `~/.codex/` → `~/.config/opencode/` → default (Claude)

### Enhanced

- **Skill Path Fallback Discovery (Feature 11)**: When installing a skill whose expected path doesn't exist in the repository, skilz now always displays a warning message when the skill is found at a different location. Previously this information was only shown in verbose mode. This helps users understand when marketplace/registry data may be stale due to repository reorganizations.
  - Warning format: `Warning: Skill 'skill-name' found at different path than expected`
  - Warning goes to stderr (not stdout) for proper script integration
  - Verbose mode shows expected and found paths for debugging
  - Installation continues successfully from the discovered location

### Fixed

- **Codex Agent Auto-Detection (BUG-001)**: Codex agent now properly detected from directories
  - Fixed detection from project-level `.codex/` directory
  - Fixed detection from user-level `~/.codex/` directory
  - Added to auto-detection priority list (was missing despite being in registry)
  - Added 3 tests to verify Codex detection works correctly

### Migration Notes

**For Gemini CLI Users:**
- **With experimental.skills plugin**: Use native support with `--agent gemini --project`
  - Skills install to `.gemini/skills/` (native location)
  - No config file needed - Gemini reads directory natively
- **Without experimental.skills plugin**: Use legacy workflow with universal agent
  - `skilz install <skill> --agent universal --project --config GEMINI.md`
  - Skills install to `.skilz/skills/`
  - GEMINI.md file created for Gemini CLI to read

**For Universal Agent Users:**
- Project-level installations now supported with automatic AGENTS.md creation
- Use `--config <filename>` to target specific config files
- Backward compatible: User-level installs work as before

See [GEMINI_MIGRATION.md](docs/GEMINI_MIGRATION.md) and [UNIVERSAL_AGENT_GUIDE.md](docs/UNIVERSAL_AGENT_GUIDE.md) for detailed guides.

## [1.6.0] - 2026-01-03

### Added

- **GitHub Copilot Native Skill Support (SKILZ-54)**: Copilot now reads skills natively from `.github/skills/`
  - Skills installed for Copilot go directly to `.github/skills/` (project-level only)
  - No config file injection needed - Copilot reads the directory natively
  - Auto-detects project-level installation with clear info message:
    `Info: GitHub Copilot only supports project-level installation (.github/skills/)`

- **OpenCode Full Native Support**: OpenCode now has full native skill support (was "home only")
  - Corrected paths to use singular `skill` format matching OpenCode's configuration
  - Home directory: `~/.config/opencode/skill/`
  - Project directory: `.opencode/skill/`
  - `native_skill_support` changed from "home" to "all"

- **Enhanced E2E Tests**: Added comprehensive GitHub Copilot tests
  - Tests auto project-level detection
  - Verifies `.github/skills/` installation path
  - Validates info message display

### Changed

- **Copilot Project Directory**: Changed from `.github/copilot/skills` to `.github/skills/` (native location)
- **OpenCode Paths**: Corrected to use singular `skill` instead of `skills` to match OpenCode's actual configuration

### Fixed

- OpenCode skill installation now uses correct paths (`~/.config/opencode/skill/` and `.opencode/skill/`)
- Agents without home support (Copilot, Gemini, etc.) now always show informative message when auto-switching to project-level

## [1.5.0] - 2026-01-02

### Added

- **`skilz search` Command**: Search GitHub for available skills
  - Searches repositories by name/description for skill-related projects
  - `--limit` / `-l` option to control number of results (default: 10)
  - `--json` option for machine-readable output
  - Uses `gh` CLI for GitHub API access

- **`skilz visit` Command**: Open skill pages in browser
  - **Default**: Opens Skilzwave marketplace page (`https://skillzwave.ai/skill/...`)
  - **`-g` / `--git`**: Force GitHub URL instead of marketplace
  - **`--dry-run`**: Output URL without opening browser (for scripting)
  - Automatic fallback: If marketplace returns 404, falls back to GitHub
  - Supports `owner/repo`, `owner/repo/skill`, and full URL formats

- **Command Aliases**: Unix-style command shortcuts
  - `skilz ls` - alias for `skilz list`
  - `skilz rm` - alias for `skilz remove`
  - `skilz uninstall` - alias for `skilz remove`

- **`-p` Short Flag**: Added `-p` as short alias for `--project` on all commands
  - Works with: `install`, `list`, `update`, `remove`, `read`, `ls`, `rm`, `uninstall`
  - Example: `skilz ls -p` instead of `skilz list --project`

- **URL Auto-Detection**: No more `-g` flag needed for Git URLs
  - `skilz install https://github.com/owner/repo` now works directly
  - Detects HTTPS, HTTP, SSH URLs, and `.git` suffix
  - Example: `skilz install https://github.com/Jamie-BitFlight/claude_skills.git --skill brainstorming-skill`

- **`--force-config` Flag**: Override native agent detection
  - Skip config sync by default for Claude, OpenCode, Codex (native support)
  - Use `--force-config` to force config file writing when needed

- **End-to-End Test Suite**: Comprehensive 66+ test script (`scripts/end_to_end.sh`)
  - Tests all major features across multiple agents
  - Includes summary table with full command details

### Changed

- **Native Agent Optimization**: Agents with native skill support skip config file modification
  - Claude Code, OpenCode, Codex: skip config sync (read skills directory natively)
  - Gemini: always sync config (no native skill support)
- Improved help text with better examples showing new 1.5 features
- Visit command defaults to marketplace URL (use `-g` for GitHub)

### Fixed

- URL auto-detection for `skilz install` (SKILZ-48)
- Config sync behavior for native agents (SKILZ-49)
- E2E test visit command using correct path for anthropics/skills repo

## [1.1.0] - 2025-12-25

### Added

- **`--version` Flag for Install**: Specify which version of a skill to install
  - `--version latest`: Install latest from default branch
  - `--version branch:NAME`: Install from specific branch
  - `--version v1.0.0`: Install specific git tag
  - `--version <SHA>`: Install specific commit
- **Resilient GitHub API Fallback**: Installation now works even when GitHub API is unavailable
  - Falls back to HEAD when SHA lookup fails
  - Tries multiple branch names (origin/HEAD, origin/main, origin/master)
  - Prints warnings but doesn't fail
- **Skill Search Fallback**: Searches repository for skills when path in registry is outdated

### Fixed

- **HTTP 422 Errors**: No longer fails when GitHub API returns validation errors
- **Branch Not Found**: Automatically tries alternative branches when specified branch doesn't exist

### Changed

- Updated documentation examples to use correct marketplace skill ID format (`owner_repo/skill-name`)

## [1.0.2] - 2025-01-15

### Added

- **14 AI Agent Support**: Full support for Claude Code, OpenAI Codex, OpenCode CLI, Gemini CLI, GitHub Copilot, Cursor, Aider, Windsurf, Qwen CLI, Kimi CLI, Crush, Plandex, Zed AI, and Universal
- **Universal Skills Directory**: Central skill storage at `~/.skilz/skills/` for sharing across agents
- **Copy vs Symlink Modes**: Choose between copying skills (works everywhere) or symlinking (saves disk space)
- **Config File Sync**: Automatic injection of skill references into agent config files (GEMINI.md, CLAUDE.md, etc.) following [agentskills.io](https://agentskills.io) standard
- **`skilz read` Command**: Load skill content for agents without native skill support
- **User-Level Installation**: Install skills once, use everywhere (for supported agents)
- **Project-Level Installation**: Install skills per-project for workspace-sandboxed agents
- **Comprehensive User Guide**: Detailed documentation for all 14 agents and workflows

### Changed

- **Default Mode for Sandboxed Agents**: Agents without native skill support (Gemini, Copilot, etc.) now default to `--copy` mode instead of `--symlink` to ensure compatibility with workspace sandboxing
- **Config File Detection**: Only updates existing config files; creates primary config file only when needed

### Fixed

- **Symlink Resolution**: Correctly resolve symlinks when reading skills
- **Config File Creation**: Prevent creating secondary config files (e.g., CONTEXT.md for Qwen) when only primary is needed

## [1.0.1] - 2025-01-10

### Added

- `skilz list` command with status checking (up-to-date, outdated, newer)
- `skilz update` command with dry-run support
- `skilz remove` command with confirmation prompts
- JSON output format for scripting
- Project-level installation with `--project` flag

### Changed

- Improved error messages with actionable suggestions
- Better manifest file handling

## [1.0.0] - 2025-01-05

### Added

- Initial release
- `skilz install` command for installing skills from Git repositories
- Registry-based skill resolution
- Claude Code support (`~/.claude/skills/`)
- OpenCode support (`~/.config/opencode/skills/`)
- Manifest file generation for tracking installed skills
- Version pinning via Git SHA
