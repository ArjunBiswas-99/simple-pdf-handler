"""
Simple PDF Handler - Merging Controller

F5: Controls merging operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot
from src.core.base_controller import BaseController
from .model import MergingModel


class MergingController(BaseController):
    """
    Controls merging operations.
    Mock implementation for UI development.
    """
    
    merge_started = Signal()
    merge_completed = Signal()
    merge_progress = Signal()
    
    def __init__(self):
        """Initializes merging controller with model."""
        super().__init__()
        self._model = MergingModel()
    
    @Slot()
    def add_file_to_merge(self) -> None:
        """Mock implementation of add_file_to_merge."""
        self.emit_start_operation("Add File To Merge...")
        self.merge_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def remove_file_from_merge(self) -> None:
        """Mock implementation of remove_file_from_merge."""
        self.emit_start_operation("Remove File From Merge...")
        self.merge_started.emit()
        self.emit_complete_operation("Operation completed")
    @Slot()
    def merge_files(self) -> None:
        """Mock implementation of merge_files."""
        self.emit_start_operation("Merge Files...")
        self.merge_started.emit()
        self.emit_complete_operation("Operation completed")
