#!/usr/bin/env python3
"""
Comprehensive test suite for QGIS SVG Library Plugin

This test suite covers:
1. Plugin initialization and loading
2. Icon provider functionality
3. Attribution tracking
4. Search and download features
5. Configuration management
"""

import unittest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Import the plugin components
from icon_providers import IconProvider, SvgIcon, SearchResult, IconProviderManager
from providers import (
    NounProjectProvider,
    MaterialSymbolsProvider,
    MakiProvider,
    FontAwesomeProvider,
    GitHubProvider
)
from attribution_utils import AttributionManager


class TestIconProviders(unittest.TestCase):
    """Test the icon provider base functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_svg_icon_creation(self):
        """Test SvgIcon dataclass creation"""
        icon = SvgIcon(
            id="test_icon_1",
            name="Test Icon",
            url="https://example.com/icon",
            preview_url="https://example.com/icon/preview",
            tags=["test", "icon"],
            license="CC0",
            attribution="Test Author",
            provider="Test Provider",
            download_url="https://example.com/icon.svg"
        )

        self.assertEqual(icon.id, "test_icon_1")
        self.assertEqual(icon.name, "Test Icon")
        self.assertEqual(len(icon.tags), 2)
        self.assertIn("test", icon.tags)

    def test_search_result_creation(self):
        """Test SearchResult dataclass"""
        icons = []
        for i in range(5):
            icon = SvgIcon(
                id=f"icon_{i}",
                name=f"Icon {i}",
                url=f"https://example.com/icon_{i}",
                preview_url=f"https://example.com/preview_{i}",
                tags=["test"],
                license="CC0",
                attribution="Test",
                provider="Test Provider",
                download_url=f"https://example.com/icon_{i}.svg"
            )
            icons.append(icon)

        result = SearchResult(
            icons=icons,
            total_count=100,
            current_page=1,
            total_pages=20,
            has_next=True,
            has_previous=False
        )

        self.assertEqual(len(result.icons), 5)
        self.assertEqual(result.total_count, 100)
        self.assertTrue(result.has_next)
        self.assertFalse(result.has_previous)

    def test_icon_provider_manager(self):
        """Test IconProviderManager functionality"""
        manager = IconProviderManager()

        # Create mock providers
        provider1 = Mock(spec=IconProvider)
        provider1.name = "Provider1"
        provider1.is_available.return_value = True

        provider2 = Mock(spec=IconProvider)
        provider2.name = "Provider2"
        provider2.is_available.return_value = False

        # Register providers
        manager.register_provider(provider1)
        manager.register_provider(provider2)

        # Test retrieval
        self.assertIsNotNone(manager.get_provider("Provider1"))
        self.assertIsNone(manager.get_provider("NonExistent"))

        # Test available providers
        available = manager.get_available_providers()
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].name, "Provider1")


class TestSpecificProviders(unittest.TestCase):
    """Test specific provider implementations"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_noun_project_provider(self):
        """Test The Noun Project provider"""
        # Test without API keys
        provider = NounProjectProvider()
        self.assertFalse(provider.is_available())

        # Test search returns empty when no API key
        result = provider.search("test")
        self.assertEqual(len(result.icons), 0)

        # Test with mock API keys
        provider_with_keys = NounProjectProvider(api_key="test_key", secret="test_secret")
        self.assertTrue(provider_with_keys.is_available())

        # Test search with API keys
        result = provider_with_keys.search("test", page=1, per_page=10)
        self.assertGreater(len(result.icons), 0)
        self.assertEqual(result.current_page, 1)

        # Test SVG download
        if result.icons:
            icon = result.icons[0]
            file_path = os.path.join(self.temp_dir, "test.svg")
            success = provider_with_keys.download_svg(icon, file_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(file_path))

            # Verify SVG content
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('<svg', content)

    @patch('providers.requests.get')
    def test_material_symbols_provider(self, mock_get):
        """Test Material Symbols provider"""
        provider = MaterialSymbolsProvider()

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "hosts": [
                {
                    "name": "Material Symbols",
                    "families": ["Material Symbols Outlined"]
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test search
        result = provider.search("home")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, SearchResult)

    @patch('providers.requests.get')
    def test_maki_provider(self, mock_get):
        """Test Maki icon provider"""
        provider = MakiProvider()

        # Mock GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "airport.svg",
                "path": "icons/airport.svg",
                "download_url": "https://raw.githubusercontent.com/mapbox/maki/main/icons/airport.svg"
            },
            {
                "name": "home.svg",
                "path": "icons/home.svg",
                "download_url": "https://raw.githubusercontent.com/mapbox/maki/main/icons/home.svg"
            }
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test search
        result = provider.search("home")
        self.assertIsNotNone(result)

    @patch('providers.requests.get')
    def test_font_awesome_provider(self, mock_get):
        """Test Font Awesome provider"""
        provider = FontAwesomeProvider()

        # Mock metadata response
        mock_response = Mock()
        mock_response.json.return_value = {
            "house": {
                "styles": ["solid"],
                "unicode": "f015",
                "label": "House"
            },
            "home": {
                "styles": ["solid"],
                "unicode": "f015",
                "label": "Home"
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test search
        result = provider.search("home")
        self.assertIsNotNone(result)

    @patch('providers.requests.get')
    def test_github_provider(self, mock_get):
        """Test GitHub repository provider"""
        provider = GitHubProvider("owner/repo")

        # Mock GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "icon1.svg",
                "path": "icons/icon1.svg",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/icons/icon1.svg"
            }
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test search
        result = provider.search("icon")
        self.assertIsNotNone(result)


class TestAttributionManager(unittest.TestCase):
    """Test attribution tracking functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = AttributionManager()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_attribution(self):
        """Test adding attribution records"""
        self.manager.add_attribution(
            icon_name="test_icon",
            provider="Test Provider",
            license="CC0",
            attribution_text="Test Author",
            url="https://example.com/icon",
            file_path="/path/to/icon.svg"
        )

        attributions = self.manager.get_attributions()
        self.assertEqual(len(attributions), 1)
        self.assertEqual(attributions[0]['icon_name'], "test_icon")
        self.assertEqual(attributions[0]['provider'], "Test Provider")

    def test_export_text(self):
        """Test exporting attributions as text"""
        # Add some attributions
        self.manager.add_attribution(
            icon_name="icon1",
            provider="Provider1",
            license="CC0",
            attribution_text="Author1",
            url="https://example.com/icon1",
            file_path="/path/to/icon1.svg"
        )

        self.manager.add_attribution(
            icon_name="icon2",
            provider="Provider2",
            license="MIT",
            attribution_text="Author2",
            url="https://example.com/icon2",
            file_path="/path/to/icon2.svg"
        )

        # Export as text
        file_path = os.path.join(self.temp_dir, "attributions.txt")
        self.manager.export_text(file_path)

        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertIn("icon1", content)
            self.assertIn("Provider1", content)
            self.assertIn("CC0", content)

    def test_export_json(self):
        """Test exporting attributions as JSON"""
        # Add attribution
        self.manager.add_attribution(
            icon_name="test_icon",
            provider="Test Provider",
            license="CC0",
            attribution_text="Test Author",
            url="https://example.com/icon",
            file_path="/path/to/icon.svg"
        )

        # Export as JSON
        file_path = os.path.join(self.temp_dir, "attributions.json")
        self.manager.export_json(file_path)

        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.assertIn('attributions', data)
            self.assertEqual(len(data['attributions']), 1)
            self.assertEqual(data['attributions'][0]['icon_name'], "test_icon")

    def test_export_html(self):
        """Test exporting attributions as HTML"""
        # Add attribution
        self.manager.add_attribution(
            icon_name="test_icon",
            provider="Test Provider",
            license="CC0",
            attribution_text="Test Author",
            url="https://example.com/icon",
            file_path="/path/to/icon.svg"
        )

        # Export as HTML
        file_path = os.path.join(self.temp_dir, "attributions.html")
        self.manager.export_html(file_path)

        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertIn("<html>", content)
            self.assertIn("test_icon", content)
            self.assertIn("Test Provider", content)

    def test_clear_attributions(self):
        """Test clearing attribution records"""
        # Add some attributions
        for i in range(3):
            self.manager.add_attribution(
                icon_name=f"icon_{i}",
                provider=f"Provider_{i}",
                license="CC0",
                attribution_text=f"Author_{i}",
                url=f"https://example.com/icon_{i}",
                file_path=f"/path/to/icon_{i}.svg"
            )

        self.assertEqual(len(self.manager.get_attributions()), 3)

        # Clear attributions
        self.manager.clear()
        self.assertEqual(len(self.manager.get_attributions()), 0)

    def test_get_by_provider(self):
        """Test filtering attributions by provider"""
        # Add attributions from different providers
        self.manager.add_attribution(
            icon_name="icon1",
            provider="Provider1",
            license="CC0",
            attribution_text="Author1",
            url="https://example.com/icon1",
            file_path="/path/to/icon1.svg"
        )

        self.manager.add_attribution(
            icon_name="icon2",
            provider="Provider2",
            license="MIT",
            attribution_text="Author2",
            url="https://example.com/icon2",
            file_path="/path/to/icon2.svg"
        )

        self.manager.add_attribution(
            icon_name="icon3",
            provider="Provider1",
            license="CC0",
            attribution_text="Author3",
            url="https://example.com/icon3",
            file_path="/path/to/icon3.svg"
        )

        # Get by provider
        provider1_attrs = self.manager.get_by_provider("Provider1")
        self.assertEqual(len(provider1_attrs), 2)

        provider2_attrs = self.manager.get_by_provider("Provider2")
        self.assertEqual(len(provider2_attrs), 1)

        # Test non-existent provider
        no_attrs = self.manager.get_by_provider("NonExistent")
        self.assertEqual(len(no_attrs), 0)


class TestPluginIntegration(unittest.TestCase):
    """Test plugin integration with QGIS (mocked)"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('svg_library_plugin.QgsProject')
    @patch('svg_library_plugin.QSettings')
    def test_plugin_initialization(self, mock_settings, mock_project):
        """Test plugin initialization"""
        from svg_library_plugin import SvgLibraryPlugin

        # Create mock iface
        mock_iface = Mock()
        mock_iface.mainWindow.return_value = Mock()

        # Initialize plugin
        plugin = SvgLibraryPlugin(mock_iface)

        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.iface, mock_iface)
        self.assertIsNotNone(plugin.plugin_dir)

    @patch('svg_library_plugin.QgsProject')
    @patch('svg_library_plugin.QSettings')
    def test_plugin_gui_creation(self, mock_settings, mock_project):
        """Test plugin GUI creation"""
        from svg_library_plugin import SvgLibraryPlugin

        # Create mock iface
        mock_iface = Mock()
        mock_iface.mainWindow.return_value = Mock()
        mock_iface.addToolBarIcon = Mock()
        mock_iface.addPluginToMenu = Mock()
        mock_iface.addDockWidget = Mock()

        # Initialize and run plugin
        plugin = SvgLibraryPlugin(mock_iface)
        plugin.initGui()

        # Check that actions were added
        self.assertGreater(len(plugin.actions), 0)
        mock_iface.addToolBarIcon.assert_called()
        mock_iface.addPluginToMenu.assert_called()

        # Run the plugin
        plugin.run()

        # Check that dockwidget was created
        self.assertIsNotNone(plugin.dockwidget)
        mock_iface.addDockWidget.assert_called()

    @patch('svg_library_plugin.QgsProject')
    @patch('svg_library_plugin.QSettings')
    def test_plugin_unload(self, mock_settings, mock_project):
        """Test plugin unloading"""
        from svg_library_plugin import SvgLibraryPlugin

        # Create mock iface
        mock_iface = Mock()
        mock_iface.mainWindow.return_value = Mock()
        mock_iface.removePluginMenu = Mock()
        mock_iface.removeToolBarIcon = Mock()

        # Initialize plugin
        plugin = SvgLibraryPlugin(mock_iface)
        plugin.initGui()

        # Unload plugin
        plugin.unload()

        # Check that actions were removed
        mock_iface.removePluginMenu.assert_called()
        mock_iface.removeToolBarIcon.assert_called()


class TestImportStatements(unittest.TestCase):
    """Test that all imports are working correctly"""

    def test_relative_imports(self):
        """Test that relative imports in __init__.py work"""
        try:
            from __init__ import classFactory
            self.assertTrue(callable(classFactory))
        except ImportError as e:
            self.fail(f"Failed to import classFactory: {e}")

    def test_provider_imports(self):
        """Test that all provider imports work"""
        try:
            from providers import (
                NounProjectProvider,
                MaterialSymbolsProvider,
                MakiProvider,
                FontAwesomeProvider,
                GitHubProvider
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import providers: {e}")

    def test_attribution_utils_import(self):
        """Test attribution utils import"""
        try:
            from attribution_utils import AttributionManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import AttributionManager: {e}")


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestIconProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestSpecificProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestAttributionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestImportStatements))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Please review the output above.")

        if result.failures:
            print("\nFailed tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print("\nTests with errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)