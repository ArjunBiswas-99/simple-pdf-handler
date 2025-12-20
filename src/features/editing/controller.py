"""
Simple PDF Handler - Editing Controller

F2: Controls PDF editing operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot, Property
from src.core.base_controller import BaseController
from .model import EditingModel


class EditingController(BaseController):
    """
    Controls PDF editing operations.
    
    Manages text editing, image insertion, and object manipulation.
    Mock implementation for UI development.
    
    Signals:
        text_added: Emitted when text is added
        image_inserted: Emitted when image is inserted
        object_modified: Emitted when object properties change
    """
    
    text_added = Signal(str)
    image_inserted = Signal(str)
    object_modified = Signal()
    
    def __init__(self):
        """Initializes editing controller with model."""
        super().__init__()
        self._model = EditingModel()
    
    @Slot(str, int, str)
    def add_text(self, text: str, x: int, y: int) -> None:
        """
        Adds text to current page.
        
        Args:
            text: Text content to add
            x: X coordinate
            y: Y coordinate
        """
        self.emit_start_operation("Adding text...")
        self.text_added.emit(text)
        self.emit_complete_operation(f"Text added at ({x}, {y})")
    
    @Slot(str)
    def insert_image(self, image_path: str) -> None:
        """
        Inserts image into document.
        
        Args:
            image_path: Path to image file
        """
        self.emit_start_operation("Inserting image...")
        self.image_inserted.emit(image_path)
        self.emit_complete_operation("Image inserted successfully")
    
    @Slot(str)
    def set_font(self, font_name: str) -> None:
        """Sets current font."""
        self._model.set_font(font_name)
        self.object_modified.emit()
    
    @Slot(int)
    def set_font_size(self, size: int) -> None:
        """Sets current font size."""
        self._model.set_font_size(size)
        self.object_modified.emit()
    
    @Slot(str)
    def set_text_color(self, color: str) -> None:
        """Sets current text color."""
        self._model.set_color(color)
        self.object_modified.emit()
    
    @Property(str, notify=object_modified)
    def current_font(self) -> str:
        """Returns current font name."""
        return self._model.current_font
    
    @Property(int, notify=object_modified)
    def current_font_size(self) -> int:
        """Returns current font size."""
        return self._model.current_font_size
