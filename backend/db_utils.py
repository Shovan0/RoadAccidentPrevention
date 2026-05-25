# db_utils.py - Supabase REST API utilities
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import socket
import urllib.parse
import time

# Load backend/.env explicitly so env vars are available regardless of CWD
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Initialize Supabase client only if credentials are present and host resolves
SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def _host_resolves(url):
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc or parsed.path
        host = host.split(":")[0]
        socket.getaddrinfo(host, 443)
        return True
    except Exception:
        return False

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ [DB_UTIL] Missing SUPABASE_PROJECT_URL or SUPABASE_SERVICE_KEY in backend/.env")
    supabase: Client = None
elif not _host_resolves(SUPABASE_URL):
    print("❌ [DB_UTIL] Supabase host DNS resolution failed. Database operations will be disabled.")
    supabase: Client = None
else:
    # Try a few times to initialize the client in case of transient network errors
    supabase = None
    delay = 1
    for attempt in range(3):
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            break
        except Exception as e:
            print(f"❌ [DB_UTIL] Supabase init attempt {attempt+1} failed: {e}")
            time.sleep(delay)
            delay *= 2
    if not supabase:
        print("❌ [DB_UTIL] Unable to initialize Supabase client after retries.")


def update_driver_contact_by_plate(plate, new_contact):
    """Update driver's contact for a car plate. Returns True on success."""
    try:
        # Get car by plate to find driver_id
        cars_response = supabase.table("cars").select("driver_id").eq("car_number", plate).execute()
        if not cars_response.data or not cars_response.data[0].get("driver_id"):
            return False
        
        driver_id = cars_response.data[0]["driver_id"]
        
        # Update driver contact
        supabase.table("drivers").update({
            "contact": new_contact
        }).eq("driver_id", driver_id).execute()
        
        print(f"✅ [DB_UTIL] Updated contact for driver_id={driver_id} (plate={plate}) -> {new_contact}")
        return True
    except Exception as e:
        print(f"❌ [DB_UTIL] update_driver_contact_by_plate failed: {e}")
        return False
