#!/bin/bash

# Turing Test Gameshow - Easy Startup Script with NVM support

echo "🎮 Starting Turing Test Gameshow..."
echo ""

# Load NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file with your LITELLM_API_KEY"
    exit 1
fi

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "🤖 Starting AI Service (Python)..."
source .venv/bin/activate
python ai_service.py &
AI_PID=$!
echo "   ✅ AI Service running on http://localhost:5000 (PID: $AI_PID)"

# Wait for AI service to be ready
sleep 3

echo "🌐 Starting Game Server (Node.js)..."
node server.js &
NODE_PID=$!
echo "   ✅ Game Server running on http://localhost:3000 (PID: $NODE_PID)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ GAME IS READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎮 Open in browser: http://localhost:3000"
echo ""
echo "🤖 AI Players:"
echo "   • Bot 0: Claude Opus 4"
echo "   • Bot 1: Claude Sonnet 4"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $AI_PID 2>/dev/null
    kill $NODE_PID 2>/dev/null
    echo "Goodbye!"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
