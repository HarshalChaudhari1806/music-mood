from flask import Flask, render_template, jsonify, request, redirect, url_for
import threading
import time
import os
from mood_detector import MoodDetector
from music_manager import MusicManager
from music_analyzer import MusicAnalyzer
import logging

app = Flask(__name__)
app.secret_key = 'music_mood_secret_key_2024'

# Initialize components
mood_detector = MoodDetector()
music_manager = MusicManager()
music_analyzer = MusicAnalyzer()

# Global state
app_state = {
    'mood_detection_active': False,
    'auto_play_enabled': True,
    'last_mood_change': time.time(),
    'mood_change_cooldown': 8,  # Reduced cooldown for better responsiveness
    'mood_stability_window': 12  # Shorter window for more responsive mood changes
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start mood detection"""
    try:
        if mood_detector.start_detection():
            app_state['mood_detection_active'] = True
            
            # Start mood monitoring thread
            monitor_thread = threading.Thread(target=mood_monitor_loop, daemon=True)
            monitor_thread.start()
            
            return jsonify({'success': True, 'message': 'Mood detection started'})
        else:
            return jsonify({'success': False, 'message': 'Failed to start camera'})
    
    except Exception as e:
        logger.error(f"Error starting detection: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    """Stop mood detection"""
    try:
        mood_detector.stop_detection()
        app_state['mood_detection_active'] = False
        return jsonify({'success': True, 'message': 'Mood detection stopped'})
    
    except Exception as e:
        logger.error(f"Error stopping detection: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/current_mood')
def get_current_mood():
    """Get current detected mood"""
    try:
        mood_data = mood_detector.get_current_mood()
        stable_mood = mood_detector.get_stable_mood()
        
        return jsonify({
            'current_mood': mood_data,
            'stable_mood': stable_mood,
            'detection_active': app_state['mood_detection_active']
        })
    
    except Exception as e:
        logger.error(f"Error getting mood: {e}")
        return jsonify({'error': str(e)})
@app.route('/api/mood_statistics')
def get_mood_statistics():
    """Get mood detection statistics"""
    try:
        stats = mood_detector.get_mood_statistics()
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting mood statistics: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/set_detection_params', methods=['POST'])
def set_detection_params():
    """Set mood detection parameters for fine-tuning"""
    try:
        data = request.get_json()
        
        if 'confidence_threshold' in data:
            mood_detector.confidence_threshold = float(data['confidence_threshold'])
        
        if 'emotion_smoothing' in data:
            mood_detector.emotion_smoothing = float(data['emotion_smoothing'])
        
        if 'mood_change_cooldown' in data:
            app_state['mood_change_cooldown'] = int(data['mood_change_cooldown'])
        
        if 'mood_stability_window' in data:
            app_state['mood_stability_window'] = int(data['mood_stability_window'])
        
        return jsonify({
            'success': True,
            'message': 'Detection parameters updated',
            'current_params': {
                'confidence_threshold': mood_detector.confidence_threshold,
                'emotion_smoothing': mood_detector.emotion_smoothing,
                'mood_change_cooldown': app_state['mood_change_cooldown'],
                'mood_stability_window': app_state['mood_stability_window']
            }
        })
    
    except Exception as e:
        logger.error(f"Error setting detection params: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/set_sad_sensitivity', methods=['POST'])
def set_sad_sensitivity():
    """Set sad emotion detection sensitivity"""
    try:
        data = request.get_json()
        sensitivity = float(data.get('sensitivity', 1.0))
        
        # Clamp sensitivity between 0.5 and 3.0
        sensitivity = max(0.5, min(3.0, sensitivity))
        
        mood_detector.update_sad_sensitivity(sensitivity)
        
        return jsonify({
            'success': True,
            'sensitivity': sensitivity,
            'debug_info': mood_detector.get_detection_debug_info()
        })
    
    except Exception as e:
        logger.error(f"Error setting sad sensitivity: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/detection_debug')
def get_detection_debug():
    """Get debug information about detection parameters"""
    try:
        return jsonify({
            'success': True,
            'debug_info': mood_detector.get_detection_debug_info(),
            'current_mood': mood_detector.get_current_mood()
        })
    
    except Exception as e:
        logger.error(f"Error getting debug info: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/play_mood/<mood>')
def play_mood_music(mood):
    """Play music for a specific mood"""
    try:
        music_manager.play_mood_music(mood)
        return jsonify({'success': True, 'message': f'Playing {mood} music'})
    
    except Exception as e:
        logger.error(f"Error playing mood music: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/music_control/<action>')
def music_control(action):
    """Control music playback"""
    try:
        if action == 'pause':
            music_manager.pause()
        elif action == 'resume':
            music_manager.resume()
        elif action == 'stop':
            music_manager.stop()
        elif action == 'next':
            music_manager.next_song()
        elif action == 'previous':
            music_manager.previous_song()
        elif action == 'shuffle':
            music_manager.toggle_shuffle()
        elif action == 'repeat':
            music_manager.toggle_repeat()
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})
        
        return jsonify({'success': True, 'message': f'Action {action} completed'})
    
    except Exception as e:
        logger.error(f"Error with music control: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/set_volume', methods=['POST'])
def set_volume():
    """Set music volume"""
    try:
        data = request.get_json()
        volume = float(data.get('volume', 0.7))
        music_manager.set_volume(volume)
        return jsonify({'success': True, 'volume': volume})
    
    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/playback_status')
def get_playback_status():
    """Get current playback status"""
    try:
        status = music_manager.get_playback_status()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting playback status: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/library_stats')
def get_library_stats():
    """Get music library statistics"""
    try:
        stats = music_manager.get_library_stats()
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting library stats: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/songs_by_mood/<mood>')
def get_songs_by_mood(mood):
    """Get all songs for a specific mood"""
    try:
        songs = music_manager.get_songs_by_mood(mood)
        return jsonify({'mood': mood, 'songs': songs})
    
    except Exception as e:
        logger.error(f"Error getting songs by mood: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/toggle_auto_play', methods=['POST'])
def toggle_auto_play():
    """Toggle automatic mood-based music playing"""
    try:
        app_state['auto_play_enabled'] = not app_state['auto_play_enabled']
        return jsonify({
            'success': True, 
            'auto_play_enabled': app_state['auto_play_enabled']
        })
    
    except Exception as e:
        logger.error(f"Error toggling auto play: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/refresh_library', methods=['POST'])
def refresh_library():
    """Refresh the music library"""
    try:
        music_manager.refresh_library()
        return jsonify({'success': True, 'message': 'Music library refreshed'})
    
    except Exception as e:
        logger.error(f"Error refreshing library: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/train_classifier', methods=['POST'])
def train_classifier():
    """Train the music mood classifier"""
    try:
        success = music_analyzer.train_classifier('music')
        if success:
            return jsonify({'success': True, 'message': 'Classifier trained successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to train classifier'})
    
    except Exception as e:
        logger.error(f"Error training classifier: {e}")
        return jsonify({'success': False, 'message': str(e)})
def mood_monitor_loop():
    """Background thread to monitor mood changes and play appropriate music"""
    logger.info("Enhanced mood monitoring started")
    
    while app_state['mood_detection_active']:
        try:
            if app_state['auto_play_enabled']:
                # Use enhanced stable mood detection
                stable_mood = mood_detector.get_stable_mood(window_seconds=app_state['mood_stability_window'])
                current_time = time.time()
                
                # Get current mood data for additional analysis
                current_mood_data = mood_detector.get_current_mood()
                
                # Check if enough time has passed since last mood change
                if (current_time - app_state['last_mood_change']) > app_state['mood_change_cooldown']:
                    
                    # Enhanced mood change logic
                    should_change_mood = False
                    
                    if stable_mood != music_manager.current_mood:
                        # Check confidence for mood change
                        if current_mood_data['confidence'] > 0.4:
                            should_change_mood = True
                        elif stable_mood in ['happy', 'sad', 'angry'] and current_mood_data['confidence'] > 0.3:
                            # Lower threshold for strong emotions
                            should_change_mood = True
                    
                    if should_change_mood:
                        logger.info(f"Enhanced mood change: {music_manager.current_mood} → {stable_mood} (confidence: {current_mood_data['confidence']:.2f})")
                        music_manager.play_mood_music(stable_mood)
                        app_state['last_mood_change'] = current_time
            
        except Exception as e:
            logger.error(f"Error in enhanced mood monitor loop: {e}")
        
        time.sleep(1.5)  # Faster checking for better responsiveness
    
    logger.info("Enhanced mood monitoring stopped")
    logger.info("Mood monitoring stopped")

if __name__ == '__main__':
    # Create music directories if they don't exist
    music_dirs = ['music/happy', 'music/sad', 'music/angry', 'music/neutral', 
                  'music/fear', 'music/surprise', 'music/disgust']
    
    for dir_path in music_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    logger.info("Music Mood Player starting...")
    logger.info("Add your music files to the appropriate mood folders in the 'music' directory")
    logger.info("Application will be available at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
