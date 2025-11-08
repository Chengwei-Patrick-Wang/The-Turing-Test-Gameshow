# Quick Setup Guide

## First Time Setup

1. **Set your API key** (you only need to do this once):
   ```bash
   export LITELLM_API_KEY='your-litellm-key-here'
   
   # Add to your shell config to make it permanent:
   echo 'export LITELLM_API_KEY="your-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Test the connection**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python test_ai.py
   ```
   
   You should see "SUCCESS! Both models are working correctly!"

3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

## Running the Gameshow

### Easy Way (Recommended)
```bash
./start.sh
```

Then open: http://localhost:3000

### Manual Way (Two Terminals)

**Terminal 1 - AI Service:**
```bash
source venv/bin/activate
python ai_service.py
```

**Terminal 2 - Game Server:**
```bash
node server.js
```

## Current AI Configuration

- **Question Generator**: Claude Opus 4
- **Bot 1**: Claude Opus 4 (creative, high quality)
- **Bot 2**: Claude Sonnet 4 (balanced, efficient)

## Stopping the Services

Press `Ctrl+C` in the terminal where you ran `./start.sh`

Or manually kill processes:
```bash
# Find processes
lsof -i :3000  # Game server
lsof -i :5000  # AI service

# Kill them
kill <PID>
```

## Troubleshooting

**"AI Service failed to start"**
- Check API key: `echo $LITELLM_API_KEY`
- Run test: `python test_ai.py`

**"Port already in use"**
```bash
# For port 3000
lsof -ti:3000 | xargs kill -9

# For port 5000
lsof -ti:5000 | xargs kill -9
```

**"Module not found"**
```bash
# Python
source venv/bin/activate
pip install -r requirements.txt

# Node.js
npm install
```

## API Endpoints

The Python AI service exposes these endpoints:

- `GET /health` - Health check
- `POST /generate-prompt` - Generate a game question
- `POST /generate-answer` - Generate one AI answer
- `POST /generate-batch-answers` - Generate multiple AI answers

You can test them manually:
```bash
# Health check
curl http://localhost:5000/health

# Generate a question
curl -X POST http://localhost:5000/generate-prompt \
  -H "Content-Type: application/json"
```

## Files Overview

- `server.js` - Main game server (Node.js)
- `ai_service.py` - AI integration service (Python)
- `public/index.html` - Game UI
- `start.sh` - Startup script
- `test_ai.py` - Connection test script
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
