# QGIS SVG Library Plugin

A QGIS plugin for browsing online SVG libraries with integrated attribution tracking and compliance features.

## Features

🔍 **Multi-Provider Search**: Browse icons from Material Symbols, Maki, Font Awesome Free, The Noun Project, and GitHub repositories

🎯 **Direct Integration**: Click to download SVGs directly to your QGIS profile and optionally apply as layer symbols

📋 **Attribution Tracking**: Automatic license and attribution tracking with export options for compliance

🎨 **Dockable Interface**: Seamlessly integrated browser that docks within QGIS

⚙️ **Configurable**: Add custom GitHub repositories and API keys for extended provider support

📊 **Project Metadata**: Save attribution information directly to QGIS project files

## Supported Providers

- **Material Symbols** (Google) - No API key required
- **Maki** (Mapbox) - No API key required  
- **Font Awesome Free** - No API key required
- **GitHub Repositories** - Public repos, no API key required
- **The Noun Project** - Requires API key (premium service)

## Installation

1. Download or clone this repository
2. Copy the plugin folder to your QGIS plugins directory:
   - **Windows**: `%APPDATA%/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Enable the plugin in QGIS Plugin Manager
4. Access via Plugins menu or toolbar icon

## Quick Start

1. **Open the browser**: Click the SVG Library Browser icon or use Plugins menu
2. **Search for icons**: Type keywords like "school", "bridge", "home"
3. **Browse results**: View thumbnails from multiple providers
4. **Import icons**: Click any icon to download and optionally apply to selected layer
5. **Track attributions**: View and export license information for compliance

## Configuration

Access settings via the ⚙️ button in the plugin:

### API Keys
- Add The Noun Project credentials for premium icon access
- All other providers work without API keys

### GitHub Repositories
Add custom repositories containing SVG icons:
```
username/repository-name
username/repository-name:path/to/svg/folder
```

### General Settings
- Configure default results per page
- Set auto-apply behavior
- Enable auto-save to project metadata

## Attribution & Compliance

The plugin automatically tracks:
- Icon names, providers, and licenses
- Attribution requirements and license text
- Import dates and file locations

Export options:
- **Text format**: For documentation
- **JSON format**: For programmatic use
- **HTML format**: For web publication
- **Project metadata**: Embedded in QGIS project files

## Development

### Architecture

- **Plugin Core**: `svg_library_plugin.py` - Main QGIS plugin integration
- **UI Components**: `svg_library_dockwidget.py` - Dockable browser interface
- **Provider System**: `icon_providers.py`, `providers.py` - Extensible provider architecture
- **Attribution System**: `attribution_utils.py` - License tracking and compliance
- **Configuration**: `config_dialog.py` - Settings management

### Adding New Providers

1. Inherit from `IconProvider` base class
2. Implement required methods: `search()`, `download_svg()`, `get_icon_details()`
3. Handle authentication and API specifics
4. Register in the provider manager

### Dependencies

- QGIS 3.0+
- Python 3.6+
- `requests` library for HTTP operations

## Screenshots

*Coming soon: Screenshots showing the dockable browser, search results, and attribution tracking*

## License

GNU General Public License v3.0

## Contributing

Contributions welcome! Please:
- Follow existing code patterns
- Include proper attribution tracking for new providers
- Update documentation for new features
- Test with multiple QGIS versions

## Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: See `README_PLUGIN.md` for detailed usage instructions
- **QGIS Community**: Share feedback on QGIS forums and mailing lists

---

*Developed to help QGIS users easily access high-quality SVG icons while maintaining proper attribution and license compliance.*
