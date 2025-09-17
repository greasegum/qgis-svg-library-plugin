#!/usr/bin/env python3
"""
Test the fixed OAuth implementation
Run this in QGIS Python Console
"""

def test_oauth_fix():
    """Test the fixed OAuth implementation"""
    print("\n" + "="*60)
    print("Testing Fixed OAuth Implementation")
    print("="*60)

    import sys
    plugin_path = '/root/repo'
    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)

    from providers import TheNounProjectProvider

    print("\n1. Testing with fixed OAuth signature generation...")
    provider = TheNounProjectProvider()

    # Test a simple query
    query = "test"
    print(f"\n2. Searching for '{query}'...")

    try:
        result = provider.search(query, page=1, per_page=5)

        print(f"\n3. Results:")
        print(f"   Total count: {result.total_count}")
        print(f"   Icons found: {len(result.icons)}")

        if result.icons:
            print("\n   ✓ SUCCESS! OAuth is working properly")
            print(f"\n   Sample results:")
            for i, icon in enumerate(result.icons[:3], 1):
                print(f"   {i}. {icon.name}")
        else:
            print("\n   ✗ No results returned - OAuth may still be failing")

    except Exception as e:
        print(f"\n   ✗ Error: {e}")

        # Try to provide more specific help
        if "403" in str(e):
            print("\n   The OAuth signature generation may still have issues.")
            print("   Trying to install requests-oauthlib for more reliable OAuth...")

            try:
                import subprocess
                import sys
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--user', 'requests', 'requests-oauthlib'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("\n   ✓ Installed requests-oauthlib successfully!")
                    print("   Try searching again - it should now use the more reliable OAuth library")
                else:
                    print("\n   Could not install requests-oauthlib automatically")
            except:
                pass

    print("\n" + "="*60)
    print("Testing other providers to ensure they still work...")
    print("="*60)

    # Test other providers
    from providers import MaterialSymbolsProvider

    print("\n4. Testing Material Symbols provider...")
    material = MaterialSymbolsProvider()

    try:
        result = material.search("home", page=1, per_page=5)
        if result.icons:
            print(f"   ✓ Material Symbols working: {len(result.icons)} icons found")
        else:
            print("   ✗ Material Symbols returned no results")
    except Exception as e:
        print(f"   ✗ Material Symbols error: {e}")

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    test_oauth_fix()