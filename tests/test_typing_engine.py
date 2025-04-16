"""
Unit tests for KasongoType typing engine
"""

import sys
import os
import unittest
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.typing_engine import TypingSession, ExerciseManager, TypingMetrics

class TestTypingEngine(unittest.TestCase):
    """Tests for the typing engine components"""

    def setUp(self):
        """Set up test environment before each test"""
        self.test_text = "The quick brown fox jumps over the lazy dog."
        self.session = TypingSession(self.test_text, "test_user")
        
        # Create a test exercise manager with a temporary file
        self.test_exercises_path = Path("test_exercises.json")
        self.exercise_manager = ExerciseManager(str(self.test_exercises_path))
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove test exercises file if it exists
        if self.test_exercises_path.exists():
            self.test_exercises_path.unlink()
    
    def test_typing_session_initialization(self):
        """Test that TypingSession initializes correctly"""
        self.assertEqual(self.session.text, self.test_text)
        self.assertEqual(self.session.user_id, "test_user")
        self.assertIsNone(self.session.start_time)
        self.assertEqual(self.session.current_position, 0)
        self.assertEqual(self.session.errors, 0)
    
    def test_typing_session_start(self):
        """Test that session timer starts correctly"""
        self.assertIsNone(self.session.start_time)
        self.session.start()
        self.assertIsNotNone(self.session.start_time)
    
    def test_correct_keystroke(self):
        """Test processing a correct keystroke"""
        # First keystroke should be 'T'
        result = self.session.process_keystroke("T")
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["complete"])
        self.assertFalse(result["error"])
        self.assertEqual(self.session.current_position, 1)
        self.assertEqual(self.session.errors, 0)
    
    def test_incorrect_keystroke(self):
        """Test processing an incorrect keystroke"""
        # 'X' is incorrect for the first character
        result = self.session.process_keystroke("X")
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["complete"])
        self.assertTrue(result["error"])
        self.assertEqual(self.session.current_position, 0)  # Position doesn't advance
        self.assertEqual(self.session.errors, 1)
        self.assertEqual(self.session.error_positions, [0])
    
    def test_complete_session(self):
        """Test completing a typing session"""
        # Use a shorter text for this test
        short_text = "abc"
        session = TypingSession(short_text, "test_user")
        
        session.process_keystroke("a")
        session.process_keystroke("b")
        result = session.process_keystroke("c")
        
        self.assertTrue(result["complete"])
        self.assertIsNotNone(session.end_time)
    
    def test_metrics_calculation(self):
        """Test calculating typing metrics"""
        # Create a session with controlled timing
        session = TypingSession("test", "test_user")
        session.start_time = time.time() - 60  # Started 60 seconds ago
        
        # Simulate typing 'test' correctly
        session.process_keystroke("t")
        session.process_keystroke("e")
        session.process_keystroke("s")
        session.process_keystroke("t")
        
        # Get metrics
        metrics = session.get_metrics()
        
        # 4 characters in 60 seconds = 4/5 words in 1 minute = 0.8 WPM
        # With rounding, this should be 0.8 or 1.0 depending on exact timing
        self.assertLessEqual(abs(metrics.wpm - 0.8), 0.3)
        self.assertEqual(metrics.accuracy, 100.0)
        self.assertEqual(metrics.errors, 0)
        self.assertEqual(metrics.characters_typed, 4)
    
    def test_exercise_manager_initialization(self):
        """Test that ExerciseManager initializes correctly"""
        # Check that default exercises were created
        self.assertIn("levels", self.exercise_manager.exercises)
        self.assertIn("beginner", self.exercise_manager.exercises["levels"])
        self.assertIn("intermediate", self.exercise_manager.exercises["levels"])
        self.assertIn("advanced", self.exercise_manager.exercises["levels"])
    
    def test_get_exercise(self):
        """Test retrieving a specific exercise"""
        # Get a beginner exercise
        exercise = self.exercise_manager.get_exercise("beginner", "b1")
        self.assertEqual(exercise["id"], "b1")
        self.assertIn("title", exercise)
        self.assertIn("text", exercise)
    
    def test_get_nonexistent_exercise(self):
        """Test retrieving a non-existent exercise"""
        exercise = self.exercise_manager.get_exercise("nonexistent", "xyz")
        self.assertEqual(exercise["id"], "not_found")
    
    def test_get_random_exercise(self):
        """Test retrieving a random exercise"""
        exercise = self.exercise_manager.get_random_exercise()
        self.assertIn("id", exercise)
        self.assertIn("title", exercise)
        self.assertIn("text", exercise)

if __name__ == "__main__":
    unittest.main()