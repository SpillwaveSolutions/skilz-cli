"""Manifest file handling for installed skills."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from skilz import __version__

MANIFEST_FILENAME = ".skilz-manifest.yaml"


@dataclass
class SkillManifest:
    """Manifest data for an installed skill."""

    installed_at: str
    skill_id: str
    git_repo: str
    skill_path: str
    git_sha: str
    skilz_version: str

    @classmethod
    def create(
        cls,
        skill_id: str,
        git_repo: str,
        skill_path: str,
        git_sha: str,
    ) -> "SkillManifest":
        """Create a new manifest with current timestamp and skilz version."""
        return cls(
            installed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            skill_id=skill_id,
            git_repo=git_repo,
            skill_path=skill_path,
            git_sha=git_sha,
            skilz_version=__version__,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return asdict(self)


def write_manifest(skill_dir: Path, manifest: SkillManifest) -> Path:
    """
    Write a manifest file to the installed skill directory.

    Args:
        skill_dir: Path to the installed skill directory.
        manifest: The manifest data to write.

    Returns:
        Path to the written manifest file.
    """
    manifest_path = skill_dir / MANIFEST_FILENAME
    content = yaml.dump(manifest.to_dict(), default_flow_style=False, sort_keys=False)
    manifest_path.write_text(content)
    return manifest_path


def read_manifest(skill_dir: Path) -> SkillManifest | None:
    """
    Read a manifest file from an installed skill directory.

    Args:
        skill_dir: Path to the installed skill directory.

    Returns:
        SkillManifest if found and valid, None otherwise.
    """
    manifest_path = skill_dir / MANIFEST_FILENAME

    if not manifest_path.exists():
        return None

    try:
        content = manifest_path.read_text()
        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            return None

        # Validate required fields
        required = ["installed_at", "skill_id", "git_repo", "skill_path", "git_sha", "skilz_version"]
        if not all(field in data for field in required):
            return None

        return SkillManifest(
            installed_at=data["installed_at"],
            skill_id=data["skill_id"],
            git_repo=data["git_repo"],
            skill_path=data["skill_path"],
            git_sha=data["git_sha"],
            skilz_version=data["skilz_version"],
        )

    except (yaml.YAMLError, OSError):
        return None


def needs_install(skill_dir: Path, registry_sha: str) -> tuple[bool, str]:
    """
    Check if a skill needs to be installed or updated.

    Args:
        skill_dir: Path to the skill directory.
        registry_sha: The SHA from the registry.

    Returns:
        Tuple of (needs_install, reason).
        - (True, "not_installed") if skill not installed
        - (True, "sha_mismatch") if installed but different SHA
        - (False, "up_to_date") if already installed with same SHA
    """
    if not skill_dir.exists():
        return True, "not_installed"

    manifest = read_manifest(skill_dir)

    if manifest is None:
        # Directory exists but no valid manifest
        return True, "no_manifest"

    if manifest.git_sha != registry_sha:
        return True, "sha_mismatch"

    return False, "up_to_date"
