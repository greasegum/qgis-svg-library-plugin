#!/usr/bin/env python3
"""
Test the plugin search functionality in QGIS context
Run this in QGIS Python console to debug search issues
"""

def test_plugin_search():
    """Test search through the plugin's UI"""
    print("\n" + "="*60)
    print("Testing SVG Library Plugin Search")
    print("="*60)

    # Import the providers module
    import sys
    import os
    plugin_path = '/root/repo'
    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)

    # Import providers
    from providers import TheNounProjectProvider

    # Test Noun Project provider directly
    print("\n1. Testing TheNounProjectProvider directly:")
    print("-" * 40)

    provider = TheNounProjectProvider()

    # Test search
    query = "cross"
    print(f"\nSearching for: '{query}'")

    try:
        result = provider.search(query, page=1, per_page=20)
        print(f"\nSearch completed:")
        print(f"  - Total results: {result.total_count}")
        print(f"  - Icons returned: {len(result.icons)}")

        if result.icons:
            print(f"\nFirst 3 results:")
            for i, icon in enumerate(result.icons[:3], 1):
                print(f"  {i}. {icon.name} (ID: {icon.id})")
        else:
            print("\n  No icons returned!")

    except Exception as e:
        import traceback
        print(f"\nError during search: {e}")
        traceback.print_exc()

    print("\n" + "="*60)
    print("Test complete - check output above for debugging info")
    print("="*60)

# Run the test
if __name__ == "__main__":
    test_plugin_search()