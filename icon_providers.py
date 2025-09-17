"""
Base classes and interfaces for SVG icon providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class SvgIcon:
    """Represents an SVG icon with metadata"""
    id: str
    name: str
    url: str
    preview_url: str
    tags: List[str]
    license: str
    attribution: str
    provider: str
    download_url: str
    size: Optional[Tuple[int, int]] = None


@dataclass
class SearchResult:
    """Results from a search query"""
    icons: List[SvgIcon]
    total_count: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class IconProvider(ABC):
    """Abstract base class for SVG icon providers"""
    
    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.session = None  # Will be created lazily if needed
        
    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search for icons by query string"""
        pass
    
    @abstractmethod
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get detailed information about a specific icon"""
        pass
    
    @abstractmethod
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG content to a file"""
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is available and configured properly"""
        try:
            # Basic connectivity test
            import requests
            if not self.session:
                self.session = requests.Session()
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False


class IconProviderManager:
    """Manages multiple icon providers"""
    
    def __init__(self):
        self.providers = {}
        
    def register_provider(self, provider: IconProvider):
        """Register a new icon provider"""
        self.providers[provider.name] = provider
        
    def get_provider(self, name: str) -> Optional[IconProvider]:
        """Get a provider by name"""
        return self.providers.get(name)
        
    def get_available_providers(self) -> List[IconProvider]:
        """Get list of available providers"""
        return [provider for provider in self.providers.values() 
                if provider.is_available()]
        
    def search_all(self, query: str, page: int = 1, per_page: int = 20) -> Dict[str, SearchResult]:
        """Search across all available providers"""
        results = {}
        for provider in self.get_available_providers():
            try:
                results[provider.name] = provider.search(query, page, per_page)
            except Exception as e:
                # Log error but continue with other providers
                print(f"Error searching {provider.name}: {e}")
        return results