# Quick Setup Guide for Turing Test Gameshow

## Step 1: Add Your LiteLLM API Key

Edit the `.env` file and replace `your_litellm_key_here` with your actual API key:

```bash
# Open .env in your editor
nano .env

# Or use VS Code
code .env
```

The file should look like:
```
LITELLM_API_KEY=sk-your-actual-key-here
```

## Step 2: Test the Connection

Run the test script to verify your API key works:

```bash
source .venv/bin/activate
python test_litellm.py
```

You should see:
```
✅ API Key found in .env file
Testing claude-opus-4-20250514-v1:0...
✅ claude-opus-4-20250514-v1:0 working!
   Response: ...
```

## Step 3: Start the Game

### Option A: Easy Start (Recommended)
```bash
./start.sh
```

### Option B: Manual Start

**Terminal 1:**
```bash
source .venv/bin/activate
python ai_service.py
```

**Terminal 2:**
```bash
node server.js
```

## Step 4: Play!

Open your browser to: **http://localhost:3000**

## Troubleshooting

### "Module not found" errors
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### API key errors
- Make sure your `.env` file has the correct key
- Check that you're using the right key format for LiteLLM
- Verify the key has access to Claude Opus 4 and Sonnet 4

### Port already in use
If port 3000 or 5000 is already in use:
- Kill existing processes: `lsof -ti:3000 | xargs kill -9`
- Or change the port in `server.js` (PORT variable) or `ai_service.py` (app.run)

### AI Service connection errors
- Ensure AI service is running on http://localhost:5000
- Check firewall settings
- Try: `curl http://localhost:5000/health`

## What Each File Does

- **ai_service.py** - Python Flask server that talks to LiteLLM
- **server.js** - Node.js game server with WebSocket support
- **public/index.html** - The game's web interface
- **test_litellm.py** - Test script to verify API connection
- **start.sh** - Startup script that runs everything

## Making Changes

### Change AI Models
Edit `ai_service.py` lines 20-21:
```python
OPUS_4_MODEL = "your-preferred-model"
SONNET_4_MODEL = "your-other-model"
```

### Change Bot Names
Edit `server.js` line 153:
```javascript
const botNames = ['Your Name 1', 'Your Name 2'];
```

### Change Prompting Style
Edit the system prompts in `ai_service.py`:
- Line 50: Prompt generation instructions
- Line 110: Answer generation instructions

Enjoy the game! 🎮🤖
