"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def sample_registry_content():
    """Sample registry YAML content for testing."""
    return """
test/sample-skill:
  git_repo: https://github.com/test/skills.git
  skill_path: /main/skills/sample-skill
  git_sha: abc123def456789012345678901234567890abcd

another/skill:
  git_repo: git@github.com:another/repo.git
  skill_path: /main/skills/another
  git_sha: 1234567890abcdef1234567890abcdef12345678
"""


@pytest.fixture
def project_registry(temp_dir, sample_registry_content):
    """Create a project-level registry file."""
    registry_dir = temp_dir / ".skilz"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "registry.yaml"
    registry_file.write_text(sample_registry_content)
    return temp_dir
