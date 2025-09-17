"""
Utilities for attribution tracking and project metadata management
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from qgis.core import QgsProject


class AttributionManager:
    """Manages attribution and license tracking for imported SVGs"""
    
    def __init__(self):
        self.attributions = []
        
    def add_attribution(self, icon_data: Dict[str, Any]):
        """Add attribution for an imported icon"""
        attribution = {
            'icon_id': icon_data.get('id'),
            'icon_name': icon_data.get('name'),
            'provider': icon_data.get('provider'),
            'license': icon_data.get('license'),
            'attribution_text': icon_data.get('attribution'),
            'url': icon_data.get('url'),
            'imported_date': datetime.now().isoformat(),
            'file_path': icon_data.get('file_path')
        }
        self.attributions.append(attribution)
        
    def get_all_attributions(self) -> List[Dict[str, Any]]:
        """Get all tracked attributions"""
        return self.attributions.copy()
        
    def export_attributions(self, format_type: str = 'text') -> str:
        """Export attributions in specified format"""
        if format_type == 'text':
            return self._export_as_text()
        elif format_type == 'json':
            return self._export_as_json()
        elif format_type == 'html':
            return self._export_as_html()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
    def _export_as_text(self) -> str:
        """Export attributions as plain text"""
        lines = ["SVG Icon Attributions", "=" * 20, ""]
        
        for attr in self.attributions:
            lines.append(f"Icon: {attr['icon_name']}")
            lines.append(f"Provider: {attr['provider']}")
            lines.append(f"License: {attr['license']}")
            lines.append(f"Attribution: {attr['attribution_text']}")
            lines.append(f"URL: {attr['url']}")
            lines.append(f"Imported: {attr['imported_date']}")
            lines.append("")
            
        return "\n".join(lines)
        
    def _export_as_json(self) -> str:
        """Export attributions as JSON"""
        return json.dumps({
            'exported_date': datetime.now().isoformat(),
            'total_icons': len(self.attributions),
            'attributions': self.attributions
        }, indent=2)
        
    def _export_as_html(self) -> str:
        """Export attributions as HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SVG Icon Attributions</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .attribution { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
                .icon-name { font-weight: bold; color: #333; }
                .provider { color: #666; }
                .license { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>SVG Icon Attributions</h1>
        """
        
        for attr in self.attributions:
            html += f"""
            <div class="attribution">
                <div class="icon-name">{attr['icon_name']}</div>
                <div class="provider">Provider: {attr['provider']}</div>
                <div class="license">License: {attr['license']}</div>
                <div>Attribution: {attr['attribution_text']}</div>
                <div><a href="{attr['url']}">Source URL</a></div>
                <div>Imported: {attr['imported_date']}</div>
            </div>
            """
            
        html += """
        </body>
        </html>
        """
        return html


class ProjectMetadataManager:
    """Manages integration of SVG attributions with QGIS project metadata"""
    
    METADATA_KEY = "svg_library_attributions"
    
    @staticmethod
    def save_attributions_to_project(attributions: List[Dict[str, Any]]):
        """Save attributions to current QGIS project metadata"""
        project = QgsProject.instance()
        
        # Get existing metadata
        existing_data = project.readEntry("svg_library", ProjectMetadataManager.METADATA_KEY)[0]
        if existing_data:
            try:
                existing_attributions = json.loads(existing_data)
            except:
                existing_attributions = []
        else:
            existing_attributions = []
            
        # Merge new attributions (avoid duplicates)
        existing_ids = {attr.get('icon_id') for attr in existing_attributions}
        new_attributions = [attr for attr in attributions 
                          if attr.get('icon_id') not in existing_ids]
                          
        all_attributions = existing_attributions + new_attributions
        
        # Save back to project
        project.writeEntry("svg_library", ProjectMetadataManager.METADATA_KEY, 
                          json.dumps(all_attributions))
        
        return len(new_attributions)
        
    @staticmethod
    def load_attributions_from_project() -> List[Dict[str, Any]]:
        """Load attributions from current QGIS project metadata"""
        project = QgsProject.instance()
        data = project.readEntry("svg_library", ProjectMetadataManager.METADATA_KEY)[0]

        if data:
            try:
                return json.loads(data)
            except:
                return []
        return []

    @staticmethod
    def get_attributions_from_project() -> List[Dict[str, Any]]:
        """Alias for load_attributions_from_project"""
        return ProjectMetadataManager.load_attributions_from_project()

    @staticmethod
    def add_single_attribution(icon_data: Dict[str, Any]):
        """Add a single attribution to project metadata"""
        existing = ProjectMetadataManager.load_attributions_from_project()

        # Check if already exists
        icon_id = icon_data.get('id', '')
        if not any(attr.get('id') == icon_id for attr in existing):
            existing.append(icon_data)

            # Save back to project
            project = QgsProject.instance()
            project.writeEntry("svg_library", ProjectMetadataManager.METADATA_KEY,
                             json.dumps(existing))
        
    @staticmethod
    def clear_project_attributions():
        """Clear all attributions from project metadata"""
        project = QgsProject.instance()
        project.removeEntry("svg_library", ProjectMetadataManager.METADATA_KEY)
        
    @staticmethod
    def export_project_attributions(format_type: str = 'text') -> str:
        """Export project attributions in specified format"""
        attributions = ProjectMetadataManager.load_attributions_from_project()
        
        manager = AttributionManager()
        manager.attributions = attributions
        
        return manager.export_attributions(format_type)


class LicenseChecker:
    """Utilities for checking and validating icon licenses"""
    
    COMMON_LICENSES = {
        'CC0': {
            'name': 'Creative Commons Zero v1.0 Universal',
            'url': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'commercial_use': True,
            'attribution_required': False
        },
        'CC BY 4.0': {
            'name': 'Creative Commons Attribution 4.0 International',
            'url': 'https://creativecommons.org/licenses/by/4.0/',
            'commercial_use': True,
            'attribution_required': True
        },
        'MIT': {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT',
            'commercial_use': True,
            'attribution_required': True
        },
        'Apache 2.0': {
            'name': 'Apache License 2.0',
            'url': 'https://www.apache.org/licenses/LICENSE-2.0',
            'commercial_use': True,
            'attribution_required': True
        }
    }
    
    @staticmethod
    def get_license_info(license_name: str) -> Dict[str, Any]:
        """Get information about a license"""
        return LicenseChecker.COMMON_LICENSES.get(license_name, {
            'name': license_name,
            'url': '',
            'commercial_use': None,
            'attribution_required': None
        })
        
    @staticmethod
    def requires_attribution(license_name: str) -> bool:
        """Check if a license requires attribution"""
        info = LicenseChecker.get_license_info(license_name)
        return info.get('attribution_required', True)  # Default to requiring attribution
        
    @staticmethod
    def allows_commercial_use(license_name: str) -> bool:
        """Check if a license allows commercial use"""
        info = LicenseChecker.get_license_info(license_name)
        return info.get('commercial_use', False)  # Default to not allowing commercial use