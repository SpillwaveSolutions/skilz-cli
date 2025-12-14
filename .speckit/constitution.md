# Skilz-CLI Constitution

## Vision

**Skilz is the universal package manager for AI skills** - bringing npm/pip-style installation to AI coding assistants.

## Core Principles

### 1. Cross-Agent Universality
- Skills install identically across Claude Code, OpenCode, and future agents
- One command works everywhere
- No agent-specific knowledge required by users

### 2. Reproducibility First
- Every install is pinned to a specific Git SHA
- Manifests track exactly what's installed and where it came from
- Deterministic behavior across machines and time

### 3. Progressive Complexity
- Phase 1: Simple direct Git installation works out of the box
- Later phases: Plugin/marketplace, dependencies, search
- Users only encounter complexity when they need it

### 4. Minimal Dependencies
- Python standard library preferred
- External dependencies require strong justification
- Single `pip install skilz` should be sufficient

### 5. Auditable by Default
- Every installed skill has a manifest
- Users can trace any skill back to its source commit
- Security-conscious teams can audit their skill supply chain

## Development Standards

### Code Quality
- Type hints required for all public APIs
- Docstrings for all public functions
- 80%+ test coverage for core functionality

### Testing Strategy
- Unit tests for registry parsing, path resolution, manifest generation
- Integration tests for actual Git clone + file copy operations
- Mock Git operations in unit tests, real Git in integration tests

### CLI Design
- Commands follow `skilz <verb> <arguments>` pattern
- Progress output to stderr, machine-readable output to stdout
- Exit codes: 0=success, 1=user error, 2=system error

### Error Handling
- Clear, actionable error messages
- Suggest fixes when possible
- Never fail silently

## Phase Strategy

**Short phases delivering working value:**
- Each phase should be usable standalone
- No phase depends on "future work" to be useful
- Phase 1 must work end-to-end for Claude Code and OpenCode

## Technology Choices

- **Language**: Python 3.10+
- **Package Management**: pip (standard), uv (optional speedup)
- **Configuration**: YAML for registries, YAML for manifests
- **CLI Framework**: argparse (stdlib) or click (if justified)

## Success Metrics

Phase 1 is successful when:
1. User can run `skilz install some-skill` and it works
2. Claude Code and OpenCode both supported
3. Manifest files are generated
4. Reinstalling same skill is idempotent
