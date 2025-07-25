#!/bin/bash

echo "========================================"
echo "Fake 2captcha Service - Automatic Setup"
echo "========================================"
echo

# Check if Python is available
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python3 3.8+ and try again"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "macOS: brew install python3"
    exit 1
fi
echo "✓ Python found"

# Create virtual environment
echo "[2/6] Setting up virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi
echo "✓ Virtual environment ready"

# Activate virtual environment
echo "[3/6] Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "[4/6] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
echo "[5/6] Configuring environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
PORT=5001
FAKE_2CAPTCHA_API_KEY=fake_680d0e29b28040ef
EOF
fi
echo "✓ Environment configured"

# Kill any existing process on port 5001
echo "[6/6] Starting service..."
echo "Checking for existing service on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Start the service in background
echo "Starting Fake 2captcha service..."
nohup python fake_2captcha_app.py > fake_2captcha.log 2>&1 &
SERVICE_PID=$!

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Test service
echo "Testing service..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo
    echo "========================================"
    echo "Setup Complete! Service is Running"
    echo "========================================"
    echo
    echo "Service Details:"
    echo "  URL: http://localhost:5001"
    echo "  API Key: fake_680d0e29b28040ef"
    echo "  Process ID: $SERVICE_PID"
    echo "  Status: Running in background"
    echo "  Logs: fake_2captcha.log"
    echo
    echo "Test the service:"
    echo "  curl http://localhost:5001/health"
    echo "  curl http://localhost:5001/res.php?key=fake_680d0e29b28040ef&action=getbalance"
    echo
    echo "To stop the service:"
    echo "  kill $SERVICE_PID"
    echo
    echo "Your INI configuration is ready to use!"
    echo
else
    echo "ERROR: Service failed to start"
    echo "Check fake_2captcha.log for errors"
    kill $SERVICE_PID 2>/dev/null || true
    exit 1
fi 