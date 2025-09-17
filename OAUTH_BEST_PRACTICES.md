# OAuth Authentication Best Practices for QGIS Plugins

## Current Status (2024)

QGIS plugin dependency management is still evolving. QEP #202 (PIP dependencies) has been proposed but not yet implemented. Until then, plugins must handle dependencies manually.

## Recommended OAuth Implementation Strategy

### 1. Hybrid Approach (Currently Implemented)
Your plugin already follows best practices by:
- Attempting to use `requests-oauthlib` when available
- Falling back to manual OAuth implementation
- Providing installation helpers

### 2. Improved Implementation Options

#### Option A: Use QGIS Native OAuth2 (For OAuth2 providers)
```python
from qgis.core import QgsApplication, QgsAuthMethodConfig, QgsNetworkAccessManager
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl

def setup_oauth2_qgis_native():
    """Use QGIS built-in OAuth2 support"""
    auth_mgr = QgsApplication.authManager()

    # Create authentication configuration
    config = QgsAuthMethodConfig()
    config.setMethod('OAuth2')
    config.setName('The Noun Project OAuth')

    # OAuth2 configuration
    oauth_config = {
        'oauth2_client_id': 'your_client_id',
        'oauth2_client_secret': 'your_client_secret',
        'oauth2_token_url': 'https://api.thenounproject.com/oauth/token',
        'oauth2_auth_url': 'https://api.thenounproject.com/oauth/authorize',
        'oauth2_scope': 'read'
    }
    config.setConfigMap(oauth_config)

    # Store configuration
    auth_mgr.storeAuthenticationConfig(config)

    # Use with QgsNetworkAccessManager
    nam = QgsNetworkAccessManager.instance()
    request = QNetworkRequest(QUrl('https://api.thenounproject.com/v2/icon'))
    auth_mgr.updateNetworkRequest(request, config.id())

    reply = nam.get(request)
    return reply
```

#### Option B: Enhanced Hybrid Approach (For OAuth 1.0a - Your Current Need)
```python
class EnhancedOAuthProvider:
    def __init__(self):
        self.auth_method = self._determine_auth_method()

    def _determine_auth_method(self):
        """Determine best available OAuth method"""
        # Priority order:
        # 1. requests-oauthlib (most reliable)
        # 2. oauthlib alone (good fallback)
        # 3. Manual implementation (last resort)

        try:
            from requests_oauthlib import OAuth1
            return 'requests_oauthlib'
        except ImportError:
            try:
                import oauthlib
                return 'oauthlib'
            except ImportError:
                return 'manual'

    def authenticate(self, url, params):
        if self.auth_method == 'requests_oauthlib':
            return self._requests_oauth(url, params)
        elif self.auth_method == 'oauthlib':
            return self._oauthlib_oauth(url, params)
        else:
            return self._manual_oauth(url, params)
```

### 3. Dependency Management Best Practices

#### In metadata.txt:
```ini
[general]
name=SVG Library Plugin
about=Search and use SVG icons in QGIS.

    Dependencies (optional but recommended):
    - requests >= 2.25.0
    - requests-oauthlib >= 1.3.0

    To install dependencies:
    1. Open QGIS Python Console (Ctrl+Alt+P)
    2. Run: import pip; pip.main(['install', '--user', 'requests', 'requests-oauthlib'])
    3. Restart QGIS

homepage=https://github.com/yourusername/qgis-svg-library-plugin
tracker=https://github.com/yourusername/qgis-svg-library-plugin/issues
repository=https://github.com/yourusername/qgis-svg-library-plugin
```

#### Smart Dependency Installer:
```python
def ensure_dependencies():
    """Ensure OAuth dependencies are available"""
    import sys
    import subprocess
    from qgis.core import QgsMessageLog, Qgis

    required_packages = {
        'requests': '2.25.0',
        'requests-oauthlib': '1.3.0'
    }

    missing_packages = []

    for package, min_version in required_packages.items():
        try:
            pkg = __import__(package.replace('-', '_'))
            QgsMessageLog.logMessage(
                f'{package} is available',
                'SVG Library',
                Qgis.Info
            )
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        QgsMessageLog.logMessage(
            f'Missing packages: {", ".join(missing_packages)}',
            'SVG Library',
            Qgis.Warning
        )

        # Attempt installation
        for package in missing_packages:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install',
                    '--user', package
                ])
                QgsMessageLog.logMessage(
                    f'Successfully installed {package}',
                    'SVG Library',
                    Qgis.Success
                )
            except subprocess.CalledProcessError:
                QgsMessageLog.logMessage(
                    f'Failed to install {package}. Please install manually.',
                    'SVG Library',
                    Qgis.Critical
                )
```

### 4. Platform-Specific Considerations

#### Windows (OSGeo4W):
```python
def get_osgeo4w_python():
    """Get OSGeo4W Python path on Windows"""
    import os
    import sys

    if sys.platform == 'win32':
        # Common OSGeo4W paths
        paths = [
            r'C:\OSGeo4W\apps\Python39',
            r'C:\OSGeo4W64\apps\Python39',
            r'C:\Program Files\QGIS 3.28\apps\Python39'
        ]

        for path in paths:
            if os.path.exists(path):
                return os.path.join(path, 'python.exe')

    return sys.executable
```

#### macOS:
```python
def install_on_macos():
    """macOS-specific installation"""
    import subprocess
    import sys

    # QGIS.app bundle Python
    if '/QGIS.app/' in sys.executable:
        # Use --target for QGIS app bundle
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '--target', os.path.dirname(sys.executable),
            'requests', 'requests-oauthlib'
        ])
```

### 5. Error Handling and User Communication

```python
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis

class OAuthErrorHandler:
    @staticmethod
    def handle_missing_dependencies(parent_widget):
        """Show user-friendly message for missing dependencies"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("OAuth Dependencies Required")
        msg.setText("This plugin works better with additional libraries.")
        msg.setDetailedText(
            "To enable full OAuth support:\n\n"
            "1. Open QGIS Python Console (Plugins → Python Console)\n"
            "2. Run this command:\n"
            "   import subprocess, sys\n"
            "   subprocess.run([sys.executable, '-m', 'pip', 'install', "
            "'--user', 'requests', 'requests-oauthlib'])\n"
            "3. Restart QGIS\n\n"
            "The plugin will still work with limited functionality."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    @staticmethod
    def log_oauth_status(has_requests, has_oauthlib):
        """Log OAuth library status"""
        if has_requests and has_oauthlib:
            QgsMessageLog.logMessage(
                "OAuth: Using requests-oauthlib (recommended)",
                "SVG Library", Qgis.Info
            )
        elif has_oauthlib:
            QgsMessageLog.logMessage(
                "OAuth: Using oauthlib (good)",
                "SVG Library", Qgis.Info
            )
        else:
            QgsMessageLog.logMessage(
                "OAuth: Using manual implementation (limited)",
                "SVG Library", Qgis.Warning
            )
```

## Implementation Checklist

- [x] Implement graceful fallbacks for missing dependencies
- [x] Provide clear installation instructions in metadata.txt
- [x] Create installation helper script
- [x] Handle SSL certificate issues
- [ ] Consider using QgsNetworkAccessManager for network requests
- [ ] Add user-friendly error messages for OAuth failures
- [ ] Test on Windows, macOS, and Linux
- [ ] Document platform-specific installation steps

## Future Considerations

1. **Monitor QEP #202** - When implemented, update to use standardized pip dependencies
2. **Consider QGIS OAuth2 migration** - If The Noun Project adds OAuth2 support
3. **Bundle critical dependencies** - For offline installations
4. **Create conda package** - For conda-forge distribution

## Testing OAuth Implementation

```python
# Test script for QGIS Python Console
def test_oauth_implementation():
    """Test OAuth with all available methods"""

    print("Testing OAuth Implementation")
    print("-" * 40)

    # Test requests-oauthlib
    try:
        import requests
        from requests_oauthlib import OAuth1
        print("✓ requests-oauthlib available")
    except ImportError:
        print("✗ requests-oauthlib not available")

    # Test QGIS auth manager
    try:
        from qgis.core import QgsApplication
        am = QgsApplication.authManager()
        print(f"✓ QGIS AuthManager available: {am is not None}")
    except:
        print("✗ QGIS AuthManager not available")

    # Test network access
    try:
        from qgis.core import QgsNetworkAccessManager
        nam = QgsNetworkAccessManager.instance()
        print(f"✓ QgsNetworkAccessManager available: {nam is not None}")
    except:
        print("✗ QgsNetworkAccessManager not available")

    print("-" * 40)
    print("Test complete")

# Run test
test_oauth_implementation()
```

## Conclusion

Your current implementation already follows many best practices. The main improvements would be:

1. **Better user communication** about missing dependencies
2. **Platform-specific installation helpers**
3. **Consider QgsNetworkAccessManager** for network requests
4. **Add comprehensive error handling** with user-friendly messages

The hybrid approach (external library with fallback) remains the best strategy until QGIS implements standardized dependency management.