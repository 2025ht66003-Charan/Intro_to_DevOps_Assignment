from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import sqlite3
import logging
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
DB_PATH = "aceest_3_2_4.db"

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'Admin')")
    cur.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER, membership_status TEXT, membership_end TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, workout_id INTEGER, name TEXT, sets INTEGER, reps INTEGER, weight REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return jsonify({"version": "3.2.4", "description": "Role-based login with program generation and membership endpoints"})

@app.route("/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        abort(400, description="username and password required")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    if not row:
        abort(401, description="Invalid credentials")
    return jsonify({"username": username, "role": row[0]}), 200

@app.route("/generate-program", methods=["POST"])
def generate_program():
    payload = request.get_json() or {}
    category = payload.get("category")
    if not category or category not in PROGRAM_TEMPLATES:
        abort(400, description="category must be one of Fat Loss, Muscle Gain, Beginner")
    program = random.choice(PROGRAM_TEMPLATES[category])
    return jsonify({"category": category, "program": program}), 200

@app.route("/membership/<name>", methods=["GET"])
def membership(name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT membership_status, membership_end FROM clients WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        abort(404, description="Client not found")
    return jsonify({"name": name, "membership_status": row[0], "membership_end": row[1]}), 200

@app.route("/clients", methods=["GET", "POST"])
def clients():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if request.method == "POST":
        payload = request.get_json() or {}
        name = payload.get("name")
        program = payload.get("program")
        if not name or not program:
            conn.close()
            abort(400, description="name and program required")
        age = payload.get("age")
        height = payload.get("height")
        weight = payload.get("weight")
        calories = payload.get("calories")
        cur.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, age, height, weight, program, calories, payload.get("target_weight"), payload.get("target_adherence"), payload.get("membership_status", "Active"), payload.get("membership_end")))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end FROM clients")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"clients": [dict(zip(["name", "age", "height", "weight", "program", "calories", "target_weight", "target_adherence", "membership_status", "membership_end"], row)) for row in rows]}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": str(error)}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5009)
