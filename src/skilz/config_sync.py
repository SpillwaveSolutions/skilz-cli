"""Config file synchronization for agent skill references.

This module handles updating agent configuration files (CLAUDE.md, GEMINI.md, etc.)
with skill references when skills are installed, following the agentskills.io standard.

See: https://agentskills.io/integrate-skills#injecting-into-context
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from skilz.agent_registry import AgentConfig, get_registry

# Markers for the managed section in config files (agentskills.io standard)
SECTION_START = "<!-- SKILLS_TABLE_START -->"
SECTION_END = "<!-- SKILLS_TABLE_END -->"


def _generate_usage_template(
    agent_name: str,
    native_support: str,
    force_extended: bool = False,
) -> str:
    """Generate agent-specific usage template.

    Args:
        agent_name: The agent identifier (e.g., "claude", "gemini")
        native_support: The native_skill_support value ("all", "home", "none")
        force_extended: If True, always include extended step-by-step instructions
                       (used when --force-config is specified)

    Returns:
        Formatted XML usage block with correct invocation command
    """
    # Claude with native "all" support doesn't need --agent flag
    if agent_name == "claude" and native_support == "all":
        invocation = 'Bash("skilz read <skill-name>")'
    else:
        invocation = f'Bash("skilz read <skill-name> --agent {agent_name}")'

    # Extended step-by-step instructions for agents without native support OR when forced
    if native_support == "none" or force_extended:
        extra_steps = """
Step-by-step process:
1. Identify a skill from <available_skills> that matches the user's request
2. Run the command above to load the skill's SKILL.md content
3. Follow the instructions in the loaded skill content
4. Skills may include bundled scripts, templates, and references
"""
    else:
        extra_steps = ""

    # Usage notes ONLY for agents without native support (not affected by force_extended)
    if native_support == "none":
        usage_notes = """
Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
"""
    else:
        usage_notes = ""

    return f"""<usage>
When users ask you to perform tasks, check if any of the available skills
below can help complete the task more effectively.

How to use skills:
- Invoke: {invocation}
- The skill content will load with detailed instructions
- Base directory provided in output for resolving bundled resources
{extra_steps}{usage_notes}</usage>"""


@dataclass
class SkillReference:
    """Information needed to create a skill reference in a config file."""

    skill_id: str
    skill_name: str
    skill_path: Path
    description: str = ""


@dataclass
class ConfigSyncResult:
    """Result of a config file sync operation."""

    config_file: Path
    agent_name: str
    updated: bool
    created: bool
    error: str | None = None


def _extract_description_from_skill(skill_path: Path) -> str:
    """Extract the description from a SKILL.md file.

    Looks for the 'description' field in the YAML frontmatter.

    Args:
        skill_path: Path to the skill directory.

    Returns:
        The description string, or empty string if not found.
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ""

    try:
        content = skill_md.read_text()

        # Check for YAML frontmatter
        if content.startswith("---"):
            # Find the closing ---
            end_idx = content.find("---", 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx]
                # Simple regex to extract description
                desc_pattern = r"description:\s*['\"]?(.+?)['\"]?\s*$"
                match = re.search(desc_pattern, frontmatter, re.MULTILINE)
                if match:
                    return match.group(1).strip()

        # Fallback: look for first paragraph after title
        lines = content.split("\n")
        in_paragraph = False
        paragraph: list[str] = []
        for line in lines:
            if line.startswith("#"):
                in_paragraph = True
                continue
            if in_paragraph:
                if line.strip() == "":
                    if paragraph:
                        break
                else:
                    paragraph.append(line.strip())

        if paragraph:
            return " ".join(paragraph)[:200]  # Limit to 200 chars

    except OSError:
        pass

    return ""


def detect_project_config_files(
    project_dir: Path,
    agent: str | None = None,
) -> list[tuple[str, Path]]:
    """Detect which agent config files exist in the project directory.

    Args:
        project_dir: The project directory to scan.
        agent: If specified, only check this agent's config files.
               If None, check all registered agents.

    Returns:
        List of (agent_name, config_path) tuples for existing config files.
    """
    registry = get_registry()
    results: list[tuple[str, Path]] = []

    if agent:
        # Only check the specified agent - return only existing files
        # If none exist, sync_skill_to_configs will create the first one
        agent_config = registry.get(agent)
        if agent_config:
            for config_file in agent_config.config_files:
                config_path = project_dir / config_file
                if config_path.exists():
                    results.append((agent, config_path))
    else:
        # Check all agents for existing config files
        for agent_name in registry.list_agents():
            agent_config = registry.get(agent_name)
            if agent_config is None:
                continue

            for config_file in agent_config.config_files:
                config_path = project_dir / config_file
                if config_path.exists():
                    results.append((agent_name, config_path))

    return results


def format_skill_element(
    skill: SkillReference,
    project_dir: Path | None = None,
) -> str:
    """Format a skill as an XML element following agentskills.io standard.

    Args:
        skill: The skill to format.
        project_dir: Project directory for calculating relative paths.

    Returns:
        Formatted skill XML element.
    """
    # Calculate relative path from project root to skill
    if project_dir:
        try:
            skill_rel_path = skill.skill_path.relative_to(project_dir)
        except ValueError:
            skill_rel_path = skill.skill_path
    else:
        skill_rel_path = skill.skill_path

    # Get description - either from the SkillReference or extract from SKILL.md
    description = skill.description
    if not description:
        description = _extract_description_from_skill(skill.skill_path)
    if not description:
        description = f"Skill: {skill.skill_id}"

    return f"""<skill>
<name>{skill.skill_name}</name>
<description>{description}</description>
<location>{skill_rel_path}/SKILL.md</location>
</skill>"""


def _build_skills_section(
    skills: list[SkillReference],
    project_dir: Path | None = None,
    agent_name: str = "claude",
    native_support: str = "all",
    force_extended: bool = False,
) -> str:
    """Build the complete skills section content following agentskills.io standard.

    Args:
        skills: List of skills to include.
        project_dir: Project directory for calculating relative paths.
        agent_name: The agent identifier for generating correct invocation.
        native_support: The agent's native_skill_support level.
        force_extended: If True, include extended instructions (--force-config).

    Returns:
        Complete section content including markers.
    """
    skill_elements = []
    for skill in sorted(skills, key=lambda s: s.skill_name):
        skill_elements.append(format_skill_element(skill, project_dir))

    skills_xml = "\n\n".join(skill_elements)
    usage_template = _generate_usage_template(agent_name, native_support, force_extended)

    return f"""<skills_system priority="1">

## Available Skills

{SECTION_START}
{usage_template}

<available_skills>

{skills_xml}

</available_skills>
{SECTION_END}

</skills_system>"""


def _parse_existing_skills(content: str) -> list[tuple[str, str, str]]:
    """Parse existing skills from a config file's skilz section.

    Args:
        content: The file content.

    Returns:
        List of (skill_name, description, location) tuples found in the managed section.
    """
    skills: list[tuple[str, str, str]] = []

    # Find the managed section
    start_match = re.search(re.escape(SECTION_START), content)
    end_match = re.search(re.escape(SECTION_END), content)

    if not start_match or not end_match:
        return skills

    section = content[start_match.end() : end_match.start()]

    # Extract skill elements
    skill_pattern = (
        r"<skill>\s*<name>([^<]+)</name>\s*"
        r"<description>([^<]*)</description>\s*"
        r"<location>([^<]+)</location>\s*</skill>"
    )
    for match in re.finditer(skill_pattern, section, re.DOTALL):
        skills.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))

    return skills


def _merge_skill_into_section(
    existing_section: str,
    new_skill: SkillReference,
    project_dir: Path | None = None,
    agent_name: str = "claude",
    native_support: str = "all",
    force_extended: bool = False,
) -> str:
    """Merge a new skill into an existing skills section.

    Args:
        existing_section: The existing section content.
        new_skill: The new skill to add.
        project_dir: Project directory for calculating relative paths.
        agent_name: The agent identifier for generating correct invocation.
        native_support: The agent's native_skill_support level.
        force_extended: If True, include extended instructions (--force-config).

    Returns:
        Updated section content.
    """
    # Parse existing skills
    existing_skills = _parse_existing_skills(existing_section)

    # Check if skill already exists
    for name, _, _ in existing_skills:
        if name == new_skill.skill_name:
            return existing_section  # Already exists, no change

    # Build all skill elements
    skill_elements = []

    # Add existing skills
    for name, description, location in existing_skills:
        skill_elements.append(f"""<skill>
<name>{name}</name>
<description>{description}</description>
<location>{location}</location>
</skill>""")

    # Add new skill
    skill_elements.append(format_skill_element(new_skill, project_dir))

    # Sort by skill name
    def _get_skill_name(elem: str) -> str:
        m = re.search(r"<name>([^<]+)</name>", elem)
        return m.group(1) if m else ""

    skill_elements.sort(key=_get_skill_name)

    skills_xml = "\n\n".join(skill_elements)
    usage_template = _generate_usage_template(agent_name, native_support, force_extended)

    return f"""<skills_system priority="1">

## Available Skills

{SECTION_START}
{usage_template}

<available_skills>

{skills_xml}

</available_skills>
{SECTION_END}

</skills_system>"""


def update_config_file(
    config_path: Path,
    skill: SkillReference,
    agent_config: AgentConfig,
    project_dir: Path | None = None,
    create_if_missing: bool = True,
    force_extended: bool = False,
) -> ConfigSyncResult:
    """Update a config file with a skill reference.

    This function is idempotent - it won't duplicate skill entries.

    Args:
        config_path: Path to the config file.
        skill: The skill to add.
        agent_config: The agent configuration.
        project_dir: Project directory for calculating relative paths.
        create_if_missing: If True, create the config file if it doesn't exist.
        force_extended: If True, include extended instructions (--force-config).

    Returns:
        ConfigSyncResult indicating what happened.
    """
    created = False
    updated = False

    try:
        # Read existing content or start fresh
        if config_path.exists():
            content = config_path.read_text()
        elif create_if_missing:
            content = f"# {config_path.name}\n\n"
            created = True
        else:
            return ConfigSyncResult(
                config_file=config_path,
                agent_name=agent_config.name,
                updated=False,
                created=False,
                error="Config file does not exist",
            )

        # Check if skill is already listed
        existing_skills = _parse_existing_skills(content)
        skill_names = [s[0] for s in existing_skills]
        if skill.skill_name in skill_names:
            return ConfigSyncResult(
                config_file=config_path,
                agent_name=agent_config.name,
                updated=False,
                created=False,
            )

        # Check for the outer skills_system tag
        system_start = re.search(r"<skills_system[^>]*>", content)
        system_end = re.search(r"</skills_system>", content)

        if system_start and system_end:
            # Update existing section
            existing_section = content[system_start.start() : system_end.end()]
            new_section = _merge_skill_into_section(
                existing_section,
                skill,
                project_dir,
                agent_name=agent_config.name,
                native_support=agent_config.native_skill_support,
                force_extended=force_extended,
            )

            new_content = (
                content[: system_start.start()] + new_section + content[system_end.end() :]
            )
            updated = True
        else:
            # Append new section at end
            new_section = _build_skills_section(
                [skill],
                project_dir,
                agent_name=agent_config.name,
                native_support=agent_config.native_skill_support,
                force_extended=force_extended,
            )
            if not content.endswith("\n"):
                content += "\n"
            new_content = content + "\n" + new_section + "\n"
            updated = True

        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write updated content
        config_path.write_text(new_content)

        return ConfigSyncResult(
            config_file=config_path,
            agent_name=agent_config.name,
            updated=updated,
            created=created,
        )

    except OSError as e:
        return ConfigSyncResult(
            config_file=config_path,
            agent_name=agent_config.name,
            updated=False,
            created=False,
            error=str(e),
        )


def sync_skill_to_configs(
    skill: SkillReference,
    project_dir: Path,
    agent: str | None = None,
    verbose: bool = False,
    target_files: tuple[str, ...] | None = None,  # SKILZ-50: Custom file override
    force_extended: bool = False,
) -> list[ConfigSyncResult]:
    """Sync a skill reference to all relevant config files.

    Args:
        skill: The skill to sync.
        project_dir: The project directory.
        agent: If specified, only sync to this agent's config files.
               If None, sync to all agent config files that exist.
        verbose: If True, print progress information.
        target_files: Optional tuple of config file names to update (e.g., ("GEMINI.md",)).
                     If provided, overrides auto-detection and only updates these files.
                     The agent parameter is ignored when target_files is specified.
        force_extended: If True, include extended instructions (--force-config).

    Returns:
        List of ConfigSyncResult for each config file processed.
    """
    results: list[ConfigSyncResult] = []
    registry = get_registry()

    # SKILZ-50: Use custom target files if provided
    if target_files:
        # Convert file names to (agent, path) tuples
        # For custom files, try to match to known agents, otherwise use "universal"
        from skilz.agent_registry import get_builtin_agents

        config_files: list[tuple[str, Path]] = []
        all_agents = get_builtin_agents()

        for file_name in target_files:
            config_path = project_dir / file_name
            # Try to find agent that owns this config file
            agent_owner = None
            for agent_name, agent_cfg in all_agents.items():
                if file_name in agent_cfg.config_files:
                    agent_owner = agent_name
                    break
            # If no owner found, use "universal" as fallback
            if not agent_owner:
                agent_owner = "universal"
            config_files.append((agent_owner, config_path))
    else:
        # Original behavior: auto-detect config files
        config_files = detect_project_config_files(project_dir, agent)

        if not config_files and agent:
            # Agent specified but no config files found - create the first one
            agent_config = registry.get(agent)
            if agent_config and agent_config.config_files:
                first_config = project_dir / agent_config.config_files[0]
                config_files = [(agent, first_config)]

    for agent_name, config_path in config_files:
        agent_config = registry.get(agent_name)
        if agent_config is None:
            continue

        if verbose:
            action = "Creating" if not config_path.exists() else "Updating"
            print(f"  {action} {config_path}...")

        result = update_config_file(
            config_path=config_path,
            skill=skill,
            agent_config=agent_config,
            project_dir=project_dir,
            create_if_missing=(agent is not None),  # Only create if agent specified
            force_extended=force_extended,
        )
        results.append(result)

        if verbose and result.error:
            print(f"    Error: {result.error}")

    return results
