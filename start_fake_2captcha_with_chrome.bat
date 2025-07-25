@echo off
setlocal enabledelayedexpansion

echo === Fake 2captcha Service Startup ===
echo This script will start Chrome with debugging and then start the fake 2captcha service
echo Chrome will continue running even if this script is terminated
echo.

REM Function to check if Chrome is running on port 9222
:check_chrome_debug
netstat -an | findstr ":9222" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    goto chrome_running
) else (
    goto chrome_not_running
)

:chrome_running
echo ✅ Chrome is already running with debugging on port 9222
goto start_service

:chrome_not_running
echo 🌐 Chrome is not running with debugging. Starting Chrome in headless mode...
call :start_chrome_debug
goto start_service

:start_chrome_debug
echo Starting Chrome with remote debugging in headless mode...

REM Kill any existing Chrome processes on port 9222
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9222"') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Wait for processes to terminate
timeout /t 2 /nobreak >nul

REM Create unique profile directory
set PROFILE_DIR=%TEMP%\chrome-headless-%RANDOM%

REM Try different Chrome locations
set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) else (
    echo ❌ ERROR: Chrome not found. Please install Google Chrome
    echo Download from: https://www.google.com/chrome/
    pause
    exit /b 1
)

REM Start Chrome with debugging in headless mode
echo Starting Chrome from: !CHROME_PATH!
echo Chrome will run in HEADLESS mode (no visible window)
!CHROME_PATH! ^
    --remote-debugging-port=9222 ^
    --headless=new ^
    --no-first-run ^
    --no-default-browser-check ^
    --disable-default-apps ^
    --disable-popup-blocking ^
    --disable-web-security ^
    --disable-features=VizDisplayCompositor ^
    --disable-dev-shm-usage ^
    --disable-gpu ^
    --no-sandbox ^
    --disable-setuid-sandbox ^
    --disable-background-timer-throttling ^
    --disable-backgrounding-occluded-windows ^
    --disable-renderer-backgrounding ^
    --disable-features=TranslateUI ^
    --disable-ipc-flooding-protection ^
    --disable-logging ^
    --log-level=3 ^
    --silent-launch ^
    --user-data-dir="!PROFILE_DIR!" ^
    --window-size=1920,1080 ^
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" >nul 2>&1 &

echo Chrome started in headless mode (detached - no visible window)

REM Wait for Chrome to be ready
echo Waiting for Chrome to be ready...
set /a counter=0
:wait_chrome
set /a counter+=1
curl -s http://127.0.0.1:9222/json/version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Chrome is ready on port 9222 in headless mode
    goto :eof
)
if !counter! geq 30 (
    echo ❌ ERROR: Chrome failed to start properly
    exit /b 1
)
echo Waiting... (!counter!/30)
timeout /t 1 /nobreak >nul
goto wait_chrome

:start_service
REM Clean up any existing processes on port 5001
echo Cleaning up existing processes on port 5001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "venv\Scripts\python.exe" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found. Creating one...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ ERROR: Failed to create virtual environment
        echo Please ensure Python is installed and in PATH
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo ❌ ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Start the fake 2captcha service
echo Starting fake 2captcha service...
echo Service will be available at: http://localhost:5001
echo Health check: http://localhost:5001/health
echo.
echo Press Ctrl+C to stop the service
echo.

python fake_2captcha_app.py

REM If we reach here, the service has stopped
echo.
echo 🛑 Service stopped
echo 📝 Note: Chrome will continue running in headless mode for other processes
echo 🔧 To stop Chrome manually: taskkill /F /IM chrome.exe
pause 