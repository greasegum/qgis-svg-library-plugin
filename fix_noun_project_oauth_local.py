#!/usr/bin/env python3
"""
Fix The Noun Project OAuth issue in QGIS - Local Version
Run this in QGIS Python Console
"""

def fix_noun_project():
    """Fix OAuth for The Noun Project"""
    print("\n" + "="*60)
    print("Fixing The Noun Project OAuth")
    print("="*60)

    import sys
    import subprocess
    import os

    # Step 1: Find the actual plugin path
    print("\n1. Locating plugin installation...")

    # Try to find the plugin in common QGIS plugin paths
    possible_paths = []

    # Get the path from the error message you showed
    # This is the actual path on your system
    if sys.platform == 'darwin':  # macOS
        home = os.path.expanduser('~')
        plugin_paths = [
            f"{home}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-svg-library-plugin-terragon-analyze-test-plugin",
            f"{home}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/svg_library",
            f"{home}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-svg-library-plugin"
        ]
    elif sys.platform == 'win32':  # Windows
        plugin_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'QGIS', 'QGIS3', 'profiles', 'default', 'python', 'plugins', 'qgis-svg-library-plugin-terragon-analyze-test-plugin'),
            os.path.join(os.environ.get('APPDATA', ''), 'QGIS', 'QGIS3', 'profiles', 'default', 'python', 'plugins', 'svg_library')
        ]
    else:  # Linux
        home = os.path.expanduser('~')
        plugin_paths = [
            f"{home}/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis-svg-library-plugin-terragon-analyze-test-plugin",
            f"{home}/.local/share/QGIS/QGIS3/profiles/default/python/plugins/svg_library"
        ]

    # Find which path exists
    plugin_path = None
    for path in plugin_paths:
        if os.path.exists(path):
            plugin_path = path
            print(f"   ✓ Found plugin at: {path}")
            break

    if not plugin_path:
        # Try to find it from the providers module if it's already imported
        try:
            import providers
            plugin_path = os.path.dirname(providers.__file__)
            print(f"   ✓ Found plugin from import at: {plugin_path}")
        except:
            print("   ⚠ Could not find plugin path automatically")
            print("   Please provide the path manually")
            return

    # Step 2: Check current status
    print("\n2. Checking current OAuth library status...")
    try:
        import requests
        from requests_oauthlib import OAuth1
        print("   ✓ requests-oauthlib is already installed!")
        oauth_available = True
    except ImportError as e:
        print(f"   ✗ OAuth library not found: {e}")
        oauth_available = False

    # Step 3: Install if needed
    if not oauth_available:
        print("\n3. Installing requests-oauthlib...")
        print("   This may take a moment...")

        try:
            # Try to install
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--user', 'requests', 'requests-oauthlib'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("   ✓ Installation successful!")

                # Try to import again
                try:
                    import requests
                    from requests_oauthlib import OAuth1
                    print("   ✓ Libraries loaded successfully!")
                    oauth_available = True
                except ImportError:
                    print("   ⚠ Libraries installed but not yet loaded.")
                    print("   → Please restart QGIS to use the new libraries")
            else:
                print("   ✗ Installation failed:")
                if 'externally-managed-environment' in result.stderr:
                    print("   Your system has restrictions on pip installations.")
                    print("   Trying alternative installation method...")

                    # Try with --break-system-packages flag (for newer systems)
                    result2 = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages', 'requests', 'requests-oauthlib'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result2.returncode == 0:
                        print("   ✓ Alternative installation successful!")
                        oauth_available = True
                    else:
                        print(f"   Error: {result.stderr[:200]}")
                else:
                    print(f"   Error: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            print("   ✗ Installation timed out")
        except Exception as e:
            print(f"   ✗ Installation error: {e}")

    # Step 4: Test if it works now
    if oauth_available:
        print("\n4. Testing The Noun Project with requests-oauthlib...")

        # Add plugin path to Python path
        if plugin_path and plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        # Force reload the module
        import importlib
        if 'providers' in sys.modules:
            print("   Reloading providers module...")
            importlib.reload(sys.modules['providers'])
        else:
            import providers

        from providers import TheNounProjectProvider

        provider = TheNounProjectProvider()
        print(f"   Provider initialized")

        # Test a search
        try:
            result = provider.search("test", page=1, per_page=1)
            if result and result.total_count > 0:
                print(f"   ✓ OAuth is working! Found {result.total_count} results.")
            else:
                print("   ⚠ Search completed but no results returned")
        except Exception as e:
            print(f"   ✗ Search failed: {e}")

    # Step 5: Provide test code with correct path
    if plugin_path:
        print("\n5. Test code for manual testing:")
        print("-" * 40)
        print(f"""
# Test The Noun Project
import sys
plugin_path = r'{plugin_path}'
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

# Reload to get latest changes
import importlib
if 'providers' in sys.modules:
    importlib.reload(sys.modules['providers'])

from providers import TheNounProjectProvider
provider = TheNounProjectProvider()

# Test search
result = provider.search("arrow", page=1, per_page=5)
print(f"Results: {{result.total_count if result else 0}}")
if result and result.icons:
    for icon in result.icons[:3]:
        print(f"  - {{icon.name}}")
""")
        print("-" * 40)

    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    if oauth_available:
        print("✓ OAuth libraries are available")
        print("✓ The Noun Project should work now")
        print("\nTry searching again in the plugin!")
    else:
        print("⚠ OAuth libraries could not be installed automatically")
        print("\nManual installation options:")
        print("\n1. In terminal (macOS/Linux):")
        print(f"   {sys.executable} -m pip install --user requests requests-oauthlib")
        print("\n2. Or with conda if using conda:")
        print("   conda install requests requests-oauthlib")
        print("\n3. Or with homebrew Python:")
        print("   pip3 install requests requests-oauthlib")
        print("\nAfter installation, restart QGIS and run this script again.")

    if plugin_path:
        print(f"\nPlugin location: {plugin_path}")

    print("="*60)

if __name__ == "__main__":
    fix_noun_project()