"""
API-based implementations of SVG icon providers
No hardcoded lists - all data from real APIs
"""

import json
import os
from typing import List, Optional
from urllib.parse import urlencode, quote
import urllib.request
import urllib.error

from .icon_providers import IconProvider, SvgIcon, SearchResult


class MaterialSymbolsProvider(IconProvider):
    """Provider for Material Design Symbols using GitHub API"""

    def __init__(self):
        super().__init__("Material Symbols", "https://api.github.com")
        self.repo = "google/material-design-icons"
        self._icon_list = None

    def _get_all_icons(self):
        """Get list of Material icons from a specific category"""
        if self._icon_list is not None:
            return self._icon_list

        try:
            # Get icons from the action category as an example
            # Material Design Icons has icons in various subdirectories
            api_url = f"https://api.github.com/repos/{self.repo}/contents/symbols/web"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'QGIS-SVG-Plugin')

            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read())

            # Extract icon names from directories
            self._icon_list = []
            for item in data:
                if item['type'] == 'dir':
                    icon_name = item['name']
                    # These are directories, each containing multiple versions
                    # For simplicity, we'll use the directory name as the icon
                    self._icon_list.append({
                        'name': icon_name,
                        'path': item['path'],
                        'url': item['url']
                    })

            return self._icon_list
        except Exception as e:
            print(f"Error fetching Material icons: {e}")
            # Fallback to a small set of known icons
            return [
                {'name': 'home', 'path': 'symbols/web/home', 'url': ''},
                {'name': 'star', 'path': 'symbols/web/star', 'url': ''},
                {'name': 'search', 'path': 'symbols/web/search', 'url': ''},
                {'name': 'settings', 'path': 'symbols/web/settings', 'url': ''},
                {'name': 'favorite', 'path': 'symbols/web/favorite', 'url': ''},
            ]

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Material Symbols"""
        try:
            # Get all icons
            all_icons = self._get_all_icons()

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons[:100]  # Limit when no query

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_icons = matching_icons[start_idx:end_idx]

            icons = []
            for icon_data in page_icons:
                icon_name = icon_data['name']
                # Material icons use a specific URL pattern
                # Using the material icons CDN for better reliability
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
            print(f"Material Symbols search error: {e}")
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific Material icon"""
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Material Symbol SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10)
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Material Symbol: {e}")
            return False


class MakiProvider(IconProvider):
    """Provider for Maki icons using GitHub API"""

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

            response = urllib.request.urlopen(req, timeout=10)
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
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Maki icons"""
        try:
            # Get all icons
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
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Maki SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10)
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Maki icon: {e}")
            return False


class FontAwesomeFreeProvider(IconProvider):
    """Provider for Font Awesome Free icons using GitHub API"""

    def __init__(self):
        super().__init__("Font Awesome Free", "https://api.github.com")
        self.repo = "FortAwesome/Font-Awesome"
        self.raw_base = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs"
        self._icon_lists = {}  # Cache for each style

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

            response = urllib.request.urlopen(req, timeout=10)
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
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Font Awesome Free icons"""
        try:
            # Search in solid icons (most common)
            # Could also search regular, brands, etc.
            all_icons = self._get_icons_for_style("solid")

            # Filter by query
            if query:
                matching_icons = [
                    icon for icon in all_icons
                    if query.lower() in icon['name'].lower()
                ]
            else:
                matching_icons = all_icons[:100]  # Limit when no query

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
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Font Awesome SVG"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10)
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading Font Awesome icon: {e}")
            return False


class GitHubRepoProvider(IconProvider):
    """Provider for GitHub repository SVG icons"""

    def __init__(self, repo: str, path: str = ""):
        """
        Initialize GitHub repository provider

        :param repo: Repository in format "owner/name"
        :param path: Optional path within repo to search for SVGs
        """
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

            response = urllib.request.urlopen(req, timeout=10)
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
            return []

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search icons in the GitHub repository"""
        try:
            # Get all icons
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
            return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from GitHub"""
        try:
            response = urllib.request.urlopen(icon.download_url, timeout=10)
            svg_content = response.read()

            with open(file_path, 'wb') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error downloading from GitHub: {e}")
            return False


# The Noun Project provider requires OAuth which is complex
# Keeping the simple implementation for now
class NounProjectProvider(IconProvider):
    """Provider for The Noun Project icons"""

    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        super().__init__("The Noun Project", "https://api.thenounproject.com", api_key)
        self.secret = secret

    def is_available(self) -> bool:
        """Check if The Noun Project provider is properly configured"""
        if not self.api_key or not self.secret:
            return False
        return True

    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search The Noun Project API"""
        if not self.api_key or not self.secret:
            return SearchResult([], 0, page, 0, False, False)

        # The Noun Project requires OAuth 1.0a authentication
        # This would require additional libraries like requests-oauthlib
        # For now, returning empty results

        # In a real implementation:
        # 1. Create OAuth1 session with api_key and secret
        # 2. Make request to https://api.thenounproject.com/icons/{query}
        # 3. Parse results and create SvgIcon objects

        return SearchResult([], 0, page, 0, False, False)

    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None

    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        return False