from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder="web/templates", static_folder="web")

BASE_PATH = "/"  # Changed from /Quarks

def safe_join(base, *paths):
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise ValueError("Access denied")
    return final_path

@app.route("/")
def index():
    return render_template("select.html")

@app.route("/browse")
def browse():
    path = request.args.get("path", BASE_PATH)
    field = request.args.get("field", "source")

    try:
        path = safe_join(BASE_PATH, os.path.relpath(path, BASE_PATH))
    except Exception as e:
        return jsonify({"error": str(e)}), 403

    try:
        items = sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    parent = os.path.dirname(path) if path != BASE_PATH else None
    return render_template("browse.html", current=path, parent=parent, items=items, field=field)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=True)
