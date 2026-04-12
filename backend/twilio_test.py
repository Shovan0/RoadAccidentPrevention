"""
Simple Twilio test script. Reads credentials from environment variables.
Run:
    python twilio_test.py +91YYYYYYYYYY

It will attempt to send an SMS (if creds and from number are set).
"""
import sys
import os
from notify import send_twilio_sms

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python twilio_test.py <E.164-phone-number>')
        sys.exit(1)
    to = sys.argv[1]
    body = 'Test message from RoadAccidentPrevention project'

    print('Testing Twilio SMS...')
    ok_sms = send_twilio_sms(to, body)
    print('SMS result:', ok_sms)

    print('Call support removed; only SMS tested.')
