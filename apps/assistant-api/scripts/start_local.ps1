param(
  [switch]$Reload
)

$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

$python = Join-Path $PWD "..\..\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python executable not found at $python"
}

if (-not (Test-Path ".env")) {
  Write-Host "No .env found. Copying .env.example -> .env"
  Copy-Item ".env.example" ".env"
  Write-Host "Update .env values before production use."
}

& $python scripts/check_first_run.py

Write-Host "Starting Ash Assistant API on http://127.0.0.1:8000"
if ($Reload) {
  & $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} else {
  & $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
}
