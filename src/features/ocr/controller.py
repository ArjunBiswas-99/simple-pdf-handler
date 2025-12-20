"""
Simple PDF Handler - OCR Controller

F7: Controls ocr operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot
from src.core.base_controller import BaseController
from .model import OCRModel


class OCRController(BaseController):
    """
    Controls OCR operations.
    Mock implementation for UI development.
    """
    
    ocr_started = Signal()
    ocr_completed = Signal()
    ocr_progress = Signal()
    
    def __init__(self):
        """Initializes OCR controller with model."""
        super().__init__()
        self._model = OCRModel()
    
    @Slot()
    def process_ocr(self) -> None:
        """Mock implementation of process_ocr."""
        self.emit_start_operation("Process Ocr...")
        self.ocr_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def set_language(self) -> None:
        """Mock implementation of set_language."""
        self.emit_start_operation("Set Language...")
        self.ocr_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def save_ocr_result(self) -> None:
        """Mock implementation of save_ocr_result."""
        self.emit_start_operation("Save Ocr Result...")
        self.ocr_started.emit()
        self.emit_complete_operation("Operation completed")
