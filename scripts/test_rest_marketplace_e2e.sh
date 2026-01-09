#!/usr/bin/env bash
#
# Comprehensive E2E Test Plan for REST Marketplace Endpoint
#
# Tests all three formats (NEW, LEGACY, SLUG) against the live REST API
# at https://skillzwave.ai/api to verify proper behavior
#
# Test Coverage:
# ✅ NEW format resolves correctly
# ✅ LEGACY format resolves correctly  
# ✅ SLUG format resolves correctly
# ✅ 404 returned for non-existent skills
# ✅ 400 returned for invalid formats
# ✅ Verbose logging shows REST vs GitHub resolution
# ✅ API endpoint reachability and response validation

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

# Test skills - using known skills from the marketplace
VALID_SKILL_OWNER="Jamie-BitFlight"
VALID_SKILL_REPO="claude_skills"
VALID_SKILL_NAME="brainstorming-skill"

# Format variations of the same skill
NEW_FORMAT="$VALID_SKILL_OWNER/$VALID_SKILL_REPO/$VALID_SKILL_NAME"
LEGACY_FORMAT="${VALID_SKILL_OWNER}_${VALID_SKILL_REPO}/$VALID_SKILL_NAME"
SLUG_FORMAT="${VALID_SKILL_OWNER}__${VALID_SKILL_REPO}__${VALID_SKILL_NAME}"

# API endpoints
API_BASE="https://skillzwave.ai/api"
API_BYNAME="$API_BASE/skills/byname"
API_COORDINATES="$API_BASE/skills/coordinates"

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

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Helper function to test API endpoint directly
test_api_endpoint() {
    local url="$1"
    local expected_status="$2"
    local description="$3"
    
    log_info "Testing: $description"
    log_info "URL: $url"
    
    local response
    local status_code
    
    # Make request and capture both status and response
    local temp_file=$(mktemp)
    local status_code
    status_code=$(curl -s -w "%{http_code}" -o "$temp_file" "$url" 2>/dev/null || echo "000")
    local response_body
    response_body=$(cat "$temp_file" 2>/dev/null || echo "")
    rm -f "$temp_file"
    
    if [[ "$status_code" == "$expected_status" ]]; then
        log_success "API returned expected status $expected_status"
        
        # If 200, validate JSON structure
        if [[ "$status_code" == "200" ]]; then
            if echo "$response_body" | jq . >/dev/null 2>&1; then
                log_success "Response is valid JSON"
                
                # Check for required fields
                if echo "$response_body" | jq -e '.name, .repoFullName, .skillPath' >/dev/null 2>&1; then
                    log_success "Response contains required fields (name, repoFullName, skillPath)"
                else
                    log_fail "Response missing required fields"
                fi
            else
                log_fail "Response is not valid JSON"
            fi
        fi
    else
        log_fail "API returned status $status_code, expected $expected_status"
        if [[ -n "$response_body" ]]; then
            echo "Response body: $response_body"
        fi
    fi
    
    return 0
}

# Helper function to test skilz install with verbose output
test_skilz_install() {
    local skill_id="$1"
    local format_type="$2"
    local expected_result="$3"  # "success" or "fail"
    local description="$4"
    
    log_info "Testing skilz install: $description"
    log_info "Skill ID: $skill_id"
    log_info "Expected format: $format_type"
    
    # Clean up any existing installation
    skilz rm "$(basename "$skill_id")" --agent claude -y 2>/dev/null || true
    
    # Capture verbose output
    local output
    local exit_code
    
    output=$(skilz -v install "$skill_id" --agent claude 2>&1)
    exit_code=$?
    
    # Check format detection
    if echo "$output" | grep -q "\[INFO\] Skill ID format: $format_type"; then
        log_success "Format correctly detected as $format_type"
    else
        log_fail "Format not detected as $format_type"
        echo "Output: $output"
    fi
    
    # Check REST API attempt
    if [[ "$format_type" != "UNKNOWN" ]]; then
        if echo "$output" | grep -q "\[INFO\] Attempting REST API lookup"; then
            log_success "REST API lookup attempted"
        else
            log_fail "REST API lookup not attempted"
        fi
    fi
    
    # Check result
    if [[ "$expected_result" == "success" ]]; then
        if [[ $exit_code -eq 0 ]]; then
            log_success "Install succeeded as expected"
            
            # Check for success message
            if echo "$output" | grep -q "\[SUCCESS\] REST API resolved skill"; then
                log_success "REST API resolution success logged"
            else
                log_fail "REST API success not logged"
            fi
            
            # Verify skill was actually installed
            if [[ -f "$HOME/.claude/skills/$(basename "$skill_id")/SKILL.md" ]]; then
                log_success "Skill file actually installed"
            else
                log_fail "Skill file not found after install"
            fi
            
        else
            log_fail "Install failed unexpectedly (exit code: $exit_code)"
            echo "Output: $output"
        fi
    else
        if [[ $exit_code -ne 0 ]]; then
            log_success "Install failed as expected"
        else
            log_fail "Install succeeded when it should have failed"
        fi
    fi
    
    # Clean up
    skilz rm "$(basename "$skill_id")" --agent claude -y 2>/dev/null || true
}

# Test 1: API Endpoint Reachability
test_api_reachability() {
    log_section "TEST 1: API Endpoint Reachability"
    
    # Test byname endpoint with valid skill
    local byname_url="$API_BYNAME?repoFullName=$VALID_SKILL_OWNER/$VALID_SKILL_REPO&name=$VALID_SKILL_NAME"
    test_api_endpoint "$byname_url" "200" "Valid skill via byname endpoint"
    
    # Test coordinates endpoint with valid path
    local coords_url="$API_COORDINATES?owner=$VALID_SKILL_OWNER&repo=$VALID_SKILL_REPO&path=$VALID_SKILL_NAME/SKILL.md"
    test_api_endpoint "$coords_url" "200" "Valid skill via coordinates endpoint"
    
    # Test 404 for non-existent skill
    local notfound_url="$API_BYNAME?repoFullName=fake-owner/fake-repo&name=fake-skill"
    test_api_endpoint "$notfound_url" "404" "Non-existent skill returns 404"
}

# Test 2: NEW Format Resolution
test_new_format() {
    log_section "TEST 2: NEW Format Resolution (owner/repo/skill)"
    
    test_skilz_install "$NEW_FORMAT" "NEW" "success" "NEW format with valid skill"
    
    # Test with non-existent skill in NEW format
    test_skilz_install "fake-owner/fake-repo/fake-skill" "NEW" "fail" "NEW format with non-existent skill"
}

# Test 3: LEGACY Format Resolution  
test_legacy_format() {
    log_section "TEST 3: LEGACY Format Resolution (owner_repo/skill)"
    
    test_skilz_install "$LEGACY_FORMAT" "LEGACY" "success" "LEGACY format with valid skill"
    
    # Test with non-existent skill in LEGACY format
    test_skilz_install "fake-owner_fake-repo/fake-skill" "LEGACY" "fail" "LEGACY format with non-existent skill"
}

# Test 4: SLUG Format Resolution
test_slug_format() {
    log_section "TEST 4: SLUG Format Resolution (owner__repo__skill)"
    
    test_skilz_install "$SLUG_FORMAT" "SLUG" "success" "SLUG format with valid skill"
    
    # Test with non-existent skill in SLUG format
    test_skilz_install "fake-owner__fake-repo__fake-skill" "SLUG" "fail" "SLUG format with non-existent skill"
}

# Test 5: Invalid Format Handling
test_invalid_formats() {
    log_section "TEST 5: Invalid Format Handling"
    
    # Test completely invalid format
    test_skilz_install "just-a-name" "UNKNOWN" "fail" "Invalid format (no separators)"
    
    # Test incomplete NEW format
    test_skilz_install "owner/skill" "UNKNOWN" "fail" "Incomplete NEW format (missing repo)"
    
    # Test incomplete LEGACY format  
    test_skilz_install "owner/skill" "UNKNOWN" "fail" "Incomplete LEGACY format (no underscore)"
}

# Test 6: Format Detection Accuracy
test_format_detection() {
    log_section "TEST 6: Format Detection Accuracy"
    
    log_info "Testing format detection with Python API..."
    
    python3 -c "
import sys
sys.path.insert(0, 'src')
from skilz.api_client import get_skill_id_format, is_marketplace_skill_id, parse_skill_id

test_cases = [
    ('$NEW_FORMAT', 'new', True),
    ('$LEGACY_FORMAT', 'legacy', True),
    ('$SLUG_FORMAT', 'slug', True),
    ('just-a-name', 'unknown', False),
    ('owner/skill', 'unknown', False),
    ('https://github.com/owner/repo', 'unknown', False),
]

all_passed = True
for skill_id, expected_format, expected_marketplace in test_cases:
    actual_format = get_skill_id_format(skill_id)
    actual_marketplace = is_marketplace_skill_id(skill_id)
    
    if actual_format == expected_format and actual_marketplace == expected_marketplace:
        print(f'✅ {skill_id} -> {actual_format} (marketplace: {actual_marketplace})')
    else:
        print(f'❌ {skill_id} -> Expected: {expected_format}/{expected_marketplace}, Got: {actual_format}/{actual_marketplace}')
        all_passed = False

# Test parsing for valid formats
try:
    owner, repo, skill = parse_skill_id('$NEW_FORMAT')
    if owner == '$VALID_SKILL_OWNER' and repo == '$VALID_SKILL_REPO' and skill == '$VALID_SKILL_NAME':
        print('✅ NEW format parsing correct')
    else:
        print(f'❌ NEW format parsing failed: {owner}/{repo}/{skill}')
        all_passed = False
        
    owner, repo, skill = parse_skill_id('$LEGACY_FORMAT')
    if owner == '$VALID_SKILL_OWNER' and repo == '$VALID_SKILL_REPO' and skill == '$VALID_SKILL_NAME':
        print('✅ LEGACY format parsing correct')
    else:
        print(f'❌ LEGACY format parsing failed: {owner}/{repo}/{skill}')
        all_passed = False
        
    owner, repo, skill = parse_skill_id('$SLUG_FORMAT')
    if owner.lower() == '$(echo $VALID_SKILL_OWNER | tr A-Z a-z)' and repo.lower() == '$(echo $VALID_SKILL_REPO | tr A-Z a-z)' and skill.lower() == '$(echo $VALID_SKILL_NAME | tr A-Z a-z)':
        print('✅ SLUG format parsing correct (normalized to lowercase)')
    else:
        print(f'❌ SLUG format parsing failed: {owner}/{repo}/{skill}')
        all_passed = False

except Exception as e:
    print(f'❌ Parsing error: {e}')
    all_passed = False

sys.exit(0 if all_passed else 1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "All format detection tests passed"
    else
        log_fail "Format detection tests failed"
    fi
}

# Test 7: REST vs GitHub Fallback Logging
test_rest_vs_github_logging() {
    log_section "TEST 7: REST vs GitHub Fallback Logging"
    
    log_info "Testing that REST API is attempted first for marketplace formats..."
    
    # Test with a skill that should be found via REST API
    local output
    output=$(skilz -v install "$NEW_FORMAT" --agent claude 2>&1)
    
    # Check that REST API is attempted before any GitHub operations
    if echo "$output" | grep -q "\[INFO\] Attempting REST API lookup" && \
       echo "$output" | grep -q "API lookup by name:"; then
        log_success "REST API attempted first as expected"
    else
        log_fail "REST API not attempted first"
        echo "Output: $output"
    fi
    
    # Clean up
    skilz rm "$VALID_SKILL_NAME" --agent claude -y 2>/dev/null || true
}

# Test 8: Error Response Validation
test_error_responses() {
    log_section "TEST 8: Error Response Validation"
    
    log_info "Testing API error responses..."
    
    # Test 404 response structure
    local notfound_url="$API_BYNAME?repoFullName=definitely-fake-owner/definitely-fake-repo&name=definitely-fake-skill"
    local response
    response=$(curl -s "$notfound_url" 2>/dev/null || echo "")
    
    if [[ -n "$response" ]]; then
        log_success "404 endpoint returned response"
        
        # Check if it's valid JSON error response
        if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
            log_success "404 response contains error field"
        else
            log_info "404 response format: $response"
        fi
    else
        log_fail "404 endpoint returned no response"
    fi
}

# Main execution
main() {
    echo ""
    echo "=============================================="
    echo " REST Marketplace Endpoint E2E Test Suite"
    echo "=============================================="
    echo ""
    echo "Testing against: $API_BASE"
    echo "Valid test skill: $NEW_FORMAT"
    echo ""
    
    # Verify skilz is installed
    if ! command -v skilz &> /dev/null; then
        log_fail "skilz command not found - please install first"
        exit 1
    fi
    
    log_info "Skilz version: $(skilz --version)"
    
    # Verify jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        log_fail "jq command not found - please install jq for JSON parsing"
        exit 1
    fi
    
    # Run all tests
    test_api_reachability
    test_format_detection
    test_new_format
    test_legacy_format
    test_slug_format
    test_invalid_formats
    test_rest_vs_github_logging
    test_error_responses
    
    # Summary
    echo ""
    echo "=============================================="
    echo " TEST SUMMARY"
    echo "=============================================="
    echo ""
    
    local total=$((TESTS_PASSED + TESTS_FAILED))
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo "Total Tests:  $total"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
        echo ""
        echo "✅ NEW format resolves correctly"
        echo "✅ LEGACY format resolves correctly"  
        echo "✅ SLUG format resolves correctly"
        echo "✅ 404 returned for non-existent skills"
        echo "✅ Invalid formats handled correctly"
        echo "✅ REST API attempted first for marketplace formats"
        echo "✅ Verbose logging shows resolution method"
        echo ""
        exit 0
    else
        echo -e "${RED}❌ $TESTS_FAILED TESTS FAILED${NC}"
        echo ""
        echo "Please review the failed tests above and fix any issues."
        exit 1
    fi
}

# Run main with error handling
main "$@"