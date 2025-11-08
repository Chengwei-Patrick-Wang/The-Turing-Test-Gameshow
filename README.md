# Turing Test Gameshow 🎮🤖

A web-based gameshow where humans compete with AI contestants! Players answer whacky questions, then try to guess which answers were written by AI and which by humans.

## 🎯 Game Overview

1. **AI Host**: Claude Opus 4 generates creative and whacky questions
2. **AI Contestants**: 
   - Bot 1: Claude Opus 4 (claude-opus-4-20250514-v1:0)
   - Bot 2: Claude Sonnet 4 (claude-sonnet-4-20250514-v1:0)
3. **Human Players**: Try to blend in with AI answers or spot the AI!

## 🏗️ Architecture

The project consists of two services:

- **Node.js Game Server** (port 3000): Handles the game logic, rooms, and Socket.IO connections
- **Python AI Service** (port 5000): Interfaces with LiteLLM to generate questions and AI answers

## 📋 Prerequisites

- **Node.js** (v14 or higher)
- **Python 3** (v3.8 or higher)
- **LiteLLM API Key** (from CMU AI Gateway)

## 🚀 Quick Start

### 1. Set Your API Key (One Time Setup)

**Option A: Use the setup script (Easiest)**
```bash
./setup_key.sh
```

**Option B: Edit .env file manually**
```bash
# Edit the .env file and replace with your actual key
nano .env
```

Then change `your-litellm-api-key-here` to your actual key.

### 2. Run the Startup Script

```bash
./start.sh
```

This will:
- Load your API key from `.env`
- Create a Python virtual environment (if needed)
- Install all dependencies
- Start the AI service on port 5000
- Start the game server on port 3000

### 3. Open the Game

Navigate to: **http://localhost:3000**

## 🛠️ Manual Setup (Alternative)

If you prefer to run services separately:

### Terminal 1: AI Service
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export LITELLM_API_KEY='your-key-here'
python ai_service.py
```

### Terminal 2: Game Server
```bash
npm install
node server.js
```

## 🎮 How to Play

1. **Create/Join a Room**: Enter your name and create a new room or join with a room code
2. **Start Round**: The host can start a new round (AI generates a question)
3. **Answer**: All players (humans and AIs) answer the question
4. **Guess**: Humans guess which answers were written by AI
5. **Score**: 
   - 10 points for each correct guess
   - 5 points for each player you fool (if you're human and they guess you're AI)

## 🔧 Configuration

### Change AI Models

Edit `ai_service.py`:
```python
BOT_MODELS = {
    'bot-0': 'claude-opus-4-20250514-v1:0',      # Bot 1
    'bot-1': 'claude-sonnet-4-20250514-v1:0'     # Bot 2
}
```

Available models:
- `claude-opus-4-20250514-v1:0`
- `claude-sonnet-4-20250514-v1:0`
- `claude-3-5-sonnet-20241022`
- `claude-3-7-sonnet-20250219-v1:0`
- `gpt-4o-2024-08-06`
- `gemini-1.5-pro-002`
- `llama3-2-90b-instruct`
- And more...

### Adjust Number of Bots

Edit `server.js` (around line 163):
```javascript
const botCount = 2; // change to add more bots
```

## 📁 Project Structure

```
The-Turing-Test-Gameshow/
├── server.js              # Node.js game server
├── ai_service.py          # Python AI service
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── start.sh              # Startup script
├── public/
│   └── index.html        # Game UI
└── README.md             # This file
```

## 🐛 Troubleshooting

### AI Service Won't Start
- Check that your API key is set: `echo $LITELLM_API_KEY`
- Verify Python dependencies: `pip install -r requirements.txt`
- Check port 5000 is not in use: `lsof -i :5000`

### Game Server Won't Start
- Verify Node dependencies: `npm install`
- Check port 3000 is not in use: `lsof -i :3000`

### AI Answers Not Appearing
- Check AI service health: `curl http://localhost:5000/health`
- Look at terminal output for error messages
- Verify API key has access to the models

### Connection Issues
- Make sure both services are running
- Check browser console for errors (F12 → Console)
- Verify firewall isn't blocking ports 3000 or 5000

## 🎨 Customization Ideas

- Add more bot personalities by tweaking prompts in `ai_service.py`
- Customize question topics in the prompt generation
- Add different scoring rules
- Create themed rounds (e.g., "Dad Jokes", "Hot Takes", etc.)

## 📝 Notes

- The AI service uses the OpenAI-compatible API from LiteLLM
- Models are accessed through the CMU AI Gateway
- Each bot uses a different Claude model for variety
- The game uses Socket.IO for real-time communication

## 🙏 Credits

Built for educational purposes using:
- Express.js & Socket.IO
- Flask & OpenAI Python SDK
- Claude Opus 4 & Sonnet 4 via LiteLLM

Enjoy the game! 🎉
