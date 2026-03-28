#!/bin/bash

cd "$(dirname "$0")"

echo ""
echo "  ========================================"
echo "  Brand EC Scraper"
echo "  ========================================"
echo ""

# --- Check Python ---
if ! command -v python3 &> /dev/null; then
    echo "  [ERROR] Python not found."
    echo "  Install from: https://www.python.org/downloads/"
    echo ""
    read -p "  Press Enter to exit..."
    exit 1
fi
echo "  Python $(python3 --version 2>&1 | awk '{print $2}') detected."
echo ""

# --- Windows用venvが残っていたら削除して作り直す ---
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo "  [!] Windows用の古いvenvを検出。削除して作り直します..."
    rm -rf venv
    echo ""
fi

# --- Setup venv (first run only) ---
if [ ! -f "venv/bin/activate" ]; then
    echo "  ----------------------------------------"
    echo "  First-time setup (next time will be fast)"
    echo "  ----------------------------------------"
    echo ""
    echo "  [1/2] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "  [ERROR] Failed to create venv."
        read -p "  Press Enter to exit..."
        exit 1
    fi
    echo "        Done."
    echo ""
fi

VENV_PYTHON="$(pwd)/venv/bin/python3"
VENV_PIP="$(pwd)/venv/bin/pip"

# --- Install packages (check actual import, not flag file) ---
NEED_INSTALL=0

# 必須パッケージが実際にインポートできるかチェック
$VENV_PYTHON -c "import streamlit" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import undetected_chromedriver" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import bs4" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import pandas" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import openpyxl" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import curl_cffi" 2>/dev/null || NEED_INSTALL=1
$VENV_PYTHON -c "import cloudscraper" 2>/dev/null || NEED_INSTALL=1

if [ $NEED_INSTALL -eq 1 ]; then
    echo "  ----------------------------------------"
    echo "  Installing / updating libraries..."
    echo "  (may take 2-3 minutes)"
    echo "  ----------------------------------------"
    echo ""
    $VENV_PIP install --disable-pip-version-check setuptools certifi streamlit requests beautifulsoup4 pandas numpy openpyxl undetected-chromedriver webdriver-manager curl_cffi cloudscraper
    if [ $? -ne 0 ]; then
        echo ""
        echo "  [ERROR] Install failed. Check internet connection."
        echo "  If the error mentions undetected-chromedriver, try:"
        echo "    source venv/bin/activate"
        echo "    pip install undetected-chromedriver"
        echo ""
        read -p "  Press Enter to exit..."
        exit 1
    fi
    echo ""
    echo "  Install complete!"
    echo ""

    # インストール後に再度チェック
    echo "  Verifying installation..."
    VERIFY_OK=1
    $VENV_PYTHON -c "import streamlit; print(f'    streamlit {streamlit.__version__}')" 2>/dev/null || VERIFY_OK=0
    $VENV_PYTHON -c "import undetected_chromedriver; print(f'    undetected-chromedriver OK')" 2>/dev/null || VERIFY_OK=0
    $VENV_PYTHON -c "import selenium; print(f'    selenium {selenium.__version__}')" 2>/dev/null || VERIFY_OK=0
    $VENV_PYTHON -c "import bs4; print('    beautifulsoup4 OK')" 2>/dev/null || VERIFY_OK=0
    $VENV_PYTHON -c "import pandas; print(f'    pandas {pandas.__version__}')" 2>/dev/null || VERIFY_OK=0

    if [ $VERIFY_OK -eq 0 ]; then
        echo ""
        echo "  [WARNING] Some packages may not have installed correctly."
        echo "  The app will start but some features may not work."
        echo ""
    else
        echo "  All packages verified!"
        echo ""
    fi
else
    echo "  All packages already installed."
    echo ""
fi

echo "  ----------------------------------------"
echo "  Starting app..."
echo "  Browser will open automatically."
echo "  To quit: press Ctrl+C or close terminal."
echo "  ----------------------------------------"
echo ""

# ブラウザを自動で開く（3秒待ってからバックグラウンドで開く）
(sleep 3 && open http://localhost:8501) &

$VENV_PYTHON -m streamlit run app.py
