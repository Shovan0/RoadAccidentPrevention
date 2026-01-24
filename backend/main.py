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

UPLOAD_DIR = "uploads"
HISTORY_DIR = "history"
ALLOWED_EXT = {"mp4", "mov", "avi", "mkv", "webm"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)

HISTORY_FILE = os.path.join(HISTORY_DIR, "processing_history.json")
USERS = {
    "admin": {"password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()), "role": "admin"},
    "user": {"password": bcrypt.hashpw("user123".encode(), bcrypt.gensalt()), "role": "user"}
}
STREAM_STATS = {}

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
    u = USERS.get(data.get("username"))
    if u and bcrypt.checkpw(data.get("password").encode(), u["password"]):
        return jsonify(access_token=create_access_token(identity=data["username"], additional_claims={"role": u["role"]}))
    return jsonify({"error": "Invalid"}), 401

@app.route("/api/verify-token", methods=["GET"])
@jwt_required()
def verify(): return jsonify({"username": get_jwt_identity(), "role": USERS.get(get_jwt_identity())["role"]}), 200

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
    dist = float(request.args.get('dist', 20))
    save = request.args.get('save', 'false') == 'true'
    user = request.args.get('user', 'anonymous')
    
    # --- VIRTUAL SIMULATION ---
    if fname == "virtual_simulation":
        def on_live_virtual(s): STREAM_STATS["virtual_simulation"] = s
        return Response(
            generate_virtual_simulation(overspeed_limit_kmh=limit, distance_meters=dist, record_config={"live_callback": on_live_virtual}),
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
                "download_name": out_name, "overspeed_limit": limit, "distance_meters": dist,
                "total_vehicles": len(d["all_logs"]), "total_violations": len(d["overspeed_summary"]),
                "overspeed_summary": d["overspeed_summary"], "all_logs": d["all_logs"]
            }
            h = load_history()
            h.append(rec)
            save_history(h)
            if name in STREAM_STATS: del STREAM_STATS[name]
        cfg.update({"output_path": out_path, "data_callback": on_done})
        
    return Response(generate_frames(path, limit, dist, cfg), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/download/<fname>", methods=["GET"])
def dl(fname):
    path = os.path.join(UPLOAD_DIR, secure_filename(fname))
    return send_file(path, as_attachment=True) if os.path.exists(path) else abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)