from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Store for Program Specification (from Tkinter app)
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
        "color": "#3498db"
    }
}

# Site Metrics (from Tkinter app)
SITE_METRICS = "CAPACITY: 150 Users\nAREA: 10,000 sq ft\nBREAK-EVEN: 250 Members"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with program selection form."""
    selected_program = None
    if request.method == 'POST':
        program_name = request.form.get('program')
        if program_name in PROGRAMS:
            selected_program = PROGRAMS[program_name]
            selected_program['name'] = program_name
    return render_template('index.html', programs=PROGRAMS, selected_program=selected_program, site_metrics=SITE_METRICS)

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """API endpoint to get all programs."""
    return jsonify({"programs": PROGRAMS, "site_metrics": SITE_METRICS}), 200

@app.route('/api/programs/<program_name>', methods=['GET'])
def get_program(program_name):
    """API endpoint to get specific program details."""
    if program_name not in PROGRAMS:
        return jsonify({"error": "Program not found"}), 404
    return jsonify({"program": PROGRAMS[program_name], "name": program_name}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)