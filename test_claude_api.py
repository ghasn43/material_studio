#!/usr/bin/env python3
"""Test script to verify Claude API is working correctly."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, RateLimitError

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment!")
    exit(1)

print(f"API Key found: {api_key[:20]}...")

# Initialize client
try:
    client = Anthropic(api_key=api_key)
    print("✓ Anthropic client initialized successfully")
except Exception as e:
    print(f"✗ Error initializing client: {e}")
    exit(1)

# Test API call
test_prompt = "Return this JSON only: {\"test\": \"success\"}"
print(f"\nCalling Claude with test prompt...")
print(f"Prompt: {test_prompt}")

# Try different model names
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet",
    "claude-3.5-sonnet-20241022",
    "claude-3.5-sonnet",
    "claude-opus-4-1",
    "claude-opus",
]

response = None
for model in models_to_try:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": test_prompt}
            ]
        )
        print(f"✓ Successfully used model: {model}")
        break
    except Exception as e:
        if "not_found" in str(e).lower():
            print(f"  Model '{model}' not found, trying next...")
            continue
        raise

try:
    if response:
        pass
    else:
        raise Exception("No response from any model")
    
    print("✓ API call successful!")
    print(f"Response: {response.content[0].text}")
    
except Exception as e:
    print(f"✗ Error calling API: {type(e).__name__}")
    print(f"Message: {e}")
    exit(1)

print("\n✓ All tests passed!")
