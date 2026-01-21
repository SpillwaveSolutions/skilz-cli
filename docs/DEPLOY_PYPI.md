# Deploying skilz to PyPI

This guide documents how to publish the `skilz` package to PyPI.

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

## Package Information

| Field | Value |
|-------|-------|
| Package Name | `skilz` |
| CLI Command | `skilz` |
| Install Command | `pip install skilz` |
| PyPI URL | https://pypi.org/project/skilz/ |
| TestPyPI URL | https://test.pypi.org/project/skilz/ |

## Prerequisites

### 1. Build Tools

The following tools are required (install globally or in your environment):

```bash
pip install build twine
```

### 2. E2E Testing

Before deploying, run the comprehensive E2E test suite to ensure all functionality works:

```bash
# Run full E2E test suite (tests all major features)
./scripts/end_to_end.sh

# Run API integration tests (tests marketplace endpoints)
./scripts/test_api_integration.sh

# Run REST marketplace tests (tests live API with real data)
./scripts/test_rest_marketplace_e2e.sh

# Run bug fix regression tests (tests recent fixes)
./scripts/test_bug_fixes_e2e.sh
```

**E2E Test Coverage:**
- ✅ Marketplace ID installation (`skilz install owner_repo/skill`)
- ✅ Git URL installation (`skilz install https://github.com/...`)
- ✅ Local file installation (`skilz install -f path/to/skill`)
- ✅ All supported agents (Claude, OpenCode, Gemini, Codex, Copilot, Universal)
- ✅ Project-level installations (`--project` flag)
- ✅ Custom config file targeting (`--config FILE`)
- ✅ List, remove, search, and visit commands
- ✅ API endpoint validation and error handling
- ✅ Regression testing for recent bug fixes

### 2. PyPI Account Setup

1. **Create account**: https://pypi.org/account/register/
2. **Enable 2FA**: Account Settings → Two-Factor Authentication
3. **Create API token**: https://pypi.org/manage/account/token/
   - Name: `skilz-cli-publish`
   - Scope: "Entire account" (first publish) or project-scoped (subsequent)

### 3. Configure Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Important**: Set file permissions to protect your tokens:
```bash
chmod 600 ~/.pypirc
```

## Quality Assurance

### Testing Strategy

Skilz uses a comprehensive multi-layer testing approach:

1. **Unit Tests**: 633+ tests covering individual functions and modules
2. **Integration Tests**: API client and config sync testing
3. **E2E Tests**: Real-world scenario testing with isolated environments
4. **Regression Tests**: Bug fix validation with before/after testing

### Pre-Deployment Checklist

- [ ] `task check` passes (lint + typecheck + test)
- [ ] `./scripts/end_to_end.sh` passes (full feature test)
- [ ] `./scripts/test_rest_marketplace_e2e.sh` passes (live API test)
- [ ] `./scripts/test_bug_fixes_e2e.sh` passes (regression test)
- [ ] Version updated in `pyproject.toml` (single source of truth)
- [ ] CHANGELOG.md updated with release notes
- [ ] GitHub release created and tagged

## Release Process

### Quick Release (All-in-One)

```bash
# Full pipeline: clean → check → test → build → publish
task publish
```

### Step-by-Step Release

#### Step 1: Pre-Release Checks

```bash
task release:check
```

This runs:
- `clean` - Remove build artifacts
- `lint` - Ruff linting
- `typecheck` - mypy type checking
- `format:check` - Code formatting verification
- `coverage:check` - Tests with 80% coverage requirement

#### Step 2: Build Distribution

```bash
task release:build
```

Creates in `dist/`:
- `skilz-X.Y.Z.tar.gz` - Source distribution
- `skilz-X.Y.Z-py3-none-any.whl` - Wheel (binary)

#### Step 3: Test on TestPyPI (Recommended)

```bash
task publish:test
```

Verify the test release:
```bash
pip install -i https://test.pypi.org/simple/ skilz
skilz --version
```

#### Step 4: Publish to Production PyPI

```bash
task publish
```

#### Step 5: Verify

```bash
pip install --upgrade skilz
skilz --version
```

## Version Management

**Single Source of Truth:** `pyproject.toml` (line 7)

The version is defined ONLY in `pyproject.toml`:

```toml
[project]
version = "1.9.0"
```

The Python package reads this dynamically at runtime via `importlib.metadata`:

```python
# src/skilz/__init__.py
from importlib.metadata import version
__version__ = version("skilz")  # Reads from pyproject.toml
```

**Before releasing**, only update `pyproject.toml`. No other files need version changes.

**Note:** Previous versions required updating both `pyproject.toml` AND `__init__.py`. This was fixed in 1.7 to use dynamic version detection, eliminating version sync issues.

## Taskfile Commands Reference

| Command | Description |
|---------|-------------|
| `task release:check` | Run all quality checks |
| `task release:build` | Build source and wheel distributions |
| `task publish:test` | Upload to TestPyPI |
| `task publish` | Upload to production PyPI |
| `task clean` | Remove build artifacts |
| `task ci` | Full CI pipeline |

## Troubleshooting

### "File already exists" Error

PyPI doesn't allow re-uploading the same version. Bump the version number.

### "Invalid or non-existent authentication"

Check your `~/.pypirc` file:
- Token must start with `pypi-`
- Username must be `__token__` (literal string)

### TestPyPI Dependencies Missing

TestPyPI may not have all dependencies. Install from regular PyPI first:
```bash
pip install pyyaml
pip install -i https://test.pypi.org/simple/ skilz
```

### Build Fails

Ensure you have the build tools:
```bash
pip install --upgrade build hatchling
```

## Security Notes

- **Never commit** `~/.pypirc` or tokens to git
- Use **project-scoped tokens** after first publish
- Enable **2FA** on your PyPI account
- Consider using **Trusted Publishers** (GitHub Actions OIDC) for CI/CD

## CI/CD Integration (Future)

For automated releases via GitHub Actions, see:
- PyPI Trusted Publishers: https://docs.pypi.org/trusted-publishers/
- GitHub Actions workflow example in `.github/workflows/`

## Links

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Hatchling Build Backend](https://hatch.pypa.io/latest/)
