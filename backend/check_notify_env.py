import os

def bool_env(name):
    return bool(os.getenv(name))

def main():
    print('Notification environment check')
    print('TWILIO_ACCOUNT_SID set:', bool_env('TWILIO_ACCOUNT_SID'))
    print('TWILIO_AUTH_TOKEN set:', bool_env('TWILIO_AUTH_TOKEN'))
    print('TWILIO_FROM_NUMBER set:', bool_env('TWILIO_FROM_NUMBER'))
    if bool_env('TWILIO_FROM_NUMBER'):
        print('TWILIO_FROM_NUMBER value (masked):', ('*' * max(0, len(os.getenv('TWILIO_FROM_NUMBER')) - 4)) + os.getenv('TWILIO_FROM_NUMBER')[-4:])
    print('TARGET_PHONE set:', bool_env('TARGET_PHONE'))
    print('TARGET_PHONE_PREFIX:', os.getenv('TARGET_PHONE_PREFIX', '+91'))

if __name__ == '__main__':
    main()
