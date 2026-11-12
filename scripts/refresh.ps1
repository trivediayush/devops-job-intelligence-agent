$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw "Virtual environment missing. Run .\scripts\setup.ps1 first." }
& .\.venv\Scripts\python.exe -m job_agent.cli --config config.yaml
