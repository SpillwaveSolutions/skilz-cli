# Supported AI Coding Agents

Skilz supports **22+ AI coding agents** from the [AGENTS.md](https://agents.md/) ecosystem, following the [agentskills.io](https://agentskills.io/) standard for skill format and installation.

## Agent Categories

### Full Skill Support (Native Directories)

Agents with dedicated skill directories at user or project level.

#### Claude Code
**Provider:** Anthropic
**Website:** [claude.ai/code](https://claude.ai/code)
**Description:** Claude Code is Anthropic's native coding assistant with deep integration into their AI platform. It provides intelligent code completion, refactoring, and multi-file editing capabilities.
**Skill Directory:** `~/.claude/skills/` (user-level), `.claude/skills/` (project-level)
**Notes:** Uses CLAUDE.md config file (not AGENTS.md)

#### OpenCode CLI
**Provider:** OpenCode
**Website:** [opencode.dev](https://opencode.dev)
**Description:** OpenCode CLI is a terminal-based coding assistant that provides AI-powered code generation and editing directly in your command line.
**Skill Directory:** `~/.config/opencode/skill/` (user-level), `.opencode/skill/` (project-level)
**Notes:** Reads AGENTS.md natively

#### OpenAI Codex
**Provider:** OpenAI
**Website:** [platform.openai.com](https://platform.openai.com)
**Description:** OpenAI Codex is a general-purpose code generation model and API that underpins several AI coding experiences. It transforms natural language instructions into code across many languages and performs structured edits on existing codebases.
**Skill Directory:** `~/.codex/skills/` (user-level), `.codex/skills/` (project-level)
**Notes:** Reads AGENTS.md natively

#### Cursor
**Provider:** Anysphere
**Website:** [cursor.sh](https://cursor.sh)
**Description:** Cursor is an AI-native code editor built around deep model integration, multi-file awareness, and repo-scale refactors. It provides tight model integration with inline edits, chat-over-repo, and structured refactors.
**Skill Directory:** `.skills/skills/` (project-level only)
**Notes:** Project-only installation

#### Aider
**Provider:** Paul Gauthier
**Website:** [aider.chat](https://aider.chat)
**Description:** Aider is a CLI-first coding agent that operates directly on local git repos, using an LLM to plan and apply code changes while keeping everything under version control. It provides precise, diff-based edits in polyglot monorepos.
**Skill Directory:** `.skilz/skills/` (project-level only)
**Notes:** Project-only, reads AGENTS.md via `.aider.conf.yml`

#### Windsurf
**Provider:** Cognition
**Website:** [windsurf.io](https://windsurf.io)
**Description:** Windsurf from Cognition is an AI-enhanced development environment that emphasizes intelligent navigation and editing of codebases. It combines navigation, search, and AI edits for quick movement through large codebases.
**Skill Directory:** `.skilz/skills/` (project-level only)
**Notes:** Project-only installation

#### Zed AI
**Provider:** Zed Industries
**Website:** [zed.dev](https://zed.dev)
**Description:** Zed is a high-performance, collaborative code editor that integrates AI-powered coding assistance and real-time pair programming features. It combines fast native performance with built-in collaboration primitives and AI features.
**Skill Directory:** `.skilz/skills/` (project-level only)
**Notes:** Project-only installation

#### RooCode
**Provider:** RooCode
**Website:** [roocode.com](https://roocode.com)
**Description:** RooCode is an AI coding agent focused on handling larger changes and scaffolding work, often integrating with tools like git and CI. It helps manage multi-file edits and feature implementations.
**Skill Directory:** `.skilz/skills/` (project-level only)
**Notes:** Project-only installation

### Project-Only Support

Agents that work with project-level skills via `--project` flag.

#### Gemini CLI
**Provider:** Google
**Website:** [ai.google.dev](https://ai.google.dev)
**Description:** Gemini CLI is a command-line client for interacting with Google's Gemini models, including coding workflows and agents. It provides scriptable, model-centric interface for code generation and repository modification.
**Skill Directory:** `.gemini/skills/` (project-level)
**Notes:** Requires `experimental.skills` plugin, reads AGENTS.md via `.gemini/settings.json`

#### GitHub Copilot
**Provider:** GitHub/Microsoft
**Website:** [github.com/copilot](https://github.com/copilot)
**Description:** GitHub Copilot represents the autonomous evolution of Copilot, expanding from inline completions to task-oriented multi-file edits. It leverages GitHub's ecosystem for context-aware coding assistance.
**Skill Directory:** `.github/skills/` (project-level)
**Notes:** Reads AGENTS.md natively

#### Qwen CLI
**Provider:** Alibaba Cloud
**Website:** [qwenlm.ai](https://qwenlm.ai)
**Description:** Qwen CLI provides AI-assisted coding capabilities with support for multiple programming languages and development workflows.
**Skill Directory:** `.skilz/skills/` (project-level)
**Notes:** Via universal agent

#### Kimi CLI
**Provider:** Moonshot AI
**Website:** [kimi.ai](https://kimi.ai)
**Description:** Kimi CLI offers intelligent coding assistance with natural language processing and code generation capabilities.
**Skill Directory:** `.skilz/skills/` (project-level)
**Notes:** Via universal agent

### Universal Support (AGENTS.md Compatible)

All agents from the AGENTS.md ecosystem work via `--agent universal --project`.

#### Ona
**Provider:** Independent
**Description:** Ona provides configurable, possibly self-hostable agents that can operate over local code with flexible behavior tuning.
**Installation:** `skilz install skill --agent universal --project`

#### Amp
**Provider:** Sourcegraph
**Website:** [sourcegraph.com](https://sourcegraph.com)
**Description:** Amp focuses on AI-powered developer tooling and agents for structured help across the development lifecycle.
**Installation:** `skilz install skill --agent universal --project`

#### Kilo Code
**Provider:** Independent
**Description:** Kilo Code provides deeper structural assistance for large-scale edits and pattern enforcement across multiple files.
**Installation:** `skilz install skill --agent universal --project`

#### Devin
**Provider:** Cognition
**Website:** [cognition.ai](https://cognition.ai)
**Description:** Devin is positioned as an "AI software engineer" that can autonomously plan, code, run tests, and iterate on tasks end-to-end.
**Installation:** `skilz install skill --agent universal --project`

#### Factory
**Provider:** Factory
**Description:** Factory provides opinionated automation around repetitive coding tasks, codebase maintenance, and templated changes.
**Installation:** `skilz install skill --agent universal --project`

#### Jules
**Provider:** Google
**Description:** Jules leverages Google's LLM stack and cloud integrations to provide coding help, refactors, and multi-file edits.
**Installation:** `skilz install skill --agent universal --project`

#### Phoenix
**Provider:** Independent
**Description:** Phoenix offers agentic assistance that can understand and modify codebases with autonomy, focusing on debugging and iterative improvement.
**Installation:** `skilz install skill --agent universal --project`

#### Goose
**Provider:** Independent
**Description:** Goose provides lightweight assistants that can run in terminals, editors, or pipelines without heavy vendor lock-in.
**Installation:** `skilz install skill --agent universal --project`

#### Google Antigravity
**Provider:** Google
**Description:** Google Antigravity is an advanced AI coding assistant that provides intelligent code generation, refactoring, and multi-file editing capabilities. Currently supported via universal mode with plans for native integration.
**Installation:** `skilz install skill --agent universal --project`
**Notes:** Native support planned for future release

#### Warp
**Provider:** Warp
**Website:** [warp.dev](https://warp.dev)
**Description:** Warp is a next-generation terminal with structured input, rich UI, and built-in AI assistance for command composition.
**Installation:** `skilz install skill --agent universal --project`

#### VS Code (with coding agents)
**Provider:** Microsoft
**Website:** [code.visualstudio.com](https://code.visualstudio.com)
**Description:** VS Code serves as the integration hub for various AI coding extensions, acting as the default environment for many organizations.
**Installation:** `skilz install skill --agent universal --project`

#### Semgrep
**Provider:** Semgrep
**Website:** [semgrep.dev](https://semgrep.dev)
**Description:** Semgrep is a static analysis engine and rule framework for code scanning, security checks, and pattern-based refactors.
**Installation:** `skilz install skill --agent universal --project`

#### Autopilot
**Provider:** UiPath
**Website:** [uipath.com](https://uipath.com)
**Description:** UiPath Autopilot extends automation platform with generative AI for understanding natural language and generating workflows.
**Installation:** `skilz install skill --agent universal --project`

## Quick Reference

### Native Support (User-Level)
- Claude Code → `~/.claude/skills/`
- OpenAI Codex → `~/.codex/skills/`
- OpenCode CLI → `~/.config/opencode/skill/`
- Universal → `~/.skilz/skills/`

### Project-Level Support
- Gemini CLI → `.gemini/skills/`
- GitHub Copilot → `.github/skills/`
- Cursor → `.skills/skills/`
- Aider → `.skilz/skills/`
- Windsurf → `.skilz/skills/`
- Qwen CLI → `.skilz/skills/`
- Kimi CLI → `.skilz/skills/`
- Zed AI → `.skilz/skills/`
- RooCode → `.skilz/skills/`

### Universal Mode (AGENTS.md Compatible)
All agents listed above work via: `skilz install <skill> --agent universal --project`

## Configuration

Most agents automatically detect and use AGENTS.md files for project-specific configuration. For agents without native support, use:

```bash
skilz install <skill-id> --agent universal --project --config AGENTS.md
```

This installs skills to `.skilz/skills/` and references them in your project's AGENTS.md file.

## Getting Started

1. Choose your AI coding agent from the list above
2. Browse skills at [skillzwave.ai](https://skillzwave.ai)
3. Install with: `skilz install <skill-id> --agent <your-agent>`

For detailed setup instructions for each agent, see the [Comprehensive User Guide](COMPREHENSIVE_USER_GUIDE.md).