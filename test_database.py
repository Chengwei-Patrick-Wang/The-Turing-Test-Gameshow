"""
Integration test for the historical data feature
Tests the complete flow of saving and using historical data
"""

import game_database as db
import json
import os

def test_database_integration():
    """Test the complete database integration"""
    
    print("=" * 60)
    print("Testing Historical Data Integration")
    print("=" * 60)
    
    # Clean up any existing test database
    if os.path.exists('gameshow.db'):
        os.remove('gameshow.db')
        print("\n✓ Cleaned up old test database")
    
    # Initialize database
    db.init_database()
    print("✓ Database initialized")
    
    # Test 1: Initial state
    print("\n1. Testing initial state...")
    stats = db.get_database_stats()
    assert stats['total_rounds'] == 0, "Should start with 0 rounds"
    assert stats['human_responses'] == 0, "Should start with 0 human responses"
    assert stats['ai_responses'] == 0, "Should start with 0 AI responses"
    print("   ✓ Initial state is correct")
    
    # Test 2: Save multiple rounds
    print("\n2. Saving multiple rounds...")
    test_rounds = [
        {
            'prompt': 'What is your favorite food?',
            'responses': [
                {'text': 'Pizza because cheese', 'isAI': False, 'authorId': 'human-1'},
                {'text': 'I enjoy pizza', 'isAI': True, 'authorId': 'bot-1', 'modelUsed': 'claude-opus-4'},
                {'text': 'Pizza is my favorite', 'isAI': True, 'authorId': 'bot-2', 'modelUsed': 'claude-sonnet-4'}
            ]
        },
        {
            'prompt': 'Describe your perfect day',
            'responses': [
                {'text': 'Sleeping until noon', 'isAI': False, 'authorId': 'human-1'},
                {'text': 'A day at the beach', 'isAI': True, 'authorId': 'bot-1', 'modelUsed': 'claude-opus-4'},
                {'text': 'Reading books all day', 'isAI': True, 'authorId': 'bot-2', 'modelUsed': 'claude-sonnet-4'}
            ]
        },
        {
            'prompt': 'What would you do with a million dollars?',
            'responses': [
                {'text': 'Buy a house and invest the rest', 'isAI': False, 'authorId': 'human-1'},
                {'text': 'Travel the world', 'isAI': True, 'authorId': 'bot-1', 'modelUsed': 'claude-opus-4'}
            ]
        }
    ]
    
    for round_data in test_rounds:
        prompt_id = db.save_round_data(round_data['prompt'], round_data['responses'])
        print(f"   ✓ Saved round: '{round_data['prompt'][:40]}...' (ID: {prompt_id})")
    
    # Test 3: Check stats after saving
    print("\n3. Checking database stats...")
    stats = db.get_database_stats()
    assert stats['total_rounds'] == 3, f"Should have 3 rounds, got {stats['total_rounds']}"
    assert stats['human_responses'] == 3, f"Should have 3 human responses, got {stats['human_responses']}"
    assert stats['ai_responses'] == 5, f"Should have 5 AI responses, got {stats['ai_responses']}"
    print(f"   ✓ Stats are correct: {stats}")
    
    # Test 4: Retrieve historical data
    print("\n4. Retrieving historical data...")
    historical = db.get_historical_data(limit=10)
    assert len(historical['prompts']) == 3, f"Should have 3 prompts, got {len(historical['prompts'])}"
    assert len(historical['human_examples']) == 3, f"Should have 3 human examples, got {len(historical['human_examples'])}"
    assert len(historical['ai_examples']) == 5, f"Should have 5 AI examples, got {len(historical['ai_examples'])}"
    print(f"   ✓ Retrieved {len(historical['prompts'])} prompts")
    print(f"   ✓ Retrieved {len(historical['human_examples'])} human examples")
    print(f"   ✓ Retrieved {len(historical['ai_examples'])} AI examples")
    
    # Test 5: Format historical context
    print("\n5. Formatting historical context...")
    context = db.format_historical_context(historical, max_examples=5)
    assert len(context) > 0, "Context should not be empty"
    assert "REAL HUMANS" in context, "Context should mention real humans"
    assert "AI bots" in context, "Context should mention AI bots"
    print("   ✓ Context formatted correctly")
    print(f"   Context length: {len(context)} characters")
    
    # Test 6: Limit historical data
    print("\n6. Testing data limiting...")
    for i in range(20):
        db.save_round_data(
            f'Test question {i}',
            [
                {'text': f'Human answer {i}', 'isAI': False, 'authorId': f'human-{i}'},
                {'text': f'AI answer {i}', 'isAI': True, 'authorId': f'bot-{i}', 'modelUsed': 'test-model'}
            ]
        )
    
    stats = db.get_database_stats()
    print(f"   ✓ Total rounds in DB: {stats['total_rounds']}")
    
    # Retrieve with limit
    historical = db.get_historical_data(limit=15)
    assert len(historical['prompts']) == 15, f"Should limit to 15 prompts, got {len(historical['prompts'])}"
    print(f"   ✓ Correctly limited to {len(historical['prompts'])} most recent rounds")
    
    # Test 7: Sample context output
    print("\n7. Sample context output...")
    context = db.format_historical_context(historical, max_examples=3)
    print("\n" + "-" * 60)
    print("SAMPLE CONTEXT (first 500 chars):")
    print("-" * 60)
    print(context[:500])
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nFinal Database Stats:")
    print(f"  Total Rounds: {stats['total_rounds']}")
    print(f"  Human Responses: {stats['human_responses']}")
    print(f"  AI Responses: {stats['ai_responses']}")
    
    return True

if __name__ == '__main__':
    try:
        test_database_integration()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
