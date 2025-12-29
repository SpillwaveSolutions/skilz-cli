# Plan: Multi-Skills in Repository Support

**Branch:** `fix/multi-skills-in-repo`
**Feature:** Support installing specific skills from multi-skill git repositories

## Problem Statement

When cloning `https://github.com/The1Studio/theone-training-skills`, skilz reports "No skills found" despite the repo containing 38+ skills in `.claude/skills/`.

**Root Cause:** The hidden directory filter at `git_install.py:79` is too aggressive:
```python
if any(part.startswith(".") for part in skill_md.parts):
    continue
```
This skips `.git/` (correct) but also skips `.claude/` and `.opencode/` (incorrect - these contain valid skills).

## Scope

1. **Bug Fix:** Fix skill discovery to NOT skip `.claude/` and `.opencode/` directories
2. **Feature:** Add `--skill <name>` flag to pre-select a specific skill
3. **Enhancement:** Support marketplace.json as alternative skill discovery

## Implementation Plan

### Phase 1: Fix Hidden Directory Filter (Bug Fix)

**File:** `src/skilz/git_install.py:64-97` (`find_skills_in_repo`)

**Change:** Replace overly-broad hidden directory filter with specific `.git` exclusion:

```python
# BEFORE (line 79)
if any(part.startswith(".") for part in skill_md.parts):
    continue

# AFTER
# Only skip .git directory, allow .claude/.opencode
relative_parts = skill_md.relative_to(repo_path).parts
if ".git" in relative_parts:
    continue
```

### Phase 2: Add --skill Flag

**Files:**
- `src/skilz/cli.py` - Add argument
- `src/skilz/commands/install_cmd.py` - Pass to git_install
- `src/skilz/git_install.py` - Filter by skill name

**CLI Changes (`cli.py` after line 147):**
```python
install_parser.add_argument(
    "--skill",
    metavar="NAME",
    help="Install specific skill by name (with -g/--git)",
)
```

**Install Command (`install_cmd.py`):**
```python
skill_name = getattr(args, "skill", None)
return install_from_git(
    ...,
    skill_name=skill_name,  # NEW
)
```

**Git Install (`git_install.py`):**
```python
def install_from_git(
    ...,
    skill_name: str | None = None,  # NEW parameter
) -> int:
    ...
    # After finding skills, if --skill specified:
    if skill_name:
        matching = [s for s in skills if s.skill_name == skill_name]
        if not matching:
            print(f"Error: Skill '{skill_name}' not found. Available: {', '.join(s.skill_name for s in skills)}")
            return 1
        selected = matching
    else:
        selected = prompt_skill_selection(skills, ...)
```

### Phase 3: Support Official Plugin Marketplace Discovery

**Research Source:** Claude Code Official Docs (https://code.claude.com/docs/en/plugin-marketplaces)

**File Location:** `.claude-plugin/marketplace.json` (NOT at repo root!)

**Official Schema:**
```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Your Name",
    "email": "user@example.com"
  },
  "description": "Description",
  "strict": true,
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/name",
      "description": "...",
      "keywords": ["tag1", "tag2"]
    }
  ]
}
```

**New Function:**
```python
import json

def find_skills_from_marketplace(repo_path: Path) -> list[GitSkillInfo]:
    """
    Find skills from official Claude plugin marketplace.json.

    Looks for .claude-plugin/marketplace.json per official Claude Code docs.
    Falls back to checking root marketplace.json for compatibility.
    """
    marketplace_paths = [
        repo_path / ".claude-plugin" / "marketplace.json",
        repo_path / "marketplace.json",
    ]

    for marketplace_path in marketplace_paths:
        if not marketplace_path.exists():
            continue

        try:
            data = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        skills = []
        for plugin in data.get("plugins", []):
            source = plugin.get("source", "")

            if isinstance(source, str) and source.startswith("./"):
                skill_path = repo_path / source.lstrip("./")
            elif isinstance(source, str):
                skill_path = repo_path / source
            else:
                continue

            if (skill_path / "SKILL.md").exists():
                skills.append(GitSkillInfo(
                    skill_name=plugin.get("name", skill_path.name),
                    skill_path=skill_path,
                    relative_path=str(skill_path.relative_to(repo_path)),
                ))

        if skills:
            return skills

    return []
```

## Files to Modify

| File | Changes |
|------|---------|
| `src/skilz/cli.py` | Add `--skill` argument (~5 lines) |
| `src/skilz/commands/install_cmd.py` | Pass `skill_name` parameter (~3 lines) |
| `src/skilz/git_install.py` | Fix filter, add skill_name filter, add marketplace support (~40 lines) |

## Test Cases

1. **Hidden dir fix:** Clone repo with skills in `.claude/skills/` - should find them
2. **--skill flag:** `skilz install -g <url> --skill theone-cocos-standards` - installs specific skill
3. **--skill not found:** `skilz install -g <url> --skill nonexistent` - shows error with available names
4. **Multiple skills menu:** `skilz install -g <url>` without --skill - shows selection menu
5. **Single skill auto-install:** Repo with one skill - auto-installs without menu
6. **Official marketplace:** Repo with `.claude-plugin/marketplace.json` - discovers skills from `plugins` array
7. **Root marketplace fallback:** Repo with `marketplace.json` at root - discovers skills
8. **Marketplace source parsing:** Handles `"source": "./plugins/skill-name"` format correctly

## Acceptance Criteria

- [ ] `skilz install -g https://github.com/The1Studio/theone-training-skills --agent universal` shows skill menu
- [ ] `skilz install -g https://github.com/The1Studio/theone-training-skills --skill theone-cocos-standards --agent universal` installs specific skill
- [ ] Skills in `.claude/skills/` and `.opencode/skills/` are discovered
- [ ] `.claude-plugin/marketplace.json` skills are discovered (official location)
- [ ] `marketplace.json` at repo root is used as fallback
- [ ] `plugins` array with `name`/`source` fields are parsed correctly
- [ ] All existing tests pass
- [ ] New tests cover multi-skill scenarios (80%+ coverage)
