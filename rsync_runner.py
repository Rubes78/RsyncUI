from flask import Response, request
import subprocess
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

        def generate():
            try:
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
