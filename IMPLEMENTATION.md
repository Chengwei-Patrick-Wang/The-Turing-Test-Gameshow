# Implementation Summary

## What Changed

### Old Architecture
```
Browser <--> Node.js Server <--> Ollama (Local)
                                   └── gpt-oss:120b-cloud
```

### New Architecture
```
Browser <--> Node.js Server <--> Python AI Service <--> LiteLLM/CMU Gateway
             (Socket.IO)          (Flask REST API)        ├── Claude Opus 4
             Port 3000            Port 5000               └── Claude Sonnet 4
```

## New Files Created

1. **`ai_service.py`** - Python Flask service that handles AI generation
   - `/generate-prompt` - Creates game questions using Opus 4
   - `/generate-batch-answers` - Gets answers from both bots
   - Uses OpenAI SDK with LiteLLM endpoint

2. **`requirements.txt`** - Python dependencies
   - flask==3.0.0
   - flask-cors==4.0.0
   - openai==1.12.0

3. **`start.sh`** - Unified startup script
   - Sets up Python venv
   - Installs dependencies
   - Starts both services
   - Handles cleanup on exit

4. **`test_ai.py`** - Connection test utility
   - Verifies API key works
   - Tests both Claude models
   - Provides helpful error messages

5. **`README.md`** - Comprehensive documentation
6. **`SETUP.md`** - Quick reference guide
7. **`.env.example`** - Environment variable template

## Modified Files

### `server.js`
**Lines 43-119** - Replaced Ollama integration with AI Service integration

**Before:**
```javascript
async function ollamaGenerate(prompt) {
  // Called Ollama API at localhost:11434
}
```

**After:**
```javascript
async function generatePrompt() {
  // Calls Python service at localhost:5000
  const res = await fetch(`${AI_SERVICE_URL}/generate-prompt`, ...);
}

async function generateBotAnswers(room) {
  // Batch request to Python service
  const res = await fetch(`${AI_SERVICE_URL}/generate-batch-answers`, ...);
}
```

## How It Works

### Starting a Round

1. Player clicks "Start New Round"
2. Node.js server receives `start_round` event
3. Server calls Python service `/generate-prompt`
4. Python service uses **Claude Opus 4** to create question
5. Question sent back to Node.js server
6. Server calls `/generate-batch-answers` with bot IDs
7. Python service generates answers:
   - Bot 0 → **Claude Opus 4**
   - Bot 1 → **Claude Sonnet 4**
8. Answers sent to all players

### Data Flow Example

```
Client                Node.js              Python Service        LiteLLM
  |                      |                       |                  |
  |--start_round-------->|                       |                  |
  |                      |--POST /generate-prompt>|                  |
  |                      |                       |--Opus 4 request-->|
  |                      |                       |<---question-------|
  |                      |<----question----------|                  |
  |                      |--POST /batch-answers->|                  |
  |                      |                       |--Opus 4 answer--->|
  |                      |                       |<---answer---------|
  |                      |                       |--Sonnet 4 answer->|
  |                      |                       |<---answer---------|
  |                      |<----both answers------|                  |
  |<--round_started------|                       |                  |
```

## Bot Model Assignment

The system identifies which model to use based on bot ID:

```python
BOT_MODELS = {
    'bot-0': 'claude-opus-4-20250514-v1:0',    # First bot
    'bot-1': 'claude-sonnet-4-20250514-v1:0'   # Second bot
}

def get_model_for_bot(bot_id):
    # "bot-ABC123-0" -> uses bot-0 model (Opus 4)
    # "bot-ABC123-1" -> uses bot-1 model (Sonnet 4)
```

## Environment Setup

Required environment variable:
```bash
LITELLM_API_KEY=your-key-here
```

This key is used by the Python service to authenticate with the CMU AI Gateway.

## Error Handling

- If AI service is down, game shows error message
- If one bot fails, other bot's answer still works
- Health check endpoint for monitoring: `http://localhost:5000/health`

## Testing

1. **Test AI connection:**
   ```bash
   python test_ai.py
   ```

2. **Test AI service manually:**
   ```bash
   # Start service
   python ai_service.py
   
   # In another terminal
   curl http://localhost:5000/health
   curl -X POST http://localhost:5000/generate-prompt
   ```

3. **Test full game:**
   ```bash
   ./start.sh
   # Open http://localhost:3000
   ```

## Advantages of This Approach

✅ **Keeps existing game logic** - Node.js server unchanged except AI calls
✅ **Leverages Python ecosystem** - Use familiar OpenAI SDK from notebook
✅ **Model flexibility** - Easy to swap models in one place
✅ **Better error handling** - Clear separation of concerns
✅ **Scalable** - Can add more bots or different models easily
✅ **Testable** - Can test AI service independently

## Future Enhancements

Possible improvements:
- Add model selection in UI
- Support more than 2 bots
- Add different "personalities" per bot
- Cache prompts/responses
- Add rate limiting
- Deploy to cloud service
