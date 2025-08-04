# Local Development Setup Guide

## Camera Version (Full Features)

### Option 1: Use the Hybrid Version
```bash
# Install camera dependencies
pip install -r requirements_camera.txt

# Run hybrid version (auto-detects camera)
python app_hybrid.py
```

### Option 2: Auto-Launcher
```bash
# Automatically chooses best version
python launch.py
```

## Available Versions

1. **app.py** - Lightweight demo (current deployment)
2. **app_hybrid.py** - Camera + demo support
3. **launch.py** - Smart launcher

## Camera Features

When camera dependencies are available:
- ✅ Real-time facial emotion detection
- ✅ Advanced ML with FER library
- ✅ OpenCV integration
- ✅ Automatic fallback to demo mode

## System Requirements

### Minimum (Demo):
- Flask
- Basic Python libraries

### Full Camera Support:
- OpenCV (cv2)
- FER library
- TensorFlow
- NumPy
- MTCNN

## Quick Start

```bash
# Clone/download the project
git clone <repository>
cd music_mood

# For demo version:
python app.py

# For camera version:
pip install opencv-python fer tensorflow
python app_hybrid.py

# Smart launcher:
python launch.py
```

## Deployment Notes

- **Railway/Render**: Uses app.py (demo) for fast deployment
- **Local development**: Use app_hybrid.py for full features
- **Docker**: Can include camera dependencies for full features
