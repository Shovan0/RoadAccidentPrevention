<#
Activate backend venv and start the Flask app (main.py).
Run from the `backend` folder in PowerShell.

Usage:
  .\start_backend.ps1
#>
Write-Host "Starting backend..."

if (-Not (Test-Path .venv)) {
  Write-Host ".venv not found. Creating virtual environment and installing dependencies..."
  if (Test-Path .\setup_backend.ps1) {
    & .\setup_backend.ps1 -SkipEnvPrompt
  } else {
    Write-Host "setup_backend.ps1 not found; attempting to create venv and install via python..."
    python -m venv .venv
    $venvPython = Join-Path -Path $PWD -ChildPath ".venv\Scripts\python.exe"
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
  }
}

# Use the venv python directly to avoid PowerShell execution policy blocking Activate.ps1
$venvPython = Join-Path -Path $PWD -ChildPath ".venv\Scripts\python.exe"
if (-Not (Test-Path $venvPython)) {
  Write-Error "Virtualenv python not found at $venvPython. Ensure Python is installed and on PATH."
  exit 1
}

Write-Host "Running main.py with venv python (use Ctrl+C to stop)"
& $venvPython main.py
