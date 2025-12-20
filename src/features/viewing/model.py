"""
Simple PDF Handler - Viewing Model

Data model for PDF viewing state.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtGui import QImage
from typing import Optional


class ViewingModel(QObject):
    """
    Stores state for PDF viewing operations.
    """
    
    # Signals for property changes
    current_page_changed = Signal()
    page_count_changed = Signal()
    zoom_level_changed = Signal()
    rotation_changed = Signal()
    document_loaded_changed = Signal()
    current_image_changed = Signal()
    filename_changed = Signal()
    view_mode_changed = Signal()
    
    def __init__(self):
        """Initialize model with default values."""
        super().__init__()
        self._current_page = 1  # 1-indexed for UI
        self._page_count = 0
        self._zoom_level = 100
        self._rotation = 0
        self._document_loaded = False
        self._current_image: Optional[QImage] = None
        self._filename = ""
        self._view_mode = "single"  # single, two_page, or scroll
    
    # Current Page (1-indexed for UI)
    def get_current_page(self) -> int:
        return self._current_page
    
    def set_current_page(self, value: int) -> None:
        if self._current_page != value:
            self._current_page = value
            self.current_page_changed.emit()
    
    current_page = Property(int, get_current_page, set_current_page, notify=current_page_changed)
    
    # Page Count
    def get_page_count(self) -> int:
        return self._page_count
    
    def set_page_count(self, value: int) -> None:
        if self._page_count != value:
            self._page_count = value
            self.page_count_changed.emit()
    
    page_count = Property(int, get_page_count, set_page_count, notify=page_count_changed)
    
    # Zoom Level
    def get_zoom_level(self) -> int:
        return self._zoom_level
    
    def set_zoom_level(self, value: int) -> None:
        if self._zoom_level != value:
            self._zoom_level = value
            self.zoom_level_changed.emit()
    
    zoom_level = Property(int, get_zoom_level, set_zoom_level, notify=zoom_level_changed)
    
    # Rotation
    def get_rotation(self) -> int:
        return self._rotation
    
    def set_rotation(self, value: int) -> None:
        if self._rotation != value:
            self._rotation = value
            self.rotation_changed.emit()
    
    rotation = Property(int, get_rotation, set_rotation, notify=rotation_changed)
    
    # Document Loaded
    def get_document_loaded(self) -> bool:
        return self._document_loaded
    
    def set_document_loaded(self, value: bool) -> None:
        if self._document_loaded != value:
            self._document_loaded = value
            self.document_loaded_changed.emit()
    
    document_loaded = Property(bool, get_document_loaded, set_document_loaded, notify=document_loaded_changed)
    
    # Filename
    def get_filename(self) -> str:
        return self._filename
    
    def set_filename(self, value: str) -> None:
        if self._filename != value:
            self._filename = value
            self.filename_changed.emit()
    
    filename = Property(str, get_filename, set_filename, notify=filename_changed)
    
    # View Mode
    def get_view_mode(self) -> str:
        return self._view_mode
    
    def set_view_mode(self, value: str) -> None:
        if self._view_mode != value:
            self._view_mode = value
            self.view_mode_changed.emit()
    
    view_mode = Property(str, get_view_mode, set_view_mode, notify=view_mode_changed)
    
    # Current Image (for internal use, not exposed as Property)
    def set_current_image(self, image: Optional[QImage]) -> None:
        """Set the current page image."""
        self._current_image = image
        self.current_image_changed.emit()
    
    def get_current_image(self) -> Optional[QImage]:
        """Get the current page image."""
        return self._current_image
