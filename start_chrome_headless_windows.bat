@echo off
setlocal enabledelayedexpansion

echo === Chrome Headless Debug Startup ===
echo Starting Chrome in headless mode with remote debugging...
echo.

REM Kill all Chrome processes first
echo Terminating existing Chrome processes...
taskkill /IM chrome.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul

REM Find Chrome installation
set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) else (
    echo ❌ ERROR: Google Chrome not found!
    pause
    exit /b 1
)

REM Create clean profile directory
set PROFILE_DIR=%TEMP%\chrome-headless-%RANDOM%
echo Using profile: !PROFILE_DIR!

REM Clear port 9222
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9222" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting Chrome in HEADLESS mode...

REM Start Chrome in background (headless)
cmd /c "!CHROME_PATH! --remote-debugging-port=9222 --headless=new --no-first-run --disable-web-security --no-sandbox --disable-gpu --user-data-dir="!PROFILE_DIR!"" >nul 2>&1 &

echo Waiting for Chrome debugging to be ready...

REM Wait for Chrome debugging
set /a counter=0
:wait_chrome
set /a counter+=1
curl -s --connect-timeout 2 http://127.0.0.1:9222/json/version >nul 2>&1
if %errorlevel% == 0 (
    echo.
    echo ✅ SUCCESS: Chrome is running in HEADLESS mode!
    echo Testing connection...
    curl -s http://127.0.0.1:9222/json/version
    echo.
    echo Chrome debugging ready at: http://127.0.0.1:9222
    echo You can now start your fake 2captcha service.
    pause
    goto :eof
)

if !counter! geq 20 (
    echo.
    echo ❌ ERROR: Chrome headless mode failed to start
    echo Try running as Administrator or check antivirus settings
    pause
    exit /b 1
)

echo Waiting... (!counter!/20)
timeout /t 1 /nobreak >nul
goto wait_chrome 