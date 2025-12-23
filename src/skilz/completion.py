"""Shell completion support for Skilz CLI."""

import os
import sys
from pathlib import Path

# Zsh completion script
ZSH_COMPLETION = """#compdef skilz

_skilz() {
    local -a commands
    local -a global_options

    global_options=(
        '-V[Show version]'
        '--version[Show version]'
        '-v[Enable verbose output]'
        '--verbose[Enable verbose output]'
        '-y[Skip all confirmation prompts]'
        '--yes-all[Skip all confirmation prompts]'
    )

    commands=(
        'install:Install a skill from the registry'
        'list:List installed skills'
        'update:Update installed skills to latest versions'
        'remove:Remove an installed skill'
        'config:Show or modify configuration'
    )

    _arguments -C \\
        $global_options \\
        ':command:->command' \\
        '*::arg:->args'

    case $state in
        command)
            _describe -t commands 'skilz commands' commands
            ;;
        args)
            case $words[1] in
                install)
                    _arguments \\
                        '--agent[Target agent]:agent:(claude opencode)' \\
                        '--project[Install to project directory]' \\
                        ':skill_id:'
                    ;;
                list)
                    _arguments \\
                        '--agent[Filter by agent type]:agent:(claude opencode)' \\
                        '--project[List project-level skills]' \\
                        '--json[Output as JSON]'
                    ;;
                update)
                    _arguments \\
                        '--agent[Filter by agent type]:agent:(claude opencode)' \\
                        '--project[Update project-level skills]' \\
                        '--dry-run[Show what would be updated]' \\
                        ':skill_id:'
                    ;;
                remove)
                    _arguments \\
                        '--agent[Filter by agent type]:agent:(claude opencode)' \\
                        '--project[Remove project-level skill]' \\
                        '-y[Skip confirmation prompt]' \\
                        '--yes[Skip confirmation prompt]' \\
                        ':skill_id:'
                    ;;
                config)
                    _arguments \\
                        '--init[Run interactive configuration setup]'
                    ;;
            esac
            ;;
    esac
}

_skilz "$@"
"""

# Bash completion script
BASH_COMPLETION = """# Bash completion for skilz

_skilz_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="install list update remove config"
    local global_opts="-V --version -v --verbose -y --yes-all"

    case "${cword}" in
        1)
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- "${cur}"))
            return 0
            ;;
    esac

    case "${words[1]}" in
        install)
            case "${prev}" in
                --agent)
                    COMPREPLY=($(compgen -W "claude opencode" -- "${cur}"))
                    return 0
                    ;;
            esac
            COMPREPLY=($(compgen -W "--agent --project" -- "${cur}"))
            ;;
        list)
            case "${prev}" in
                --agent)
                    COMPREPLY=($(compgen -W "claude opencode" -- "${cur}"))
                    return 0
                    ;;
            esac
            COMPREPLY=($(compgen -W "--agent --project --json" -- "${cur}"))
            ;;
        update)
            case "${prev}" in
                --agent)
                    COMPREPLY=($(compgen -W "claude opencode" -- "${cur}"))
                    return 0
                    ;;
            esac
            COMPREPLY=($(compgen -W "--agent --project --dry-run" -- "${cur}"))
            ;;
        remove)
            case "${prev}" in
                --agent)
                    COMPREPLY=($(compgen -W "claude opencode" -- "${cur}"))
                    return 0
                    ;;
            esac
            COMPREPLY=($(compgen -W "--agent --project -y --yes" -- "${cur}"))
            ;;
        config)
            COMPREPLY=($(compgen -W "--init" -- "${cur}"))
            ;;
    esac
}

complete -F _skilz_completion skilz
"""


def get_shell_type() -> str | None:
    """
    Detect the current shell type.

    Returns:
        Shell type ('zsh', 'bash') or None if unknown.
    """
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    return None


def get_completion_script(shell: str) -> str | None:
    """
    Get the completion script for a shell.

    Args:
        shell: Shell type ('zsh' or 'bash').

    Returns:
        Completion script content or None if unsupported.
    """
    if shell == "zsh":
        return ZSH_COMPLETION
    elif shell == "bash":
        return BASH_COMPLETION
    return None


def get_rc_file(shell: str) -> Path | None:
    """
    Get the RC file path for a shell.

    Args:
        shell: Shell type ('zsh' or 'bash').

    Returns:
        Path to RC file or None if unknown.
    """
    home = Path.home()
    if shell == "zsh":
        return home / ".zshrc"
    elif shell == "bash":
        # macOS uses .bash_profile, Linux uses .bashrc
        bash_profile = home / ".bash_profile"
        bashrc = home / ".bashrc"
        if bash_profile.exists():
            return bash_profile
        return bashrc
    return None


def get_completion_dir(shell: str) -> Path | None:
    """
    Get the directory for completion scripts.

    Args:
        shell: Shell type ('zsh' or 'bash').

    Returns:
        Path to completion directory or None.
    """
    home = Path.home()
    if shell == "zsh":
        # Use ~/.zfunc for zsh completions
        return home / ".zfunc"
    elif shell == "bash":
        # Use ~/.local/share/bash-completion/completions
        return home / ".local" / "share" / "bash-completion" / "completions"
    return None


def install_completion(shell: str) -> tuple[bool, str]:
    """
    Install shell completion for skilz.

    Args:
        shell: Shell type ('zsh' or 'bash').

    Returns:
        Tuple of (success, message).
    """
    script = get_completion_script(shell)
    if not script:
        return False, f"Unsupported shell: {shell}"

    completion_dir = get_completion_dir(shell)
    if not completion_dir:
        return False, f"Cannot determine completion directory for {shell}"

    rc_file = get_rc_file(shell)

    try:
        # Create completion directory
        completion_dir.mkdir(parents=True, exist_ok=True)

        if shell == "zsh":
            # Write completion script
            script_path = completion_dir / "_skilz"
            script_path.write_text(script)

            # Add to .zshrc if not already present
            if rc_file and rc_file.exists():
                rc_content = rc_file.read_text()
                fpath_line = f"fpath=({completion_dir} $fpath)"
                if str(completion_dir) not in rc_content:
                    with open(rc_file, "a") as f:
                        f.write("\n# Skilz CLI completion\n")
                        f.write(f"{fpath_line}\n")
                        f.write("autoload -Uz compinit && compinit\n")
                    return True, f"Added completion to {rc_file}"
                return True, f"Completion script written to {script_path}"

        elif shell == "bash":
            # Write completion script
            script_path = completion_dir / "skilz"
            script_path.write_text(script)

            # Add source to bashrc if not already present
            if rc_file:
                rc_content = rc_file.read_text() if rc_file.exists() else ""
                source_line = f"source {script_path}"
                if str(script_path) not in rc_content:
                    with open(rc_file, "a") as f:
                        f.write("\n# Skilz CLI completion\n")
                        f.write(f"[[ -f {script_path} ]] && {source_line}\n")
                    return True, f"Added completion to {rc_file}"
                return True, f"Completion script written to {script_path}"

        return True, f"Completion script installed for {shell}"

    except OSError as e:
        return False, f"Failed to install completion: {e}"


def print_completion_script(shell: str) -> int:
    """
    Print the completion script for a shell.

    Useful for manual installation or piping to a file.

    Args:
        shell: Shell type ('zsh' or 'bash').

    Returns:
        Exit code (0 for success, 1 for error).
    """
    script = get_completion_script(shell)
    if not script:
        print(f"Error: Unsupported shell: {shell}", file=sys.stderr)
        return 1

    print(script)
    return 0
