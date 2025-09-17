# QGIS Symbology Integration - Development Documentation

## Overview
This document outlines methods to more directly integrate the SVG Library Plugin's icon fetching capabilities with QGIS's native symbology controls. The goal is to make the plugin feel like a natural extension of QGIS rather than a separate tool.

## Integration Methods

### 1. Automatic SVG Path Registration (Priority: HIGH)
**Description**: Automatically register downloaded icons with QGIS's SVG system.

**Implementation**:
```python
from qgis.core import QgsApplication

class SvgPathManager:
    def __init__(self):
        self.plugin_svg_dir = os.path.join(
            QgsApplication.qgisSettingsDirPath(),
            'svg',
            'svg_library_plugin'
        )
        self._ensure_directory()
        self._register_with_qgis()

    def _ensure_directory(self):
        """Create plugin SVG directory if it doesn't exist"""
        os.makedirs(self.plugin_svg_dir, exist_ok=True)

    def _register_with_qgis(self):
        """Add plugin directory to QGIS SVG paths"""
        current_paths = QgsApplication.svgPaths()
        if self.plugin_svg_dir not in current_paths:
            current_paths.append(self.plugin_svg_dir)
            QgsApplication.setSvgPaths(current_paths)
            # Invalidate cache to recognize new icons
            QgsApplication.svgCache().containsParams(None, None, None)
```

**Benefits**:
- Downloaded icons immediately available in all QGIS symbol selectors
- No manual path configuration needed
- Works with existing QGIS workflows

### 2. Custom Layer Properties Tab (Priority: MEDIUM)
**Description**: Add a dedicated "SVG Library" tab to the layer properties dialog.

**Implementation**:
```python
from qgis.gui import QgsMapLayerConfigWidget, QgsMapLayerConfigWidgetFactory

class SvgLibraryConfigWidget(QgsMapLayerConfigWidget):
    def __init__(self, layer, canvas, parent):
        super().__init__(layer, canvas, parent)
        self.setupUi()

    def setupUi(self):
        # Add search interface
        self.search_widget = SvgSearchWidget()
        self.icon_list = SvgIconListWidget()

        # Connect to apply directly to layer
        self.icon_list.iconSelected.connect(self.applyToLayer)

    def applyToLayer(self, svg_path):
        """Apply selected SVG to layer symbology"""
        from qgis.core import QgsSvgMarkerSymbolLayer, QgsSingleSymbolRenderer

        svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
        symbol = QgsMarkerSymbol()
        symbol.changeSymbolLayer(0, svg_layer)

        renderer = QgsSingleSymbolRenderer(symbol)
        self.layer.setRenderer(renderer)
        self.layer.triggerRepaint()

class SvgLibraryConfigWidgetFactory(QgsMapLayerConfigWidgetFactory):
    def __init__(self):
        super().__init__('SVG Library', QIcon(':/plugins/svg_library/icon.png'))

    def supportsLayer(self, layer):
        return layer.type() == QgsMapLayerType.VectorLayer

    def createWidget(self, layer, canvas, parent):
        return SvgLibraryConfigWidget(layer, canvas, parent)
```

**Registration** (in plugin's `initGui`):
```python
self.config_factory = SvgLibraryConfigWidgetFactory()
QgsGui.instance().mapLayerConfigWidgetFactoryRegistry().registerFactory(self.config_factory)
```

### 3. Extend QgsSvgSelectorWidget (Priority: HIGH)
**Description**: Enhance the native SVG selector with online browsing capabilities.

**Implementation**:
```python
from qgis.gui import QgsSvgSelectorWidget

class EnhancedSvgSelector(QgsSvgSelectorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_online_button()

    def add_online_button(self):
        """Add 'Browse Online' button to the widget"""
        self.online_btn = QPushButton("Browse Online Icons")
        self.online_btn.clicked.connect(self.open_online_browser)

        # Insert button into existing layout
        self.layout().addWidget(self.online_btn)

    def open_online_browser(self):
        """Open icon browser dialog"""
        dialog = OnlineIconBrowserDialog(self)
        if dialog.exec_():
            svg_path = dialog.selected_svg_path
            # Download to registered SVG directory
            self.download_and_refresh(svg_path)

    def download_and_refresh(self, svg_path):
        """Download icon and refresh the selector"""
        local_path = self.download_icon(svg_path)
        # Refresh the widget to show new icon
        self.setSvgPath(local_path)
```

### 4. Symbol Button Integration (Priority: LOW)
**Description**: Add online browsing to QgsSymbolButton context menu.

**Implementation**:
```python
from qgis.gui import QgsSymbolButton

def enhance_symbol_button(button):
    """Add online browsing to symbol button"""
    action = QAction("Browse Online Icons...", button)
    action.triggered.connect(lambda: browse_online_for_button(button))

    # Add to context menu
    button.customContextMenuRequested.connect(
        lambda pos: show_enhanced_menu(button, pos, action)
    )

def browse_online_for_button(button):
    """Open browser and apply to button"""
    dialog = OnlineIconBrowserDialog()
    if dialog.exec_():
        # Create symbol with downloaded SVG
        svg_layer = QgsSvgMarkerSymbolLayer(dialog.selected_path)
        symbol = QgsMarkerSymbol()
        symbol.changeSymbolLayer(0, svg_layer)
        button.setSymbol(symbol)
```

### 5. Drag and Drop Support (Priority: HIGH)
**Description**: Enable dragging icons from the dock widget to layers.

**Implementation**:
```python
from qgis.PyQt.QtCore import Qt, QMimeData
from qgis.PyQt.QtGui import QDrag

class DraggableIconList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        """Start drag operation with SVG path"""
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()

            # Include SVG path and icon data
            icon_data = item.data(Qt.UserRole)
            mime_data.setData("application/x-qgis-svg-icon",
                             icon_data.download_url.encode())
            mime_data.setText(icon_data.name)

            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)

# In main window, accept drops on layer tree
def setup_drop_handling(layer_tree_view):
    """Enable dropping SVGs on layers"""
    layer_tree_view.setAcceptDrops(True)

    def handle_drop(event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-qgis-svg-icon"):
            svg_url = mime_data.data("application/x-qgis-svg-icon").data().decode()

            # Download and apply to target layer
            layer = get_layer_at_position(event.pos())
            if layer:
                apply_svg_to_layer(layer, svg_url)
                event.accept()
```

### 6. Context Menu Integration (Priority: MEDIUM)
**Description**: Add right-click options to layer context menu.

**Implementation**:
```python
def add_layer_context_action(layer_tree_view):
    """Add SVG library action to layer context menu"""

    def on_context_menu(point):
        layer = layer_tree_view.currentLayer()
        if not layer or layer.type() != QgsMapLayerType.VectorLayer:
            return

        menu = layer_tree_view.createContextMenu()

        # Add our action
        svg_action = QAction(QIcon(":/plugins/svg_library/icon.png"),
                           "Apply SVG from Library...", menu)
        svg_action.triggered.connect(lambda: open_svg_picker(layer))

        # Insert before separator or at end
        actions = menu.actions()
        if actions:
            menu.insertAction(actions[0], svg_action)
            menu.insertSeparator(actions[0])
        else:
            menu.addAction(svg_action)

        menu.exec_(layer_tree_view.mapToGlobal(point))

    layer_tree_view.customContextMenuRequested.connect(on_context_menu)

def open_svg_picker(layer):
    """Open streamlined SVG picker for layer"""
    dialog = QuickSvgPickerDialog(layer)
    if dialog.exec_():
        apply_svg_to_layer(layer, dialog.selected_svg)
```

### 7. Symbol Selector Dialog Hook (Priority: LOW)
**Description**: Add online browsing to QgsSymbolSelectorDialog.

**Implementation**:
```python
from qgis.gui import QgsSymbolSelectorDialog

# Monkey-patch or subclass the dialog
original_init = QgsSymbolSelectorDialog.__init__

def enhanced_init(self, symbol, style, layer, parent=None):
    original_init(self, symbol, style, layer, parent)

    # Add toolbar action
    toolbar = self.findChild(QToolBar)
    if toolbar:
        action = QAction(QIcon(":/plugins/svg_library/icon.png"),
                        "Browse Online Icons", self)
        action.triggered.connect(lambda: browse_and_apply(self))
        toolbar.addAction(action)

QgsSymbolSelectorDialog.__init__ = enhanced_init

def browse_and_apply(dialog):
    """Browse online and apply to current symbol"""
    browser = OnlineIconBrowserDialog(dialog)
    if browser.exec_():
        # Get current symbol layer
        current_layer = dialog.currentSymbolLayer()
        if isinstance(current_layer, QgsSvgMarkerSymbolLayer):
            current_layer.setPath(browser.selected_path)
            dialog.symbolChanged()
```

### 8. Quick Access Toolbar (Priority: LOW)
**Description**: Create a favorites/recent icons toolbar.

**Implementation**:
```python
class SvgQuickAccessToolbar(QToolBar):
    def __init__(self, iface):
        super().__init__("SVG Quick Access")
        self.iface = iface
        self.setup_actions()

    def setup_actions(self):
        """Add recent and favorite icons"""
        settings = QSettings()

        # Recent icons
        recent = settings.value("svg_library/recent_icons", [])
        for svg_data in recent[:5]:  # Show last 5
            action = QAction(QIcon(svg_data['path']),
                           svg_data['name'], self)
            action.setData(svg_data)
            action.triggered.connect(self.apply_quick_icon)
            self.addAction(action)

        self.addSeparator()

        # Favorites
        favorites = settings.value("svg_library/favorite_icons", [])
        for svg_data in favorites:
            action = QAction(QIcon(svg_data['path']),
                           svg_data['name'], self)
            action.setData(svg_data)
            action.triggered.connect(self.apply_quick_icon)
            self.addAction(action)

    def apply_quick_icon(self):
        """Apply icon to active layer"""
        action = self.sender()
        svg_data = action.data()

        layer = self.iface.activeLayer()
        if layer and layer.type() == QgsMapLayerType.VectorLayer:
            apply_svg_to_layer(layer, svg_data['path'])
```

## Implementation Strategy

### Phase 1: Foundation (Week 1)
1. Implement automatic SVG path registration
2. Create download manager for proper file organization
3. Test with existing QGIS symbol selectors

### Phase 2: Basic Integration (Week 2)
1. Implement drag and drop support
2. Add context menu integration
3. Create quick SVG picker dialog

### Phase 3: Advanced Integration (Week 3)
1. Develop custom layer properties tab
2. Extend QgsSvgSelectorWidget
3. Test with various QGIS versions

### Phase 4: Polish (Week 4)
1. Add quick access toolbar
2. Implement favorites system
3. Create comprehensive documentation

## Technical Considerations

### QGIS Version Compatibility
- Test with QGIS 3.16 LTR and latest version
- Use try/except blocks for newer API features
- Provide fallbacks for older versions

### Performance
- Cache downloaded icons locally
- Use lazy loading for icon previews
- Implement pagination for large result sets

### File Organization
```
~/.qgis3/svg/svg_library_plugin/
├── downloads/
│   ├── noun_project/
│   ├── material_symbols/
│   ├── font_awesome/
│   └── maki/
├── favorites/
└── cache/
```

### Settings Storage
```python
settings = QSettings()
settings.beginGroup("svg_library")
settings.setValue("download_path", path)
settings.setValue("auto_register", True)
settings.setValue("recent_icons", recent_list)
settings.setValue("favorite_icons", fav_list)
settings.endGroup()
```

## Testing Strategy

### Unit Tests
- Test SVG path registration
- Test download and file management
- Test OAuth implementation

### Integration Tests
- Test with various layer types
- Test with different symbology renderers
- Test drag and drop operations

### User Acceptance Tests
- Test workflow efficiency
- Test UI responsiveness
- Gather user feedback on integration points

## Future Enhancements

### AI-Powered Icon Search
- Implement semantic search using icon descriptions
- Suggest icons based on layer name/attributes
- Auto-categorize downloaded icons

### Cloud Sync
- Sync favorites across machines
- Share icon collections with team
- Backup settings to cloud

### Advanced Styling
- Apply color variations to SVGs
- Batch apply to multiple layers
- Create symbol presets

## Resources

### QGIS API Documentation
- [QgsSymbol](https://qgis.org/pyqgis/master/core/QgsSymbol.html)
- [QgsSvgMarkerSymbolLayer](https://qgis.org/pyqgis/master/core/QgsSvgMarkerSymbolLayer.html)
- [QgsMapLayerConfigWidget](https://qgis.org/pyqgis/master/gui/QgsMapLayerConfigWidget.html)

### Example Plugins
- [Style Manager](https://github.com/qgis/QGIS/tree/master/src/app/qgsstylemanagerdialog.cpp)
- [Resource Sharing](https://github.com/QGIS-Contribution/QGIS-ResourceSharing)

### Community Resources
- [QGIS Developer Cookbook](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/)
- [QGIS Python Plugins Repository](https://plugins.qgis.org/)