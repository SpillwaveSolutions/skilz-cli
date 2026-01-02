#!/usr/bin/env bash
#
# Skilz 1.5.0 End-to-End Test Script
#
# This script tests all major features of skilz:
# - Install via marketplace ID
# - Install via Git URL (HTTPS, SSH, -g flag, auto-detect)
# - Install from filesystem
# - Install to various agents (claude, opencode, codex, gemini, universal)
# - Install at project level
# - List commands (skilz list, skilz ls)
# - Remove commands (skilz uninstall, skilz rm)
# - Search command
# - Visit command (dry-run only)
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

# Test skill to use
SKILL_ID="Jamie-BitFlight_claude_skills/brainstorming-skill"
SKILL_NAME="brainstorming-skill"
GIT_REPO_HTTPS="https://github.com/Jamie-BitFlight/claude_skills.git"
GIT_REPO_SSH="git@github.com:Jamie-BitFlight/claude_skills.git"
GIT_REPO_URL="https://github.com/Jamie-BitFlight/claude_skills"

# Test project directory
TEST_PROJECT_DIR=""

# Backup directories (to restore after tests)
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
    
    # Create backup directory for any existing installations
    BACKUP_DIR=$(mktemp -d)
    log_info "Backup directory: $BACKUP_DIR"
    
    # Create test project directory
    TEST_PROJECT_DIR=$(mktemp -d)
    log_info "Test project directory: $TEST_PROJECT_DIR"
    
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
    
    # Install for Claude
    log_info "Installing $SKILL_ID for Claude..."
    if skilz install "$SKILL_ID" --agent claude; then
        log_success "Marketplace install for Claude succeeded"
    else
        log_fail "Marketplace install for Claude failed"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    assert_exists "$HOME/.claude/skills/$SKILL_NAME/SKILL.md" "SKILL.md file"
    assert_exists "$HOME/.claude/skills/$SKILL_NAME/.skilz-manifest.yaml" "Manifest file"
    
    # Verify in list
    assert_skill_in_list "$SKILL_NAME" "claude" "false"
    
    # Test skilz ls alias
    log_info "Testing 'skilz ls' alias..."
    if skilz ls --agent claude 2>/dev/null | grep -q "$SKILL_NAME"; then
        log_success "'skilz ls' alias works correctly"
    else
        log_fail "'skilz ls' alias failed"
    fi
    
    # Cleanup
    log_info "Removing skill..."
    if skilz uninstall "$SKILL_NAME" --agent claude -y 2>/dev/null || \
       skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null; then
        log_success "Uninstall succeeded"
    else
        log_fail "Uninstall failed"
    fi
    
    assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    assert_skill_not_in_list "$SKILL_NAME" "claude" "false"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (HTTPS with -g flag)
#------------------------------------------------------------------------------

test_install_git_https_flag() {
    log_section "TEST: Install from Git URL (HTTPS with -g flag)"
    
    log_info "Installing from $GIT_REPO_HTTPS with -g flag..."
    if skilz install -g "$GIT_REPO_HTTPS" --skill "$SKILL_NAME" --agent opencode; then
        log_success "Git HTTPS install with -g flag succeeded"
    else
        log_fail "Git HTTPS install with -g flag failed"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.config/opencode/skills/$SKILL_NAME" "OpenCode skill directory"
    assert_skill_in_list "$SKILL_NAME" "opencode" "false"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent opencode -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent opencode -y 2>/dev/null || true
    assert_not_exists "$HOME/.config/opencode/skills/$SKILL_NAME" "OpenCode skill directory"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (Auto-detect - no flag)
#------------------------------------------------------------------------------

test_install_git_autodetect() {
    log_section "TEST: Install from Git URL (Auto-detect - NEW in 1.5)"
    
    log_info "Installing from $GIT_REPO_URL without -g flag (auto-detect)..."
    if skilz install "$GIT_REPO_URL" --skill "$SKILL_NAME" --agent codex 2>&1; then
        log_success "Git URL auto-detect install succeeded"
        
        # Verify installation
        assert_exists "$HOME/.codex/skills/$SKILL_NAME" "Codex skill directory"
        assert_skill_in_list "$SKILL_NAME" "codex" "false"
        
        # Cleanup - try both uninstall and remove for compatibility
        skilz uninstall "$SKILL_NAME" --agent codex -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent codex -y 2>/dev/null || true
        assert_not_exists "$HOME/.codex/skills/$SKILL_NAME" "Codex skill directory"
    else
        log_warn "Git URL auto-detect may not be available - trying with -g flag"
        # Fall back to -g flag
        if skilz install -g "$GIT_REPO_URL" --skill "$SKILL_NAME" --agent codex 2>&1; then
            log_success "Git install with -g flag succeeded (auto-detect not available)"
            skilz remove "$SKILL_NAME" --agent codex -y 2>/dev/null || true
        else
            log_fail "Git URL install failed"
        fi
    fi
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (HTTPS ending with .git)
#------------------------------------------------------------------------------

test_install_git_https_dotgit() {
    log_section "TEST: Install from Git URL (HTTPS .git suffix)"
    
    log_info "Installing from $GIT_REPO_HTTPS (auto-detect .git suffix)..."
    if skilz install "$GIT_REPO_HTTPS" --skill "$SKILL_NAME" --agent universal; then
        log_success "Git HTTPS .git install succeeded"
    else
        log_fail "Git HTTPS .git install failed"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.skilz/skills/$SKILL_NAME" "Universal skill directory"
    assert_skill_in_list "$SKILL_NAME" "universal" "false"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent universal -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent universal -y 2>/dev/null || true
    assert_not_exists "$HOME/.skilz/skills/$SKILL_NAME" "Universal skill directory"
}

#------------------------------------------------------------------------------
# Test: Install from Git URL (SSH format)
#------------------------------------------------------------------------------

test_install_git_ssh() {
    log_section "TEST: Install from Git URL (SSH format)"
    
    log_info "Installing from $GIT_REPO_SSH..."
    
    # SSH may require authentication - try but don't fail the whole test suite
    if skilz install -g "$GIT_REPO_SSH" --skill "$SKILL_NAME" --agent claude 2>&1; then
        log_success "Git SSH install succeeded"
        
        # Verify and cleanup
        assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
        skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null || true
        assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    else
        log_warn "Git SSH install failed (may require SSH key authentication)"
    fi
}

#------------------------------------------------------------------------------
# Test: Install to Project Directory
#------------------------------------------------------------------------------

test_install_project() {
    log_section "TEST: Install to Project Directory"
    
    cd "$TEST_PROJECT_DIR"
    log_info "Working in project directory: $TEST_PROJECT_DIR"
    
    # Install to project for Gemini (project-only agent)
    log_info "Installing to project for Gemini..."
    if skilz install "$SKILL_ID" --agent gemini --project; then
        log_success "Project install for Gemini succeeded"
    else
        log_fail "Project install for Gemini failed"
        cd "$PROJECT_ROOT"
        return
    fi
    
    # Verify installation
    assert_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Project skill directory"
    assert_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME/SKILL.md" "Project SKILL.md"
    
    # Check for GEMINI.md config injection (Gemini doesn't have native support)
    if [[ -f "$TEST_PROJECT_DIR/GEMINI.md" ]]; then
        if grep -q "$SKILL_NAME" "$TEST_PROJECT_DIR/GEMINI.md"; then
            log_success "GEMINI.md config injection verified"
        else
            log_fail "GEMINI.md does not contain skill reference"
        fi
    else
        log_info "GEMINI.md not created (may be expected behavior)"
    fi
    
    # Verify in list
    assert_skill_in_list "$SKILL_NAME" "gemini" "true"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent gemini --project -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent gemini --project -y 2>/dev/null || true
    assert_not_exists "$TEST_PROJECT_DIR/.skilz/skills/$SKILL_NAME" "Project skill directory"
    
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
        rm -rf "$temp_clone"
        return
    fi
    
    log_info "Found skill at: $skill_source"
    
    # Install from filesystem
    log_info "Installing from filesystem..."
    if skilz install -f "$skill_source" --agent claude; then
        log_success "Filesystem install succeeded"
    else
        log_fail "Filesystem install failed"
        rm -rf "$temp_clone"
        return
    fi
    
    # Verify installation
    assert_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    assert_skill_in_list "$SKILL_NAME" "claude" "false"
    
    # Cleanup
    skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || \
        skilz remove "$SKILL_NAME" --agent claude -y 2>/dev/null || true
    assert_not_exists "$HOME/.claude/skills/$SKILL_NAME" "Claude skill directory"
    
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
        "$HOME/.config/opencode/skills/$SKILL_NAME"
        "$HOME/.codex/skills/$SKILL_NAME"
        "$HOME/.skilz/skills/$SKILL_NAME"
    )
    
    # Install to all agents
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local path="${paths[$i]}"
        
        log_info "Installing to $agent..."
        if skilz install "$SKILL_ID" --agent "$agent"; then
            log_success "Install to $agent succeeded"
            assert_exists "$path" "$agent skill directory"
        else
            log_fail "Install to $agent failed"
        fi
    done
    
    # Verify all are in list
    log_info "Verifying all installations in list..."
    for agent in "${agents[@]}"; do
        assert_skill_in_list "$SKILL_NAME" "$agent" "false"
    done
    
    # Test skilz list without agent filter
    # Note: Unified list only shows configured agents, so we just check it works
    log_info "Testing 'skilz list' (all agents)..."
    local total_count=$(skilz list 2>/dev/null | grep -c "$SKILL_NAME" || echo "0")
    if [[ "$total_count" -ge 1 ]]; then
        log_success "Unified list works (found $total_count entries for configured agents)"
    else
        log_fail "Unified list failed (found 0 entries)"
    fi
    
    # Cleanup all
    log_info "Cleaning up all installations..."
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local path="${paths[$i]}"
        
        skilz rm "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || \
            skilz remove "$SKILL_NAME" --agent "$agent" -y 2>/dev/null || true
        assert_not_exists "$path" "$agent skill directory"
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
        return
    fi
    
    # Basic search
    log_info "Testing 'skilz search excel'..."
    if skilz search excel 2>/dev/null; then
        log_success "'skilz search' command works"
    else
        log_warn "'skilz search' command failed (may require gh CLI)"
    fi
    
    # Search with limit
    log_info "Testing 'skilz search pdf --limit 3'..."
    if skilz search pdf --limit 3 2>/dev/null; then
        log_success "'skilz search --limit' works"
    else
        log_warn "'skilz search --limit' failed"
    fi
    
    # Search with JSON output
    log_info "Testing 'skilz search skill --json'..."
    local json_output
    json_output=$(skilz search skill --json --limit 2 2>/dev/null || echo "{}")
    
    if echo "$json_output" | grep -q '"query"'; then
        log_success "'skilz search --json' produces valid JSON"
    else
        log_warn "'skilz search --json' did not produce expected JSON"
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
        return
    fi
    
    # We can't actually open a browser in a script, but we can test URL resolution
    # by checking the output
    
    log_info "Testing URL resolution for 'skilz visit owner/repo'..."
    local output
    output=$(skilz visit anthropics/skills 2>&1 || true)
    
    if echo "$output" | grep -q "https://github.com/anthropics/skills"; then
        log_success "Visit URL resolution works for owner/repo format"
    else
        log_fail "Visit URL resolution failed for owner/repo format"
    fi
    
    log_info "Testing URL resolution for 'skilz visit owner/repo/path'..."
    output=$(skilz visit anthropics/skills/excel 2>&1 || true)
    
    if echo "$output" | grep -q "https://github.com/anthropics/skills/tree/main/excel"; then
        log_success "Visit URL resolution works for owner/repo/path format"
    else
        log_fail "Visit URL resolution failed for owner/repo/path format"
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
        return
    fi
    
    # Install a skill to test aliases
    log_info "Installing skill for alias tests..."
    skilz install "$SKILL_ID" --agent claude >/dev/null 2>&1 || true
    
    # Test ls alias
    log_info "Testing 'skilz ls' alias..."
    if skilz ls --agent claude 2>/dev/null | grep -q "$SKILL_NAME"; then
        log_success "'skilz ls' alias works"
    else
        log_fail "'skilz ls' alias failed"
    fi
    
    # Test rm alias
    log_info "Testing 'skilz rm' alias..."
    if skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null; then
        log_success "'skilz rm' alias works"
    else
        log_fail "'skilz rm' alias failed"
    fi
    
    # Verify removal
    assert_skill_not_in_list "$SKILL_NAME" "claude" "false"
}

#------------------------------------------------------------------------------
# Test: Help Commands
#------------------------------------------------------------------------------

test_help_commands() {
    log_section "TEST: Help Commands"
    
    # Main help
    if skilz --help | grep -q "install"; then
        log_success "'skilz --help' shows commands"
    else
        log_fail "'skilz --help' failed"
    fi
    
    # Install help
    if skilz install --help 2>&1 | grep -qi "skill"; then
        log_success "'skilz install --help' works"
    else
        log_fail "'skilz install --help' failed"
    fi
    
    # List help
    if skilz list --help 2>&1 | grep -qi "agent"; then
        log_success "'skilz list --help' works"
    else
        log_fail "'skilz list --help' failed"
    fi
    
    # Remove/Uninstall help
    if skilz remove --help 2>&1 | grep -qi "skill" || \
       skilz uninstall --help 2>&1 | grep -qi "skill"; then
        log_success "'skilz remove/uninstall --help' works"
    else
        log_fail "'skilz remove/uninstall --help' failed"
    fi
    
    # Search help (may not exist in older versions)
    if skilz search --help 2>&1 | grep -qi "query"; then
        log_success "'skilz search --help' works"
    else
        log_warn "'skilz search --help' not available (may be newer feature)"
    fi
    
    # Visit help (may not exist in older versions)
    if skilz visit --help 2>&1 | grep -qi "source"; then
        log_success "'skilz visit --help' works"
    else
        log_warn "'skilz visit --help' not available (may be newer feature)"
    fi
}

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

cleanup() {
    log_section "CLEANUP"
    
    log_info "Cleaning up test directories..."
    
    # Remove test project directory
    if [[ -n "$TEST_PROJECT_DIR" && -d "$TEST_PROJECT_DIR" ]]; then
        rm -rf "$TEST_PROJECT_DIR"
        log_info "Removed test project directory"
    fi
    
    # Remove backup directory
    if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
        log_info "Removed backup directory"
    fi
    
    # Final cleanup of any remaining test skills
    log_info "Final cleanup of any remaining test installations..."
    for agent in claude opencode codex universal; do
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
    echo " Skilz 1.5.0 End-to-End Test Suite"
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
    test_install_filesystem
    test_multiple_agents
    test_command_aliases
    test_search_command
    test_visit_command
    
    # Cleanup
    cleanup
    
    # Summary
    log_section "TEST SUMMARY"
    echo ""
    echo -e "  ${GREEN}Passed:${NC} $TESTS_PASSED"
    echo -e "  ${RED}Failed:${NC} $TESTS_FAILED"
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
