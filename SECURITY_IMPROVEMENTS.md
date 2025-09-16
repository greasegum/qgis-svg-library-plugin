# API Key Security Improvements

## Changes Made

### 1. Removed Hardcoded API Keys
- **Previous Issue**: API key was hardcoded as plaintext in `providers.py:26`
- **Security Risk**: Anyone with access to the code could see and use the API key
- **Solution**: Removed hardcoded credentials completely

### 2. Implemented Secure Key Loading
The API keys are now loaded from secure sources in this priority order:

1. **Environment Variables** (Recommended for CI/CD)
   - `NOUN_PROJECT_API_KEY`
   - `NOUN_PROJECT_SECRET`

2. **QGIS Settings** (For end users)
   - Stored in `svg_library/noun_api_key`
   - Stored in `svg_library/noun_secret`
   - Can be encrypted on some platforms

3. **Constructor Parameters** (For programmatic use)
   - Keys can be passed directly when instantiating the provider

### 3. Provider Availability Check
- Added `is_available()` method to check if credentials are configured
- Search returns empty results if no credentials are available
- Prevents crashes when API keys are not configured

## How to Configure API Keys

### For Users:
1. **Via Environment Variables** (Most secure for servers):
   ```bash
   export NOUN_PROJECT_API_KEY="your_api_key_here"
   export NOUN_PROJECT_SECRET="your_secret_here"
   ```

2. **Via QGIS Plugin Settings**:
   - Open the plugin configuration dialog
   - Enter your API credentials in the API Keys tab
   - Keys are stored in QGIS settings (can be encrypted)

3. **Via Plugin Configuration**:
   - Use the config dialog in the plugin
   - Settings are persisted across sessions

### For Developers:
```python
# Option 1: Let it load from environment/settings
provider = NounProjectProvider()

# Option 2: Pass directly (use secure config management)
provider = NounProjectProvider(
    api_key=secure_config.get('noun_api_key'),
    secret=secure_config.get('noun_secret')
)
```

## Additional Security Recommendations

### 1. Use OS Keyring/Keychain
For maximum security, consider using OS-level secure storage:
- **Windows**: Windows Credential Manager
- **macOS**: Keychain
- **Linux**: Secret Service API / gnome-keyring

Example using `python-keyring`:
```python
import keyring

# Store
keyring.set_password("qgis_svg_plugin", "noun_api_key", api_key)

# Retrieve
api_key = keyring.get_password("qgis_svg_plugin", "noun_api_key")
```

### 2. Encrypt Settings
If storing in QSettings, consider encrypting the values:
```python
from cryptography.fernet import Fernet

def encrypt_key(api_key: str, master_key: bytes) -> str:
    f = Fernet(master_key)
    return f.encrypt(api_key.encode()).decode()

def decrypt_key(encrypted: str, master_key: bytes) -> str:
    f = Fernet(master_key)
    return f.decrypt(encrypted.encode()).decode()
```

### 3. API Key Rotation
- Implement regular key rotation
- Store key version/timestamp
- Support multiple keys during rotation period

### 4. Audit Logging
- Log API key usage (without logging the key itself)
- Track which features require API access
- Monitor for unusual usage patterns

### 5. Principle of Least Privilege
- Use read-only API keys when possible
- Separate keys for different environments
- Revoke unused keys promptly

## Testing Without Exposing Keys

For CI/CD and testing:
1. Use environment variables in CI/CD pipelines
2. Use GitHub Secrets or similar secure variable storage
3. Mock API responses for unit tests
4. Use separate test API keys with limited scope

## Security Checklist

- ✅ No hardcoded credentials in source code
- ✅ API keys loaded from secure sources
- ✅ Graceful handling when keys are not configured
- ✅ Support for environment variables
- ✅ Integration with QGIS settings
- ⬜ Consider implementing OS keyring support
- ⬜ Add key encryption for stored settings
- ⬜ Implement audit logging
- ⬜ Add key rotation support
- ⬜ Create separate test keys

## Important Notes

1. **Never commit API keys** to version control
2. **Add `.env` to `.gitignore`** if using local env files
3. **Use secrets management** in production deployments
4. **Educate users** about API key security
5. **Monitor API usage** for anomalies

## Migration Path for Existing Users

If users have the old version with hardcoded keys:
1. Update to the new version
2. Configure their own API keys via settings or environment
3. The plugin will automatically use the new secure loading mechanism

## Compliance

This implementation helps meet security requirements for:
- OWASP guidelines on credential storage
- PCI DSS requirements (if handling payment-related icons)
- GDPR compliance (protecting user API keys)
- General security best practices