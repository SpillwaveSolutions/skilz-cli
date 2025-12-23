# Architectural Decision Records (ADRs)

This document captures architectural decisions for the Skilz CLI project.

---

## ADR-001: Registry-Based Skill Resolution

**Date:** 2025-12-22
**Status:** Accepted
**Context:** Skills can come from many sources - GitHub, GitLab, local directories. We needed a unified way to resolve skill identifiers to their actual locations.

**Decision:** Use YAML registry files (`.skilz/registry.yaml`) that map skill IDs to Git repositories with pinned SHAs.

**Rationale:**
- Reproducible builds - exact commits are pinned
- Auditable - manifest files track what's installed
- Flexible - works with any Git repository

**Consequences:**
- Users must maintain registry files
- Updates require registry updates, not just Git pulls

---

## ADR-002: Multi-Agent Support (Claude Code + OpenCode)

**Date:** 2025-12-22
**Status:** Accepted
**Context:** Users may use different AI coding assistants. Skills should be installable for any supported agent.

**Decision:** Implement pluggable agent backends with auto-detection.

**Rationale:**
- `--agent` flag for explicit selection
- Auto-detection based on available config directories
- Unified CLI experience across agents

**Consequences:**
- Each agent has different skill directory conventions
- Need to maintain compatibility with each agent's expectations

---

## ADR-003: Manifest Files for Tracking

**Date:** 2025-12-22
**Status:** Accepted
**Context:** Need to know what skills are installed, their versions, and sources.

**Decision:** Write `.skilz-manifest.yaml` into each installed skill directory.

**Rationale:**
- Self-documenting installations
- Enables `skilz list` and `skilz update` commands
- Audit trail for security/compliance

**Consequences:**
- Adds a file to each skill directory
- Must handle manifest-less skills gracefully

---

## ADR-004: Poetry + Taskfile for Development

**Date:** 2025-12-22
**Status:** Accepted
**Context:** Need consistent development experience across team members.

**Decision:** Use Poetry for dependency management, Taskfile for automation.

**Rationale:**
- Poetry handles Python dependencies and virtual environments
- Taskfile provides cross-platform task runner (Go-based, fast)
- Both are well-documented and widely adopted

**Consequences:**
- Requires both tools installed for full development experience
- Manual commands documented as fallback

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded
**Context:** [What is the issue we're addressing?]

**Decision:** [What did we decide?]

**Rationale:** [Why did we make this decision?]

**Consequences:** [What are the implications?]
```
