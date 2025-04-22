from flask import Response, request, jsonify
import subprocess
import json
import os
from datetime import datetime
from log import log

def init_rsync_routes(app):
    @app.route("/run-rsync", methods=["POST"])
    def run_rsync():
        data = request.get_json()
        source = data.get("source")
        destination = data.get("destination")
        options = data.get("options", "-avh --progress")
        log_output = data.get("log_output", True)

        if not source or not destination:
            return Response("Missing source or destination", status=400)

        cmd = ["rsync"] + options.split() + [source, destination]
        log(f"Executing rsync command: {' '.join(cmd)}", "info")

        history_path = os.path.join(os.getcwd(), "sync_history.json")
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "destination": destination,
            "options": options
        }

        def generate():
            try:
                # Save run to history
                if os.path.exists(history_path):
                    with open(history_path, "r") as f:
                        history = json.load(f)
                else:
                    history = []

                history.insert(0, history_entry)  # newest first
                with open(history_path, "w") as f:
                    json.dump(history, f, indent=2)

                # Run rsync
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in iter(process.stdout.readline, ''):
                    if log_output:
                        log(line.strip(), "debug")
                    yield f"data: {line.strip()}\n\n"
                process.stdout.close()
                process.wait()
                yield f"data: Rsync process finished with exit code {process.returncode}\n\n"
                log(f"Rsync process completed with code {process.returncode}", "info")
            except Exception as e:
                log(f"Error running rsync: {e}", "error")
                yield f"data: Error running rsync: {e}\n\n"

        return Response(generate(), mimetype="text/event-stream")
    @app.route("/sync-history", methods=["GET"])
    def sync_history():
        history_path = os.path.join(os.getcwd(), "sync_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    history = json.load(f)
                return jsonify(history)
            except Exception as e:
                log(f"Failed to read sync_history.json: {e}", "error")
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify([])

