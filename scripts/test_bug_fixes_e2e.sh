#!/usr/bin/env bash
#
# E2E Tests for Bug Fixes: SKILZ-64 and SKILZ-65
#
# SKILZ-64: Temp directory warning during git installs should not appear
# SKILZ-65: --config flag should work for git installs
#
# These tests should FAIL initially, then PASS after fixes
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test data
TEST_SKILL_URL="https://github.com/SpillwaveSolutions/sdd-skill"
TEST_SKILL_NAME="sdd"
TEST_PROJECT_DIR="/tmp/skilz-bug-test-$(date +%s)"
TEST_CONFIG_FILE="TEST_CONFIG.md"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local expected_exit="$3"
    local description="$4"

    log_info "Running: $test_name"
    log_info "Command: $test_cmd"
    log_info "Expected: $description"

    # Run command and capture output
    local output
    local exit_code
    output=$(eval "$test_cmd" 2>&1) || exit_code=$?

    if [[ "$expected_exit" == "success" && $exit_code -eq 0 ]]; then
        log_success "$test_name: $description"
        return 0
    elif [[ "$expected_exit" == "failure" && $exit_code -ne 0 ]]; then
        log_success "$test_name: $description"
        return 0
    else
        log_failure "$test_name: Expected $expected_exit but got exit code $exit_code"
        echo "Output: $output"
        return 1
    fi
}

setup_test_env() {
    log_info "Setting up test environment..."

    # Create test project directory
    mkdir -p "$TEST_PROJECT_DIR"
    cd "$TEST_PROJECT_DIR"

    # Initialize as git repo (some tests need this)
    git init --quiet
    git config user.name "Test User"
    git config user.email "test@example.com"

    log_info "Test environment ready: $TEST_PROJECT_DIR"
}

cleanup_test_env() {
    log_info "Cleaning up test environment..."
    cd /
    rm -rf "$TEST_PROJECT_DIR"
    log_info "Cleanup complete"
}

# ============================================================================
# BUG 1 TESTS: SKILZ-64 - Temp Directory Warning During Git Installs
# ============================================================================

test_bug1_git_install_no_temp_warning() {
    # Test that git installs don't show temp directory warnings
    # This should PASS after the fix

    local test_name="BUG1_GIT_NO_TEMP_WARNING"
    local cmd="skilz install $TEST_SKILL_URL --project --agent gemini 2>&1"
    local expected_exit="success"
    local description="Git install should not show temp directory name warnings"

    log_info "Testing Bug 1: Git installs should not warn about temp directories"

    # Run the install command
    local output
    output=$(eval "$cmd")

    # Check for temp directory warnings (should NOT be present after fix)
    if echo "$output" | grep -q "doesn't match skill name"; then
        log_failure "$test_name: Found temp directory warning (bug still present)"
        echo "Output: $output"
        return 1
    else
        log_success "$test_name: No temp directory warnings found"
        return 0
    fi
}

test_bug1_local_install_shows_warning() {
    # Test that local installs STILL show warnings for permanent directories
    # This should PASS both before and after the fix

    local test_name="BUG1_LOCAL_STILL_WARNS"
    local description="Local installs should still warn about mismatched directory names"

    log_info "Testing Bug 1: Local installs should still warn for permanent directories"

    # Create a local skill directory with wrong name
    local wrong_dir="wrong-skill-name"
    mkdir -p "$wrong_dir"
    echo "name: $TEST_SKILL_NAME" > "$wrong_dir/SKILL.md"
    echo "description: Test skill" >> "$wrong_dir/SKILL.md"

    local cmd="skilz install -f $wrong_dir --project --agent gemini 2>&1"
    local output
    output=$(eval "$cmd")

    # Clean up
    rm -rf "$wrong_dir"

    # Check for warnings (should be present for local installs)
    if echo "$output" | grep -q "doesn't match skill name"; then
        log_success "$test_name: Local install correctly shows warning for mismatched names"
        return 0
    else
        log_failure "$test_name: Local install should warn about mismatched directory names"
        echo "Output: $output"
        return 1
    fi
}

# ============================================================================
# BUG 2 TESTS: SKILZ-65 - --config Flag Not Working for Git Installs
# ============================================================================

test_bug2_git_config_flag_works() {
    # Test that --config flag works for git installs
    # This should FAIL before fix, PASS after fix

    local test_name="BUG2_GIT_CONFIG_WORKS"
    local cmd="skilz install $TEST_SKILL_URL --project --agent gemini --config $TEST_CONFIG_FILE"
    local expected_exit="success"
    local description="Git install with --config should create/update config file"

    log_info "Testing Bug 2: Git installs should honor --config flag"

    # Run the install command
    if eval "$cmd"; then
        # Check if config file was created/updated
        if [[ -f "$TEST_CONFIG_FILE" ]]; then
            # Check if it contains skill reference
            if grep -q "$TEST_SKILL_NAME" "$TEST_CONFIG_FILE"; then
                log_success "$test_name: --config flag worked for git install"
                return 0
            else
                log_failure "$test_name: Config file created but doesn't contain skill reference"
                cat "$TEST_CONFIG_FILE"
                return 1
            fi
        else
            log_failure "$test_name: --config flag ignored - file not created"
            return 1
        fi
    else
        log_failure "$test_name: Git install with --config failed"
        return 1
    fi
}

test_bug2_git_config_vs_force_config() {
    # Test that --config behaves like --force-config but with custom file
    # This should FAIL before fix, PASS after fix

    local test_name="BUG2_CONFIG_VS_FORCE"
    local description="--config should work like --force-config with custom file"

    log_info "Testing Bug 2: --config vs --force-config behavior"

    # Clean up any existing files
    rm -f "$TEST_CONFIG_FILE" "AGENTS.md"

    # Test 1: --force-config should work (baseline)
    log_info "Testing --force-config (should work)..."
    if skilz install "$TEST_SKILL_URL" --project --agent gemini --force-config; then
        if [[ -f "AGENTS.md" ]] && grep -q "$TEST_SKILL_NAME" "AGENTS.md"; then
            log_success "Baseline: --force-config works"
        else
            log_failure "Baseline: --force-config doesn't work"
            return 1
        fi
    else
        log_failure "Baseline: --force-config command failed"
        return 1
    fi

    # Clean up for next test
    rm -f "$TEST_CONFIG_FILE" "AGENTS.md"

    # Test 2: --config should work like --force-config but with custom file
    log_info "Testing --config (should work after fix)..."
    if skilz install "$TEST_SKILL_URL" --project --agent gemini --config "$TEST_CONFIG_FILE"; then
        if [[ -f "$TEST_CONFIG_FILE" ]] && grep -q "$TEST_SKILL_NAME" "$TEST_CONFIG_FILE"; then
            # Also verify AGENTS.md was NOT touched (since we specified custom file)
            if [[ ! -f "AGENTS.md" ]]; then
                log_success "$test_name: --config works like --force-config with custom file"
                return 0
            else
                log_failure "$test_name: --config created custom file but also touched default file"
                return 1
            fi
        else
            log_failure "$test_name: --config flag ignored - custom file not created properly"
            return 1
        fi
    else
        log_failure "$test_name: Git install with --config failed"
        return 1
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    log_info "Starting E2E Tests for SKILZ-64 and SKILZ-65 Bug Fixes"
    log_info "These tests should FAIL initially, then PASS after fixes"
    echo

    # Setup
    setup_test_env

    # Bug 1 Tests
    echo "=========================================="
    log_info "Testing BUG 1: SKILZ-64 - Temp Directory Warnings"
    echo "=========================================="

    test_bug1_git_install_no_temp_warning
    test_bug1_local_install_shows_warning

    echo
    echo "=========================================="
    log_info "Testing BUG 2: SKILZ-65 - --config Flag for Git Installs"
    echo "=========================================="

    test_bug2_git_config_flag_works
    test_bug2_git_config_vs_force_config

    # Cleanup
    cleanup_test_env

    # Results
    echo
    echo "=========================================="
    log_info "Test Results Summary"
    echo "=========================================="
    log_info "Tests Passed: $TESTS_PASSED"
    log_info "Tests Failed: $TESTS_FAILED"
    log_info "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_failure "Some tests failed. Fix the bugs and run again."
        exit 1
    fi
}

# Run main function
main "$@"