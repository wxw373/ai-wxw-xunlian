# AI Knowledge Assistant - Quick Start
# This script will start the interactive mode

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Knowledge Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting AI Knowledge Assistant..." -ForegroundColor Green
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  - Type your question and press Enter"
Write-Host "  - Type 'exit' to quit"
Write-Host "  - Type 'info' to see system information"
Write-Host ""
Write-Host "Note: First run may take a few minutes to initialize." -ForegroundColor Gray
Write-Host ""

# Run the interactive mode
& venv\Scripts\python.exe main.py --mode interactive

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Session ended" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"