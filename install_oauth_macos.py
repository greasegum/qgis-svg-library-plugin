#!/usr/bin/env python3
"""
Install OAuth libraries for QGIS on macOS
This script handles macOS-specific installation challenges
Run this in QGIS Python Console
"""

def install_oauth_libraries():
    """Install requests and requests-oauthlib for QGIS on macOS"""
    print("\n" + "="*60)
    print("Installing OAuth Libraries for QGIS (macOS)")
    print("="*60)

    import sys
    import subprocess
    import os

    # Check if already installed
    print("\n1. Checking current installation status...")
    has_requests = False
    has_oauthlib = False

    try:
        import requests
        has_requests = True
        print(f"   ✓ requests {requests.__version__} is installed")
    except ImportError:
        print("   ✗ requests is not installed")

    try:
        from requests_oauthlib import OAuth1
        has_oauthlib = True
        print("   ✓ requests-oauthlib is installed")
    except ImportError:
        print("   ✗ requests-oauthlib is not installed")

    if has_requests and has_oauthlib:
        print("\n✓ All OAuth libraries are already installed!")
        test_oauth()
        return True

    # Installation needed
    print("\n2. Installing missing libraries...")
    print(f"   Python executable: {sys.executable}")

    # Different installation methods for macOS
    installation_methods = [
        # Method 1: Standard pip with user flag
        {
            'name': 'Standard pip install (user)',
            'command': [sys.executable, '-m', 'pip', 'install', '--user', 'requests', 'requests-oauthlib']
        },
        # Method 2: With break-system-packages (for newer Python)
        {
            'name': 'pip with break-system-packages',
            'command': [sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages', 'requests', 'requests-oauthlib']
        },
        # Method 3: Direct to site-packages
        {
            'name': 'Direct to QGIS packages',
            'command': [sys.executable, '-m', 'pip', 'install', '--target',
                       os.path.join(os.path.dirname(sys.executable), '..', 'Resources', 'python', 'site-packages'),
                       'requests', 'requests-oauthlib']
        }
    ]

    success = False
    for method in installation_methods:
        print(f"\n   Trying: {method['name']}...")
        try:
            result = subprocess.run(
                method['command'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"   ✓ Success with {method['name']}")
                success = True
                break
            else:
                print(f"   ✗ Failed: {result.stderr[:100]}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")

    if not success:
        print("\n3. Manual installation instructions:")
        print("-" * 40)
        print("Since automatic installation failed, try these methods:")
        print("\nOption A - In Terminal:")
        print("1. Open Terminal")
        print("2. Run these commands:")
        print(f"   {sys.executable} -m pip install --user requests requests-oauthlib")
        print("\nOption B - Using Homebrew Python:")
        print("1. Install homebrew if not installed: https://brew.sh")
        print("2. In Terminal run:")
        print("   brew install python3")
        print("   pip3 install requests requests-oauthlib")
        print("3. Link libraries to QGIS (run in QGIS Python Console):")
        print("""
import sys
import site
# Add homebrew site-packages to path
homebrew_packages = '/opt/homebrew/lib/python3.11/site-packages'  # Adjust version if needed
if homebrew_packages not in sys.path:
    sys.path.append(homebrew_packages)
""")
        return False

    # Test if installation worked
    print("\n4. Testing installation...")
    try:
        # Try importing again
        import importlib
        importlib.invalidate_caches()

        import requests
        from requests_oauthlib import OAuth1
        print("   ✓ Libraries successfully loaded!")
        test_oauth()
        return True
    except ImportError as e:
        print(f"   ⚠ Libraries installed but not loaded: {e}")
        print("   → Please restart QGIS to complete installation")
        return False


def test_oauth():
    """Test OAuth functionality"""
    print("\n5. Testing OAuth with The Noun Project...")

    import sys
    import os

    # Find plugin path
    home = os.path.expanduser('~')
    plugin_path = f"{home}/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis-svg-library-plugin-terragon-analyze-test-plugin"

    if not os.path.exists(plugin_path):
        # Try to find from imported module
        try:
            import providers
            plugin_path = os.path.dirname(providers.__file__)
        except:
            print("   Could not find plugin path")
            return

    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)

    try:
        # Force reload to use new libraries
        import importlib
        if 'providers' in sys.modules:
            importlib.reload(sys.modules['providers'])

        from providers import TheNounProjectProvider

        provider = TheNounProjectProvider()

        # Check which OAuth method is being used
        try:
            import requests
            from requests_oauthlib import OAuth1
            print("   Using: requests-oauthlib (reliable)")
        except:
            print("   Using: manual OAuth (less reliable)")

        # Test search
        result = provider.search("test", page=1, per_page=1)

        if result and result.total_count > 0:
            print(f"   ✓ OAuth working! Found {result.total_count} results")
        else:
            print("   ⚠ No results returned")

    except Exception as e:
        print(f"   ✗ Error: {e}")


def main():
    """Main function"""
    success = install_oauth_libraries()

    print("\n" + "="*60)
    print("Installation Complete")
    print("="*60)

    if success:
        print("✓ OAuth libraries are ready to use")
        print("✓ The Noun Project searches should work now")
        print("\nThe plugin will now use the reliable requests-oauthlib")
    else:
        print("⚠ Manual installation required")
        print("Follow the instructions above, then restart QGIS")

    print("="*60)


if __name__ == "__main__":
    main()