@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Google reCAPTCHA Bypass - Windows Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo ✅ pip found

REM Check if Chrome is installed
set CHROME_FOUND=0
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

if !CHROME_FOUND! == 0 (
    echo ⚠️  WARNING: Google Chrome not found
    echo Please install Chrome from: https://www.google.com/chrome/
    echo The service can still work but you'll need Chrome for captcha solving
    echo.
) else (
    echo ✅ Google Chrome found
)

REM Check if curl is available (for testing)
curl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: curl not found
    echo Install curl for testing: https://curl.se/windows/
    echo Or use PowerShell Invoke-WebRequest instead
    echo.
) else (
    echo ✅ curl found
)

echo.
echo 🔧 Setting up virtual environment...

REM Remove existing virtual environment if it exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to create virtual environment
    echo Please check your Python installation
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install requirements
    echo Please check your internet connection and requirements.txt file
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

echo.
echo 🧪 Testing installation...

REM Test if Flask can be imported
python -c "import flask; print('✅ Flask:', flask.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Flask import failed
) else (
    echo ✅ Flask working
)

REM Test if DrissionPage can be imported
python -c "import DrissionPage; print('✅ DrissionPage working')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ DrissionPage import failed
) else (
    echo ✅ DrissionPage working
)

REM Test if speech_recognition can be imported
python -c "import speech_recognition; print('✅ SpeechRecognition working')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ SpeechRecognition import failed
) else (
    echo ✅ SpeechRecognition working
)

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo 🚀 To start the service:
echo    start_fake_2captcha_with_chrome.bat
echo.
echo 🧪 To test the setup:
echo    python test_fake_2captcha.py
echo.
echo 📋 Available files:
echo    - start_fake_2captcha_with_chrome.bat  (Main startup script)
echo    - setup_automatic.bat                  (This setup script)
echo    - test_fake_2captcha.py               (Test suite)
echo    - fake_2captcha_app.py                (Main service)
echo    - RecaptchaSolver.py                  (Captcha solver)
echo.
echo 🔧 Service Details:
echo    - API URL: http://localhost:5001
echo    - API Key: fake_680d0e29b28040ef
echo    - Chrome Debug Port: 9222
echo.
echo 📖 For help and documentation, see README.md
echo.
pause 