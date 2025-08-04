"""
Lightweight Music Mood Player - Demo Version
Optimized for fast deployment without heavy ML dependencies
"""
import os
import time
import random
from flask import Flask, render_template, jsonify, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Demo data for mood simulation
MOODS = ['happy', 'sad', 'angry', 'surprise', 'fear', 'neutral', 'disgust']
MOOD_EMOJIS = {
    'happy': '😊',
    'sad': '😢', 
    'angry': '😠',
    'surprise': '😲',
    'fear': '😨',
    'neutral': '😐',
    'disgust': '🤢'
}

# Global state for demo
current_mood_state = {
    'mood': 'neutral',
    'confidence': 0.8,
    'timestamp': time.time()
}

detection_active = False
demo_songs = {
    'happy': ['Sunshine Vibes', 'Happy Days', 'Feel Good Song'],
    'sad': ['Melancholy Blues', 'Tears in Rain', 'Lonely Heart'],
    'angry': ['Rage Storm', 'Fire Inside', 'Break the Walls'],
    'surprise': ['Unexpected Joy', 'Wow Moment', 'Amazing Grace'],
    'fear': ['Dark Shadows', 'Tension Rising', 'Heart Racing'],
    'neutral': ['Calm Waters', 'Peaceful Mind', 'Steady Beat'],
    'disgust': ['Bitter Truth', 'Sour Notes', 'Distaste']
}

@app.route('/')
def index():
    """Main page - serves the demo template"""
    return render_template('demo.html')

@app.route('/full')
def full_app():
    """Full app page - shows what the complete app looks like"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': 'demo',
        'mode': 'lightweight',
        'timestamp': time.time()
    })

@app.route('/api/demo')
def demo_info():
    """Demo information"""
    return jsonify({
        'title': 'Music Mood Player - Demo',
        'description': 'AI-powered emotion detection and music recommendation system',
        'features': [
            'Real-time facial emotion detection',
            'Advanced machine learning mood classification', 
            'Adaptive music selection based on emotions',
            'Enhanced sad emotion sensitivity',
            'Customizable detection parameters'
        ],
        'deployment': {
            'platforms': ['Railway', 'Render', 'Fly.io', 'Heroku'],
            'demo_mode': True,
            'full_version_available': True
        }
    })

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start demo mood detection"""
    global detection_active
    detection_active = True
    logger.info("Demo detection started")
    return jsonify({
        'success': True,
        'message': 'Demo mood detection started',
        'mode': 'simulation'
    })

@app.route('/api/stop_detection', methods=['POST']) 
def stop_detection():
    """Stop demo mood detection"""
    global detection_active
    detection_active = False
    logger.info("Demo detection stopped")
    return jsonify({
        'success': True,
        'message': 'Demo detection stopped'
    })

@app.route('/api/current_mood')
def get_current_mood():
    """Get current mood - simulated or set"""
    global current_mood_state
    
    # If detection is active, occasionally change mood randomly
    if detection_active and random.random() < 0.3:  # 30% chance
        new_mood = random.choice(MOODS)
        current_mood_state = {
            'mood': new_mood,
            'confidence': round(random.uniform(0.6, 0.95), 2),
            'timestamp': time.time()
        }
    
    return jsonify(current_mood_state)

@app.route('/api/demo_mood/<mood>')
def set_demo_mood(mood):
    """Set specific mood for demo"""
    global current_mood_state
    
    if mood in MOODS:
        current_mood_state = {
            'mood': mood,
            'confidence': round(random.uniform(0.7, 0.95), 2),
            'timestamp': time.time()
        }
        logger.info(f"Demo mood set to: {mood}")
        return jsonify({
            'success': True,
            'mood': mood,
            'confidence': current_mood_state['confidence'],
            'emoji': MOOD_EMOJIS.get(mood, '😐')
        })
    
    return jsonify({'success': False, 'message': 'Invalid mood'})

@app.route('/api/songs_by_mood/<mood>')
def get_songs_by_mood(mood):
    """Get demo songs for a mood"""
    songs = demo_songs.get(mood, demo_songs['neutral'])
    return jsonify({
        'mood': mood,
        'songs': [{'title': song, 'artist': 'Demo Artist'} for song in songs],
        'count': len(songs)
    })

@app.route('/api/library_stats')
def get_library_stats():
    """Get demo library statistics"""
    total_songs = sum(len(songs) for songs in demo_songs.values())
    return jsonify({
        'total_songs': total_songs,
        'mood_counts': {mood: len(songs) for mood, songs in demo_songs.items()},
        'demo_mode': True
    })

@app.route('/api/playback_status')
def get_playback_status():
    """Get demo playback status"""
    mood = current_mood_state['mood']
    current_song = random.choice(demo_songs.get(mood, demo_songs['neutral']))
    
    return jsonify({
        'is_playing': detection_active,
        'current_song': {
            'title': current_song,
            'artist': 'Demo Artist',
            'mood': mood
        },
        'position': random.randint(30, 180),  # Random position
        'volume': 70,
        'demo_mode': True
    })

@app.route('/api/mood_stats')
def get_mood_stats():
    """Get mood detection statistics"""
    return jsonify({
        'session_duration': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
        'total_detections': random.randint(50, 200),
        'mood_distribution': {
            'happy': random.randint(10, 30),
            'sad': random.randint(5, 15), 
            'neutral': random.randint(20, 40),
            'angry': random.randint(2, 8),
            'surprise': random.randint(3, 10),
            'fear': random.randint(1, 5),
            'disgust': random.randint(1, 3)
        },
        'average_confidence': round(random.uniform(0.75, 0.90), 2),
        'demo_mode': True
    })

@app.route('/api/set_detection_params', methods=['POST'])
def set_detection_params():
    """Demo endpoint for detection parameters"""
    data = request.get_json()
    logger.info(f"Demo: Detection params updated: {data}")
    return jsonify({
        'success': True,
        'message': 'Demo parameters updated',
        'params': data
    })

@app.route('/api/set_sad_sensitivity', methods=['POST'])
def set_sad_sensitivity():
    """Demo endpoint for sad sensitivity"""
    data = request.get_json()
    sensitivity = data.get('sensitivity', 1.0)
    logger.info(f"Demo: Sad sensitivity set to {sensitivity}")
    return jsonify({
        'success': True,
        'sensitivity': sensitivity,
        'message': f'Demo sad sensitivity: {sensitivity}x'
    })

@app.route('/api/detection_debug')
def get_detection_debug():
    """Demo debug information"""
    return jsonify({
        'success': True,
        'debug_info': {
            'confidence_threshold': 0.20,
            'emotion_thresholds': {
                'sad': 0.15,
                'happy': 0.25,
                'angry': 0.30,
                'neutral': 0.20
            },
            'emotion_intensity': {
                'sad': 1.2,
                'happy': 1.0,
                'angry': 1.0,
                'neutral': 0.5
            },
            'demo_mode': True
        },
        'current_mood': current_mood_state
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found', 'demo_mode': True}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'demo_mode': True}), 500

if __name__ == '__main__':
    # Set start time for statistics
    app.start_time = time.time()
    
    # Get port and host from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info("🎵 Music Mood Player - Demo Version 🎵")
    logger.info("=====================================")
    logger.info("🚀 Lightweight deployment version")
    logger.info("📱 Full camera features in local version")
    logger.info(f"🌐 Starting on {host}:{port}")
    
    # Run the app
    app.run(host=host, port=port, debug=False)
