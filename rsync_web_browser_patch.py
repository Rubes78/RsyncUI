
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import logging

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_FILE = os.path.join(BASE_DIR, 'saved_paths.json')
HISTORY_FILE = os.path.join(BASE_DIR, 'sync_history.json')

@app.route("/")
def index():
    return render_template("select.html")

@app.route("/load-paths", methods=["GET"])
def load_paths():
    if not os.path.exists(SAVE_PATH_FILE):
        return jsonify({})
    try:
        with open(SAVE_PATH_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sync-history", methods=["GET"])
def sync_history():
    if not os.path.exists(HISTORY_FILE):
        return jsonify([])
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
