#!/usr/bin/env python3
"""
Test the search flow as it would happen in the UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from icon_providers import IconProviderManager
from providers import MaterialSymbolsProvider, MakiProvider, FontAwesomeFreeProvider, NounProjectProvider

def test_ui_search_flow():
    """Simulate the UI search flow"""

    # 1. Setup providers like the UI does
    print("1. Setting up provider manager...")
    provider_manager = IconProviderManager()

    # Register providers
    providers_to_add = [
        MaterialSymbolsProvider(),
        MakiProvider(),
        FontAwesomeFreeProvider(),
        NounProjectProvider()  # Will work if requests is available
    ]

    for provider in providers_to_add:
        provider_manager.register_provider(provider)
        print(f"   Registered: {provider.name}")

    print(f"\n   Total providers: {len(provider_manager.providers)}")
    print(f"   Available providers: {list(provider_manager.providers.keys())}")

    # 2. Simulate selecting a specific provider (like from dropdown)
    selected_provider = "Material Symbols"  # This would come from provider_combo.currentData()
    print(f"\n2. Selected provider from dropdown: '{selected_provider}'")

    # 3. Simulate the SearchWorker logic
    query = "home"
    page = 1
    per_page = 20

    print(f"\n3. Searching with query: '{query}'")
    print(f"   Page: {page}, Per page: {per_page}")

    # This is what SearchWorker.run() does:
    if selected_provider:
        provider = provider_manager.get_provider(selected_provider)
        print(f"\n4. Getting provider '{selected_provider}'...")
        print(f"   Provider found: {provider is not None}")

        if provider:
            print(f"   Provider name: {provider.name}")
            print(f"   Provider base URL: {provider.base_url}")

            print(f"\n5. Calling search...")
            result = provider.search(query, page, per_page)

            print(f"\n6. Search results:")
            print(f"   Result type: {type(result)}")
            print(f"   Icons returned: {len(result.icons) if result else 0}")

            if result and result.icons:
                print(f"   Total count: {result.total_count}")
                print(f"   First 3 icons:")
                for i, icon in enumerate(result.icons[:3], 1):
                    print(f"     {i}. {icon.name} (ID: {icon.id})")

            # This would be emitted to display_results
            results = {selected_provider: result}
            print(f"\n7. Results dict to emit: {len(results)} provider(s)")
        else:
            print(f"   ERROR: Provider not found!")
            results = {}
    else:
        print("\n4. No specific provider selected - searching all")
        results = provider_manager.search_all(query, page, per_page)

    # 8. Simulate what display_results would receive
    print(f"\n8. Display results would receive:")
    for provider_name, search_result in results.items():
        if search_result and search_result.icons:
            print(f"   {provider_name}: {len(search_result.icons)} icons")
        else:
            print(f"   {provider_name}: No results")

    return results

if __name__ == "__main__":
    print("="*60)
    print("TESTING UI SEARCH FLOW")
    print("="*60)
    results = test_ui_search_flow()

    print("\n" + "="*60)
    if results:
        total_icons = sum(len(r.icons) if r and r.icons else 0 for r in results.values())
        print(f"SUMMARY: {total_icons} total icons from {len(results)} provider(s)")
    else:
        print("SUMMARY: No results!")
    print("="*60)