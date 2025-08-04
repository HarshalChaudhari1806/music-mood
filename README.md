# Music Mood Player

A Python application that detects your mood through facial expression recognition and plays music accordingly.

## Features

- Real-time mood detection using computer vision
- Automatic music categorization by mood
- Mood-based music recommendation and playback
- Web-based user interface
- Support for multiple audio formats (MP3, WAV, etc.)

## Moods Detected

- **Happy**: Upbeat, energetic music
- **Sad**: Melancholic, slow music
- **Angry**: Intense, rock/metal music
- **Neutral**: Ambient, chill music
- **Fear**: Calming, soothing music
- **Surprise**: Dynamic, varied music
- **Disgust**: Alternative, experimental music

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create music folders:
   ```
   music/
   ├── happy/
   ├── sad/
   ├── angry/
   ├── neutral/
   ├── fear/
   ├── surprise/
   └── disgust/
   ```

4. Add your music files to the appropriate mood folders

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`

3. Allow camera access and let the mood detection begin!

## Project Structure

```
music_mood/
├── app.py                 # Main Flask application
├── mood_detector.py       # Mood detection module
├── music_manager.py       # Music management and playback
├── music_analyzer.py      # Music mood analysis
├── requirements.txt       # Dependencies
├── templates/             # HTML templates
├── static/               # CSS, JS, images
└── music/               # Music files organized by mood
```

## License

MIT License
