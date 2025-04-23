
from flask import Response, request, jsonify
import subprocess
import json
import os
from datetime import datetime
from log import log

def init_rsync_routes(app):
    def get_project_file(filename):
        return os.path.join(os.getcwd(), filename)

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

        history_path = get_project_file("sync_history.json")
        saved_paths_path = get_project_file("saved_paths.json")
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "destination": destination,
            "options": options
        }

        try:
            with open(saved_paths_path, "w") as f:
                json.dump({"source": source, "destination": destination}, f, indent=2)
            log("Saved paths updated", "debug")
        except Exception as e:
            log(f"Failed to save paths: {e}", "error")

        def generate():
            try:
                if os.path.exists(history_path):
                    with open(history_path, "r") as f:
                        history = json.load(f)
                else:
                    history = []

                history.insert(0, history_entry)
                with open(history_path, "w") as f:
                    json.dump(history, f, indent=2)

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

    def sync_history():
        history_path = get_project_file("sync_history.json")
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

    def load_saved_paths():
        saved_paths_path = get_project_file("saved_paths.json")
        if os.path.exists(saved_paths_path):
            try:
                with open(saved_paths_path, "r") as f:
                    return jsonify(json.load(f))
            except Exception as e:
                log(f"Failed to read saved_paths.json: {e}", "error")
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({})

    # Use unique endpoint names
    app.add_url_rule("/run-rsync", view_func=run_rsync, methods=["POST"], endpoint="run_rsync_route")
    app.add_url_rule("/sync-history", view_func=sync_history, methods=["GET"], endpoint="sync_history_route")
    app.add_url_rule("/load-paths", view_func=load_saved_paths, methods=["GET"], endpoint="load_saved_paths_route")
