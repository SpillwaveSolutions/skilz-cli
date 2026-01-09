# Feature Specification: Marketplace Submission

**Feature Branch**: `12-marketplace-submission`  
**Created**: 2026-01-08  
**Status**: Future (Not Ready for Implementation)  
**Blocked By**: Marketplace REST API endpoint development

## Feature Summary

Enable users to submit skills to the skillzwave.ai marketplace directly from the CLI when installing from Git URLs (`-g` flag) or GitHub repositories.

## User Scenarios & Testing

### User Story 1 - Submit Skill to Marketplace (Priority: P1)

As a skill developer who has installed a skill using `-g https://github.com/myorg/my-skill.git`, I want to be prompted (or use a flag) to submit this skill to the marketplace, so that other users can discover and install it more easily.

**Why this priority**: Core feature - enables community contribution to marketplace

**Acceptance Scenarios**:

1. **Given** user installs with `-g <url>`, **When** installation succeeds, **Then** user is prompted: "Would you like to submit this skill to the marketplace? [y/N]"

2. **Given** user installs with `-g <url> --submit-to-marketplace`, **When** installation succeeds, **Then** skill is automatically submitted without prompt

3. **Given** skill is submitted, **When** API responds with success, **Then** user sees: "Skill submitted to marketplace for review"

---

### User Story 2 - Submission Validation (Priority: P2)

As a marketplace maintainer, I want submitted skills to be validated before acceptance, so that the marketplace maintains quality standards.

**Acceptance Scenarios**:

1. **Given** skill has valid SKILL.md with required frontmatter, **When** submitted, **Then** submission is accepted for review

2. **Given** skill is missing required fields, **When** submitted, **Then** submission is rejected with clear error message

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide `--submit-to-marketplace` flag on install command
- **FR-002**: System MUST prompt user after successful `-g` install (unless `--no-prompt`)
- **FR-003**: System MUST call marketplace REST API with skill metadata
- **FR-004**: System MUST display submission status/result to user
- **FR-005**: System MUST handle API errors gracefully

### Blocked Requirements (Need Backend Work)

- **BLOCKED-001**: Marketplace REST endpoint `POST /api/skills/submit` [NEEDS BACKEND]
- **BLOCKED-002**: Skill validation endpoint `POST /api/skills/validate` [NEEDS BACKEND]
- **BLOCKED-003**: Authentication for submission (API key or OAuth) [NEEDS BACKEND]

### API Schema (Proposed)

```json
POST /api/skills/submit
{
  "git_repo": "https://github.com/owner/repo.git",
  "skill_path": "/main/skills/my-skill/SKILL.md",
  "git_sha": "abc123...",
  "skill_name": "my-skill",
  "description": "From SKILL.md frontmatter",
  "submitter_email": "optional@email.com"
}

Response:
{
  "status": "pending_review" | "rejected",
  "submission_id": "uuid",
  "message": "Skill submitted for review"
}
```

## Success Criteria

- **SC-001**: Users can submit skills via CLI
- **SC-002**: Submissions appear in marketplace admin queue
- **SC-003**: 90% of valid skills pass automated validation
- **SC-004**: Clear error messages for invalid submissions

## Implementation Notes

This feature is **NOT READY** for implementation until:

1. Marketplace backend team implements `POST /api/skills/submit` endpoint
2. Authentication/authorization strategy is defined
3. Skill validation rules are finalized

**Estimated Backend Work**: 2-3 weeks
**Estimated CLI Work**: 3-5 days (after backend ready)

## Related Features

- Feature 11: Skill Path Fallback Discovery (implements path search that could validate submissions)
- Feature 08: Multi-Skill Repository Support (provides skill discovery logic)
