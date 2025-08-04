# Music Mood Player Configuration

## Camera Settings
CAMERA_INDEX = 0  # Change if you have multiple cameras
DETECTION_INTERVAL = 2  # Seconds between mood checks
MOOD_CHANGE_COOLDOWN = 10  # Minimum seconds between mood changes

## Audio Settings
DEFAULT_VOLUME = 0.7  # 0.0 to 1.0
AUDIO_BUFFER_SIZE = 512
AUDIO_FREQUENCY = 22050

## Mood Detection Settings
CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence for mood detection
STABLE_MOOD_WINDOW = 15  # Seconds to consider for stable mood
MOOD_HISTORY_SIZE = 50  # Number of mood detections to keep

## Web Interface
HOST = '0.0.0.0'  # Set to '127.0.0.1' for local access only
PORT = 5000
DEBUG = True  # Set to False in production

## Machine Learning
AUTO_TRAIN = True  # Automatically train classifier when music is added
MODEL_PATH = 'music_mood_model.pkl'
FEATURE_EXTRACTION_DURATION = 30  # Seconds of audio to analyze per song
