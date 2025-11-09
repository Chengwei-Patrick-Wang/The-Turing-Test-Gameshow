# How to Run the Turing Test Gameshow

## ✅ Current Status
- ✅ AI Service is configured and working (Claude Opus 4 & Sonnet 4)
- ✅ Python dependencies installed
- ✅ API key configured

## 🚀 Quick Start (Manual Method - RECOMMENDED)

### Terminal 1: Start AI Service
```bash
cd /Users/ssura/Desktop/The-Turing-Test-Gameshow
source .venv/bin/activate
python ai_service.py
```

**Wait for this message:**
```
 * Running on http://127.0.0.1:5000
```

### Terminal 2: Start Game Server

Open a **NEW terminal window** and run:

```bash
cd /Users/ssura/Desktop/The-Turing-Test-Gameshow
node server.js
```

**If `node` command not found**, try:
```bash
# If using nvm
nvm use node
node server.js

# OR find node and use full path
/usr/local/bin/node server.js
```

**Wait for this message:**
```
Server running on http://localhost:3000
```

### Step 3: Open Browser
```
http://localhost:3000
```

---

## 🎮 How to Play

1. **Create a Room**
   - Enter your name
   - Click "Create Room"
   - Share the room code with friends

2. **Start Round**
   - Click "Start New Round"
   - The AI (Opus 4) will generate a wacky question
   - Both AI bots (Opus 4 and Sonnet 4) will submit answers automatically

3. **Submit Your Answer**
   - Type your answer in 1-3 sentences
   - Try to sound human!
   - Click "Submit Answer"

4. **Guess Which Are AI**
   - Once all humans answer, you'll see all answers shuffled
   - Click on each answer to mark it as "AI" or "Human"
   - Click "Submit Guesses"

5. **See Results**
   - View scores
   - See which answers were actually from AI
   - Start another round!

---

## 🔍 Verifying AIs Are Working

### Test 1: Check AI Service Health
```bash
curl http://localhost:5000/health
```
**Expected output:**
```json
{"models":["claude-opus-4-20250514-v1:0","claude-sonnet-4-20250514-v1:0"],"status":"healthy"}
```

### Test 2: Test Both AI Models
```bash
curl -X POST http://localhost:5000/test
```
**Expected:** You'll see responses from both Opus 4 and Sonnet 4

### Test 3: Run the Python Test Script
```bash
source .venv/bin/activate
python test_litellm.py
```
**Expected:**
```
✅ claude-opus-4-20250514-v1:0 working!
✅ claude-sonnet-4-20250514-v1:0 working!
```

---

## 🐛 Troubleshooting

### AI Service Issues

**Problem:** `LITELLM_API_KEY not found`
```bash
# Check your .env file
cat .env
# Should contain: LITELLM_API_KEY=sk-...
```

**Problem:** AI responses failing
```bash
# Test the connection
python test_litellm.py
```

### Game Server Issues

**Problem:** `node: command not found`
```bash
# Find node
which node

# OR install node via nvm or homebrew
brew install node
```

**Problem:** `Cannot connect to AI service`
- Make sure AI service is running on port 5000
- Check: `curl http://localhost:5000/health`

**Problem:** Port already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

---

## 📊 Monitor the AIs

Watch the AI Service terminal to see when it generates responses:

```
Generated answer from Opus 4
Generated answer from Sonnet 4
```

You'll see the actual API calls and responses in real-time!

---

## 🛑 Stopping the Services

Press `Ctrl+C` in each terminal window to stop the services.

---

## 💡 Tips for Best Results

1. **Ask clear questions** - The AI generates better questions when the prompt is specific
2. **Keep answers brief** - 1-2 sentences works best for the guessing game
3. **Watch the terminal** - You can see which AI model generated each answer
4. **Test first** - Always run `test_litellm.py` before starting a game session

---

## 🎯 Summary

**Two terminals needed:**
1. `python ai_service.py` (port 5000)
2. `node server.js` (port 3000)

**Open browser:**
- http://localhost:3000

**The AIs are working when:**
- AI service shows "Running on http://127.0.0.1:5000"
- Game shows "Opus 4" and "Sonnet 4" as players
- Questions are generated automatically
- AI answers appear after clicking "Start New Round"
