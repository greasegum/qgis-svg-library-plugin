#!/usr/bin/env python3
"""
Debug OAuth implementation for The Noun Project API
"""

import sys
import os
import time
import hashlib
import hmac
import base64
import urllib.request
import urllib.error
from urllib.parse import urlencode, quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_oauth():
    """Test OAuth with minimal parameters"""

    # Credentials
    api_key = "e6b1100db018427482300dc87cf31117"
    api_secret = "ebf7f2fa53974daea57035822ec65a90"

    print("Testing The Noun Project OAuth 1.0a...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Secret: {api_secret[:8]}...{api_secret[-4:]}")
    print("=" * 60)

    # Simple endpoint without parameters
    base_url = "https://api.thenounproject.com"
    endpoint = f"{base_url}/icons/computer"

    # OAuth parameters
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_nonce': base64.b64encode(os.urandom(32)).decode('utf-8'),
        'oauth_version': '1.0'
    }

    # No additional query parameters for this test
    params = {}

    # Combine all parameters
    all_params = {**params, **oauth_params}

    # Sort and encode parameters
    sorted_params = sorted(all_params.items())
    param_string = '&'.join([f"{quote(k)}={quote(str(v))}" for k, v in sorted_params])

    # Create signature base string
    signature_base = f"GET&{quote(endpoint)}&{quote(param_string)}"

    print(f"Signature base string (first 100 chars):")
    print(f"  {signature_base[:100]}...")

    # Create signing key
    signing_key = f"{api_secret}&"

    # Generate signature
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')

    oauth_params['oauth_signature'] = signature

    print(f"\nOAuth signature: {signature}")

    # Build Authorization header
    auth_header = 'OAuth ' + ', '.join([
        f'{k}="{quote(str(v))}"' for k, v in oauth_params.items()
    ])

    print(f"\nAuthorization header (first 100 chars):")
    print(f"  {auth_header[:100]}...")

    # Make request
    print(f"\nMaking request to: {endpoint}")

    try:
        req = urllib.request.Request(endpoint)
        req.add_header('Authorization', auth_header)
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', 'QGIS-SVG-Plugin/1.0')

        response = urllib.request.urlopen(req, timeout=10)
        data = response.read()

        print(f"\n✓ SUCCESS! Response received")
        print(f"  Status: {response.status}")
        print(f"  Response length: {len(data)} bytes")

        # Parse and show first result
        import json
        result = json.loads(data)
        if 'icons' in result and result['icons']:
            icon = result['icons'][0]
            print(f"\n  First icon:")
            print(f"    ID: {icon.get('id')}")
            print(f"    Term: {icon.get('term')}")
            print(f"    Attribution: {icon.get('attribution')}")

        return True

    except urllib.error.HTTPError as e:
        print(f"\n✗ HTTP Error {e.code}: {e.reason}")
        print(f"  URL: {e.url}")
        if e.code == 403:
            print("\n  Possible issues:")
            print("  - Invalid API key or secret")
            print("  - OAuth signature calculation error")
            print("  - Timestamp out of sync")
        return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_oauth()
    print("\n" + "=" * 60)
    print("Test", "PASSED" if success else "FAILED")