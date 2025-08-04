# Quick Start Guide

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
