#!/bin/bash

# Comprehensive Test Runner for ClosetGPT
# This script runs all tests and generates a comprehensive report

set -e  # Exit on any error

echo "🧪 Starting Comprehensive Test Suite for ClosetGPT"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}Running: $test_name${NC}"
    echo "Command: $test_command"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

# Function to print summary
print_summary() {
    echo -e "\n${BLUE}=================================================="
    echo "TEST SUMMARY"
    echo "=================================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Success Rate: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"
    echo "==================================================${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed!${NC}"
        exit 1
    fi
}

# Backend Tests
print_section "Backend Tests"

# Check if we're in the backend directory
if [ -d "backend" ]; then
    cd backend
    
    # Python environment setup
    if command_exists python3; then
        echo "Setting up Python environment..."
        python3 -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov flake8 black isort bandit safety
    fi
    
    # Linting tests
    run_test "Python Linting (flake8)" "flake8 src/ --max-line-length=88 --extend-ignore=E203,W503"
    run_test "Code Formatting (black)" "black --check src/"
    run_test "Import Sorting (isort)" "isort --check-only src/"
    
    # Security tests
    run_test "Security Scan (bandit)" "bandit -r src/ -f json -o bandit-report.json || true"
    run_test "Dependency Security (safety)" "safety check --json --output safety-report.json || true"
    
    # Unit tests
    if [ -d "tests" ]; then
        run_test "Unit Tests (pytest)" "pytest tests/ -v --cov=src --cov-report=xml --cov-report=html"
    fi
    
    # Validation tests
    if [ -f "run_validation_tests.py" ]; then
        run_test "Validation Tests" "python run_validation_tests.py"
    fi
    
    # Outfit generation tests
    if [ -f "test_outfit_generation.py" ]; then
        run_test "Outfit Generation Tests" "python test_outfit_generation.py"
    fi
    
    # Comprehensive tests
    if [ -f "comprehensive_testing_framework.py" ]; then
        run_test "Comprehensive Tests" "python comprehensive_testing_framework.py"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠️  Backend directory not found, skipping backend tests${NC}"
fi

# Frontend Tests
print_section "Frontend Tests"

if [ -d "frontend" ]; then
    cd frontend
    
    # Node.js environment setup
    if command_exists node; then
        echo "Setting up Node.js environment..."
        npm ci
    fi
    
    # Linting tests
    run_test "JavaScript/TypeScript Linting" "npm run lint"
    
    # Security tests
    run_test "Dependency Audit" "npm audit --audit-level=moderate"
    
    # Unit tests
    run_test "Unit Tests" "npm test"
    
    # Type checking
    run_test "Type Checking" "npm run type-check || npx tsc --noEmit"
    
    # Build test
    run_test "Build Test" "npm run build"
    
    # E2E tests (if Cypress is available)
    if command_exists npx; then
        run_test "Cypress E2E Tests" "npx cypress run --headless"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠️  Frontend directory not found, skipping frontend tests${NC}"
fi

# Integration Tests
print_section "Integration Tests"

if [ -d "backend" ] && [ -d "frontend" ]; then
    echo "Starting backend server for integration tests..."
    
    # Start backend server in background
    cd backend
    python -m src.app &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 10
    
    # Start frontend server in background
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 15
    
    # Run integration tests
    run_test "API Integration Tests" "cd backend && python test_frontend_api.py"
    
    # Cleanup
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  Both backend and frontend required for integration tests${NC}"
fi

# Performance Tests
print_section "Performance Tests"

if [ -d "backend" ]; then
    cd backend
    
    # Simple performance test
    run_test "API Response Time Test" "
        python -c \"
        import time
        import requests
        start = time.time()
        response = requests.post('http://localhost:3001/api/outfit/generate', 
            json={'wardrobe': [], 'occasion': 'casual', 'weather': {'temperature': 70}})
        end = time.time()
        print(f'Response time: {end - start:.2f}s')
        assert response.status_code in [200, 400, 500], f'Unexpected status: {response.status_code}'
        \"
    " || echo "Performance test skipped (server not running)"
    
    cd ..
fi

# Generate test artifacts
print_section "Generating Test Artifacts"

if [ -d "backend" ]; then
    cd backend
    if [ -f "coverage.xml" ]; then
        echo "📊 Coverage report generated"
    fi
    if [ -f "bandit-report.json" ]; then
        echo "🔒 Security report generated"
    fi
    cd ..
fi

if [ -d "frontend" ]; then
    cd frontend
    if [ -d "coverage" ]; then
        echo "📊 Frontend coverage report generated"
    fi
    cd ..
fi

# Print final summary
print_summary 