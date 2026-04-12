Notification setup and testing

1) Create a .env file
- Copy `.env.example` to `.env` and fill your values.

2) Important notes
- `TWILIO_FROM_NUMBER` must be a phone number owned by your Twilio account (or valid alphanumeric sender ID for some countries).
- Trial Twilio accounts can only send to verified recipient numbers. Upgrade to send to arbitrary numbers.
- Use E.164 format for phone numbers (e.g. +919876543210).

3) Install dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

4) Start the backend
```bash
python main.py
```

5) Check notifier configuration
```bash
curl http://localhost:5000/api/notify-status
```

6) Quick notification tests
- Twilio SMS (replace phone):
```bash
curl "http://localhost:5000/api/test-notify?mode=sms&phone=+91YYYYYYYYYY&body=Test+SMS"
```


7) Direct test script
```bash
python twilio_test.py +91YYYYYYYYYY
```

8) Troubleshooting
- If `Twilio credentials not set` appears, ensure `.env` is present and `load_dotenv()` runs (the app prints startup status).
- For Twilio API errors, check the Twilio Console logs and paste error codes here if you need help.
