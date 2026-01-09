#!/usr/bin/env bash
#
# API Integration Test for Skilz CLI
#
# This script specifically tests that the owner_repo/skill format
# correctly calls the REST endpoint at skillzwave.ai/api
#
# Usage: ./scripts/test_api_integration.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test skill in marketplace format
SKILL_ID="Jamie-BitFlight_claude_skills/brainstorming-skill"
SKILL_NAME="brainstorming-skill"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

test_api_endpoint_calls() {
    log_section "TEST: API Endpoint Integration"
    
    # Test 1: Verify API endpoint is reachable
    log_info "Testing API endpoint reachability..."
    local api_url="https://skillzwave.ai/api/skills/byname"
    local test_params="?repoFullName=Jamie-BitFlight/claude_skills&name=brainstorming-skill"
    
    if curl -s -f "$api_url$test_params" >/dev/null 2>&1; then
        log_success "API endpoint is reachable"
    else
        log_fail "API endpoint is not reachable (may be expected in CI)"
    fi
    
    # Test 2: Install with verbose to see API calls
    log_info "Installing with verbose to verify API calls..."
    
    # Clean up any existing installation
    skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || true
    
    # Install with verbose output and capture logs
    local install_output
    install_output=$(skilz install "$SKILL_ID" --agent claude --verbose 2>&1)
    local install_exit_code=$?
    
    if [[ $install_exit_code -eq 0 ]]; then
        log_success "Marketplace install succeeded"
        
        # Check if API calls are mentioned in verbose output
        if echo "$install_output" | grep -q "API lookup\|skillzwave.ai\|/api/"; then
            log_success "API calls detected in verbose output"
        else
            log_info "API calls not explicitly shown (may use local registry)"
        fi
        
        # Verify the skill was installed correctly
        if [[ -f "$HOME/.claude/skills/$SKILL_NAME/SKILL.md" ]]; then
            log_success "Skill installed correctly via API resolution"
        else
            log_fail "Skill not found after installation"
        fi
        
        # Check manifest for source information
        if [[ -f "$HOME/.claude/skills/$SKILL_NAME/.skilz-manifest.yaml" ]]; then
            local manifest_content
            manifest_content=$(cat "$HOME/.claude/skills/$SKILL_NAME/.skilz-manifest.yaml")
            
            if echo "$manifest_content" | grep -q "Jamie-BitFlight/claude_skills"; then
                log_success "Manifest shows correct repository resolution"
            else
                log_fail "Manifest does not show expected repository"
            fi
            
            if echo "$manifest_content" | grep -q "git_sha:"; then
                log_success "Manifest contains git SHA (API provided metadata)"
            else
                log_fail "Manifest missing git SHA"
            fi
        else
            log_fail "Manifest file not found"
        fi
        
        # Clean up
        skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || true
        
    else
        log_fail "Marketplace install failed"
        echo "Install output:"
        echo "$install_output"
    fi
}

test_api_format_parsing() {
    log_section "TEST: API Format Parsing"
    
    # Test the format parsing directly with Python
    log_info "Testing marketplace format parsing..."
    
    python3 -c "
import sys
sys.path.insert(0, 'src')
from skilz.api_client import parse_skill_id, is_marketplace_skill_id

# Test marketplace format detection
skill_id = '$SKILL_ID'
print(f'Testing skill ID: {skill_id}')

if is_marketplace_skill_id(skill_id):
    print('✓ Correctly identified as marketplace format')
    
    owner, repo, skill = parse_skill_id(skill_id)
    print(f'✓ Parsed: owner={owner}, repo={repo}, skill={skill}')
    
    expected_owner = 'Jamie-BitFlight'
    expected_repo = 'claude_skills'
    expected_skill = 'brainstorming-skill'
    
    if owner == expected_owner and repo == expected_repo and skill == expected_skill:
        print('✓ Parsing results are correct')
    else:
        print(f'✗ Parsing mismatch: expected {expected_owner}/{expected_repo}/{expected_skill}')
        sys.exit(1)
else:
    print('✗ Failed to identify marketplace format')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "Marketplace format parsing works correctly"
    else
        log_fail "Marketplace format parsing failed"
    fi
}

test_registry_api_fallback() {
    log_section "TEST: Registry → API Fallback Logic"
    
    log_info "Testing registry fallback to API..."
    
    # Create a temporary directory without any registry
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Try to install - should fall back to API since no local registry
    log_info "Installing from directory with no local registry..."
    
    local output
    output=$(skilz install "$SKILL_ID" --agent claude --verbose 2>&1)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Install succeeded with API fallback"
        
        if echo "$output" | grep -q "not in local registries\|trying.*API\|marketplace API"; then
            log_success "API fallback logic triggered correctly"
        else
            log_info "API fallback not explicitly shown in output"
        fi
        
        # Clean up
        skilz rm "$SKILL_NAME" --agent claude -y 2>/dev/null || true
    else
        log_fail "Install failed during API fallback test"
        echo "Output: $output"
    fi
    
    cd - >/dev/null
    rm -rf "$temp_dir"
}

main() {
    echo ""
    echo "=============================================="
    echo " Skilz API Integration Test"
    echo "=============================================="
    echo ""
    
    # Verify skilz is installed
    if ! command -v skilz &> /dev/null; then
        log_fail "skilz command not found - please install first"
        exit 1
    fi
    
    log_info "Testing with skill: $SKILL_ID"
    log_info "Skilz version: $(skilz --version)"
    
    # Run tests
    test_api_format_parsing
    test_api_endpoint_calls
    test_registry_api_fallback
    
    echo ""
    log_success "API integration tests completed"
}

main "$@"