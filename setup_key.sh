#!/bin/bash

# Setup script to configure your API key

echo "=========================================="
echo "  Turing Test Gameshow - Setup"
echo "=========================================="
echo ""
echo "This script will help you set up your API key."
echo ""

# Check if .env already exists and has a key
if [ -f .env ] && grep -q "LITELLM_API_KEY=sk-" .env 2>/dev/null; then
    echo "✅ .env file already exists with an API key."
    echo ""
    read -p "Do you want to replace it? (y/N): " replace
    if [[ ! $replace =~ ^[Yy]$ ]]; then
        echo "Keeping existing API key."
        exit 0
    fi
fi

echo ""
read -p "Enter your LiteLLM API key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Write to .env file
echo "LITELLM_API_KEY=$api_key" > .env

echo ""
echo "✅ API key saved to .env file!"
echo ""
echo "Next steps:"
echo "  1. Test the connection: python test_ai.py"
echo "  2. Start the gameshow: ./start.sh"
echo ""
