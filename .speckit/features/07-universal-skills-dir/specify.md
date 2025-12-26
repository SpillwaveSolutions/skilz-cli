# Phase 7: Universal Skills Directory

## Feature Summary

Implement `.skilz/skills/` as a universal skills directory with symlink/copy mode support, enabling skills to be installed once and shared across multiple AI agents through symbolic links.

## Background

With Phase 6 complete (14 agents supported), users need a way to:
1. Install skills once and share them across agents
2. Choose between copy and symlink installation modes
3. Install skills directly from filesystem paths or git URLs
4. Manage symlinked skills properly (listing, updating, removing)

The universal directory (`.skilz/skills/` or `~/.skilz/skills/`) serves as the canonical source, with agent-specific directories optionally symlinking to it.

## User Stories

### US-1: Symlink Installation Mode
**As a** developer using multiple AI assistants
**I want to** install a skill once and symlink it to agent directories
**So that** I don't have duplicate copies and updates are automatic

**Acceptance Criteria:**
- `skilz install pdf --symlink` creates symlink instead of copy
- `skilz install pdf --agent gemini --project` uses symlink by default (gemini has no native support)
- `skilz install pdf --agent claude` uses copy by default (claude has native support)
- Symlinks point to canonical location in `.skilz/skills/` or `~/.skilz/skills/`

### US-2: Copy Installation Mode
**As a** developer who needs file copies
**I want to** explicitly request copy mode
**So that** I have full control over when symlinks are used

**Acceptance Criteria:**
- `skilz install pdf --copy` forces copy mode regardless of agent default
- `skilz install pdf --symlink` forces symlink mode regardless of agent default
- Mode overrides agent's `default_mode` setting

### US-3: Universal Agent
**As a** developer
**I want to** install skills to the universal directory directly
**So that** they're available for symlinking to any agent

**Acceptance Criteria:**
- `skilz install pdf --agent universal` installs to `~/.skilz/skills/`
- `skilz install pdf --agent universal --project` installs to `.skilz/skills/`
- `skilz install pdf --global` is shorthand for `--agent universal`

### US-4: Filesystem Installation
**As a** developer with local skill directories
**I want to** install skills from my filesystem
**So that** I can use skills I've developed locally

**Acceptance Criteria:**
- `skilz install -f /path/to/skill` installs from local path
- `skilz install -f ~/my-skills/pdf` works with ~ expansion
- Validates SKILL.md exists in source directory
- Supports both copy and symlink modes

### US-5: Git URL Installation
**As a** developer
**I want to** install skills directly from git repositories
**So that** I don't need the central registry for all skills

**Acceptance Criteria:**
- `skilz install -g https://github.com/user/skill-repo` clones and installs
- `skilz install -g git@github.com:user/skill.git` works with SSH URLs
- Clones to temp directory, copies/symlinks skill, cleans up
- Validates SKILL.md exists after clone

### US-6: List Shows Symlink Status
**As a** user
**I want to** see which skills are symlinked vs copied
**So that** I understand my installation state

**Acceptance Criteria:**
- `skilz list` shows install mode (copy/symlink) for each skill
- `skilz list` shows symlink target for symlinked skills
- Broken symlinks are flagged as errors

### US-7: Remove Handles Symlinks
**As a** user removing skills
**I want to** properly remove symlinked skills
**So that** cleanup is complete and correct

**Acceptance Criteria:**
- `skilz remove pdf` removes symlink without affecting target
- `skilz remove pdf --agent universal` removes canonical copy
- Warning if removing canonical source that has symlinks pointing to it

### US-8: Update Handles Symlinks
**As a** user updating skills
**I want to** update canonical sources, not symlinks
**So that** all symlinked instances are updated automatically

**Acceptance Criteria:**
- `skilz update pdf` updates canonical source if symlinked
- Symlinks automatically reflect updated content
- `skilz update --all` updates all canonical sources

## Functional Requirements

### FR-1: Link Operations Module
Create `src/skilz/link_ops.py` with:
- `create_symlink(source: Path, target: Path) -> bool`
- `is_symlink(path: Path) -> bool`
- `get_symlink_target(path: Path) -> Path | None`
- `is_broken_symlink(path: Path) -> bool`
- `copy_directory(source: Path, target: Path) -> bool`
- `validate_skill_source(path: Path) -> bool` (checks SKILL.md exists)

### FR-2: Install Mode Detection
Installation mode determination order:
1. Explicit `--copy` or `--symlink` flag (highest priority)
2. Agent's `default_mode` from registry
3. Fall back to "copy" for safety

### FR-3: Canonical Path Resolution
For symlink installations:
1. If `--global` or `--agent universal`: use `~/.skilz/skills/`
2. If `--project` with `--agent universal`: use `.skilz/skills/`
3. For other agents with symlink mode: ensure canonical exists in universal dir first

### FR-4: Manifest Extensions
Add to manifest:
- `install_mode: Literal["copy", "symlink"]`
- `canonical_path: str | None` (target of symlink, null if copy)

### FR-5: Filesystem Source Validation
When installing from `-f`:
1. Path must exist and be a directory
2. Must contain SKILL.md
3. Skill name derived from directory name
4. SKILL.md frontmatter parsed for metadata

### FR-6: Git Clone Installation
When installing from `-g`:
1. Clone to temporary directory
2. Validate SKILL.md exists
3. Install skill using normal flow
4. Clean up temporary directory

## Non-Functional Requirements

### NFR-1: Platform Compatibility
Symlinks must work on:
- macOS (native support)
- Linux (native support)
- Windows (requires developer mode or admin)

### NFR-2: Broken Symlink Handling
Gracefully detect and report broken symlinks without crashing.

### NFR-3: Atomic Operations
File operations should be atomic where possible to prevent partial states.

### NFR-4: Test Coverage
Link operations code must have 90%+ test coverage.

## Out of Scope

- SKILL.md frontmatter parsing (Phase 8)
- Config file sync for non-native agents (Phase 10)
- Skill validation command (Phase 11)

## Dependencies

- Phase 6 Agent Registry (complete)
- Existing installer.py module
- Existing scanner.py module

## Success Metrics

Phase 7 is successful when:
1. `skilz install pdf --symlink` creates working symlinks
2. `skilz install pdf --copy` creates file copies
3. `skilz install -f /path` works for local skills
4. `skilz list` shows symlink status
5. `skilz remove` handles symlinks correctly
6. 90%+ test coverage on link_ops.py
