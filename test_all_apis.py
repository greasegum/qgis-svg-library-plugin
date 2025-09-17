#!/usr/bin/env python3
"""
Comprehensive API testing for all SVG icon providers
Tests each provider's search and download functionality
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the base classes first
from icon_providers import IconProvider, SvgIcon, SearchResult

# Then import providers
import providers

NounProjectProvider = providers.NounProjectProvider
MaterialSymbolsProvider = providers.MaterialSymbolsProvider
MakiProvider = providers.MakiProvider
FontAwesomeFreeProvider = providers.FontAwesomeFreeProvider
GitHubRepoProvider = providers.GitHubRepoProvider

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_provider(provider, provider_name, test_queries=None):
    """Test a single provider with various queries"""
    if test_queries is None:
        test_queries = ["home", "user", "settings", "search", "arrow"]

    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Testing: {provider_name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    results = {
        'provider': provider_name,
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }

    # Test each query
    for query in test_queries:
        print(f"\n{Colors.BOLD}Query: '{query}'{Colors.END}")

        try:
            # Perform search
            search_result = provider.search(query, page=1, per_page=5)

            if search_result.icons:
                print(f"{Colors.GREEN}✓ Found {search_result.total_count} total results{Colors.END}")
                print(f"  Showing {len(search_result.icons)} on page {search_result.current_page}/{search_result.total_pages}")

                # Display first few results
                for i, icon in enumerate(search_result.icons[:3], 1):
                    print(f"\n  {i}. {Colors.BOLD}{icon.name}{Colors.END}")
                    print(f"     ID: {icon.id}")
                    print(f"     Tags: {', '.join(icon.tags[:5]) if icon.tags else 'None'}")
                    if icon.preview_url:
                        print(f"     Preview: {icon.preview_url[:80]}...")
                    if icon.download_url:
                        print(f"     Download: {icon.download_url[:80]}...")

                # Test download for first icon
                if search_result.icons[0].download_url:
                    test_icon = search_result.icons[0]
                    test_file = f"/tmp/test_{provider_name}_{query}.svg"

                    print(f"\n  {Colors.YELLOW}Testing download for: {test_icon.name}{Colors.END}")
                    success = provider.download_svg(test_icon, test_file)

                    if success and os.path.exists(test_file):
                        file_size = os.path.getsize(test_file)
                        print(f"  {Colors.GREEN}✓ Downloaded successfully ({file_size} bytes){Colors.END}")

                        # Check if it's valid SVG
                        with open(test_file, 'r') as f:
                            content = f.read(200)
                            if '<svg' in content.lower():
                                print(f"  {Colors.GREEN}✓ Valid SVG file{Colors.END}")
                            else:
                                print(f"  {Colors.RED}✗ Invalid SVG content{Colors.END}")

                        # Clean up
                        os.remove(test_file)
                    else:
                        print(f"  {Colors.RED}✗ Download failed{Colors.END}")

                results['tests'].append({
                    'query': query,
                    'status': 'success',
                    'count': search_result.total_count,
                    'results': len(search_result.icons)
                })

            else:
                print(f"{Colors.YELLOW}⚠ No results found{Colors.END}")
                results['tests'].append({
                    'query': query,
                    'status': 'no_results',
                    'count': 0
                })

        except urllib.error.HTTPError as e:
            print(f"{Colors.RED}✗ HTTP Error {e.code}: {e.reason}{Colors.END}")
            results['tests'].append({
                'query': query,
                'status': 'http_error',
                'error': f"{e.code}: {e.reason}"
            })

        except urllib.error.URLError as e:
            print(f"{Colors.RED}✗ Connection Error: {e.reason}{Colors.END}")
            results['tests'].append({
                'query': query,
                'status': 'connection_error',
                'error': str(e.reason)
            })

        except Exception as e:
            print(f"{Colors.RED}✗ Error: {str(e)}{Colors.END}")
            results['tests'].append({
                'query': query,
                'status': 'error',
                'error': str(e)
            })

    return results

def test_noun_project():
    """Test The Noun Project API with obfuscated credentials"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Testing API Key Deobfuscation...{Colors.END}")

    provider = NounProjectProvider()

    # Check if deobfuscation worked
    if provider.api_key and provider.api_key != "":
        print(f"{Colors.GREEN}✓ API key deobfuscated successfully{Colors.END}")
        print(f"  Key starts with: {provider.api_key[:8]}...{provider.api_key[-4:]}")
    else:
        print(f"{Colors.RED}✗ API key deobfuscation failed{Colors.END}")
        return None

    if provider.secret and provider.secret != "":
        print(f"{Colors.GREEN}✓ Secret deobfuscated successfully{Colors.END}")
        masked_secret = provider.secret[:4] + '*' * (len(provider.secret) - 8) + provider.secret[-4:]
        print(f"  Secret: {masked_secret}")
    else:
        print(f"{Colors.RED}✗ Secret deobfuscation failed{Colors.END}")

    # Test with different queries
    queries = ["computer", "cloud", "data", "network", "security"]
    return test_provider(provider, "The Noun Project", queries)

def test_material_symbols():
    """Test Material Symbols API"""
    provider = MaterialSymbolsProvider()
    queries = ["home", "settings", "account", "search", "favorite"]
    return test_provider(provider, "Material Symbols", queries)

def test_maki():
    """Test Maki (Mapbox) icons API"""
    provider = MakiProvider()
    queries = ["airport", "bank", "hospital", "school", "park"]
    return test_provider(provider, "Maki (Mapbox)", queries)

def test_font_awesome():
    """Test Font Awesome Free API"""
    provider = FontAwesomeFreeProvider()
    queries = ["user", "heart", "star", "check", "times"]
    return test_provider(provider, "Font Awesome Free", queries)

def test_github_repo():
    """Test GitHub Repository API with a sample repo"""
    # Test with Feather icons repo
    provider = GitHubRepoProvider("feathericons/feather", "icons")
    queries = ["arrow", "edit", "file", "home", "user"]
    return test_provider(provider, "GitHub: feathericons/feather", queries)

def main():
    """Run all API tests"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("SVG LIBRARY PLUGIN - COMPREHENSIVE API TEST")
    print("=" * 60)
    print(f"{Colors.END}")

    all_results = []

    # Test each provider
    providers_to_test = [
        ("The Noun Project", test_noun_project),
        ("Material Symbols", test_material_symbols),
        ("Maki (Mapbox)", test_maki),
        ("Font Awesome Free", test_font_awesome),
        ("GitHub Repository", test_github_repo)
    ]

    success_count = 0
    failed_providers = []

    for provider_name, test_func in providers_to_test:
        print(f"\n{Colors.BOLD}Starting test for {provider_name}...{Colors.END}")

        try:
            result = test_func()
            if result:
                all_results.append(result)
                success_count += 1
            else:
                failed_providers.append(provider_name)
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to test {provider_name}: {str(e)}{Colors.END}")
            failed_providers.append(provider_name)

    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

    print(f"\n{Colors.BOLD}Providers Tested:{Colors.END} {len(providers_to_test)}")
    print(f"{Colors.GREEN}✓ Successful:{Colors.END} {success_count}")

    if failed_providers:
        print(f"{Colors.RED}✗ Failed:{Colors.END} {len(failed_providers)}")
        for provider in failed_providers:
            print(f"  - {provider}")

    # Save detailed results
    results_file = "/root/repo/API_TEST_RESULTS.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{Colors.BOLD}Detailed results saved to:{Colors.END} {results_file}")

    # Performance notes
    print(f"\n{Colors.BOLD}{Colors.YELLOW}Performance Notes:{Colors.END}")
    print("1. GitHub API has rate limits (60/hour without auth)")
    print("2. The Noun Project requires valid OAuth credentials")
    print("3. Material Symbols may have large result sets")
    print("4. Network latency affects all API calls")

    return all_results

if __name__ == "__main__":
    main()