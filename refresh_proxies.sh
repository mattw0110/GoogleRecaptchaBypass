#!/bin/bash
# Proxy Refresh Tool - Linux/macOS Wrapper Script

echo "🔄 Proxy Refresh Tool for Google reCAPTCHA Bypass"
echo "=================================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if Python requirements are met
python -c "import requests, concurrent.futures" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing Python dependencies. Please run:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Function to show usage
show_usage() {
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --stats             Show current proxy statistics only"
    echo "  --force             Force refresh even if we have enough proxies"
    echo "  --clean             Clean failed proxies before fetching new ones"
    echo "  --test-existing     Test existing proxies health"
    echo "  --quick             Quick refresh (test 25 proxies)"
    echo "  --full              Full refresh (test 100 proxies)"
    echo
    echo "Examples:"
    echo "  $0                  # Standard refresh (50 proxies)"
    echo "  $0 --stats          # Show current proxy stats"
    echo "  $0 --force --clean  # Force refresh and clean old proxies"
    echo "  $0 --quick          # Quick refresh for testing"
    echo "  $0 --full           # Full refresh for maximum proxies"
    echo
}

# Parse command line arguments
FORCE=""
CLEAN=""
TEST_EXISTING=""
TEST_COUNT="50"
STATS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --stats|-s)
            STATS="--stats"
            shift
            ;;
        --force|-f)
            FORCE="--force"
            shift
            ;;
        --clean|-c)
            CLEAN="--clean"
            shift
            ;;
        --test-existing|-e)
            TEST_EXISTING="--test-existing"
            shift
            ;;
        --quick)
            TEST_COUNT="25"
            shift
            ;;
        --full)
            TEST_COUNT="100"
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run the proxy refresh script
echo "Running proxy refresh with options..."
echo

python refresh_proxies.py $STATS $FORCE $CLEAN $TEST_EXISTING --test-count $TEST_COUNT

# Check exit status
if [ $? -eq 0 ]; then
    echo
    echo "✅ Proxy refresh completed!"
else
    echo
    echo "❌ Proxy refresh failed. Check the output above for details."
    exit 1
fi 