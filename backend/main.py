# main.py
import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, Response, abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import bcrypt
# Import both generators
from process_video import generate_frames, generate_virtual_simulation
# DB helpers
from database import get_all_registered_cars, get_vehicle_details, get_user_by_username, seed_default_users, save_violation_log, get_all_violation_logs, get_violation_logs_by_plate
# Load .env if present and notification helpers
from dotenv import load_dotenv
load_dotenv()

# Notification test helpers (optional)
try:
    from notify import send_twilio_sms
except Exception:
    send_twilio_sms = None
import os

UPLOAD_DIR = "uploads"
HISTORY_DIR = "history"
ALLOWED_EXT = {"mp4", "mov", "avi", "mkv", "webm"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "final-year-project"  
jwt = JWTManager(app)


# Better JWT error responses to avoid opaque 422s and log concise messages
@jwt.unauthorized_loader
def _jwt_missing_callback(callback):
    print("[JWT] Missing or malformed Authorization header")
    return jsonify({"error": "Missing Authorization Header"}), 401


@jwt.invalid_token_loader
def _jwt_invalid_callback(reason):
    print(f"[JWT] Invalid token: {reason}")
    return jsonify({"error": "Invalid token", "message": reason}), 401


@jwt.expired_token_loader
def _jwt_expired_callback(jwt_header, jwt_payload):
    print("[JWT] Token expired")
    return jsonify({"error": "Token has expired"}), 401

HISTORY_FILE = os.path.join(HISTORY_DIR, "processing_history.json")
STREAM_STATS = {}

# Ensure default users exist in the database on startup
seed_default_users()

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except: return []

def save_history(data):
    try:
        with open(HISTORY_FILE, 'w') as f: json.dump(data, f, indent=2)
    except Exception as e: print(f"Save error: {e}")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    user = get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        token = create_access_token(identity=username, additional_claims={"role": user["role"]})
        return jsonify(access_token=token, username=username, role=user["role"])
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/verify-token", methods=["GET"])
@jwt_required()
def verify():
    username = get_jwt_identity()
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"username": username, "role": user["role"]}), 200

@app.route("/api/history", methods=["GET"])
@jwt_required()
def get_history():
    h = load_history()
    h.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify(h), 200

@app.route("/api/history/<hid>", methods=["DELETE"])
@jwt_required()
def del_hist(hid):
    h = load_history()
    h = [x for x in h if x.get("id") != hid]
    save_history(h)
    return jsonify({"msg": "Deleted"}), 200

@app.route("/api/stats", methods=["GET"])
@jwt_required()
def stats():
    h = load_history()
    return jsonify({
        "total_videos": len(h),
        "total_vehicles": sum(len(x.get("all_logs", [])) for x in h),
        "total_violations": sum(len(x.get("overspeed_summary", [])) for x in h)
    }), 200

@app.route("/api/prepare-simulation", methods=["POST"])
def prep():
    if "video" not in request.files: return jsonify({"error": "No file"}), 400
    f = request.files["video"]
    name = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR, name))
    STREAM_STATS[name] = {"total_vehicles": 0, "total_violations": 0}
    return jsonify({"filename": name})

@app.route("/api/stream-status/<fname>", methods=["GET"])
def status(fname): 
    key = fname if "virtual" in fname else secure_filename(fname)
    return jsonify(STREAM_STATS.get(key, {"total_vehicles": 0, "total_violations": 0}))

@app.route("/video_feed/<fname>")
def feed(fname):
    limit = float(request.args.get('limit', 60))
    # 'dist' / line distance removed — not used anymore
    save = request.args.get('save', 'false') == 'true'
    user = request.args.get('user', 'anonymous')
    
    # --- VIRTUAL SIMULATION ---
    if fname == "virtual_simulation":
        def on_live_virtual(s): STREAM_STATS["virtual_simulation"] = s
        return Response(
            generate_virtual_simulation(overspeed_limit_kmh=limit, record_config={"live_callback": on_live_virtual}),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    # --- REAL VIDEO PROCESSING ---
    name = secure_filename(fname)
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.exists(path): abort(404)
    
    def on_live(s): STREAM_STATS[name] = s
    cfg = {"live_callback": on_live}
    
    if save:
        out_name = f"processed_{name}"
        out_path = os.path.join(UPLOAD_DIR, out_name)
        def on_done(d):
            rec = {
                "id": str(uuid.uuid4()), "timestamp": datetime.now().isoformat(),
                "user": user, "original_filename": name,
                "input_video_path": path, "output_video_path": out_path,
                "download_name": out_name, "overspeed_limit": limit,
                "total_vehicles": len(d["all_logs"]), "total_violations": len(d["overspeed_summary"]),
                "overspeed_summary": d["overspeed_summary"], "all_logs": d["all_logs"]
            }
            # Save each violation to the database
            for violation in d["overspeed_summary"]:
                try:
                    vehicle_type = violation.get("label", "Unknown")
                    speed = violation.get("speed", 0)
                    # Use plate if available, otherwise use tracking ID
                    plate = violation.get("plate", f"TRACKED_{violation.get('id', 'unknown')}")
                    
                    save_violation_log(
                        plate=plate,
                        vehicle_type=vehicle_type,
                        speed=speed,
                        driver_name=violation.get("driver_name"),
                        driver_contact=violation.get("driver_contact"),
                        owner_name=violation.get("owner_name"),
                        owner_contact=violation.get("owner_contact")
                    )
                    print(f"✅ [DB] Saved violation: {plate} at {speed} km/h")
                except Exception as e:
                    print(f"⚠️  Failed to save violation: {e}")
            h = load_history()
            h.append(rec)
            save_history(h)
            if name in STREAM_STATS: del STREAM_STATS[name]
        cfg.update({"output_path": out_path, "data_callback": on_done})
        # Allow client to request full preprocessing before streaming by adding ?preprocess=true
        if request.args.get('preprocess', 'false').lower() == 'true':
            cfg.update({"preprocess_first": True})
        
    return Response(generate_frames(path, limit, record_config=cfg), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/download/<fname>", methods=["GET"])
def dl(fname):
    path = os.path.join(UPLOAD_DIR, secure_filename(fname))
    return send_file(path, as_attachment=True) if os.path.exists(path) else abort(404)

# ── Database-backed endpoints ──────────────────────────────────────────────────

@app.route("/api/registered-cars", methods=["GET"])
@jwt_required()
def registered_cars():
    """Return all cars registered in the DB (admin use)."""
    try:
        cars = get_all_registered_cars()
        return jsonify(cars), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/vehicle-details/<path:plate>", methods=["GET"])
@jwt_required()
def vehicle_details(plate):
    """Return full car + owner + driver details for a given plate number."""
    try:
        details = get_vehicle_details(plate)
        if details is None:
            return jsonify({"error": "Vehicle not found"}), 404
        return jsonify(details), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/violations", methods=["GET"])
@jwt_required()
def get_violations():
    """Return all violation logs from the database."""
    try:
        violations = get_all_violation_logs()
        return jsonify(violations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/violations/<plate>", methods=["GET"])
@jwt_required()
def get_violations_by_plate(plate):
    """Return all violations for a specific plate."""
    try:
        violations = get_violation_logs_by_plate(plate)
        return jsonify(violations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-violation", methods=["POST"])
def test_violation():
    """Test endpoint to manually insert a violation (for debugging)."""
    try:
        data = request.get_json() or {}
        plate = data.get("plate", "TEST_PLATE")
        vehicle_type = data.get("vehicle_type", "Test Car")
        speed = float(data.get("speed", 85.0))
        driver_name = data.get("driver_name")
        driver_contact = data.get("driver_contact")
        owner_name = data.get("owner_name")
        owner_contact = data.get("owner_contact")
        
        result = save_violation_log(
            plate=plate,
            vehicle_type=vehicle_type,
            speed=speed,
            driver_name=driver_name,
            driver_contact=driver_contact,
            owner_name=owner_name,
            owner_contact=owner_contact
        )
        
        if result:
            return jsonify({"success": True, "message": f"Violation recorded for {plate}"}), 201
        else:
            return jsonify({"success": False, "message": "Failed to save violation"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/save-simulation-violations", methods=["POST"])
def save_simulation_violations():
    """Save violations from completed simulation to the database."""
    try:
        data = request.get_json() or {}
        violations = data.get("violations", [])
        saved_count = 0
        
        for violation in violations:
            try:
                plate = violation.get("plate", f"SIM_VIO_{violation.get('id', 'unknown')}")
                vehicle_type = violation.get("label", violation.get("vehicle_type", "Unknown"))
                speed = float(violation.get("speed", 0))
                
                result = save_violation_log(
                    plate=plate,
                    vehicle_type=vehicle_type,
                    speed=speed,
                    driver_name=violation.get("driver_name"),
                    driver_contact=violation.get("driver_contact"),
                    owner_name=violation.get("owner_name"),
                    owner_contact=violation.get("owner_contact")
                )
                
                if result:
                    saved_count += 1
            except Exception as e:
                print(f"⚠️  Failed to save simulation violation: {e}")
        
        return jsonify({
            "success": True, 
            "message": f"Saved {saved_count} out of {len(violations)} violations"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/test-notify", methods=["GET", "POST"])
def test_notify():
    """Test notification endpoint. Use query params or JSON:
    - phone: target phone number (E.164 preferred)
    - mode: one of 'sms' or 'all' (default 'all')
    - body: message text to send
    """
    data = request.get_json(silent=True) or {}
    phone = request.args.get('phone') or data.get('phone') or os.getenv('TARGET_PHONE')
    mode = request.args.get('mode') or data.get('mode') or 'all'
    body = request.args.get('body') or data.get('body') or f"Test alert {datetime.now().isoformat()}"

    result = {}

    # SMS via Twilio (requires TWILIO env vars)
    # Note: Telegram and voice-call support removed — only Twilio SMS is available.

    if mode in ('sms', 'all'):
        if send_twilio_sms and phone:
            result['sms'] = bool(send_twilio_sms(phone, body))
        else:
            result['sms'] = False

    # Voice-call support removed.

    return jsonify(result), 200

if __name__ == "__main__":
    # Print notifier configuration (no secrets)
    tw_ok = bool(os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN') and os.getenv('TWILIO_FROM_NUMBER'))
    print(f"[STARTUP] Twilio configured: {tw_ok}")
    if tw_ok:
        # show the from number but not tokens
        print(f"[STARTUP] Twilio from number: {os.getenv('TWILIO_FROM_NUMBER')}")
    print("[STARTUP] Notification status endpoint: /api/notify-status")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


@app.route('/api/notify-status', methods=['GET'])
def notify_status():
    """Return which notification channels are configured (no secrets)."""
    tw_ok = bool(os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN') and os.getenv('TWILIO_FROM_NUMBER'))
    return jsonify({
        'twilio_configured': tw_ok,
        'twilio_from_number': os.getenv('TWILIO_FROM_NUMBER') if tw_ok else None,
        'target_phone_prefix': os.getenv('TARGET_PHONE_PREFIX')
    }), 200