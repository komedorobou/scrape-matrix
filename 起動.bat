@echo off
setlocal

cd /d "%~dp0"

echo.
echo   ========================================
echo   Brand EC Scraper
echo   ========================================
echo.

REM ========== Check Python ==========
python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python not found.
    echo   Install from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

REM ========== Create venv if needed ==========
if exist "venv\Scripts\python.exe" goto :HAS_VENV

echo   [SETUP] Creating virtual environment...
python -m venv venv
if not exist "venv\Scripts\python.exe" (
    echo   [ERROR] Failed to create venv.
    pause
    exit /b 1
)
echo   [SETUP] Ensuring pip...
venv\Scripts\python.exe -m ensurepip --upgrade >nul 2>&1
echo         Done.
echo.

:HAS_VENV

REM ========== Install / update packages ==========
echo   Checking libraries...
venv\Scripts\python.exe -m pip install --disable-pip-version-check -q setuptools streamlit requests beautifulsoup4 pandas openpyxl undetected-chromedriver
if errorlevel 1 (
    echo   [ERROR] pip install failed.
    pause
    exit /b 1
)

REM ========== Verify ==========
venv\Scripts\python.exe -c "import undetected_chromedriver; import streamlit; print()"
if errorlevel 1 (
    echo   [ERROR] Package verification failed.
    pause
    exit /b 1
)
echo   Libraries OK.
echo.

REM ========== Launch ==========
echo   ----------------------------------------
echo   Starting app...
echo   Browser will open automatically.
echo   To quit: close this window.
echo   ----------------------------------------
echo.

venv\Scripts\python.exe -m streamlit run app.py

endlocal
