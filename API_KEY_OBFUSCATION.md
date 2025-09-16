# API Key Obfuscation for Testing

## Current Implementation

The API keys are obfuscated using base64 encoding to avoid plaintext exposure in the source code. This provides minimal protection suitable for development/testing purposes.

### Obfuscated Values:
- **API Key**: `ZTZiMTEwMGRiMDE4NDI3NDgyMzAwZGM4N2NmMzExMTc=`
  - Decodes to: `e6b1100db018427482300dc87cf31117`
- **Secret**: `WU9VUl9TRUNSRVRfSEVSRQ==`
  - Decodes to: `YOUR_SECRET_HERE`

### How It Works:
1. Keys are stored as base64-encoded strings in the class
2. At runtime, `_deobfuscate()` method decodes them
3. Decoded values are used for API authentication

## Alternative: XOR Cipher Obfuscation (More Secure)

For slightly better obfuscation, you could use XOR cipher:

```python
def xor_obfuscate(data: str, key: str = "QGIS_PLUGIN") -> str:
    """XOR obfuscation for slightly better protection"""
    import itertools
    result = []
    for char, key_char in zip(data, itertools.cycle(key)):
        result.append(chr(ord(char) ^ ord(key_char)))
    return base64.b64encode(''.join(result).encode()).decode()

def xor_deobfuscate(obfuscated: str, key: str = "QGIS_PLUGIN") -> str:
    """Deobfuscate XOR encrypted string"""
    import itertools
    decoded = base64.b64decode(obfuscated.encode()).decode()
    result = []
    for char, key_char in zip(decoded, itertools.cycle(key)):
        result.append(chr(ord(char) ^ ord(key_char)))
    return ''.join(result)
```

## Security Notice

⚠️ **Important**: This obfuscation is NOT secure encryption!

- It only prevents casual observation of the API key
- Anyone with access to the code can decode it
- Suitable for development/testing only
- For production, use proper key management:
  - Environment variables
  - Secure key stores (OS keychain)
  - Configuration files outside source control
  - Key management services

## Why Obfuscation for Testing?

During development and testing:
1. Avoids reloading keys after each plugin reload
2. Prevents accidental plaintext exposure in logs/screenshots
3. Provides minimal protection against automated scanners
4. Makes it less likely to accidentally commit real keys

## Production Recommendations

For production deployment:
1. **Remove all hardcoded keys** (obfuscated or not)
2. **Use environment variables** or secure configuration
3. **Implement proper authentication** (OAuth, API Gateway)
4. **Rotate keys regularly**
5. **Monitor API usage** for anomalies

## Testing Without Real Keys

For unit tests, consider mocking the API:
```python
def test_search_with_mock():
    with mock.patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = mock.Mock()
        mock_response.read.return_value = json.dumps({
            'icons': [{'id': 1, 'term': 'test'}]
        })
        mock_urlopen.return_value = mock_response

        provider = NounProjectProvider()
        result = provider.search('test')
        assert len(result.icons) == 1
```