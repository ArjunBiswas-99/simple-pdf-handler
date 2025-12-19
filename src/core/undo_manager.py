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


class DeletePageAction(UndoAction):
    """
    Action representing deletion of a page from PDF.
    Stores complete page data for full restoration on undo.
    """
    
    def __init__(self, page_number: int, page_data: Optional[bytes] = None):
        """
        Initialize delete page action.
        
        Args:
            page_number: Page number that was deleted (0-indexed)
            page_data: Serialized page data for restoration (captured during deletion)
        """
        self._page_number = page_number
        self._page_data = page_data
    
    def set_page_data(self, data: bytes) -> None:
        """
        Store page data after deletion for undo.
        
        Args:
            data: Serialized page content as bytes
        """
        self._page_data = data
    
    def undo(self, backend) -> bool:
        """
        Restore the deleted page with complete content.
        Uses stored page data to restore exact page state.
        """
        if not self._page_data:
            print("Cannot undo: No page data stored")
            return False
        
        # Restore page from serialized data
        return backend.restore_page(self._page_number, self._page_data)
    
    def redo(self, backend) -> bool:
        """
        Re-delete the page.
        Captures page data again for potential future undo.
        """
        success, new_page_data = backend.delete_page(self._page_number)
        
        if success:
            # Update stored data with newly captured data
            self._page_data = new_page_data
        
        return success
    
    def get_description(self) -> str:
        """Get action description."""
        return f"Delete page {self._page_number + 1}"
    
    def get_page_number(self) -> int:
        """Get the page number this action affects."""
        return self._page_number


class InsertPageAction(UndoAction):
    """Action representing insertion of a blank page."""
    
    def __init__(self, position: int, width: float = 595, height: float = 842):
        """
        Initialize insert page action.
        
        Args:
            position: Position where page was inserted (0-indexed)
            width: Page width in points
            height: Page height in points
        """
        self._position = position
        self._width = width
        self._height = height
    
    def undo(self, backend) -> bool:
        """Remove the inserted page."""
        return backend.delete_page(self._position)
    
    def redo(self, backend) -> bool:
        """Re-insert the blank page."""
        return backend.insert_blank_page(self._position, self._width, self._height)
    
    def get_description(self) -> str:
        """Get action description."""
        return f"Insert blank page at position {self._position + 1}"
    
    def get_page_number(self) -> int:
        """Get the page number this action affects."""
        return self._position


class MovePageAction(UndoAction):
    """
    Action representing moving a page to a new position.
    Handles complex undo logic for page reordering.
    """
    
    def __init__(self, from_page: int, to_page: int):
        """
        Initialize move page action.
        
        Args:
            from_page: Original page position (0-indexed)
            to_page: New page position (0-indexed)
        """
        self._from_page = from_page
        self._to_page = to_page
        
        # Calculate where the page actually ends up after the move
        # PyMuPDF's move_page behavior: moves page to BEFORE to_page position
        # If moving forward: page ends up at to_page - 1
        # If moving backward: page ends up at to_page
        if from_page < to_page:
            self._actual_position = to_page - 1
        else:
            self._actual_position = to_page
    
    def undo(self, backend) -> bool:
        """
        Move page back to original position.
        Must account for PyMuPDF's move behavior.
        """
        # To undo: move from current position back to original
        # If original move was forward, we need to move backward
        # If original move was backward, we need to move forward
        
        if self._from_page < self._to_page:
            # Was moved forward, now move backward
            # Page is currently at to_page-1, move it back to from_page
            return backend.move_page(self._actual_position, self._from_page)
        else:
            # Was moved backward, now move forward
            # Page is currently at to_page, move it to from_page+1 (to get back to from_page)
            return backend.move_page(self._actual_position, self._from_page + 1)
    
    def redo(self, backend) -> bool:
        """Re-apply the page move."""
        return backend.move_page(self._from_page, self._to_page)
    
    def get_description(self) -> str:
        """Get action description."""
        return f"Move page {self._from_page + 1} to position {self._to_page + 1}"
    
    def get_page_number(self) -> int:
        """Get the page number this action affects."""
        return self._actual_position


class AddShapeAction(UndoAction):
    """
    Action representing adding a shape to a PDF page.
    Captures page state before drawing to enable undo.
    """
    
    def __init__(self, shape_data: dict, page_snapshot: Optional[bytes] = None):
        """
        Initialize add shape action.
        
        Args:
            shape_data: Dictionary containing shape type, coordinates, and properties
            page_snapshot: Serialized page state before shape was drawn (for undo)
        """
        self._shape_data = shape_data
        self._page_number = shape_data.get('page_number', 0)
        self._page_snapshot = page_snapshot
    
    def set_page_snapshot(self, snapshot: bytes) -> None:
        """
        Store page snapshot after shape is drawn.
        
        Args:
            snapshot: Serialized page state before drawing
        """
        self._page_snapshot = snapshot
    
    def undo(self, backend) -> bool:
        """
        Remove the shape by restoring page to state before drawing.
        """
        if not self._page_snapshot:
            print("Cannot undo shape: No page snapshot available")
            return False
        
        # Restore page from snapshot
        return backend.restore_page_from_snapshot(self._page_number, self._page_snapshot)
    
    def redo(self, backend) -> bool:
        """Re-add the shape."""
        shape_type = self._shape_data.get('type')
        page_num = self._shape_data.get('page_number')
        props = self._shape_data.get('properties', {})
        
        # Convert QColor to RGB tuple (0-1 range)
        border_color = props.get('border_color')
        if border_color:
            border_rgb = (
                border_color.red() / 255.0,
                border_color.green() / 255.0,
                border_color.blue() / 255.0
            )
        else:
            border_rgb = (0, 0, 0)
        
        border_width = props.get('border_width', 2)
        
        # Get fill color if enabled
        fill_rgba = None
        if props.get('fill_enabled') and props.get('fill_color'):
            fill_color = props.get('fill_color')
            fill_rgba = (
                fill_color.red() / 255.0,
                fill_color.green() / 255.0,
                fill_color.blue() / 255.0,
                fill_color.alpha() / 255.0
            )
        
        # Draw shape based on type
        if shape_type == 'rectangle':
            return backend.add_rectangle_shape(
                page_num,
                self._shape_data['x0'],
                self._shape_data['y0'],
                self._shape_data['x1'],
                self._shape_data['y1'],
                border_rgb,
                border_width,
                fill_rgba
            )
        elif shape_type == 'circle':
            return backend.add_circle_shape(
                page_num,
                self._shape_data['center_x'],
                self._shape_data['center_y'],
                self._shape_data['radius'],
                border_rgb,
                border_width,
                fill_rgba
            )
        elif shape_type == 'line':
            return backend.add_line_shape(
                page_num,
                self._shape_data['x0'],
                self._shape_data['y0'],
                self._shape_data['x1'],
                self._shape_data['y1'],
                border_rgb,
                border_width
            )
        
        return False
    
    def get_description(self) -> str:
        """Get action description."""
        shape_type = self._shape_data.get('type', 'shape')
        return f"Add {shape_type}"
    
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
