#!/bin/bash
# Development helper script for ChipClaw

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_help() {
    echo "ChipClaw Development Script"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test              Run all tests"
    echo "  test-unit         Run unit tests only"
    echo "  lint              Check Python syntax"
    echo "  install-deps      Install Python dependencies for development"
    echo "  upload            Upload files to ESP32 (requires MPREMOTE_DEVICE)"
    echo "  upload-tests      Upload tests to ESP32"
    echo "  clean             Clean temporary files and cache"
    echo "  help              Show this help message"
    echo ""
}

run_tests() {
    echo -e "${YELLOW}Running all tests...${NC}"
    python tests/test_runner.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
    else
        echo -e "${RED}✗ Tests failed!${NC}"
        exit 1
    fi
}

run_unit_tests() {
    echo -e "${YELLOW}Running unit tests...${NC}"
    for test_file in tests/unit/test_*.py; do
        echo "Running $(basename $test_file)..."
        python "$test_file"
    done
    echo -e "${GREEN}✓ Unit tests completed!${NC}"
}

run_lint() {
    echo -e "${YELLOW}Checking Python syntax...${NC}"
    python -m py_compile main.py boot.py
    find chipclaw -name "*.py" -exec python -m py_compile {} \;
    find tests -name "*.py" -exec python -m py_compile {} \;
    echo -e "${GREEN}✓ Syntax check passed!${NC}"
}

install_deps() {
    echo -e "${YELLOW}Installing development dependencies...${NC}"
    python -m pip install --upgrade pip
    pip install aiohttp
    echo -e "${GREEN}✓ Dependencies installed!${NC}"
}

upload_to_esp32() {
    if [ -z "$MPREMOTE_DEVICE" ]; then
        echo -e "${RED}Error: MPREMOTE_DEVICE environment variable not set${NC}"
        echo "Set it with: export MPREMOTE_DEVICE=/dev/ttyUSB0"
        exit 1
    fi
    
    echo -e "${YELLOW}Uploading files to ESP32 ($MPREMOTE_DEVICE)...${NC}"
    mpremote fs cp boot.py :boot.py
    mpremote fs cp main.py :main.py
    mpremote fs cp config.json :config.json
    mpremote fs cp -r chipclaw :chipclaw
    mpremote fs cp -r workspace :workspace
    mpremote fs cp -r data :data
    echo -e "${GREEN}✓ Files uploaded!${NC}"
}

upload_tests_to_esp32() {
    if [ -z "$MPREMOTE_DEVICE" ]; then
        echo -e "${RED}Error: MPREMOTE_DEVICE environment variable not set${NC}"
        echo "Set it with: export MPREMOTE_DEVICE=/dev/ttyUSB0"
        exit 1
    fi
    
    echo -e "${YELLOW}Uploading tests to ESP32 ($MPREMOTE_DEVICE)...${NC}"
    mpremote fs cp -r tests :tests
    echo -e "${GREEN}✓ Tests uploaded!${NC}"
    echo "To run tests on ESP32: mpremote exec 'import tests.test_runner'"
}

clean() {
    echo -e "${YELLOW}Cleaning temporary files...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
    rm -rf /tmp/test_workspace /tmp/test_data 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup complete!${NC}"
}

# Main script logic
case "$1" in
    test)
        run_tests
        ;;
    test-unit)
        run_unit_tests
        ;;
    lint)
        run_lint
        ;;
    install-deps)
        install_deps
        ;;
    upload)
        upload_to_esp32
        ;;
    upload-tests)
        upload_tests_to_esp32
        ;;
    clean)
        clean
        ;;
    help|--help|-h|"")
        print_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_help
        exit 1
        ;;
esac
