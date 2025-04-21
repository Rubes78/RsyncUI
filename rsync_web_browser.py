from flask import Flask, render_template, request, jsonify
import os
import json
from log import log
from rsync_runner import init_rsync_routes

app = Flask(__name__, template_folder="web/templates", static_folder="web")
init_rsync_routes(app)

BASE_PATH = "/"
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_paths.json")

def safe_join(base, *paths):
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise ValueError("Access denied")
    return final_path

@app.route("/")
def index():
    log("Serving folder selection UI")
    return render_template("select.html")

@app.route("/browse")
def browse():
    path = request.args.get("path", BASE_PATH)
    field = request.args.get("field", "source")

    try:
        path = safe_join(BASE_PATH, os.path.relpath(path, BASE_PATH))
        log(f"Browsing path: {path} (field={field})", "debug")
    except Exception as e:
        log(f"Access denied while joining path: {path} | {str(e)}", "error")
        return jsonify({"error": str(e)}), 403

    try:
        items = sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
        log(f"Found {len(items)} subdirectories in: {path}", "debug")
    except Exception as e:
        log(f"Error reading directory '{path}': {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

    parent = os.path.dirname(path) if path != BASE_PATH else None
    return render_template("browse.html", current=path, parent=parent, items=items, field=field)

@app.route("/save-paths", methods=["POST"])
def save_paths():
    try:
        data = request.get_json(force=True)
        log(f"Received data for saving: {data}", "debug")
    except Exception as e:
        log(f"Failed to parse JSON: {str(e)}", "error")
        return jsonify({"error": "Invalid JSON format"}), 400

    if not data or "source" not in data or "destination" not in data:
        log(f"Incomplete path data: {data}", "warning")
        return jsonify({"error": "Missing source or destination"}), 400

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log(f"Paths saved successfully to {SAVE_FILE}: {data}", "info")
        return jsonify({"message": "Paths saved successfully"}), 200
    except Exception as e:
        log(f"Error writing to file {SAVE_FILE}: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

@app.route("/load-paths", methods=["GET"])
def load_paths():
    if not os.path.exists(SAVE_FILE):
        log("No saved paths found", "warning")
        return jsonify({"error": "No saved paths"}), 404

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        log(f"Loaded saved paths: {data}", "debug")
        return jsonify(data)
    except Exception as e:
        log(f"Failed to load saved paths: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    log("Launching Rsync Web GUI...", "info")
    app.run(host="0.0.0.0", port=5055, debug=True)
