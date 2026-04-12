import getpass
import os

print('Create backend/.env interactively (press Enter to skip optional)')

def ask(prompt, required=False, secret=False, default=None):
    while True:
        if secret:
            val = getpass.getpass(f"{prompt}{' (required)' if required else ''}: ")
        else:
            val = input(f"{prompt}{' (required)' if required else ''}{f' [default: {default}]' if default else ''}: ")
        if not val and default is not None:
            val = default
        if required and not val:
            print('This field is required.')
            continue
        return val

sid = ask('TWILIO_ACCOUNT_SID', required=True)
token = ask('TWILIO_AUTH_TOKEN', required=True, secret=True)
from_num = ask('TWILIO_FROM_NUMBER', required=True)

use_target = ask('Set TARGET_PHONE now? (y/N)', default='N')
if use_target.lower().startswith('y'):
    target_phone = ask('TARGET_PHONE (E.164, e.g. +9198...)', required=True)
else:
    target_phone = ''

prefix = ask('TARGET_PHONE_PREFIX', default='+91')

env_lines = []
env_lines.append(f"TWILIO_ACCOUNT_SID={sid}")
env_lines.append(f"TWILIO_AUTH_TOKEN={token}")
env_lines.append(f"TWILIO_FROM_NUMBER={from_num}")
if target_phone:
    env_lines.append(f"TARGET_PHONE={target_phone}")
env_lines.append(f"TARGET_PHONE_PREFIX={prefix}")

path = os.path.join(os.path.dirname(__file__), '.env')
with open(path, 'w') as f:
    f.write('\n'.join(env_lines) + '\n')

print(f"Wrote {path}")
print('Now run:')
print('  python main.py')
print('Or set environment variables in your shell if you prefer.')
