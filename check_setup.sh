#!/bin/bash

# Step-by-step manual startup guide

echo "=================================================="
echo "🎮 TURING TEST GAMESHOW - STARTUP GUIDE"
echo "=================================================="
echo ""

echo "📋 PREREQUISITES CHECK:"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ Python3: NOT FOUND"
fi

# Check Node
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js: NOT FOUND"
    echo ""
    echo "📦 TO INSTALL NODE.JS:"
    echo "   Option 1 - Using Homebrew (recommended for macOS):"
    echo "      brew install node"
    echo ""
    echo "   Option 2 - Download from:"
    echo "      https://nodejs.org/"
    echo ""
fi

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file: EXISTS"
else
    echo "❌ .env file: NOT FOUND"
    echo "   Create .env with: LITELLM_API_KEY=your_key_here"
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✅ Node modules: INSTALLED"
else
    echo "⚠️  Node modules: NOT INSTALLED"
    echo "   Run: npm install"
fi

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "✅ Python venv: EXISTS"
else
    echo "⚠️  Python venv: NOT FOUND"
fi

echo ""
echo "=================================================="
echo "📝 STARTUP INSTRUCTIONS:"
echo "=================================================="
echo ""
echo "STEP 1: Install Node.js (if not installed)"
echo "   brew install node"
echo "   OR download from https://nodejs.org/"
echo ""
echo "STEP 2: Install Node dependencies"
echo "   npm install"
echo ""
echo "STEP 3: Start AI Service (Terminal 1)"
echo "   source .venv/bin/activate"
echo "   python ai_service.py"
echo ""
echo "STEP 4: Start Game Server (Terminal 2)"
echo "   node server.js"
echo ""
echo "STEP 5: Open Browser"
echo "   http://localhost:3000"
echo ""
echo "=================================================="
echo ""
