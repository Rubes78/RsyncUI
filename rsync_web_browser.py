
from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path
from app.rsync_runner import init_rsync_routes

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = Path(__file__).resolve().parent
PATHS_FILE = BASE_DIR / "saved_paths.json"

@app.route("/")
def index():
    return render_template("select.html")

@app.route("/browse.html")
def browse():
    return render_template("browse.html")

@app.route("/browse-folder")
def browse_folder():
    base_path = request.args.get("path", "/")
    try:
        dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        return jsonify(folders=sorted(dirs))
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/load-paths")
def load_paths():
    if PATHS_FILE.exists():
        with open(PATHS_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"source": "", "destination": ""})

@app.route("/save-paths", methods=["POST"])
def save_paths():
    data = request.get_json()
    with open(PATHS_FILE, "w") as f:
        json.dump(data, f)
    return jsonify({"message": "Paths saved"})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--silent", action="store_true", help="Suppress Flask startup logs")
    args = parser.parse_args()

    if args.silent:
        import logging
        cli = logging.getLogger("werkzeug")
        cli.setLevel(logging.ERROR)

    init_rsync_routes(app)

    app.run(host="0.0.0.0", port=5055)
