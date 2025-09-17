"""
Clean API-based implementations of SVG icon providers
No fallbacks - straight API implementation only
"""

import json
import os
import time
import hashlib
import hmac
import base64
import ssl
from typing import List, Optional
from urllib.parse import urlencode, quote, urlparse
import urllib.request
import urllib.error

try:
    from .icon_providers import IconProvider, SvgIcon, SearchResult
except ImportError:
    # For standalone testing
    from icon_providers import IconProvider, SvgIcon, SearchResult

# Try to use requests-oauthlib if available (better OAuth implementation)
try:
    import requests
    from requests_oauthlib import OAuth1
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def get_ssl_context():
    """Get SSL context for urllib requests

    Returns an SSL context that works in various environments.
    For development/testing, this disables certificate verification.
    For production, you should use the default context.
    """
    try:
        # Try to create default context first
        ssl_context = ssl.create_default_context()
        # For development - disable verification if having issues
        # Comment these out for production
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
    except:
        # Fallback - create basic context
        return ssl.SSLContext(ssl.PROTOCOL_TLS)


class NounProjectProvider(IconProvider):
    """Provider for The Noun Project icons with OAuth 1.0a authentication"""

    # Obfuscated API credentials for testing - base64 encoded
    # This provides minimal obfuscation to avoid plaintext exposure
    # Not for production use - implement proper key management
    _OBFUSCATED_KEY = "ZTZiMTEwMGRiMDE4NDI3NDgyMzAwZGM4N2NmMzExMTc="  # base64 of API key
    _OBFUSCATED_SECRET = "ZWJmN2YyZmE1Mzk3NGRhZWE1NzAzNTgyMmVjNjVhOTA="  # base64 of API secret

    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        super().__init__("The Noun Project", "https://api.thenounproject.com", api_key)
        # Use provided keys or decode obfuscated ones for testing
        self.api_key = api_key or self._deobfuscate(self._OBFUSCATED_KEY)
        self.secret = secret or self._deobfuscate(self._OBFUSCATED_SECRET)

    def _deobfuscate(self, obfuscated: str) -> str:
        """Deobfuscate base64 encoded string"""
        try:
            return base64.b64decode(obfuscated.encode()).decode('utf-8')
        except Exception:
            return ""

    def _generate_oauth_signature(self, method, url, params):
        """Generate OAuth 1.0a signature"""
        # OAuth parameters
        # Generate a simple alphanumeric nonce like requests-oauthlib does
        import random
        import string
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

        # Sort and encode parameters
        sorted_params = sorted(all_params.items())
        param_string = '&'.join([f"{quote(k)}={quote(str(v))}" for k, v in sorted_params])

        # Create signature base string
        signature_base = f"{method}&{quote(url)}&{quote(param_string)}"

        # Create signing key
        signing_key = f"{self.secret}&"

        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode('utf-8'),
                signature_base.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')

        oauth_params['oauth_signature'] = signature
        return oauth_params

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search The Noun Project API with OAuth authentication"""
        if not self.api_key or not self.secret:
            # Return empty result if not configured
            return SearchResult([], 0, page, 0, False, False)

        try:
            # API endpoint - v2 uses /icon with query parameter
            endpoint = f"{self.base_url}/v2/icon"

            # Query parameters
            params = {
                'query': query,
                'limit': str(per_page)
            }

            # Use requests-oauthlib if available (more reliable OAuth)
            if HAS_REQUESTS:
                auth = OAuth1(self.api_key, self.secret)
                url = f"{endpoint}?{urlencode(params)}"
                response = requests.get(url, auth=auth, timeout=10)

                if response.status_code != 200:
                    print(f"Noun Project API error: {response.status_code}")
                    return SearchResult([], 0, page, 0, False, False)

                data = response.json()
            else:
                # Fallback to manual OAuth (may have issues)
                oauth_params = self._generate_oauth_signature('GET', endpoint, params)

                auth_header = 'OAuth ' + ', '.join([
                    f'{k}="{quote(str(v))}"' for k, v in oauth_params.items()
                ])

                url = f"{endpoint}?{urlencode(params)}"

                req = urllib.request.Request(url)
                req.add_header('Authorization', auth_header)
                req.add_header('Accept', 'application/json')

                # Use SSL context to handle certificate issues
                response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
                data = json.loads(response.read())

            # Parse results
            icons = []
            for item in data.get('icons', []):
                icon = SvgIcon(
                    id=str(item.get('id', '')),
                    name=item.get('term', 'Unknown'),
                    url=item.get('permalink', ''),
                    preview_url=item.get('preview_url', ''),
                    tags=item.get('tags', []),
                    license=item.get('license_description', 'Unknown'),
                    attribution=f"Created by {item.get('uploader', {}).get('name', 'Unknown')} from Noun Project",
                    provider=self.name,
                    download_url=item.get('icon_url', '')
                )
                icons.append(icon)

            total_count = data.get('total', 0)
            total_pages = (total_count + per_page - 1) // per_page

            return SearchResult(
                icons=icons,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )

        except Exception as e:
            print(f"Noun Project API error: {e}")
            # No fallback - return empty
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific icon"""
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from The Noun Project"""
        try:
            # Generate OAuth for download URL
            oauth_params = self._generate_oauth_signature('GET', icon.download_url, {})

            auth_header = 'OAuth ' + ', '.join([
                f'{k}="{quote(str(v))}"' for k, v in oauth_params.items()
            ])

            req = urllib.request.Request(icon.download_url)
            req.add_header('Authorization', auth_header)

            response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True

        except Exception as e:
            print(f"Error downloading from Noun Project: {e}")
            return False


class MaterialSymbolsProvider(IconProvider):
    """Provider for Material Design Symbols - direct API only"""

    def __init__(self):
        super().__init__("Material Symbols", "https://api.github.com")
        self.repo = "google/material-design-icons"
        self._icon_list = None

    def _get_all_icons(self):
        """Get list of Material icons from GitHub API"""
        if self._icon_list is not None:
            return self._icon_list

        try:
            # Get icons from the symbols/web directory
            api_url = f"https://api.github.com/repos/{self.repo}/contents/symbols/web"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'QGIS-SVG-Plugin')

            response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
            data = json.loads(response.read())

            # Extract icon names from directories
            self._icon_list = []
            for item in data:
                if item['type'] == 'dir':
                    icon_name = item['name']
                    self._icon_list.append({
                        'name': icon_name,
                        'path': item['path'],
                        'url': item['url']
                    })

            return self._icon_list
        except Exception as e:
            print(f"Error fetching Material icons: {e}")
            # No fallback - return empty
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Material Symbols"""
        try:
            # Get all icons from API
            all_icons = self._get_all_icons()

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons[:100]

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_icons = matching_icons[start_idx:end_idx]

            icons = []
            for icon_data in page_icons:
                icon_name = icon_data['name']
                # Use Material Icons CDN
                preview_url = f"https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{icon_name}/default/48px.svg"

                icon = SvgIcon(
                    id=icon_name,
                    name=icon_name.replace('_', ' ').title(),
                    url=f"https://fonts.google.com/icons?selected=Material+Symbols+Outlined:{icon_name}",
                    preview_url=preview_url,
                    tags=[icon_name],
                    license="Apache License 2.0",
                    attribution="Material Symbols by Google",
                    provider=self.name,
                    download_url=preview_url
                )
                icons.append(icon)

            total_count = len(matching_icons)
            total_pages = (total_count + per_page - 1) // per_page

            return SearchResult(
                icons=icons,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except Exception as e:
            print(f"Material Symbols API error: {e}")
            # No fallback - return empty
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Material Symbol SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10, context=get_ssl_context())
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Material Symbol: {e}")
            return False


class MakiProvider(IconProvider):
    """Provider for Maki icons - direct API only"""

    def __init__(self):
        super().__init__("Maki", "https://api.github.com")
        self.repo = "mapbox/maki"
        self.raw_base = "https://raw.githubusercontent.com/mapbox/maki/main"
        self._icon_list = None

    def _get_all_icons(self):
        """Get list of all Maki icons from GitHub"""
        if self._icon_list is not None:
            return self._icon_list

        try:
            # Get list of icons from the icons directory
            api_url = f"https://api.github.com/repos/{self.repo}/contents/icons"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'QGIS-SVG-Plugin')

            response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
            data = json.loads(response.read())

            # Extract icon names
            self._icon_list = []
            for item in data:
                if item['name'].endswith('.svg'):
                    icon_name = item['name'].replace('.svg', '')
                    self._icon_list.append({
                        'name': icon_name,
                        'path': item['path'],
                        'download_url': item['download_url']
                    })

            return self._icon_list
        except Exception as e:
            print(f"Error fetching Maki icon list: {e}")
            # No fallback - return empty
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Maki icons"""
        try:
            # Get all icons from API
            all_icons = self._get_all_icons()

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_icons = matching_icons[start_idx:end_idx]

            icons = []
            for icon_data in page_icons:
                icon_name = icon_data['name']
                icon = SvgIcon(
                    id=icon_name,
                    name=icon_name.replace('-', ' ').title(),
                    url=f"https://github.com/{self.repo}/blob/main/icons/{icon_name}.svg",
                    preview_url=icon_data['download_url'],
                    tags=[icon_name],
                    license="CC0 1.0 Universal",
                    attribution="Maki Icons by Mapbox",
                    provider=self.name,
                    download_url=icon_data['download_url']
                )
                icons.append(icon)

            total_count = len(matching_icons)
            total_pages = (total_count + per_page - 1) // per_page

            return SearchResult(
                icons=icons,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )

        except Exception as e:
            print(f"Maki search error: {e}")
            # No fallback - return empty
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Maki SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10, context=get_ssl_context())
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Maki icon: {e}")
            return False


class FontAwesomeFreeProvider(IconProvider):
    """Provider for Font Awesome Free icons - direct API only"""

    def __init__(self):
        super().__init__("Font Awesome Free", "https://api.github.com")
        self.repo = "FortAwesome/Font-Awesome"
        self._icon_lists = {}

    def _get_icons_for_style(self, style="solid"):
        """Get list of Font Awesome icons for a specific style"""
        if style in self._icon_lists:
            return self._icon_lists[style]

        try:
            # Get list of icons from the style directory
            api_url = f"https://api.github.com/repos/{self.repo}/contents/svgs/{style}"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'QGIS-SVG-Plugin')

            response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
            data = json.loads(response.read())

            # Extract icon names
            icons = []
            for item in data:
                if item['name'].endswith('.svg'):
                    icon_name = item['name'].replace('.svg', '')
                    icons.append({
                        'name': icon_name,
                        'style': style,
                        'path': item['path'],
                        'download_url': item['download_url']
                    })

            self._icon_lists[style] = icons
            return icons
        except Exception as e:
            print(f"Error fetching Font Awesome {style} icons: {e}")
            # No fallback - return empty
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Font Awesome Free icons"""
        try:
            # Get icons from solid style
            all_icons = self._get_icons_for_style("solid")

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons[:100]

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_icons = matching_icons[start_idx:end_idx]

            icons = []
            for icon_data in page_icons:
                icon_name = icon_data['name']
                style = icon_data['style']

                icon = SvgIcon(
                    id=icon_name,
                    name=icon_name.replace('-', ' ').title(),
                    url=f"https://fontawesome.com/icons/{icon_name}",
                    preview_url=icon_data['download_url'],
                    tags=[icon_name, style],
                    license="CC BY 4.0 License",
                    attribution="Font Awesome Free by Fonticons",
                    provider=self.name,
                    download_url=icon_data['download_url']
                )
                icons.append(icon)

            total_count = len(matching_icons)
            total_pages = (total_count + per_page - 1) // per_page

            return SearchResult(
                icons=icons,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )

        except Exception as e:
            print(f"Font Awesome search error: {e}")
            # No fallback - return empty
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Font Awesome SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10, context=get_ssl_context())
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Font Awesome icon: {e}")
            return False


class GitHubRepoProvider(IconProvider):
    """Provider for GitHub repository SVG icons - direct API only"""

    def __init__(self, repo: str, path: str = ""):
        super().__init__(f"GitHub: {repo}", f"https://api.github.com/repos/{repo}")
        self.repo = repo
        self.search_path = path
        self._icon_list = None

    def _get_all_icons(self):
        """Get list of all SVG icons from the repository"""
        if self._icon_list is not None:
            return self._icon_list

        try:
            # Get list of files from the specified path
            path_param = f"/contents/{self.search_path}" if self.search_path else "/contents"
            api_url = f"https://api.github.com/repos/{self.repo}{path_param}"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'QGIS-SVG-Plugin')

            response = urllib.request.urlopen(req, timeout=10, context=get_ssl_context())
            data = json.loads(response.read())

            # Extract SVG files
            self._icon_list = []
            for item in data:
                if item['name'].endswith('.svg'):
                    icon_name = item['name'].replace('.svg', '')
                    self._icon_list.append({
                        'name': icon_name,
                        'path': item['path'],
                        'download_url': item['download_url']
                    })

            return self._icon_list
        except Exception as e:
            print(f"Error fetching icons from {self.repo}: {e}")
            # No fallback - return empty
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search icons in the GitHub repository"""
        try:
            # Get all icons from API
            all_icons = self._get_all_icons()

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_icons = matching_icons[start_idx:end_idx]

            icons = []
            for icon_data in page_icons:
                icon_name = icon_data['name']
                icon = SvgIcon(
                    id=icon_name,
                    name=icon_name.replace('-', ' ').replace('_', ' ').title(),
                    url=f"https://github.com/{self.repo}/blob/main/{icon_data['path']}",
                    preview_url=icon_data['download_url'],
                    tags=[icon_name],
                    license="Check repository license",
                    attribution=f"Icons from {self.repo}",
                    provider=self.name,
                    download_url=icon_data['download_url']
                )
                icons.append(icon)

            total_count = len(matching_icons)
            total_pages = (total_count + per_page - 1) // per_page

            return SearchResult(
                icons=icons,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )

        except Exception as e:
            print(f"GitHub repo search error: {e}")
            # No fallback - return empty
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from GitHub"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10, context=get_ssl_context())
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading from GitHub: {e}")
            return False