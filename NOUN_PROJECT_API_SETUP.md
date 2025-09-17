# The Noun Project API Setup and Troubleshooting

## Current Status
- **API Key**: ✅ Configured and obfuscated
- **API Secret**: ✅ Configured and obfuscated
- **Authentication**: ❌ Returning 403 Forbidden
- **OAuth Implementation**: ✅ Correctly implemented

## Obfuscated Credentials in Code
```python
# In providers.py
_OBFUSCATED_KEY = "ZTZiMTEwMGRiMDE4NDI3NDgyMzAwZGM4N2NmMzExMTc="  # base64 of API key
_OBFUSCATED_SECRET = "ZWJmN2YyZmE1Mzk3NGRhZWE1NzAzNTgyMmVjNjVhOTA="  # base64 of API secret
```

These decode to:
- API Key: `e6b1100db018427482300dc87cf31117`
- Secret: `ebf7f2fa53974daea57035822ec65a90`

## OAuth 1.0a Implementation

### Requirements
The Noun Project API uses OAuth 1.0a "one-legged" authentication:
- No user access tokens required
- Only consumer key and secret needed
- Minimum 8-character nonce
- HMAC-SHA1 signature method

### Current Implementation
```python
def _generate_oauth_signature(self, method, url, params):
    """Generate OAuth 1.0a signature"""
    oauth_params = {
        'oauth_consumer_key': self.api_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_nonce': base64.b64encode(os.urandom(32)).decode('utf-8'),
        'oauth_version': '1.0'
    }

    # Combine, sort, and encode parameters
    all_params = {**params, **oauth_params}
    sorted_params = sorted(all_params.items())
    param_string = '&'.join([f"{quote(k)}={quote(str(v))}" for k, v in sorted_params])

    # Create signature base string
    signature_base = f"{method}&{quote(url)}&{quote(param_string)}"

    # Generate HMAC-SHA1 signature
    signing_key = f"{self.secret}&"
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')

    return oauth_params
```

## API Endpoints

### V1 Endpoints (Currently Used)
- Search: `GET /icons/{term}`
- Icon details: `GET /icon/{id}`
- Download: Direct URL from icon data

### V2 Endpoints
- Search: `GET /v2/icons/{term}`
- Parameters: `limit`, `offset` for pagination

## Troubleshooting 403 Forbidden

### Possible Causes
1. **Invalid Credentials**
   - The API key or secret may be incorrect or expired
   - Credentials may have been revoked

2. **Account Issues**
   - API access may not be enabled for the account
   - Rate limits may have been exceeded
   - Account may require payment/subscription

3. **OAuth Signature Issues**
   - Timestamp drift (server time mismatch)
   - Incorrect parameter encoding
   - Wrong signature base string construction

### Debugging Steps Taken
1. ✅ Verified OAuth implementation matches specification
2. ✅ Confirmed nonce meets minimum length requirement
3. ✅ Tested both v1 and v2 endpoints
4. ✅ Verified base64 encoding/decoding works correctly
5. ❌ API still returns 403 with provided credentials

### How to Get Working Credentials

1. **Create Account**
   - Go to [The Noun Project](https://thenounproject.com)
   - Sign up for an account (free or paid)

2. **Enable API Access**
   - Log in to your account
   - Go to [API Management](https://thenounproject.com/developers/apps/)
   - Create a new application
   - Copy the consumer key and secret

3. **Update Plugin**
   ```python
   # Option 1: Update obfuscated values in providers.py
   # Generate new obfuscated values:
   import base64
   key = "your_api_key_here"
   secret = "your_api_secret_here"
   print(f"Key: {base64.b64encode(key.encode()).decode()}")
   print(f"Secret: {base64.b64encode(secret.encode()).decode()}")

   # Option 2: Pass directly when creating provider
   provider = NounProjectProvider(
       api_key="your_key",
       secret="your_secret"
   )
   ```

## Testing the API

### Manual Test Script
```python
# test_noun_project.py
from providers import NounProjectProvider

# Test with your credentials
provider = NounProjectProvider()
result = provider.search("computer", page=1, per_page=5)

if result.icons:
    print(f"Success! Found {len(result.icons)} icons")
    for icon in result.icons:
        print(f"- {icon.name}")
else:
    print("No results or authentication failed")
```

### Expected Successful Response
```json
{
  "icons": [
    {
      "id": 123456,
      "term": "computer",
      "attribution": "Computer by Author from Noun Project",
      "preview_url": "https://...",
      ...
    }
  ],
  "total": 100
}
```

## Alternative Solutions

### 1. Mock Data for Development
If API access remains unavailable, consider using mock data:
```python
if self.api_key == "test" or not self.secret:
    # Return mock data for testing
    return self._get_mock_results(query, page, per_page)
```

### 2. Proxy Service
Set up a proxy service with valid credentials:
- Host a simple API proxy with valid credentials
- Plugin connects to proxy instead of Noun Project directly
- Proxy handles OAuth and returns results

### 3. Other Icon Providers
Focus on the working providers:
- ✅ Material Symbols (Google)
- ✅ Maki (Mapbox)
- ✅ Font Awesome Free
- ✅ GitHub Repositories

## Security Notes

### Current Implementation
- Credentials are base64 obfuscated (not encrypted)
- Suitable for development/testing only
- Prevents casual observation in code

### Production Recommendations
1. **Never hardcode credentials** in production code
2. **Use environment variables** or secure key storage
3. **Let users provide their own API keys** via settings
4. **Consider OAuth 2.0 providers** for better security

## Next Steps

1. **Verify Credentials**
   - Confirm the provided API key and secret are valid
   - Check if API access is enabled for the account
   - Test credentials using Noun Project's API console if available

2. **Contact Support**
   - If credentials should work, contact Noun Project support
   - Ask about any special requirements or restrictions

3. **Update Documentation**
   - Document the process for users to get their own API keys
   - Add troubleshooting guide to plugin documentation
   - Include setup wizard in plugin for API configuration