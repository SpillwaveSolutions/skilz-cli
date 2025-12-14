# Phase 1: Tasks

## Phase 1a: Foundation (MVP)

### T1: Project Setup
- [ ] Create `pyproject.toml` with metadata, dependencies (PyYAML), entry point
- [ ] Create `src/skilz/__init__.py` with `__version__ = "0.1.0"`
- [ ] Create `src/skilz/__main__.py` for `python -m skilz`
- [ ] Verify `pip install -e .` works

**Definition of Done**: Can run `skilz --version` and see version number

### T2: CLI Skeleton
- [ ] Create `src/skilz/cli.py` with argparse
- [ ] Add `install` subcommand with positional `skill_id`
- [ ] Add `--agent` optional flag (choices: claude, opencode)
- [ ] Add `--verbose` flag for debug output
- [ ] Wire up to `__main__.py`

**Definition of Done**: `skilz install test-skill` runs without error (even if no-op)

### T3: Registry Module
- [ ] Create `src/skilz/registry.py`
- [ ] Implement `load_registry()` - check project then user location
- [ ] Implement `lookup_skill(skill_id)` - return dict or raise
- [ ] Create `src/skilz/errors.py` with `SkillNotFoundError`
- [ ] Add unit tests in `tests/test_registry.py`

**Definition of Done**: Can load a registry file and look up a skill

### T4: Git Operations Module
- [ ] Create `src/skilz/git_ops.py`
- [ ] Implement `clone_or_fetch(git_repo)` - clone to cache or fetch if exists
- [ ] Implement `checkout_sha(cache_path, sha)` - checkout specific commit
- [ ] Implement `get_cache_path(git_repo)` - hash-based cache directory
- [ ] Handle errors: clone failure, SHA not found
- [ ] Add unit tests with mocked subprocess

**Definition of Done**: Can clone a repo and checkout a specific SHA

### T5: Basic Installer (Claude Code Only)
- [ ] Create `src/skilz/installer.py`
- [ ] Implement `install_skill(skill_id, agent="claude")`
- [ ] Wire together: registry → git → copy files
- [ ] Copy to `~/.claude/skills/<skill-name>/`
- [ ] Add integration test with real Git repo

**Definition of Done**: `skilz install test-skill` actually installs to Claude Code

---

## Phase 1b: Multi-Agent Support

### T6: Agent Detection Module
- [ ] Create `src/skilz/agents.py`
- [ ] Implement `detect_agent()` - auto-detect from environment
- [ ] Implement `get_skills_dir(agent)` - return Path for agent
- [ ] Support Claude Code: `~/.claude/skills/` or `.claude/skills/`
- [ ] Support OpenCode: `~/.config/opencode/skills/`
- [ ] Add unit tests

**Definition of Done**: Correctly detects agent and returns appropriate path

### T7: Integrate Agent Detection
- [ ] Update `installer.py` to use `agents.py`
- [ ] Respect `--agent` flag override
- [ ] Update integration tests for both agents

**Definition of Done**: Can install to either Claude Code or OpenCode

---

## Phase 1c: Polish

### T8: Manifest Module
- [ ] Create `src/skilz/manifest.py`
- [ ] Implement `write_manifest(skill_dir, skill_info)`
- [ ] Implement `read_manifest(skill_dir)` - returns dict or None
- [ ] Include: installed_at, skill_id, git_repo, skill_path, git_sha, skilz_version
- [ ] Add unit tests

**Definition of Done**: Manifest files are created on install

### T9: Idempotency Logic
- [ ] Implement `needs_install(skill_dir, registry_sha)` in manifest.py
- [ ] Update installer to skip if already installed with same SHA
- [ ] Print appropriate message: "Already installed" vs "Installed" vs "Updated"

**Definition of Done**: Re-running install is a no-op for same SHA

### T10: Error Handling Polish
- [ ] Review all error paths
- [ ] Ensure clear, actionable messages
- [ ] Consistent exit codes (0=success, 1=user error, 2=system error)
- [ ] Add `--verbose` debug output

**Definition of Done**: All error scenarios have helpful messages

### T11: Test Coverage
- [ ] Run `pytest --cov` and identify gaps
- [ ] Add missing unit tests
- [ ] Add edge case tests (missing registry, bad YAML, etc.)
- [ ] Target 80%+ coverage

**Definition of Done**: Coverage report shows 80%+

### T12: Documentation
- [ ] Update README with installation instructions
- [ ] Add usage examples
- [ ] Document registry format
- [ ] Add contributing guide (optional)

**Definition of Done**: New user can install and use skilz from README alone

---

## Task Dependencies

```
T1 (setup) ──► T2 (cli) ──► T5 (installer)
                  │              │
                  │              ▼
T3 (registry) ────┴────► T5 ──► T7 (integrate agents)
                              │
T4 (git ops) ─────────────────┘
                              │
T6 (agents) ──────────────────┘
                              │
                              ▼
                    T8 (manifest) ──► T9 (idempotency)
                              │
                              ▼
                    T10 (errors) ──► T11 (tests) ──► T12 (docs)
```

## Estimated Complexity

| Task | Complexity | Lines of Code |
|------|------------|---------------|
| T1   | Low        | ~50           |
| T2   | Low        | ~80           |
| T3   | Medium     | ~100          |
| T4   | Medium     | ~120          |
| T5   | Medium     | ~150          |
| T6   | Low        | ~60           |
| T7   | Low        | ~30           |
| T8   | Low        | ~60           |
| T9   | Low        | ~40           |
| T10  | Low        | ~50           |
| T11  | Medium     | ~200 (tests)  |
| T12  | Low        | Docs only     |

**Total**: ~940 lines of code + ~200 lines of tests
