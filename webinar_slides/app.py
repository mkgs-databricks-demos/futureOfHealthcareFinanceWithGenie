from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

# Serve files from the same directory as this script.
# When deployed, the snapshot includes all slide HTML files alongside app.py.
SLIDES_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(SLIDES_DIR, "presenter.html")

@app.route("/<path:filename>")
def serve_file(filename):
    safe_path = os.path.join(SLIDES_DIR, filename)
    if not os.path.isfile(safe_path):
        abort(404)
    return send_from_directory(SLIDES_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)