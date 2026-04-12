<#
Verify notification environment and optionally run Twilio test.
Run from the `backend` folder in PowerShell.

Usage:
  .\verify_and_test.ps1

# This will:
#  - activate the venv at .venv
#  - run `python check_notify_env.py`
#  - show whether `twilio` package is installed
#  - optionally run `python twilio_test.py <phone>` to send a test SMS
#>

if (-Not (Test-Path .venv)) {
    Write-Error ".venv not found. Run .\setup_backend.ps1 first."
    exit 1
}

Write-Host "Activating venv..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Running environment checks..."
python check_notify_env.py

Write-Host "Checking Twilio package..."
python -m pip show twilio > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Twilio package not found. Install with: python -m pip install twilio"
}

$tw_ok = $false
try {
    $pyOut = python -c "import os,sys; ok = bool(os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN') and os.getenv('TWILIO_FROM_NUMBER')); sys.stdout.write('1' if ok else '0')"
    if ($pyOut.Trim() -eq '1') { $tw_ok = $true }
} catch {
    # ignore
}

if (-Not $tw_ok) {
    Write-Host "Twilio credentials not fully configured. Fill TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER in .env or environment."
    $shouldTest = Read-Host "Do you still want to attempt a twilio_test run? (y/N)"
    if (-Not $shouldTest.ToLower().StartsWith('y')) { exit 0 }
}

# Determine phone to test
$target = $env:TARGET_PHONE
if (-Not $target) { $target = Read-Host "Enter E.164 phone number to test (e.g. +9190...)" }
if (-Not $target) { Write-Host "No phone provided; aborting test."; exit 0 }

Write-Host "Running twilio_test.py against $target"
python twilio_test.py $target

Write-Host "Done. If the test failed, paste the script output here and I'll help debug."
