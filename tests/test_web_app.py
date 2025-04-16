"""
Unit tests for KasongoType web application
"""

import sys
import os
import unittest
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app as flask_app
from common.typing_engine import ExerciseManager

class TestWebApp(unittest.TestCase):
    """Tests for the Flask web application"""

    def setUp(self):
        """Set up test environment before each test"""
        # Configure Flask app for testing
        flask_app.config['TESTING'] = True
        flask_app.config['WTF_CSRF_ENABLED'] = False
        
        # Create a test client
        self.client = flask_app.test_client()
        
        # Create temporary files for testing
        self.exercises_fd, self.exercises_path = tempfile.mkstemp(suffix='.json')
        self.profiles_fd, self.profiles_path = tempfile.mkstemp(suffix='.json')
        
        # Create test exercises
        test_exercises = {
            "levels": {
                "test_level": [
                    {
                        "id": "test1",
                        "title": "Test Exercise",
                        "text": "This is a test exercise."
                    }
                ]
            }
        }
        
        with os.fdopen(self.exercises_fd, 'w') as f:
            json.dump(test_exercises, f)
        
        # Create empty profiles file
        with os.fdopen(self.profiles_fd, 'w') as f:
            json.dump({}, f)
        
        # Override the exercise_manager in the Flask app
        flask_app.config['EXERCISES_PATH'] = self.exercises_path
        
        # Create a session object for testing
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove temporary files
        os.unlink(self.exercises_path)
        os.unlink(self.profiles_path)
    
    def test_index_route(self):
        """Test the main index route"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_dashboard_route(self):
        """Test the dashboard route"""
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_exercises_route(self):
        """Test the exercises route"""
        response = self.client.get('/exercises')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Exercises', response.data)
    
    def test_api_exercises(self):
        """Test the exercises API endpoint"""
        # Test with no level parameter (all exercises)
        response = self.client.get('/api/exercises')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('exercises', data)
        
        # Test with specific level
        response = self.client.get('/api/exercises?level=test_level')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['exercises']), 1)
        self.assertEqual(data['exercises'][0]['id'], 'test1')
    
    def test_api_exercise_by_id(self):
        """Test retrieving a specific exercise"""
        response = self.client.get('/api/exercise/test_level/test1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['exercise']['id'], 'test1')
        self.assertEqual(data['exercise']['title'], 'Test Exercise')
    
    def test_start_session(self):
        """Test starting a typing session"""
        payload = {
            'exercise_id': 'test1',
            'level': 'test_level'
        }
        
        response = self.client.post(
            '/api/session/start',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('session_id', data)
        self.assertIn('exercise', data)
    
    def test_process_keystroke(self):
        """Test processing keystrokes in a session"""
        # First start a session
        payload = {
            'exercise_id': 'test1',
            'level': 'test_level'
        }
        
        start_response = self.client.post(
            '/api/session/start',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        start_data = json.loads(start_response.data)
        session_id = start_data['session_id']
        
        # Now process a keystroke
        keystroke_payload = {
            'key': 'T',
            'exercise_id': 'test1'
        }
        
        response = self.client.post(
            f'/api/session/{session_id}/keystroke',
            data=json.dumps(keystroke_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
        self.assertIn('metrics', data)

if __name__ == "__main__":
    unittest.main()