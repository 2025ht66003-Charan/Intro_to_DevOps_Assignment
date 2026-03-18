"""
Comprehensive Pytest test suite for the Fitness Management Flask application.
Tests cover all endpoints, business logic, and error handling.
"""
import pytest
import json
import sys
import os

# Add the app module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, FitnessProgram, Client


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def app_context():
    """Create an application context."""
    with app.app_context():
        yield app


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test that health check endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestFitnessProgram:
    """Test FitnessProgram class logic."""
    
    def test_get_valid_program(self):
        """Test retrieving a valid program."""
        program = FitnessProgram.get_program("Fat Loss (FL)")
        assert program is not None
        assert program['calorie_factor'] == 22
        assert 'workout' in program
        assert 'diet' in program
    
    def test_get_invalid_program(self):
        """Test retrieving an invalid program returns None."""
        program = FitnessProgram.get_program("Invalid Program")
        assert program is None
    
    def test_calculate_calories_fat_loss(self):
        """Test calorie calculation for Fat Loss program."""
        calories = FitnessProgram.calculate_calories(70, "Fat Loss (FL)")
        assert calories == 70 * 22
        assert calories == 1540
    
    def test_calculate_calories_muscle_gain(self):
        """Test calorie calculation for Muscle Gain program."""
        calories = FitnessProgram.calculate_calories(80, "Muscle Gain (MG)")
        assert calories == 80 * 35
        assert calories == 2800
    
    def test_calculate_calories_beginner(self):
        """Test calorie calculation for Beginner program."""
        calories = FitnessProgram.calculate_calories(60, "Beginner (BG)")
        assert calories == 60 * 26
        assert calories == 1560
    
    def test_calculate_calories_invalid_program(self):
        """Test calorie calculation with invalid program uses default."""
        calories = FitnessProgram.calculate_calories(70, "Invalid")
        assert calories == 70 * 25  # default factor


class TestClientClass:
    """Test Client class logic."""
    
    def test_client_creation(self):
        """Test client object creation."""
        client = Client("1", "John Doe", 30, 75.5, "Muscle Gain (MG)")
        assert client.client_id == "1"
        assert client.name == "John Doe"
        assert client.age == 30
        assert client.weight == 75.5
        assert client.program == "Muscle Gain (MG)"
        assert client.progress == 0
        assert client.notes == ""
    
    def test_client_to_dict(self):
        """Test converting client to dictionary."""
        client = Client("1", "Jane Doe", 25, 60, "Fat Loss (FL)")
        client_dict = client.to_dict()
        assert client_dict['client_id'] == "1"
        assert client_dict['name'] == "Jane Doe"
        assert client_dict['age'] == 25
        assert client_dict['weight'] == 60
        assert 'created_at' in client_dict


class TestClientEndpoints:
    """Test client management endpoints."""
    
    def test_create_client_success(self, client):
        """Test successful client creation."""
        payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        response = client.post('/api/clients',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == "John Doe"
        assert data['age'] == 30
        assert data['weight'] == 75.5
    
    def test_create_client_missing_fields(self, client):
        """Test client creation with missing fields."""
        payload = {"name": "John Doe", "age": 30}
        response = client.post('/api/clients',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_client_invalid_program(self, client):
        """Test client creation with invalid program."""
        payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Invalid Program"
        }
        response = client.post('/api/clients',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_all_clients(self, client):
        """Test retrieving all clients."""
        # Create multiple clients
        for i in range(2):
            payload = {
                "name": f"Client {i}",
                "age": 25 + i,
                "weight": 70 + i,
                "program": "Muscle Gain (MG)"
            }
            client.post('/api/clients',
                       data=json.dumps(payload),
                       content_type='application/json')
        
        # Get all clients
        response = client.get('/api/clients')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'clients' in data
        assert 'total' in data
        assert data['total'] >= 2
    
    def test_get_single_client(self, client):
        """Test retrieving a single client."""
        # Create a client
        payload = {
            "name": "Jane Doe",
            "age": 25,
            "weight": 60,
            "program": "Fat Loss (FL)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Get the client
        response = client.get(f'/api/clients/{client_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == "Jane Doe"
    
    def test_get_nonexistent_client(self, client):
        """Test retrieving a nonexistent client."""
        response = client.get('/api/clients/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_client(self, client):
        """Test updating a client."""
        # Create a client
        payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Update the client
        update_payload = {
            "weight": 80,
            "progress": 50,
            "notes": "Great progress!"
        }
        response = client.put(f'/api/clients/{client_id}',
                             data=json.dumps(update_payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['weight'] == 80
        assert data['progress'] == 50
        assert data['notes'] == "Great progress!"
    
    def test_update_client_program(self, client):
        """Test updating client program."""
        # Create a client
        payload = {
            "name": "Alice",
            "age": 28,
            "weight": 65,
            "program": "Fat Loss (FL)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Update program
        update_payload = {"program": "Muscle Gain (MG)"}
        response = client.put(f'/api/clients/{client_id}',
                             data=json.dumps(update_payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['program'] == "Muscle Gain (MG)"
    
    def test_update_client_age(self, client):
        """Test updating client age."""
        # Create a client
        payload = {
            "name": "Bob",
            "age": 30,
            "weight": 80,
            "program": "Beginner (BG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Update age
        update_payload = {"age": 32}
        response = client.put(f'/api/clients/{client_id}',
                             data=json.dumps(update_payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['age'] == 32
    
    def test_update_nonexistent_client(self, client):
        """Test updating a nonexistent client."""
        payload = {"weight": 80}
        response = client.put('/api/clients/999',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 404
    
    def test_delete_client(self, client):
        """Test deleting a client."""
        # Create a client
        payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Delete the client
        response = client.delete(f'/api/clients/{client_id}')
        assert response.status_code == 200
        
        # Verify client is deleted
        get_response = client.get(f'/api/clients/{client_id}')
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_client(self, client):
        """Test deleting a nonexistent client."""
        response = client.delete('/api/clients/999')
        assert response.status_code == 404


class TestProgramEndpoints:
    """Test fitness program endpoints."""
    
    def test_get_programs(self, client):
        """Test retrieving all available programs."""
        response = client.get('/api/programs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'programs' in data
        assert len(data['programs']) == 3
        assert "Fat Loss (FL)" in data['programs']
        assert "Muscle Gain (MG)" in data['programs']
        assert "Beginner (BG)" in data['programs']
    
    def test_get_specific_program(self, client):
        """Test retrieving a specific program."""
        response = client.get('/api/programs/Fat Loss (FL)')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'program' in data
        program = data['program']
        assert program['calorie_factor'] == 22
    
    def test_get_invalid_program(self, client):
        """Test retrieving an invalid program."""
        response = client.get('/api/programs/Invalid Program')
        assert response.status_code == 404


class TestCalculationEndpoints:
    """Test calculation endpoints."""
    
    def test_calculate_calories_success(self, client):
        """Test successful calorie calculation."""
        payload = {
            "weight": 70,
            "program": "Fat Loss (FL)"
        }
        response = client.post('/api/calculate-calories',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['weight'] == 70
        assert data['daily_calories'] == 1540
        assert data['program'] == "Fat Loss (FL)"
    
    def test_calculate_calories_missing_fields(self, client):
        """Test calorie calculation with missing fields."""
        payload = {"weight": 70}
        response = client.post('/api/calculate-calories',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_calculate_calories_missing_weight(self, client):
        """Test calorie calculation with missing weight."""
        payload = {"program": "Fat Loss (FL)"}
        response = client.post('/api/calculate-calories',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_calculate_calories_multiple_programs(self, client):
        """Test calorie calculation for all programs."""
        programs = ["Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"]
        expected_calories = {
            "Fat Loss (FL)": 1760,  # 80 * 22
            "Muscle Gain (MG)": 2800,  # 80 * 35
            "Beginner (BG)": 2080  # 80 * 26
        }
        
        for program in programs:
            payload = {"weight": 80, "program": program}
            response = client.post('/api/calculate-calories',
                                  data=json.dumps(payload),
                                  content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['program'] == program
            assert data['daily_calories'] == expected_calories[program]
    
    def test_calculate_calories_zero_weight(self, client):
        """Test calorie calculation with zero weight."""
        payload = {"weight": 0, "program": "Fat Loss (FL)"}
        response = client.post('/api/calculate-calories',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['daily_calories'] == 0
    
    def test_calculate_calories_decimal_weight(self, client):
        """Test calorie calculation with decimal weight."""
        payload = {"weight": 75.5, "program": "Muscle Gain (MG)"}
        response = client.post('/api/calculate-calories',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['weight'] == 75.5
        assert data['daily_calories'] == 75.5 * 35


class TestProgressTracking:
    """Test progress tracking endpoints."""
    
    def test_log_progress_success(self, client):
        """Test successful progress logging."""
        # Create a client first
        client_payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(client_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Log progress
        progress_payload = {
            "workout": "Bench Press",
            "duration": 60,
            "calories_burned": 350
        }
        response = client.post(f'/api/progress/{client_id}',
                              data=json.dumps(progress_payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['workout'] == "Bench Press"
        assert data['duration'] == 60
        assert data['calories_burned'] == 350
    
    def test_log_progress_missing_fields(self, client):
        """Test progress logging with missing fields."""
        # Create a client
        client_payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(client_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Try to log progress with missing fields
        progress_payload = {"workout": "Bench Press"}
        response = client.post(f'/api/progress/{client_id}',
                              data=json.dumps(progress_payload),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_log_progress_for_nonexistent_client(self, client):
        """Test logging progress for nonexistent client."""
        progress_payload = {
            "workout": "Cardio",
            "duration": 45,
            "calories_burned": 300
        }
        response = client.post('/api/progress/999',
                              data=json.dumps(progress_payload),
                              content_type='application/json')
        assert response.status_code == 404
    
    def test_get_progress_success(self, client):
        """Test retrieving progress records."""
        # Create a client
        client_payload = {
            "name": "Jane Doe",
            "age": 25,
            "weight": 60,
            "program": "Fat Loss (FL)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(client_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Log multiple progress entries
        for i in range(3):
            progress_payload = {
                "workout": f"Workout {i}",
                "duration": 30 + i * 5,
                "calories_burned": 250 + i * 25
            }
            client.post(f'/api/progress/{client_id}',
                       data=json.dumps(progress_payload),
                       content_type='application/json')
        
        # Get progress
        response = client.get(f'/api/progress/{client_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['client_id'] == client_id
        assert 'progress_records' in data
        assert data['total_records'] == 3
    
    def test_get_progress_nonexistent_client(self, client):
        """Test retrieving progress for nonexistent client."""
        response = client.get('/api/progress/999')
        assert response.status_code == 404
    
    def test_get_progress_empty_records(self, client):
        """Test retrieving progress with no records."""
        # Create a client
        client_payload = {
            "name": "TestClient",
            "age": 28,
            "weight": 70,
            "program": "Beginner (BG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(client_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Get progress (should be empty)
        response = client.get(f'/api/progress/{client_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_records'] == 0
        assert data['progress_records'] == []


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_bad_json(self, client):
        """Test handling of bad JSON."""
        response = client.post('/api/clients',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400


class TestUpdateClientEdgeCases:
    """Test edge cases for client updates."""
    
    def test_update_client_all_fields(self, client):
        """Test updating all client fields."""
        # Create a client
        create_payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(create_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Update all fields
        update_payload = {
            "name": "Jane Doe",
            "age": 28,
            "weight": 65,
            "program": "Fat Loss (FL)",
            "progress": 75,
            "notes": "Excellent adherence"
        }
        response = client.put(f'/api/clients/{client_id}',
                             data=json.dumps(update_payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == "Jane Doe"
        assert data['age'] == 28
        assert data['weight'] == 65
        assert data['program'] == "Fat Loss (FL)"
        assert data['progress'] == 75
        assert data['notes'] == "Excellent adherence"
    
    def test_update_client_invalid_program_in_update(self, client):
        """Test updating client with invalid program."""
        # Create a client
        create_payload = {
            "name": "John Doe",
            "age": 30,
            "weight": 75.5,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(create_payload),
                                     content_type='application/json')
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Try to update with invalid program
        update_payload = {"program": "Invalid Program"}
        response = client.put(f'/api/clients/{client_id}',
                             data=json.dumps(update_payload),
                             content_type='application/json')
        assert response.status_code == 400


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_complete_client_workflow(self, client):
        """Test complete workflow: create, update, get, delete."""
        # Create
        create_payload = {
            "name": "Integration Test Client",
            "age": 28,
            "weight": 72,
            "program": "Muscle Gain (MG)"
        }
        create_response = client.post('/api/clients',
                                     data=json.dumps(create_payload),
                                     content_type='application/json')
        assert create_response.status_code == 201
        client_data = json.loads(create_response.data)
        client_id = client_data['client_id']
        
        # Update
        update_payload = {"weight": 74, "progress": 25}
        update_response = client.put(f'/api/clients/{client_id}',
                                    data=json.dumps(update_payload),
                                    content_type='application/json')
        assert update_response.status_code == 200
        
        # Get
        get_response = client.get(f'/api/clients/{client_id}')
        assert get_response.status_code == 200
        updated_data = json.loads(get_response.data)
        assert updated_data['weight'] == 74
        
        # Delete
        delete_response = client.delete(f'/api/clients/{client_id}')
        assert delete_response.status_code == 200
        
        # Verify deleted
        final_response = client.get(f'/api/clients/{client_id}')
        assert final_response.status_code == 404
    
    def test_multiple_clients_management(self, client):
        """Test managing multiple clients."""
        clients_to_create = [
            {"name": "Client 1", "age": 25, "weight": 70, "program": "Fat Loss (FL)"},
            {"name": "Client 2", "age": 30, "weight": 80, "program": "Muscle Gain (MG)"},
            {"name": "Client 3", "age": 20, "weight": 65, "program": "Beginner (BG)"}
        ]
        
        created_ids = []
        for payload in clients_to_create:
            response = client.post('/api/clients',
                                  data=json.dumps(payload),
                                  content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            created_ids.append(data['client_id'])
        
        # Get all clients
        all_response = client.get('/api/clients')
        assert all_response.status_code == 200
        all_data = json.loads(all_response.data)
        assert all_data['total'] >= 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
