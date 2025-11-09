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
# Ensure Python dependencies are installed in the venv
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Choose an AI service port. Port 5000 is the default but macOS sometimes
# has system services listening on 5000 (Control Center). If 5000 is busy,
# fall back to 5001 and export AI_SERVICE_URL so Node can find it.
AI_PORT=5000
if lsof -iTCP:${AI_PORT} -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "Port ${AI_PORT} is in use; starting AI service on 5001 instead"
    AI_PORT=5001
fi
export AI_SERVICE_PORT=${AI_PORT}
export AI_SERVICE_URL="http://localhost:${AI_PORT}"

# Start the AI service (it will pick up AI_SERVICE_PORT via environment)
.venv/bin/python ai_service.py &
AI_PID=$!
echo "   ✅ AI Service running on http://localhost:5000 (PID: $AI_PID)"

# Wait for AI service to be ready
sleep 3

echo "🌐 Starting Game Server (Node.js)..."
# Install Node dependencies if missing
if [ -f "package.json" ] && [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi
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
