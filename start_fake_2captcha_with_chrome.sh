#!/bin/bash
# Start Fake 2captcha Service with Chrome Debug Support

# Set up signal handling to clean up Chrome on script exit
cleanup() {
    echo ""
    echo "🛑 Shutting down gracefully..."
    echo "📝 Note: Chrome will continue running in headless mode for other processes"
    echo "🔧 To stop Chrome manually: pkill -f 'chrome.*9222'"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "=== Fake 2captcha Service Startup ==="
echo "This script will start Chrome with debugging and then start the fake 2captcha service"
echo "Chrome will continue running even if this script is terminated"
echo ""

# Function to check if Chrome is running on port 9222
check_chrome_debug() {
    if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start Chrome with debugging
start_chrome_debug() {
    echo "Starting Chrome with remote debugging in headless mode..."
    
    # Kill any existing Chrome processes on port 9222
    lsof -ti:9222 | xargs kill -9 2>/dev/null || true
    
    # Clean up any existing profile directories
    rm -rf /tmp/chrome-debug-profile
    rm -rf /tmp/chrome-headless-*
    
    # Wait for processes to terminate
    sleep 2
    
    # Create unique profile directory
    PROFILE_DIR="/tmp/chrome-headless-$(date +%s)"
    
    # Start Chrome with debugging in headless mode - detach it completely
    nohup "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --remote-debugging-port=9222 \
        --headless=new \
        --no-first-run \
        --no-default-browser-check \
        --disable-default-apps \
        --disable-popup-blocking \
        --disable-web-security \
        --disable-features=VizDisplayCompositor \
        --disable-dev-shm-usage \
        --disable-gpu \
        --no-sandbox \
        --disable-setuid-sandbox \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding \
        --disable-features=TranslateUI \
        --disable-ipc-flooding-protection \
        --disable-logging \
        --log-level=3 \
        --silent-launch \
        --user-data-dir="$PROFILE_DIR" > /dev/null 2>&1 &
    
    CHROME_PID=$!
    echo "Chrome started with PID: $CHROME_PID in headless mode (detached)"
    
    # Wait for Chrome to be ready
    echo "Waiting for Chrome to be ready..."
    for i in {1..30}; do
        if check_chrome_debug; then
            echo "✅ Chrome is ready on port 9222 in headless mode"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 1
    done
    
    if ! check_chrome_debug; then
        echo "❌ ERROR: Chrome failed to start properly"
        kill $CHROME_PID 2>/dev/null || true
        exit 1
    fi
}

# Check if Chrome is already running
if check_chrome_debug; then
    echo "✅ Chrome is already running with debugging on port 9222"
else
    echo "🌐 Chrome is not running with debugging. Starting Chrome in headless mode..."
    start_chrome_debug
fi

# Clean up any existing processes on port 5001
echo "Cleaning up existing processes on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the fake 2captcha service
echo "Starting fake 2captcha service..."
echo "Service will be available at: http://localhost:5001"
echo "Health check: http://localhost:5001/health"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

python fake_2captcha_app.py 