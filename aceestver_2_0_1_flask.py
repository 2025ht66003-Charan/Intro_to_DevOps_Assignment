from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import sqlite3
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
DB_PATH = "aceest_2_0_1.db"

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, weight REAL, program TEXT, calories INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)")
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return jsonify({"version": "2.0.1", "description": "Client persistence and weekly progress tracking"})

@app.route("/programs", methods=["GET"])
def list_programs():
    return jsonify({"programs": PROGRAMS}), 200

@app.route("/calculate", methods=["POST"])
def calculate():
    payload = request.get_json() or {}
    program_name = payload.get("program")
    weight = payload.get("weight")
    if not program_name or weight is None:
        abort(400, description="program and weight required")
    program = PROGRAMS.get(program_name)
    if not program:
        abort(404, description="Program not found")
    return jsonify({"calories": int(weight * program["factor"])}), 200

@app.route("/clients", methods=["GET", "POST"])
def manage_clients():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if request.method == "POST":
        payload = request.get_json() or {}
        name = payload.get("name")
        program = payload.get("program")
        weight = payload.get("weight")
        age = payload.get("age")
        if not name or not program:
            conn.close()
            abort(400, description="name and program required")
        factor = PROGRAMS.get(program, {}).get("factor")
        calories = int(weight * factor) if factor and weight is not None else None
        cur.execute("INSERT OR REPLACE INTO clients (name, age, weight, program, calories) VALUES (?, ?, ?, ?, ?)", (name, age, weight, program, calories))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT name, age, weight, program, calories FROM clients")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"clients": [dict(zip(["name", "age", "weight", "program", "calories"], row)) for row in rows]}), 200

@app.route("/progress", methods=["GET", "POST"])
def manage_progress():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if request.method == "POST":
        payload = request.get_json() or {}
        client_name = payload.get("client_name")
        adherence = payload.get("adherence")
        if not client_name or adherence is None:
            conn.close()
            abort(400, description="client_name and adherence required")
        week = datetime.now().strftime("Week %U - %Y")
        cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)", (client_name, week, int(adherence)))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT client_name, week, adherence FROM progress")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"progress": [dict(zip(["client_name", "week", "adherence"], row)) for row in rows]}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5003)
