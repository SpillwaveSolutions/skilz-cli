# Implementation Plan: `-g/--git` Install from Git URL

## Overview

Implement `skilz install -g <git-url>` to install skills directly from git repositories without requiring registry entries.

## User Requirements

1. Clone repo to temp directory
2. Find all directories with SKILL.md files
3. Parse skill names from SKILL.md frontmatter
4. Present numbered menu for selection (unless `--all` specified)
5. Install selected skill(s)
6. Clean up temp directory

## CLI Changes

### New Flag in cli.py

Add `--all` flag to install command:
```python
install_parser.add_argument(
    "--all",
    action="store_true",
    help="Install all skills found in repository (with -g)",
)
```

## Implementation

### File: `src/skilz/git_install.py` (NEW)

Create new module with these functions:

```python
def find_skills_in_repo(repo_path: Path) -> list[SkillInfo]:
    """
    Find all SKILL.md files in a cloned repository.

    Returns list of SkillInfo with:
    - skill_name: from frontmatter 'name:' field or directory name
    - skill_path: relative path to skill directory
    - display_name: for menu display
    """

def parse_skill_name(skill_md_path: Path) -> str:
    """
    Parse skill name from SKILL.md frontmatter.

    Looks for 'name:' field in YAML frontmatter.
    Falls back to parent directory name.
    """

def prompt_skill_selection(skills: list[SkillInfo], yes_all: bool = False) -> list[SkillInfo]:
    """
    Display numbered menu for skill selection.

    Format:
      Found 3 skills in repository:
        [1] skill-name-1
        [2] skill-name-2
        [3] skill-name-3
        [A] Install all
        [Q] Cancel

      Select skill(s) [1-3, A, Q]:

    If yes_all=True, returns all skills without prompting.
    """

def install_from_git(
    git_url: str,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    install_all: bool = False,
    yes_all: bool = False,
) -> int:
    """
    Main entry point for -g/--git installation.

    Steps:
    1. Clone repo to temp directory (shallow clone)
    2. Find all skills (SKILL.md files)
    3. If no skills found, error
    4. If one skill found, install it
    5. If multiple skills:
       - If --all or yes_all: install all
       - Else: show menu, install selected
    6. Clean up temp directory
    """
```

### File: `src/skilz/commands/install_cmd.py` (MODIFY)

Replace lines 69-71:
```python
if git_url is not None:
    from skilz.git_install import install_from_git

    install_all = getattr(args, "all", False)
    yes_all = getattr(args, "yes_all", False)

    return install_from_git(
        git_url=git_url,
        agent=agent,
        project_level=project_level,
        verbose=verbose,
        mode=mode,
        install_all=install_all,
        yes_all=yes_all,
    )
```

## Data Structures

### SkillInfo for Git Install

```python
@dataclass
class GitSkillInfo:
    """Information about a skill found in a git repo."""
    skill_name: str       # From frontmatter or directory name
    skill_path: Path      # Absolute path to skill directory in temp clone
    relative_path: str    # Relative path from repo root
```

## Menu Format

```
Found 3 skills in repository:

  [1] extracting-keywords
  [2] pdf-tools
  [3] web-artifacts-builder
  [A] Install all
  [Q] Cancel

Select skill(s) [1-3, A, Q]:
```

- Single number: Install that skill
- Multiple numbers (comma-separated): `1,3` installs skills 1 and 3
- `A` or `all`: Install all skills
- `Q` or `q` or Enter: Cancel

## Manifest for Git-Installed Skills

```yaml
installed_at: 2025-12-27T10:00:00Z
skill_id: git/<skill_name>
git_repo: https://github.com/user/repo.git
skill_path: /path/to/skill
git_sha: <HEAD sha at time of clone>
skilz_version: 1.2.0
install_mode: copy
```

## Error Handling

| Scenario | Error Message |
|----------|---------------|
| Git clone fails | `Git clone failed: <stderr>` |
| No SKILL.md found | `No skills found in repository. Skills must contain a SKILL.md file.` |
| Invalid selection | `Invalid selection. Please enter a number, 'A' for all, or 'Q' to cancel.` |
| User cancels | Exit with code 0, no message |

## Test Cases

1. Single skill repo - auto-installs without menu
2. Multi-skill repo - shows menu
3. Multi-skill repo with `--all` - installs all without menu
4. Multi-skill repo with `-y` - installs all without menu
5. Invalid git URL - shows error
6. Empty repo (no SKILL.md) - shows error
7. SSH URL format (git@github.com:...)
8. HTTPS URL format (https://github.com/...)

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/skilz/git_install.py` | CREATE - new module |
| `src/skilz/cli.py` | MODIFY - add `--all` flag |
| `src/skilz/commands/install_cmd.py` | MODIFY - call git_install |
| `tests/test_git_install.py` | CREATE - unit tests |

## Dependencies

Uses existing modules:
- `link_ops.clone_git_repo()` - clone to temp dir
- `link_ops.cleanup_temp_dir()` - cleanup
- `installer.install_local_skill()` - actual installation
- `git_ops` patterns for frontmatter parsing

## Exit Criteria

1. `skilz install -g https://github.com/user/skill-repo` works
2. `skilz install -g git@github.com:user/skill.git` works
3. Multi-skill repos show selection menu
4. `--all` flag installs all skills without prompting
5. `-y` flag also installs all without prompting
6. Temp directories are cleaned up on success and failure
7. Tests cover all scenarios
