"""Unit tests for SKILZ-64 and SKILZ-65 bug fixes.

These tests should FAIL initially due to the bugs, then PASS after fixes.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestBugFixes:
    """Test cases for SKILZ-64 and SKILZ-65 bug fixes."""

    # ============================================================================
    # BUG 1 TESTS: SKILZ-64 - Temp Directory Warning During Git Installs
    # ============================================================================

    def test_bug1_git_install_no_temp_warning(self):
        """Test that git installs don't show temp directory warnings.

        This test should FAIL before the fix, PASS after.
        """
        from skilz.installer import install_local_skill

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock skill directory with SKILL.md
            skill_dir = Path(temp_dir) / "test-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("name: test-skill\ndescription: Test skill")

            # Capture stderr to check for warnings
            import io

            stderr_capture = io.StringIO()

            with patch("sys.stderr", stderr_capture):
                # This should NOT produce a warning for git installs (git_url provided)
                install_local_skill(
                    source_path=skill_dir,
                    agent="gemini",  # type: ignore
                    project_level=True,
                    verbose=False,
                    git_url="https://github.com/test/repo",  # Indicates git install
                    skill_name="test-skill",
                )

                # Check stderr for warnings
                stderr_output = stderr_capture.getvalue()
                assert "doesn't match skill name" not in stderr_output, (
                    f"Git install should not warn about temp directories, but got: {stderr_output}"
                )

    def test_bug1_local_install_shows_warning(self):
        """Test that local installs still show warnings for permanent directories.

        This test should PASS both before and after the fix.
        """
        from skilz.installer import install_local_skill

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a skill directory with WRONG name
            wrong_dir = Path(temp_dir) / "wrong-name-skill"
            wrong_dir.mkdir()
            skill_md = wrong_dir / "SKILL.md"
            skill_md.write_text("name: correct-skill-name\ndescription: Test skill")

            # Capture stderr
            import io

            stderr_capture = io.StringIO()

            with patch("sys.stderr", stderr_capture):
                # This SHOULD produce a warning for local installs (no git_url)
                install_local_skill(
                    source_path=wrong_dir,
                    agent="gemini",  # type: ignore
                    project_level=True,
                    verbose=False,
                    git_url=None,  # Indicates local install
                    skill_name="correct-skill-name",
                )

                # Check stderr for warnings
                stderr_output = stderr_capture.getvalue()
                assert "doesn't match skill name" in stderr_output, (
                    "Local install should warn about mismatched directory names, "
                    f"but got: {stderr_output}"
                )

    # ============================================================================
    # BUG 2 TESTS: SKILZ-65 - --config Flag Not Working for Git Installs
    # ============================================================================

    def test_bug2_git_install_config_parameter_exists(self):
        """Test that install_from_git accepts config_file parameter.

        This test should PASS after the fix (parameter exists), FAIL before.
        """
        from skilz.git_install import install_from_git

        # This should NOT raise TypeError after the fix (parameter exists)
        # We expect it to fail with git repo not found, not parameter error
        try:
            install_from_git(
                git_url="https://github.com/test/repo",
                agent="gemini",  # type: ignore
                project_level=True,
                config_file="TEST_CONFIG.md",  # This parameter should exist after fix
            )
            # If we get here, something unexpected happened
            assert False, "Expected git clone to fail, but it didn't"
        except Exception as e:
            # We expect some error (git repo not found), but NOT TypeError about missing parameter
            assert not isinstance(e, TypeError) or "config_file" not in str(e), (
                f"config_file parameter should exist, but got TypeError: {e}"
            )
            # Any other error (like git repo not found) means the parameter exists
            assert True, "config_file parameter accepted (git error expected)"

    def test_bug2_config_flag_validation(self):
        """Test that --config requires --project flag.

        This should PASS both before and after the fix (existing validation).
        """
        import argparse

        from skilz.commands.install_cmd import cmd_install

        # Mock args with --config but no --project
        mock_args = argparse.Namespace(
            skill_id="test-skill",
            agent="gemini",
            project=False,  # No --project
            config="TEST.md",  # Has --config
            file=None,
            git=None,
            version_spec=None,
            force_config=False,
            copy=False,
            symlink=False,
            verbose=False,
            yes_all=False,
            install_all=False,
            skill=None,
        )

        # This should fail with error message
        import io

        stderr_capture = io.StringIO()

        with patch("sys.stderr", stderr_capture):
            result = cmd_install(mock_args)
            assert result == 1, "Should return error code 1"

            stderr_output = stderr_capture.getvalue()
            assert "--config requires --project" in stderr_output, (
                f"Should show config validation error, got: {stderr_output}"
            )
