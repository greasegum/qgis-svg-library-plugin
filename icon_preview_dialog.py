"""
Icon Preview Dialog for SVG Library Browser
Follows QGIS plugin idiomatic style
"""

import os
import tempfile
import urllib.request
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QGroupBox, QTextEdit, QMessageBox,
                                 QCheckBox, QDialogButtonBox, QFrame)
from qgis.PyQt.QtGui import QPixmap, QFont
from qgis.PyQt.QtSvg import QSvgWidget
from qgis.core import QgsApplication, QgsProject
from qgis.gui import QgsMessageBar


class IconPreviewDialog(QDialog):
    """Preview dialog for SVG icons following QGIS style"""

    def __init__(self, icon, provider_manager, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.provider_manager = provider_manager
        self.svg_content = None
        self.setupUI()
        self.loadIcon()

    def setupUI(self):
        """Setup the user interface following QGIS conventions"""
        self.setWindowTitle(f"Icon Preview - {self.icon.name}")
        self.setModal(True)
        self.resize(500, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Message bar for notifications (QGIS style)
        self.message_bar = QgsMessageBar()
        layout.addWidget(self.message_bar)

        # Icon preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)

        # SVG widget for larger preview
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumSize(QSize(256, 256))
        self.svg_widget.setMaximumSize(QSize(256, 256))
        preview_layout.addWidget(self.svg_widget, alignment=Qt.AlignCenter)

        # Icon name
        name_label = QLabel(self.icon.name)
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(name_label)

        layout.addWidget(preview_group)

        # Icon details section
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout()
        details_group.setLayout(details_layout)

        # Create detail labels
        details = [
            ("Provider:", self.icon.provider),
            ("License:", self.icon.license),
            ("Tags:", ", ".join(self.icon.tags) if self.icon.tags else "None"),
            ("ID:", self.icon.id)
        ]

        for label_text, value_text in details:
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setMinimumWidth(80)
            label.setStyleSheet("font-weight: bold;")
            row_layout.addWidget(label)

            value = QLabel(value_text)
            value.setWordWrap(True)
            row_layout.addWidget(value, stretch=1)

            details_layout.addLayout(row_layout)

        # Attribution text
        attr_label = QLabel("Attribution:")
        attr_label.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(attr_label)

        self.attribution_text = QTextEdit()
        self.attribution_text.setMaximumHeight(60)
        self.attribution_text.setReadOnly(True)
        self.attribution_text.setPlainText(self.icon.attribution)
        details_layout.addWidget(self.attribution_text)

        layout.addWidget(details_group)

        # Options section
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.apply_to_layer_check = QCheckBox("Apply to selected layer after import")
        self.apply_to_layer_check.setToolTip(
            "Automatically apply this icon as a symbol to the currently selected layer"
        )
        options_layout.addWidget(self.apply_to_layer_check)

        self.save_attribution_check = QCheckBox("Save attribution to project metadata")
        self.save_attribution_check.setChecked(True)
        self.save_attribution_check.setToolTip(
            "Store attribution information in the QGIS project for license compliance"
        )
        options_layout.addWidget(self.save_attribution_check)

        layout.addWidget(options_group)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Button box (QGIS standard)
        self.button_box = QDialogButtonBox()

        # Save button
        self.save_button = QPushButton("Save to SVG Library")
        self.save_button.setToolTip("Save icon to your QGIS SVG library")
        self.button_box.addButton(self.save_button, QDialogButtonBox.ActionRole)
        self.save_button.clicked.connect(self.saveIcon)

        # Import button
        self.import_button = QPushButton("Import && Apply")
        self.import_button.setToolTip("Import icon and apply to selected layer")
        self.button_box.addButton(self.import_button, QDialogButtonBox.AcceptRole)
        self.import_button.clicked.connect(self.importAndApply)

        # Cancel button
        self.button_box.addButton(QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def loadIcon(self):
        """Load and display the icon"""
        try:
            # Create SSL context for HTTPS requests
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Download SVG content
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_file:
                response = urllib.request.urlopen(self.icon.preview_url, timeout=10, context=ssl_context)
                self.svg_content = response.read()
                tmp_file.write(self.svg_content)
                tmp_file.flush()

                # Load into SVG widget
                self.svg_widget.load(tmp_file.name)

                # Clean up
                os.unlink(tmp_file.name)

        except Exception as e:
            self.message_bar.pushMessage(
                "Error",
                f"Failed to load icon preview: {str(e)}",
                level=QgsMessageBar.WARNING,
                duration=5
            )

    def getSvgPath(self):
        """Get the path where SVG should be saved"""
        svg_paths = QgsApplication.svgPaths()
        if not svg_paths:
            raise Exception("No SVG paths configured in QGIS")

        # Use first writable SVG path (usually user profile)
        svg_dir = svg_paths[0]
        if not os.path.exists(svg_dir):
            os.makedirs(svg_dir)

        # Create filename (sanitize for filesystem)
        safe_provider = "".join(c for c in self.icon.provider if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_id = "".join(c for c in self.icon.id if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_provider}_{safe_id}.svg".replace(" ", "_")

        return os.path.join(svg_dir, filename)

    def saveIcon(self):
        """Save icon to SVG library"""
        try:
            file_path = self.getSvgPath()

            # Get the provider and download
            provider = self.provider_manager.get_provider(self.icon.provider)
            if provider and provider.download_svg(self.icon, file_path):
                self.message_bar.pushMessage(
                    "Success",
                    f"Icon saved to: {file_path}",
                    level=QgsMessageBar.SUCCESS,
                    duration=3
                )

                # Save attribution if requested
                if self.save_attribution_check.isChecked():
                    self.saveAttribution(file_path)

                return True
            else:
                self.message_bar.pushMessage(
                    "Error",
                    "Failed to download icon",
                    level=QgsMessageBar.CRITICAL,
                    duration=5
                )
                return False

        except Exception as e:
            self.message_bar.pushMessage(
                "Error",
                f"Failed to save icon: {str(e)}",
                level=QgsMessageBar.CRITICAL,
                duration=5
            )
            return False

    def importAndApply(self):
        """Import icon and optionally apply to layer"""
        if self.saveIcon():
            if self.apply_to_layer_check.isChecked():
                self.applyToLayer()
            self.accept()

    def applyToLayer(self):
        """Apply icon to selected layer"""
        try:
            # Get active layer
            from qgis.utils import iface
            layer = iface.activeLayer()

            if not layer:
                self.message_bar.pushMessage(
                    "Warning",
                    "No layer selected",
                    level=QgsMessageBar.WARNING,
                    duration=3
                )
                return

            # Check if it's a vector layer
            from qgis.core import QgsVectorLayer, QgsSingleSymbolRenderer, QgsMarkerSymbol
            if not isinstance(layer, QgsVectorLayer):
                self.message_bar.pushMessage(
                    "Warning",
                    "Selected layer is not a vector layer",
                    level=QgsMessageBar.WARNING,
                    duration=3
                )
                return

            # Apply SVG symbol
            file_path = self.getSvgPath()

            # Create SVG marker symbol
            from qgis.core import QgsSvgMarkerSymbolLayer
            svg_symbol = QgsSvgMarkerSymbolLayer(file_path)
            svg_symbol.setSize(6)

            # Create marker symbol
            symbol = QgsMarkerSymbol()
            symbol.changeSymbolLayer(0, svg_symbol)

            # Apply to layer
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)
            layer.triggerRepaint()

            self.message_bar.pushMessage(
                "Success",
                f"Icon applied to layer: {layer.name()}",
                level=QgsMessageBar.SUCCESS,
                duration=3
            )

        except Exception as e:
            self.message_bar.pushMessage(
                "Error",
                f"Failed to apply icon to layer: {str(e)}",
                level=QgsMessageBar.CRITICAL,
                duration=5
            )

    def saveAttribution(self, file_path):
        """Save attribution to project metadata"""
        try:
            # Create attribution data
            from attribution_utils import ProjectMetadataManager

            icon_data = {
                'id': self.icon.id,
                'name': self.icon.name,
                'provider': self.icon.provider,
                'license': self.icon.license,
                'attribution': self.icon.attribution,
                'url': self.icon.url,
                'file_path': file_path
            }

            # Save to project
            ProjectMetadataManager.add_single_attribution(icon_data)

        except Exception as e:
            print(f"Failed to save attribution: {e}")