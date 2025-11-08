# Bot Comparison: Old vs New

## Before (Ollama - gpt-oss:120b-cloud)

**Single Model for Everything:**
- Question generation: gpt-oss:120b-cloud
- Bot 1 answers: gpt-oss:120b-cloud  
- Bot 2 answers: gpt-oss:120b-cloud

**Characteristics:**
- Local model (fast, no API costs)
- Limited by local GPU/CPU
- Same "voice" for both bots
- Potential for repetitive patterns

## After (LiteLLM - Claude Opus 4 & Sonnet 4)

**Specialized Models:**
- Question generation: **Claude Opus 4** (most creative)
- Bot 1 answers: **Claude Opus 4** (high quality, creative)
- Bot 2 answers: **Claude Sonnet 4** (balanced, efficient)

**Characteristics:**
- Cloud-based (requires API key)
- State-of-the-art language models
- Different "personalities" between bots
- More variety in responses

## Expected Improvements

### 1. Question Quality
**Before:**
```
"What would you do if you saw a dinosaur?"
```

**After (Opus 4):**
```
"If you had to convince a T-Rex to become a vegetarian, 
what would be your opening argument?"
```

More creative, specific, and entertaining questions.

### 2. Answer Variety

**Before (Both bots sound similar):**
- Bot 1: "I would run away because dinosaurs are dangerous."
- Bot 2: "I would try to hide because dinosaurs can be scary."

**After (Different models, different styles):**
- Bot 1 (Opus): "I'd probably freeze like a deer in headlights because my flight instinct apparently needs to buffer first."
- Bot 2 (Sonnet): "Run to the nearest building because concrete walls > my cardio skills."

### 3. Human-likeness

The new models are better at:
- Using casual language
- Adding personality without overdoing it
- Avoiding "AI-ish" phrases
- Being genuinely funny in a natural way

## Model Characteristics

### Claude Opus 4
- **Strengths:** Creative, nuanced, great at humor
- **Weakness:** Can be slightly verbose
- **Best for:** Question generation, creative answers
- **Personality:** Witty, thoughtful, slightly sophisticated

### Claude Sonnet 4  
- **Strengths:** Balanced, efficient, clear
- **Weakness:** Slightly less creative than Opus
- **Best for:** Quick, punchy answers
- **Personality:** Direct, casual, relatable

## Why Two Different Models?

Having different models makes the game more interesting:

1. **Harder to Spot AI:** If both bots sound different, they're less obviously "bots"
2. **More Variety:** Players see diverse answer styles
3. **Better Competition:** Different approaches to fooling humans
4. **Learning Opportunity:** Players learn to recognize different AI styles

## Switching Back (If Needed)

If you want to use Ollama again or try other models:

**Edit `ai_service.py`:**
```python
# Use different LiteLLM models
BOT_MODELS = {
    'bot-0': 'gpt-4o-2024-08-06',           # GPT-4
    'bot-1': 'gemini-1.5-pro-002'           # Gemini
}

# Or use the same model for both
BOT_MODELS = {
    'bot-0': 'claude-3-5-sonnet-20241022',
    'bot-1': 'claude-3-5-sonnet-20241022'
}
```

**Or revert to Ollama in `server.js`:**
- Replace the AI service calls with the old Ollama code
- Change back to `http://localhost:11434/api/generate`

## Cost Considerations

### Ollama (Local)
- ✅ Free to use
- ✅ No rate limits
- ❌ Requires powerful local hardware
- ❌ Slower response times
- ❌ Limited model selection

### LiteLLM (Cloud via CMU Gateway)
- ✅ Access to best models
- ✅ Fast responses
- ✅ No local hardware needed
- ⚠️ May have usage limits (check your CMU allocation)
- ℹ️ Usually free for CMU students/research

## Testing the Difference

To see the improvement:

1. **Start a game with the new system:**
   ```bash
   ./start.sh
   ```

2. **Play a few rounds and note:**
   - How creative are the questions?
   - Do the bot answers feel different from each other?
   - Are they convincingly human-like?
   - Can you spot patterns?

3. **Compare answers side by side:**
   - Bot 1 (Opus 4): Usually more elaborate
   - Bot 2 (Sonnet 4): Usually more concise

## Available Alternative Models

If you want to experiment with other models:

**High Quality (Similar to Opus/Sonnet):**
- `claude-3-5-sonnet-20241022` - Previous Claude version
- `gpt-4o-2024-08-06` - OpenAI's best
- `gemini-1.5-pro-002` - Google's top model

**Faster/Cheaper:**
- `claude-3-7-sonnet-20250219-v1:0` - Newer Sonnet
- `gemini-1.5-flash-002` - Fast Gemini
- `claude-3-haiku-20240307` - Fast Claude

**Fun Experiments:**
- `llama3-2-90b-instruct` - Open source, large
- `llama3-2-11b-instruct` - Open source, smaller
- `deepseek-ai/deepseek-coder-v2-lite-instruct` - Code-focused

## Recommendation

**For best game experience:**
- Keep Opus 4 for questions (most creative)
- Try different combinations for bots:
  - Opus + Sonnet (current, good balance)
  - Opus + GPT-4o (both high-quality)
  - Sonnet + Gemini Flash (fast, diverse)

**For experimentation:**
- Use same model for both bots first
- Then try different combos
- See which pairing is hardest for humans to spot!
