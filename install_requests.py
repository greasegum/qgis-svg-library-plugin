#!/usr/bin/env python3
"""
Install requests and requests-oauthlib in QGIS Python environment
Run this in QGIS Python Console
"""

import subprocess
import sys

def install_requests_in_qgis():
    """Install requests and requests-oauthlib"""
    print("Installing requests and requests-oauthlib for QGIS...")

    try:
        # Try to import first
        import requests
        from requests_oauthlib import OAuth1
        print("✓ requests and requests-oauthlib are already installed!")
        return True
    except ImportError:
        pass

    # Get the Python executable path
    python_exe = sys.executable
    print(f"Python executable: {python_exe}")

    # Try to install using pip
    packages = ['requests', 'requests-oauthlib']

    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            # Try with --user flag first (doesn't require admin rights)
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'install', '--user', package],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"✓ {package} installed successfully")
            else:
                print(f"Error installing {package}:")
                print(result.stderr)

                # Try without --user flag
                print(f"Trying to install {package} without --user flag...")
                result = subprocess.run(
                    [python_exe, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print(f"✓ {package} installed successfully")
                else:
                    print(f"✗ Failed to install {package}")
                    print(result.stderr)

        except Exception as e:
            print(f"Error: {e}")

    # Test the installation
    print("\nTesting installation...")
    try:
        import requests
        from requests_oauthlib import OAuth1
        print("✓ Successfully imported requests and requests-oauthlib!")
        print(f"  requests version: {requests.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

if __name__ == "__main__":
    success = install_requests_in_qgis()
    if success:
        print("\n" + "="*60)
        print("SUCCESS: requests-oauthlib is now available!")
        print("The Noun Project searches should now work properly.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("WARNING: Could not install requests-oauthlib")
        print("The plugin will use the fallback OAuth implementation")
        print("="*60)