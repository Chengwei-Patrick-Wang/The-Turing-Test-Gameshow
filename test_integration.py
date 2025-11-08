"""
End-to-end integration test simulating a complete game round
Tests the flow: save data -> retrieve historical data -> use in prompts
"""

import requests
import json
import time
import sys

AI_SERVICE_URL = "http://localhost:5000"

def wait_for_service(max_retries=10):
    """Wait for the AI service to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{AI_SERVICE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✓ AI service is ready")
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"  Waiting for AI service... (attempt {i+1}/{max_retries})")
                time.sleep(1)
    return False

def test_integration():
    """Test the complete integration flow"""
    
    print("=" * 60)
    print("End-to-End Integration Test")
    print("=" * 60)
    
    # Check if service is running
    if not wait_for_service():
        print("\n❌ AI service is not running!")
        print("Please start it with: python ai_service.py")
        return False
    
    # Test 1: Get initial stats
    print("\n1. Getting initial database stats...")
    response = requests.get(f"{AI_SERVICE_URL}/stats")
    assert response.status_code == 200, f"Stats endpoint failed: {response.status_code}"
    stats = response.json()
    print(f"   ✓ Initial stats: {stats['stats']}")
    initial_rounds = stats['stats']['total_rounds']
    
    # Test 2: Save a few rounds to build history
    print("\n2. Saving sample rounds to build history...")
    sample_rounds = [
        {
            "prompt": "What's your spirit animal?",
            "responses": [
                {"text": "Probably a sloth because I'm lazy", "isAI": False, "authorId": "human-1"},
                {"text": "A majestic eagle soaring through the skies", "isAI": True, "authorId": "bot-1", "modelUsed": "claude-opus-4"}
            ]
        },
        {
            "prompt": "Best pizza topping?",
            "responses": [
                {"text": "Pineapple fight me", "isAI": False, "authorId": "human-2"},
                {"text": "I prefer classic pepperoni", "isAI": True, "authorId": "bot-2", "modelUsed": "claude-sonnet-4"}
            ]
        },
        {
            "prompt": "Worst movie you've ever seen?",
            "responses": [
                {"text": "The emoji movie was painful", "isAI": False, "authorId": "human-1"},
                {"text": "I found 'The Room' to be quite challenging", "isAI": True, "authorId": "bot-1", "modelUsed": "claude-opus-4"}
            ]
        }
    ]
    
    for round_data in sample_rounds:
        response = requests.post(
            f"{AI_SERVICE_URL}/save-round",
            json=round_data
        )
        assert response.status_code == 200, f"Save round failed: {response.status_code}"
        result = response.json()
        assert result['success'], f"Save round not successful: {result}"
        print(f"   ✓ Saved: '{round_data['prompt'][:40]}...'")
    
    # Test 3: Verify data was saved
    print("\n3. Verifying data was saved...")
    response = requests.get(f"{AI_SERVICE_URL}/stats")
    stats = response.json()
    new_rounds = stats['stats']['total_rounds']
    assert new_rounds == initial_rounds + 3, f"Expected {initial_rounds + 3} rounds, got {new_rounds}"
    print(f"   ✓ Database now has {new_rounds} rounds")
    print(f"   ✓ {stats['stats']['human_responses']} human responses")
    print(f"   ✓ {stats['stats']['ai_responses']} AI responses")
    
    # Test 4: Verify historical data is being used (we can't actually call the LLM without API key)
    print("\n4. Testing that historical context would be included...")
    import game_database as db
    historical = db.get_historical_data()
    context = db.format_historical_context(historical, max_examples=5)
    
    assert len(context) > 0, "Historical context should not be empty"
    assert "REAL HUMANS" in context, "Context should include human examples"
    assert "sloth" in context or "Pineapple" in context or "emoji" in context, "Context should include our saved data"
    print(f"   ✓ Historical context is {len(context)} characters")
    print(f"   ✓ Context includes human examples from saved rounds")
    
    # Show a sample of the context
    print("\n" + "-" * 60)
    print("Sample historical context that would be sent to AI:")
    print("-" * 60)
    print(context[:400] + "..." if len(context) > 400 else context)
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print("\nThe system is working correctly:")
    print("  • Rounds are being saved to the database")
    print("  • Historical data is being retrieved")
    print("  • Context is being formatted for AI prompts")
    print("  • AI bots will learn from human responses")
    
    return True

if __name__ == '__main__':
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
