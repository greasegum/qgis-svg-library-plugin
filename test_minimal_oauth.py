#!/usr/bin/env python3
"""
Minimal test to find the exact issue
"""

import requests
from requests_oauthlib import OAuth1
import json

api_key = "e6b1100db018427482300dc87cf31117"
api_secret = "ebf7f2fa53974daea57035822ec65a90"

auth = OAuth1(api_key, api_secret)

# Test exactly what works
tests = [
    ("https://api.thenounproject.com/v2/icon?query=computer&limit=5&thumbnail_size=84", "With thumbnail_size"),
    ("https://api.thenounproject.com/v2/icon?query=computer&limit=5", "Without thumbnail_size"),
    ("https://api.thenounproject.com/v2/icon?query=computer", "Just query"),
]

print("Finding exact working format...")
print("=" * 60)

for url, desc in tests:
    print(f"\n{desc}:")
    print(f"URL: {url}")

    response = requests.get(url, auth=auth, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS - Found {len(data.get('icons', []))} icons")
        if data.get('icons'):
            icon = data['icons'][0]
            print(f"  First: {icon.get('term')} (ID: {icon.get('id')})")
            print(f"  Thumbnail: {icon.get('thumbnail', 'N/A')}")
    else:
        print(f"✗ FAILED - {response.status_code}")