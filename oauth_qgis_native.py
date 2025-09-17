"""
Enhanced OAuth implementation using QGIS native features where possible
"""

import sys
import subprocess
from typing import Optional, Dict, Any

# Try to import QGIS components
try:
    from qgis.core import QgsApplication, QgsMessageLog, Qgis, QgsNetworkAccessManager
    from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
    from qgis.PyQt.QtCore import QUrl, QEventLoop, QTimer
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False

# Try to import requests-oauthlib
try:
    import requests
    from requests_oauthlib import OAuth1
    HAS_REQUESTS_OAUTH = True
except ImportError:
    HAS_REQUESTS_OAUTH = False


class QGISNativeOAuth:
    """OAuth implementation that prefers QGIS native features"""

    def __init__(self, api_key: str, api_secret: str, provider_name: str = "OAuth Provider"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.provider_name = provider_name
        self.auth_method = self._determine_auth_method()

        if HAS_QGIS:
            QgsMessageLog.logMessage(
                f"OAuth method: {self.auth_method}",
                self.provider_name,
                Qgis.Info
            )

    def _determine_auth_method(self) -> str:
        """Determine the best available OAuth method"""
        if HAS_REQUESTS_OAUTH:
            return 'requests_oauthlib'
        elif HAS_QGIS:
            return 'qgis_native'
        else:
            return 'manual'

    def make_request(self, url: str, params: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make an authenticated OAuth request"""
        if self.auth_method == 'requests_oauthlib':
            return self._request_with_requests_oauthlib(url, params)
        elif self.auth_method == 'qgis_native':
            return self._request_with_qgis_native(url, params)
        else:
            return self._request_with_manual_oauth(url, params)

    def _request_with_requests_oauthlib(self, url: str, params: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make request using requests-oauthlib (most reliable)"""
        try:
            auth = OAuth1(self.api_key, client_secret=self.api_secret)

            # Build URL with params
            if params:
                from urllib.parse import urlencode
                url = f"{url}?{urlencode(params)}"

            response = requests.get(url, auth=auth, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                if HAS_QGIS:
                    QgsMessageLog.logMessage(
                        f"OAuth request failed: {response.status_code}",
                        self.provider_name,
                        Qgis.Warning
                    )
                return None

        except Exception as e:
            if HAS_QGIS:
                QgsMessageLog.logMessage(
                    f"OAuth error: {str(e)}",
                    self.provider_name,
                    Qgis.Critical
                )
            return None

    def _request_with_qgis_native(self, url: str, params: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make request using QGIS native network manager"""
        try:
            from urllib.parse import urlencode
            import json

            # Build full URL
            if params:
                url = f"{url}?{urlencode(params)}"

            # Create OAuth header manually for OAuth 1.0a
            oauth_header = self._generate_oauth_header(url, 'GET', params or {})

            # Create request
            request = QNetworkRequest(QUrl(url))
            request.setRawHeader(b'Authorization', oauth_header.encode())
            request.setRawHeader(b'Accept', b'application/json')

            # Get network manager
            nam = QgsNetworkAccessManager.instance()

            # Make synchronous request
            event_loop = QEventLoop()
            reply = nam.get(request)

            # Set timeout
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(event_loop.quit)
            timer.start(10000)  # 10 second timeout

            reply.finished.connect(event_loop.quit)
            event_loop.exec_()

            # Check if timeout occurred
            if timer.isActive():
                timer.stop()

                if reply.error() == QNetworkReply.NoError:
                    data = reply.readAll().data()
                    reply.deleteLater()
                    return json.loads(data.decode('utf-8'))
                else:
                    QgsMessageLog.logMessage(
                        f"Network error: {reply.errorString()}",
                        self.provider_name,
                        Qgis.Warning
                    )
                    reply.deleteLater()
                    return None
            else:
                # Timeout occurred
                reply.abort()
                reply.deleteLater()
                QgsMessageLog.logMessage(
                    "Request timeout",
                    self.provider_name,
                    Qgis.Warning
                )
                return None

        except Exception as e:
            QgsMessageLog.logMessage(
                f"QGIS native request error: {str(e)}",
                self.provider_name,
                Qgis.Critical
            )
            return None

    def _request_with_manual_oauth(self, url: str, params: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Fallback to manual OAuth implementation"""
        import urllib.request
        import json
        from urllib.parse import urlencode

        try:
            # Build URL with params
            if params:
                url = f"{url}?{urlencode(params)}"

            oauth_header = self._generate_oauth_header(url, 'GET', params or {})

            req = urllib.request.Request(url)
            req.add_header('Authorization', oauth_header)
            req.add_header('Accept', 'application/json')

            # Use SSL context
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            response = urllib.request.urlopen(req, timeout=10, context=ssl_context)
            data = json.loads(response.read())
            return data

        except Exception as e:
            if HAS_QGIS:
                QgsMessageLog.logMessage(
                    f"Manual OAuth error: {str(e)}",
                    self.provider_name,
                    Qgis.Critical
                )
            return None

    def _generate_oauth_header(self, url: str, method: str, params: Dict[str, str]) -> str:
        """Generate OAuth 1.0a header"""
        import time
        import hmac
        import hashlib
        import base64
        import random
        import string
        from urllib.parse import quote

        # OAuth parameters
        nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': nonce,
            'oauth_version': '1.0'
        }

        # Combine all parameters
        all_params = {**params, **oauth_params}

        # RFC3986 percent encoding
        def percent_encode(s):
            return quote(str(s), safe='~')

        # Sort and encode parameters
        sorted_params = sorted(all_params.items())
        param_string = '&'.join([f"{percent_encode(k)}={percent_encode(v)}" for k, v in sorted_params])

        # Create signature base string
        signature_base = f"{method}&{percent_encode(url.split('?')[0])}&{percent_encode(param_string)}"

        # Create signing key
        signing_key = f"{percent_encode(self.api_secret)}&"

        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode('utf-8'),
                signature_base.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')

        oauth_params['oauth_signature'] = signature

        # Format OAuth header
        auth_header = 'OAuth ' + ', '.join([
            f'{k}="{percent_encode(v)}"' for k, v in oauth_params.items()
        ])

        return auth_header

    @staticmethod
    def install_dependencies() -> bool:
        """Attempt to install OAuth dependencies"""
        try:
            # Check if already installed
            import requests
            from requests_oauthlib import OAuth1
            return True
        except ImportError:
            pass

        packages = ['requests', 'requests-oauthlib']
        success = True

        for package in packages:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--user', package],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    success = False
                    if HAS_QGIS:
                        QgsMessageLog.logMessage(
                            f"Failed to install {package}: {result.stderr}",
                            "OAuth Setup",
                            Qgis.Warning
                        )
            except Exception as e:
                success = False
                if HAS_QGIS:
                    QgsMessageLog.logMessage(
                        f"Error installing {package}: {str(e)}",
                        "OAuth Setup",
                        Qgis.Critical
                    )

        return success

    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """Check which OAuth dependencies are available"""
        status = {
            'requests': False,
            'requests_oauthlib': False,
            'qgis_native': HAS_QGIS,
            'recommended_available': False
        }

        try:
            import requests
            status['requests'] = True
        except ImportError:
            pass

        try:
            from requests_oauthlib import OAuth1
            status['requests_oauthlib'] = True
        except ImportError:
            pass

        status['recommended_available'] = status['requests_oauthlib']

        return status


def setup_oauth_for_provider(api_key: str, api_secret: str, provider_name: str) -> QGISNativeOAuth:
    """Setup OAuth with best available method for a provider"""

    oauth = QGISNativeOAuth(api_key, api_secret, provider_name)

    # Check dependencies
    deps = oauth.check_dependencies()

    if HAS_QGIS:
        if deps['recommended_available']:
            QgsMessageLog.logMessage(
                "Using requests-oauthlib for OAuth (recommended)",
                provider_name,
                Qgis.Success
            )
        elif deps['qgis_native']:
            QgsMessageLog.logMessage(
                "Using QGIS native network manager for OAuth",
                provider_name,
                Qgis.Info
            )
        else:
            QgsMessageLog.logMessage(
                "Using manual OAuth implementation (limited reliability)",
                provider_name,
                Qgis.Warning
            )

            # Offer to install dependencies
            if not deps['requests_oauthlib']:
                QgsMessageLog.logMessage(
                    "Run QGISNativeOAuth.install_dependencies() to install recommended libraries",
                    provider_name,
                    Qgis.Info
                )

    return oauth


# Example usage
if __name__ == "__main__":
    # Test the implementation
    print("OAuth Implementation Test")
    print("-" * 40)

    # Check dependencies
    deps = QGISNativeOAuth.check_dependencies()
    for key, available in deps.items():
        status = "✓" if available else "✗"
        print(f"{status} {key}: {available}")

    print("-" * 40)

    if not deps['recommended_available']:
        print("Installing recommended dependencies...")
        success = QGISNativeOAuth.install_dependencies()
        if success:
            print("✓ Dependencies installed successfully")
        else:
            print("✗ Failed to install some dependencies")

    # Test OAuth
    print("\nTesting OAuth request...")
    oauth = setup_oauth_for_provider(
        api_key="test_key",
        api_secret="test_secret",
        provider_name="Test Provider"
    )

    print(f"Using auth method: {oauth.auth_method}")