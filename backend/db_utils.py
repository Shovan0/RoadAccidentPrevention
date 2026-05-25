# db_utils.py - Supabase REST API utilities
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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
