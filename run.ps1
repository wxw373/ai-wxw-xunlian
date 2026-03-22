# AI RAG Assistant one-click launcher for Windows.
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    $pythonExe = "py"
    $pythonArgs = @("-3")
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "[ERROR] Python 3.9+ is required. Install Python and rerun this script." -ForegroundColor Red
        exit 1
    }
    $pythonExe = "python"
    $pythonArgs = @()
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[SETUP] Creating virtual environment..." -ForegroundColor Cyan
    & $pythonExe @pythonArgs -m venv .venv
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "[SETUP] Installing dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[SETUP] Created .env from .env.example. Add a real API key before asking questions." -ForegroundColor Yellow
}

if (-not (Test-Path "vector_db\chroma.sqlite3")) {
    Write-Host "[SETUP] Building vector index. The first run may download the embedding model." -ForegroundColor Cyan
    & $venvPython main.py --mode index --force
}

$port = if ($env:PORT) { $env:PORT } else { "8501" }
Write-Host "[START] Web app: http://localhost:$port" -ForegroundColor Green
& $venvPython -m streamlit run web_app.py --server.port $port --server.address 0.0.0.0
