# database.py  –  MySQL helper for Road Accident Prevention
import mysql.connector
from mysql.connector import Error
import bcrypt

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "database": "road-accident-prevention",
    "user":     "root",
    "password": "Shovan@2001",
}


def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_all_car_numbers():
    """Return a list of every car_number registered in the database."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT car_number FROM cars")
        plates = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return plates
    except Error as e:
        print(f"[DB] get_all_car_numbers failed: {e}")
        return []


def get_vehicle_details(plate):
    """
    Return a dict with full car + owner + driver details for the given plate.
    Returns None if the plate is not found or the DB is unreachable.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                c.car_number,
                c.make,
                c.model,
                c.year,
                c.color,
                c.vehicle_type,
                o.owner_id,
                o.name        AS owner_name,
                o.contact     AS owner_contact,
                o.email       AS owner_email,
                o.address     AS owner_address,
                d.driver_id,
                d.name        AS driver_name,
                d.license_number,
                d.contact     AS driver_contact,
                d.email       AS driver_email,
                d.date_of_birth
            FROM cars c
            LEFT JOIN owners  o ON c.owner_id  = o.owner_id
            LEFT JOIN drivers d ON c.driver_id = d.driver_id
            WHERE c.car_number = %s
            """,
            (plate,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Error as e:
        print(f"[DB] get_vehicle_details failed: {e}")
        return None


def get_all_registered_cars():
    """Return all cars with joined owner and driver info (for admin panel)."""
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                c.car_number,
                c.make, c.model, c.year, c.color, c.vehicle_type,
                o.name        AS owner_name,
                o.contact     AS owner_contact,
                d.name        AS driver_name,
                d.license_number,
                d.contact     AS driver_contact
            FROM cars c
            LEFT JOIN owners  o ON c.owner_id  = o.owner_id
            LEFT JOIN drivers d ON c.driver_id = d.driver_id
            ORDER BY c.car_number
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"[DB] get_all_registered_cars failed: {e}")
        return []


# ── User authentication helpers ───────────────────────────────────────────────

def get_user_by_username(username):
    """Return {username, password, role} dict or None if not found."""
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT username, password, role FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Error as e:
        print(f"[DB] get_user_by_username failed: {e}")
        return None


def create_user(username, password_hash, role="user"):
    """Insert a new user. password_hash must already be a bcrypt hash string."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password_hash, role),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"[DB] create_user failed: {e}")
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
                print(f"[DB] Seeded default user: {username} (role={role})")
