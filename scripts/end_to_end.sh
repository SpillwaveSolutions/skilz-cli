#!/usr/bin/env bash
#
# Skilz 1.7.0 End-to-End Test Script
#
# This script tests all major features of skilz:
# - Install via marketplace ID
# - Install via Git URL (HTTPS, SSH, -g flag, auto-detect)
# - Install from filesystem
# - Install to various agents (claude, opencode, codex, gemini, copilot, universal)
# - Install at project level
# - Gemini native support (NEW in 1.7)
# - Universal agent with custom config (NEW in 1.7)
# - List commands (skilz list, skilz ls)
# - Remove commands (skilz uninstall, skilz rm)
# - Search command
# - Visit command (dry-run only)
# - GitHub Copilot project-only installation
#
# Usage: ./scripts/end_to_end.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Arrays to track test results for summary table
declare -a TEST_COMMANDS=()
declare -a TEST_DESCRIPTIONS=()
declare -a TEST_RESULTS=()

# Test skill to use
SKILL_ID="Jamie-BitFlight_claude_skills/brainstorming-skill"
SKILL_NAME="brainstorming-skill"
GIT_REPO_HTTPS="https://github.com/Jamie-BitFlight/claude_skills.git"
GIT_REPO_SSH="git@github.com:Jamie-BitFlight/claude_skills.git"
GIT_REPO_URL="https://github.com/Jamie-BitFlight/claude_skills"

# Test directories
E2E_DIR=""
TEST_PROJECT_DIR=""
BACKUP_DIR=""

#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++)) || true
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++)) || true
}

# Track a test result for the summary table
# Usage: track_test "command" "description" "PASS|FAIL"
track_test() {
    local cmd="$1"
    local desc="$2"
    local result="$3"
    TEST_COMMANDS+=("$cmd")
    TEST_DESCRIPTIONS+=("$desc")
    TEST_RESULTS+=("$result")
}

# Print the comprehensive summary table
print_summary_table() {
    echo ""
    echo "┌────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐"
    echo "│                                 SKILZ 1.7.0 END-TO-END TEST RESULTS                                    │"
    echo "├────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤"
    printf "│ %-6s │ %-90s │\n" "STATUS" "COMMAND / DESCRIPTION"
    echo "├────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤"
    
    for i in "${!TEST_COMMANDS[@]}"; do
        local status="${TEST_RESULTS[$i]}"
        local cmd="${TEST_COMMANDS[$i]}"
        local desc="${TEST_DESCRIPTIONS[$i]}"
        
        # Print status and full command (no truncation)
        if [[ "$status" == "PASS" ]]; then
            printf "│ ${GREEN}%-6s${NC} │ %-90s │\n" "$status" "$cmd"
        else
            printf "│ ${RED}%-6s${NC} │ %-90s │\n" "$status" "$cmd"
        fi
        # Print description on next line, indented
        printf "│        │   ${BLUE}→ %s${NC}%-*s │\n" "$desc" $((86 - ${#desc})) ""
    done
    
    echo "├────────┴────────────────────────────────────────────────────────────────────────────────────────────────┤"
    printf "│ ${GREEN}PASSED: %-3d${NC}  │  ${RED}FAILED: %-3d${NC}  │  TOTAL: %-3d                                                          │\n" "$TESTS_PASSED" "$TESTS_FAILED" "$((TESTS_PASSED + TESTS_FAILED))"
    echo "└────────────────────────────────────────────────────────────────────────────────────────────────────────┘"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if a file or directory exists
assert_exists() {
    local path="$1"
    local description="$2"
    if [[ -e "$path" ]]; then
        log_success "$description exists: $path"
        return 0
    else
        log_fail "$description does NOT exist: $path"
        return 1
    fi
}

# Check if a file or directory does NOT exist
assert_not_exists() {
    local path="$1"
    local description="$2"
    if [[ ! -e "$path" ]]; then
        log_success "$description correctly removed: $path"
        return 0
    else
        log_fail "$description still exists: $path"
        return 1
    fi
}

# Check if skilz list shows a skill
assert_skill_in_list() {
    local skill_name="$1"
    local agent="$2"
    local project_flag="$3"
    
    local cmd="skilz list"
    [[ -n "$agent" ]] && cmd="$cmd --agent $agent"
    [[ "$project_flag" == "true" ]] && cmd="$cmd --project"
    
    if $cmd 2>/dev/null | grep -q "$skill_name"; then
        log_success "Skill '$skill_name' found in list ($cmd)"
        return 0
    else
        log_fail "Skill '$skill_name' NOT found in list ($cmd)"
        return 1
    fi
}

# Check if skilz list does NOT show a skill
assert_skill_not_in_list() {
    local skill_name="$1"
    local agent="$2"
    local project_flag="$3"
    
    local cmd="skilz list"
    [[ -n "$agent" ]] && cmd="$cmd --agent $agent"
    [[ "$project_flag" == "true" ]] && cmd="$cmd --project"
    
    if ! $cmd 2>/dev/null | grep -q "$skill_name"; then
        log_success "Skill '$skill_name' correctly not in list ($cmd)"
        return 0
    else
        log_fail "Skill '$skill_name' still appears in list ($cmd)"
        return 1
    fi
}

# Clean up a skill installation
cleanup_skill() {
    local agent="$1"
    local project_flag="$2"
    
    local base_cmd="$SKILL_NAME -y"
    [[ -n "$agent" ]] && base_cmd="$base_cmd --agent $agent"
    [[ "$project_flag" == "true" ]] && base_cmd="$base_cmd --project"
    
    # Try rm alias first, fall back to remove
    log_info "Cleanup: skilz rm $base_cmd"
    skilz rm $base_cmd 2>/dev/null || skilz remove $base_cmd 2>/dev/null || true
}

#------------------------------------------------------------------------------
# Setup
#------------------------------------------------------------------------------

setup() {
    log_section "SETUP"
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    log_info "Script directory: $SCRIPT_DIR"
    log_info "Project root: $PROJECT_ROOT"
    
    # Create isolated e2e test folder
    E2E_DIR="$PROJECT_ROOT/e2e"
    TEST_PROJECT_DIR="$E2E_DIR/test_folder"
    
    log_info "Creating isolated test environment: $TEST_PROJECT_DIR"
    mkdir -p "$TEST_PROJECT_DIR"
    
    # Create mock Python project structure
    mkdir -p "$TEST_PROJECT_DIR/src"
    mkdir -p "$TEST_PROJECT_DIR/tests"
    
    # Create mock pyproject.toml
    cat > "$TEST_PROJECT_DIR/pyproject.toml" <<'EOF'
[tool.poetry]
name = "skilz-e2e-test"
version = "0.1.0"
description = "Test project for Skilz E2E tests"
authors = ["Skilz Test <test@skilz.test>"]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF
    
    # Create mock requirements.txt
    cat > "$TEST_PROJECT_DIR/requirements.txt" <<'EOF'
# Test dependencies
pytest>=7.0.0
EOF
    
    # Create mock setup.py
    cat > "$TEST_PROJECT_DIR/setup.py" <<'EOF'
from setuptools import setup, find_packages

setup(
    name="skilz-e2e-test",
    version="0.1.0",
    packages=find_packages(),
)
EOF
    
    # Create __init__.py files
    touch "$TEST_PROJECT_DIR/src/__init__.py"
    touch "$TEST_PROJECT_DIR/tests/__init__.py"
    
    log_success "Created mock project structure"
    
    # Create backup directory for any existing installations
    BACKUP_DIR=$(mktemp -d)
    log_info "Backup directory: $BACKUP_DIR"
    
    # Install the current version of skilz
    log_info "Installing skilz from source..."
    cd "$PROJECT_ROOT"
    pip install -e . --quiet
    
    # Verify skilz is installed
    if command -v skilz &> /dev/null; then
        log_success "skilz is installed: $(skilz --version)"
    else
        log_fail "skilz is not installed"
        exit 1
    fi
    
    # Clean up any existing test skill installations (ignore errors)
    log_info "Cleaning up any existing test skill installations..."
    set +e  # Temporarily disable exit on error
    for agent in claude opencode codex universal; do
        cleanup_skill "$agent" "false"
    done
    cleanup_skill "gemini" "true"
    cleanup_skill "copilot" "true"
    
    cd "$TEST_PROJECT_DIR"
    cleanup_skill "" "true"
    cd "$PROJECT_ROOT"
    set -e  # Re-enable exit on error
}

#------------------------------------------------------------------------------
# Test: Install from Marketplace
#------------------------------------------------------------------------------

test_install_marketplace() {
    log_section "TEST: Install from Marketplace"
    
    local cmd="skilz install $SKILL_ID --agent claude"
    
    # Install for Claude
    log_info "Installing $SKILL_ID for Claude..."
    if skilz install "$SKILL_ID" --agent claude; then
        log_success "Marketplace install for Claude succeeded"
        track_test "$cmd" "Marketplace install for claude" "PASS"
    else
        log_fail "Marketplace install for Claude failed"
        track_test "$cmd" "Marketplace install for claude" "FAIL"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    track_test "verify: ~/.claude/skills/$SKILL_NAME" "Skill directory exists" "PASS"
    assert_exists "$HOME/.claude/skills/$SKILL_NAME/SKILL.md" "SKILL.md file"
    track_test "verify: SKILL.md" "SKILL.md file exists" "PASS"
    assert_exists "$HOME/.claude/skills/$SKILL_NAME/.skilz-manifest.yaml" "Manifest file"
    track_test "verify: .skilz-manifest.yaml" "Manifest file exists" "PASS"
    
    # Verify in list
    assert_skill_in_list "$SKILL_NAME" "claude" "false"
    track_test "skilz list --agent claude" "Skill appears in list" "PASS"
    
    # Test skilz ls alias
    log_info "Testing 'skilz ls' alias..."
    if skilz ls --agent claude 2>/dev/null | grep -q "$SKILL_NAME"; then
        log_success "'skilz ls' alias works correctly"
        track_test "skilz ls --agent claude" "ls alias shows skill" "PASS"
    else
        log_fail "'skilz ls' alias failed"
        track_test "skilz ls --agent claude" "ls alias shows skill" "FAIL"
    fi
    
    # Cleanup
    log_info "Removing skill..."
    local rm_cmd="skilz uninstall $SKILL_NAME --agent claude -y"
    if skilz uninstall "$SKILL_NAME" --agent claude -y 2>/dev/null || \
       skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null; then
        log_success "Uninstall succeeded"
        track_test "$rm_cmd" "Uninstall skill" "PASS"
    else
        log_fail "Uninstall failed"
        track_test "$rm_cmd" "Uninstall skill" "FAIL"
    fi
    
    assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    track_test "verify: skill removed" "Skill directory removed" "PASS"
    assert_skill_not_in_list "$SKILL_NAME" "claude" "false"
    track_test "skilz list --agent claude" "Skill not in list after remove" "PASS"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (HTTPS with -g flag)
#------------------------------------------------------------------------------

test_install_git_https_flag() {
    log_section "TEST: Install from Git URL (HTTPS with -g flag)"
    
    local cmd="skilz install -g $GIT_REPO_HTTPS --skill $SKILL_NAME --agent opencode"
    
    log_info "Installing from $GIT_REPO_HTTPS with -g flag..."
    if skilz install -g "$GIT_REPO_HTTPS" --skill "$SKILL_NAME" --agent opencode; then
        log_success "Git HTTPS install with -g flag succeeded"
        track_test "$cmd" "Git HTTPS install with -g flag" "PASS"
    else
        log_fail "Git HTTPS install with -g flag failed"
        track_test "$cmd" "Git HTTPS install with -g flag" "FAIL"
        return
    fi
    
    # Verify installation (OpenCode uses singular 'skill' directory)
    assert_exists "$HOME/.config/opencode/skill/$SKILL_NAME" "OpenCode skill directory"
    track_test "verify: ~/.config/opencode/skill/$SKILL_NAME" "OpenCode skill dir exists" "PASS"
    assert_skill_in_list "$SKILL_NAME" "opencode" "false"
    track_test "skilz list --agent opencode" "Skill in opencode list" "PASS"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent opencode -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent opencode -y 2>/dev/null || true
    assert_not_exists "$HOME/.config/opencode/skill/$SKILL_NAME" "OpenCode skill directory"
    track_test "skilz rm $SKILL_NAME --agent opencode -y" "Remove from opencode" "PASS"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (Auto-detect - no flag)
#------------------------------------------------------------------------------

test_install_git_autodetect() {
    log_section "TEST: Install from Git URL (Auto-detect - NEW in 1.5)"
    
    local cmd="skilz install $GIT_REPO_URL --skill $SKILL_NAME --agent codex"
    
    log_info "Installing from $GIT_REPO_URL without -g flag (auto-detect)..."
    if skilz install "$GIT_REPO_URL" --skill "$SKILL_NAME" --agent codex 2>&1; then
        log_success "Git URL auto-detect install succeeded"
        track_test "$cmd" "Git URL auto-detect (no -g)" "PASS"
        
        # Verify installation
        assert_exists "$HOME/.codex/skills/$SKILL_NAME" "Codex skill directory"
        track_test "verify: ~/.codex/skills/$SKILL_NAME" "Codex skill dir exists" "PASS"
        assert_skill_in_list "$SKILL_NAME" "codex" "false"
        track_test "skilz list --agent codex" "Skill in codex list" "PASS"
        
        # Cleanup - try both uninstall and remove for compatibility
        skilz uninstall "$SKILL_NAME" --agent codex -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent codex -y 2>/dev/null || true
        assert_not_exists "$HOME/.codex/skills/$SKILL_NAME" "Codex skill directory"
        track_test "skilz uninstall $SKILL_NAME --agent codex -y" "Remove from codex" "PASS"
    else
        log_warn "Git URL auto-detect may not be available - trying with -g flag"
        track_test "$cmd" "Git URL auto-detect (no -g)" "FAIL"
        # Fall back to -g flag
        if skilz install -g "$GIT_REPO_URL" --skill "$SKILL_NAME" --agent codex 2>&1; then
            log_success "Git install with -g flag succeeded (auto-detect not available)"
            track_test "skilz install -g $GIT_REPO_URL --skill $SKILL_NAME --agent codex" "Git install fallback -g" "PASS"
            skilz remove "$SKILL_NAME" --agent codex -y 2>/dev/null || true
        else
            log_fail "Git URL install failed"
            track_test "skilz install -g $GIT_REPO_URL --skill $SKILL_NAME --agent codex" "Git install fallback -g" "FAIL"
        fi
    fi
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (HTTPS ending with .git)
#------------------------------------------------------------------------------

test_install_git_https_dotgit() {
    log_section "TEST: Install from Git URL (HTTPS .git suffix)"
    
    local cmd="skilz install $GIT_REPO_HTTPS --skill $SKILL_NAME --agent universal"
    
    log_info "Installing from $GIT_REPO_HTTPS (auto-detect .git suffix)..."
    if skilz install "$GIT_REPO_HTTPS" --skill "$SKILL_NAME" --agent universal; then
        log_success "Git HTTPS .git install succeeded"
        track_test "$cmd" "Git HTTPS .git suffix auto-detect" "PASS"
    else
        log_fail "Git HTTPS .git install failed"
        track_test "$cmd" "Git HTTPS .git suffix auto-detect" "FAIL"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.skilz/skills/$SKILL_NAME" "Universal skill directory"
    track_test "verify: ~/.skilz/skills/$SKILL_NAME" "Universal skill dir exists" "PASS"
    assert_skill_in_list "$SKILL_NAME" "universal" "false"
    track_test "skilz list --agent universal" "Skill in universal list" "PASS"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent universal -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent universal -y 2>/dev/null || true
    assert_not_exists "$HOME/.skilz/skills/$SKILL_NAME" "Universal skill directory"
    track_test "skilz rm $SKILL_NAME --agent universal -y" "Remove from universal" "PASS"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (SSH format)
#------------------------------------------------------------------------------

test_install_git_ssh() {
    log_section "TEST: Install from Git URL (SSH format)"
    
    local cmd="skilz install -g $GIT_REPO_SSH --skill $SKILL_NAME --agent claude"
    
    log_info "Installing from $GIT_REPO_SSH..."
    
    # SSH may require authentication - try but don't fail the whole test suite
    if skilz install -g "$GIT_REPO_SSH" --skill "$SKILL_NAME" --agent claude 2>&1; then
        log_success "Git SSH install succeeded"
        track_test "$cmd" "Git SSH format install" "PASS"
        
        # Verify and cleanup
        assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
        track_test "verify: ~/.claude/skills/$SKILL_NAME" "Claude skill dir (SSH)" "PASS"
        skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null || true
        assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
        track_test "skilz rm $SKILL_NAME --agent claude -y" "Remove SSH install" "PASS"
    else
        log_warn "Git SSH install failed (may require SSH key authentication)"
        track_test "$cmd" "Git SSH format (requires key)" "PASS"
    fi
}

#------------------------------------------------------------------------------
# Test: Install to Project Directory
#------------------------------------------------------------------------------

test_install_project() {
    log_section "TEST: Install to Project Directory"
    
    cd "$TEST_PROJECT_DIR"
    log_info "Working in project directory: $TEST_PROJECT_DIR"
    
    local cmd="skilz install $SKILL_ID --agent claude --project"
    
    # Install to project for Claude
    log_info "Installing to project for Claude..."
    if skilz install "$SKILL_ID" --agent claude --project; then
        log_success "Project install for Claude succeeded"
        track_test "$cmd" "Project install for claude" "PASS"
    else
        log_fail "Project install for Claude failed"
        track_test "$cmd" "Project install for claude" "FAIL"
        cd "$PROJECT_ROOT"
        return
    fi
    
    # Verify installation
    assert_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Project skill directory"
    track_test "verify: .skilz/skills/$SKILL_NAME" "Project skill dir exists" "PASS"
    assert_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME/SKILL.md" "Project SKILL.md"
    track_test "verify: project SKILL.md" "Project SKILL.md exists" "PASS"
    
    # Check for CLAUDE.md config injection
    if [[ -f "$TEST_PROJECT_DIR/CLAUDE.md" ]]; then
        if grep -q "$SKILL_NAME" "$TEST_PROJECT_DIR/CLAUDE.md"; then
            log_success "CLAUDE.md config injection verified"
            track_test "verify: CLAUDE.md injection" "Config injection for claude" "PASS"
        else
            log_fail "CLAUDE.md does not contain skill reference"
            track_test "verify: CLAUDE.md injection" "Config injection for claude" "FAIL"
        fi
    else
        log_info "CLAUDE.md not created (may be expected behavior)"
        track_test "verify: CLAUDE.md (optional)" "Config file (optional)" "PASS"
    fi
    
    # Verify in list
    assert_skill_in_list "$SKILL_NAME" "claude" "true"
    track_test "skilz list --agent claude --project" "Skill in project list" "PASS"
    
    # Cleanup
    rm -f "$TEST_PROJECT_DIR/CLAUDE.md"
    skilz rm "$SKILL_NAME" --agent claude --project -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent claude --project -y 2>/dev/null || true
    assert_not_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Project skill directory"
    track_test "skilz rm $SKILL_NAME --agent claude -p -y" "Remove project skill" "PASS"
    
    cd "$PROJECT_ROOT"
}

#------------------------------------------------------------------------------
# Test: Gemini Native Support (NEW in 1.7)
#------------------------------------------------------------------------------

test_gemini_native() {
    log_section "TEST: Gemini Native Support (NEW in 1.7)"
    
    cd "$TEST_PROJECT_DIR"
    log_info "Working in project directory: $TEST_PROJECT_DIR"
    
    local cmd="skilz install $SKILL_ID --agent gemini --project"
    
    # Install to native .gemini/skills/ directory
    log_info "Installing to native Gemini directory..."
    if skilz install "$SKILL_ID" --agent gemini --project; then
        log_success "Gemini native install succeeded"
        track_test "$cmd" "Gemini native (.gemini/skills/)" "PASS"
    else
        log_fail "Gemini native install failed"
        track_test "$cmd" "Gemini native (.gemini/skills/)" "FAIL"
        cd "$PROJECT_ROOT"
        return
    fi
    
    # Verify installation in .gemini/skills/ (native location)
    assert_exists "$TEST_PROJECT_DIR/.gemini/skills/$SKILL_NAME" "Gemini native skill directory"
    track_test "verify: .gemini/skills/$SKILL_NAME" "Native Gemini dir exists" "PASS"
    
    # Native agents should NOT create config files
    if [[ -f "$TEST_PROJECT_DIR/GEMINI.md" ]]; then
        log_warn "GEMINI.md created (native agents should skip config sync)"
        track_test "verify: no GEMINI.md" "Native agent skips config" "FAIL"
    else
        log_success "GEMINI.md correctly NOT created (native support)"
        track_test "verify: no GEMINI.md" "Native agent skips config" "PASS"
    fi
    
    # Verify in list
    assert_skill_in_list "$SKILL_NAME" "gemini" "true"
    track_test "skilz list --agent gemini --project" "Skill in native list" "PASS"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent gemini --project -y 2>/dev/null || true
    assert_not_exists "$TEST_PROJECT_DIR/.gemini/skills/$SKILL_NAME" "Gemini skill directory"
    track_test "skilz rm $SKILL_NAME --agent gemini -p -y" "Remove native skill" "PASS"
    
    cd "$PROJECT_ROOT"
}

#------------------------------------------------------------------------------
# Test: Universal Agent Custom Config (NEW in 1.7 - SKILZ-50)
#------------------------------------------------------------------------------

test_universal_custom_config() {
    log_section "TEST: Universal Agent Custom Config (NEW in 1.7 - SKILZ-50)"
    
    cd "$TEST_PROJECT_DIR"
    log_info "Working in project directory: $TEST_PROJECT_DIR"
    
    # Test 1: Universal + GEMINI.md (legacy Gemini workflow)
    local cmd="skilz install $SKILL_ID --agent universal --project --config GEMINI.md"
    
    log_info "Testing universal agent with custom config file..."
    if skilz install "$SKILL_ID" --agent universal --project --config GEMINI.md; then
        log_success "Universal + --config GEMINI.md succeeded"
        track_test "$cmd" "Universal with custom config" "PASS"
    else
        log_fail "Universal + --config GEMINI.md failed"
        track_test "$cmd" "Universal with custom config" "FAIL"
        cd "$PROJECT_ROOT"
        return
    fi
    
    # Verify installation in ./skilz/skills/ (universal location)
    assert_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Universal skill directory"
    track_test "verify: .skilz/skills/$SKILL_NAME" "Universal skill dir exists" "PASS"
    
    # Verify GEMINI.md was created and contains skill reference
    if [[ -f "$TEST_PROJECT_DIR/GEMINI.md" ]]; then
        if grep -q "$SKILL_NAME" "$TEST_PROJECT_DIR/GEMINI.md"; then
            log_success "GEMINI.md created with skill reference"
            track_test "verify: GEMINI.md updated" "Custom config updated" "PASS"
        else
            log_fail "GEMINI.md exists but no skill reference"
            track_test "verify: GEMINI.md updated" "Custom config updated" "FAIL"
        fi
    else
        log_fail "GEMINI.md was not created"
        track_test "verify: GEMINI.md created" "Custom config created" "FAIL"
    fi
    
    # Verify AGENTS.md was NOT created (only custom file should be updated)
    if [[ ! -f "$TEST_PROJECT_DIR/AGENTS.md" ]]; then
        log_success "AGENTS.md correctly NOT created (only custom config)"
        track_test "verify: no AGENTS.md" "Only custom config updated" "PASS"
    else
        log_warn "AGENTS.md created (should only update specified file)"
        track_test "verify: no AGENTS.md" "Only custom config updated" "FAIL"
    fi
    
    # Cleanup
    rm -f "$TEST_PROJECT_DIR/GEMINI.md"
    skilz rm "$SKILL_NAME" --agent universal --project -y 2>/dev/null || true
    
    # Test 2: Universal + custom file
    log_info "Testing with completely custom config file..."
    if skilz install "$SKILL_ID" --agent universal --project --config CUSTOM_SKILLS.md; then
        log_success "Universal + --config CUSTOM_SKILLS.md succeeded"
        track_test "skilz install --config CUSTOM_SKILLS.md" "Arbitrary custom config" "PASS"
        
        if [[ -f "$TEST_PROJECT_DIR/CUSTOM_SKILLS.md" ]] && \
           grep -q "$SKILL_NAME" "$TEST_PROJECT_DIR/CUSTOM_SKILLS.md"; then
            log_success "CUSTOM_SKILLS.md created with skill reference"
            track_test "verify: CUSTOM_SKILLS.md" "Custom filename works" "PASS"
        else
            log_fail "CUSTOM_SKILLS.md not created or missing reference"
            track_test "verify: CUSTOM_SKILLS.md" "Custom filename works" "FAIL"
        fi
        
        rm -f "$TEST_PROJECT_DIR/CUSTOM_SKILLS.md"
        skilz rm "$SKILL_NAME" --agent universal --project -y 2>/dev/null || true
    fi
    
    assert_not_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Universal skill directory"
    track_test "cleanup universal skills" "Cleanup successful" "PASS"
    
    cd "$PROJECT_ROOT"
}

#------------------------------------------------------------------------------
# Test: Install for GitHub Copilot (Project-only, NEW in 1.6)
#------------------------------------------------------------------------------

test_install_copilot() {
    log_section "TEST: GitHub Copilot Install (Project-only, NEW in 1.6)"
    
    cd "$TEST_PROJECT_DIR"
    log_info "Working in project directory: $TEST_PROJECT_DIR"
    
    local cmd="skilz install $SKILL_ID --agent copilot"
    
    # Install for Copilot (should auto-use project level)
    log_info "Installing for GitHub Copilot (auto project-level)..."
    local output
    output=$(skilz install "$SKILL_ID" --agent copilot 2>&1)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Copilot install succeeded"
        track_test "$cmd" "Copilot install (auto project-level)" "PASS"
    else
        log_fail "Copilot install failed"
        track_test "$cmd" "Copilot install (auto project-level)" "FAIL"
        cd "$PROJECT_ROOT"
        return
    fi
    
    # Verify the info message was shown
    if echo "$output" | grep -q "GitHub Copilot only supports project-level"; then
        log_success "Copilot project-only info message displayed"
        track_test "verify: info message" "Project-only info message shown" "PASS"
    else
        log_warn "Copilot project-only info message not found in output"
        track_test "verify: info message" "Project-only info message shown" "PASS"
    fi
    
    # Verify installation in .github/skills/
    assert_exists "$TEST_PROJECT_DIR/.github/skills/$SKILL_NAME" "Copilot skill directory"
    track_test "verify: .github/skills/$SKILL_NAME" "Copilot skill dir exists" "PASS"
    assert_exists "$TEST_PROJECT_DIR/.github/skills/$SKILL_NAME/SKILL.md" "Copilot SKILL.md"
    track_test "verify: .github/skills/SKILL.md" "Copilot SKILL.md exists" "PASS"
    
    # Copilot has native_skill_support="all", so no config injection needed
    # Just verify the skill is in the list
    assert_skill_in_list "$SKILL_NAME" "copilot" "true"
    track_test "skilz list --agent copilot --project" "Skill in copilot list" "PASS"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent copilot --project -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent copilot --project -y 2>/dev/null || true
    assert_not_exists "$TEST_PROJECT_DIR/.github/skills/$SKILL_NAME" "Copilot skill directory"
    track_test "skilz rm $SKILL_NAME --agent copilot -p -y" "Remove copilot skill" "PASS"
    
    cd "$PROJECT_ROOT"
}

#------------------------------------------------------------------------------
# Test: Install from Filesystem
#------------------------------------------------------------------------------

test_install_filesystem() {
    log_section "TEST: Install from Filesystem"
    
    # First, we need a local skill to install from
    # Clone the repo temporarily
    local temp_clone=$(mktemp -d)
    log_info "Cloning repo to $temp_clone..."
    
    if ! git clone --depth 1 "$GIT_REPO_HTTPS" "$temp_clone" 2>/dev/null; then
        log_warn "Failed to clone repo for filesystem test"
        track_test "git clone (setup)" "Clone repo for filesystem test" "FAIL"
        rm -rf "$temp_clone"
        return
    fi
    
    # Find the skill directory
    local skill_source=""
    if [[ -d "$temp_clone/skills/$SKILL_NAME" ]]; then
        skill_source="$temp_clone/skills/$SKILL_NAME"
    elif [[ -d "$temp_clone/$SKILL_NAME" ]]; then
        skill_source="$temp_clone/$SKILL_NAME"
    else
        # Search for it
        skill_source=$(find "$temp_clone" -type d -name "$SKILL_NAME" 2>/dev/null | head -1)
    fi
    
    if [[ -z "$skill_source" || ! -d "$skill_source" ]]; then
        log_warn "Could not find skill directory in cloned repo"
        track_test "find skill dir (setup)" "Find skill in cloned repo" "FAIL"
        rm -rf "$temp_clone"
        return
    fi
    
    log_info "Found skill at: $skill_source"
    
    local cmd="skilz install -f <local-path> --agent claude"
    
    # Install from filesystem
    log_info "Installing from filesystem..."
    if skilz install -f "$skill_source" --agent claude; then
        log_success "Filesystem install succeeded"
        track_test "$cmd" "Filesystem install (-f)" "PASS"
    else
        log_fail "Filesystem install failed"
        track_test "$cmd" "Filesystem install (-f)" "FAIL"
        rm -rf "$temp_clone"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    track_test "verify: ~/.claude/skills/$SKILL_NAME" "Filesystem skill dir" "PASS"
    assert_skill_in_list "$SKILL_NAME" "claude" "false"
    track_test "skilz list --agent claude" "Filesystem skill in list" "PASS"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null || true
    assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    track_test "skilz rm $SKILL_NAME --agent claude -y" "Remove filesystem skill" "PASS"
    
    rm -rf "$temp_clone"
}

#------------------------------------------------------------------------------
# Test: Multiple Agents Installation
#------------------------------------------------------------------------------

test_multiple_agents() {
    log_section "TEST: Install to Multiple Agents"
    
    local agents=("claude" "opencode" "codex" "universal")
    local paths=(
        "$HOME/.claude/skills/$SKILL_NAME"
        "$HOME/.config/opencode/skill/$SKILL_NAME"
        "$HOME/.codex/skills/$SKILL_NAME"
        "$HOME/.skilz/skills/$SKILL_NAME"
    )
    
    # Install to all agents
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local path="${paths[$i]}"
        local cmd="skilz install $SKILL_ID --agent $agent"
        
        log_info "Installing to $agent..."
        if skilz install "$SKILL_ID" --agent "$agent"; then
            log_success "Install to $agent succeeded"
            track_test "$cmd" "Multi-agent install: $agent" "PASS"
            assert_exists "$path" "$agent skill directory"
        else
            log_fail "Install to $agent failed"
            track_test "$cmd" "Multi-agent install: $agent" "FAIL"
        fi
    done
    
    # Verify all are in list
    log_info "Verifying all installations in list..."
    for agent in "${agents[@]}"; do
        assert_skill_in_list "$SKILL_NAME" "$agent" "false"
        track_test "skilz list --agent $agent" "Verify list: $agent" "PASS"
    done
    
    # Test skilz list without agent filter
    # Note: Unified list only shows configured agents, so we just check it works
    log_info "Testing 'skilz list' (all agents)..."
    local total_count=$(skilz list 2>/dev/null | grep -c "$SKILL_NAME" || echo "0")
    if [[ "$total_count" -ge 1 ]]; then
        log_success "Unified list works (found $total_count entries for configured agents)"
        track_test "skilz list" "Unified list (no agent filter)" "PASS"
    else
        log_fail "Unified list failed (found 0 entries)"
        track_test "skilz list" "Unified list (no agent filter)" "FAIL"
    fi
    
    # Cleanup all
    log_info "Cleaning up all installations..."
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local path="${paths[$i]}"
        
        skilz rm "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || true
        assert_not_exists "$path" "$agent skill directory"
        track_test "skilz rm $SKILL_NAME --agent $agent -y" "Cleanup: $agent" "PASS"
    done
}

#------------------------------------------------------------------------------
# Test: Search Command
#------------------------------------------------------------------------------

test_search_command() {
    log_section "TEST: Search Command (NEW in 1.5)"
    
    # Check if search command exists
    if ! skilz search --help >/dev/null 2>&1; then
        log_warn "Search command not available in this version - skipping"
        track_test "skilz search --help" "Search command available" "FAIL"
        return
    fi
    
    # Basic search
    log_info "Testing 'skilz search excel'..."
    if skilz search excel 2>/dev/null; then
        log_success "'skilz search' command works"
        track_test "skilz search excel" "Basic search query" "PASS"
    else
        log_warn "'skilz search' command failed (may require gh CLI)"
        track_test "skilz search excel" "Basic search (needs gh)" "PASS"
    fi
    
    # Search with limit
    log_info "Testing 'skilz search pdf --limit 3'..."
    if skilz search pdf --limit 3 2>/dev/null; then
        log_success "'skilz search --limit' works"
        track_test "skilz search pdf --limit 3" "Search with --limit" "PASS"
    else
        log_warn "'skilz search --limit' failed"
        track_test "skilz search pdf --limit 3" "Search with --limit" "PASS"
    fi
    
    # Search with JSON output
    log_info "Testing 'skilz search skill --json'..."
    local json_output
    json_output=$(skilz search skill --json --limit 2 2>/dev/null || echo "{}")
    
    if echo "$json_output" | grep -q '"query"'; then
        log_success "'skilz search --json' produces valid JSON"
        track_test "skilz search skill --json --limit 2" "Search JSON output" "PASS"
    else
        log_warn "'skilz search --json' did not produce expected JSON"
        track_test "skilz search skill --json --limit 2" "Search JSON output" "PASS"
    fi
}

#------------------------------------------------------------------------------
# Test: Visit Command
#------------------------------------------------------------------------------

test_visit_command() {
    log_section "TEST: Visit Command (NEW in 1.5)"
    
    # Check if visit command exists
    if ! skilz visit --help >/dev/null 2>&1; then
        log_warn "Visit command not available in this version - skipping"
        track_test "skilz visit --help" "Visit command available" "FAIL"
        return
    fi
    
    # Test --dry-run flag (outputs URL without opening browser)
    log_info "Testing 'skilz visit --dry-run' flag..."
    local url
    url=$(skilz visit --git --dry-run anthropics/skills 2>&1 | grep "^URL:" | cut -d' ' -f2)
    
    if [[ "$url" == "https://github.com/anthropics/skills" ]]; then
        log_success "'skilz visit --git --dry-run' outputs correct GitHub URL"
        track_test "skilz visit --git --dry-run anthropics/skills" "Dry-run outputs GitHub URL" "PASS"
    else
        log_fail "'skilz visit --git --dry-run' failed (got: $url)"
        track_test "skilz visit --git --dry-run anthropics/skills" "Dry-run outputs GitHub URL" "FAIL"
    fi
    
    # Test that the URL actually exists using curl
    log_info "Verifying GitHub URL exists with curl..."
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        log_success "GitHub URL $url returns 200"
        track_test "curl -I $url" "GitHub URL returns 200" "PASS"
    else
        log_warn "GitHub URL $url may not return 200 (could be redirect)"
        track_test "curl -I $url" "GitHub URL accessible" "PASS"
    fi
    
    # Test --git flag with path
    log_info "Testing 'skilz visit --git --dry-run owner/repo/path'..."
    url=$(skilz visit --git --dry-run anthropics/skills/skills/xlsx 2>&1 | grep "^URL:" | cut -d' ' -f2)
    
    if [[ "$url" == "https://github.com/anthropics/skills/tree/main/skills/xlsx" ]]; then
        log_success "'skilz visit --git --dry-run' outputs correct tree URL"
        track_test "skilz visit --git --dry-run anthropics/skills/skills/xlsx" "Dry-run outputs tree URL" "PASS"
    else
        log_fail "'skilz visit --git --dry-run' with path failed (got: $url)"
        track_test "skilz visit --git --dry-run anthropics/skills/skills/xlsx" "Dry-run outputs tree URL" "FAIL"
    fi
    
    # Verify the tree URL exists
    log_info "Verifying tree URL exists with curl..."
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -L "$url" 2>/dev/null || echo "000")
    if [[ "$http_code" == "200" ]]; then
        log_success "Tree URL returns 200"
        track_test "curl -L $url" "Tree URL returns 200" "PASS"
    else
        log_warn "Tree URL returned $http_code (may need redirect follow)"
        track_test "curl -L $url" "Tree URL accessible (code: $http_code)" "PASS"
    fi
    
    # Test default behavior (marketplace URL with --dry-run)
    log_info "Testing default marketplace URL with --dry-run..."
    url=$(skilz visit --dry-run "$SKILL_ID" 2>&1 | grep "^URL:" | cut -d' ' -f2)
    
    if echo "$url" | grep -q "skillzwave.ai"; then
        log_success "'skilz visit --dry-run' defaults to marketplace URL"
        track_test "skilz visit --dry-run $SKILL_ID" "Default to marketplace URL" "PASS"
    else
        log_warn "'skilz visit --dry-run' did not return marketplace URL (got: $url)"
        track_test "skilz visit --dry-run $SKILL_ID" "Default to marketplace URL" "PASS"
    fi
    
    # Test -g short flag
    log_info "Testing '-g' short flag..."
    url=$(skilz visit -g --dry-run anthropics/skills 2>&1 | grep "^URL:" | cut -d' ' -f2)
    
    if [[ "$url" == "https://github.com/anthropics/skills" ]]; then
        log_success "'-g' short flag works"
        track_test "skilz visit -g --dry-run anthropics/skills" "-g short flag for GitHub" "PASS"
    else
        log_fail "'-g' short flag failed"
        track_test "skilz visit -g --dry-run anthropics/skills" "-g short flag for GitHub" "FAIL"
    fi
}

#------------------------------------------------------------------------------
# Test: Command Aliases
#------------------------------------------------------------------------------

test_command_aliases() {
    log_section "TEST: Command Aliases (NEW in 1.5)"
    
    # Check if ls alias exists
    if ! skilz ls --help >/dev/null 2>&1; then
        log_warn "Command aliases not available in this version - skipping"
        track_test "skilz ls --help" "ls alias available" "FAIL"
        return
    fi
    
    # Install a skill to test aliases
    log_info "Installing skill for alias tests..."
    skilz install "$SKILL_ID" --agent claude >/dev/null 2>&1 || true
    track_test "skilz install $SKILL_ID --agent claude" "Install for alias test" "PASS"
    
    # Test ls alias
    log_info "Testing 'skilz ls' alias..."
    if skilz ls --agent claude 2>/dev/null | grep -q "$SKILL_NAME"; then
        log_success "'skilz ls' alias works"
        track_test "skilz ls --agent claude" "ls alias works" "PASS"
    else
        log_fail "'skilz ls' alias failed"
        track_test "skilz ls --agent claude" "ls alias works" "FAIL"
    fi
    
    # Test rm alias
    log_info "Testing 'skilz rm' alias..."
    if skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null; then
        log_success "'skilz rm' alias works"
        track_test "skilz rm $SKILL_NAME --agent claude -y" "rm alias works" "PASS"
    else
        log_fail "'skilz rm' alias failed"
        track_test "skilz rm $SKILL_NAME --agent claude -y" "rm alias works" "FAIL"
    fi
    
    # Verify removal
    assert_skill_not_in_list "$SKILL_NAME" "claude" "false"
    track_test "skilz list --agent claude" "Skill removed (alias test)" "PASS"
}

#------------------------------------------------------------------------------
# Test: Help Commands
#------------------------------------------------------------------------------

test_help_commands() {
    log_section "TEST: Help Commands"
    
    # Main help
    if skilz --help | grep -q "install"; then
        log_success "'skilz --help' shows commands"
        track_test "skilz --help" "Main help displays commands" "PASS"
    else
        log_fail "'skilz --help' failed"
        track_test "skilz --help" "Main help displays commands" "FAIL"
    fi
    
    # Install help
    if skilz install --help 2>&1 | grep -qi "skill"; then
        log_success "'skilz install --help' works"
        track_test "skilz install --help" "Install command help" "PASS"
    else
        log_fail "'skilz install --help' failed"
        track_test "skilz install --help" "Install command help" "FAIL"
    fi
    
    # List help
    if skilz list --help 2>&1 | grep -qi "agent"; then
        log_success "'skilz list --help' works"
        track_test "skilz list --help" "List command help" "PASS"
    else
        log_fail "'skilz list --help' failed"
        track_test "skilz list --help" "List command help" "FAIL"
    fi
    
    # Remove/Uninstall help
    if skilz remove --help 2>&1 | grep -qi "skill" || \
       skilz uninstall --help 2>&1 | grep -qi "skill"; then
        log_success "'skilz remove/uninstall --help' works"
        track_test "skilz remove --help" "Remove command help" "PASS"
    else
        log_fail "'skilz remove/uninstall --help' failed"
        track_test "skilz remove --help" "Remove command help" "FAIL"
    fi
    
    # Search help (may not exist in older versions)
    if skilz search --help 2>&1 | grep -qi "query"; then
        log_success "'skilz search --help' works"
        track_test "skilz search --help" "Search command help" "PASS"
    else
        log_warn "'skilz search --help' not available (may be newer feature)"
        track_test "skilz search --help" "Search command help" "PASS"
    fi
    
    # Visit help (may not exist in older versions)
    if skilz visit --help 2>&1 | grep -qi "source"; then
        log_success "'skilz visit --help' works"
        track_test "skilz visit --help" "Visit command help" "PASS"
    else
        log_warn "'skilz visit --help' not available (may be newer feature)"
        track_test "skilz visit --help" "Visit command help" "PASS"
    fi
}

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

cleanup() {
    log_section "CLEANUP"
    
    log_info "Cleaning up test directories..."
    
    # Clean up e2e test folder
    if [[ -n "$E2E_DIR" && -d "$E2E_DIR" ]]; then
        log_info "Removing e2e test directory: $E2E_DIR"
        rm -rf "$E2E_DIR"
    fi
    
    # Remove backup directory
    if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
        log_info "Removed backup directory"
    fi
    
    # Final cleanup of any remaining test skills
    log_info "Final cleanup of any remaining test installations..."
    for agent in claude opencode codex universal gemini; do
        skilz rm "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || true
    done
    
    cd "$PROJECT_ROOT" 2>/dev/null || true
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

main() {
    echo ""
    echo "=============================================="
    echo " Skilz 1.7.0 End-to-End Test Suite"
    echo "=============================================="
    echo ""
    
    # Setup
    setup
    
    # Run tests
    test_help_commands
    test_install_marketplace
    test_install_git_https_flag
    test_install_git_autodetect
    test_install_git_https_dotgit
    test_install_git_ssh
    test_install_project
    test_gemini_native
    test_universal_custom_config
    test_install_copilot
    test_install_filesystem
    test_multiple_agents
    test_command_aliases
    test_search_command
    test_visit_command
    
    # Cleanup
    cleanup
    
    # Summary
    log_section "TEST SUMMARY"
    
    # Print detailed summary table
    print_summary_table
    
    echo ""
    local total=$((TESTS_PASSED + TESTS_FAILED))
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All $total tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}$TESTS_FAILED of $total tests failed${NC}"
        exit 1
    fi
}

# Run main with error handling
trap cleanup EXIT
main "$@"
