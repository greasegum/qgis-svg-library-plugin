#!/usr/bin/env python3
"""Simple OAuth installer for QGIS - single execution"""
import subprocess, sys
try:
    import requests
    from requests_oauthlib import OAuth1
    print("✓ OAuth libraries already installed!")
except ImportError:
    print("Installing OAuth libraries...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'requests', 'requests-oauthlib'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Installation successful! Please restart QGIS.")
    else:
        print("Trying with --break-system-packages...")
        result2 = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages', 'requests', 'requests-oauthlib'], capture_output=True, text=True)
        if result2.returncode == 0:
            print("✓ Installation successful! Please restart QGIS.")
        else:
            print("Installation failed. Error:", result2.stderr[:200])
            print("\nPlease install manually in Terminal:")
            print(f"{sys.executable} -m pip install --user requests requests-oauthlib")