#!/usr/bin/env python3
"""
Simple test to verify search results for "school"
"""

# Simulate the search logic from providers
def test_material_symbols():
    common_icons = [
        "home", "house", "arrow_back", "arrow_forward", "arrow_upward", "arrow_downward",
        "public", "school", "share", "whatshot",  # school is here
        # ... truncated for brevity
    ]

    query = "school"
    query_lower = query.lower()
    matching_icons = [icon for icon in common_icons if query_lower in icon.lower()]

    print(f"Material Symbols search for '{query}':")
    print(f"  Matching icons: {matching_icons}")
    print(f"  Count: {len(matching_icons)}")
    return matching_icons

def test_maki():
    maki_icons = [
        "art-gallery", "college", "library", "monument", "museum", "music", "school",
        "restaurant-seafood", "roadblock", "school", "shelter", "shoe", "shop",
        # ... truncated for brevity
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_icons = []
    for icon in maki_icons:
        if icon not in seen:
            seen.add(icon)
            unique_icons.append(icon)
    maki_icons = unique_icons

    query = "school"
    query_lower = query.lower()
    matching_icons = [icon for icon in maki_icons if query_lower in icon.lower()]

    print(f"\nMaki search for '{query}':")
    print(f"  All icons sample: {maki_icons[:10]}...")
    print(f"  Matching icons: {matching_icons}")
    print(f"  Count: {len(matching_icons)}")

    # Check if there's a school-specific icon
    print(f"  'school' in list: {'school' in maki_icons}")
    return matching_icons

def test_font_awesome():
    fa_icons = [
        "university", "graduation-cap", "school", "chalkboard", "chalkboard-teacher",
        "preschool", "high-school", "elementary-school",  # These might not exist
        # ... truncated for brevity
    ]

    # Remove duplicates
    seen = set()
    unique_icons = []
    for icon in fa_icons:
        if icon not in seen:
            seen.add(icon)
            unique_icons.append(icon)
    fa_icons = unique_icons

    query = "school"
    query_lower = query.lower()
    matching_icons = [icon for icon in fa_icons if query_lower in icon.lower()]

    print(f"\nFont Awesome search for '{query}':")
    print(f"  Matching icons: {matching_icons}")
    print(f"  Count: {len(matching_icons)}")
    return matching_icons

def test_pagination():
    # Simulate having multiple results but pagination limiting them
    all_results = ["school", "preschool", "school-bus", "school-flag", "school-circle"]
    per_page = 20  # Default
    page = 1

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_results = all_results[start_idx:end_idx]

    print(f"\nPagination test:")
    print(f"  All results: {all_results}")
    print(f"  Page {page} results (per_page={per_page}): {page_results}")
    print(f"  Count on page: {len(page_results)}")

# Run tests
print("="*50)
print("Testing search for 'school'")
print("="*50)

ms_results = test_material_symbols()
maki_results = test_maki()
fa_results = test_font_awesome()
test_pagination()

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Total results across all providers: {len(ms_results) + len(maki_results) + len(fa_results)}")
print(f"- Material Symbols: {len(ms_results)}")
print(f"- Maki: {len(maki_results)}")
print(f"- Font Awesome: {len(fa_results)}")

# Test preview URLs
print("\n" + "="*50)
print("Testing Preview URLs")
print("="*50)

if ms_results:
    icon_name = ms_results[0]
    url = f"https://fonts.gstatic.com/s/i/materialicons/{icon_name}/v1/24px.svg"
    print(f"Material Symbols URL for '{icon_name}': {url}")

if maki_results:
    icon_name = maki_results[0]
    url = f"https://raw.githubusercontent.com/mapbox/maki/main/icons/{icon_name}.svg"
    print(f"Maki URL for '{icon_name}': {url}")

if fa_results:
    icon_name = fa_results[0]
    url = f"https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/{icon_name}.svg"
    print(f"Font Awesome URL for '{icon_name}': {url}")