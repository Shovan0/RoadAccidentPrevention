"""
Create a .env file non-interactively from CLI args or environment variables.

Usage examples:
  # pass as args
  python create_env_cli.py --twilio-sid SID --twilio-token TOKEN --twilio-from +1234567890 --target-phone +9007074039

  # or use environment variables and run without args
  TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... python create_env_cli.py
"""
import os
import argparse

parser = argparse.ArgumentParser(description="Create .env for backend from args or environment variables")
parser.add_argument('--twilio-sid')
parser.add_argument('--twilio-token')
parser.add_argument('--twilio-from')
parser.add_argument('--target-phone')
parser.add_argument('--target-prefix', default='+')
parser.add_argument('--out', default='.env')
args = parser.parse_args()

def pick(argname, envname=None):
    envname = envname or argname.upper()
    val = getattr(args, argname.replace('-', '_'))
    if val:
        return val
    return os.environ.get(envname)

TWILIO_ACCOUNT_SID = pick('twilio-sid', 'TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = pick('twilio-token', 'TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = pick('twilio-from', 'TWILIO_FROM_NUMBER')
TARGET_PHONE = pick('target-phone', 'TARGET_PHONE')
TARGET_PHONE_PREFIX = args.target_prefix or os.environ.get('TARGET_PHONE_PREFIX', '+')

lines = []
if TWILIO_ACCOUNT_SID:
    lines.append(f"TWILIO_ACCOUNT_SID={TWILIO_ACCOUNT_SID}")
if TWILIO_AUTH_TOKEN:
    lines.append(f"TWILIO_AUTH_TOKEN={TWILIO_AUTH_TOKEN}")
if TWILIO_FROM_NUMBER:
    lines.append(f"TWILIO_FROM_NUMBER={TWILIO_FROM_NUMBER}")
if TARGET_PHONE:
    lines.append(f"TARGET_PHONE={TARGET_PHONE}")
if TARGET_PHONE_PREFIX:
    lines.append(f"TARGET_PHONE_PREFIX={TARGET_PHONE_PREFIX}")

if not lines:
    print("No values provided via args or environment. Nothing to write. Use --help for usage.")
    raise SystemExit(1)

with open(args.out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"Wrote {len(lines)} keys to {args.out}")
