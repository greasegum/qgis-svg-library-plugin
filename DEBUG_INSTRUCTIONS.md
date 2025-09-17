# Debugging Search Issues in QGIS Plugin

## Current Status
The plugin has been updated with extensive debug logging to help identify why searches might not be returning results.

## How to View Debug Output in QGIS

### Method 1: QGIS Python Console
1. Open QGIS
2. Go to **Plugins → Python Console** (or press `Ctrl+Alt+P`)
3. Load the plugin normally
4. Perform a search
5. Watch the console for debug output

### Method 2: Run QGIS from Terminal
1. Open a terminal
2. Run QGIS from command line:
   ```bash
   # Linux
   qgis

   # macOS
   /Applications/QGIS.app/Contents/MacOS/QGIS

   # Windows
   C:\Program Files\QGIS\bin\qgis.exe
   ```
3. All print statements will appear in the terminal
4. Load the plugin and perform searches

### Method 3: QGIS Log Messages Panel
1. Go to **View → Panels → Log Messages**
2. Look for messages in the "Python" tab
3. Some debug output may appear here

## Debug Output to Expect

When you perform a search, you should see output like:

```
[perform_search] Query: 'home'
[perform_search] Starting search for 'home' page 1
[search_icons] Called with query='home', page=1
[search_icons] Selected provider from combo: 'Material Symbols'
[SearchWorker] Starting search:
  Query: 'home'
  Page: 1
  Per page: 20
  Selected provider: Material Symbols
  Provider found: True
  Calling Material Symbols.search('home', 1, 20)
  Results: 4 icons
[SearchWorker] Emitting results
[display_results] Received results from 1 providers
  Material Symbols: 4 icons
[IconThumbnail] Loading preview for Add Home from https://fonts.gstatic.com/...
[IconThumbnail] Loading preview for Add Home Work from https://fonts.gstatic.com/...
[display_results] Total icons displayed: 4
```

## Common Issues and What to Look For

### Issue 1: No Results Displayed
Look for:
- `[SearchWorker] Results: 0 icons` - API returned no results
- `[display_results] Total icons displayed: 0` - Results received but not displayed
- `ERROR: Provider 'ProviderName' not found!` - Provider selection issue

### Issue 2: Provider Not Found
Check:
- `[search_icons] Selected provider from combo:` - What provider is selected?
- The provider name must match exactly what's registered

### Issue 3: API Errors
Look for:
- HTTP errors (403, 404, etc.)
- Connection timeouts
- OAuth authentication failures

### Issue 4: UI Not Updating
Check:
- `[display_results] Received results from X providers` - Are results being received?
- `[IconThumbnail] Loading preview` - Are thumbnails loading?
- Qt/PyQt errors in the console

## Testing Without QGIS

You can test the search functionality without QGIS:

```bash
# Test all APIs
python3 test_all_apis.py

# Test UI search flow
python3 test_ui_search.py

# Debug search with detailed output
python3 debug_search.py
```

## Quick Fixes to Try

### 1. Verify Provider is Selected
- Make sure a provider is selected in the dropdown (not "All Providers" if it exists)
- The current implementation requires selecting a specific provider

### 2. Check Network Connection
- Ensure you have internet connectivity
- Check if you're behind a proxy

### 3. Test with Simple Queries
Try these queries that should definitely return results:
- Material Symbols: "home", "search", "settings"
- Maki: "airport", "bank", "school"
- Font Awesome: "user", "heart", "star"

### 4. Check API Keys (The Noun Project)
If testing The Noun Project:
- Ensure `requests` and `requests-oauthlib` are installed:
  ```bash
  pip install requests requests-oauthlib
  ```

## Reporting Issues

If searches still don't work, please provide:
1. The complete debug output from the console
2. The query you searched for
3. The provider you selected
4. Your QGIS version
5. Your operating system

## Current Known Working State

As of the latest tests:
- ✅ All API providers return results when tested directly
- ✅ Search flow logic works correctly
- ✅ Debug logging is comprehensive
- ✅ The Noun Project works with requests-oauthlib

The issue is likely in:
1. Provider selection in the UI
2. Qt thread communication
3. Network/proxy issues
4. QGIS-specific environment differences