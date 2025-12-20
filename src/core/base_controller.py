"""
Simple PDF Handler - Base Controller

Base class for all feature controllers providing common functionality.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class BaseController(QObject):
    """
    Base controller class for all feature controllers.
    
    Provides common functionality and signals that all controllers inherit.
    Each feature-specific controller extends this base class.
    
    Signals:
        error_occurred: Emitted when an error occurs (str: error message)
        operation_started: Emitted when a long-running operation begins
        operation_completed: Emitted when an operation completes successfully
        progress_updated: Emitted to report progress (int: percentage 0-100)
    """
    
    # Common signals available to all controllers
    error_occurred = Signal(str)
    operation_started = Signal(str)
    operation_completed = Signal(str)
    progress_updated = Signal(int)
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initializes base controller.
        
        Args:
            parent: Optional parent QObject for Qt ownership
        """
        super().__init__(parent)
        self._is_busy = False
    
    def emit_error(self, message: str) -> None:
        """
        Emits error signal with formatted message.
        
        Args:
            message: Error message to display
        """
        self._is_busy = False
        self.error_occurred.emit(message)
    
    def emit_start_operation(self, operation_name: str) -> None:
        """
        Emits signal indicating operation has started.
        
        Args:
            operation_name: Name of the operation starting
        """
        self._is_busy = True
        self.operation_started.emit(operation_name)
    
    def emit_complete_operation(self, message: str = "Operation completed") -> None:
        """
        Emits signal indicating operation completed successfully.
        
        Args:
            message: Success message to display
        """
        self._is_busy = False
        self.operation_completed.emit(message)
    
    def emit_progress(self, percentage: int) -> None:
        """
        Emits progress update signal.
        
        Args:
            percentage: Progress percentage (0-100)
        """
        # Clamp percentage to valid range
        clamped = max(0, min(100, percentage))
        self.progress_updated.emit(clamped)
    
    @property
    def is_busy(self) -> bool:
        """
        Returns whether controller is currently processing an operation.
        
        Returns:
            True if busy, False otherwise
        """
        return self._is_busy
