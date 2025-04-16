"""
Analytics module for KasongoType
Tracks user performance over time and provides insights
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

class UserProfile:
    def __init__(self, user_id: str, data_path: str = "../common/data/user_profiles.json"):
        self.user_id = user_id
        self.data_path = Path(data_path)
        self.profile = self._load_profile()
        
    def _load_profile(self) -> Dict:
        """Load user profile from storage or create new one"""
        if not self.data_path.exists():
            # Create directory if it doesn't exist
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty profiles file
            with open(self.data_path, 'w') as f:
                json.dump({}, f)
                
            return self._create_new_profile()
            
        try:
            with open(self.data_path, 'r') as f:
                profiles = json.load(f)
            
            if self.user_id in profiles:
                return profiles[self.user_id]
            else:
                return self._create_new_profile()
                
        except (json.JSONDecodeError, IOError):
            # Return empty structure if file is corrupted or unreadable
            return self._create_new_profile()
    
    def _create_new_profile(self) -> Dict:
        """Create a new user profile with default values"""
        new_profile = {
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "sessions": [],
            "stats": {
                "best_wpm": 0,
                "average_wpm": 0,
                "total_time": 0,
                "exercises_completed": 0,
                "accuracy": 100
            }
        }
        
        # Save new profile
        self._save_profile(new_profile)
        return new_profile
    
    def _save_profile(self, profile_data: Optional[Dict] = None) -> None:
        """Save user profile to storage"""
        if profile_data is None:
            profile_data = self.profile
            
        try:
            with open(self.data_path, 'r') as f:
                profiles = json.load(f)
        except (json.JSONDecodeError, IOError):
            profiles = {}
            
        profiles[self.user_id] = profile_data
        
        with open(self.data_path, 'w') as f:
            json.dump(profiles, f, indent=2)
    
    def record_session(self, exercise_id: str, wpm: float, accuracy: float, time_elapsed: float) -> None:
        """Record a completed typing session"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "exercise_id": exercise_id,
            "wpm": wpm,
            "accuracy": accuracy,
            "time_elapsed": time_elapsed
        }
        
        # Update profile with new session
        self.profile["sessions"].append(session)
        self.profile["last_active"] = datetime.now().isoformat()
        
        # Update aggregate stats
        stats = self.profile["stats"]
        stats["best_wpm"] = max(stats["best_wpm"], wpm)
        stats["exercises_completed"] += 1
        stats["total_time"] += time_elapsed
        
        # Calculate new average WPM
        total_sessions = len(self.profile["sessions"])
        if total_sessions > 0:
            total_wpm = sum(s["wpm"] for s in self.profile["sessions"])
            stats["average_wpm"] = round(total_wpm / total_sessions, 2)
            
            # Calculate new average accuracy
            total_accuracy = sum(s["accuracy"] for s in self.profile["sessions"])
            stats["accuracy"] = round(total_accuracy / total_sessions, 2)
            
        # Save updated profile
        self._save_profile()
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get the most recent typing sessions"""
        sessions = sorted(
            self.profile["sessions"], 
            key=lambda s: s["timestamp"], 
            reverse=True
        )
        return sessions[:limit]
    
    def get_progress_data(self) -> Dict[str, List]:
        """Get data for progress charts"""
        # Sort sessions by timestamp
        sorted_sessions = sorted(
            self.profile["sessions"],
            key=lambda s: s["timestamp"]
        )
        
        # Prepare data for charts
        wpm_over_time = []
        accuracy_over_time = []
        
        for session in sorted_sessions:
            timestamp = datetime.fromisoformat(session["timestamp"]).timestamp() * 1000  # Convert to JS timestamp
            wpm_over_time.append({"x": timestamp, "y": session["wpm"]})
            accuracy_over_time.append({"x": timestamp, "y": session["accuracy"]})
            
        return {
            "wpm": wpm_over_time,
            "accuracy": accuracy_over_time
        }
        
    def get_stats(self) -> Dict:
        """Get user statistics"""
        return self.profile["stats"]