"""
Icon management system for professional UI.

Loads professional SVG icons from assets/icons directory.
"""

import os
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer


class IconManager:
    """
    Manages application icons using SVG files.
    
    Loads professional Lucide icons from assets/icons/ directory.
    Supports color customization and caching for performance.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for icon manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize icon manager."""
        if self._initialized:
            return
        
        self._initialized = True
        self._icon_cache = {}
        
        # Determine base path (relative to this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self._icons_dir = os.path.join(project_root, 'assets', 'icons')
        
        # Icon name mappings (icon_name -> svg_filename)
        self._icon_mappings = {
            # File operations
            'file_open': 'file-open.svg',
            'open': 'file-open.svg',
            'save': 'save.svg',
            'file_save': 'save.svg',
            'print': 'print.svg',
            
            # View operations
            'zoom_in': 'zoom-in.svg',
            'zoom_out': 'zoom-out.svg',
            'rotate': 'rotate.svg',
            'rotate_right': 'rotate.svg',
            
            # Edit operations
            'undo': 'undo.svg',
            'redo': 'redo.svg',
            'cut': 'cut.svg',
            'content_cut': 'cut.svg',
            'copy': 'copy.svg',
            'content_copy': 'copy.svg',
            'paste': 'paste.svg',
            'content_paste': 'paste.svg',
            'delete': 'delete.svg',
            'select_all': 'select-all.svg',
            
            # Annotation
            'highlight': 'highlight.svg',
            'comment': 'comment.svg',
            'comments': 'comment.svg',
            'note': 'note.svg',
            'note_add': 'note.svg',
            
            # Navigation & info
            'search': 'search.svg',
            'bookmark': 'bookmark.svg',
            'bookmarks': 'bookmark.svg',
            'layers': 'layers.svg',
            'pages': 'pages.svg',
            'article': 'pages.svg',
            'file_text': 'file-text.svg',
            'info': 'info.svg',
        }
    
    def get_icon(self, icon_name: str, size: int = 24, color: str = None) -> QIcon:
        """
        Get an icon by name with optional size and color.
        
        Args:
            icon_name: Icon identifier (e.g., 'file_open', 'save', 'zoom_in')
            size: Icon size in pixels (default: 24)
            color: Optional color override as hex string (e.g., '#0078d4')
            
        Returns:
            QIcon object
        """
        # Create cache key
        cache_key = f"{icon_name}_{size}_{color or 'default'}"
        
        # Return cached icon if available
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Get SVG filename
        svg_filename = self._icon_mappings.get(icon_name)
        if not svg_filename:
            # Try direct filename
            svg_filename = f"{icon_name}.svg"
        
        svg_path = os.path.join(self._icons_dir, svg_filename)
        
        # Check if file exists
        if not os.path.exists(svg_path):
            print(f"[IconManager] Warning: Icon file not found: {svg_path}")
            return QIcon()  # Return empty icon
        
        # Load and render SVG
        icon = self._load_svg_icon(svg_path, size, color)
        
        # Cache and return
        self._icon_cache[cache_key] = icon
        return icon
    
    def _load_svg_icon(self, svg_path: str, size: int, color: str = None) -> QIcon:
        """
        Load SVG file and create QIcon.
        
        Args:
            svg_path: Path to SVG file
            size: Icon size in pixels
            color: Optional color override
            
        Returns:
            QIcon object
        """
        # Qt can load SVG directly and handle scaling automatically
        icon = QIcon(svg_path)
        
        # If color customization is needed, we'd render to pixmap
        # For now, use native SVG rendering for best quality
        if color:
            # Custom color rendering (optional)
            pixmap = self._render_svg_with_color(svg_path, size, color)
            return QIcon(pixmap)
        
        return icon
    
    def _render_svg_with_color(self, svg_path: str, size: int, color: str) -> QPixmap:
        """
        Render SVG with custom color.
        
        Args:
            svg_path: Path to SVG file
            size: Icon size
            color: Color as hex string
            
        Returns:
            Colored pixmap
        """
        # Read SVG and replace color
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        
        # Simple color replacement (works for Lucide icons)
        # Lucide icons use currentColor, so we can replace it
        svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
        svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')
        
        # Render to pixmap
        renderer = QSvgRenderer(svg_content.encode('utf-8'))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    def has_icon(self, icon_name: str) -> bool:
        """
        Check if icon exists.
        
        Args:
            icon_name: Icon identifier
            
        Returns:
            True if icon exists
        """
        svg_filename = self._icon_mappings.get(icon_name)
        if not svg_filename:
            svg_filename = f"{icon_name}.svg"
        
        svg_path = os.path.join(self._icons_dir, svg_filename)
        return os.path.exists(svg_path)
    
    def clear_cache(self):
        """Clear icon cache (useful when theme changes)."""
        self._icon_cache.clear()


# Singleton instance
_icon_manager = None


def get_icon_manager() -> IconManager:
    """
    Get the global icon manager instance.
    
    Returns:
        IconManager singleton
    """
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


def get_icon(icon_name: str, size: int = 24, color: str = None) -> QIcon:
    """
    Convenience function to get an icon.
    
    Args:
        icon_name: Icon identifier
        size: Icon size in pixels
        color: Optional color override
        
    Returns:
        QIcon object
    """
    return get_icon_manager().get_icon(icon_name, size, color)
