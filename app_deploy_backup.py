"""
Deployment-ready version of the Music Mood Player
Optimized for cloud hosting platforms
"""
import os
from flask import Flask, render_template, jsonify, request
import logging
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for deployment
mood_detector = None
music_manager = None
current_mood = {"mood": "neutral", "confidence": 0.0}

def initialize_components():
    """Initialize components with error handling for deployment"""
    global mood_detector, music_manager
    
    try:
        # Import here to handle missing dependencies gracefully
        from mood_detector import MoodDetector
        from music_manager import MusicManager
        
        mood_detector = MoodDetector()
        music_manager = MusicManager()
        logger.info("Components initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        logger.info("Running in demo mode - camera features disabled")
        return False

# Try to initialize components
components_loaded = initialize_components()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'components_loaded': components_loaded,
        'mode': 'full' if components_loaded else 'demo'
    })

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start mood detection"""
    if not components_loaded:
        return jsonify({
            'success': False, 
            'message': 'Camera detection not available in demo mode'
        })
    
    try:
        if mood_detector.start_detection():
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to start camera'})
    except Exception as e:
        logger.error(f"Error starting detection: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    """Stop mood detection"""
    if not components_loaded:
        return jsonify({'success': True})
    
    try:
        mood_detector.stop_detection()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error stopping detection: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/current_mood')
def get_current_mood():
    """Get current detected mood"""
    if not components_loaded:
        return jsonify(current_mood)
    
    try:
        return jsonify(mood_detector.get_current_mood())
    except Exception as e:
        logger.error(f"Error getting current mood: {e}")
        return jsonify(current_mood)

@app.route('/api/demo_mood/<mood>')
def set_demo_mood(mood):
    """Set mood in demo mode"""
    global current_mood
    current_mood = {
        "mood": mood,
        "confidence": 0.8,
        "timestamp": time.time()
    }
    return jsonify({'success': True, 'mood': mood})

@app.route('/api/library_stats')
def get_library_stats():
    """Get music library statistics"""
    if not components_loaded:
        return jsonify({
            'total_songs': 0,
            'mood_counts': {},
            'demo_mode': True
        })
    
    try:
        return jsonify(music_manager.get_library_stats())
    except Exception as e:
        logger.error(f"Error getting library stats: {e}")
        return jsonify({'total_songs': 0, 'mood_counts': {}})

@app.route('/api/playback_status')
def get_playback_status():
    """Get current playback status"""
    if not components_loaded:
        return jsonify({
            'is_playing': False,
            'current_song': None,
            'position': 0,
            'volume': 70,
            'demo_mode': True
        })
    
    try:
        return jsonify(music_manager.get_playback_status())
    except Exception as e:
        logger.error(f"Error getting playback status: {e}")
        return jsonify({'is_playing': False, 'current_song': None})

# Demo endpoints for hosting platforms
@app.route('/api/demo')
def demo_info():
    """Demo information endpoint"""
    return jsonify({
        'message': 'Music Mood Player Demo',
        'features': [
            'Real-time facial emotion detection',
            'AI-powered music mood classification',
            'Adaptive music playback based on emotions',
            'Advanced detection parameter controls',
            'Enhanced sad emotion sensitivity'
        ],
        'demo_mode': not components_loaded,
        'instructions': 'This is a demo version. Full functionality requires local deployment with camera access.'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Music Mood Player on {host}:{port}")
    if not components_loaded:
        logger.info("Running in DEMO MODE - Camera features disabled")
        logger.info("Full features available with local deployment")
    
    app.run(host=host, port=port, debug=False)
