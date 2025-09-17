#!/usr/bin/env python3
"""
Debug OAuth signature generation
Run this in QGIS Python Console to see what's happening
"""

def debug_oauth():
    """Debug the OAuth signature generation"""
    print("\n" + "="*60)
    print("OAuth Signature Debug")
    print("="*60)

    import sys
    import os
    import base64

    # Find plugin
    home = os.path.expanduser('~')
    plugin_path = f"{home}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-svg-library-plugin-terragon-analyze-test-plugin"

    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)

    # Get the actual API keys
    from providers import TheNounProjectProvider
    provider = TheNounProjectProvider()

    print(f"\n1. API Keys:")
    print(f"   Key: {provider.api_key}")
    print(f"   Secret: {'*' * len(provider.secret)} ({len(provider.secret)} chars)")

    # Decode the base64 keys to check they're correct
    print(f"\n2. Checking base64 decoding:")
    try:
        key_decoded = base64.b64decode("ZTZiMTEwMGRiMDE4NDI3NDgyMzAwZGM4N2NmMzExMTc=").decode('utf-8')
        secret_decoded = base64.b64decode("ZWJmN2YyZmE1Mzk3NGRhZWE1NzAzNTgyMmVjNjVhOTA=").decode('utf-8')
        print(f"   Decoded key matches: {key_decoded == provider.api_key}")
        print(f"   Decoded secret matches: {secret_decoded == provider.secret}")
    except Exception as e:
        print(f"   Error decoding: {e}")

    print(f"\n3. Testing OAuth methods:")

    # Method 1: Try with requests-oauthlib if available
    try:
        import requests
        from requests_oauthlib import OAuth1

        print("\n   Method A: requests-oauthlib")
        auth = OAuth1(provider.api_key, client_secret=provider.secret)
        test_url = "https://api.thenounproject.com/icons/test"

        response = requests.get(test_url, auth=auth, params={'limit': '1'})
        print(f"   Response: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ OAuth working with requests-oauthlib!")
        else:
            print(f"   ✗ Failed: {response.text[:200]}")

    except ImportError:
        print("\n   Method A: requests-oauthlib not available")
    except Exception as e:
        print(f"   Error: {e}")

    # Method 2: Manual OAuth
    print("\n   Method B: Manual OAuth implementation")

    import time
    import hmac
    import hashlib
    import random
    import string
    from urllib.parse import quote, urlencode

    # Generate OAuth params
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = str(int(time.time()))

    oauth_params = {
        'oauth_consumer_key': provider.api_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestamp,
        'oauth_nonce': nonce,
        'oauth_version': '1.0'
    }

    # Test parameters
    query_params = {'limit': '1'}
    url = "https://api.thenounproject.com/icons/test"

    # Combine parameters
    all_params = {**query_params, **oauth_params}

    # Sort and encode
    def percent_encode(s):
        return quote(str(s), safe='~')

    sorted_params = sorted(all_params.items())
    param_string = '&'.join([f"{percent_encode(k)}={percent_encode(v)}" for k, v in sorted_params])

    # Create signature base
    signature_base = f"GET&{percent_encode(url)}&{percent_encode(param_string)}"

    print(f"\n   OAuth Parameters:")
    print(f"   Timestamp: {timestamp}")
    print(f"   Nonce: {nonce[:20]}...")
    print(f"\n   Signature base string (first 200 chars):")
    print(f"   {signature_base[:200]}...")

    # Create signing key - THIS IS THE CRITICAL PART
    signing_key = f"{provider.secret}&"

    # Generate signature
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')

    print(f"\n   Generated signature: {signature[:30]}...")

    # Create OAuth header
    oauth_params['oauth_signature'] = signature
    auth_header = 'OAuth ' + ', '.join([
        f'{k}="{percent_encode(v)}"' for k, v in oauth_params.items()
    ])

    print(f"\n   OAuth header (first 150 chars):")
    print(f"   {auth_header[:150]}...")

    # Test the request
    import urllib.request
    full_url = f"{url}?{urlencode(query_params)}"
    req = urllib.request.Request(full_url)
    req.add_header('Authorization', auth_header)

    try:
        response = urllib.request.urlopen(req, timeout=10)
        print(f"\n   ✓ Manual OAuth successful!")
    except urllib.error.HTTPError as e:
        print(f"\n   ✗ Manual OAuth failed: {e.code} {e.reason}")
        # Try to read error details
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Error details: {error_body[:200]}")
        except:
            pass

    print("\n" + "="*60)
    print("Recommendations:")
    print("="*60)

    try:
        import requests
        print("✓ requests-oauthlib is available - plugin should use it")
    except:
        print("✗ requests-oauthlib not installed")
        print("\nTo fix OAuth issues, install requests-oauthlib:")
        print("Run in QGIS Python Console:")
        print("exec(open(r'" + plugin_path + "/install_oauth_macos.py').read())")

    print("="*60)


if __name__ == "__main__":
    debug_oauth()