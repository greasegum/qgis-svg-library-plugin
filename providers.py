"""
Specific implementations of SVG icon providers
"""

import json
import os
from typing import List, Optional
from urllib.parse import urlencode, quote
import zipfile
import tempfile

from icon_providers import IconProvider, SvgIcon, SearchResult


class NounProjectProvider(IconProvider):
    """Provider for The Noun Project icons"""
    
    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        super().__init__("The Noun Project", "https://api.thenounproject.com", api_key)
        self.secret = secret
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search The Noun Project API"""
        if not self.api_key:
            # Return empty results if no API key
            return SearchResult([], 0, page, 0, False, False)
            
        offset = (page - 1) * per_page
        params = {
            'query': query,
            'limit': per_page,
            'offset': offset
        }
        
        # Note: Actual implementation would need OAuth authentication
        # This is a simplified version
        try:
            url = f"{self.base_url}/icons?" + urlencode(params)
            response = self.session.get(url, headers={'Authorization': f'Bearer {self.api_key}'})
            
            if response.status_code == 200:
                data = response.json()
                icons = []
                for item in data.get('icons', []):
                    icon = SvgIcon(
                        id=str(item['id']),
                        name=item.get('term', ''),
                        url=item.get('icon_url', ''),
                        preview_url=item.get('preview_url', ''),
                        tags=[item.get('term', '')],
                        license=item.get('license_description', 'Creative Commons'),
                        attribution=f"Icon by {item.get('uploader', {}).get('name', 'Unknown')} from the Noun Project",
                        provider=self.name,
                        download_url=item.get('svg_url', '')
                    )
                    icons.append(icon)
                
                total_count = data.get('total_count', len(icons))
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
            print(f"Error searching Noun Project: {e}")
            
        return SearchResult([], 0, page, 0, False, False)
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific icon"""
        # Implementation would fetch detailed icon info
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from The Noun Project"""
        try:
            response = self.session.get(icon.download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading SVG: {e}")
        return False


class MaterialSymbolsProvider(IconProvider):
    """Provider for Material Design Symbols"""
    
    def __init__(self):
        super().__init__("Material Symbols", "https://fonts.googleapis.com/css2")
        # Material Symbols are available via Google Fonts
        self.github_base = "https://raw.githubusercontent.com/google/material-design-icons/master"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Material Symbols (using local index or GitHub API)"""
        # For demo purposes, return some common material icons
        # In a real implementation, you'd have a local index or use GitHub API
        
        common_icons = [
            "home", "search", "menu", "close", "add", "remove", "edit", "delete",
            "save", "settings", "account_circle", "favorite", "star", "share",
            "download", "upload", "folder", "file", "image", "video"
        ]
        
        matching_icons = [icon for icon in common_icons if query.lower() in icon.lower()]
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('_', ' ').title(),
                url=f"https://fonts.google.com/icons?selected=Material+Icons:{icon_name}",
                preview_url=f"https://fonts.gstatic.com/s/i/materialicons/{icon_name}/v1/24px.svg",
                tags=[icon_name],
                license="Apache License 2.0",
                attribution="Material Symbols by Google",
                provider=self.name,
                download_url=f"https://fonts.gstatic.com/s/i/materialicons/{icon_name}/v1/24px.svg"
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
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific Material icon"""
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Material Symbol SVG"""
        try:
            response = self.session.get(icon.download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading Material Symbol: {e}")
        return False


class MakiProvider(IconProvider):
    """Provider for Maki icons (Mapbox)"""
    
    def __init__(self):
        super().__init__("Maki", "https://github.com/mapbox/maki")
        self.raw_base = "https://raw.githubusercontent.com/mapbox/maki/main"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Maki icons"""
        # Common Maki icons for demo
        maki_icons = [
            "airport", "art-gallery", "bank", "bar", "bicycle", "bridge", "bus",
            "cafe", "car", "cemetery", "cinema", "college", "commercial", "fire-station",
            "fuel", "golf", "grocery", "harbor", "hospital", "hotel", "library",
            "monument", "museum", "park", "pharmacy", "police", "post", "religious-christian",
            "restaurant", "school", "stadium", "swimming", "theatre", "zoo"
        ]
        
        matching_icons = [icon for icon in maki_icons if query.lower() in icon.lower()]
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('-', ' ').title(),
                url=f"https://github.com/mapbox/maki/blob/main/icons/{icon_name}-15.svg",
                preview_url=f"{self.raw_base}/icons/{icon_name}-15.svg",
                tags=[icon_name],
                license="CC0 1.0 Universal",
                attribution="Maki Icons by Mapbox",
                provider=self.name,
                download_url=f"{self.raw_base}/icons/{icon_name}-15.svg"
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
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Maki SVG"""
        try:
            response = self.session.get(icon.download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading Maki icon: {e}")
        return False


class FontAwesomeFreeProvider(IconProvider):
    """Provider for Font Awesome Free icons"""
    
    def __init__(self):
        super().__init__("Font Awesome Free", "https://github.com/FortAwesome/Font-Awesome")
        self.raw_base = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Font Awesome Free icons"""
        # Common FA Free icons for demo
        fa_icons = [
            "home", "user", "search", "envelope", "heart", "star", "flag", "music",
            "image", "film", "download", "upload", "edit", "trash", "save", "print",
            "calendar", "clock", "map", "phone", "fax", "wifi", "car", "plane",
            "ship", "train", "bicycle", "shopping-cart", "credit-card", "university"
        ]
        
        matching_icons = [icon for icon in fa_icons if query.lower() in icon.lower()]
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('-', ' ').title(),
                url=f"https://fontawesome.com/icons/{icon_name}",
                preview_url=f"{self.raw_base}/solid/{icon_name}.svg",
                tags=[icon_name],
                license="CC BY 4.0 License",
                attribution="Font Awesome Free by Fonticons",
                provider=self.name,
                download_url=f"{self.raw_base}/solid/{icon_name}.svg"
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
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Font Awesome SVG"""
        try:
            response = self.session.get(icon.download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading Font Awesome icon: {e}")
        return False


class GitHubRepoProvider(IconProvider):
    """Provider for GitHub repositories containing SVG icons"""
    
    def __init__(self, repo_url: str, svg_path: str = ""):
        """
        Initialize GitHub repo provider
        
        :param repo_url: GitHub repository URL (e.g., "username/repo-name")
        :param svg_path: Path within repo where SVGs are located
        """
        super().__init__(f"GitHub: {repo_url}", "https://api.github.com")
        self.repo_url = repo_url
        self.svg_path = svg_path
        self.raw_base = f"https://raw.githubusercontent.com/{repo_url}/main"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search GitHub repository for SVG files"""
        try:
            # Use GitHub API to search for SVG files
            search_url = f"{self.base_url}/search/code"
            params = {
                'q': f'{query} extension:svg repo:{self.repo_url}',
                'page': page,
                'per_page': per_page
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                icons = []
                
                for item in data.get('items', []):
                    filename = item['name']
                    icon_name = os.path.splitext(filename)[0]
                    file_path = item['path']
                    
                    icon = SvgIcon(
                        id=file_path,
                        name=icon_name.replace('-', ' ').replace('_', ' ').title(),
                        url=item['html_url'],
                        preview_url=f"{self.raw_base}/{file_path}",
                        tags=[icon_name],
                        license="See repository license",
                        attribution=f"From {self.repo_url}",
                        provider=self.name,
                        download_url=f"{self.raw_base}/{file_path}"
                    )
                    icons.append(icon)
                
                total_count = data.get('total_count', len(icons))
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
            print(f"Error searching GitHub repo: {e}")
            
        return SearchResult([], 0, page, 0, False, False)
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from GitHub repository"""
        try:
            response = self.session.get(icon.download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading GitHub SVG: {e}")
        return False