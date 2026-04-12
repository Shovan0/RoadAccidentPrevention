Backend setup and run
---------------------

Prerequisites
- Python 3.8+ installed and on PATH
- Node/npm for frontend (handled separately)

Quick steps

1. Create and activate venv, install deps

```powershell
cd backend
.\setup_backend.ps1
.\.venv\Scripts\Activate.ps1
```

2. Create `.env` (interactive)

```powershell
python create_env.py
# or non-interactive
python create_env_cli.py --twilio-sid SID --twilio-token TOKEN --twilio-from +123... --target-phone +900...
```

3. Check env

```powershell
python check_notify_env.py
```

4. Start backend

```powershell
.\start_backend.ps1
```

5. Test Twilio (after backend running and valid creds)

```powershell
python twilio_test.py +9007074039
```

If you run into errors, paste the full console output here and I will help diagnose.
