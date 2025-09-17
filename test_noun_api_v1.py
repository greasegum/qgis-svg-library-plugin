#!/usr/bin/env python3
"""
Test The Noun Project API v1 endpoint
Run this in QGIS Python Console to verify API access
"""

def test_noun_project_v1():
    """Test v1 API directly"""
    print("\n" + "="*60)
    print("Testing The Noun Project API v1")
    print("="*60)

    import sys
    import os

    # Add plugin path
    plugin_path = '/root/repo'
    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)

    # Import the provider
    from providers import TheNounProjectProvider

    print("\n1. Initializing provider...")
    provider = TheNounProjectProvider()

    print("\n2. Testing search with v1 API...")
    query = "arrow"
    print(f"   Searching for: '{query}'")

    try:
        result = provider.search(query, page=1, per_page=5)

        print(f"\n3. Results:")
        print(f"   Total count: {result.total_count}")
        print(f"   Icons returned: {len(result.icons)}")

        if result.icons:
            print(f"\n   First few icons:")
            for i, icon in enumerate(result.icons[:3], 1):
                print(f"   {i}. {icon.name} (ID: {icon.id})")
        else:
            print("\n   ✗ No icons returned - API may be rejecting requests")

    except Exception as e:
        import traceback
        print(f"\n✗ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

    print("\n" + "="*60)

    # Try to help with debugging
    print("\nDEBUGGING TIPS:")
    print("-" * 40)
    print("1. If you see 403 Forbidden:")
    print("   - The API keys may be invalid or revoked")
    print("   - Try registering for new API keys at:")
    print("     https://thenounproject.com/api/")
    print("\n2. To install requests-oauthlib (recommended):")
    print("   Run: exec(open('/root/repo/install_requests.py').read())")
    print("\n3. The v1 API endpoint format is:")
    print("   https://api.thenounproject.com/icons/{query}")
    print("="*60)

if __name__ == "__main__":
    test_noun_project_v1()