# Gemini CLI Migration Guide

**Version:** Skilz 1.7.0  
**Date:** January 8, 2026

---

## Overview

Skilz 1.7.0 introduces native support for Gemini CLI's `.gemini/skills/` directory. This guide helps you choose the right installation method and migrate existing installations if needed.

---

## Which Installation Method Should I Use?

### ✅ Native Support (Recommended)

**Use this if you have:**
- Gemini CLI with `experimental.skills` plugin enabled

**Benefits:**
- Skills install directly to `.gemini/skills/` (native location)
- No config file needed - Gemini reads the directory natively
- Cleaner project structure
- Faster skill loading

**Command:**
```bash
skilz install <skill-name> --agent gemini --project
```

**What happens:**
- Skill installs to: `.gemini/skills/<skill-name>/`
- Config file: None (not needed)
- Gemini reads skills automatically from the directory

---

### 🔧 Legacy/Universal Mode

**Use this if you:**
- Don't have the `experimental.skills` plugin
- Use an older version of Gemini CLI
- Prefer explicit config file management

**Benefits:**
- Works with any version of Gemini CLI
- Skills listed explicitly in GEMINI.md
- Compatible with multi-agent projects

**Command:**
```bash
skilz install <skill-name> --agent universal --project --config GEMINI.md
```

**What happens:**
- Skill installs to: `.skilz/skills/<skill-name>/`
- Config file: `GEMINI.md` (created/updated)
- You reference the config file in your Gemini prompts

---

## How to Check if You Have Native Support

### Option 1: Check Gemini CLI Version

```bash
gemini --version
```

If you see version **0.5.0 or higher**, you likely have native support available.

### Option 2: Check for experimental.skills Plugin

```bash
# Check Gemini's configuration
cat ~/.gemini/settings.json | grep experimental
```

If you see `"experimental.skills": true`, native support is enabled.

### Option 3: Test It

```bash
# Try installing with native support
skilz install anthropics_skills/algorithmic-art --agent gemini --project

# Check if directory was created
ls -la .gemini/skills/
```

If `.gemini/skills/algorithmic-art/` exists, native support is working.

---

## Migration Paths

### Scenario 1: Moving from Universal to Native

**Before (Universal Mode):**
```
project/
├── .skilz/
│   └── skills/
│       └── pdf-reader/
└── GEMINI.md          ← Config file with skill reference
```

**After (Native Mode):**
```
project/
└── .gemini/
    └── skills/
        └── pdf-reader/  ← Direct native location
```

**Migration Steps:**

1. **Check if native support is available** (see above)

2. **Remove old installation:**
   ```bash
   skilz rm pdf-reader --agent universal --project -y
   ```

3. **Reinstall with native support:**
   ```bash
   skilz install <skill-id> --agent gemini --project
   ```

4. **Clean up config file (optional):**
   ```bash
   rm GEMINI.md  # Only if no other skills use it
   ```

5. **Verify installation:**
   ```bash
   skilz list --agent gemini --project
   ```

---

### Scenario 2: Staying on Universal Mode

If you prefer to keep using universal mode (or can't use native support), no migration is needed. Your existing installations will continue to work.

**To install new skills:**
```bash
skilz install <skill-id> --agent universal --project --config GEMINI.md
```

---

### Scenario 3: Mixed Environment (Multiple Projects)

You can use different modes for different projects:

**Project A (Native):**
```bash
cd project-a
skilz install pdf-reader --agent gemini --project
# → Uses .gemini/skills/
```

**Project B (Universal):**
```bash
cd project-b
skilz install pdf-reader --agent universal --project --config GEMINI.md
# → Uses .skilz/skills/ + GEMINI.md
```

---

## Detailed Examples

### Example 1: Install PDF Reader with Native Support

```bash
# Navigate to your project
cd ~/my-project

# Install with native Gemini support
skilz install anthropics_skills/pdf-reader --agent gemini --project

# Verify installation
ls -la .gemini/skills/pdf-reader/

# List installed skills
skilz list --agent gemini --project
```

**Output:**
```
Skill                           Version   Installed   Status
──────────────────────────────────────────────────────────────────
anthropics_skills/pdf-reader    abc123    2026-01-08  up-to-date
```

**Directory structure:**
```
my-project/
└── .gemini/
    └── skills/
        └── pdf-reader/
            ├── SKILL.md
            ├── .skilz-manifest.yaml
            └── ... (skill files)
```

---

### Example 2: Install Excel Skill with Legacy Mode

```bash
# Navigate to your project
cd ~/my-project

# Install with universal agent + GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md

# Verify installation
ls -la .skilz/skills/excel/
cat GEMINI.md  # View the generated config

# List installed skills
skilz list --agent universal --project
```

**Output:**
```
Skill                       Version   Installed   Status
────────────────────────────────────────────────────────────────
anthropics_skills/excel     def456    2026-01-08  up-to-date
```

**Directory structure:**
```
my-project/
├── .skilz/
│   └── skills/
│       └── excel/
│           ├── SKILL.md
│           ├── .skilz-manifest.yaml
│           └── ... (skill files)
└── GEMINI.md          ← Config file with skill reference
```

**GEMINI.md contents:**
```markdown
# GEMINI.md

## Available Skills

<!-- SKILLS_TABLE_START -->
<available_skills>
  <skill>
    <name>excel</name>
    <description>Work with Excel spreadsheets</description>
    <invocation>skilz read excel</invocation>
  </skill>
</available_skills>
<!-- SKILLS_TABLE_END -->
```

---

### Example 3: Installing Multiple Skills

**Native mode (multiple skills):**
```bash
skilz install anthropics_skills/pdf-reader --agent gemini --project
skilz install anthropics_skills/excel --agent gemini --project
skilz install anthropics_skills/docx --agent gemini --project

# All skills in .gemini/skills/
ls -la .gemini/skills/
# pdf-reader/  excel/  docx/
```

**Legacy mode (multiple skills):**
```bash
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
skilz install anthropics_skills/docx --agent universal --project --config GEMINI.md

# All skills in .skilz/skills/, all referenced in GEMINI.md
ls -la .skilz/skills/
# pdf-reader/  excel/  docx/
cat GEMINI.md  # Shows all 3 skills
```

---

## Troubleshooting

### Issue: Native installation fails

**Error:**
```
Error: Agent 'gemini' does not support home-level installations
```

**Solution:** Add the `--project` flag:
```bash
skilz install <skill-name> --agent gemini --project
```

---

### Issue: Skills not loading in Gemini CLI

**For Native Mode:**

1. **Check if experimental.skills is enabled:**
   ```bash
   cat ~/.gemini/settings.json | grep experimental
   ```

2. **Verify skills are in correct location:**
   ```bash
   ls -la .gemini/skills/
   ```

3. **Try restarting Gemini CLI:**
   ```bash
   # Exit and restart Gemini
   ```

**For Legacy Mode:**

1. **Check if GEMINI.md exists:**
   ```bash
   cat GEMINI.md
   ```

2. **Manually load skills in your prompts:**
   ```
   Use the skills defined in GEMINI.md
   ```

---

### Issue: Config file not created (legacy mode)

**Error:**
```
GEMINI.md not created after installation
```

**Solution:** Make sure you're using the `--config` flag:
```bash
skilz install <skill-name> --agent universal --project --config GEMINI.md
#                                                      ^^^^^^ Must include this
```

---

### Issue: Mixed native and legacy installations

If you accidentally installed some skills with native mode and others with legacy mode:

**Check which mode each skill uses:**
```bash
# Native skills
ls -la .gemini/skills/

# Universal/legacy skills
ls -la .skilz/skills/
```

**Standardize on one mode:**

**Option A: Move to native (recommended):**
```bash
# Remove universal installations
skilz rm <skill-name> --agent universal --project -y

# Reinstall with native
skilz install <skill-id> --agent gemini --project
```

**Option B: Move to universal:**
```bash
# Remove native installations
skilz rm <skill-name> --agent gemini --project -y

# Reinstall with universal
skilz install <skill-id> --agent universal --project --config GEMINI.md
```

---

## FAQ

### Q: Which mode is better?

**A:** Native mode is recommended if you have `experimental.skills` enabled. It's cleaner, faster, and follows Gemini's intended architecture.

### Q: Can I use both modes in the same project?

**A:** Technically yes, but it's not recommended. Choose one mode to avoid confusion.

### Q: Will my existing installations break after upgrading to Skilz 1.7.0?

**A:** No. Existing installations continue to work. You only get native support if you explicitly use `--agent gemini`.

### Q: How do I enable experimental.skills in Gemini CLI?

**A:** Check Gemini CLI's documentation:
```bash
gemini config set experimental.skills true
```
(Note: Exact command may vary by Gemini version)

### Q: Can I switch between modes easily?

**A:** Yes. Just uninstall and reinstall with the desired mode (see migration steps above).

### Q: Does native mode work for user-level installs?

**A:** Yes! In Skilz 1.7.0, Gemini supports both:
- Project-level: `.gemini/skills/`
- User-level: `~/.gemini/skills/`

```bash
# User-level native install (NEW in 1.7.0)
skilz install <skill-name> --agent gemini
```

---

## Summary

| Feature | Native Mode | Legacy/Universal Mode |
|---------|-------------|----------------------|
| **Requires** | experimental.skills plugin | Any Gemini version |
| **Install location** | `.gemini/skills/` | `.skilz/skills/` |
| **Config file** | None | GEMINI.md |
| **Performance** | Faster (direct read) | Slightly slower (config parse) |
| **Recommended for** | New projects | Older Gemini versions |
| **User-level support** | ✅ Yes (NEW in 1.7) | ✅ Yes |
| **Project-level support** | ✅ Yes | ✅ Yes |

---

## Next Steps

1. **Determine which mode you need** (native vs legacy)
2. **Test with one skill** before migrating all skills
3. **Update your project documentation** to reflect the chosen mode
4. **Consider setting a default agent** in `.skilz/config.yaml`:

```yaml
default_agent: gemini  # For native mode projects
# OR
default_agent: universal  # For legacy mode projects
```

For more information, see:
- [Universal Agent Guide](UNIVERSAL_AGENT_GUIDE.md)
- [User Manual](USER_MANUAL.md)
- [CHANGELOG](../CHANGELOG.md)

---

**Need help?** Open an issue on [GitHub](https://github.com/spillwave/skilz-cli/issues).
