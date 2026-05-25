#!/usr/bin/env python3
"""Test script to verify Supabase REST API connection."""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

print(f"🔍 Attempting to connect to Supabase REST API...")
print(f"📍 Project URL: {SUPABASE_URL}")

try:
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized!")
    
    # Test connection by fetching car count
    print("\n📊 Testing database access...")
    cars_response = supabase.table("cars").select("*", count="exact").execute()
    car_count = len(cars_response.data) if cars_response.data else 0
    
    print(f"✅ Successfully fetched cars from database!")
    print(f"📊 Total cars in database: {car_count}")
    
    # Check users table
    users_response = supabase.table("users").select("*", count="exact").execute()
    user_count = len(users_response.data) if users_response.data else 0
    print(f"👥 Total users in database: {user_count}")
    
    # List some tables
    print(f"\n📑 Sample data from cars table:")
    if cars_response.data:
        for i, car in enumerate(cars_response.data[:3]):
            print(f"  {i+1}. {car.get('car_number')} - {car.get('make')} {car.get('model')}")
    
    print("\n✨ All REST API tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

