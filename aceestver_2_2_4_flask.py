from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import sqlite3
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
DB_PATH = "aceest_2_2_4.db"

PROGRAMS = {
    "Fat Loss (FL) – 3 day": {"factor": 22, "desc": "3-day full-body fat loss"},
    "Fat Loss (FL) – 5 day": {"factor": 24, "desc": "5-day split, higher volume fat loss"},
    "Muscle Gain (MG) – PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy"},
    "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"}
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, workout_id INTEGER, name TEXT, sets INTEGER, reps INTEGER, weight REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return jsonify({"version": "2.2.4", "description": "Advanced client, workout, and metrics API"})

@app.route("/programs")
def programs():
    return jsonify({"programs": PROGRAMS}), 200

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
        calories = int(weight * PROGRAMS[program]["factor"]) if weight is not None else None
        cur.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, age, height, weight, program, calories, payload.get("target_weight"), payload.get("target_adherence")))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT name, age, height, weight, program, calories, target_weight, target_adherence FROM clients")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"clients": [dict(zip(["name", "age", "height", "weight", "program", "calories", "target_weight", "target_adherence"], row)) for row in rows]}), 200

@app.route("/progress", methods=["GET", "POST"])
def progress():
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

@app.route("/workouts", methods=["GET", "POST"])
def workouts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if request.method == "POST":
        payload = request.get_json() or {}
        required = ["client_name", "date", "workout_type"]
        if not all(payload.get(k) for k in required):
            conn.close()
            abort(400, description="client_name, date, and workout_type required")
        cur.execute("INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)", (payload.get("client_name"), payload.get("date"), payload.get("workout_type"), payload.get("duration_min"), payload.get("notes")))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT client_name, date, workout_type, duration_min, notes FROM workouts")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"workouts": [dict(zip(["client_name", "date", "workout_type", "duration_min", "notes"], row)) for row in rows]}), 200

@app.route("/metrics", methods=["GET", "POST"])
def metrics():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if request.method == "POST":
        payload = request.get_json() or {}
        if not payload.get("client_name") or not payload.get("date"):
            conn.close()
            abort(400, description="client_name and date required")
        cur.execute("INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)", (payload.get("client_name"), payload.get("date"), payload.get("weight"), payload.get("waist"), payload.get("bodyfat")))
        conn.commit()
        conn.close()
        return jsonify({"saved": payload}), 201
    cur.execute("SELECT client_name, date, weight, waist, bodyfat FROM metrics")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"metrics": [dict(zip(["client_name", "date", "weight", "waist", "bodyfat"], row)) for row in rows]}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5006)
