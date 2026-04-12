import os
import time
from typing import Optional
from dotenv import load_dotenv

# Load .env at import time so scripts that don't call load_dotenv() still pick up values.
load_dotenv()

# Note: read env values inside the send function to avoid stale values at module-import time.


def _normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return phone
    p = str(phone).strip()
    for ch in [' ', '-', '(', ')']:
        p = p.replace(ch, '')
    if p.startswith('+'):
        return p
    if p.startswith('0') and len(p) == 11:
        p = p[1:]
    if p.isdigit() and len(p) == 10:
        prefix = os.getenv('TARGET_PHONE_PREFIX', '+91')
        return prefix + p
    if p.isdigit() and len(p) >= 11 and p.startswith('91'):
        return '+' + p
    return p


def send_twilio_sms(to_number: str, body: str) -> bool:
    """Send SMS via Twilio. Returns True on success."""
    # Re-read env vars in case they were set after module import
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER):
        print('[NOTIFY] Twilio credentials not set; skipping Twilio SMS')
        return False
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        to_norm = _normalize_phone(to_number)
        attempts = 2
        for i in range(attempts):
            try:
                msg = client.messages.create(from_=TWILIO_FROM_NUMBER, to=to_norm, body=body)
                print(f"[NOTIFY] Twilio SMS sent SID={msg.sid} to={to_norm}")
                return True
            except Exception as e:
                print(f"[NOTIFY] send_twilio_sms attempt {i+1} failed: {e}")
                time.sleep(1 + i)
        return False
    except Exception as e:
        print(f"[NOTIFY] send_twilio_sms failed: {e}")
        return False


def send_sms(to_number: Optional[str], body: str) -> bool:
    """Send SMS using Twilio. Returns True on success, False otherwise."""
    if not to_number:
        print('[NOTIFY] No target phone provided for SMS')
        return False
    return send_twilio_sms(to_number, body)
