"""Tests for the list command."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse

from skilz.commands.list_cmd import (
    cmd_list,
    format_table_output,
    format_json_output,
    get_skill_status,
)
from skilz.scanner import InstalledSkill
from skilz.manifest import SkillManifest, write_manifest
from skilz.registry import SkillInfo


@pytest.fixture
def sample_manifest():
    """Create a sample manifest."""
    return SkillManifest.create(
        skill_id="spillwave/plantuml",
        git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
        skill_path="/main/SKILL.md",
        git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",
    )


@pytest.fixture
def sample_installed_skill(temp_dir, sample_manifest):
    """Create a sample installed skill."""
    skill_dir = temp_dir / "plantuml"
    skill_dir.mkdir(parents=True)
    return InstalledSkill(
        skill_id="spillwave/plantuml",
        skill_name="plantuml",
        path=skill_dir,
        manifest=sample_manifest,
        agent="claude",
        project_level=False,
    )


@pytest.fixture
def skills_dir_with_skills(temp_dir):
    """Create a skills directory with installed skills."""
    skills_dir = temp_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create first skill
    skill1_dir = skills_dir / "plantuml"
    skill1_dir.mkdir()
    manifest1 = SkillManifest.create(
        skill_id="spillwave/plantuml",
        git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
        skill_path="/main/SKILL.md",
        git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",
    )
    write_manifest(skill1_dir, manifest1)

    # Create second skill
    skill2_dir = skills_dir / "mermaid"
    skill2_dir.mkdir()
    manifest2 = SkillManifest.create(
        skill_id="spillwave/design-doc-mermaid",
        git_repo="https://github.com/SpillwaveSolutions/design-doc-mermaid.git",
        skill_path="/v1.0.0/SKILL.md",
        git_sha="e1c29a38abcd1234567890abcdef1234567890ab",
    )
    write_manifest(skill2_dir, manifest2)

    return temp_dir


class TestGetSkillStatus:
    """Tests for get_skill_status function."""

    def test_status_up_to_date(self, sample_installed_skill):
        """Test status when SHA matches registry."""
        with patch("skilz.commands.list_cmd.lookup_skill") as mock_lookup:
            mock_lookup.return_value = SkillInfo(
                skill_id="spillwave/plantuml",
                git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
                skill_path="/main/SKILL.md",
                git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",  # Same SHA
            )

            status = get_skill_status(sample_installed_skill)
            assert status == "up-to-date"

    def test_status_outdated(self, sample_installed_skill):
        """Test status when SHA differs from registry."""
        with patch("skilz.commands.list_cmd.lookup_skill") as mock_lookup:
            mock_lookup.return_value = SkillInfo(
                skill_id="spillwave/plantuml",
                git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
                skill_path="/main/SKILL.md",
                git_sha="new_sha_from_registry_1234567890abcdef",  # Different SHA
            )

            status = get_skill_status(sample_installed_skill)
            assert status == "outdated"

    def test_status_unknown_when_not_in_registry(self, sample_installed_skill):
        """Test status when skill not found in registry."""
        with patch("skilz.commands.list_cmd.lookup_skill") as mock_lookup:
            mock_lookup.side_effect = Exception("Skill not found")

            status = get_skill_status(sample_installed_skill)
            assert status == "unknown"


class TestFormatTableOutput:
    """Tests for format_table_output function."""

    def test_empty_skills_list(self):
        """Test output when no skills are installed."""
        output = format_table_output([])
        assert output == "No skills installed."

    def test_table_has_headers(self, sample_installed_skill):
        """Test that table output includes headers."""
        with patch("skilz.commands.list_cmd.get_skill_status", return_value="up-to-date"):
            output = format_table_output([sample_installed_skill])

        assert "Skill" in output
        assert "Version" in output
        assert "Installed" in output
        assert "Status" in output

    def test_table_has_skill_data(self, sample_installed_skill):
        """Test that table output includes skill data."""
        with patch("skilz.commands.list_cmd.get_skill_status", return_value="up-to-date"):
            output = format_table_output([sample_installed_skill])

        assert "spillwave/plantuml" in output
        assert "f2489dcd" in output  # Short SHA
        assert "up-to-date" in output


class TestFormatJsonOutput:
    """Tests for format_json_output function."""

    def test_empty_skills_list(self):
        """Test JSON output when no skills are installed."""
        output = format_json_output([])
        parsed = json.loads(output)
        assert parsed == []

    def test_json_has_required_fields(self, sample_installed_skill):
        """Test that JSON output includes all required fields."""
        with patch("skilz.commands.list_cmd.get_skill_status", return_value="up-to-date"):
            output = format_json_output([sample_installed_skill])

        parsed = json.loads(output)
        assert len(parsed) == 1

        skill = parsed[0]
        assert skill["skill_id"] == "spillwave/plantuml"
        assert skill["skill_name"] == "plantuml"
        assert skill["git_sha"] == "f2489dcd47799e4aaff3ae0a34cde0ebf2288a66"
        assert skill["status"] == "up-to-date"
        assert skill["agent"] == "claude"
        assert skill["project_level"] is False
        assert "path" in skill
        assert "installed_at" in skill


class TestCmdList:
    """Tests for cmd_list function."""

    def test_list_command_success(self, skills_dir_with_skills, capsys):
        """Test successful list command execution."""
        args = argparse.Namespace(
            agent="claude",
            project=True,
            json=False,
            verbose=False,
        )

        with patch("skilz.commands.list_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = []
            with patch("skilz.commands.list_cmd.get_skill_status", return_value="unknown"):
                result = cmd_list(args)

        assert result == 0

    def test_list_command_json_output(self, skills_dir_with_skills, capsys):
        """Test list command with JSON output."""
        args = argparse.Namespace(
            agent="claude",
            project=True,
            json=True,
            verbose=False,
        )

        with patch("skilz.commands.list_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = []
            result = cmd_list(args)

        captured = capsys.readouterr()
        # Should be valid JSON
        parsed = json.loads(captured.out)
        assert parsed == []
        assert result == 0

    def test_list_command_handles_error(self, capsys):
        """Test list command error handling."""
        args = argparse.Namespace(
            agent="claude",
            project=False,
            json=False,
            verbose=False,
        )

        with patch("skilz.commands.list_cmd.scan_installed_skills") as mock_scan:
            mock_scan.side_effect = Exception("Test error")
            result = cmd_list(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
