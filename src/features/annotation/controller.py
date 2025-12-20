"""
Simple PDF Handler - Annotation Controller

F4: Controls annotation operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot
from src.core.base_controller import BaseController
from .model import AnnotationModel


class AnnotationController(BaseController):
    """
    Controls annotation operations.
    Mock implementation for UI development.
    """
    
    annotation_added = Signal()
    annotation_modified = Signal()
    annotation_deleted = Signal()
    
    def __init__(self):
        """Initializes annotation controller with model."""
        super().__init__()
        self._model = AnnotationModel()
    
    @Slot()
    def add_highlight(self) -> None:
        """Mock implementation of add_highlight."""
        self.emit_start_operation("Add Highlight...")
        self.annotation_added.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def add_note(self) -> None:
        """Mock implementation of add_note."""
        self.emit_start_operation("Add Note...")
        self.annotation_added.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def add_shape(self) -> None:
        """Mock implementation of add_shape."""
        self.emit_start_operation("Add Shape...")
        self.annotation_added.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def add_stamp(self) -> None:
        """Mock implementation of add_stamp."""
        self.emit_start_operation("Add Stamp...")
        self.annotation_added.emit()
        self.emit_complete_operation("Operation completed")
