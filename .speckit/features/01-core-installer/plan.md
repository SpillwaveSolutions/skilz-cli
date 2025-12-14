# Phase 1: Implementation Plan

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.10+ | Wide adoption, excellent stdlib, easy pip install |
| CLI Framework | `argparse` (stdlib) | No external deps, sufficient for Phase 1 |
| YAML Parsing | `PyYAML` | De facto standard, one dependency |
| Git Operations | Subprocess `git` | No gitpython dep, user has git installed |
| File Operations | `shutil`, `pathlib` | Stdlib, cross-platform |
| Date/Time | `datetime` | Stdlib, ISO 8601 formatting |

## Project Structure

```
skilz-cli/
├── pyproject.toml          # Package configuration
├── README.md               # User documentation
├── src/
│   └── skilz/
│       ├── __init__.py     # Version, exports
│       ├── __main__.py     # Entry point: python -m skilz
│       ├── cli.py          # Argument parsing, command dispatch
│       ├── registry.py     # Registry loading and parsing
│       ├── installer.py    # Core install logic
│       ├── git_ops.py      # Git clone, fetch, checkout
│       ├── agents.py       # Agent detection, path resolution
│       ├── manifest.py     # Manifest read/write
│       └── errors.py       # Custom exceptions
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_registry.py
│   ├── test_installer.py
│   ├── test_git_ops.py
│   ├── test_agents.py
│   └── test_manifest.py
└── .speckit/               # SDD artifacts
```

## Architecture

### Component Diagram

```
┌─────────────┐
│   cli.py    │  Parse args, dispatch to installer
└─────┬───────┘
      │
      v
┌─────────────┐    ┌──────────────┐
│ installer.py│───►│ registry.py  │  Load + parse registry
└─────┬───────┘    └──────────────┘
      │
      ├───────────►┌──────────────┐
      │            │  git_ops.py  │  Clone/fetch/checkout
      │            └──────────────┘
      │
      ├───────────►┌──────────────┐
      │            │  agents.py   │  Detect agent, get paths
      │            └──────────────┘
      │
      └───────────►┌──────────────┐
                   │ manifest.py  │  Write manifest
                   └──────────────┘
```

### Data Flow

```
1. User runs: skilz install some-skill

2. cli.py parses args:
   - skill_id = "some-skill"
   - agent = auto-detect or --agent flag

3. installer.py orchestrates:
   a. registry.py loads .skilz/registry.yaml or ~/.skilz/registry.yaml
   b. Look up skill_id → {git_repo, skill_path, git_sha}
   c. git_ops.py clones/fetches repo to ~/.skilz/cache/
   d. git_ops.py checks out git_sha
   e. agents.py determines target directory
   f. Copy skill files from cache to target
   g. manifest.py writes .skilz-manifest.yaml

4. cli.py prints success message, exits 0
```

## Key Design Decisions

### D1: Cache Strategy
**Decision**: Cache repos in `~/.skilz/cache/<repo-hash>/`

**Rationale**:
- Multiple skills from same repo share one clone
- Hash prevents path collisions from different repo URLs
- User can delete cache to force fresh clone

**Implementation**:
```python
import hashlib
def cache_path(git_repo: str) -> Path:
    repo_hash = hashlib.sha256(git_repo.encode()).hexdigest()[:12]
    return Path.home() / ".skilz" / "cache" / repo_hash
```

### D2: Agent Detection
**Decision**: Check for marker directories, allow override

**Rationale**:
- `.claude/` in cwd or home → Claude Code
- `~/.config/opencode/` exists → OpenCode
- Explicit `--agent` flag overrides auto-detection

**Implementation**:
```python
def detect_agent() -> str:
    if (Path.cwd() / ".claude").exists():
        return "claude"
    if (Path.home() / ".claude").exists():
        return "claude"
    if (Path.home() / ".config" / "opencode").exists():
        return "opencode"
    return "claude"  # Default
```

### D3: skill_path Parsing
**Decision**: skill_path format is `/<branch>/path/to/skill`

**Rationale**:
- Branch/tag prefix allows version pinning beyond just SHA
- Path after branch points to skill directory
- Consistent with GitHub URL patterns

**Implementation**:
```python
def parse_skill_path(skill_path: str) -> tuple[str, str]:
    parts = skill_path.lstrip("/").split("/", 1)
    branch = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    return branch, path
```

### D4: Idempotency Check
**Decision**: Compare manifest SHA to registry SHA

**Rationale**:
- If manifest exists and SHA matches, skip installation
- If SHA differs, reinstall (overwrite)
- If no manifest, fresh install

**Implementation**:
```python
def needs_install(target_dir: Path, registry_sha: str) -> bool:
    manifest = target_dir / ".skilz-manifest.yaml"
    if not manifest.exists():
        return True
    current = yaml.safe_load(manifest.read_text())
    return current.get("git_sha") != registry_sha
```

## Dependencies

### Runtime (pyproject.toml)
```toml
[project]
dependencies = [
    "PyYAML>=6.0",
]
```

### Development
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
```

## Error Strategy

| Error | Exit Code | User Message |
|-------|-----------|--------------|
| Skill not in registry | 1 | "Skill 'X' not found. Check .skilz/registry.yaml or ~/.skilz/registry.yaml" |
| Git clone failed | 2 | "Failed to clone {repo}. Check URL and access permissions." |
| SHA not found | 2 | "Commit {sha} not found in {repo}. Registry may be outdated." |
| Permission denied | 2 | "Cannot write to {path}. Check directory permissions." |

## Testing Strategy

### Unit Tests (mocked Git)
- `test_registry.py`: YAML parsing, fallback logic, missing fields
- `test_agents.py`: Detection logic, path resolution
- `test_manifest.py`: Read/write, schema validation

### Integration Tests (real Git)
- `test_installer.py`: Full install flow with test repo
- Use a small public repo (or create one) for testing
- Clean up installed skills after tests

### Test Fixtures
```python
@pytest.fixture
def sample_registry(tmp_path):
    registry = tmp_path / ".skilz" / "registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text("""
test/skill:
  git_repo: https://github.com/test/skills.git
  skill_path: /main/test-skill
  git_sha: abc123...
""")
    return tmp_path
```

## Implementation Phases

### Phase 1a: Foundation (MVP)
1. Project setup (pyproject.toml, structure)
2. Registry loading
3. Git operations (clone, checkout)
4. Basic installer
5. Claude Code support only

### Phase 1b: Multi-Agent
1. Agent detection
2. OpenCode support
3. `--agent` flag

### Phase 1c: Polish
1. Manifest generation
2. Idempotency checks
3. Error messages
4. Tests to 80%+
5. README documentation
