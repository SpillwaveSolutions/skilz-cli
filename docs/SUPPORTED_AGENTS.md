# Supported AI Coding Agents

Skilz supports **30+ AI coding agents** from the [AGENTS.md](https://agents.md/) ecosystem, following the [agentskills.io](https://agentskills.io/) standard for skill format and installation.

## Agent Categories

### Tier 1: Full Native Support (User + Project Level)

These agents have dedicated skill directories and full native support for both user-level and project-level installations.

#### Gemini CLI
**Provider:** Google  
**Website:** [ai.google.dev](https://ai.google.dev)  
**Description:** Gemini CLI is a command-line client for interacting with Google's Gemini models, including coding workflows and agents. It provides scriptable, model-centric interface for code generation and repository modification.  
**Skill Directory:** `~/.gemini/skills/` (user-level), `.gemini/skills/` (project-level)  
**Notes:** Requires `experimental.skills` plugin, reads GEMINI.md via `.gemini/settings.json`

#### OpenCode CLI
**Provider:** OpenCode  
**Website:** [opencode.dev](https://opencode.dev)  
**Description:** OpenCode CLI is a terminal-based coding assistant that provides AI-powered code generation and editing directly in your command line.  
**Skill Directory:** `~/.config/opencode/skill/` (user-level), `.opencode/skill/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### OpenHands
**Provider:** OpenHands  
**Website:** [openhands.ai](https://openhands.ai)  
**Description:** OpenHands is an autonomous AI software engineer that can execute complex engineering tasks with minimal supervision.  
**Skill Directory:** `~/.openhands/skills/` (user-level), `.openhands/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Claude Code
**Provider:** Anthropic  
**Website:** [claude.ai/code](https://claude.ai/code)  
**Description:** Claude Code is Anthropic's native coding assistant with deep integration into their AI platform. It provides intelligent code completion, refactoring, and multi-file editing capabilities.  
**Skill Directory:** `~/.claude/skills/` (user-level), `.claude/skills/` (project-level)  
**Notes:** Uses CLAUDE.md config file (not AGENTS.md)

#### Cline
**Provider:** Cline  
**Website:** [cline.ai](https://cline.ai)  
**Description:** Cline is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.cline/skills/` (user-level), `.cline/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### OpenAI Codex
**Provider:** OpenAI  
**Website:** [platform.openai.com](https://platform.openai.com)  
**Description:** OpenAI Codex is a general-purpose code generation model and API that underpins several AI coding experiences. It transforms natural language instructions into code across many languages and performs structured edits on existing codebases.  
**Skill Directory:** `~/.codex/skills/` (user-level), `.codex/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Goose
**Provider:** Goose  
**Website:** [goose.ai](https://goose.ai)  
**Description:** Goose provides lightweight assistants that can run in terminals, editors, or pipelines without heavy vendor lock-in.  
**Skill Directory:** `~/.config/goose/skills/` (user-level), `.goose/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Roo Code
**Provider:** RooCode  
**Website:** [roocode.com](https://roocode.com)  
**Description:** RooCode is an AI coding agent focused on handling larger changes and scaffolding work, often integrating with tools like git and CI. It helps manage multi-file edits and feature implementations.  
**Skill Directory:** `~/.roo/skills/` (user-level), `.roo/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Kilo Code
**Provider:** Kilo Code  
**Website:** [kilocode.ai](https://kilocode.ai)  
**Description:** Kilo Code provides deeper structural assistance for large-scale edits and pattern enforcement across multiple files.  
**Skill Directory:** `~/.kilocode/skills/` (user-level), `.kilocode/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Trae
**Provider:** Trae  
**Website:** [trae.ai](https://trae.ai)  
**Description:** Trae is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.trae/skills/` (user-level), `.trae/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Droid
**Provider:** Factory  
**Website:** [factory.ai](https://factory.ai)  
**Description:** Droid provides opinionated automation around repetitive coding tasks, codebase maintenance, and templated changes.  
**Skill Directory:** `~/.factory/skills/` (user-level), `.factory/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Clawdbot
**Provider:** Clawdbot  
**Website:** [clawdbot.ai](https://clawdbot.ai)  
**Description:** Clawdbot is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.clawdbot/skills/` (user-level), `skills/` (project-level)  
**Notes:** Reads AGENTS.md natively, unique project root skills/ directory

#### Kiro CLI
**Provider:** Kiro  
**Website:** [kiro.ai](https://kiro.ai)  
**Description:** Kiro CLI is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.kiro/skills/` (user-level), `.kiro/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Pi
**Provider:** Pi  
**Website:** [pi.ai](https://pi.ai)  
**Description:** Pi is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.pi/agent/skills/` (user-level), `.pi/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Neovate
**Provider:** Neovate  
**Website:** [neovate.ai](https://neovate.ai)  
**Description:** Neovate is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.neovate/skills/` (user-level), `.neovate/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Google Antigravity
**Provider:** Google  
**Website:** [ai.google.dev](https://ai.google.dev)  
**Description:** Google Antigravity is an advanced AI coding assistant that provides intelligent code generation, refactoring, and multi-file editing capabilities.  
**Skill Directory:** `~/.gemini/antigravity/skills/` (user-level), `.agent/skills/` (project-level)  
**Notes:** Native discovery, unique dual-path configuration

#### Cursor
**Provider:** Anysphere  
**Website:** [cursor.sh](https://cursor.sh)  
**Description:** Cursor is an AI-native code editor built around deep model integration, multi-file awareness, and repo-scale refactors. It provides tight model integration with inline edits, chat-over-repo, and structured refactors.  
**Skill Directory:** `~/.cursor/skills/` (user-level), `.cursor/skills/` (project-level)  
**Notes:** Uses folder-based rules, reads .cursor/rules/RULES.md

#### Windsurf
**Provider:** Cognition  
**Website:** [windsurf.io](https://windsurf.io)  
**Description:** Windsurf from Cognition is an AI-enhanced development environment that emphasizes intelligent navigation and editing of codebases. It combines navigation, search, and AI edits for quick movement through large codebases.  
**Skill Directory:** `~/.codeium/windsurf/skills/` (user-level), `.windsurf/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### GitHub Copilot
**Provider:** GitHub/Microsoft  
**Website:** [github.com/copilot](https://github.com/copilot)  
**Description:** GitHub Copilot represents the autonomous evolution of Copilot, expanding from inline completions to task-oriented multi-file edits. It leverages GitHub's ecosystem for context-aware coding assistance.  
**Skill Directory:** `~/.copilot/skills/` (user-level), `.github/skills/` (project-level)  
**Notes:** Reads .github/copilot-instructions.md

#### Qwen Code
**Provider:** Alibaba  
**Website:** [qwen.ai](https://qwen.ai)  
**Description:** Qwen Code is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.qwen/skills/` (user-level), `.qwen/skills/` (project-level)  
**Notes:** Reads QWEN.md config file

#### Zencoder
**Provider:** Zencoder  
**Website:** [zencoder.ai](https://zencoder.ai)  
**Description:** Zencoder is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.zencoder/skills/` (user-level), `.zencoder/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Amp
**Provider:** Sourcegraph  
**Website:** [sourcegraph.com](https://sourcegraph.com)  
**Description:** Amp focuses on AI-powered developer tooling and agents for structured help across the development lifecycle.  
**Skill Directory:** `~/.config/agents/skills/` (user-level), `.agents/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Qoder
**Provider:** Qoder  
**Website:** [qoder.ai](https://qoder.ai)  
**Description:** Qoder is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.qoder/skills/` (user-level), `.qoder/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

#### Command Code
**Provider:** Command Code  
**Website:** [commandcode.ai](https://commandcode.ai)  
**Description:** Command Code is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `~/.commandcode/skills/` (user-level), `.commandcode/skills/` (project-level)  
**Notes:** Reads AGENTS.md natively

### Tier 2: Bridged Support (Project-Level Only)

These agents work through the universal bridge system with project-level installation only.

#### Aider
**Provider:** Paul Gauthier  
**Website:** [aider.chat](https://aider.chat)  
**Description:** Aider is a CLI-first coding agent that operates directly on local git repos, using an LLM to plan and apply code changes while keeping everything under version control. It provides precise, diff-based edits in polyglot monorepos.  
**Skill Directory:** `.skilz/skills/` (project-level only)  
**Notes:** Project-only, reads CONVENTIONS.md

#### Zed AI
**Provider:** Zed Industries  
**Website:** [zed.dev](https://zed.dev)  
**Description:** Zed is a high-performance, collaborative code editor that integrates AI-powered coding assistance and real-time pair programming features. It combines fast native performance with built-in collaboration primitives and AI features.  
**Skill Directory:** `.skilz/skills/` (project-level only)  
**Notes:** Project-only installation

#### Crush
**Provider:** Crush  
**Website:** [crush.ai](https://crush.ai)  
**Description:** Crush is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `.skilz/skills/` (project-level only)  
**Notes:** Project-only installation

#### Kimi CLI
**Provider:** Moonshot AI  
**Website:** [kimi.ai](https://kimi.ai)  
**Description:** Kimi CLI offers intelligent coding assistance with natural language processing and code generation capabilities.  
**Skill Directory:** `.skilz/skills/` (project-level only)  
**Notes:** Project-only installation

#### Plandex
**Provider:** Plandex  
**Website:** [plandex.ai](https://plandex.ai)  
**Description:** Plandex is an AI coding assistant that provides intelligent code generation and editing capabilities.  
**Skill Directory:** `.skilz/skills/` (project-level only)  
**Notes:** Project-only installation

### Tier 3: Universal Support

All agents from the AGENTS.md ecosystem work via `--agent universal --project`.

#### Universal (Skilz)
**Provider:** Skilz  
**Website:** [skillzwave.ai](https://skillzwave.ai)  
**Description:** Universal agent support for any AGENTS.md compatible AI coding assistant.  
**Skill Directory:** `~/.skilz/skills/` (user-level), `.skilz/skills/` (project-level)  
**Notes:** Reads AGENTS.md, supports any agent via universal mode

## Quick Reference

### Tier 1: Full Native Support (User + Project)
**User-Level Directories:**
- Gemini CLI → `~/.gemini/skills/`
- OpenCode CLI → `~/.config/opencode/skill/`
- OpenHands → `~/.openhands/skills/`
- Claude Code → `~/.claude/skills/`
- Cline → `~/.cline/skills/`
- OpenAI Codex → `~/.codex/skills/`
- Goose → `~/.config/goose/skills/`
- Roo Code → `~/.roo/skills/`
- Kilo Code → `~/.kilocode/skills/`
- Trae → `~/.trae/skills/`
- Droid → `~/.factory/skills/`
- Clawdbot → `~/.clawdbot/skills/`
- Kiro CLI → `~/.kiro/skills/`
- Pi → `~/.pi/agent/skills/`
- Neovate → `~/.neovate/skills/`
- Google Antigravity → `~/.gemini/antigravity/skills/`
- Cursor → `~/.cursor/skills/`
- Windsurf → `~/.codeium/windsurf/skills/`
- GitHub Copilot → `~/.copilot/skills/`
- Qwen Code → `~/.qwen/skills/`
- Zencoder → `~/.zencoder/skills/`
- Amp → `~/.config/agents/skills/`
- Qoder → `~/.qoder/skills/`
- Command Code → `~/.commandcode/skills/`
- Universal → `~/.skilz/skills/`

**Project-Level Directories:**
- Gemini CLI → `.gemini/skills/`
- OpenCode CLI → `.opencode/skill/`
- OpenHands → `.openhands/skills/`
- Claude Code → `.claude/skills/`
- Cline → `.cline/skills/`
- OpenAI Codex → `.codex/skills/`
- Goose → `.goose/skills/`
- Roo Code → `.roo/skills/`
- Kilo Code → `.kilocode/skills/`
- Trae → `.trae/skills/`
- Droid → `.factory/skills/`
- Clawdbot → `skills/` (project root)
- Kiro CLI → `.kiro/skills/`
- Pi → `.pi/skills/`
- Neovate → `.neovate/skills/`
- Google Antigravity → `.agent/skills/`
- Cursor → `.cursor/skills/`
- Windsurf → `.windsurf/skills/`
- GitHub Copilot → `.github/skills/`
- Qwen Code → `.qwen/skills/`
- Zencoder → `.zencoder/skills/`
- Amp → `.agents/skills/`
- Qoder → `.qoder/skills/`
- Command Code → `.commandcode/skills/`
- Universal → `.skilz/skills/`

### Tier 2: Bridged Support (Project-Only)
- Aider → `.skilz/skills/`
- Zed AI → `.skilz/skills/`
- Crush → `.skilz/skills/`
- Kimi CLI → `.skilz/skills/`
- Plandex → `.skilz/skills/`

### Universal Mode (AGENTS.md Compatible)
All agents listed above work via: `skilz install <skill> --agent universal --project`

## Installation Examples

### Native Agent Installation
```bash
# Install to Gemini CLI (most popular)
skilz install mastering-git-cli --agent gemini

# Install to OpenCode CLI
skilz install mastering-git-cli --agent opencode

# Install to Claude Code
skilz install mastering-git-cli --agent claude

# Install to OpenHands
skilz install mastering-git-cli --agent openhands
```

### Project-Level Installation
```bash
# Install to project for any native agent
skilz install mastering-git-cli --agent gemini --project

# Install to bridged agent (project-only)
skilz install mastering-git-cli --agent aider --project
```

### Universal Mode
```bash
# Works with any AGENTS.md compatible agent
skilz install mastering-git-cli --agent universal --project
```

## Configuration

Most agents automatically detect and use their respective config files:
- **AGENTS.md**: OpenCode, OpenHands, Cline, Codex, Goose, Roo, Kilo, Trae, Droid, Clawdbot, Kiro, Pi, Neovate, Windsurf, Zencoder, Amp, Qoder, Command Code, Universal
- **CLAUDE.md**: Claude Code
- **GEMINI.md**: Gemini CLI
- **QWEN.md**: Qwen Code
- **.github/copilot-instructions.md**: GitHub Copilot
- **.cursor/rules/RULES.md**: Cursor
- **CONVENTIONS.md**: Aider

## Getting Started

1. Choose your AI coding agent from the 30+ supported agents above
2. Browse skills at [skillzwave.ai](https://skillzwave.ai)
3. Install with: `skilz install <skill-id> --agent <your-agent>`
4. For project-specific installation, add `--project` flag

For detailed setup instructions for each agent, see the [Comprehensive User Guide](COMPREHENSIVE_USER_GUIDE.md).