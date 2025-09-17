#!/usr/bin/env python3
"""
Test The Noun Project API with valid obfuscated credentials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from icon_providers import IconProvider, SvgIcon, SearchResult
import providers

def test_noun_project():
    """Test The Noun Project with obfuscated credentials"""
    print("Testing The Noun Project API...")
    print("=" * 60)

    # Create provider (will use obfuscated credentials)
    provider = providers.NounProjectProvider()

    # Verify credentials were loaded
    print(f"API Key loaded: {'Yes' if provider.api_key else 'No'}")
    print(f"Secret loaded: {'Yes' if provider.secret else 'No'}")

    if provider.api_key:
        print(f"API Key (masked): {provider.api_key[:8]}...{provider.api_key[-4:]}")
    if provider.secret:
        print(f"Secret (masked): {provider.secret[:8]}...{provider.secret[-4:]}")

    print("\n" + "=" * 60)

    # Test queries
    test_queries = ["computer", "cloud", "data", "network", "security"]

    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        print("-" * 40)

        try:
            result = provider.search(query, page=1, per_page=5)

            if result.icons:
                print(f"✓ Found {result.total_count} total results")
                print(f"  Showing {len(result.icons)} icons:")

                for i, icon in enumerate(result.icons[:3], 1):
                    print(f"\n  {i}. {icon.name}")
                    print(f"     ID: {icon.id}")
                    print(f"     License: {icon.license}")
                    print(f"     Attribution: {icon.attribution}")
                    if icon.tags:
                        print(f"     Tags: {', '.join(icon.tags[:5])}")

                # Test download
                if result.icons and result.icons[0].download_url:
                    test_icon = result.icons[0]
                    test_file = f"/tmp/noun_project_{query}.svg"

                    print(f"\n  Testing download for: {test_icon.name}")
                    success = provider.download_svg(test_icon, test_file)

                    if success and os.path.exists(test_file):
                        size = os.path.getsize(test_file)
                        print(f"  ✓ Downloaded successfully ({size} bytes)")

                        # Check if valid SVG
                        with open(test_file, 'r') as f:
                            content = f.read(100)
                            if '<svg' in content.lower():
                                print(f"  ✓ Valid SVG file")
                            else:
                                print(f"  ✗ Invalid SVG content")

                        os.remove(test_file)
                    else:
                        print(f"  ✗ Download failed")
            else:
                print(f"✗ No results found")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            if "403" in str(e):
                print("  Authentication failed - check API credentials")
            elif "401" in str(e):
                print("  Unauthorized - invalid OAuth signature")

    print("\n" + "=" * 60)
    print("Test complete!")

    return provider

if __name__ == "__main__":
    test_noun_project()