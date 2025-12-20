"""
Simple PDF Handler - Conversion Controller

F6: Controls conversion operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot
from src.core.base_controller import BaseController
from .model import ConversionModel


class ConversionController(BaseController):
    """
    Controls conversion operations.
    Mock implementation for UI development.
    """
    
    conversion_started = Signal()
    conversion_completed = Signal()
    conversion_progress = Signal()
    
    def __init__(self):
        """Initializes conversion controller with model."""
        super().__init__()
        self._model = ConversionModel()
    
    @Slot()
    def convert_to_word(self) -> None:
        """Mock implementation of convert_to_word."""
        self.emit_start_operation("Convert To Word...")
        self.conversion_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def convert_to_image(self) -> None:
        """Mock implementation of convert_to_image."""
        self.emit_start_operation("Convert To Image...")
        self.conversion_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def convert_from_word(self) -> None:
        """Mock implementation of convert_from_word."""
        self.emit_start_operation("Convert From Word...")
        self.conversion_started.emit()
        self.emit_complete_operation("Operation completed")
