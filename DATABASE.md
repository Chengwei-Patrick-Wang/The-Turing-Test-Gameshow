# Database & Few-Shot Learning Feature

## Overview

The Turing Test Gameshow now includes a database that stores all game rounds and uses them for **few-shot learning** to help the AI bots improve over time!

## How It Works

### 1. **Data Storage**
After each round completes, all answers (both AI and human) are automatically stored in a SQLite database (`game_history.db`).

Each entry contains:
- **Question asked** - The AI-generated question for that round
- **Answer given** - The response text
- **Is AI** - Whether this was from an AI bot or human player
- **AI Model** - Which model generated it (Opus 4 or Sonnet 4) if applicable
- **Round number** - Auto-incrementing round ID

### 2. **Few-Shot Learning**
When generating answers, each AI bot receives 10 random examples from past rounds to learn from:

- **Distinct Samples**: Each bot gets different examples (Bot 0 and Bot 1 see different past answers)
- **Excluding Current Round**: The current round's data is excluded from examples
- **Learning from Mistakes**: Bots can see both successful human-like answers and their own past attempts

### 3. **Automatic Process**
Everything happens automatically:
1. ✅ Round completes → Stored in database
2. ✅ New round starts → Bots receive 10 past examples each
3. ✅ Bots generate answers using few-shot learning
4. ✅ Cycle repeats, improving over time

## Database Schema

```sql
-- Tracks each game round
CREATE TABLE rounds (
    round_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stores all answers from all rounds
CREATE TABLE answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    is_ai BOOLEAN NOT NULL,
    ai_model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (round_id) REFERENCES rounds (round_id)
);
```

## API Endpoints

### Store Round
```
POST /store_round
```
**Body:**
```json
{
  "question": "What's your favorite color?",
  "answers": [
    {"answer": "Blue because sky", "is_ai": true, "ai_model": "Opus 4"},
    {"answer": "Red is best", "is_ai": false, "ai_model": null}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "round_id": 1,
  "stats": {
    "total_rounds": 1,
    "total_answers": 2,
    "ai_answers": 1,
    "human_answers": 1
  }
}
```

### Get Database Stats
```
GET /database_stats
```

**Response:**
```json
{
  "total_rounds": 10,
  "total_answers": 40,
  "ai_answers": 20,
  "human_answers": 20
}
```

### Generate Answer (Updated)
```
POST /generate_answer
```
**Body:**
```json
{
  "prompt": "What's your favorite food?",
  "bot_index": 0,
  "current_round_id": 5
}
```

**Response:**
```json
{
  "answer": "Pizza because cheese is life",
  "model": "Opus 4",
  "examples_used": 10
}
```

## Testing the Database

### Run Database Tests
```bash
source .venv/bin/activate
python test_database.py
```

This will:
- ✅ Initialize the database
- ✅ Store test rounds
- ✅ Retrieve random samples
- ✅ Test distinct samples for each bot
- ✅ Show formatted examples

### Check Database Stats
While the game is running, you can check stats:

```bash
curl http://localhost:5000/database_stats
```

### View Database Directly
```bash
sqlite3 game_history.db "SELECT * FROM rounds LIMIT 5;"
sqlite3 game_history.db "SELECT question, answer, is_ai FROM answers LIMIT 10;"
```

## Files Added/Modified

### New Files:
- **`database.py`** - Database module with all CRUD operations
- **`test_database.py`** - Test script for database functionality
- **`game_history.db`** - SQLite database (auto-created)

### Modified Files:
- **`ai_service.py`** - Added database integration and few-shot learning
- **`server.js`** - Added round storage after completion

## How Bots Learn

### Before Database:
```
Prompt to Bot:
"You are a contestant in a party game. Answer this question:
What's your favorite food?"
```

### After Database:
```
Prompt to Bot:
"You are a contestant in a party game.

Here are 10 examples from past rounds:

Example 1 (Round 3, Human):
Q: What's the best pizza topping?
A: Pineapple because it's controversial

Example 2 (Round 5, Sonnet 4):
Q: What superpower would you want?
A: Flying because traffic sucks

... [8 more examples] ...

Now answer this question:
What's your favorite food?"
```

## Benefits

1. **Continuous Improvement**: Bots learn what makes answers sound human
2. **Style Consistency**: See patterns in successful answers
3. **Diverse Examples**: Learn from both AI and human responses
4. **Distinct Learning**: Each bot gets different examples to develop unique styles
5. **Data Collection**: Build a dataset for future analysis

## Monitoring

Watch the Python AI service terminal to see:
- Number of examples used per generation
- Database storage confirmations
- Current database statistics

Example output:
```
Generated answer from Opus 4 using 10 past examples
✅ Stored round 15 in database
   Database stats: 15 rounds, 60 answers
```

## Limitations & Future Improvements

### Current:
- Random sampling (not intelligent selection)
- Fixed sample size of 10
- No quality filtering

### Potential Improvements:
- **Smart Selection**: Choose most human-like past answers
- **Adaptive Sampling**: More examples when struggling
- **Quality Metrics**: Track which examples lead to success
- **Temporal Awareness**: Weight recent examples more heavily
- **Category-Based**: Sample similar question types

## Database Management

### Reset Database
```bash
rm game_history.db
python test_database.py  # Will recreate with test data
```

### Backup Database
```bash
cp game_history.db game_history_backup_$(date +%Y%m%d).db
```

### Clear Database
```bash
sqlite3 game_history.db "DELETE FROM answers; DELETE FROM rounds;"
```

## Privacy Note

The database stores all answers including human responses. If running in a production environment with real users, consider:
- Adding data retention policies
- Implementing user consent
- Anonymizing stored data
- Adding encryption for sensitive content

---

**Enjoy watching your AI bots learn and improve! 🤖📚**
