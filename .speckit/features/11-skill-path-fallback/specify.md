# Feature Specification: Skill Path Fallback Discovery

**Feature Branch**: `11-skill-path-fallback`  
**Created**: 2026-01-08  
**Status**: Approved  
**Input**: User request for graceful handling of repository reorganizations

## User Scenarios & Testing

### User Story 1 - Path Fallback with Warning (Priority: P1)

As a developer installing a skill from the marketplace, when the skill maintainer has reorganized their repository, I want skilz to still find and install the skill and warn me that the path changed, so that my installation doesn't fail just because the marketplace has stale path data.

**Why this priority**: This is the core functionality - without it, installations fail when paths change.

**Independent Test**: Can be fully tested by installing a skill whose expected path doesn't exist but whose SKILL.md can be found elsewhere in the repo.

**Acceptance Scenarios**:

1. **Given** a skill with marketplace path `/main/old-location/SKILL.md`, **When** the repo has been reorganized and the skill now exists at `/main/new-location/skill-name/SKILL.md`, **Then** skilz finds the skill by searching for SKILL.md files with matching name, installs it successfully, AND displays a warning message to the user (always, not just verbose mode).

2. **Given** a skill path that doesn't exist AND no matching SKILL.md can be found anywhere in the repo, **When** user runs `skilz install`, **Then** skilz raises an InstallError with a clear message explaining the skill may have been removed.

3. **Given** multiple SKILL.md files with the same skill name in different locations, **When** user runs `skilz install`, **Then** skilz uses the first match and logs a verbose warning about multiple matches.

---

### User Story 2 - Warning Message Content (Priority: P1)

As a developer, when a skill is found at a different path than expected, I want to see a clear warning message that explains what happened, so that I understand why the installation took longer or behaved differently.

**Why this priority**: User visibility is essential - users need to know their installation succeeded but from a different location.

**Independent Test**: Can be verified by checking stderr output contains expected warning format.

**Acceptance Scenarios**:

1. **Given** skill found at different path, **When** installation completes, **Then** warning message is printed to stderr (not stdout) with format:
   ```
   Warning: Skill 'skill-name' found at different path than expected
   ```

2. **Given** skill found at expected path (normal case), **When** installation completes, **Then** NO warning message is displayed.

---

### Edge Cases

- What happens when SKILL.md exists but has no `name:` field in frontmatter?
  - Falls back to directory name matching (existing behavior)
- What happens when repository has been completely deleted/emptied?
  - Standard Git clone/fetch error is raised
- What happens when skill name contains special characters?
  - Handled by existing `validate_skill_name` function

## Requirements

### Functional Requirements

- **FR-001**: System MUST search for SKILL.md files when expected path doesn't exist
- **FR-002**: System MUST match skills by directory name OR `name:` field in frontmatter
- **FR-003**: System MUST display warning message to stderr when path differs (ALWAYS, not just verbose)
- **FR-004**: System MUST continue installation using found path when discovered
- **FR-005**: Warning message MUST be minimal but informative

### Key Entities

- **SkillInfo**: Contains expected `skill_path` from registry/API
- **Found Path**: Actual path discovered via `find_skill_by_name()`
- **Warning**: Message displayed when paths differ

## Success Criteria

### Measurable Outcomes

- **SC-001**: All existing tests continue to pass (617 tests)
- **SC-002**: New tests verify warning is displayed when path differs
- **SC-003**: New tests verify warning is NOT displayed when path matches
- **SC-004**: Installation succeeds when skill moved to different location
- **SC-005**: Warning appears on stderr, not stdout
