"""Tests for the CLI module."""

from unittest.mock import patch

from skilz.cli import create_parser, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_has_version(self):
        """Parser should have --version option."""
        parser = create_parser()
        # Test version action exists
        assert any(action.option_strings == ["-V", "--version"] for action in parser._actions)

    def test_parser_has_verbose(self):
        """Parser should have --verbose option."""
        parser = create_parser()
        args = parser.parse_args(["--verbose", "install", "test/skill"])
        assert args.verbose is True

    def test_verbose_default_is_false(self):
        """Verbose should default to False."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill"])
        assert args.verbose is False

    def test_parser_has_install_command(self):
        """Parser should have install subcommand."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill"])
        assert args.command == "install"
        assert args.skill_id == "test/skill"

    def test_install_command_agent_option(self):
        """Install command should have --agent option."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill", "--agent", "claude"])
        assert args.agent == "claude"

    def test_install_command_opencode_agent(self):
        """Install command should accept opencode agent."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill", "--agent", "opencode"])
        assert args.agent == "opencode"

    def test_install_command_project_option(self):
        """Install command should have --project option."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill", "--project"])
        assert args.project is True

    def test_install_command_combined_options(self):
        """Install command should handle combined options."""
        parser = create_parser()
        args = parser.parse_args(
            ["--verbose", "install", "test/skill", "--agent", "claude", "--project"]
        )
        assert args.verbose is True
        assert args.agent == "claude"
        assert args.project is True
        assert args.skill_id == "test/skill"

    def test_install_command_copy_flag(self):
        """Install command should have --copy flag."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill", "--copy"])
        assert args.copy is True
        assert args.symlink is False

    def test_install_command_symlink_flag(self):
        """Install command should have --symlink flag."""
        parser = create_parser()
        args = parser.parse_args(["install", "test/skill", "--symlink"])
        assert args.symlink is True
        assert args.copy is False

    def test_install_command_file_option(self):
        """Install command should have -f/--file option."""
        parser = create_parser()
        args = parser.parse_args(["install", "-f", "/path/to/skill"])
        assert args.file == "/path/to/skill"
        assert args.skill_id is None

    def test_install_command_git_option(self):
        """Install command should have -g/--git option."""
        parser = create_parser()
        args = parser.parse_args(["install", "-g", "https://github.com/test/skill.git"])
        assert args.git == "https://github.com/test/skill.git"
        assert args.skill_id is None

    def test_parser_has_list_command(self):
        """Parser should have list subcommand."""
        parser = create_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"

    def test_list_command_json_option(self):
        """List command should have --json option."""
        parser = create_parser()
        args = parser.parse_args(["list", "--json"])
        assert args.json is True

    def test_list_command_agent_option(self):
        """List command should have --agent option."""
        parser = create_parser()
        args = parser.parse_args(["list", "--agent", "claude"])
        assert args.agent == "claude"

    def test_list_command_project_option(self):
        """List command should have --project option."""
        parser = create_parser()
        args = parser.parse_args(["list", "--project"])
        assert args.project is True

    def test_parser_has_update_command(self):
        """Parser should have update subcommand."""
        parser = create_parser()
        args = parser.parse_args(["update"])
        assert args.command == "update"
        assert args.skill_id is None

    def test_update_with_skill_id(self):
        """Update command should accept optional skill_id."""
        parser = create_parser()
        args = parser.parse_args(["update", "test/skill"])
        assert args.skill_id == "test/skill"

    def test_update_dry_run(self):
        """Update command should have --dry-run option."""
        parser = create_parser()
        args = parser.parse_args(["update", "--dry-run"])
        assert args.dry_run is True

    def test_update_command_agent_option(self):
        """Update command should have --agent option."""
        parser = create_parser()
        args = parser.parse_args(["update", "--agent", "opencode"])
        assert args.agent == "opencode"

    def test_parser_has_remove_command(self):
        """Parser should have remove subcommand."""
        parser = create_parser()
        args = parser.parse_args(["remove", "test/skill"])
        assert args.command == "remove"
        assert args.skill_id == "test/skill"

    def test_remove_yes_option(self):
        """Remove command should have -y/--yes option."""
        parser = create_parser()
        args = parser.parse_args(["remove", "test/skill", "-y"])
        assert args.yes is True

    def test_remove_yes_long_option(self):
        """Remove command should have --yes option."""
        parser = create_parser()
        args = parser.parse_args(["remove", "test/skill", "--yes"])
        assert args.yes is True

    def test_parser_has_global_yes_all_short(self):
        """Parser should have global -y flag."""
        parser = create_parser()
        args = parser.parse_args(["-y", "list"])
        assert args.yes_all is True

    def test_parser_has_global_yes_all_long(self):
        """Parser should have global --yes-all flag."""
        parser = create_parser()
        args = parser.parse_args(["--yes-all", "list"])
        assert args.yes_all is True

    def test_yes_all_default_is_false(self):
        """Global yes_all should default to False."""
        parser = create_parser()
        args = parser.parse_args(["list"])
        assert args.yes_all is False

    def test_yes_all_works_with_all_commands(self):
        """Global -y flag should work with all commands."""
        parser = create_parser()

        # Test with install
        args = parser.parse_args(["-y", "install", "test/skill"])
        assert args.yes_all is True
        assert args.command == "install"

        # Test with list
        args = parser.parse_args(["-y", "list"])
        assert args.yes_all is True
        assert args.command == "list"

        # Test with update
        args = parser.parse_args(["-y", "update"])
        assert args.yes_all is True
        assert args.command == "update"

        # Test with remove
        args = parser.parse_args(["-y", "remove", "test/skill"])
        assert args.yes_all is True
        assert args.command == "remove"

    def test_parser_has_config_command(self):
        """Parser should have config subcommand."""
        parser = create_parser()
        args = parser.parse_args(["config"])
        assert args.command == "config"

    def test_config_command_init_option(self):
        """Config command should have --init option."""
        parser = create_parser()
        args = parser.parse_args(["config", "--init"])
        assert args.init is True

    def test_config_init_default_is_false(self):
        """Config --init should default to False."""
        parser = create_parser()
        args = parser.parse_args(["config"])
        assert args.init is False

    def test_yes_all_works_with_config(self):
        """Global -y flag should work with config command."""
        parser = create_parser()
        args = parser.parse_args(["-y", "config", "--init"])
        assert args.yes_all is True
        assert args.command == "config"
        assert args.init is True


class TestMain:
    """Tests for main function."""

    def test_no_command_prints_help(self, capsys):
        """No command should print help and return 0."""
        result = main([])
        assert result == 0
        captured = capsys.readouterr()
        assert "skilz" in captured.out.lower() or "usage" in captured.out.lower()

    def test_install_command_calls_handler(self):
        """Install command should call cmd_install."""
        with patch("skilz.commands.install_cmd.cmd_install", return_value=0) as mock:
            result = main(["install", "test/skill"])

        assert result == 0
        mock.assert_called_once()
        args = mock.call_args[0][0]
        assert args.skill_id == "test/skill"

    def test_list_command_calls_handler(self):
        """List command should call cmd_list."""
        with patch("skilz.commands.list_cmd.cmd_list", return_value=0) as mock:
            result = main(["list"])

        assert result == 0
        mock.assert_called_once()

    def test_update_command_calls_handler(self):
        """Update command should call cmd_update."""
        with patch("skilz.commands.update_cmd.cmd_update", return_value=0) as mock:
            result = main(["update"])

        assert result == 0
        mock.assert_called_once()

    def test_remove_command_calls_handler(self):
        """Remove command should call cmd_remove."""
        with patch("skilz.commands.remove_cmd.cmd_remove", return_value=0) as mock:
            result = main(["remove", "test/skill"])

        assert result == 0
        mock.assert_called_once()

    def test_config_command_calls_handler(self):
        """Config command should call cmd_config."""
        with patch("skilz.commands.config_cmd.cmd_config", return_value=0) as mock:
            result = main(["config"])

        assert result == 0
        mock.assert_called_once()

    def test_passes_verbose_flag(self):
        """Verbose flag should be passed to command handlers."""
        with patch("skilz.commands.list_cmd.cmd_list", return_value=0) as mock:
            main(["--verbose", "list"])

        args = mock.call_args[0][0]
        assert args.verbose is True

    def test_install_passes_project_flag(self):
        """Project flag should be passed to install command."""
        with patch("skilz.commands.install_cmd.cmd_install", return_value=0) as mock:
            main(["install", "test/skill", "--project"])

        args = mock.call_args[0][0]
        assert args.project is True

    def test_install_passes_agent_flag(self):
        """Agent flag should be passed to install command."""
        with patch("skilz.commands.install_cmd.cmd_install", return_value=0) as mock:
            main(["install", "test/skill", "--agent", "opencode"])

        args = mock.call_args[0][0]
        assert args.agent == "opencode"

    def test_command_handler_returns_exit_code(self):
        """Main should return the exit code from command handler."""
        with patch("skilz.commands.list_cmd.cmd_list", return_value=42):
            result = main(["list"])

        assert result == 42

    def test_search_command_calls_handler(self):
        """Search command should call cmd_search."""
        with patch("skilz.commands.search_cmd.cmd_search", return_value=0) as mock:
            result = main(["search", "excel"])

        assert result == 0
        mock.assert_called_once()
        args = mock.call_args[0][0]
        assert args.query == "excel"


class TestCommandAliases:
    """Tests for Unix-style command aliases."""

    def test_ls_alias_parses(self):
        """ls should be recognized as a command."""
        parser = create_parser()
        args = parser.parse_args(["ls"])
        assert args.command == "ls"

    def test_ls_calls_list_handler(self):
        """ls command should call cmd_list."""
        with patch("skilz.commands.list_cmd.cmd_list", return_value=0) as mock:
            result = main(["ls"])

        assert result == 0
        mock.assert_called_once()

    def test_ls_accepts_json_option(self):
        """ls command should accept --json option."""
        parser = create_parser()
        args = parser.parse_args(["ls", "--json"])
        assert args.json is True

    def test_ls_accepts_agent_option(self):
        """ls command should accept --agent option."""
        parser = create_parser()
        args = parser.parse_args(["ls", "--agent", "claude"])
        assert args.agent == "claude"

    def test_ls_accepts_project_option(self):
        """ls command should accept --project option."""
        parser = create_parser()
        args = parser.parse_args(["ls", "--project"])
        assert args.project is True

    def test_rm_alias_parses(self):
        """rm should be recognized as a command."""
        parser = create_parser()
        args = parser.parse_args(["rm", "test/skill"])
        assert args.command == "rm"
        assert args.skill_id == "test/skill"

    def test_rm_calls_remove_handler(self):
        """rm command should call cmd_remove."""
        with patch("skilz.commands.remove_cmd.cmd_remove", return_value=0) as mock:
            result = main(["rm", "test/skill"])

        assert result == 0
        mock.assert_called_once()

    def test_rm_accepts_yes_option(self):
        """rm command should accept -y option."""
        parser = create_parser()
        args = parser.parse_args(["rm", "test/skill", "-y"])
        assert args.yes is True

    def test_uninstall_alias_parses(self):
        """uninstall should be recognized as a command."""
        parser = create_parser()
        args = parser.parse_args(["uninstall", "test/skill"])
        assert args.command == "uninstall"
        assert args.skill_id == "test/skill"

    def test_uninstall_calls_remove_handler(self):
        """uninstall command should call cmd_remove."""
        with patch("skilz.commands.remove_cmd.cmd_remove", return_value=0) as mock:
            result = main(["uninstall", "test/skill"])

        assert result == 0
        mock.assert_called_once()

    def test_remove_still_works(self):
        """Original remove command should still work."""
        with patch("skilz.commands.remove_cmd.cmd_remove", return_value=0) as mock:
            result = main(["remove", "test/skill"])

        assert result == 0
        mock.assert_called_once()


class TestSearchCommand:
    """Tests for search command CLI parsing."""

    def test_search_command_parses(self):
        """search should be recognized as a command."""
        parser = create_parser()
        args = parser.parse_args(["search", "excel"])
        assert args.command == "search"
        assert args.query == "excel"

    def test_search_limit_option(self):
        """search should accept --limit option."""
        parser = create_parser()
        args = parser.parse_args(["search", "pdf", "--limit", "5"])
        assert args.limit == 5

    def test_search_limit_short_option(self):
        """search should accept -l option."""
        parser = create_parser()
        args = parser.parse_args(["search", "pdf", "-l", "3"])
        assert args.limit == 3

    def test_search_json_option(self):
        """search should accept --json option."""
        parser = create_parser()
        args = parser.parse_args(["search", "data", "--json"])
        assert args.json is True

    def test_search_default_limit(self):
        """search should default to limit 10."""
        parser = create_parser()
        args = parser.parse_args(["search", "tools"])
        assert args.limit == 10
