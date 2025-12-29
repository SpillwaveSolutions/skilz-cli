"""Tests for git_install module."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from skilz.git_install import (
    GitSkillInfo,
    find_skills_from_marketplace,
    find_skills_in_repo,
    get_head_sha,
    install_from_git,
    parse_skill_name,
    prompt_skill_selection,
)


class TestParseSkillName:
    """Tests for parse_skill_name function."""

    def test_parse_name_from_frontmatter(self, tmp_path):
        """Test extracting name from YAML frontmatter."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            """---
name: my-custom-skill
description: A test skill
---

# My Skill

Content here.
"""
        )

        result = parse_skill_name(skill_md)
        assert result == "my-custom-skill"

    def test_parse_name_quoted(self, tmp_path):
        """Test extracting quoted name from frontmatter."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            """---
name: "quoted-skill-name"
---

# Content
"""
        )

        result = parse_skill_name(skill_md)
        assert result == "quoted-skill-name"

    def test_parse_name_single_quoted(self, tmp_path):
        """Test extracting single-quoted name from frontmatter."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            """---
name: 'single-quoted'
---

Content
"""
        )

        result = parse_skill_name(skill_md)
        assert result == "single-quoted"

    def test_fallback_to_directory_name(self, tmp_path):
        """Test falling back to directory name when no name in frontmatter."""
        skill_dir = tmp_path / "my-skill-dir"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Just content, no frontmatter")

        result = parse_skill_name(skill_md)
        assert result == "my-skill-dir"

    def test_fallback_when_empty_name(self, tmp_path):
        """Test falling back when name field is empty."""
        skill_dir = tmp_path / "fallback-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name:
---

Content
"""
        )

        result = parse_skill_name(skill_md)
        assert result == "fallback-skill"

    def test_fallback_on_read_error(self, tmp_path):
        """Test falling back when file can't be read."""
        skill_dir = tmp_path / "error-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        # Create file that exists but with name we can get from parent

        result = parse_skill_name(skill_md)  # File doesn't exist
        assert result == "error-skill"


class TestFindSkillsInRepo:
    """Tests for find_skills_in_repo function."""

    def test_find_single_skill(self, tmp_path):
        """Test finding a single skill in repo root."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            """---
name: root-skill
---

Content
"""
        )

        skills = find_skills_in_repo(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "root-skill"
        assert skills[0].skill_path == tmp_path
        assert skills[0].relative_path == "."

    def test_find_multiple_skills(self, tmp_path):
        """Test finding multiple skills in subdirectories."""
        # Create skill 1
        skill1_dir = tmp_path / "skills" / "skill-one"
        skill1_dir.mkdir(parents=True)
        (skill1_dir / "SKILL.md").write_text("---\nname: skill-one\n---\n")

        # Create skill 2
        skill2_dir = tmp_path / "skills" / "skill-two"
        skill2_dir.mkdir(parents=True)
        (skill2_dir / "SKILL.md").write_text("---\nname: skill-two\n---\n")

        skills = find_skills_in_repo(tmp_path)

        assert len(skills) == 2
        skill_names = [s.skill_name for s in skills]
        assert "skill-one" in skill_names
        assert "skill-two" in skill_names

    def test_skip_git_directory_only(self, tmp_path):
        """Test that only .git directory is skipped, not .claude or .opencode."""
        # Create skill in .git directory (should be skipped)
        git_dir = tmp_path / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "SKILL.md").write_text("---\nname: git-hook\n---\n")

        # Create skill in .claude directory (should be found)
        claude_dir = tmp_path / ".claude" / "skills" / "my-skill"
        claude_dir.mkdir(parents=True)
        (claude_dir / "SKILL.md").write_text("---\nname: claude-skill\n---\n")

        # Create skill in .opencode directory (should be found)
        opencode_dir = tmp_path / ".opencode" / "skills" / "another-skill"
        opencode_dir.mkdir(parents=True)
        (opencode_dir / "SKILL.md").write_text("---\nname: opencode-skill\n---\n")

        # Create visible skill
        visible_dir = tmp_path / "visible"
        visible_dir.mkdir()
        (visible_dir / "SKILL.md").write_text("---\nname: visible\n---\n")

        skills = find_skills_in_repo(tmp_path)

        # Should find 3 skills (claude, opencode, visible) but not .git
        assert len(skills) == 3
        skill_names = [s.skill_name for s in skills]
        assert "claude-skill" in skill_names
        assert "opencode-skill" in skill_names
        assert "visible" in skill_names
        assert "git-hook" not in skill_names

    def test_empty_repo(self, tmp_path):
        """Test finding no skills in empty repo."""
        skills = find_skills_in_repo(tmp_path)
        assert len(skills) == 0

    def test_sorted_by_name(self, tmp_path):
        """Test skills are sorted alphabetically by name."""
        for name in ["zebra", "alpha", "middle"]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\n---\n")

        skills = find_skills_in_repo(tmp_path)

        assert len(skills) == 3
        assert skills[0].skill_name == "alpha"
        assert skills[1].skill_name == "middle"
        assert skills[2].skill_name == "zebra"


class TestPromptSkillSelection:
    """Tests for prompt_skill_selection function."""

    def test_single_skill_returns_directly(self):
        """Test that single skill is returned without prompting."""
        skill = GitSkillInfo(
            skill_name="only-skill",
            skill_path=Path("/tmp/skill"),
            relative_path="skill",
        )

        result = prompt_skill_selection([skill])

        assert len(result) == 1
        assert result[0].skill_name == "only-skill"

    def test_install_all_flag(self):
        """Test --all flag returns all skills without prompting."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        result = prompt_skill_selection(skills, install_all=True)

        assert len(result) == 2

    def test_yes_all_flag(self):
        """Test -y flag returns all skills without prompting."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        result = prompt_skill_selection(skills, yes_all=True)

        assert len(result) == 2

    def test_select_single_number(self, monkeypatch):
        """Test selecting a single skill by number."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "1")

        result = prompt_skill_selection(skills)

        assert len(result) == 1
        assert result[0].skill_name == "skill1"

    def test_select_multiple_numbers(self, monkeypatch):
        """Test selecting multiple skills by comma-separated numbers."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
            GitSkillInfo(skill_name="skill3", skill_path=Path("/tmp/3"), relative_path="3"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "1,3")

        result = prompt_skill_selection(skills)

        assert len(result) == 2
        assert result[0].skill_name == "skill1"
        assert result[1].skill_name == "skill3"

    def test_select_all_option(self, monkeypatch):
        """Test selecting all with 'A' option."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "A")

        result = prompt_skill_selection(skills)

        assert len(result) == 2

    def test_cancel_option(self, monkeypatch):
        """Test canceling with 'Q' option."""
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "Q")

        result = prompt_skill_selection(skills)

        assert len(result) == 0

    def test_empty_input_cancels(self, monkeypatch):
        """Test empty input cancels selection."""
        # Need multiple skills to trigger prompt
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "")

        result = prompt_skill_selection(skills)

        assert len(result) == 0

    def test_invalid_number(self, monkeypatch, capsys):
        """Test invalid number shows error."""
        # Need multiple skills to trigger prompt
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "99")

        result = prompt_skill_selection(skills)

        assert len(result) == 0
        captured = capsys.readouterr()
        assert "Invalid selection" in captured.out

    def test_invalid_input(self, monkeypatch, capsys):
        """Test invalid input shows error."""
        # Need multiple skills to trigger prompt
        skills = [
            GitSkillInfo(skill_name="skill1", skill_path=Path("/tmp/1"), relative_path="1"),
            GitSkillInfo(skill_name="skill2", skill_path=Path("/tmp/2"), relative_path="2"),
        ]

        monkeypatch.setattr("builtins.input", lambda _: "abc")

        result = prompt_skill_selection(skills)

        assert len(result) == 0
        captured = capsys.readouterr()
        assert "Invalid selection" in captured.out


class TestGetHeadSha:
    """Tests for get_head_sha function."""

    def test_get_sha_from_repo(self, tmp_path):
        """Test getting HEAD SHA from a git repo."""
        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=tmp_path,
            capture_output=True,
            env={
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@test.com",
            },
        )

        sha = get_head_sha(tmp_path)

        assert len(sha) == 40
        assert all(c in "0123456789abcdef" for c in sha)

    def test_get_sha_non_repo(self, tmp_path):
        """Test getting SHA from non-git directory returns 'unknown'."""
        sha = get_head_sha(tmp_path)
        assert sha == "unknown"


class TestInstallFromGit:
    """Tests for install_from_git function."""

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_single_skill_installs_without_prompt(
        self, mock_install, mock_cleanup, mock_clone, tmp_path
    ):
        """Test single skill in repo installs without prompting."""
        # Setup mock repo
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        mock_clone.return_value = tmp_path

        result = install_from_git(
            git_url="https://github.com/test/repo.git",
            verbose=False,
        )

        assert result == 0
        mock_install.assert_called_once()
        mock_cleanup.assert_called_once_with(tmp_path)

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    def test_no_skills_found_error(self, mock_cleanup, mock_clone, tmp_path, capsys):
        """Test error when no skills found in repo."""
        mock_clone.return_value = tmp_path  # Empty directory

        result = install_from_git(
            git_url="https://github.com/test/empty.git",
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "No skills found" in captured.err
        mock_cleanup.assert_called_once()

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_install_all_flag(self, mock_install, mock_cleanup, mock_clone, tmp_path):
        """Test --all flag installs all skills."""
        # Create multiple skills
        for name in ["skill1", "skill2"]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\n---\n")

        mock_clone.return_value = tmp_path

        result = install_from_git(
            git_url="https://github.com/test/repo.git",
            install_all=True,
        )

        assert result == 0
        assert mock_install.call_count == 2
        mock_cleanup.assert_called_once()

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    def test_clone_failure(self, mock_cleanup, mock_clone, capsys):
        """Test handling clone failure."""
        mock_clone.side_effect = RuntimeError("Clone failed")

        result = install_from_git(
            git_url="https://github.com/test/bad.git",
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Clone failed" in captured.err

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_passes_parameters_to_install(self, mock_install, mock_cleanup, mock_clone, tmp_path):
        """Test that parameters are passed through to install."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: skill\n---\n")

        mock_clone.return_value = tmp_path

        result = install_from_git(
            git_url="https://github.com/test/repo.git",
            agent="opencode",
            project_level=True,
            verbose=True,
            mode="copy",
        )

        assert result == 0
        call_kwargs = mock_install.call_args[1]
        assert call_kwargs["agent"] == "opencode"
        assert call_kwargs["project_level"] is True
        assert call_kwargs["verbose"] is True
        assert call_kwargs["mode"] == "copy"
        assert call_kwargs["git_url"] == "https://github.com/test/repo.git"

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_cleanup_on_success(self, mock_install, mock_cleanup, mock_clone, tmp_path):
        """Test cleanup happens on success."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: skill\n---\n")

        mock_clone.return_value = tmp_path

        install_from_git(git_url="https://github.com/test/repo.git")

        mock_cleanup.assert_called_once_with(tmp_path)

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_cleanup_on_install_error(self, mock_install, mock_cleanup, mock_clone, tmp_path):
        """Test cleanup happens even on install failure."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: skill\n---\n")

        mock_clone.return_value = tmp_path
        from skilz.errors import InstallError

        mock_install.side_effect = InstallError("skill", "Install failed")

        result = install_from_git(git_url="https://github.com/test/repo.git")

        assert result == 1
        mock_cleanup.assert_called_once_with(tmp_path)

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    @patch("skilz.installer.install_local_skill")
    def test_skill_filter_name_success(self, mock_install, mock_cleanup, mock_clone, tmp_path):
        """Test --skill flag finds and installs specific skill."""
        # Create multiple skills
        for name in ["skill1", "skill2", "target-skill"]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\n---\n")

        mock_clone.return_value = tmp_path

        result = install_from_git(
            git_url="https://github.com/test/repo.git",
            skill_filter_name="target-skill",
        )

        assert result == 0
        # Only the target skill should be installed
        assert mock_install.call_count == 1
        call_kwargs = mock_install.call_args[1]
        assert call_kwargs["skill_name"] == "target-skill"
        mock_cleanup.assert_called_once()

    @patch("skilz.link_ops.clone_git_repo")
    @patch("skilz.link_ops.cleanup_temp_dir")
    def test_skill_filter_name_not_found(self, mock_cleanup, mock_clone, tmp_path, capsys):
        """Test --skill flag shows error when skill not found."""
        # Create some skills (but not the one we're looking for)
        for name in ["skill1", "skill2"]:
            skill_dir = tmp_path / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\n---\n")

        mock_clone.return_value = tmp_path

        result = install_from_git(
            git_url="https://github.com/test/repo.git",
            skill_filter_name="nonexistent-skill",
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "nonexistent-skill" in captured.err
        assert "not found" in captured.err
        assert "Available skills:" in captured.err
        assert "skill1" in captured.err
        assert "skill2" in captured.err
        mock_cleanup.assert_called_once()


class TestFindSkillsFromMarketplace:
    """Tests for find_skills_from_marketplace function."""

    def test_official_location(self, tmp_path):
        """Test finding skills from official .claude-plugin/marketplace.json location."""
        # Create official marketplace location
        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()

        # Create skill directory
        skill_dir = tmp_path / "plugins" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        # Create marketplace.json
        (plugin_dir / "marketplace.json").write_text(
            """
{
    "name": "test-marketplace",
    "plugins": [
        {
            "name": "my-skill",
            "source": "./plugins/my-skill"
        }
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "my-skill"
        assert skills[0].relative_path == "plugins/my-skill"

    def test_root_fallback(self, tmp_path):
        """Test fallback to marketplace.json at repo root."""
        # Create skill directory
        skill_dir = tmp_path / "skills" / "root-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: root-skill\n---\n")

        # Create marketplace.json at root (no .claude-plugin/)
        (tmp_path / "marketplace.json").write_text(
            """
{
    "name": "root-marketplace",
    "plugins": [
        {
            "name": "root-skill",
            "source": "./skills/root-skill"
        }
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "root-skill"

    def test_official_takes_priority(self, tmp_path):
        """Test that .claude-plugin/marketplace.json takes priority over root."""
        # Create skill directories
        official_skill = tmp_path / "official-skill"
        official_skill.mkdir()
        (official_skill / "SKILL.md").write_text("---\nname: official\n---\n")

        root_skill = tmp_path / "root-skill"
        root_skill.mkdir()
        (root_skill / "SKILL.md").write_text("---\nname: root\n---\n")

        # Create both marketplace files
        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text(
            '{"name": "official", "plugins": [{"name": "official", "source": "./official-skill"}]}'
        )
        (tmp_path / "marketplace.json").write_text(
            '{"name": "root", "plugins": [{"name": "root", "source": "./root-skill"}]}'
        )

        skills = find_skills_from_marketplace(tmp_path)

        # Should find the official one, not the root one
        assert len(skills) == 1
        assert skills[0].skill_name == "official"

    def test_multiple_plugins(self, tmp_path):
        """Test finding multiple skills from marketplace."""
        # Create skill directories
        for name in ["alpha", "beta", "gamma"]:
            skill_dir = tmp_path / "plugins" / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\n---\n")

        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text(
            """
{
    "name": "multi",
    "plugins": [
        {"name": "alpha", "source": "./plugins/alpha"},
        {"name": "beta", "source": "./plugins/beta"},
        {"name": "gamma", "source": "./plugins/gamma"}
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 3
        skill_names = [s.skill_name for s in skills]
        # Should be sorted alphabetically
        assert skill_names == ["alpha", "beta", "gamma"]

    def test_skips_missing_skill_md(self, tmp_path):
        """Test that plugins without SKILL.md are skipped."""
        # Create one skill with SKILL.md
        good_skill = tmp_path / "good-skill"
        good_skill.mkdir()
        (good_skill / "SKILL.md").write_text("---\nname: good\n---\n")

        # Create one skill without SKILL.md
        bad_skill = tmp_path / "bad-skill"
        bad_skill.mkdir()
        (bad_skill / "README.md").write_text("No SKILL.md here")

        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text(
            """
{
    "name": "mixed",
    "plugins": [
        {"name": "good", "source": "./good-skill"},
        {"name": "bad", "source": "./bad-skill"}
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "good"

    def test_skips_non_local_sources(self, tmp_path):
        """Test that non-local sources (github refs) are skipped."""
        # Create local skill
        local_skill = tmp_path / "local-skill"
        local_skill.mkdir()
        (local_skill / "SKILL.md").write_text("---\nname: local\n---\n")

        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text(
            """
{
    "name": "mixed-sources",
    "plugins": [
        {"name": "local", "source": "./local-skill"},
        {"name": "remote", "source": {"github": "owner/repo", "ref": "v1.0"}}
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "local"

    def test_no_marketplace_returns_empty(self, tmp_path):
        """Test that missing marketplace files return empty list."""
        skills = find_skills_from_marketplace(tmp_path)
        assert len(skills) == 0

    def test_invalid_json_skipped(self, tmp_path):
        """Test that invalid JSON is gracefully handled."""
        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text("{ invalid json }")

        skills = find_skills_from_marketplace(tmp_path)
        assert len(skills) == 0

    def test_source_without_dot_slash(self, tmp_path):
        """Test handling source paths without ./ prefix."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "marketplace.json").write_text(
            """
{
    "name": "no-prefix",
    "plugins": [
        {"name": "my-skill", "source": "my-skill"}
    ]
}
"""
        )

        skills = find_skills_from_marketplace(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "my-skill"
