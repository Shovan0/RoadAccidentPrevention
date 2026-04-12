# db_utils.py - small helpers that extend database.py without modifying it
import mysql.connector
from mysql.connector import Error
import database

DB_CONFIG = database.DB_CONFIG


def update_driver_contact_by_plate(plate, new_contact):
    """Update driver's contact for a car plate. Returns True on success."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT driver_id FROM cars WHERE car_number = %s", (plate,))
        row = cursor.fetchone()
        if not row or row[0] is None:
            cursor.close()
            conn.close()
            return False
        driver_id = row[0]
        cursor.execute("UPDATE drivers SET contact = %s WHERE driver_id = %s", (new_contact, driver_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB_UTIL] Updated contact for driver_id={driver_id} (plate={plate}) -> {new_contact}")
        return True
    except Error as e:
        print(f"[DB_UTIL] update_driver_contact_by_plate failed: {e}")
        return False
