"""
Configuration dialog for SVG Library Browser plugin
"""

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QLineEdit, QPushButton, QTabWidget, QWidget,
                                QFormLayout, QCheckBox, QSpinBox, QTextEdit,
                                QMessageBox)
from qgis.PyQt.QtCore import QSettings


class ConfigDialog(QDialog):
    """Configuration dialog for the SVG Library Browser plugin"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SVG Library Browser - Settings")
        self.setMinimumSize(500, 400)
        self.setupUI()
        self.loadSettings()
        
    def setupUI(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # API Keys tab
        self.setupApiKeysTab()
        
        # General Settings tab
        self.setupGeneralTab()
        
        # GitHub Repositories tab
        self.setupGitHubTab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.saveSettings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def setupApiKeysTab(self):
        """Setup API keys configuration tab"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        
        # The Noun Project
        layout.addRow(QLabel("The Noun Project API:"))
        self.noun_api_key = QLineEdit()
        self.noun_api_key.setPlaceholderText("Enter your API key")
        layout.addRow("API Key:", self.noun_api_key)
        
        self.noun_secret = QLineEdit()
        self.noun_secret.setPlaceholderText("Enter your API secret")
        layout.addRow("API Secret:", self.noun_secret)
        
        # Add note about getting API keys
        note_text = QTextEdit()
        note_text.setMaximumHeight(100)
        note_text.setPlainText(
            "API Key Information:\n"
            "• The Noun Project: Register at thenounproject.com/developers/\n"
            "• Material Symbols: No API key required\n"
            "• Maki: No API key required\n"
            "• Font Awesome: No API key required for Free icons\n"
            "• GitHub: Uses public API, no key required for public repos"
        )
        note_text.setReadOnly(True)
        layout.addRow("Note:", note_text)
        
        self.tab_widget.addTab(widget, "API Keys")
        
    def setupGeneralTab(self):
        """Setup general settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        
        # Default results per page
        self.default_per_page = QSpinBox()
        self.default_per_page.setMinimum(10)
        self.default_per_page.setMaximum(100)
        self.default_per_page.setValue(20)
        layout.addRow("Results per page:", self.default_per_page)
        
        # Auto-apply to layer
        self.auto_apply_default = QCheckBox("Auto-apply to selected layer by default")
        layout.addRow(self.auto_apply_default)
        
        # Auto-save attributions to project
        self.auto_save_attributions = QCheckBox("Auto-save attributions to project metadata")
        layout.addRow(self.auto_save_attributions)
        
        # Thumbnail size
        self.thumbnail_size = QSpinBox()
        self.thumbnail_size.setMinimum(32)
        self.thumbnail_size.setMaximum(128)
        self.thumbnail_size.setValue(64)
        layout.addRow("Thumbnail size (px):", self.thumbnail_size)
        
        self.tab_widget.addTab(widget, "General")
        
    def setupGitHubTab(self):
        """Setup GitHub repositories configuration"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        layout.addWidget(QLabel("Custom GitHub Repositories:"))
        layout.addWidget(QLabel("Add GitHub repositories containing SVG icons (one per line):"))
        layout.addWidget(QLabel("Format: username/repository-name or username/repository-name:path/to/svgs"))
        
        self.github_repos = QTextEdit()
        self.github_repos.setPlaceholderText(
            "Example:\n"
            "tabler/tabler-icons\n"
            "feathericons/feather\n"
            "ionic-team/ionicons:src/svg\n"
            "microsoft/fluentui-system-icons:assets"
        )
        layout.addWidget(self.github_repos)
        
        self.tab_widget.addTab(widget, "GitHub Repos")
        
    def loadSettings(self):
        """Load settings from QSettings"""
        settings = QSettings()
        
        # API Keys
        self.noun_api_key.setText(settings.value("svg_library/noun_api_key", ""))
        self.noun_secret.setText(settings.value("svg_library/noun_secret", ""))
        
        # General settings
        self.default_per_page.setValue(int(settings.value("svg_library/default_per_page", 20)))
        self.auto_apply_default.setChecked(bool(settings.value("svg_library/auto_apply_default", False)))
        self.auto_save_attributions.setChecked(bool(settings.value("svg_library/auto_save_attributions", True)))
        self.thumbnail_size.setValue(int(settings.value("svg_library/thumbnail_size", 64)))
        
        # GitHub repos
        github_repos = settings.value("svg_library/github_repos", "")
        self.github_repos.setPlainText(github_repos)
        
    def saveSettings(self):
        """Save settings to QSettings"""
        settings = QSettings()
        
        # API Keys
        settings.setValue("svg_library/noun_api_key", self.noun_api_key.text())
        settings.setValue("svg_library/noun_secret", self.noun_secret.text())
        
        # General settings
        settings.setValue("svg_library/default_per_page", self.default_per_page.value())
        settings.setValue("svg_library/auto_apply_default", self.auto_apply_default.isChecked())
        settings.setValue("svg_library/auto_save_attributions", self.auto_save_attributions.isChecked())
        settings.setValue("svg_library/thumbnail_size", self.thumbnail_size.value())
        
        # GitHub repos
        settings.setValue("svg_library/github_repos", self.github_repos.toPlainText())
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
        self.accept()