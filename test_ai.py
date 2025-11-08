"""
Test script for AI Service
Run this to verify your LiteLLM connection works
"""

import openai
import os
import sys

def test_connection():
    """Test the LiteLLM connection"""
    
    api_key = os.environ.get('LITELLM_API_KEY', '')
    
    if not api_key:
        print("❌ ERROR: LITELLM_API_KEY environment variable not set!")
        print("\nPlease set it:")
        print("  export LITELLM_API_KEY='your-key-here'")
        return False
    
    print("✅ API Key found")
    print(f"   Key starts with: {api_key[:10]}...")
    
    print("\n🔗 Testing connection to AI Gateway...")
    
    try:
        llm = openai.OpenAI(
            api_key=api_key,
            base_url="https://ai-gateway.andrew.cmu.edu/",
            max_retries=2,
            timeout=30.0
        )
        
        # Test with a simple prompt
        print("\n🤖 Testing Claude Opus 4...")
        response = llm.chat.completions.create(
            model='claude-opus-4-20250514-v1:0',
            messages=[
                {"role": "user", "content": "Say 'Hello from Opus 4!' and nothing else."}
            ],
            max_tokens=50
        )
        
        opus_response = response.choices[0].message.content
        print(f"   Response: {opus_response}")
        
        print("\n🤖 Testing Claude Sonnet 4...")
        response = llm.chat.completions.create(
            model='claude-sonnet-4-20250514-v1:0',
            messages=[
                {"role": "user", "content": "Say 'Hello from Sonnet 4!' and nothing else."}
            ],
            max_tokens=50
        )
        
        sonnet_response = response.choices[0].message.content
        print(f"   Response: {sonnet_response}")
        
        print("\n✅ SUCCESS! Both models are working correctly!")
        print("\nYou can now run the gameshow:")
        print("  ./start.sh")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("  1. Check your API key is correct")
        print("  2. Verify you have access to these models")
        print("  3. Check your internet connection")
        return False

if __name__ == '__main__':
    print("="*50)
    print("  LiteLLM Connection Test")
    print("="*50)
    print()
    
    success = test_connection()
    sys.exit(0 if success else 1)
