"""Update command implementation."""

import argparse
import sys

from skilz.agents import AgentType
from skilz.installer import install_skill
from skilz.registry import lookup_skill
from skilz.scanner import InstalledSkill, find_installed_skill, scan_installed_skills


def check_skill_update(skill: InstalledSkill, verbose: bool = False) -> tuple[bool, str | None]:
    """
    Check if a skill needs an update.

    Args:
        skill: The installed skill to check.
        verbose: If True, print debug info.

    Returns:
        Tuple of (needs_update, new_sha).
        If needs_update is False, new_sha is None.
    """
    try:
        registry_skill = lookup_skill(skill.skill_id, verbose=verbose)

        if skill.manifest.git_sha == registry_skill.git_sha:
            return False, None
        else:
            return True, registry_skill.git_sha

    except Exception:
        # Skill not in registry - can't update
        return False, None


def cmd_update(args: argparse.Namespace) -> int:
    """
    Handle the update command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    verbose = getattr(args, "verbose", False)
    dry_run = getattr(args, "dry_run", False)
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    skill_id: str | None = getattr(args, "skill_id", None)

    try:
        # If specific skill requested, find it
        if skill_id:
            skill = find_installed_skill(
                skill_id,
                agent=agent,
                project_level=project_level,
            )

            if skill is None:
                print(f"Error: Skill '{skill_id}' not found.", file=sys.stderr)
                return 1

            skills = [skill]
        else:
            # Get all installed skills
            skills = scan_installed_skills(
                agent=agent,
                project_level=project_level,
            )

        if not skills:
            print("No skills installed.")
            return 0

        print(f"Checking {len(skills)} installed skill(s)...")

        # Track results
        updated = 0
        up_to_date = 0
        failed = 0
        unknown = 0
        broken = 0

        # Track already-updated canonical paths to avoid duplicate updates
        updated_canonicals: set[str] = set()

        for skill in skills:
            # Handle broken symlinks
            if skill.is_broken:
                print(f"  {skill.skill_id}: broken symlink (target: {skill.canonical_path})")
                broken += 1
                continue

            needs_update, new_sha = check_skill_update(skill, verbose=verbose)

            if new_sha is None and not needs_update:
                # Check if it's unknown (not in registry) vs up-to-date
                try:
                    lookup_skill(skill.skill_id, verbose=False)
                    # Found in registry, must be up-to-date
                    mode_info = f" [{skill.install_mode}]" if verbose else ""
                    print(f"  {skill.skill_id}: up-to-date ({skill.git_sha_short}){mode_info}")
                    up_to_date += 1
                except Exception:
                    # Not in registry
                    print(f"  {skill.skill_id}: unknown (not in registry)")
                    unknown += 1
                continue

            if needs_update:
                old_sha = skill.git_sha_short
                new_sha_short = new_sha[:8] if new_sha else "?"
                is_symlink = skill.install_mode == "symlink"

                # For symlinks, check if canonical was already updated
                if is_symlink and skill.canonical_path:
                    canonical_key = str(skill.canonical_path)
                    if canonical_key in updated_canonicals:
                        # Canonical already updated, symlink auto-reflects
                        mode_info = " [symlink - auto-updated]" if verbose else ""
                        print(f"  {skill.skill_id}: updated via canonical{mode_info}")
                        updated += 1
                        continue

                mode_info = f" [{skill.install_mode}]" if verbose else ""

                if dry_run:
                    msg = f"  {skill.skill_id}: would update {old_sha} -> {new_sha_short}"
                    print(f"{msg}{mode_info}")
                    updated += 1
                else:
                    msg = f"  {skill.skill_id}: updating {old_sha} -> {new_sha_short}"
                    print(f"{msg}{mode_info}")

                    try:
                        # Pass mode to preserve install mode during update
                        install_skill(
                            skill_id=skill.skill_id,
                            agent=skill.agent,
                            project_level=skill.project_level,
                            verbose=verbose,
                            mode=skill.install_mode,
                        )
                        updated += 1

                        # Track updated canonical for symlinked skills
                        if is_symlink and skill.canonical_path:
                            updated_canonicals.add(str(skill.canonical_path))

                    except Exception as e:
                        print(f"    Failed: {e}", file=sys.stderr)
                        failed += 1

        # Summary
        print()
        if dry_run:
            print(f"Would update {updated} skill(s), {up_to_date} already up-to-date", end="")
        else:
            print(f"Updated {updated} skill(s), {up_to_date} already up-to-date", end="")

        if failed > 0:
            print(f", {failed} failed", end="")
        if unknown > 0:
            print(f", {unknown} not in registry", end="")
        if broken > 0:
            print(f", {broken} broken", end="")
        print()

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
