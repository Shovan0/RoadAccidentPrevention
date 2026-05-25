#!/usr/bin/env python3
"""Test the violations API endpoints."""
import os
import json
from dotenv import load_dotenv
import bcrypt
from database import get_user_by_username, create_user
from flask_jwt_extended import create_access_token

load_dotenv()

# Setup Flask app context
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import app

print("=" * 60)
print("VIOLATIONS API TEST")
print("=" * 60)

# Create test client
client = app.test_client()

# Get or create test token
print("\n1️⃣  Getting authentication token...")
with app.app_context():
    username = "testuser"
    password = "testpass123"
    
    # Try to get existing user
    user = get_user_by_username(username)
    if not user:
        # Create test user
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
        create_user(username, pw_hash, "user")
        print(f"✅ Created test user: {username}")
    else:
        print(f"✅ Using existing user: {username}")
    
    # Generate token
    token = create_access_token(identity=username, additional_claims={"role": "user"})
    print(f"✅ Generated JWT token")

# Test violation insertion (no auth required)
print("\n2️⃣  Testing manual violation insertion...")
headers = {"Content-Type": "application/json"}
violation_data = {
    "plate": "ABC123",
    "vehicle_type": "Car",
    "speed": 95.5,
    "driver_name": "John Doe",
    "driver_contact": "+1234567890",
    "owner_name": "Jane Doe",
    "owner_contact": "+0987654321"
}
response = client.post("/api/test-violation", json=violation_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.get_json(), indent=2)}")

# Test fetch violations (requires auth)
print("\n3️⃣  Testing fetch all violations (with JWT)...")
headers["Authorization"] = f"Bearer {token}"
response = client.get("/api/violations", headers=headers)
print(f"Status: {response.status_code}")
data = response.get_json()
if isinstance(data, list):
    print(f"✅ Retrieved {len(data)} violations")
    if data:
        print(f"\nLatest violation:")
        v = data[-1]  # Most recent
        print(f"  Plate: {v.get('plate')}")
        print(f"  Speed: {v.get('speed')} km/h")
        print(f"  Vehicle: {v.get('vehicle_type')}")
        print(f"  Timestamp: {v.get('violation_timestamp')}")
else:
    print(f"❌ Error: {data}")

# Test fetch violations by plate
print("\n4️⃣  Testing fetch violations by plate (ABC123)...")
response = client.get("/api/violations/ABC123", headers=headers)
print(f"Status: {response.status_code}")
data = response.get_json()
if isinstance(data, list):
    print(f"✅ Retrieved {len(data)} violations for plate ABC123")
else:
    print(f"Response: {json.dumps(data, indent=2)}")

print("\n" + "=" * 60)
print("API TEST COMPLETE")
print("=" * 60)
