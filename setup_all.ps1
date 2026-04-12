<#
Run full setup: backend venv + install and frontend install.
From repo root run:
  .\setup_all.ps1

This script will call backend/setup_backend.ps1 and frontend/setup_frontend.ps1.
#>
Write-Host "Running backend setup..."
Push-Location .\backend
.\setup_backend.ps1 -SkipEnvPrompt
Pop-Location

Write-Host "Running frontend setup..."
Push-Location .\frontend
.
if (Test-Path .\setup_frontend.ps1) {
    .\setup_frontend.ps1
} else {
    Write-Host "setup_frontend.ps1 not found; running npm install only"
    npm install
}
Pop-Location

Write-Host "Full setup attempted. Activate backend venv manually: .\\backend\\.venv\\Scripts\\Activate.ps1"
