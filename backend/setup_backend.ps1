<#
Setup backend virtual environment and install Python dependencies.
Run from the repository `backend` folder in PowerShell.

Usage:
  Open PowerShell as normal user and run:
    .\setup_backend.ps1

This will:
  - create a .venv directory if missing
  - install packages from requirements.txt using the venv python
  - print next steps to create a .env
#>
param(
    [switch]$SkipEnvPrompt
)

Write-Host "Setting up backend virtualenv and installing requirements..."

if (-Not (Test-Path .venv)) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists. Skipping creation."
}

$venvPython = Join-Path -Path $PWD -ChildPath ".venv\Scripts\python.exe"
if (-Not (Test-Path $venvPython)) {
    Write-Error "Virtualenv python not found at $venvPython. Ensure Python is installed and on PATH."
    exit 1
}

Write-Host "Upgrading pip and installing requirements using venv python..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Backend dependencies installed."

if (-Not $SkipEnvPrompt) {
    Write-Host "To create .env interactively run: python create_env.py"
    Write-Host "Or create .env from .env.example and fill values."
}

Write-Host "Done. Activate the venv with: .\\.venv\\Scripts\\Activate.ps1"
