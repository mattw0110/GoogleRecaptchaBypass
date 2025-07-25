@echo off
setlocal enabledelayedexpansion

echo === Chrome Debug Mode Startup ===
echo This will start Chrome with remote debugging on port 9222
echo.

REM Kill all Chrome processes first
echo Terminating existing Chrome processes...
taskkill /IM chrome.exe /F >nul 2>&1
taskkill /IM chrome.exe /T /F >nul 2>&1

REM Wait for processes to fully terminate
echo Waiting for Chrome processes to terminate...
timeout /t 5 /nobreak >nul

REM Find Chrome installation
set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
    echo Found Chrome at: C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    echo Found Chrome at: C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
    echo Found Chrome at: %LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
) else (
    echo ❌ ERROR: Google Chrome not found!
    echo Please install Chrome from: https://www.google.com/chrome/
    echo Or check if Chrome is installed in a different location.
    pause
    exit /b 1
)

REM Create clean profile directory
set PROFILE_DIR=%TEMP%\chrome-debug-%RANDOM%-%TIME:~6,2%
echo Profile directory: !PROFILE_DIR!

REM Clear port 9222 if something else is using it
echo Checking port 9222...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9222" ^| findstr "LISTENING"') do (
    echo Terminating process using port 9222: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting Chrome with debugging...
echo Chrome path: !CHROME_PATH!
echo Profile: !PROFILE_DIR!
echo.

REM Start Chrome with comprehensive debugging flags (headless)
!CHROME_PATH! ^
    --remote-debugging-port=9222 ^
    --remote-debugging-address=127.0.0.1 ^
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
    --disable-extensions ^
    --disable-plugins ^
    --disable-sync ^
    --disable-translate ^
    --disable-background-networking ^
    --disable-client-side-phishing-detection ^
    --disable-component-extensions-with-background-pages ^
    --disable-domain-reliability ^
    --disable-hang-monitor ^
    --disable-prompt-on-repost ^
    --disable-sync-preferences ^
    --metrics-recording-only ^
    --safebrowsing-disable-auto-update ^
    --user-data-dir="!PROFILE_DIR!" ^
    --window-size=1920,1080 ^
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" ^
    --disable-logging ^
    --log-level=3 ^
    --silent-launch >nul 2>&1 &

echo Chrome started in headless mode. Waiting for debugging interface to be ready...

REM Wait for Chrome debugging to be available
set /a counter=0
:wait_chrome
set /a counter+=1
curl -s --connect-timeout 2 http://127.0.0.1:9222/json/version >nul 2>&1
if %errorlevel% == 0 (
    echo.
    echo ✅ SUCCESS: Chrome debugging is ready!
    echo Testing connection...
    curl -s http://127.0.0.1:9222/json/version
    echo.
    echo Chrome debugging is now available at: http://127.0.0.1:9222
    echo You can now start the fake 2captcha service.
    echo.
    echo To stop Chrome debug mode, run: taskkill /IM chrome.exe /F
    pause
    goto :eof
)

if !counter! geq 30 (
    echo.
    echo ❌ ERROR: Chrome debugging failed to start after 30 seconds
    echo.
    echo Troubleshooting:
    echo 1. Check if Chrome is running: tasklist ^| findstr chrome
    echo 2. Check port 9222: netstat -ano ^| findstr :9222
    echo 3. Try running as Administrator
    echo 4. Check Windows Defender/Antivirus settings
    echo 5. Verify Chrome installation
    echo.
    pause
    exit /b 1
)

echo Waiting... (!counter!/30)
timeout /t 1 /nobreak >nul
goto wait_chrome 