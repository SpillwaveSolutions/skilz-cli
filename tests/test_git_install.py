"""Tests for git_install module."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from skilz.git_install import (
    GitSkillInfo,
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

    def test_skip_hidden_directories(self, tmp_path):
        """Test that hidden directories are skipped."""
        # Create skill in hidden directory
        hidden_dir = tmp_path / ".hidden" / "skill"
        hidden_dir.mkdir(parents=True)
        (hidden_dir / "SKILL.md").write_text("---\nname: hidden\n---\n")

        # Create visible skill
        visible_dir = tmp_path / "visible"
        visible_dir.mkdir()
        (visible_dir / "SKILL.md").write_text("---\nname: visible\n---\n")

        skills = find_skills_in_repo(tmp_path)

        assert len(skills) == 1
        assert skills[0].skill_name == "visible"

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
