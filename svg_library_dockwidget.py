"""
SVG Library Browser Dock Widget
"""

import os
import tempfile
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QThread, QTimer, Qt
from qgis.PyQt.QtWidgets import (QDockWidget, QVBoxLayout, QHBoxLayout, 
                                QLineEdit, QPushButton, QComboBox, QScrollArea,
                                QWidget, QLabel, QGridLayout, QMessageBox,
                                QProgressBar, QSpinBox, QCheckBox, QTextEdit)
from qgis.PyQt.QtGui import QPixmap, QIcon
from qgis.core import (QgsProject, QgsVectorLayer, QgsSymbol, QgsSvgMarkerSymbolLayer,
                      QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsApplication)

from .icon_providers import IconProviderManager
from .providers import (NounProjectProvider, MaterialSymbolsProvider, 
                       MakiProvider, FontAwesomeFreeProvider, GitHubRepoProvider)
from .attribution_utils import AttributionManager, ProjectMetadataManager
from .config_dialog import ConfigDialog


class IconThumbnailWidget(QWidget):
    """Widget to display a single icon thumbnail"""
    
    iconClicked = pyqtSignal(object)  # Emit SvgIcon object
    
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Icon preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(64, 64)
        self.preview_label.setStyleSheet("border: 1px solid gray; background: white;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("Loading...")
        layout.addWidget(self.preview_label)
        
        # Icon name
        name_label = QLabel(self.icon.name)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(80)
        layout.addWidget(name_label)
        
        # Provider label
        provider_label = QLabel(self.icon.provider)
        provider_label.setStyleSheet("font-size: 9px; color: gray;")
        layout.addWidget(provider_label)
        
        self.setLayout(layout)
        self.setMaximumWidth(90)
        self.setStyleSheet("QWidget:hover { background-color: #e6f3ff; }")
        
        # Load preview image
        self.load_preview()
        
    def load_preview(self):
        """Load preview image from URL"""
        # For now, just show a placeholder
        # In a real implementation, you'd download the image asynchronously
        self.preview_label.setText("SVG")
        
    def mousePressEvent(self, event):
        """Handle click on thumbnail"""
        if event.button() == Qt.LeftButton:
            self.iconClicked.emit(self.icon)


class SearchWorker(QThread):
    """Worker thread for searching icons"""
    
    resultsReady = pyqtSignal(dict)  # Dict of provider_name: SearchResult
    
    def __init__(self, provider_manager, query, page=1, per_page=20):
        super().__init__()
        self.provider_manager = provider_manager
        self.query = query
        self.page = page
        self.per_page = per_page
        
    def run(self):
        """Run search in background thread"""
        results = self.provider_manager.search_all(self.query, self.page, self.per_page)
        self.resultsReady.emit(results)


class SvgLibraryDockWidget(QDockWidget):
    """Main dock widget for SVG library browser"""
    
    closingPlugin = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.iface = None  # Will be set by plugin
        self.setupUI()
        self.setupProviders()
        self.search_worker = None
        self.attribution_manager = AttributionManager()
        
    def set_iface(self, iface):
        """Set QGIS interface reference"""
        self.iface = iface
        
    def setupUI(self):
        """Setup the user interface"""
        self.setObjectName("SvgLibraryDockWidget")
        self.setWindowTitle("SVG Library Browser")
        
        # Main widget
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Search section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for icons (e.g., 'school', 'bridge')")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_button)
        
        self.settings_button = QPushButton("⚙")
        self.settings_button.setMaximumWidth(30)
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        search_layout.addWidget(self.settings_button)
        
        layout.addLayout(search_layout)
        
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Providers:"))
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("All Providers", "all")
        provider_layout.addWidget(self.provider_combo)
        
        layout.addLayout(provider_layout)
        
        # Results per page
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Results per page:"))
        
        self.per_page_spin = QSpinBox()
        self.per_page_spin.setMinimum(10)
        self.per_page_spin.setMaximum(100)
        self.per_page_spin.setValue(20)
        page_layout.addWidget(self.per_page_spin)
        
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        self.scroll_area = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QGridLayout()
        self.results_widget.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Pagination
        pagination_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.page_label)
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
        
        # Import options
        import_group = QWidget()
        import_layout = QVBoxLayout()
        import_group.setLayout(import_layout)
        
        self.auto_apply_check = QCheckBox("Auto-apply to selected layer")
        import_layout.addWidget(self.auto_apply_check)
        
        # Attribution tracking
        attribution_layout = QVBoxLayout()
        attribution_layout.addWidget(QLabel("Attributions:"))
        
        self.attribution_text = QTextEdit()
        self.attribution_text.setMaximumHeight(80)
        self.attribution_text.setPlaceholderText("Icon attributions will appear here...")
        attribution_layout.addWidget(self.attribution_text)
        
        # Attribution buttons
        attr_buttons_layout = QHBoxLayout()
        
        self.save_to_project_btn = QPushButton("Save to Project")
        self.save_to_project_btn.clicked.connect(self.save_attributions_to_project)
        attr_buttons_layout.addWidget(self.save_to_project_btn)
        
        self.export_attr_btn = QPushButton("Export")
        self.export_attr_btn.clicked.connect(self.export_attributions)
        attr_buttons_layout.addWidget(self.export_attr_btn)
        
        self.clear_attr_btn = QPushButton("Clear")
        self.clear_attr_btn.clicked.connect(self.clear_attributions)
        attr_buttons_layout.addWidget(self.clear_attr_btn)
        
        attribution_layout.addLayout(attr_buttons_layout)
        import_layout.addLayout(attribution_layout)
        
        layout.addWidget(import_group)
        
        # Initialize state
        self.current_page = 1
        self.current_query = ""
        self.current_results = {}
        
    def setupProviders(self):
        """Setup icon providers"""
        self.provider_manager = IconProviderManager()
        
        # Load settings
        from qgis.PyQt.QtCore import QSettings
        settings = QSettings()
        
        # Register providers with API keys from settings
        noun_api_key = settings.value("svg_library/noun_api_key", "")
        noun_secret = settings.value("svg_library/noun_secret", "")
        if noun_api_key and noun_secret:
            self.provider_manager.register_provider(
                NounProjectProvider(noun_api_key, noun_secret)
            )
        
        # Register free providers
        self.provider_manager.register_provider(MaterialSymbolsProvider())
        self.provider_manager.register_provider(MakiProvider())
        self.provider_manager.register_provider(FontAwesomeFreeProvider())
        
        # Add GitHub repos from settings
        github_repos = settings.value("svg_library/github_repos", "")
        if github_repos:
            for line in github_repos.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        repo, path = line.split(':', 1)
                        self.provider_manager.register_provider(
                            GitHubRepoProvider(repo, path)
                        )
                    else:
                        self.provider_manager.register_provider(
                            GitHubRepoProvider(line)
                        )
        else:
            # Add some default GitHub repos
            self.provider_manager.register_provider(
                GitHubRepoProvider("tabler/tabler-icons", "icons")
            )
        
        # Update provider combo
        self.provider_combo.clear()
        self.provider_combo.addItem("All Providers", "all")
        for provider_name in self.provider_manager.providers.keys():
            self.provider_combo.addItem(provider_name, provider_name)
            
    def show_settings(self):
        """Show settings dialog"""
        dialog = ConfigDialog(self)
        if dialog.exec_() == ConfigDialog.Accepted:
            # Reload providers with new settings
            self.setupProviders()
            
    def perform_search(self):
        """Perform icon search"""
        query = self.search_input.text().strip()
        if not query:
            return
            
        self.current_query = query
        self.current_page = 1
        self.search_icons()
        
    def search_icons(self):
        """Search for icons using current parameters"""
        if self.search_worker and self.search_worker.isRunning():
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.search_button.setEnabled(False)
        
        # Start search worker
        per_page = self.per_page_spin.value()
        self.search_worker = SearchWorker(
            self.provider_manager, 
            self.current_query, 
            self.current_page, 
            per_page
        )
        self.search_worker.resultsReady.connect(self.display_results)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.start()
        
    def search_finished(self):
        """Called when search is finished"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        
    def display_results(self, results):
        """Display search results"""
        self.current_results = results
        
        # Clear previous results
        self.clear_results()
        
        # Display icons from all providers
        row = 0
        col = 0
        max_cols = 5
        
        for provider_name, search_result in results.items():
            if search_result.icons:
                # Add provider header
                header_label = QLabel(f"{provider_name} ({len(search_result.icons)} results)")
                header_label.setStyleSheet("font-weight: bold; padding: 5px;")
                self.results_layout.addWidget(header_label, row, 0, 1, max_cols)
                row += 1
                col = 0
                
                # Add icons
                for icon in search_result.icons:
                    thumbnail = IconThumbnailWidget(icon)
                    thumbnail.iconClicked.connect(self.icon_clicked)
                    self.results_layout.addWidget(thumbnail, row, col)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                
                if col > 0:
                    row += 1
                    col = 0
                    
        # Update pagination
        self.update_pagination()
        
    def clear_results(self):
        """Clear current results"""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def update_pagination(self):
        """Update pagination controls"""
        has_results = bool(self.current_results)
        
        # For simplicity, assume pagination based on first provider with results
        has_next = False
        has_prev = self.current_page > 1
        
        for search_result in self.current_results.values():
            if search_result.icons:
                has_next = search_result.has_next
                break
                
        self.prev_button.setEnabled(has_prev)
        self.next_button.setEnabled(has_next)
        self.page_label.setText(f"Page {self.current_page}")
        
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.search_icons()
            
    def next_page(self):
        """Go to next page"""
        self.current_page += 1
        self.search_icons()
        
    def icon_clicked(self, icon):
        """Handle icon click - download and optionally apply"""
        try:
            # Get QGIS SVG directory
            svg_paths = QgsApplication.svgPaths()
            if not svg_paths:
                QMessageBox.warning(self, "Error", "No SVG paths configured in QGIS")
                return
                
            # Use first writable SVG path (usually user profile)
            svg_dir = svg_paths[0]
            if not os.path.exists(svg_dir):
                os.makedirs(svg_dir)
                
            # Create filename
            filename = f"{icon.provider}_{icon.id}.svg".replace(" ", "_").replace("/", "_")
            file_path = os.path.join(svg_dir, filename)
            
            # Download SVG
            provider = self.provider_manager.get_provider(icon.provider)
            if provider and provider.download_svg(icon, file_path):
                QMessageBox.information(self, "Success", f"SVG saved to: {file_path}")
                
                # Add attribution
                icon.file_path = file_path  # Store file path for attribution
                self.add_attribution(icon)
                
                # Optionally apply to selected layer
                if self.auto_apply_check.isChecked():
                    self.apply_to_layer(file_path, icon)
                    
            else:
                QMessageBox.warning(self, "Error", "Failed to download SVG")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error downloading icon: {str(e)}")
            
    def add_attribution(self, icon):
        """Add attribution text"""
        # Add to attribution manager
        icon_data = {
            'id': icon.id,
            'name': icon.name,
            'provider': icon.provider,
            'license': icon.license,
            'attribution': icon.attribution,
            'url': icon.url,
            'file_path': getattr(icon, 'file_path', '')
        }
        self.attribution_manager.add_attribution(icon_data)
        
        # Update display
        attribution = f"{icon.name} - {icon.attribution} ({icon.license})\n"
        current_text = self.attribution_text.toPlainText()
        if attribution not in current_text:
            self.attribution_text.append(attribution.strip())
            
    def save_attributions_to_project(self):
        """Save attributions to QGIS project metadata"""
        try:
            attributions = self.attribution_manager.get_all_attributions()
            count = ProjectMetadataManager.save_attributions_to_project(attributions)
            QMessageBox.information(self, "Success", 
                                  f"Saved {count} new attributions to project metadata")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save attributions: {str(e)}")
            
    def export_attributions(self):
        """Export attributions to file"""
        try:
            from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog
            
            # Ask for format
            formats = ["Text (*.txt)", "JSON (*.json)", "HTML (*.html)"]
            format_choice, ok = QInputDialog.getItem(
                self, "Export Format", "Choose export format:", formats, 0, False
            )
            
            if not ok:
                return
                
            # Get file path
            if "Text" in format_choice:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export Attributions", "attributions.txt", "Text files (*.txt)"
                )
                format_type = "text"
            elif "JSON" in format_choice:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export Attributions", "attributions.json", "JSON files (*.json)"
                )
                format_type = "json"
            else:  # HTML
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export Attributions", "attributions.html", "HTML files (*.html)"
                )
                format_type = "html"
                
            if file_path:
                content = self.attribution_manager.export_attributions(format_type)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Attributions exported to {file_path}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export attributions: {str(e)}")
            
    def clear_attributions(self):
        """Clear all attributions"""
        reply = QMessageBox.question(
            self, "Clear Attributions", 
            "Are you sure you want to clear all attributions?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.attribution_manager = AttributionManager()
            self.attribution_text.clear()
            
    def apply_to_layer(self, svg_path, icon):
        """Apply SVG as symbol to selected layer"""
        try:
            # Get current layer
            layer = self.iface.activeLayer() if self.iface else None
            if not layer or not isinstance(layer, QgsVectorLayer):
                QMessageBox.warning(self, "Warning", "Please select a vector layer")
                return
                
            # Create SVG marker symbol layer
            svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
            svg_layer.setSize(10)  # Default size
            
            # Get current symbol or create new one
            renderer = layer.renderer()
            if hasattr(renderer, 'symbol') and renderer.symbol():
                symbol = renderer.symbol().clone()
                # Replace first symbol layer
                symbol.changeSymbolLayer(0, svg_layer)
            else:
                # Create new symbol
                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                symbol.changeSymbolLayer(0, svg_layer)
                
            # Apply to layer
            from qgis.core import QgsSingleSymbolRenderer
            new_renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(new_renderer)
            layer.triggerRepaint()
            
            QMessageBox.information(self, "Success", f"Applied {icon.name} symbol to layer")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to apply symbol: {str(e)}")
    
    def closeEvent(self, event):
        """Handle dock widget close"""
        self.closingPlugin.emit()
        event.accept()