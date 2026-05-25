#!/usr/bin/env python3
"""Test script for violation_logs table."""
import os
from dotenv import load_dotenv
from database import save_violation_log, get_all_violation_logs, supabase

load_dotenv()

print("=" * 60)
print("VIOLATION LOGS TEST")
print("=" * 60)

# Check Supabase connection
print("\n1️⃣  Checking Supabase connection...")
if supabase:
    print("✅ Supabase client initialized")
else:
    print("❌ Supabase client NOT initialized")
    exit(1)

# Test table access
print("\n2️⃣  Testing table access...")
try:
    response = supabase.table("violation_logs").select("*").limit(1).execute()
    print(f"✅ Can access violation_logs table")
except Exception as e:
    print(f"❌ Cannot access violation_logs table: {e}")
    exit(1)

# Test inserting a test violation
print("\n3️⃣  Testing insert operation...")
test_plate = f"TEST_PLATE_{os.getenv('HOSTNAME', 'LOCAL')}"
result = save_violation_log(
    plate=test_plate,
    vehicle_type="Test Vehicle",
    speed=85.5,
    driver_name="Test Driver",
    driver_contact="+1234567890",
    owner_name="Test Owner",
    owner_contact="+0987654321"
)

if result:
    print("✅ Insert successful")
else:
    print("❌ Insert failed")
    exit(1)

# Fetch all violations
print("\n4️⃣  Fetching all violations...")
violations = get_all_violation_logs()
print(f"✅ Retrieved {len(violations)} violation(s)")

if violations:
    print("\nRecent violations:")
    for v in violations[:3]:  # Show last 3
        print(f"  - Plate: {v.get('plate')}, Speed: {v.get('speed')} km/h, Time: {v.get('violation_timestamp')}")
else:
    print("⚠️  No violations found")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
