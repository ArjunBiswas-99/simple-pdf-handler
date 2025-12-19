"""
Simple PDF Handler - Document State Manager

Manages the modification state of the PDF document, tracking whether changes
have been made that require saving. Implements the Observer pattern through
Qt signals to notify UI components of state changes.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal


class DocumentStateManager(QObject):
    """
    Manages document modification state and notifies observers of changes.
    
    This class is responsible for tracking whether a document has unsaved changes
    (dirty state) and notifying the UI when the state changes. It follows the
    Single Responsibility Principle by focusing solely on state management.
    """
    
    # Signal emitted when document state changes (clean/dirty)
    state_changed = pyqtSignal(bool)  # True = dirty, False = clean
    
    def __init__(self):
        """Initialize the document state manager with clean state."""
        super().__init__()
        self._is_dirty = False
        self._file_path: Optional[str] = None
    
    def mark_dirty(self) -> None:
        """
        Mark the document as modified (unsaved changes exist).
        
        This is called whenever an edit operation is performed (add text,
        modify object, etc.). Emits state_changed signal if state actually changed.
        """
        if not self._is_dirty:
            self._is_dirty = True
            self.state_changed.emit(True)
    
    def mark_clean(self) -> None:
        """
        Mark the document as saved (no unsaved changes).
        
        This is called after successfully saving the document. Emits state_changed
        signal if state actually changed.
        """
        if self._is_dirty:
            self._is_dirty = False
            self.state_changed.emit(False)
    
    def is_dirty(self) -> bool:
        """
        Check if document has unsaved changes.
        
        Returns:
            True if document has been modified since last save, False otherwise
        """
        return self._is_dirty
    
    def set_file_path(self, file_path: Optional[str]) -> None:
        """
        Set the current file path being edited.
        
        Args:
            file_path: Path to the PDF file, or None if no file loaded
        """
        self._file_path = file_path
        # Reset dirty state when loading new file
        if self._is_dirty:
            self._is_dirty = False
            self.state_changed.emit(False)
    
    def get_file_path(self) -> Optional[str]:
        """
        Get the current file path being edited.
        
        Returns:
            Path to the PDF file, or None if no file loaded
        """
        return self._file_path
    
    def reset(self) -> None:
        """
        Reset state manager to initial state.
        
        Called when closing a document. Clears file path and marks as clean.
        """
        was_dirty = self._is_dirty
        self._is_dirty = False
        self._file_path = None
        
        if was_dirty:
            self.state_changed.emit(False)
