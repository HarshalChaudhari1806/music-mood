#!/usr/bin/env python3
"""
Music Mood Player Launcher
Automatically selects best version based on available dependencies
"""
import sys
import subprocess
import importlib.util

def check_dependency(module_name):
    """Check if a module is available"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def main():
    print("🎵 Music Mood Player Launcher 🎵")
    print("=================================")
    
    # Check for camera dependencies
    has_opencv = check_dependency('cv2')
    has_fer = check_dependency('fer')
    
    print(f"📷 OpenCV: {'✅ Available' if has_opencv else '❌ Not found'}")
    print(f"🤖 FER: {'✅ Available' if has_fer else '❌ Not found'}")
    
    if has_opencv or has_fer:
        print("\n🚀 Starting CAMERA-ENABLED version...")
        print("Features: Camera detection + Demo mode")
        subprocess.run([sys.executable, "app_hybrid.py"])
    else:
        print("\n🚀 Starting DEMO version...")
        print("Features: Demo mode only (lightweight)")
        subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
