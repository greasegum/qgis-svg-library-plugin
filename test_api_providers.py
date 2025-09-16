#!/usr/bin/env python3
"""
Test the API-based providers directly
"""

import sys
import os
import json
import urllib.request
import urllib.error

def test_github_api():
    """Test if we can access GitHub API"""
    print("Testing GitHub API access...")
    try:
        # Test basic GitHub API
        req = urllib.request.Request("https://api.github.com")
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'QGIS-SVG-Plugin')

        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        print("✓ GitHub API is accessible")
        return True
    except Exception as e:
        print(f"✗ GitHub API error: {e}")
        return False

def test_maki_api():
    """Test Maki icon fetching"""
    print("\nTesting Maki icons API...")
    try:
        api_url = "https://api.github.com/repos/mapbox/maki/contents/icons"

        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'QGIS-SVG-Plugin')

        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())

        # Filter for star icons
        star_icons = [item['name'] for item in data if 'star' in item['name'].lower() and item['name'].endswith('.svg')]

        print(f"✓ Found {len(data)} total icons")
        print(f"✓ Star icons found: {star_icons}")
        return star_icons
    except Exception as e:
        print(f"✗ Maki API error: {e}")
        return []

def test_font_awesome_api():
    """Test Font Awesome icon fetching"""
    print("\nTesting Font Awesome API...")
    try:
        api_url = "https://api.github.com/repos/FortAwesome/Font-Awesome/contents/svgs/solid"

        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'QGIS-SVG-Plugin')

        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())

        # Filter for star icons
        star_icons = [item['name'] for item in data if 'star' in item['name'].lower() and item['name'].endswith('.svg')]

        print(f"✓ Found {len(data)} total solid icons")
        print(f"✓ Star icons found: {star_icons[:10]}...")  # Show first 10
        return star_icons
    except Exception as e:
        print(f"✗ Font Awesome API error: {e}")
        return []

def test_material_search():
    """Test Material Symbols search API"""
    print("\nTesting Material Symbols search...")
    try:
        # Search for star in Material Design Icons repo
        search_query = "star extension:svg repo:google/material-design-icons"
        from urllib.parse import quote
        encoded_query = quote(search_query)

        api_url = f"https://api.github.com/search/code?q={encoded_query}&per_page=10"

        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'QGIS-SVG-Plugin')

        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())

        print(f"✓ Search returned {data.get('total_count', 0)} results")

        if 'items' in data:
            for item in data['items'][:5]:  # Show first 5
                print(f"  - {item['path']}")

        return data.get('total_count', 0) > 0
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"✗ Rate limit hit: {e.headers.get('X-RateLimit-Remaining', 'unknown')} requests remaining")
        else:
            print(f"✗ HTTP Error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"✗ Material search error: {e}")
        return False

def test_providers_module():
    """Test if providers module works"""
    print("\nTesting providers module...")
    try:
        # Fix relative import for testing
        with open('providers.py', 'r') as f:
            content = f.read()

        # Check if it's using the API version
        if 'urllib.request' in content:
            print("✓ Providers using API implementation")
        else:
            print("✗ Providers might be using old hardcoded version")

        # Try to import after fixing relative import
        temp_content = content.replace('from .icon_providers', 'from icon_providers')
        with open('providers_test.py', 'w') as f:
            f.write(temp_content)

        from providers_test import MakiProvider, FontAwesomeFreeProvider

        # Test Maki provider
        print("\nTesting MakiProvider...")
        maki = MakiProvider()
        result = maki.search("star")
        print(f"  Results: {result.total_count} icons")
        if result.icons:
            print(f"  First icon: {result.icons[0].name}")
            print(f"  Preview URL: {result.icons[0].preview_url}")

        # Test Font Awesome provider
        print("\nTesting FontAwesomeFreeProvider...")
        fa = FontAwesomeFreeProvider()
        result = fa.search("star")
        print(f"  Results: {result.total_count} icons")
        if result.icons:
            print(f"  First icon: {result.icons[0].name}")
            print(f"  Preview URL: {result.icons[0].preview_url}")

        # Clean up
        os.unlink('providers_test.py')

    except Exception as e:
        print(f"✗ Provider module error: {e}")
        import traceback
        traceback.print_exc()

# Run all tests
print("="*50)
print("API Provider Tests")
print("="*50)

if test_github_api():
    test_maki_api()
    test_font_awesome_api()
    test_material_search()
    test_providers_module()
else:
    print("\nCannot proceed - GitHub API is not accessible")