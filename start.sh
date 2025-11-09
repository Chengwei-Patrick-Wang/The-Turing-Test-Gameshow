#!/bin/bash

# Turing Test Gameshow - Startup Script

echo "🎮 Starting Turing Test Gameshow..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file with your LITELLM_API_KEY"
    echo "See .env.example for reference"
    exit 1
fi

# Start AI Service in background
echo "🤖 Starting AI Service (Python Flask)..."
python ai_service.py &
AI_PID=$!
echo "AI Service running on http://localhost:5000 (PID: $AI_PID)"

# Wait for AI service to be ready
echo "Waiting for AI Service to be ready..."
sleep 3

# Start Node.js server
echo "🌐 Starting Game Server (Node.js)..."
node server.js &
NODE_PID=$!
echo "Game Server running on http://localhost:3000 (PID: $NODE_PID)"

echo ""
echo "✅ Both services are running!"
echo "🎮 Open http://localhost:3000 in your browser to play!"
echo ""
echo "Press Ctrl+C to stop all services..."

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
