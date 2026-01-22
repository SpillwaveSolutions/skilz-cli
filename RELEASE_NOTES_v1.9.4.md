# 🚀 Skilz CLI v1.9.4 Release Notes

**Release Date**: January 21, 2026  
**Version**: 1.9.4  
**Tag**: `v1.9.4`

## 🎯 Overview

This release significantly improves the user experience with major enhancements to skill discovery and installation workflows. The highlight is **GitHub shorthand URL support**, making it much easier to install skills directly from search results.

## ✨ What's New

### 🔗 GitHub Shorthand URL Support (v1.9.4)

**The Big Feature**: You can now use GitHub shorthand URLs with the `-g` flag!

```bash
# ✅ NEW: This now works!
skilz install -g tfriedel/claude-office-skills

# ✅ OLD: This still works
skilz install -g https://github.com/tfriedel/claude-office-skills
```

**How it works**: When you use `-g owner/repo`, skilz automatically converts it to `https://github.com/owner/repo` behind the scenes.

**Why this matters**: 
- 🎯 **Easier workflow**: Search → Copy repo name → Install directly
- ⚡ **Faster typing**: No need for full URLs
- 🔄 **Seamless integration**: Works with existing search results

### 🔍 Search Functionality Restored (v1.9.3)

**Problem Fixed**: `skilz search` was returning no results for any queries.

**Solution**: Complete overhaul of search logic:
- **Better Query**: Changed from `{query} skill OR skills` to `{query} claude`
- **Smart Sorting**: Results now sorted by GitHub stars (most popular first)
- **More Results**: Significantly improved result quality and quantity

**Real Examples**:
```bash
skilz search docx
# Returns 10 results, top: tfriedel/claude-office-skills (208 stars)

skilz search excel  
# Returns 94 results, top: mcp-excel-server (81 stars)

skilz search python
# Returns 10 results with relevant Claude/AI repositories
```

## 🛠️ Bug Fixes & Improvements

### v1.9.2: OpenCode Directory Path Fix
- **Fixed**: OpenCode skills directory path
- **Was**: `~/.config/opencode/skills` (plural) ❌
- **Now**: `~/.config/opencode/skill` (singular) ✅
- **Impact**: `skilz list --agent opencode` now correctly finds installed skills

### v1.9.1: Configuration & Path Improvements
- **Usage Notes Fix**: Usage instructions now only appear for agents that need them
  - Native agents (Claude, OpenCode, Codex): No usage notes clutter
  - Non-native agents (Gemini, Cursor, etc.): Clear usage instructions
- **Path Consistency**: Fixed directory paths for 8 non-native agents to use `.skilz/skills`

## 🎯 Complete Workflow Example

Here's how the improved workflow looks:

```bash
# 1. Search for skills
skilz search docx
# Found 10 skill(s) matching 'docx':
# tfriedel/claude-office-skills    208  Office document creation...

# 2. Install directly with shorthand
skilz install -g tfriedel/claude-office-skills
# Found 4 skills in repository:
#   [1] docx  (public/docx)
#   [2] pdf   (public/pdf)
#   [3] pptx  (public/pptx)  
#   [4] xlsx  (public/xlsx)

# 3. Select and install
# Select skill(s) [1-4, A, Q]: 1
# Installed: docx -> Claude Code (user) [git]
```

## 📊 Technical Details

### Quality Assurance
- ✅ **659 tests passing** (100% test suite success)
- ✅ **Type safety**: Full mypy compliance
- ✅ **Code quality**: Ruff linting passed
- ✅ **Coverage**: 85%+ test coverage maintained

### Agent Support Matrix
| Agent | Directory | Native Support | Config Sync |
|-------|-----------|----------------|-------------|
| Claude Code | `~/.claude/skills/` | ✅ All | ❌ Not needed |
| OpenCode | `~/.config/opencode/skill/` | ✅ All | ❌ Not needed |
| Codex | `~/.codex/skills/` | ✅ All | ❌ Not needed |
| Gemini | `~/.gemini/skills/` | ✅ With plugin | ✅ GEMINI.md |
| Universal | `~/.skilz/skills/` | ❌ None | ✅ AGENTS.md |
| Others (8) | `.skilz/skills/` | ❌ None | ✅ AGENTS.md |

### Files Changed
- **Core Logic**: `src/skilz/commands/install_cmd.py` - GitHub shorthand support
- **Search**: `src/skilz/commands/search_cmd.py` - Query and sorting improvements  
- **Agents**: `src/skilz/agents.py` - OpenCode path fix
- **Config**: `src/skilz/config_sync.py` - Usage notes logic
- **Registry**: `src/skilz/agent_registry.py` - Path consistency
- **Tests**: `tests/test_agents.py` - Updated for path changes

## 🔄 Migration Guide

### For Existing Users
**No action required!** All existing functionality continues to work:
- Existing installations remain unchanged
- All previous command syntax still works
- Configuration files are automatically updated

### New Capabilities
You can now use these new patterns:
```bash
# GitHub shorthand (NEW)
skilz install -g owner/repo

# Search and install workflow (IMPROVED)
skilz search <term>
skilz install -g <repo-from-results>
```

## 🐛 Known Issues
- Minor: Debug output may appear during GitHub shorthand URL conversion (cosmetic only)
- This will be addressed in a future patch release

## 📈 Impact Metrics

### Before v1.9.4
- Search: ❌ No results returned
- Install: Required full GitHub URLs
- OpenCode: ❌ Skills not detected
- UX: Cluttered usage notes for all agents

### After v1.9.4  
- Search: ✅ 10-94 results per query
- Install: ✅ Shorthand URLs work
- OpenCode: ✅ Skills properly detected
- UX: ✅ Clean, agent-appropriate guidance

## 🙏 Acknowledgments

This release addresses multiple user pain points identified through community feedback:
- Simplified installation workflow
- Better skill discovery
- Improved agent compatibility
- Cleaner user interface

## 🔗 Links

- **Repository**: https://github.com/SpillwaveSolutions/skilz-cli
- **Documentation**: [User Manual](docs/USER_MANUAL.md)
- **Issues**: https://github.com/SpillwaveSolutions/skilz-cli/issues
- **PyPI**: https://pypi.org/project/skilz/

## 📦 Installation

### New Installation
```bash
pip install skilz
```

### Upgrade from Previous Version
```bash
pip install --upgrade skilz
```

### Verify Installation
```bash
skilz --version
# skilz 1.9.4

skilz search test
# Should return results
```

---

**Full Changelog**: [v1.9.3...v1.9.4](https://github.com/SpillwaveSolutions/skilz-cli/compare/v1.9.3...v1.9.4)

**Questions?** Open an issue or check our [documentation](docs/).