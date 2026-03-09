from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from werkzeug.exceptions import BadRequest
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (can be replaced with database)
clients = {}
workouts = {}
progress_records = {}


class FitnessProgram:
    """Represents a fitness program."""
    
    PROGRAMS = {
        "Fat Loss (FL)": {
            "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
            "diet": "Egg Whites, Chicken, Fish Curry",
            "color": "#e74c3c",
            "calorie_factor": 22
        },
        "Muscle Gain (MG)": {
            "workout": "Squat, Bench, Deadlift, Press, Rows",
            "diet": "Eggs, Biryani, Mutton Curry",
            "color": "#2ecc71",
            "calorie_factor": 35
        },
        "Beginner (BG)": {
            "workout": "Air Squats, Ring Rows, Push-ups",
            "diet": "Balanced Meals",
            "color": "#3498db",
            "calorie_factor": 26
        }
    }
    
    @staticmethod
    def get_program(program_name):
        """Get program details by name."""
        return FitnessProgram.PROGRAMS.get(program_name)
    
    @staticmethod
    def calculate_calories(weight, program_name):
        """Calculate daily calorie requirement based on weight and program."""
        program = FitnessProgram.get_program(program_name)
        if program:
            return weight * program["calorie_factor"]
        return weight * 25  # default factor


class Client:
    """Represents a fitness client."""
    
    def __init__(self, client_id, name, age, weight, program):
        self.client_id = client_id
        self.name = name
        self.age = age
        self.weight = weight
        self.program = program
        self.created_at = datetime.now().isoformat()
        self.progress = 0
        self.notes = ""
    
    def to_dict(self):
        """Convert client object to dictionary."""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "age": self.age,
            "weight": self.weight,
            "program": self.program,
            "created_at": self.created_at,
            "progress": self.progress,
            "notes": self.notes
        }


# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


# ===== CLIENT ENDPOINTS =====

@app.route('/api/clients', methods=['POST'])
def create_client():
    """Create a new client."""
    try:
        try:
            data = request.get_json()
        except BadRequest:
            return jsonify({"error": "Invalid JSON"}), 400
        
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate required fields
        if not all(k in data for k in ['name', 'age', 'weight', 'program']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate program
        if data['program'] not in FitnessProgram.PROGRAMS:
            return jsonify({"error": "Invalid program"}), 400
        
        # Create client
        client_id = str(len(clients) + 1)
        client = Client(
            client_id=client_id,
            name=data['name'],
            age=int(data['age']),
            weight=float(data['weight']),
            program=data['program']
        )
        
        clients[client_id] = client
        logger.info(f"Client created: {client_id}")
        
        return jsonify(client.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/clients', methods=['GET'])
def get_all_clients():
    """Get all clients."""
    try:
        client_list = [client.to_dict() for client in clients.values()]
        return jsonify({"clients": client_list, "total": len(client_list)}), 200
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client."""
    try:
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        return jsonify(clients[client_id].to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching client: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/clients/<client_id>', methods=['PUT'])
def update_client(client_id):
    """Update a client."""
    try:
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        data = request.get_json()
        client = clients[client_id]
        
        # Update fields
        if 'name' in data:
            client.name = data['name']
        if 'age' in data:
            client.age = int(data['age'])
        if 'weight' in data:
            client.weight = float(data['weight'])
        if 'program' in data:
            if data['program'] not in FitnessProgram.PROGRAMS:
                return jsonify({"error": "Invalid program"}), 400
            client.program = data['program']
        if 'progress' in data:
            client.progress = int(data['progress'])
        if 'notes' in data:
            client.notes = data['notes']
        
        logger.info(f"Client updated: {client_id}")
        return jsonify(client.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error updating client: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client."""
    try:
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        del clients[client_id]
        logger.info(f"Client deleted: {client_id}")
        return jsonify({"message": "Client deleted successfully"}), 200
    
    except Exception as e:
        logger.error(f"Error deleting client: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== PROGRAM ENDPOINTS =====

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """Get all available fitness programs."""
    try:
        return jsonify({"programs": FitnessProgram.PROGRAMS}), 200
    except Exception as e:
        logger.error(f"Error fetching programs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/programs/<program_name>', methods=['GET'])
def get_program(program_name):
    """Get specific program details."""
    try:
        program = FitnessProgram.get_program(program_name)
        if not program:
            return jsonify({"error": "Program not found"}), 404
        return jsonify({"program": program}), 200
    except Exception as e:
        logger.error(f"Error fetching program: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== CALCULATION ENDPOINTS =====

@app.route('/api/calculate-calories', methods=['POST'])
def calculate_calories():
    """Calculate daily calories for a client."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['weight', 'program']):
            return jsonify({"error": "Missing required fields"}), 400
        
        weight = float(data['weight'])
        program = data['program']
        
        calories = FitnessProgram.calculate_calories(weight, program)
        
        return jsonify({
            "weight": weight,
            "program": program,
            "daily_calories": round(calories, 2)
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating calories: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== PROGRESS TRACKING =====

@app.route('/api/progress/<client_id>', methods=['POST'])
def log_progress(client_id):
    """Log progress for a client."""
    try:
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        data = request.get_json()
        
        if not all(k in data for k in ['workout', 'duration', 'calories_burned']):
            return jsonify({"error": "Missing required fields"}), 400
        
        if client_id not in progress_records:
            progress_records[client_id] = []
        
        record = {
            "date": datetime.now().isoformat(),
            "workout": data['workout'],
            "duration": int(data['duration']),
            "calories_burned": float(data['calories_burned'])
        }
        
        progress_records[client_id].append(record)
        logger.info(f"Progress logged for client: {client_id}")
        
        return jsonify(record), 201
    
    except Exception as e:
        logger.error(f"Error logging progress: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/progress/<client_id>', methods=['GET'])
def get_progress(client_id):
    """Get progress records for a client."""
    try:
        if client_id not in clients:
            return jsonify({"error": "Client not found"}), 404
        
        records = progress_records.get(client_id, [])
        return jsonify({
            "client_id": client_id,
            "progress_records": records,
            "total_records": len(records)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching progress: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== ERROR HANDLERS =====

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({"error": "Bad request"}), 400


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
