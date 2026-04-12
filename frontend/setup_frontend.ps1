<#
Install frontend Node dependencies and start dev server.
Run from the `frontend` folder.

Usage:
  .\setup_frontend.ps1
#>
Write-Host "Installing frontend dependencies..."
npm install

Write-Host "Starting dev server (npm run dev)..."
npm run dev
