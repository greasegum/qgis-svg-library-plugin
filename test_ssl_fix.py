#!/usr/bin/env python3
"""
Test that SSL fixes work for all providers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import providers

def test_providers_with_ssl():
    """Test all providers with SSL context"""

    print("Testing SSL fixes for all providers...")
    print("=" * 60)

    # Test each provider
    test_cases = [
        ("Material Symbols", providers.MaterialSymbolsProvider(), "home"),
        ("Maki", providers.MakiProvider(), "airport"),
        ("Font Awesome", providers.FontAwesomeFreeProvider(), "star"),
        ("Noun Project", providers.NounProjectProvider(), "star"),
        ("GitHub", providers.GitHubRepoProvider("feathericons/feather", "icons"), "arrow")
    ]

    for provider_name, provider, query in test_cases:
        print(f"\n{provider_name}: Testing with query '{query}'")
        print("-" * 40)

        try:
            result = provider.search(query, page=1, per_page=5)

            if result and result.icons:
                print(f"✅ SUCCESS - Found {len(result.icons)} icons")
                print(f"   First icon: {result.icons[0].name}")

                # Try to download the first icon
                if result.icons[0].download_url:
                    test_file = f"/tmp/test_{provider_name.replace(' ', '_')}.svg"
                    success = provider.download_svg(result.icons[0], test_file)
                    if success:
                        print(f"   ✅ Download successful")
                        if os.path.exists(test_file):
                            os.remove(test_file)
                    else:
                        print(f"   ❌ Download failed")
            else:
                print(f"❌ No results returned")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            if "SSL" in str(e) or "certificate" in str(e):
                print("   SSL/Certificate issue detected!")

    print("\n" + "=" * 60)
    print("SSL test complete!")

if __name__ == "__main__":
    test_providers_with_ssl()