@echo off
echo.
echo 🎵 Music Mood Player - Camera Setup 🎵
echo =====================================
echo.

echo Installing camera dependencies...
echo.

echo [1/5] Installing OpenCV...
pip install opencv-python==4.8.1.78

echo [2/5] Installing NumPy...
pip install numpy==1.24.3

echo [3/5] Installing FER (Facial Expression Recognition)...
pip install fer==22.5.1

echo [4/5] Installing TensorFlow...
pip install tensorflow==2.15.0

echo [5/5] Installing MTCNN...
pip install mtcnn==0.1.1

echo.
echo ✅ Camera dependencies installed!
echo.
echo Available commands:
echo   python app_hybrid.py  - Camera + demo version
echo   python app.py         - Demo only version  
echo   python launch.py      - Smart launcher
echo.
echo 🚀 Starting camera-enabled version...
python launch.py
