#!/usr/bin/env python
"""Test API key loading."""
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

print('API Key Loaded:', 'YES' if api_key else 'NO')
print('Key Length:', len(api_key) if api_key else 0)
if api_key:
    print('Starts with:', api_key[:30] + '...')
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    print('Anthropic Client: READY ✅')
    print('Successfully initialized Anthropic client with API key')
