# Phase 1: Core Installer

## Feature Summary

Implement the core `skilz install` command that:
1. Reads a skill ID from the registry
2. Clones the Git repository (or reuses existing)
3. Checks out the pinned commit
4. Copies skill files to the correct agent-specific location
5. Writes a manifest for tracking

## Target Agents

| Agent | Skills Directory |
|-------|------------------|
| Claude Code | `~/.claude/skills/` (user) or `.claude/skills/` (project) |
| OpenCode | `~/.config/opencode/skills/` |

## User Stories

### US-1: Basic Skill Installation
**As a** developer using Claude Code
**I want to** run `skilz install anthropics/web-artifacts-builder`
**So that** the skill is installed and immediately available in my Claude Code sessions

**Acceptance Criteria:**
- Skill ID is resolved from registry file
- Git repository is cloned to cache location
- Specified commit is checked out
- Skill files are copied to `~/.claude/skills/<skill-name>/`
- Manifest file is created in skill directory
- Command exits with code 0 on success

### US-2: Project-Level Registry
**As a** team lead
**I want to** commit a `.skilz/registry.yaml` to my project
**So that** team members can install the same skills with the same versions

**Acceptance Criteria:**
- Project registry (`.skilz/registry.yaml`) is checked first
- User registry (`~/.skilz/registry.yaml`) is used as fallback
- Clear error if skill ID not found in either

### US-3: OpenCode Support
**As a** developer using OpenCode
**I want to** run `skilz install some-skill`
**So that** the skill is installed to my OpenCode skills directory

**Acceptance Criteria:**
- Auto-detects OpenCode environment
- Installs to `~/.config/opencode/skills/`
- Same manifest format as Claude Code installs

### US-4: Manifest Generation
**As a** security-conscious developer
**I want to** see a manifest file in each installed skill
**So that** I can audit exactly what version is installed and where it came from

**Acceptance Criteria:**
- `.skilz-manifest.yaml` created in skill directory
- Contains: installed_at, skill_id, git_repo, skill_path, git_sha, skilz_version
- Timestamps in ISO 8601 format

### US-5: Idempotent Installation
**As a** developer
**I want to** run `skilz install` multiple times
**So that** I can ensure skills are up-to-date without side effects

**Acceptance Criteria:**
- Re-running install for same skill+SHA is a no-op
- If SHA differs from manifest, reinstall with new version
- Clear output indicating "already installed" vs "updated"
- Directory name validation only applies to permanent skill directories, not temp git clone directories

## Functional Requirements

### FR-1: Registry Resolution
- Load registry from `.skilz/registry.yaml` (project) first
- Fall back to `~/.skilz/registry.yaml` (user)
- Parse YAML to extract: git_repo, skill_path, git_sha

### FR-2: Git Operations
- Clone repository to `~/.skilz/cache/<repo-hash>/`
- If cache exists, fetch and checkout specified SHA
- Sparse checkout if only skill_path needed (optimization, can defer)

### FR-3: File Copy
- Copy skill directory from cache to agent skills directory
- Preserve file permissions
- Overwrite existing files if reinstalling

### FR-4: Agent Detection
- Check for `.claude/` directory presence → Claude Code
- Check for `~/.config/opencode/` → OpenCode
- Allow `--agent claude|opencode` override
- Default to Claude Code if ambiguous

### FR-5: Error Handling
- Git clone failure: show repo URL and suggest checking access
- SHA not found: show SHA and suggest checking registry
- Permission denied: show path and suggest permissions fix
- Registry not found: show expected paths
- Directory name validation: only warn for permanent skill directories, not temp git clone directories

## Non-Functional Requirements

### NFR-1: Performance
- Install a new skill in <30 seconds on decent network
- Reinstall (cache hit) in <5 seconds

### NFR-2: Offline Tolerance
- If repo already cached and SHA present, installation works offline
- Clear error message if network needed but unavailable

## Out of Scope for Phase 1

- `skilz list` command
- `skilz update` command
- `skilz remove` command
- `skilz search` command
- Plugin/marketplace installation
- Dependency resolution
- Cursor/Codex/Gemini support

## Registry Schema (Phase 1)

```yaml
# .skilz/registry.yaml
skill-id:
  git_repo: git@github.com:org/repo.git
  skill_path: /main/path/to/skill/SKILL.md
  git_sha: <40-char SHA>
```

## Manifest Schema

```yaml
# .skilz-manifest.yaml (in installed skill directory)
installed_at: 2025-01-15T14:32:00Z
skill_id: anthropics/web-artifacts-builder
git_repo: git@github.com:anthropics/skills.git
skill_path: /main/skills/web-artifacts-builder/SKILL.md
git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d
skilz_version: 0.1.0
```

## Success Metrics

Phase 1 is complete when:
1. `skilz install skill-id` works for Claude Code
2. `skilz install skill-id` works for OpenCode
3. Manifests are generated correctly
4. Tests pass with 80%+ coverage
5. README documents basic usage
