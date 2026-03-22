@echo off
chcp 65001 >nul
title AI Knowledge Assistant - Interactive Mode

echo ========================================
echo AI Knowledge Assistant - Interactive Mode
echo ========================================
echo.

cd /d "%~dp0"

echo Current Directory: %CD%
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo [ERROR] main.py not found!
    echo.
    pause
    exit /b 1
)

echo [START] Launching AI Knowledge Assistant...
echo.
echo Tips:
echo   - Type your question and press Enter
echo   - Type 'exit' or 'quit' to exit
echo   - Type 'info' to see system information
echo.
echo ========================================
echo.

venv\Scripts\python.exe main.py --mode interactive

echo.
echo ========================================
echo Program exited
echo ========================================
pause