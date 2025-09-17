#!/usr/bin/env python3
"""
Test The Noun Project API using requests library as recommended in docs
"""

import sys
import json

# Try using requests as recommended in the documentation
try:
    import requests
    from requests_oauthlib import OAuth1
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("requests-oauthlib not installed")
    print("Install with: pip install requests requests-oauthlib")

def test_with_requests():
    """Test using the recommended library"""
    if not HAS_REQUESTS:
        print("Cannot test - missing requests-oauthlib")
        return False

    # Your credentials
    api_key = "e6b1100db018427482300dc87cf31117"
    api_secret = "ebf7f2fa53974daea57035822ec65a90"

    print("Testing The Noun Project API with requests-oauthlib")
    print("=" * 60)
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Secret: {api_secret[:8]}...{api_secret[-4:]}")
    print()

    # Create OAuth1 session
    auth = OAuth1(api_key, api_secret)

    # Test different endpoints
    endpoints = [
        ("https://api.thenounproject.com/v2/icon?query=computer&limit=5", "v2/icon with query"),
        ("https://api.thenounproject.com/icons/computer", "v1 /icons/{term}"),
        ("https://api.thenounproject.com/icon/1", "v1 /icon/{id}")
    ]

    for endpoint, description in endpoints:
        print(f"\nTesting: {description}")
        print(f"URL: {endpoint}")
        print("-" * 40)

        try:
            response = requests.get(endpoint, auth=auth, timeout=10)

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✓ SUCCESS!")
                data = response.json()

                # Print first result if available
                if 'icons' in data and data['icons']:
                    icon = data['icons'][0]
                    print(f"\nFirst icon:")
                    print(f"  ID: {icon.get('id')}")
                    print(f"  Term: {icon.get('term')}")
                elif 'icon' in data:
                    print(f"\nIcon:")
                    print(f"  ID: {data['icon'].get('id')}")
                    print(f"  Term: {data['icon'].get('term')}")
                else:
                    print(f"Response keys: {list(data.keys())[:5]}")

            elif response.status_code == 403:
                print("✗ 403 FORBIDDEN - Authentication failed")
                print(f"Response: {response.text[:200]}")
            elif response.status_code == 404:
                print("✗ 404 NOT FOUND - Invalid endpoint")
            else:
                print(f"✗ Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")

    return True

def test_our_implementation():
    """Test our manual OAuth implementation for comparison"""
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from icon_providers import IconProvider, SvgIcon, SearchResult
    import providers

    print("\n" + "=" * 60)
    print("Testing our OAuth implementation")
    print("=" * 60)

    provider = providers.NounProjectProvider()
    result = provider.search("computer", page=1, per_page=5)

    if result.icons:
        print(f"✓ Found {len(result.icons)} icons")
        for icon in result.icons[:3]:
            print(f"  - {icon.name}")
    else:
        print("✗ No results (authentication likely failed)")

if __name__ == "__main__":
    success = test_with_requests()
    if success:
        test_our_implementation()