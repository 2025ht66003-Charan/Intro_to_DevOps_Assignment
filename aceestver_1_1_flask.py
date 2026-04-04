from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "color": "#e74c3c",
        "calorie_factor": 22
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "color": "#2ecc71",
        "calorie_factor": 35
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "color": "#3498db",
        "calorie_factor": 26
    }
}

SITE_METRICS = "CAPACITY: 150 Users\nAREA: 10,000 sq ft\nBREAK-EVEN: 250 Members"

@app.route("/")
def index():
    return jsonify({
        "version": "1.1",
        "description": "Flask app version 1.1 with calorie calculator",
        "programs": list(PROGRAMS.keys()),
        "site_metrics": SITE_METRICS
    })

@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify({"programs": PROGRAMS, "site_metrics": SITE_METRICS}), 200

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
    if not program or "calorie_factor" not in program:
        abort(400, description="Invalid program or calorie factor unavailable")
    calories = int(weight * program["calorie_factor"])
    return jsonify({"program": program_name, "weight": weight, "calories": calories}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
