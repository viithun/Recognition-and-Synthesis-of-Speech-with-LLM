from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

from project import chat 

BASE_DIR = Path(__file__).parent
app = Flask(__name__, static_folder="static", template_folder="templates")

# ─── Front page ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ─── API ───────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400
    try:
        reply = chat(user_msg)
        return jsonify({"reply": reply})
    except Exception as err:
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)