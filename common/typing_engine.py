"""
Core typing engine for KasongoType
Handles typing sessions, statistics, and exercise management
"""

import json
import time
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class TypingMetrics:
    wpm: float = 0.0
    accuracy: float = 0.0
    errors: int = 0
    time_elapsed: float = 0.0
    time_remaining: float = 0.0
    characters_typed: int = 0
    
class TypingSession:
    def __init__(self, text, user_id):
        self.text = text
        self.user_id = user_id
        self.start_time = time.time()
        self.current_position = 0
        self.errors = 0
        self.keystrokes = []
        
        # Calculate estimated completion time based on text length
        # Average typing speed is ~40 WPM = ~200 CPM
        char_count = len(text)
        # 1 word ≈ 5 characters
        word_count = char_count / 5
        # Minimum 20 seconds, maximum 5 minutes
        self.estimated_duration = max(20, min(300, word_count * 1.5))
    
    def process_keystroke(self, keystroke):
        # Record the keystroke
        timestamp = time.time()
        self.keystrokes.append({
            'key': keystroke,
            'timestamp': timestamp
        })
        
        # Check if correct
        expected = self.text[self.current_position] if self.current_position < len(self.text) else None
        correct = expected == keystroke
        
        if correct:
            self.current_position += 1
        else:
            self.errors += 1
        
        # Calculate time values
        time_elapsed = timestamp - self.start_time
        
        # Check if exercise is complete by text or time
        time_completed = time_elapsed >= self.estimated_duration
        text_completed = self.current_position >= len(self.text)
        complete = text_completed or time_completed
        
        # Calculate time remaining (for countdown mode)
        time_remaining = max(0, self.estimated_duration - time_elapsed)
        
        return {
            "correct": correct,
            "complete": complete,
            "position": self.current_position,
            "remaining": len(self.text) - self.current_position,
            "time_elapsed": time_elapsed,
            "time_remaining": time_remaining,
            "time_completed": time_completed,
            "text_completed": text_completed
        }
    
    def get_metrics(self):
        # Calculate time elapsed
        time_elapsed = time.time() - self.start_time
        
        # Calculate WPM: (characters / 5) / (minutes)
        char_count = self.current_position
        minutes = max(time_elapsed / 60, 0.01)  # Prevent division by zero, minimum 0.01 minutes
        
        # Standard formula: (characters typed / 5) / minutes elapsed
        wpm = (char_count / 5) / minutes
        
        # Calculate accuracy - account for zero division
        total_keystrokes = len(self.keystrokes)
        if total_keystrokes > 0:
            accuracy = ((total_keystrokes - self.errors) / total_keystrokes) * 100
        else:
            accuracy = 100.0
        
        return {
            'wpm': round(wpm, 1),
            'accuracy': round(accuracy, 1),
            'time_elapsed': time_elapsed,
            'errors': self.errors,
            'char_count': char_count,
            'total_keystrokes': total_keystrokes
        }



class ExerciseManager:
    def __init__(self, data_path: str = "../common/data/exercises.json"):
        self.data_path = Path(data_path)
        self.exercises = self._load_exercises()
        
    def _load_exercises(self) -> Dict:
        """Load exercises from JSON file"""
        if not self.data_path.exists():
            # Create default exercises if file doesn't exist
            default_exercises = {
                "levels": {
                    "beginner": [
                        {"id": "b1", "title": "Home Row", "text": "asdf jkl; asdf jkl; asdf jkl;"},
                        {"id": "b2", "title": "Top Row", "text": "qwer tyui qwer tyui qwer tyui"},
                        {"id": "b3", "title": "Bottom Row", "text": "zxcv bnm, zxcv bnm, zxcv bnm,"}
                    ],
                    "intermediate": [
                        {"id": "i1", "title": "Common Words", "text": "the quick brown fox jumps over the lazy dog"},
                        {"id": "i2", "title": "Numbers", "text": "1234 5678 9000 1234 5678 9000"},
                        {"id": "i3", "title": "Symbols", "text": "!@#$ %^&* !@#$ %^&* !@#$ %^&*"}
                    ],
                    "advanced": [
                        {"id": "a1", "title": "Code Syntax", "text": "def main(): print('Hello, World!')"},
                        {"id": "a2", "title": "Cyberpunk", "text": "Neon lights glowed in the digital haze of Night City."},
                        {"id": "a3", "title": "Speed Challenge", "text": "The five boxing wizards jump quickly to explore the vast cybernetic mainframe."}
                    ]
                }
            }
            
            # Create directory if it doesn't exist
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default exercises
            with open(self.data_path, 'w') as f:
                json.dump(default_exercises, f, indent=2)
                
            return default_exercises
        
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return empty structure if file is corrupted or unreadable
            return {"levels": {}}
    
    def get_exercise(self, level: str, exercise_id: str) -> Dict:
        """Get a specific exercise by level and ID"""
        if level in self.exercises["levels"]:
            for exercise in self.exercises["levels"][level]:
                if exercise["id"] == exercise_id:
                    return exercise
        return {"id": "not_found", "title": "Exercise Not Found", "text": ""}
    
    def get_exercises_by_level(self, level: str) -> List[Dict]:
        """Get all exercises for a specific level"""
        return self.exercises["levels"].get(level, [])
    
    def get_random_exercise(self) -> Dict:
        """Get a random exercise from any level"""
        all_exercises = []
        for level in self.exercises["levels"].values():
            all_exercises.extend(level)
            
        if all_exercises:
            return random.choice(all_exercises)
        return {"id": "empty", "title": "No Exercises Available", "text": ""}