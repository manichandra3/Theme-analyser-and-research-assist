#!/bin/bash
# Endpoint Test Script for Theme Analyser
# Tests all endpoints across FastAPI (8000), Spring Boot (8080), and React (3000)

set -e

# Configuration
FASTAPI_URL=${FASTAPI_URL:-"http://localhost:8000"}
SPRINGBOOT_URL=${SPRINGBOOT_URL:-"http://localhost:8080"}
REACT_URL=${REACT_URL:-"http://localhost:3000"}

echo "=== Testing All Endpoints ==="
echo "FastAPI: $FASTAPI_URL"
echo "Spring Boot: $SPRINGBOOT_URL"
echo "React: $REACT_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=$4
    local expected_status=${5:-200}
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url" 2>/dev/null || echo -e "\n000")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "Response: $body"
        return 1
    fi
}

test_multipart() {
    local name=$1
    local url=$2
    local file_path=$3
    local expected_status=${4:-200}
    
    echo -n "Testing $name... "
    
    # Create a test file if it doesn't exist
    if [ ! -f "$file_path" ]; then
        echo "Test content for upload" > "$file_path"
    fi
    
    response=$(curl -s -w "\n%{http_code}" -X POST -F "file=@$file_path" "$url" 2>/dev/null || echo -e "\n000")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "Response: $body"
        return 1
    fi
}

# Track results
PASSED=0
FAILED=0

run_test() {
    if $1; then
        ((PASSED++))
    else
        ((FAILED++))
    fi
}

echo "=== FASTAPI ENDPOINTS (port 8000) ==="

# Health check
run_test "test_endpoint 'FastAPI Root' '$FASTAPI_URL/'"

# Documents
run_test "test_endpoint 'List Documents' '$FASTAPI_URL/api/v1/documents'"
run_test "test_endpoint 'Get Document (will 404)' '$FASTAPI_URL/api/v1/documents/1'"

# Search
run_test "test_endpoint 'Semantic Search' '$FASTAPI_URL/api/v1/search?query=test&k=5&mode=hybrid'"
run_test "test_endpoint 'Dense Search' '$FASTAPI_URL/api/v1/search?query=test&k=5&mode=dense'"

# Q&A
run_test "test_endpoint 'Ask Question' '$FASTAPI_URL/api/v1/ask?question=What is AI?&k=5'"

# Evaluation
run_test "test_endpoint 'Setup Test Data' '$FASTAPI_URL/api/v1/test/setup' 'POST'"

# Retrieval Evaluation
RETRIEVAL_DATA='{"test_cases": [{"question": "What is AI?", "relevant_chunk_ids": ["test1"]}], "eval_k": 5}'
run_test "test_endpoint 'Retrieval Evaluation' '$FASTAPI_URL/api/v1/evaluate/retrieval' 'POST' '$RETRIEVAL_DATA'"

# Generation Evaluation
GENERATION_DATA='{"test_cases": [{"question": "What is AI?", "reference_answer": "AI is artificial intelligence"}], "final_k": 5}'
run_test "test_endpoint 'Generation Evaluation' '$FASTAPI_URL/api/v1/evaluate/generation' 'POST' '$GENERATION_DATA'"

echo ""
echo "=== SPRING BOOT ENDPOINTS (port 8080) ==="

# Health check
run_test "test_endpoint 'Spring Boot Root' '$SPRINGBOOT_URL/'"
run_test "test_endpoint 'Actuator Health' '$SPRINGBOOT_URL/actuator/health'"

# Document API (via Spring Boot)
run_test "test_endpoint 'List Documents (Spring)' '$SPRINGBOOT_URL/api/documents'"
run_test "test_endpoint 'Search Documents (Spring)' '$SPRINGBOOT_URL/api/search?query=test&k=5&mode=hybrid'"
run_test "test_endpoint 'Ask Question (Spring)' '$SPRINGBOOT_URL/api/ask?question=What is AI?&k=5'"

# RAG Pipeline endpoints
run_test "test_endpoint 'RAG Ask' '$SPRINGBOOT_URL/api/rag/ask?question=What is AI?&k=5'"
run_test "test_endpoint 'RAG Search' '$SPRINGBOOT_URL/api/rag/search?query=test&k=5&mode=hybrid'"

# Verification
VERIFY_DATA='{"answer": "AI is artificial intelligence", "chunks": [{"doc_id": "test1", "content": "AI is transforming the way we live", "page": 1, "paragraph": 1}]}'
run_test "test_endpoint 'Verify' '$SPRINGBOOT_URL/api/verify' 'POST' '$VERIFY_DATA'"

# Evaluation via Spring Boot
run_test "test_endpoint 'Retrieval Eval (Spring)' '$SPRINGBOOT_URL/api/evaluate/retrieval' 'POST' '$RETRIEVAL_DATA'"
run_test "test_endpoint 'Generation Eval (Spring)' '$SPRINGBOOT_URL/api/evaluate/generation' 'POST' '$GENERATION_DATA'"

echo ""
echo "=== REACT ENDPOINTS (port 3000) ==="

run_test "test_endpoint 'React App' '$REACT_URL/'"

echo ""
echo "=== FILE UPLOAD TESTS ==="

# Test file upload to FastAPI
TEST_FILE="/tmp/test_upload.txt"
echo "This is a test document for upload testing." > "$TEST_FILE"
run_test "test_multipart 'Upload Document (FastAPI)' '$FASTAPI_URL/api/v1/upload' '$TEST_FILE'"

# Test file upload to Spring Boot
run_test "test_multipart 'Upload Document (Spring)' '$SPRINGBOOT_URL/api/upload' '$TEST_FILE'"

# Cleanup
rm -f "$TEST_FILE"

echo ""
echo "=== SUMMARY ==="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi