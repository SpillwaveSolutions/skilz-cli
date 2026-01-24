"""Integration tests for new agents added in Issues #46, #47, #49."""

from unittest.mock import patch

from skilz.agents import detect_agent
from skilz.installer import install_local_skill
from skilz.manifest import read_manifest


class TestOpenHandsIntegration:
    """Test OpenHands native skill installation scenarios."""

    def test_install_skill_to_openhands_native_project(self, tmp_path, monkeypatch):
        """Install skill to OpenHands project-level (.openhands/skills/) without config sync."""
        # Setup: Create an OpenHands project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".openhands" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill\nA test skill for OpenHands.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="openhands"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to .openhands/skills/
        installed_skill = target_root / "test-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/test-skill"


class TestClineIntegration:
    """Test Cline native skill installation scenarios."""

    def test_install_skill_to_cline_native_user(self, tmp_path, monkeypatch):
        """Install skill to Cline user-level (~/.cline/skills/) without config sync."""
        # Setup: Create fake home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        target_root = fake_home / ".cline" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "user-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# User Skill\nA user-level skill for Cline.")

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="cline"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=False,  # User-level install
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to ~/.cline/skills/
        installed_skill = target_root / "user-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/user-skill"


class TestAntigravityIntegration:
    """Test Google Antigravity native skill installation scenarios (Issue #47)."""

    def test_install_skill_to_antigravity_unique_paths(self, tmp_path, monkeypatch):
        """Install skill to Antigravity with unique dual-path configuration."""
        # Setup: Create project structure with .agent/skills/
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".agent" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "antigravity-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text(
            "# Antigravity Skill\nA skill for Google Antigravity."
        )

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="antigravity"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native discovery)
            mock_sync.assert_not_called()

        # Verify: Skill installed to .agent/skills/ (unique path)
        installed_skill = target_root / "antigravity-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/antigravity-skill"


class TestQwenIntegration:
    """Test Qwen Code native skill installation scenarios (Issue #46)."""

    def test_install_skill_to_qwen_native_project(self, tmp_path, monkeypatch):
        """Install skill to Qwen project-level (.qwen/skills/) without config sync."""
        # Setup: Create a Qwen project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".qwen" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "qwen-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Qwen Skill\nA test skill for Qwen Code.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="qwen"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to .qwen/skills/
        installed_skill = target_root / "qwen-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/qwen-skill"


class TestCursorUpgradedIntegration:
    """Test Cursor upgraded to native support scenarios."""

    def test_install_skill_to_cursor_native_project(self, tmp_path, monkeypatch):
        """Install skill to Cursor project-level (.cursor/skills/) without config sync."""
        # Setup: Create a Cursor project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".cursor" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "cursor-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Cursor Skill\nA test skill for Cursor.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="cursor"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (upgraded to native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to .cursor/skills/
        installed_skill = target_root / "cursor-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/cursor-skill"


class TestAgentDetectionPriority:
    """Test agent detection priority follows Issue #49 popularity order."""

    def test_gemini_priority_over_new_agents(self, tmp_path, monkeypatch):
        """Ensure Gemini takes priority over other agents when multiple present."""
        # Setup: Create project with multiple agent directories
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".gemini").mkdir()
        (project_dir / ".openhands").mkdir()
        (project_dir / ".cline").mkdir()
        (project_dir / ".claude").mkdir()

        # Detect agent - Gemini should win (highest priority in Issue #49)
        agent = detect_agent(project_dir)

        assert agent == "gemini"

    def test_opencode_priority_over_openhands(self, tmp_path, monkeypatch):
        """Ensure OpenCode takes priority over OpenHands when both present."""
        # Setup: Create project with OpenCode and OpenHands
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".opencode").mkdir()
        (project_dir / ".openhands").mkdir()

        # Detect agent - OpenCode should win
        agent = detect_agent(project_dir)

        assert agent == "opencode"

    def test_openhands_priority_over_claude(self, tmp_path, monkeypatch):
        """Ensure OpenHands takes priority over Claude when both present."""
        # Setup: Create project with OpenHands and Claude
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".openhands").mkdir()
        (project_dir / ".claude").mkdir()

        # Detect agent - OpenHands should win (higher in Issue #49 order)
        agent = detect_agent(project_dir)

        assert agent == "openhands"


class TestClawdbotUniqueConfiguration:
    """Test Clawdbot's unique project root skills/ directory."""

    def test_install_skill_to_clawdbot_project_root(self, tmp_path, monkeypatch):
        """Install skill to Clawdbot project root skills/ directory."""
        # Setup: Create a project with skills/ in root
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "clawdbot-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Clawdbot Skill\nA test skill for Clawdbot.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="clawdbot"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to skills/ (project root)
        installed_skill = target_root / "clawdbot-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest written
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.skill_id == "local/clawdbot-skill"
