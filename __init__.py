"""
SVG Library Browser Plugin for QGIS
"""

def classFactory(iface):
    """Load SvgLibraryPlugin class from file svg_library_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .svg_library_plugin import SvgLibraryPlugin
    return SvgLibraryPlugin(iface)