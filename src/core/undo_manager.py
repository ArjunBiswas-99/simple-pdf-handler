"""
Simple PDF Handler - Undo/Redo Manager

Manages undo and redo operations for PDF editing actions.
Uses command pattern with action objects.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class UndoAction(ABC):
    """
    Abstract base class for undo/redo actions.
    Each action must implement undo() and redo() methods.
    """
    
    @abstractmethod
    def undo(self, backend) -> bool:
        """
        Undo this action.
        
        Args:
            backend: PyMuPDF backend instance
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def redo(self, backend) -> bool:
        """
        Redo this action.
        
        Args:
            backend: PyMuPDF backend instance
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of this action.
        
        Returns:
            Description string
        """
        pass


class AddTextAction(UndoAction):
    """Action representing adding text to a PDF page."""
    
    def __init__(
        self,
        page_number: int,
        x: float,
        y: float,
        text: str,
        font_name: str,
        font_size: int,
        color: tuple,
        annot_xref: Optional[int] = None
    ):
        """
        Initialize add text action.
        
        Args:
            page_number: Page number (0-indexed)
            x, y: Position in PDF coordinates
            text: Text content
            font_name: Font name (helv, times, cour)
            font_size: Font size in points
            color: RGB color tuple (0.0-1.0 range)
            annot_xref: Annotation reference (set after adding)
        """
        self._page_number = page_number
        self._x = x
        self._y = y
        self._text = text
        self._font_name = font_name
        self._font_size = font_size
        self._color = color
        self._annot_xref = annot_xref
    
    def set_annot_xref(self, xref: int) -> None:
        """Set annotation reference after creation."""
        self._annot_xref = xref
    
    def undo(self, backend) -> bool:
        """Remove the text annotation."""
        if self._annot_xref is None:
            return False
        
        return backend.delete_annotation(self._page_number, self._annot_xref)
    
    def redo(self, backend) -> bool:
        """Re-add the text annotation."""
        xref = backend.add_text_annotation(
            self._page_number,
            self._x,
            self._y,
            self._text,
            font_name=self._font_name,
            font_size=self._font_size,
            color=self._color
        )
        
        if xref:
            self._annot_xref = xref
            return True
        return False
    
    def get_description(self) -> str:
        """Get action description."""
        preview = self._text[:20] + "..." if len(self._text) > 20 else self._text
        return f"Add text: \"{preview}\""
    
    def get_page_number(self) -> int:
        """Get the page number this action affects."""
        return self._page_number


class UndoManager(QObject):
    """
    Manages undo and redo stacks for edit operations.
    Emits signals when undo/redo availability changes.
    """
    
    # Signals
    can_undo_changed = pyqtSignal(bool)  # True if undo is available
    can_redo_changed = pyqtSignal(bool)  # True if redo is available
    
    def __init__(self, max_undo_levels: int = 50):
        """
        Initialize undo manager.
        
        Args:
            max_undo_levels: Maximum number of undo levels to keep
        """
        super().__init__()
        self._undo_stack = []
        self._redo_stack = []
        self._max_levels = max_undo_levels
    
    def record_action(self, action: UndoAction) -> None:
        """
        Record a new action.
        Clears redo stack and adds to undo stack.
        
        Args:
            action: Action to record
        """
        # Check state before
        was_empty = len(self._undo_stack) == 0
        
        # Add to undo stack
        self._undo_stack.append(action)
        
        # Limit stack size
        if len(self._undo_stack) > self._max_levels:
            self._undo_stack.pop(0)
        
        # Clear redo stack (new action invalidates redo history)
        old_can_redo = self.can_redo()
        self._redo_stack.clear()
        
        # Emit signals
        if was_empty:
            self.can_undo_changed.emit(True)
        
        if old_can_redo:
            self.can_redo_changed.emit(False)
    
    def undo(self, backend) -> Optional[int]:
        """
        Undo the most recent action.
        
        Args:
            backend: PyMuPDF backend instance
            
        Returns:
            Page number affected, or None if undo failed
        """
        if not self.can_undo():
            return None
        
        # Pop from undo stack
        action = self._undo_stack.pop()
        
        # Execute undo
        success = action.undo(backend)
        
        if success:
            # Add to redo stack
            self._redo_stack.append(action)
            
            # Emit signals
            if not self.can_undo():
                self.can_undo_changed.emit(False)
            
            if len(self._redo_stack) == 1:
                self.can_redo_changed.emit(True)
            
            # Return affected page number
            if hasattr(action, 'get_page_number'):
                return action.get_page_number()
            return 0
        else:
            # Undo failed - put action back
            self._undo_stack.append(action)
            return None
    
    def redo(self, backend) -> Optional[int]:
        """
        Redo the most recently undone action.
        
        Args:
            backend: PyMuPDF backend instance
            
        Returns:
            Page number affected, or None if redo failed
        """
        if not self.can_redo():
            return None
        
        # Pop from redo stack
        action = self._redo_stack.pop()
        
        # Execute redo
        success = action.redo(backend)
        
        if success:
            # Add back to undo stack
            self._undo_stack.append(action)
            
            # Emit signals
            if not self.can_redo():
                self.can_redo_changed.emit(False)
            
            if len(self._undo_stack) == 1:
                self.can_undo_changed.emit(True)
            
            # Return affected page number
            if hasattr(action, 'get_page_number'):
                return action.get_page_number()
            return 0
        else:
            # Redo failed - put action back
            self._redo_stack.append(action)
            return None
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def clear(self) -> None:
        """Clear all undo/redo history."""
        old_can_undo = self.can_undo()
        old_can_redo = self.can_redo()
        
        self._undo_stack.clear()
        self._redo_stack.clear()
        
        # Emit signals if state changed
        if old_can_undo:
            self.can_undo_changed.emit(False)
        if old_can_redo:
            self.can_redo_changed.emit(False)
    
    def get_undo_description(self) -> Optional[str]:
        """
        Get description of the action that would be undone.
        
        Returns:
            Description string, or None if no undo available
        """
        if self.can_undo():
            return self._undo_stack[-1].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """
        Get description of the action that would be redone.
        
        Returns:
            Description string, or None if no redo available
        """
        if self.can_redo():
            return self._redo_stack[-1].get_description()
        return None
