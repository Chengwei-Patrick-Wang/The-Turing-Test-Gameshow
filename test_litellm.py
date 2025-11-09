"""
Quick test script to verify LiteLLM connection via CMU AI Gateway
Uses requests library to avoid Python 3.14 compatibility issues
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

LITELLM_API_KEY = os.getenv('LITELLM_API_KEY')

if not LITELLM_API_KEY or LITELLM_API_KEY == 'your_litellm_key_here':
    print("❌ ERROR: LITELLM_API_KEY not set in .env file")
    print("Please edit .env and add your actual LiteLLM API key")
    exit(1)

print("✅ API Key found in .env file")
print(f"Key starts with: {LITELLM_API_KEY[:10]}...")
print()

# CMU AI Gateway endpoint
API_BASE_URL = "https://ai-gateway.andrew.cmu.edu/v1/chat/completions"

# Test models
models_to_test = [
    "claude-opus-4-20250514-v1:0",
    "claude-sonnet-4-20250514-v1:0"
]

test_prompt = "Say 'Hello, I am working!' in a fun way."

for model in models_to_test:
    print(f"Testing {model}...")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LITELLM_API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": test_prompt}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        answer = data['choices'][0]['message']['content'].strip()
        print(f"✅ {model} working!")
        print(f"   Response: {answer}")
        print()
    except Exception as e:
        print(f"❌ {model} failed!")
        print(f"   Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        print()

print("Testing complete!")
