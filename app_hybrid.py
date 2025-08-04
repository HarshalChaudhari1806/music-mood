"""
Hybrid Music Mood Player - Camera + Demo Version
Supports both camera detection and demo mode for deployment
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

# Try to import camera dependencies
try:
    import cv2
    import numpy as np
    CAMERA_AVAILABLE = True
    logger.info("Camera dependencies loaded successfully")
except ImportError as e:
    CAMERA_AVAILABLE = False
    logger.info(f"Camera dependencies not available: {e}")
    logger.info("Running in demo mode")

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

# Global state
current_mood_state = {
    'mood': 'neutral',
    'confidence': 0.8,
    'timestamp': time.time()
}

detection_active = False
camera = None
demo_songs = {
    'happy': ['Sunshine Vibes', 'Happy Days', 'Feel Good Song'],
    'sad': ['Melancholy Blues', 'Tears in Rain', 'Lonely Heart'],
    'angry': ['Rage Storm', 'Fire Inside', 'Break the Walls'],
    'surprise': ['Unexpected Joy', 'Wow Moment', 'Amazing Grace'],
    'fear': ['Dark Shadows', 'Tension Rising', 'Heart Racing'],
    'neutral': ['Calm Waters', 'Peaceful Mind', 'Steady Beat'],
    'disgust': ['Bitter Truth', 'Sour Notes', 'Distaste']
}

class SimpleMoodDetector:
    """Simplified mood detector for web deployment"""
    
    def __init__(self):
        self.is_detecting = False
        self.current_mood = "neutral"
        self.mood_confidence = 0.0
        self.camera = None
        
        # Try to load advanced ML if available
        try:
            from fer import FER
            self.detector = FER(mtcnn=True)
            self.advanced_detection = True
            logger.info("Advanced FER detection loaded")
        except ImportError:
            self.detector = None
            self.advanced_detection = False
            logger.info("Using basic mood detection")
    
    def start_detection(self, camera_index=0):
        """Start camera-based mood detection"""
        if not CAMERA_AVAILABLE:
            return False
            
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                return False
            
            self.is_detecting = True
            # Start detection in a separate thread
            import threading
            detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            detection_thread.start()
            
            logger.info("Camera mood detection started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera detection: {e}")
            return False
    
    def stop_detection(self):
        """Stop camera detection"""
        self.is_detecting = False
        if self.camera:
            self.camera.release()
            self.camera = None
        logger.info("Camera detection stopped")
    
    def _detection_loop(self):
        """Basic detection loop"""
        while self.is_detecting and self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            try:
                if self.advanced_detection and self.detector:
                    # Use FER if available
                    emotions = self.detector.detect_emotions(frame)
                    if emotions and len(emotions) > 0:
                        emotion_scores = emotions[0]['emotions']
                        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
                        confidence = emotion_scores[dominant_emotion]
                        
                        if confidence > 0.3:
                            self.current_mood = dominant_emotion
                            self.mood_confidence = confidence
                else:
                    # Basic face detection fallback
                    self._basic_detection(frame)
                
            except Exception as e:
                logger.error(f"Detection error: {e}")
            
            time.sleep(0.1)  # 10 FPS
    
    def _basic_detection(self, frame):
        """Basic mood detection using OpenCV face detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Simple mood simulation based on face detection
                # In a real implementation, you'd analyze facial features
                mood_options = ['happy', 'neutral', 'sad']
                self.current_mood = random.choice(mood_options)
                self.mood_confidence = random.uniform(0.6, 0.9)
                
        except Exception as e:
            logger.error(f"Basic detection error: {e}")
    
    def get_current_mood(self):
        """Get current detected mood"""
        return {
            'mood': self.current_mood,
            'confidence': self.mood_confidence,
            'timestamp': time.time(),
            'method': 'camera' if self.is_detecting else 'demo'
        }

# Initialize mood detector
mood_detector = SimpleMoodDetector() if CAMERA_AVAILABLE else None

@app.route('/')
def index():
    """Main page - adaptive based on capabilities"""
    if CAMERA_AVAILABLE:
        return render_template('index.html')  # Full version with camera
    else:
        return render_template('demo.html')   # Demo version

@app.route('/camera')
def camera_page():
    """Camera-enabled page"""
    return render_template('index.html')

@app.route('/demo')
def demo_page():
    """Demo page"""
    return render_template('demo.html')

@app.route('/api/capabilities')
def get_capabilities():
    """Get system capabilities"""
    return jsonify({
        'camera_available': CAMERA_AVAILABLE,
        'advanced_detection': mood_detector.advanced_detection if mood_detector else False,
        'features': {
            'camera_detection': CAMERA_AVAILABLE,
            'demo_mode': True,
            'advanced_ml': mood_detector.advanced_detection if mood_detector else False
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': 'hybrid',
        'mode': 'camera+demo' if CAMERA_AVAILABLE else 'demo',
        'timestamp': time.time()
    })

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start mood detection - camera or demo"""
    global detection_active
    
    if CAMERA_AVAILABLE and mood_detector:
        # Try camera detection
        success = mood_detector.start_detection()
        if success:
            detection_active = True
            return jsonify({
                'success': True,
                'message': 'Camera detection started',
                'mode': 'camera'
            })
    
    # Fallback to demo mode
    detection_active = True
    logger.info("Demo detection started")
    return jsonify({
        'success': True,
        'message': 'Demo detection started (camera not available)',
        'mode': 'demo'
    })

@app.route('/api/stop_detection', methods=['POST']) 
def stop_detection():
    """Stop mood detection"""
    global detection_active
    detection_active = False
    
    if mood_detector:
        mood_detector.stop_detection()
    
    return jsonify({
        'success': True,
        'message': 'Detection stopped'
    })

@app.route('/api/current_mood')
def get_current_mood():
    """Get current mood - camera or simulated"""
    global current_mood_state
    
    if CAMERA_AVAILABLE and mood_detector and mood_detector.is_detecting:
        # Get real camera detection
        return jsonify(mood_detector.get_current_mood())
    else:
        # Demo mode - simulate mood changes
        if detection_active and random.random() < 0.2:  # 20% chance
            new_mood = random.choice(MOODS)
            current_mood_state = {
                'mood': new_mood,
                'confidence': round(random.uniform(0.6, 0.95), 2),
                'timestamp': time.time(),
                'method': 'demo'
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
            'timestamp': time.time(),
            'method': 'manual'
        }
        logger.info(f"Manual mood set to: {mood}")
        return jsonify({
            'success': True,
            'mood': mood,
            'confidence': current_mood_state['confidence'],
            'emoji': MOOD_EMOJIS.get(mood, '😐')
        })
    
    return jsonify({'success': False, 'message': 'Invalid mood'})

# Include all the other API endpoints from the demo version
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
        'camera_mode': CAMERA_AVAILABLE
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
        'position': random.randint(30, 180),
        'volume': 70,
        'camera_mode': CAMERA_AVAILABLE
    })

@app.route('/api/set_detection_params', methods=['POST'])
def set_detection_params():
    """Set detection parameters"""
    data = request.get_json()
    logger.info(f"Detection params updated: {data}")
    return jsonify({
        'success': True,
        'message': 'Parameters updated',
        'params': data,
        'camera_mode': CAMERA_AVAILABLE
    })

@app.route('/api/detection_debug')
def get_detection_debug():
    """Debug information"""
    return jsonify({
        'success': True,
        'debug_info': {
            'camera_available': CAMERA_AVAILABLE,
            'detection_active': detection_active,
            'advanced_detection': mood_detector.advanced_detection if mood_detector else False,
            'current_mode': 'camera' if (CAMERA_AVAILABLE and detection_active) else 'demo'
        },
        'current_mood': current_mood_state
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Set start time for statistics
    app.start_time = time.time()
    
    # Get port and host from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info("🎵 Music Mood Player - Hybrid Version 🎵")
    logger.info("=========================================")
    logger.info(f"📷 Camera Available: {CAMERA_AVAILABLE}")
    logger.info(f"🤖 Advanced ML: {mood_detector.advanced_detection if mood_detector else False}")
    logger.info(f"🌐 Starting on {host}:{port}")
    
    # Run the app
    app.run(host=host, port=port, debug=False)
