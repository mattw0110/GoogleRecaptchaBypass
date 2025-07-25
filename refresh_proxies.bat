@echo off
setlocal enabledelayedexpansion

echo 🔄 Proxy Refresh Tool for Google reCAPTCHA Bypass
echo ==================================================

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found. Please run setup first.
    echo Run: setup_automatic.bat
    pause
    exit /b 1
)

REM Check if Python requirements are met
python -c "import requests, concurrent.futures" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Missing Python dependencies. Please run:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Function to show usage
if "%1"=="--help" goto show_usage
if "%1"=="-h" goto show_usage
if "%1"=="/?" goto show_usage

REM Parse command line arguments
set FORCE=
set CLEAN=
set TEST_EXISTING=
set TEST_COUNT=50
set STATS=

:parse_args
if "%1"=="" goto run_script

if "%1"=="--stats" (
    set STATS=--stats
    shift
    goto parse_args
)
if "%1"=="-s" (
    set STATS=--stats
    shift
    goto parse_args
)
if "%1"=="--force" (
    set FORCE=--force
    shift
    goto parse_args
)
if "%1"=="-f" (
    set FORCE=--force
    shift
    goto parse_args
)
if "%1"=="--clean" (
    set CLEAN=--clean
    shift
    goto parse_args
)
if "%1"=="-c" (
    set CLEAN=--clean
    shift
    goto parse_args
)
if "%1"=="--test-existing" (
    set TEST_EXISTING=--test-existing
    shift
    goto parse_args
)
if "%1"=="-e" (
    set TEST_EXISTING=--test-existing
    shift
    goto parse_args
)
if "%1"=="--quick" (
    set TEST_COUNT=25
    shift
    goto parse_args
)
if "%1"=="--full" (
    set TEST_COUNT=100
    shift
    goto parse_args
)

echo ❌ Unknown option: %1
goto show_usage

:run_script
REM Run the proxy refresh script
echo Running proxy refresh with options...
echo.

python refresh_proxies.py !STATS! !FORCE! !CLEAN! !TEST_EXISTING! --test-count !TEST_COUNT!

REM Check exit status
if !errorlevel! equ 0 (
    echo.
    echo ✅ Proxy refresh completed!
) else (
    echo.
    echo ❌ Proxy refresh failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
pause
exit /b 0

:show_usage
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --help              Show this help message
echo   --stats             Show current proxy statistics only
echo   --force             Force refresh even if we have enough proxies
echo   --clean             Clean failed proxies before fetching new ones
echo   --test-existing     Test existing proxies health
echo   --quick             Quick refresh (test 25 proxies)
echo   --full              Full refresh (test 100 proxies)
echo.
echo Examples:
echo   %0                  # Standard refresh (50 proxies)
echo   %0 --stats          # Show current proxy stats
echo   %0 --force --clean  # Force refresh and clean old proxies
echo   %0 --quick          # Quick refresh for testing
echo   %0 --full           # Full refresh for maximum proxies
echo.
pause
exit /b 0 