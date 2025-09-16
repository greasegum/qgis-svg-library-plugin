#!/usr/bin/env python3
"""
Test search functionality to debug issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Need to temporarily fix the import
import icon_providers
import providers

# Temporarily modify the import in providers
original_import = "from .icon_providers import IconProvider, SvgIcon, SearchResult"
fixed_import = "from icon_providers import IconProvider, SvgIcon, SearchResult"

# Read and fix providers.py
with open('providers.py', 'r') as f:
    content = f.read()

temp_content = content.replace(original_import, fixed_import)

# Write temporary fixed content
with open('providers_temp.py', 'w') as f:
    f.write(temp_content)

# Import from the fixed file
from icon_providers import IconProviderManager
from providers_temp import MaterialSymbolsProvider, MakiProvider, FontAwesomeFreeProvider

# Clean up
os.unlink('providers_temp.py')

# Create manager and register providers
manager = IconProviderManager()
manager.register_provider(MaterialSymbolsProvider())
manager.register_provider(MakiProvider())
manager.register_provider(FontAwesomeFreeProvider())

# Search for "school"
query = "school"
print(f"\n=== Searching for '{query}' ===\n")

results = manager.search_all(query, page=1, per_page=20)

for provider_name, search_result in results.items():
    print(f"\n{provider_name}:")
    print(f"  Total count: {search_result.total_count}")
    print(f"  Icons on page: {len(search_result.icons)}")

    if search_result.icons:
        for icon in search_result.icons[:5]:  # Show first 5
            print(f"    - {icon.name} ({icon.id})")
            print(f"      Preview URL: {icon.preview_url}")
    else:
        print("    No results")

# Also test the individual providers directly
print("\n=== Direct Provider Test ===\n")

# Material Symbols
ms = MaterialSymbolsProvider()
ms_result = ms.search("school")
print(f"Material Symbols direct search:")
print(f"  Total results: {ms_result.total_count}")
print(f"  Icons returned: {len(ms_result.icons)}")

# Maki
maki = MakiProvider()
maki_result = maki.search("school")
print(f"\nMaki direct search:")
print(f"  Total results: {maki_result.total_count}")
print(f"  Icons returned: {len(maki_result.icons)}")

# Font Awesome
fa = FontAwesomeFreeProvider()
fa_result = fa.search("school")
print(f"\nFont Awesome direct search:")
print(f"  Total results: {fa_result.total_count}")
print(f"  Icons returned: {len(fa_result.icons)}")