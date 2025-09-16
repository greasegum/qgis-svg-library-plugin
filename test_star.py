#!/usr/bin/env python3
"""
Test searching for 'star' with the fixed providers
"""

import os
import sys

# Fix imports for standalone testing
with open('providers.py', 'r') as f:
    content = f.read()

temp_content = content.replace('from .icon_providers', 'from icon_providers')
with open('providers_test.py', 'w') as f:
    f.write(temp_content)

from providers_test import MaterialSymbolsProvider, MakiProvider, FontAwesomeFreeProvider

def test_provider(provider, query="star"):
    """Test a single provider"""
    print(f"\n{provider.name}:")
    print("-" * 40)

    try:
        result = provider.search(query)
        print(f"Total results: {result.total_count}")
        print(f"Icons on page: {len(result.icons)}")

        if result.icons:
            print(f"\nFirst 3 results:")
            for i, icon in enumerate(result.icons[:3]):
                print(f"  {i+1}. {icon.name}")
                print(f"     ID: {icon.id}")
                print(f"     Preview: {icon.preview_url}")
        else:
            print("  No results found")

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

# Test each provider
print("="*50)
print(f"Testing search for 'star'")
print("="*50)

# Material Symbols
ms = MaterialSymbolsProvider()
test_provider(ms, "star")

# Maki
maki = MakiProvider()
test_provider(maki, "star")

# Font Awesome
fa = FontAwesomeFreeProvider()
test_provider(fa, "star")

# Clean up
os.unlink('providers_test.py')

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print("If any provider returns 0 results, check:")
print("1. API rate limits (GitHub allows 60 requests/hour)")
print("2. Network connectivity")
print("3. Provider-specific API changes")