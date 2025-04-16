"""
Flask web application for KasongoType
Serves the web interface and handles API requests
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.typing_engine import TypingSession, ExerciseManager
from common.analytics import UserProfile

app = Flask(__name__)
app.secret_key = 'kasongoType_cyb3rpunk_2077'  # For session management

# Initialize exercise manager
exercise_manager = ExerciseManager(data_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                        "common/data/exercises.json"))

# Store active typing sessions
active_sessions = {}

@app.route('/')
def index():
    """Render main typing interface"""
    # Generate a session ID if not exists
    if 'user_id' not in session:
        session['user_id'] = f"web_user_{hash(request.remote_addr)}"
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render user analytics dashboard"""
    return render_template('dashboard.html')

@app.route('/exercises')
def exercises():
    """Render exercises selection page"""
    return render_template('exercises.html')

@app.route('/api/exercises')
def get_exercises():
    """Get all available exercises"""
    level = request.args.get('level', None)
    
    if level:
        exercises = exercise_manager.get_exercises_by_level(level)
        return jsonify({"status": "success", "exercises": exercises})
    else:
        all_exercises = {}
        for level_name in exercise_manager.exercises["levels"]:
            all_exercises[level_name] = exercise_manager.get_exercises_by_level(level_name)
        
        return jsonify({"status": "success", "exercises": all_exercises})

@app.route('/api/exercise/<level>/<id>')
def get_exercise(level, id):
    """Get a specific exercise"""
    exercise = exercise_manager.get_exercise(level, id)
    return jsonify({"status": "success", "exercise": exercise})

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new typing session"""
    data = request.json
    exercise_id = data.get('exercise_id')
    level = data.get('level')
    
    if exercise_id and level:
        exercise = exercise_manager.get_exercise(level, exercise_id)
    else:
        exercise = exercise_manager.get_random_exercise()
    
    # Create a new typing session
    session_id = f"{session['user_id']}_{hash(exercise['text'])}"
    active_sessions[session_id] = TypingSession(exercise['text'], session['user_id'])
    
    return jsonify({
        "status": "success", 
        "session_id": session_id,
        "exercise": exercise
    })

@app.route('/api/session/status')
def session_status():
    """Check if session has started"""
    session_id = request.args.get('session_id')
    
    if session_id and session_id in active_sessions:
        typing_session = active_sessions[session_id]
        return jsonify({
            "status": "success",
            "started": True,
            "session_id": session_id,
            "start_time": typing_session.start_time
        })
    
    return jsonify({
        "status": "success",
        "started": False
    })

@app.route('/api/session/<string:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """Complete a typing session and save final metrics"""
    data = request.json
    metrics = data.get('metrics', {})
    exercise_id = data.get('exercise_id', 'unknown')
    
    # Record the session in user profile
    user_profile = UserProfile(session['user_id'],
                              data_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    "common/data/user_profiles.json"))
    
    user_profile.record_session(
        exercise_id,
        metrics.get('wpm', 0),
        metrics.get('accuracy', 0),
        metrics.get('time_elapsed', 0)
    )
    
    return jsonify({
        "status": "success",
        "message": "Session completed and results saved"
    })

@app.route('/api/session/<string:session_id>/keystroke', methods=['POST'])
def process_keystroke(session_id):
    """Process a keystroke in a typing session"""
    if session_id not in active_sessions:
        return jsonify({"status": "error", "message": "Session not found"}), 404
        
    data = request.json
    keystroke = data.get('key', '')
    
    typing_session = active_sessions[session_id]
    result = typing_session.process_keystroke(keystroke)
    
    # If session is complete, save the results
    if result["complete"]:
        metrics = typing_session.get_metrics()
        user_profile = UserProfile(session['user_id'], 
                                   data_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                         "common/data/user_profiles.json"))
        
        # Check if metrics is a dict or an object with attributes
        if isinstance(metrics, dict):
            user_profile.record_session(
                data.get('exercise_id', 'unknown'),
                metrics.get('wpm', 0),
                metrics.get('accuracy', 0),
                metrics.get('time_elapsed', 0)
            )
        else:
            # Assuming metrics is an object with attributes
            user_profile.record_session(
                data.get('exercise_id', 'unknown'),
                getattr(metrics, 'wpm', 0),
                getattr(metrics, 'accuracy', 0),
                getattr(metrics, 'time_elapsed', 0)
            )
        
        # Clean up the session
        del active_sessions[session_id]
    
    # Handle metrics similarly for the response
    metrics_data = None
    if "complete" in result and result["complete"]:
        metrics = typing_session.get_metrics()
        if isinstance(metrics, dict):
            metrics_data = metrics
        else:
            metrics_data = metrics.__dict__
        
    return jsonify({
        "status": "success",
        "result": result,
        "metrics": metrics_data
    })


@app.route('/api/user/stats')
def get_user_stats():
    """Get user statistics"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "No user session"}), 401
        
    user_profile = UserProfile(session['user_id'], 
                               data_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                     "common/data/user_profiles.json"))
    
    stats = user_profile.get_stats()
    recent_sessions = user_profile.get_recent_sessions(10)
    progress_data = user_profile.get_progress_data()
    
    return jsonify({
        "status": "success",
        "stats": stats,
        "recent_sessions": recent_sessions,
        "progress_data": progress_data
    })

if __name__ == '__main__':
    app.run(debug=True)