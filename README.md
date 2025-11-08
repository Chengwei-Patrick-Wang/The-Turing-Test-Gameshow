# Turing Test Gameshow 🎮🤖

A web-based game show where humans compete against AI to see who can better imitate the other!

## Overview

In this game:
1. An AI (Claude Opus 4) generates a wacky question
2. Both humans and AI contestants (Claude Opus 4 and Sonnet 4) answer the question
3. Human players try to guess which answers were written by AI
4. Points are awarded for correct guesses and for fooling other players

## AI Models Used

- **Question Generator**: Claude Opus 4 (`claude-opus-4-20250514-v1:0`)
- **Bot 0 (Opus 4)**: Claude Opus 4 (`claude-opus-4-20250514-v1:0`)
- **Bot 1 (Sonnet 4)**: Claude Sonnet 4 (`claude-sonnet-4-20250514-v1:0`)

All models are accessed via LiteLLM API Gateway.

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- A LiteLLM API key

### Installation

1. **Clone the repository and navigate to it**
   ```bash
   cd The-Turing-Test-Gameshow
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Create and configure your environment file**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your LiteLLM API key:
   ```
   LITELLM_API_KEY=your_actual_key_here
   ```

4. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Running the Game

### Option 1: Use the startup script (Recommended for macOS/Linux)

```bash
chmod +x start.sh
./start.sh
```

This will start both the AI service and the game server automatically.

### Option 2: Manual startup

**Terminal 1 - Start the AI Service:**
```bash
source venv/bin/activate
python ai_service.py
```

**Terminal 2 - Start the Game Server:**
```bash
node server.js
```

### Access the Game

Open your browser and navigate to:
```
http://localhost:3000
```

## How to Play

1. **Create a Room**: Enter your name and create a new game room
2. **Share the Code**: Share the room code with other players
3. **Start Round**: Any player can start a new round
4. **Answer**: All human players submit their answers to the AI-generated question
5. **Guess**: Try to identify which answers were written by AI
6. **Score**: Get points for correct guesses and for fooling other players!

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (index.html)   │
└────────┬────────┘
         │ WebSocket
         │ (Socket.IO)
         ▼
┌─────────────────┐      HTTP      ┌──────────────────┐
│   Node.js       │◄──────────────►│  Python Flask    │
│   Server        │                │  AI Service      │
│  (server.js)    │                │ (ai_service.py)  │
└─────────────────┘                └────────┬─────────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │   LiteLLM      │
                                   │   API Gateway  │
                                   └────────────────┘
```

## Testing the AI Service

You can test if the AI models are working correctly:

```bash
curl -X POST http://localhost:5000/test
```

This will return responses from both Opus 4 and Sonnet 4.

## API Endpoints

### AI Service (Python - Port 5000)

- `GET /health` - Health check
- `POST /generate_prompt` - Generate a new question
- `POST /generate_answer` - Generate an AI answer
  - Body: `{ "prompt": "question", "bot_index": 0 or 1 }`
- `POST /test` - Test both AI models

### Game Server (Node.js - Port 3000)

- WebSocket events via Socket.IO
- Static files served from `/public`

## Troubleshooting

### AI Service won't start
- Check that your `LITELLM_API_KEY` is set in `.env`
- Verify Python dependencies are installed: `pip list | grep -E "flask|litellm"`

### Models not responding
- Test the AI service endpoint: `curl -X POST http://localhost:5000/test`
- Check the Python console for error messages
- Verify your LiteLLM API key has access to the Claude models

### Game server can't connect to AI service
- Ensure the AI service is running on port 5000
- Check for firewall issues blocking localhost connections

## Scoring System

- **Correct Guess**: 10 points per correct identification
- **Fooling Bonus**: 5 points for each player who mistakes your human answer for AI

## Development

### Project Structure

```
.
├── server.js              # Node.js game server (Socket.IO)
├── ai_service.py          # Python AI service (Flask + LiteLLM)
├── public/
│   └── index.html         # Frontend game interface
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── start.sh              # Startup script
└── .env                  # Environment variables (not in git)
```

### Adding More AI Models

Edit `ai_service.py` and update the model constants:

```python
OPUS_4_MODEL = "your-model-here"
SONNET_4_MODEL = "your-other-model-here"
```

Available LiteLLM models:
- claude-3-haiku-20240307
- gemini-1.5-pro-002
- claude-3-5-sonnet-20241022
- llama3-2-11b-instruct
- gpt-4o-2024-08-06
- And more...

## License

MIT

## Credits

Built with ❤️ using Node.js, Python, Flask, Socket.IO, and LiteLLM
