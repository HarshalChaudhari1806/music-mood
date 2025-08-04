import os
import sys
import subprocess
import logging

def setup_music_mood_player():
    """Setup script for Music Mood Player"""
    
    print("🎵 Music Mood Player Setup 🎵")
    print("=" * 40)
    
    # Create music directories
    music_dirs = [
        'music',
        'music/happy',
        'music/sad', 
        'music/angry',
        'music/neutral',
        'music/fear',
        'music/surprise',
        'music/disgust'
    ]
    
    print("\n📁 Creating music directories...")
    for directory in music_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    # Create sample playlist files
    print("\n📝 Creating sample playlist files...")
    
    sample_instructions = {
        'happy': "Upbeat, energetic songs (pop, dance, uplifting rock)",
        'sad': "Melancholic, slow songs (ballads, indie, acoustic)",
        'angry': "Intense, aggressive music (rock, metal, rap)",
        'neutral': "Ambient, chill music (lo-fi, instrumental, soft rock)",
        'fear': "Calming, soothing music (classical, ambient, peaceful)",
        'surprise': "Dynamic, varied music (experimental, eclectic)",
        'disgust': "Alternative, experimental music (avant-garde, unique)"
    }
    
    for mood, description in sample_instructions.items():
        readme_path = f"music/{mood}/README.md"
        with open(readme_path, 'w') as f:
            f.write(f"# {mood.title()} Music\n\n")
            f.write(f"Add your {mood} music files to this folder.\n\n")
            f.write(f"**Recommended genres:** {description}\n\n")
            f.write("**Supported formats:** MP3, WAV, OGG, M4A\n\n")
            f.write("**Note:** The AI will analyze these songs to learn what ")
            f.write(f"{mood} music sounds like and recommend similar songs.\n")
        print(f"✓ Created: {readme_path}")
    
    # Create a sample configuration file
    print("\n⚙️ Creating configuration file...")
    config_content = """# Music Mood Player Configuration

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
"""
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    print("✓ Created: config.py")
    
    # Create a requirements checker
    print("\n📦 Checking Python packages...")
    
    required_packages = [
        'opencv-python', 'tensorflow', 'numpy', 'pygame', 'flask',
        'Pillow', 'scikit-learn', 'pandas', 'librosa', 'mutagen', 'fer'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        
        install_now = input("\nWould you like to install them now? (y/n): ").lower().strip()
        if install_now == 'y':
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("✓ All packages installed successfully!")
            except subprocess.CalledProcessError:
                print("✗ Failed to install packages. Please install manually.")
    else:
        print("\n✅ All required packages are installed!")
    
    # Create a quick start guide
    print("\n📖 Creating quick start guide...")
    
    quick_start = """# Quick Start Guide

## 1. Add Your Music
1. Copy your music files to the appropriate mood folders in the `music/` directory
2. The AI will learn from these examples to classify new music automatically

## 2. Start the Application
```bash
python app.py
```

## 3. Open Your Browser
Navigate to: http://localhost:5000

## 4. Start Mood Detection
1. Click "Start Camera" to begin facial mood detection
2. Allow camera access when prompted
3. The system will automatically play music based on your detected mood

## 5. Manual Control
- Use the mood buttons to manually select music categories
- Control playback with the music player controls
- Adjust volume and enable shuffle/repeat modes

## Tips for Best Results

### Camera Setup
- Ensure good lighting on your face
- Position camera at eye level
- Minimize background distractions
- Allow a few seconds for mood stabilization

### Music Organization
- Add at least 5-10 songs per mood category for best results
- Use clear, well-defined examples of each mood
- The AI learns from your music choices, so organize thoughtfully

### Mood Categories
- **Happy**: Upbeat, positive, energetic music
- **Sad**: Melancholic, slow, emotional music  
- **Angry**: Intense, aggressive, powerful music
- **Neutral**: Calm, ambient, background music
- **Fear**: Soothing, calming, peaceful music
- **Surprise**: Dynamic, varied, unexpected music
- **Disgust**: Alternative, experimental, unique music

## Troubleshooting

### Camera Issues
- Check camera permissions in your browser
- Try different camera index in config.py
- Ensure no other applications are using the camera

### Music Issues
- Check file formats (MP3, WAV, OGG, M4A supported)
- Verify file permissions
- Refresh library after adding new music

### Performance Issues
- Close unnecessary applications
- Reduce detection interval in config.py
- Use smaller audio buffer size for real-time response

## Advanced Features

### Training the AI
- Click "Train AI" after adding music to retrain the classifier
- The system learns your music preferences over time
- More diverse training data = better recommendations

### API Access
The application provides a REST API for integration:
- GET /api/current_mood - Get detected mood
- POST /api/play_mood/<mood> - Play specific mood music
- GET /api/playback_status - Get player status

Enjoy your personalized music experience! 🎵
"""
    
    with open('QUICK_START.md', 'w', encoding='utf-8') as f:
        f.write(quick_start)
    print("✓ Created: QUICK_START.md")
    
    print("\n🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Add music files to the mood folders in 'music/' directory")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Click 'Start Camera' and enjoy!")
    
    print("\n📚 For detailed instructions, see QUICK_START.md")

if __name__ == "__main__":
    setup_music_mood_player()
