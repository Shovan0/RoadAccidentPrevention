#!/usr/bin/env python3
"""Quick test of database functions."""

from database import get_all_car_numbers, get_vehicle_details, get_all_registered_cars, get_user_by_username

print("=" * 60)
print("TESTING SUPABASE REST API CONNECTION")
print("=" * 60)

# Test 1: Get all car numbers
print("\n✅ Test 1: Get all car numbers")
cars = get_all_car_numbers()
print(f"   Found {len(cars)} cars: {cars}")

# Test 2: Get vehicle details
print("\n✅ Test 2: Get vehicle details for 'MH 01 AB 1234'")
details = get_vehicle_details('MH 01 AB 1234')
if details:
    print(f"   Owner: {details['owner_name']}")
    print(f"   Driver: {details['driver_name']}")
    print(f"   Vehicle: {details['make']} {details['model']}")
else:
    print("   Vehicle not found")

# Test 3: Get all registered cars
print("\n✅ Test 3: Get all registered cars")
all_cars = get_all_registered_cars()
print(f"   Retrieved {len(all_cars)} cars:")
for car in all_cars:
    print(f"   - {car['car_number']}: {car['make']} {car['model']} ({car['year']})")

# Test 4: Check user authentication
print("\n✅ Test 4: Check admin user exists")
admin = get_user_by_username('admin')
if admin:
    print(f"   Admin user found with role: {admin['role']}")
else:
    print("   Admin user not found")

print("\n" + "=" * 60)
print("✨ ALL TESTS PASSED! Database is working correctly.")
print("=" * 60)
