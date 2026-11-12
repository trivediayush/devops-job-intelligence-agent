$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw "Python launcher not found. Install Python 3.11+ and enable Add to PATH." }
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path config.yaml)) { Copy-Item config.example.yaml config.yaml }
Write-Host "Setup complete. Edit config.yaml, then run .\.venv\Scripts\Activate.ps1"
