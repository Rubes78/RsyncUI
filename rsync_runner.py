
import os
import json
from flask import request, Response, jsonify

def init_rsync_routes(app):
    @app.route("/sync-history", methods=["GET"])
    def sync_history():
        try:
            with open("sync_history.json", "r") as file:
                history = json.load(file)
            return jsonify(history)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
