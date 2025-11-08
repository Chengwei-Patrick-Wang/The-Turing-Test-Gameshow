#!/bin/bash

# Turing Test Gameshow - Startup Script
# This script starts both the Python AI service and the Node.js game server

echo "=========================================="
echo "  Turing Test Gameshow - Starting Up"
echo "=========================================="

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Load NVM if it exists
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check if node is available now
if ! command -v node &> /dev/null; then
    echo ""
    echo "❌ ERROR: Node.js not found!"
    echo "Please install Node.js or activate your Node environment."
    echo "If you use nvm, run: source ~/.nvm/nvm.sh"
    exit 1
fi

# Check if LITELLM_API_KEY is set
if [ -z "$LITELLM_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: LITELLM_API_KEY is not set!"
    echo "Please add your key to the .env file:"
    echo "  echo 'LITELLM_API_KEY=your-key-here' > .env"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit and set the key..."
else
    echo "✅ API Key loaded successfully"
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating Python environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -q -r requirements.txt

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start Python AI service in background
echo ""
echo "🤖 Starting AI Service (Python) on port 5000..."
python ai_service.py &
AI_PID=$!

# Wait a moment for AI service to start
sleep 3

# Check if AI service is running
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "❌ AI Service failed to start!"
    kill $AI_PID 2>/dev/null
    exit 1
fi

echo "✅ AI Service is running (PID: $AI_PID)"

# Start Node.js game server
echo ""
echo "🎮 Starting Game Server (Node.js) on port 3000..."
echo ""
echo "=========================================="
echo "  🎉 Gameshow is ready!"
echo "  Open: http://localhost:3000"
echo "  AI Service: http://localhost:5000"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to clean up
trap "echo ''; echo 'Stopping services...'; kill $AI_PID 2>/dev/null; exit" INT TERM

# Start Node.js server (this will block)
node server.js

# Cleanup (in case node exits)
kill $AI_PID 2>/dev/null
