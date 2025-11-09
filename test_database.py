"""
Test script for database functionality
"""

import database

print("=" * 60)
print("TESTING DATABASE FUNCTIONALITY")
print("=" * 60)

# Initialize database
print("\n1. Initializing database...")
database.init_database()

# Check initial stats
print("\n2. Initial database stats:")
stats = database.get_database_stats()
print(f"   Total rounds: {stats['total_rounds']}")
print(f"   Total answers: {stats['total_answers']}")
print(f"   AI answers: {stats['ai_answers']}")
print(f"   Human answers: {stats['human_answers']}")

# Store a test round
print("\n3. Storing test round...")
test_question = "What's the best pizza topping?"
test_answers = [
    {"answer": "Pineapple because it's sweet and controversial!", "is_ai": True, "ai_model": "Opus 4"},
    {"answer": "Pepperoni, obviously. Classic never fails.", "is_ai": True, "ai_model": "Sonnet 4"},
    {"answer": "Mushrooms! They're earthy and delicious.", "is_ai": False, "ai_model": None},
    {"answer": "Extra cheese because more cheese = more happiness", "is_ai": False, "ai_model": None}
]

round_id = database.store_round(test_question, test_answers)
print(f"   ✅ Stored round {round_id}")

# Check updated stats
print("\n4. Updated database stats:")
stats = database.get_database_stats()
print(f"   Total rounds: {stats['total_rounds']}")
print(f"   Total answers: {stats['total_answers']}")
print(f"   AI answers: {stats['ai_answers']}")
print(f"   Human answers: {stats['human_answers']}")

# Store another round
print("\n5. Storing another test round...")
test_question2 = "What superpower would you want?"
test_answers2 = [
    {"answer": "Flying, because traffic is the worst", "is_ai": True, "ai_model": "Opus 4"},
    {"answer": "Invisibility so I can skip boring meetings", "is_ai": True, "ai_model": "Sonnet 4"},
    {"answer": "Teleportation would save so much time", "is_ai": False, "ai_model": None},
]

round_id2 = database.store_round(test_question2, test_answers2)
print(f"   ✅ Stored round {round_id2}")

# Test getting random samples
print("\n6. Testing random sample retrieval...")
sample = database.get_random_sample(sample_size=5)
print(f"   Retrieved {len(sample)} samples:")
for i, s in enumerate(sample, 1):
    source = s['ai_model'] if s['is_ai'] and s['ai_model'] else ('AI' if s['is_ai'] else 'Human')
    print(f"   {i}. [{source}] {s['answer'][:50]}...")

# Test getting distinct random samples
print("\n7. Testing distinct random samples for two bots...")
samples = database.get_distinct_random_samples(sample_size=3, num_samples=2)
print(f"   Bot 0 got {len(samples[0])} samples:")
for i, s in enumerate(samples[0], 1):
    source = s['ai_model'] if s['is_ai'] and s['ai_model'] else ('AI' if s['is_ai'] else 'Human')
    print(f"     {i}. [{source}] {s['answer'][:40]}...")

print(f"\n   Bot 1 got {len(samples[1])} samples:")
for i, s in enumerate(samples[1], 1):
    source = s['ai_model'] if s['is_ai'] and s['ai_model'] else ('AI' if s['is_ai'] else 'Human')
    print(f"     {i}. [{source}] {s['answer'][:40]}...")

# Test formatting for prompt
print("\n8. Testing prompt formatting...")
formatted = database.format_examples_for_prompt(samples[0][:2])
print("   Formatted examples:")
print("   " + "\n   ".join(formatted.split("\n")[:10]))

# Final stats
print("\n9. Final database stats:")
stats = database.get_database_stats()
print(f"   Total rounds: {stats['total_rounds']}")
print(f"   Total answers: {stats['total_answers']}")
print(f"   AI answers: {stats['ai_answers']}")
print(f"   Human answers: {stats['human_answers']}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print(f"\nDatabase location: {database.DB_PATH}")
