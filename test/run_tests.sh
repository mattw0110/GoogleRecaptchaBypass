#!/bin/bash
# Comprehensive Test Runner for Google reCAPTCHA Bypass Service

echo "🧪 Comprehensive Test Suite for Google reCAPTCHA Bypass"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "../fake_2captcha_app.py" ]; then
    echo "❌ Error: Please run this script from the test directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: ProjectRoot/test/"
    exit 1
fi

# Check if virtual environment exists
if [ -d "../venv" ]; then
    echo "Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Checking for Python dependencies..."
fi

# Check if Python requirements are met
python -c "import requests, concurrent.futures" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing Python dependencies. Please install:"
    echo "   pip install requests"
    exit 1
fi

# Function to show usage
show_usage() {
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --health            Run only health tests"
    echo "  --recaptcha-v2      Run only reCAPTCHA v2 tests"
    echo "  --recaptcha-v3      Run only reCAPTCHA v3 tests"
    echo "  --api-formats       Run only API format tests"
    echo "  --quick             Run quick test suite (submissions only)"
    echo "  --full              Run full comprehensive test suite (default)"
    echo "  --start-service     Start the service if not running"
    echo
    echo "Examples:"
    echo "  $0                  # Run full comprehensive tests"
    echo "  $0 --health         # Run only health checks"
    echo "  $0 --quick          # Run quick tests"
    echo "  $0 --start-service  # Start service and run tests"
    echo
}

# Parse command line arguments
RUN_ALL=true
RUN_HEALTH=false
RUN_V2=false
RUN_V3=false
RUN_API=false
START_SERVICE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --health)
            RUN_ALL=false
            RUN_HEALTH=true
            shift
            ;;
        --recaptcha-v2)
            RUN_ALL=false
            RUN_V2=true
            shift
            ;;
        --recaptcha-v3)
            RUN_ALL=false
            RUN_V3=true
            shift
            ;;
        --api-formats)
            RUN_ALL=false
            RUN_API=true
            shift
            ;;
        --quick)
            RUN_ALL=false
            RUN_HEALTH=true
            RUN_API=true
            shift
            ;;
        --full)
            RUN_ALL=true
            shift
            ;;
        --start-service)
            START_SERVICE=true
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to check if service is running
check_service() {
    curl -s http://localhost:5001/health >/dev/null 2>&1
    return $?
}

# Start service if requested
if [ "$START_SERVICE" = true ]; then
    echo "🚀 Starting service..."
    cd ..
    ./start_fake_2captcha_with_chrome.sh &
    SERVICE_PID=$!
    cd test
    
    echo "⏳ Waiting for service to start..."
    for i in {1..30}; do
        if check_service; then
            echo "✅ Service started successfully!"
            break
        fi
        echo "   Attempt $i/30..."
        sleep 2
    done
    
    if ! check_service; then
        echo "❌ Service failed to start"
        exit 1
    fi
fi

# Check if service is running
if ! check_service; then
    echo "❌ Service is not running!"
    echo "Please start the service first:"
    echo "   cd .. && ./start_fake_2captcha_with_chrome.sh"
    echo ""
    echo "Or use --start-service to start it automatically"
    exit 1
fi

echo "✅ Service is running, starting tests..."
echo

# Run tests based on options
if [ "$RUN_ALL" = true ]; then
    echo "Running comprehensive test suite..."
    python run_comprehensive_tests.py
    TEST_EXIT_CODE=$?
elif [ "$RUN_HEALTH" = true ] && [ "$RUN_V2" = false ] && [ "$RUN_V3" = false ] && [ "$RUN_API" = false ]; then
    echo "Running health tests only..."
    python test_service_health.py
    TEST_EXIT_CODE=$?
elif [ "$RUN_V2" = true ] && [ "$RUN_HEALTH" = false ] && [ "$RUN_V3" = false ] && [ "$RUN_API" = false ]; then
    echo "Running reCAPTCHA v2 tests only..."
    python test_recaptcha_v2.py
    TEST_EXIT_CODE=$?
elif [ "$RUN_V3" = true ] && [ "$RUN_HEALTH" = false ] && [ "$RUN_V2" = false ] && [ "$RUN_API" = false ]; then
    echo "Running reCAPTCHA v3 tests only..."
    python test_recaptcha_v3.py
    TEST_EXIT_CODE=$?
elif [ "$RUN_API" = true ] && [ "$RUN_HEALTH" = false ] && [ "$RUN_V2" = false ] && [ "$RUN_V3" = false ]; then
    echo "Running API format tests only..."
    python test_api_formats.py
    TEST_EXIT_CODE=$?
else
    echo "Running selected test modules..."
    TEST_EXIT_CODE=0
    
    if [ "$RUN_HEALTH" = true ]; then
        echo "🏥 Running health tests..."
        python test_service_health.py
        if [ $? -ne 0 ]; then TEST_EXIT_CODE=1; fi
        echo
    fi
    
    if [ "$RUN_V2" = true ]; then
        echo "🤖 Running reCAPTCHA v2 tests..."
        python test_recaptcha_v2.py
        if [ $? -ne 0 ]; then TEST_EXIT_CODE=1; fi
        echo
    fi
    
    if [ "$RUN_V3" = true ]; then
        echo "🎯 Running reCAPTCHA v3 tests..."
        python test_recaptcha_v3.py
        if [ $? -ne 0 ]; then TEST_EXIT_CODE=1; fi
        echo
    fi
    
    if [ "$RUN_API" = true ]; then
        echo "🔄 Running API format tests..."
        python test_api_formats.py
        if [ $? -ne 0 ]; then TEST_EXIT_CODE=1; fi
        echo
    fi
fi

# Clean up if we started the service
if [ "$START_SERVICE" = true ] && [ -n "$SERVICE_PID" ]; then
    echo "🛑 Stopping service..."
    kill $SERVICE_PID 2>/dev/null
fi

# Report results
echo
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests completed successfully!"
else
    echo "❌ Some tests failed. Check the output above for details."
fi

exit $TEST_EXIT_CODE 