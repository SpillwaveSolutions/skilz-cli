"""Tests for the completion module."""

from pathlib import Path

from skilz.completion import (
    BASH_COMPLETION,
    ZSH_COMPLETION,
    get_completion_dir,
    get_completion_script,
    get_rc_file,
    get_shell_type,
    install_completion,
    print_completion_script,
)


class TestGetShellType:
    """Tests for get_shell_type function."""

    def test_detect_zsh(self, monkeypatch):
        """Should detect zsh shell."""
        monkeypatch.setenv("SHELL", "/bin/zsh")
        assert get_shell_type() == "zsh"

    def test_detect_bash(self, monkeypatch):
        """Should detect bash shell."""
        monkeypatch.setenv("SHELL", "/bin/bash")
        assert get_shell_type() == "bash"

    def test_detect_unknown(self, monkeypatch):
        """Should return None for unknown shell."""
        monkeypatch.setenv("SHELL", "/bin/fish")
        assert get_shell_type() is None

    def test_detect_no_shell_var(self, monkeypatch):
        """Should return None when SHELL not set."""
        monkeypatch.delenv("SHELL", raising=False)
        assert get_shell_type() is None


class TestGetCompletionScript:
    """Tests for get_completion_script function."""

    def test_get_zsh_script(self):
        """Should return zsh completion script."""
        script = get_completion_script("zsh")
        assert script == ZSH_COMPLETION
        assert "#compdef skilz" in script

    def test_get_bash_script(self):
        """Should return bash completion script."""
        script = get_completion_script("bash")
        assert script == BASH_COMPLETION
        assert "_skilz_completion" in script

    def test_get_unknown_returns_none(self):
        """Should return None for unknown shell."""
        assert get_completion_script("fish") is None


class TestGetRcFile:
    """Tests for get_rc_file function."""

    def test_zsh_rc_file(self, tmp_path, monkeypatch):
        """Should return .zshrc for zsh."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        rc = get_rc_file("zsh")
        assert rc == tmp_path / ".zshrc"

    def test_bash_rc_file_bashrc(self, tmp_path, monkeypatch):
        """Should return .bashrc when .bash_profile doesn't exist."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        rc = get_rc_file("bash")
        assert rc == tmp_path / ".bashrc"

    def test_bash_rc_file_bash_profile(self, tmp_path, monkeypatch):
        """Should return .bash_profile when it exists."""
        (tmp_path / ".bash_profile").touch()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        rc = get_rc_file("bash")
        assert rc == tmp_path / ".bash_profile"

    def test_unknown_returns_none(self):
        """Should return None for unknown shell."""
        assert get_rc_file("fish") is None


class TestGetCompletionDir:
    """Tests for get_completion_dir function."""

    def test_zsh_completion_dir(self, tmp_path, monkeypatch):
        """Should return .zfunc for zsh."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        completion_dir = get_completion_dir("zsh")
        assert completion_dir == tmp_path / ".zfunc"

    def test_bash_completion_dir(self, tmp_path, monkeypatch):
        """Should return bash-completion dir for bash."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        completion_dir = get_completion_dir("bash")
        assert completion_dir == tmp_path / ".local" / "share" / "bash-completion" / "completions"

    def test_unknown_returns_none(self):
        """Should return None for unknown shell."""
        assert get_completion_dir("fish") is None


class TestInstallCompletion:
    """Tests for install_completion function."""

    def test_install_unsupported_shell(self):
        """Should fail for unsupported shell."""
        success, message = install_completion("fish")
        assert success is False
        assert "Unsupported shell" in message

    def test_install_zsh_completion(self, tmp_path, monkeypatch):
        """Should install zsh completion."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create .zshrc
        zshrc = tmp_path / ".zshrc"
        zshrc.write_text("# existing content\n")

        success, message = install_completion("zsh")

        assert success is True
        assert "Added completion to" in message or "Completion script written" in message

        # Check script was written
        script_path = tmp_path / ".zfunc" / "_skilz"
        assert script_path.exists()
        assert "#compdef skilz" in script_path.read_text()

    def test_install_bash_completion(self, tmp_path, monkeypatch):
        """Should install bash completion."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create .bashrc
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text("# existing content\n")

        success, message = install_completion("bash")

        assert success is True

        # Check script was written
        script_path = tmp_path / ".local" / "share" / "bash-completion" / "completions" / "skilz"
        assert script_path.exists()
        assert "_skilz_completion" in script_path.read_text()

    def test_install_zsh_idempotent(self, tmp_path, monkeypatch):
        """Should not duplicate entries in .zshrc."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create .zshrc
        zshrc = tmp_path / ".zshrc"
        zshrc.write_text("# existing content\n")

        # Install twice
        install_completion("zsh")
        install_completion("zsh")

        # Check .zshrc doesn't have duplicate entries
        content = zshrc.read_text()
        assert content.count(".zfunc") <= 2  # May appear in fpath and comment


class TestPrintCompletionScript:
    """Tests for print_completion_script function."""

    def test_print_zsh(self, capsys):
        """Should print zsh completion script."""
        result = print_completion_script("zsh")
        assert result == 0
        captured = capsys.readouterr()
        assert "#compdef skilz" in captured.out

    def test_print_bash(self, capsys):
        """Should print bash completion script."""
        result = print_completion_script("bash")
        assert result == 0
        captured = capsys.readouterr()
        assert "_skilz_completion" in captured.out

    def test_print_unknown_fails(self, capsys):
        """Should fail for unknown shell."""
        result = print_completion_script("fish")
        assert result == 1
        captured = capsys.readouterr()
        assert "Unsupported shell" in captured.err
