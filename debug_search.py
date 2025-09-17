#!/usr/bin/env python3
"""
Debug search functionality to see why results aren't showing
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from icon_providers import IconProvider, SvgIcon, SearchResult
import providers

def debug_search(provider_class, provider_name, query="home"):
    """Debug search for a specific provider"""
    print(f"\n{'='*60}")
    print(f"Testing: {provider_name}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")

    try:
        # Create provider instance
        if provider_name == "The Noun Project":
            provider = provider_class()
        elif provider_name == "GitHub":
            provider = provider_class("feathericons/feather", "icons")
        else:
            provider = provider_class()

        print(f"Provider created: {provider.name}")
        print(f"Base URL: {provider.base_url}")

        # Perform search
        print(f"\nCalling search('{query}')...")
        result = provider.search(query, page=1, per_page=5)

        print(f"\nSearch Result object:")
        print(f"  Type: {type(result)}")
        print(f"  Total count: {result.total_count}")
        print(f"  Icons returned: {len(result.icons)}")
        print(f"  Current page: {result.current_page}")
        print(f"  Total pages: {result.total_pages}")
        print(f"  Has next: {result.has_next}")
        print(f"  Has previous: {result.has_previous}")

        if result.icons:
            print(f"\nFirst 3 icons:")
            for i, icon in enumerate(result.icons[:3], 1):
                print(f"\n  {i}. Icon Details:")
                print(f"     ID: {icon.id}")
                print(f"     Name: {icon.name}")
                print(f"     URL: {icon.url}")
                print(f"     Preview URL: {icon.preview_url}")
                print(f"     Download URL: {icon.download_url}")
                print(f"     Tags: {icon.tags[:3] if icon.tags else 'None'}")
                print(f"     License: {icon.license}")
                print(f"     Provider: {icon.provider}")
        else:
            print("\n❌ NO ICONS RETURNED!")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print("\nTraceback:")
        traceback.print_exc()

def test_all_providers():
    """Test all providers"""

    print("="*60)
    print("DEBUGGING SEARCH FUNCTIONALITY")
    print("="*60)

    providers_to_test = [
        (providers.MaterialSymbolsProvider, "Material Symbols"),
        (providers.MakiProvider, "Maki"),
        (providers.FontAwesomeFreeProvider, "Font Awesome Free"),
        (providers.GitHubRepoProvider, "GitHub"),
        (providers.NounProjectProvider, "The Noun Project")
    ]

    for provider_class, provider_name in providers_to_test:
        debug_search(provider_class, provider_name, "home")

def test_specific_queries():
    """Test specific queries that should definitely return results"""
    print("\n" + "="*60)
    print("TESTING SPECIFIC QUERIES")
    print("="*60)

    test_cases = [
        (providers.MaterialSymbolsProvider, "home"),
        (providers.MaterialSymbolsProvider, "search"),
        (providers.MakiProvider, "airport"),
        (providers.FontAwesomeFreeProvider, "user"),
        (providers.NounProjectProvider, "computer")
    ]

    for provider_class, query in test_cases:
        provider = provider_class() if provider_class != providers.GitHubRepoProvider else provider_class("feathericons/feather", "icons")
        provider_name = provider.name

        print(f"\n{provider_name}: Searching for '{query}'...")
        result = provider.search(query)

        if result and result.icons:
            print(f"  ✅ Found {len(result.icons)} results")
        else:
            print(f"  ❌ No results!")

if __name__ == "__main__":
    test_all_providers()
    test_specific_queries()