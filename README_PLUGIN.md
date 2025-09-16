# SVG Library Browser Plugin Documentation

## Overview

The SVG Library Browser is a QGIS plugin that provides a dockable browser for searching and importing SVG icons from multiple online providers. It supports The Noun Project, Material Symbols, Maki, Font Awesome Free, and GitHub repositories containing SVG icons.

## Features

- **Multi-Provider Search**: Search across multiple icon libraries simultaneously
- **Dockable Interface**: Integrated browser that docks within QGIS
- **Attribution Tracking**: Automatic tracking of icon licenses and attributions
- **Project Integration**: Save attributions to QGIS project metadata for compliance
- **Symbol Application**: Directly apply imported SVGs as symbols to vector layers
- **Configurable Providers**: Add custom GitHub repositories and API keys

## Installation

1. Copy the plugin folder to your QGIS plugins directory
2. Enable the plugin in QGIS Plugin Manager
3. The SVG Library Browser will appear in the Plugins menu

## Usage

### Basic Search

1. Open the SVG Library Browser from the Plugins menu or toolbar
2. Enter search terms in the search box (e.g., "school", "bridge", "home")
3. Click Search or press Enter
4. Browse thumbnails from different providers
5. Click on any icon to download and import it

### Configuration

Click the ⚙ (settings) button to configure:

- **API Keys**: Add your The Noun Project API credentials
- **GitHub Repositories**: Add custom repositories containing SVG icons
- **General Settings**: Configure default behavior and thumbnail sizes

### Icon Providers

#### Included Providers

1. **Material Symbols**: Google's Material Design icons (no API key required)
2. **Maki**: Mapbox's open-source icon set for maps (no API key required)
3. **Font Awesome Free**: Popular icon library (no API key required)
4. **GitHub Repositories**: Any public GitHub repo with SVG files
5. **The Noun Project**: Premium icon library (requires API key)

#### Adding GitHub Repositories

In Settings > GitHub Repos tab, add repositories in the format:
```
username/repository-name
username/repository-name:path/to/svg/folder
```

Example:
```
tabler/tabler-icons
feathericons/feather
ionic-team/ionicons:src/svg
```

### Attribution Management

The plugin automatically tracks:
- Icon name and provider
- License information
- Attribution requirements
- Import date and file location

You can:
- View attributions in the plugin panel
- Export attributions as Text, JSON, or HTML
- Save attributions to QGIS project metadata
- Clear attribution history

### Applying Icons to Layers

1. Select a vector layer in QGIS
2. Check "Auto-apply to selected layer" in the plugin
3. Click any icon to automatically apply it as the layer symbol
4. The SVG will be saved to your QGIS profile SVG directory

### File Locations

Downloaded SVGs are saved to your QGIS profile SVG directory, typically:
- **Windows**: `%APPDATA%/QGIS/QGIS3/profiles/default/svg/`
- **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/svg/`
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/svg/`

## API Keys

### The Noun Project

1. Register at [thenounproject.com/developers/](https://thenounproject.com/developers/)
2. Create a new application to get API key and secret
3. Add credentials in plugin Settings > API Keys tab

Note: The Noun Project requires proper OAuth 1.0a authentication. The current implementation includes a demo version that creates sample icons.

## Compliance and Legal

### License Tracking

The plugin tracks license information for each imported icon:
- Creative Commons licenses (CC0, CC BY, etc.)
- Proprietary licenses
- Attribution requirements

### Project Metadata

Enable "Auto-save attributions to project metadata" to automatically store attribution information in your QGIS project files. This ensures compliance when sharing projects or publications.

### Export Options

Export attribution information for:
- **Legal compliance**: Include in project documentation
- **Publications**: Add to academic papers or reports
- **Client deliverables**: Provide license information

## Troubleshooting

### Common Issues

1. **No search results**: Check internet connectivity and API credentials
2. **Download failures**: Verify provider availability and network access
3. **Symbol not applied**: Ensure a vector layer is selected
4. **Missing icons**: Check QGIS SVG paths in settings

### Error Messages

- **"No SVG paths configured"**: QGIS installation issue, reinstall QGIS
- **"Failed to download SVG"**: Network or provider issue, try again later
- **"Please select a vector layer"**: Select a vector layer before importing

### Getting Help

- Check QGIS logs for detailed error messages
- Verify plugin installation in QGIS Plugin Manager
- Ensure internet connectivity for provider access

## Development

### Plugin Structure

```
svg_library_plugin/
├── __init__.py                 # Plugin entry point
├── svg_library_plugin.py      # Main plugin class
├── svg_library_dockwidget.py   # Main UI widget
├── icon_providers.py          # Base provider classes
├── providers.py               # Specific provider implementations
├── attribution_utils.py       # Attribution and license tracking
├── config_dialog.py           # Settings dialog
├── metadata.txt               # Plugin metadata
└── requirements.txt           # Python dependencies
```

### Extending Providers

To add a new icon provider:

1. Inherit from `IconProvider` class
2. Implement required methods: `search()`, `download_svg()`, `get_icon_details()`
3. Register the provider in `setupProviders()` method

### Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- New providers include proper attribution tracking
- UI changes maintain consistency with QGIS design
- Documentation is updated for new features

## License

This plugin is released under the GNU General Public License v3.0.

## Credits

Developed for the QGIS community to provide easy access to high-quality SVG icons with proper attribution tracking and license compliance.