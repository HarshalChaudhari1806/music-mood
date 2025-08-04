#!/bin/bash

# Music Mood Player - Quick Deployment Setup
echo "🎵 Music Mood Player - Deployment Setup 🎵"
echo "============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Music Mood Player"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Virtual environment
.venv/
venv/
env/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Environment variables
.env

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Music files (too large for git)
music/*.mp3
music/*.wav
music/*.m4a
music/*.flac

# Temporary files
*.tmp
*.temp
EOF
    echo "✅ .gitignore created"
fi

echo ""
echo "🚀 Deployment Options:"
echo "======================"
echo ""
echo "1. 🌟 Railway (Recommended):"
echo "   - Go to https://railway.app"
echo "   - Connect GitHub and deploy"
echo "   - Auto-detects Python"
echo ""
echo "2. 🔥 Render:"
echo "   - Go to https://render.com"
echo "   - Create Web Service"
echo "   - Build: pip install -r requirements.txt"
echo "   - Start: python app_deploy.py"
echo ""
echo "3. ⚡ Fly.io:"
echo "   - Install flyctl"
echo "   - Run: fly launch"
echo "   - Run: fly deploy"
echo ""
echo "4. 🐳 Docker:"
echo "   - Run: docker build -t music-mood-player ."
echo "   - Run: docker run -p 5000:5000 music-mood-player"
echo ""
echo "📋 Files ready for deployment:"
echo "- ✅ requirements.txt (updated)"
echo "- ✅ Procfile (Heroku/Railway)"
echo "- ✅ runtime.txt (Python version)"
echo "- ✅ app_deploy.py (deployment app)"
echo "- ✅ Dockerfile (container)"
echo "- ✅ DEPLOYMENT.md (full guide)"
echo ""
echo "🎯 Next steps:"
echo "1. Push code to GitHub"
echo "2. Choose hosting platform"
echo "3. Deploy and enjoy!"
echo ""
echo "📖 Full deployment guide: cat DEPLOYMENT.md"
