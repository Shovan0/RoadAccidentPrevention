# database.py  –  Supabase REST API helper for Road Accident Prevention
import os
from dotenv import load_dotenv
import bcrypt
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase client with REST API
SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key for write operations

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_KEY in .env")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ [DB] Supabase REST API client initialized successfully")
except Exception as e:
    print(f"❌ [DB] Failed to initialize Supabase client: {e}")
    supabase = None


def get_all_car_numbers():
    """Return a list of every car_number registered in the database."""
    try:
        if not supabase:
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
        if not supabase:
            return None
        
        # Get car data
        cars_response = supabase.table("cars").select("*").eq("car_number", plate).execute()
        if not cars_response.data:
            return None
        
        car = cars_response.data[0]
        
        # Get owner data if owner_id exists
        owner = None
        if car.get("owner_id"):
            owner_response = supabase.table("owners").select("*").eq("owner_id", car["owner_id"]).execute()
            if owner_response.data:
                owner = owner_response.data[0]
        
        # Get driver data if driver_id exists
        driver = None
        if car.get("driver_id"):
            driver_response = supabase.table("drivers").select("*").eq("driver_id", car["driver_id"]).execute()
            if driver_response.data:
                driver = driver_response.data[0]
        
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
        if not supabase:
            return False
        
        # Build the record - don't include violation_timestamp so DB uses CURRENT_TIMESTAMP default
        record = {
            "plate": plate,
            "vehicle_type": vehicle_type,
            "speed": float(speed),
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
        
        supabase.table("violation_logs").insert(record).execute()
        print(f"✅ [DB] Violation logged for plate: {plate} at speed: {speed} km/h")
        return True
    except Exception as e:
        print(f"❌ [DB] save_violation_log failed: {e}")
        return False


def get_all_violation_logs():
    """Fetch all violation logs from the violation_logs table, sorted by timestamp (newest first)."""
    try:
        if not supabase:
            return []
        response = supabase.table("violation_logs").select("*").order("violation_timestamp", desc=True).execute()
        print(f"✅ [DB] Retrieved {len(response.data)} violation logs")
        return response.data
    except Exception as e:
        print(f"❌ [DB] get_all_violation_logs failed: {e}")
        return []


def get_violation_logs_by_plate(plate):
    """Fetch all violation logs for a specific plate."""
    try:
        if not supabase:
            return []
        response = supabase.table("violation_logs").select("*").eq("plate", plate).order("violation_timestamp", desc=True).execute()
        print(f"✅ [DB] Retrieved {len(response.data)} violation logs for plate: {plate}")
        return response.data
    except Exception as e:
        print(f"❌ [DB] get_violation_logs_by_plate failed: {e}")
        return []
