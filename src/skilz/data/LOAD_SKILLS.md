# How to Use Skills

This guide explains how AI coding agents can discover and use skills installed via the skilz CLI.

## What Are Skills?

Skills are reusable instruction sets that extend an AI agent's capabilities. Each skill contains:
- **SKILL.md** - The main instruction file with guidance, examples, and commands
- **Bundled resources** - Scripts, templates, reference docs, and other files

## Discovering Available Skills

Skills are listed in your agent's config file under `<available_skills>`:

```xml
<available_skills>
  <skill>
    <name>plantuml</name>
    <description>Generate PlantUML diagrams from text descriptions</description>
    <location>.claude/skills/plantuml/SKILL.md</location>
  </skill>
</available_skills>
```

## Loading a Skill

When a user's request matches a skill's purpose, load it using the CLI:

```bash
skilz read <skill-name> --agent <your-agent>
```

**Examples:**
- Claude: `skilz read plantuml` (no --agent needed)
- Gemini: `skilz read plantuml --agent gemini`
- Codex: `skilz read plantuml --agent codex`

The command outputs:
1. **Base Directory** - Path for resolving bundled resources
2. **SKILL.md Content** - Full instructions to follow

## Using Bundled Resources

Skills may include additional files. The base directory path tells you where to find them:

```
# Skill: plantuml
# Base Directory: /Users/name/.claude/skills/plantuml
# SKILL.md Path: /Users/name/.claude/skills/plantuml/SKILL.md

[SKILL.md content follows...]
```

To use bundled files, resolve paths relative to the base directory:
- `references/syntax-guide.md` -> `/Users/name/.claude/skills/plantuml/references/syntax-guide.md`
- `scripts/convert.py` -> `/Users/name/.claude/skills/plantuml/scripts/convert.py`

## Step-by-Step Process

1. **Identify** - Check `<available_skills>` for a skill matching the user's request
2. **Load** - Run `skilz read <skill-name> --agent <your-agent>`
3. **Follow** - Execute the instructions in the loaded SKILL.md
4. **Use Resources** - Access bundled scripts/templates via the base directory path

## Lazy Loading

Don't load skills preemptively. Load them only when:
- A user explicitly requests the skill's functionality
- The task clearly matches the skill's description
- You need the skill's specific guidance to complete a request

## Troubleshooting

**Skill not found:**
```bash
skilz list --agent <your-agent>  # See installed skills
skilz install <skill-name> --agent <your-agent>  # Install if missing
```

**Wrong agent directory:**
Each agent has its own skills directory. Use `--agent` to specify which one.

**Broken symlink:**
Run `skilz list` to identify broken skills, then reinstall them.
