# AI Knowledge Assistant - Interactive Mode Launcher
# PowerShell Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Knowledge Assistant - Interactive Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "Current Directory: $PWD" -ForegroundColor Gray
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "[ERROR] main.py not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[START] Launching AI Knowledge Assistant..." -ForegroundColor Green
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  - Type your question and press Enter"
Write-Host "  - Type 'exit' or 'quit' to exit"
Write-Host "  - Type 'info' to see system information"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Launch Python program
& venv\Scripts\python.exe main.py --mode interactive

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Program exited" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"