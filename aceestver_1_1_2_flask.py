from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

PROGRAMS = {
    "Fat Loss (FL)": {"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery", "diet": "Egg Whites, Chicken, Fish Curry", "color": "#e74c3c", "calorie_factor": 22},
    "Muscle Gain (MG)": {"workout": "Squat, Bench, Deadlift, Press, Rows", "diet": "Eggs, Biryani, Mutton Curry", "color": "#2ecc71", "calorie_factor": 35},
    "Beginner (BG)": {"workout": "Air Squats, Ring Rows, Push-ups", "diet": "Balanced Tamil Meals", "color": "#3498db", "calorie_factor": 26}
}

clients = []

@app.route("/")
def index():
    return jsonify({"version": "1.1.2", "description": "In-memory client manager with program data"})

@app.route("/programs", methods=["GET"])
def list_programs():
    return jsonify({"programs": PROGRAMS}), 200

@app.route("/programs/<program_name>", methods=["GET"])
def get_program(program_name):
    program = PROGRAMS.get(program_name)
    if not program:
        abort(404, description="Program not found")
    return jsonify({"program_name": program_name, "program": program}), 200

@app.route("/calculate", methods=["POST"])
def calculate():
    payload = request.get_json() or {}
    program_name = payload.get("program")
    weight = payload.get("weight")
    if not program_name or weight is None:
        abort(400, description="program and weight are required")
    program = PROGRAMS.get(program_name)
    if not program:
        abort(404, description="Program not found")
    calories = int(weight * program["calorie_factor"])
    return jsonify({"program": program_name, "weight": weight, "calories": calories}), 200

@app.route("/clients", methods=["GET", "POST"])
def manage_clients():
    if request.method == "POST":
        payload = request.get_json() or {}
        if not payload.get("name") or not payload.get("program"):
            abort(400, description="name and program are required")
        clients.append(payload)
        return jsonify({"saved": payload}), 201
    return jsonify({"clients": clients}), 200

@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    for client in clients:
        if client.get("name") == name:
            return jsonify({"client": client}), 200
    abort(404, description="Client not found")

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
