# database.py  –  Supabase REST API helper for Road Accident Prevention
import os
from dotenv import load_dotenv
import bcrypt
from supabase import create_client, Client
import socket
import time
import urllib.parse
import json
from datetime import datetime

# Local fallback plates file (used when Supabase is unreachable)
LOCAL_PLATES_PATH = os.path.join(os.path.dirname(__file__), "local_plates.json")

# Local fallback users file (used when Supabase is unreachable)
LOCAL_USERS_PATH = os.path.join(os.path.dirname(__file__), "local_users.json")
LOCAL_VIOLATIONS_PATH = os.path.join(os.path.dirname(__file__), "local_violations.json")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Initialize Supabase client with REST API
SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key for write operations

def resolve_host(url):
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc or parsed.path
        host = host.split(":")[0]
        socket.getaddrinfo(host, 443)
        return True, host
    except Exception as e:
        return False, str(e)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ [DB] Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_KEY in backend/.env")
    supabase = None
else:
    ok, info = resolve_host(SUPABASE_URL)
    if not ok:
        print(f"❌ [DB] DNS resolution failed for Supabase host: {info}")
        print("   Suggestions: check internet connection, VPN/proxy/firewall, or your backend/.env host value.")
        supabase = None
    else:
        host = info
        # Try to initialize client with retries to handle transient network issues
        supabase = None
        attempts = 3
        delay = 1
        for i in range(attempts):
            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("✅ [DB] Supabase REST API client initialized successfully")
                break
            except Exception as e:
                print(f"❌ [DB] Supabase client init attempt {i+1} failed: {e}")
                time.sleep(delay)
                delay *= 2
        if not supabase:
            print("❌ [DB] All Supabase client init attempts failed. Database operations will be disabled until connectivity is restored.")


def get_all_car_numbers():
    """Return a list of every car_number registered in the database."""
    try:
        if not supabase:
            # Supabase unavailable — try local plates file as fallback
            try:
                if os.path.exists(LOCAL_PLATES_PATH):
                    with open(LOCAL_PLATES_PATH, 'r') as f:
                        data = json.load(f)
                    plates = list(data) if isinstance(data, list) else []
                    print(f"✅ [DB-LOCAL] Loaded {len(plates)} plates from local_plates.json")
                    return plates
            except Exception as e:
                print(f"❌ [DB-LOCAL] Failed to load local plates: {e}")
            print("⚠️ [DB] Supabase unavailable and no local plates found — returning empty plate list.")
            return []
        response = supabase.table("cars").select("car_number").execute()
        plates = [row["car_number"] for row in response.data]
        print(f"✅ [DB] Retrieved {len(plates)} car numbers")
        return plates
    except Exception as e:
        print(f"❌ [DB] get_all_car_numbers failed: {e}")
        return []


def get_vehicle_details(plate):
    """
    Return a dict with full car + owner + driver details for the given plate.
    Returns None if the plate is not found or the DB is unreachable.
    """
    try:
        # Normalize plate formatting
        plate = (plate or "").strip().upper()

        if not supabase:
            # If supabase not available, try local plates (no details)
            print("⚠️ [DB] Supabase unavailable — cannot fetch vehicle details")
            return None

        # Get car data
        cars_response = supabase.table("cars").select("*").eq("car_number", plate).execute()
        if not cars_response.data:
            print(f"⚠️ [DB] No car record found for plate: {plate}")
            return None
        
        car = cars_response.data[0]
        
        # Get owner data if owner_id exists
        owner = None
        owid = car.get("owner_id")
        if owid:
            # coerce numeric id when possible
            try:
                owq = int(owid)
            except Exception:
                owq = owid
            owner_response = supabase.table("owners").select("*").eq("owner_id", owq).execute()
            if owner_response.data:
                owner = owner_response.data[0]
            else:
                print(f"[DB] Owner not found for owner_id={owid} in car record: {car}")
        
        # Get driver data if driver_id exists
        driver = None
        drid = car.get("driver_id")
        if drid:
            try:
                drq = int(drid)
            except Exception:
                drq = drid
            driver_response = supabase.table("drivers").select("*").eq("driver_id", drq).execute()
            if driver_response.data:
                driver = driver_response.data[0]
            else:
                print(f"[DB] Driver not found for driver_id={drid} in car record: {car}")
        
        # Construct response dict with all details
        result = {
            "car_number": car.get("car_number"),
            "make": car.get("make"),
            "model": car.get("model"),
            "year": car.get("year"),
            "color": car.get("color"),
            "vehicle_type": car.get("vehicle_type"),
            "owner_id": car.get("owner_id"),
            "owner_name": owner.get("name") if owner else None,
            "owner_contact": owner.get("contact") if owner else None,
            "owner_email": owner.get("email") if owner else None,
            "owner_address": owner.get("address") if owner else None,
            "driver_id": car.get("driver_id"),
            "driver_name": driver.get("name") if driver else None,
            "driver_license_number": driver.get("license_number") if driver else None,
            "driver_contact": driver.get("contact") if driver else None,
            "driver_email": driver.get("email") if driver else None,
            "driver_date_of_birth": driver.get("date_of_birth") if driver else None,
        }
        print(f"✅ [DB] Retrieved vehicle details for plate: {plate}")
        return result
    except Exception as e:
        print(f"❌ [DB] get_vehicle_details failed: {e}")
        return None


def get_all_registered_cars():
    """Return all cars with joined owner and driver info (for admin panel)."""
    try:
        if not supabase:
            return []
        
        # Get all cars
        cars_response = supabase.table("cars").select("*").execute()
        cars = cars_response.data
        
        result = []
        for car in cars:
            # Get owner data
            owner = None
            if car.get("owner_id"):
                owner_response = supabase.table("owners").select("*").eq("owner_id", car["owner_id"]).execute()
                if owner_response.data:
                    owner = owner_response.data[0]
            
            # Get driver data
            driver = None
            if car.get("driver_id"):
                driver_response = supabase.table("drivers").select("*").eq("driver_id", car["driver_id"]).execute()
                if driver_response.data:
                    driver = driver_response.data[0]
            
            # Build car entry
            car_entry = {
                "car_number": car.get("car_number"),
                "make": car.get("make"),
                "model": car.get("model"),
                "year": car.get("year"),
                "color": car.get("color"),
                "vehicle_type": car.get("vehicle_type"),
                "owner_name": owner.get("name") if owner else None,
                "owner_contact": owner.get("contact") if owner else None,
                "driver_name": driver.get("name") if driver else None,
                "driver_license_number": driver.get("license_number") if driver else None,
                "driver_contact": driver.get("contact") if driver else None,
            }
            result.append(car_entry)
        
        print(f"✅ [DB] Retrieved {len(result)} registered cars")
        return result
    except Exception as e:
        print(f"❌ [DB] get_all_registered_cars failed: {e}")
        return []


# ── User authentication helpers ───────────────────────────────────────────────

def get_user_by_username(username):
    """Return {username, password, role} dict or None if not found."""
    try:
        if not supabase:
            # Fallback to local users file when DB is unreachable
            try:
                if os.path.exists(LOCAL_USERS_PATH):
                    with open(LOCAL_USERS_PATH, 'r') as f:
                        users = json.load(f)
                    user = users.get(username)
                    if user:
                        return user
            except Exception as e:
                print(f"❌ [DB] local users load failed: {e}")
            return None
        response = supabase.table("users").select("*").eq("username", username).execute()
        if response.data:
            user = response.data[0]
            return {
                "username": user.get("username"),
                "password": user.get("password"),
                "role": user.get("role")
            }
        return None
    except Exception as e:
        print(f"❌ [DB] get_user_by_username failed: {e}")
        return None


def create_user(username, password_hash, role="user"):
    """Insert a new user. password_hash must already be a bcrypt hash string."""
    try:
        if not supabase:
            # Save to local users file as a fallback
            try:
                users = {}
                if os.path.exists(LOCAL_USERS_PATH):
                    with open(LOCAL_USERS_PATH, 'r') as f:
                        users = json.load(f)
                users[username] = {"username": username, "password": password_hash, "role": role}
                with open(LOCAL_USERS_PATH, 'w') as f:
                    json.dump(users, f, indent=2)
                print(f"✅ [DB] Locally created user: {username} (role={role})")
                return True
            except Exception as e:
                print(f"❌ [DB] create_user local fallback failed: {e}")
                return False
        
        supabase.table("users").insert({
            "username": username,
            "password": password_hash,
            "role": role
        }).execute()
        print(f"✅ [DB] Created user: {username} (role={role})")
        return True
    except Exception as e:
        print(f"❌ [DB] create_user failed: {e}")
        return False


def seed_default_users():
    """Create default admin and user accounts if they do not already exist."""
    defaults = [
        ("admin", "admin123", "admin"),
        ("user",  "user123",  "user"),
    ]
    for username, password, role in defaults:
        if get_user_by_username(username) is None:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
            if create_user(username, pw_hash, role):
                print(f"✅ [DB] Seeded default user: {username} (role={role})")


# ── Violation logging ─────────────────────────────────────────────────────────

def save_violation_log(plate, vehicle_type, speed, driver_name=None, driver_contact=None, 
                       owner_name=None, owner_contact=None):
    """Insert a violation record into the violation_logs table."""
    try:
        # Build the record
        record = {
            "plate": plate,
            "vehicle_type": vehicle_type,
            "speed": float(speed),
            "violation_timestamp": datetime.utcnow().isoformat()
        }

        # Only add optional fields if they're not None
        if driver_name:
            record["driver_name"] = driver_name
        if driver_contact:
            record["driver_contact"] = driver_contact
        if owner_name:
            record["owner_name"] = owner_name
        if owner_contact:
            record["owner_contact"] = owner_contact

        if not supabase:
            # Fallback: persist locally
            try:
                violations = []
                if os.path.exists(LOCAL_VIOLATIONS_PATH):
                    with open(LOCAL_VIOLATIONS_PATH, 'r') as f:
                        violations = json.load(f)
                violations.append(record)
                with open(LOCAL_VIOLATIONS_PATH, 'w') as f:
                    json.dump(violations, f, indent=2)
                print(f"✅ [DB-LOCAL] Violation saved locally for plate: {plate} at speed: {speed} km/h")
                return True
            except Exception as e:
                print(f"❌ [DB-LOCAL] Failed to save violation locally: {e}")
                return False

        supabase.table("violation_logs").insert(record).execute()
        print(f"✅ [DB] Violation logged for plate: {plate} at speed: {speed} km/h")
        return True
    except Exception as e:
        print(f"❌ [DB] save_violation_log failed: {e}")
        return False


def get_all_violation_logs():
    """Fetch all violation logs from the violation_logs table, sorted by timestamp (newest first)."""
    try:
        results = []
        if supabase:
            try:
                response = supabase.table("violation_logs").select("*", order="violation_timestamp", desc=True).execute()
                if response.data:
                    results.extend(response.data)
            except Exception as e:
                print(f"❌ [DB] Remote fetch failed: {e}")

        # Include local persisted violations if present
        try:
            if os.path.exists(LOCAL_VIOLATIONS_PATH):
                with open(LOCAL_VIOLATIONS_PATH, 'r') as f:
                    local = json.load(f)
                results.extend(local)
        except Exception as e:
            print(f"❌ [DB-LOCAL] Failed to read local violations: {e}")

        # Sort by timestamp descending if available
        try:
            results.sort(key=lambda x: x.get('violation_timestamp', ''), reverse=True)
        except Exception:
            pass

        print(f"✅ [DB] Retrieved {len(results)} violation logs (remote + local)")
        return results
    except Exception as e:
        print(f"❌ [DB] get_all_violation_logs failed: {e}")
        return []


def get_violation_logs_by_plate(plate):
    """Fetch all violation logs for a specific plate."""
    try:
        results = []
        if supabase:
            try:
                response = supabase.table("violation_logs").select("*",).eq("plate", plate).order("violation_timestamp", desc=True).execute()
                if response.data:
                    results.extend(response.data)
            except Exception as e:
                print(f"❌ [DB] Remote fetch by plate failed: {e}")

        # Local persisted violations
        try:
            if os.path.exists(LOCAL_VIOLATIONS_PATH):
                with open(LOCAL_VIOLATIONS_PATH, 'r') as f:
                    local = json.load(f)
                results.extend([r for r in local if r.get('plate') == plate])
        except Exception as e:
            print(f"❌ [DB-LOCAL] Failed to read local violations: {e}")

        results.sort(key=lambda x: x.get('violation_timestamp', ''), reverse=True)
        print(f"✅ [DB] Retrieved {len(results)} violation logs for plate: {plate}")
        return results
    except Exception as e:
        print(f"❌ [DB] get_violation_logs_by_plate failed: {e}")
        return []
