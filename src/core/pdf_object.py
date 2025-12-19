"""
Simple PDF Handler - PDF Object Models

Defines base classes and concrete implementations for editable PDF objects.
These classes represent visual elements that can be added, modified, and
removed from PDF pages during editing operations.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from enum import Enum
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QColor


class ObjectType(Enum):
    """Enumeration of supported PDF object types."""
    TEXT = "text"
    IMAGE = "image"
    SHAPE = "shape"


class PDFObject(ABC):
    """
    Abstract base class for all editable PDF objects.
    
    This class defines the interface that all PDF objects must implement,
    following the Liskov Substitution Principle - any concrete object can
    be used wherever a PDFObject is expected.
    """
    
    def __init__(self, page_number: int, position: QPointF):
        """
        Initialize base PDF object.
        
        Args:
            page_number: Zero-indexed page number where object exists
            position: Object position in PDF coordinates (top-left corner)
        """
        self._page_number = page_number
        self._position = position
        self._bounding_box = QRectF()
        self._is_selected = False
        self._z_order = 0  # Layering order (higher = on top)
        self._annotation_id: Optional[int] = None  # PyMuPDF reference
    
    @abstractmethod
    def get_type(self) -> ObjectType:
        """
        Get the type of this object.
        
        Returns:
            ObjectType enum value
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize object to dictionary for storage/undo.
        
        Returns:
            Dictionary containing all object properties
        """
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Deserialize object from dictionary.
        
        Args:
            data: Dictionary containing object properties
        """
        pass
    
    def get_page_number(self) -> int:
        """Get the page number where this object exists."""
        return self._page_number
    
    def set_page_number(self, page_number: int) -> None:
        """Set the page number where this object exists."""
        self._page_number = page_number
    
    def get_position(self) -> QPointF:
        """Get the position of this object in PDF coordinates."""
        return self._position
    
    def set_position(self, position: QPointF) -> None:
        """Set the position of this object in PDF coordinates."""
        self._position = position
        self._update_bounding_box()
    
    def get_bounding_box(self) -> QRectF:
        """Get the bounding rectangle of this object."""
        return self._bounding_box
    
    def is_selected(self) -> bool:
        """Check if this object is currently selected."""
        return self._is_selected
    
    def set_selected(self, selected: bool) -> None:
        """Set the selection state of this object."""
        self._is_selected = selected
    
    def get_z_order(self) -> int:
        """Get the layering order (z-index) of this object."""
        return self._z_order
    
    def set_z_order(self, z_order: int) -> None:
        """Set the layering order (z-index) of this object."""
        self._z_order = z_order
    
    def get_annotation_id(self) -> Optional[int]:
        """Get the PyMuPDF annotation ID if this object is persisted."""
        return self._annotation_id
    
    def set_annotation_id(self, annotation_id: int) -> None:
        """Set the PyMuPDF annotation ID after persisting to PDF."""
        self._annotation_id = annotation_id
    
    def contains_point(self, point: QPointF) -> bool:
        """
        Check if a point is within this object's bounds.
        
        Args:
            point: Point in PDF coordinates
            
        Returns:
            True if point is inside object's bounding box
        """
        return self._bounding_box.contains(point)
    
    @abstractmethod
    def _update_bounding_box(self) -> None:
        """Update the bounding box based on current position and size."""
        pass


class TextObject(PDFObject):
    """
    Represents an editable text object in a PDF.
    
    Text objects can be positioned, styled, and modified. They are rendered
    as FreeText annotations in PyMuPDF for maximum compatibility.
    """
    
    # Default font options
    DEFAULT_FONT = "Helvetica"
    DEFAULT_SIZE = 12
    DEFAULT_COLOR = (0, 0, 0)  # Black
    
    def __init__(self, page_number: int, position: QPointF, content: str = ""):
        """
        Initialize a text object.
        
        Args:
            page_number: Zero-indexed page number
            position: Text position in PDF coordinates
            content: Text content (default empty)
        """
        super().__init__(page_number, position)
        
        # Text content and styling
        self._content = content
        self._font_name = self.DEFAULT_FONT
        self._font_size = self.DEFAULT_SIZE
        self._color = QColor(*self.DEFAULT_COLOR)
        self._bold = False
        self._italic = False
        self._underline = False
        self._alignment = "left"  # left, center, right
        
        # Calculate initial bounding box
        self._update_bounding_box()
    
    def get_type(self) -> ObjectType:
        """Return TEXT object type."""
        return ObjectType.TEXT
    
    def get_content(self) -> str:
        """Get the text content."""
        return self._content
    
    def set_content(self, content: str) -> None:
        """
        Set the text content.
        
        Args:
            content: New text content
        """
        self._content = content
        self._update_bounding_box()
    
    def get_font_name(self) -> str:
        """Get the font name."""
        return self._font_name
    
    def set_font_name(self, font_name: str) -> None:
        """Set the font name."""
        self._font_name = font_name
        self._update_bounding_box()
    
    def get_font_size(self) -> int:
        """Get the font size."""
        return self._font_size
    
    def set_font_size(self, size: int) -> None:
        """Set the font size."""
        self._font_size = max(1, size)  # Minimum size of 1
        self._update_bounding_box()
    
    def get_color(self) -> QColor:
        """Get the text color."""
        return self._color
    
    def set_color(self, color: QColor) -> None:
        """Set the text color."""
        self._color = color
    
    def is_bold(self) -> bool:
        """Check if text is bold."""
        return self._bold
    
    def set_bold(self, bold: bool) -> None:
        """Set bold style."""
        self._bold = bold
    
    def is_italic(self) -> bool:
        """Check if text is italic."""
        return self._italic
    
    def set_italic(self, italic: bool) -> None:
        """Set italic style."""
        self._italic = italic
    
    def is_underline(self) -> bool:
        """Check if text is underlined."""
        return self._underline
    
    def set_underline(self, underline: bool) -> None:
        """Set underline style."""
        self._underline = underline
    
    def get_alignment(self) -> str:
        """Get text alignment (left, center, right)."""
        return self._alignment
    
    def set_alignment(self, alignment: str) -> None:
        """
        Set text alignment.
        
        Args:
            alignment: One of "left", "center", "right"
        """
        if alignment in ("left", "center", "right"):
            self._alignment = alignment
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize text object to dictionary.
        
        Returns:
            Dictionary with all text properties
        """
        return {
            "type": self.get_type().value,
            "page_number": self._page_number,
            "position": {"x": self._position.x(), "y": self._position.y()},
            "content": self._content,
            "font_name": self._font_name,
            "font_size": self._font_size,
            "color": self._color.getRgb()[:3],  # RGB only
            "bold": self._bold,
            "italic": self._italic,
            "underline": self._underline,
            "alignment": self._alignment,
            "z_order": self._z_order,
            "annotation_id": self._annotation_id
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Deserialize text object from dictionary.
        
        Args:
            data: Dictionary containing text properties
        """
        self._page_number = data.get("page_number", 0)
        pos = data.get("position", {"x": 0, "y": 0})
        self._position = QPointF(pos["x"], pos["y"])
        self._content = data.get("content", "")
        self._font_name = data.get("font_name", self.DEFAULT_FONT)
        self._font_size = data.get("font_size", self.DEFAULT_SIZE)
        
        color_rgb = data.get("color", self.DEFAULT_COLOR)
        self._color = QColor(*color_rgb)
        
        self._bold = data.get("bold", False)
        self._italic = data.get("italic", False)
        self._underline = data.get("underline", False)
        self._alignment = data.get("alignment", "left")
        self._z_order = data.get("z_order", 0)
        self._annotation_id = data.get("annotation_id")
        
        self._update_bounding_box()
    
    def _update_bounding_box(self) -> None:
        """
        Update bounding box based on text content and styling.
        
        This is an approximation - actual rendering will determine precise bounds.
        """
        # Estimate text dimensions (rough calculation)
        # In practice, we'd use QFontMetrics for accurate measurement
        char_width = self._font_size * 0.6  # Average character width
        char_height = self._font_size * 1.2  # Line height
        
        text_width = len(self._content) * char_width
        text_height = char_height
        
        # Add some padding
        padding = 4
        self._bounding_box = QRectF(
            self._position.x() - padding,
            self._position.y() - padding,
            text_width + 2 * padding,
            text_height + 2 * padding
        )


class ObjectCollection:
    """
    Manages a collection of PDF objects for a document.
    
    This class provides methods to add, remove, find, and iterate over
    PDF objects. It maintains objects sorted by z-order for proper rendering.
    """
    
    def __init__(self):
        """Initialize empty object collection."""
        self._objects: list[PDFObject] = []
        self._next_z_order = 0
    
    def add(self, obj: PDFObject) -> None:
        """
        Add an object to the collection.
        
        Args:
            obj: PDF object to add
        """
        # Assign z-order if not set
        if obj.get_z_order() == 0:
            obj.set_z_order(self._next_z_order)
            self._next_z_order += 1
        
        self._objects.append(obj)
        self._sort_by_z_order()
    
    def remove(self, obj: PDFObject) -> bool:
        """
        Remove an object from the collection.
        
        Args:
            obj: PDF object to remove
            
        Returns:
            True if object was removed, False if not found
        """
        try:
            self._objects.remove(obj)
            return True
        except ValueError:
            return False
    
    def clear(self) -> None:
        """Remove all objects from the collection."""
        self._objects.clear()
        self._next_z_order = 0
    
    def get_all(self) -> list[PDFObject]:
        """Get all objects in z-order (bottom to top)."""
        return self._objects.copy()
    
    def get_by_page(self, page_number: int) -> list[PDFObject]:
        """
        Get all objects on a specific page.
        
        Args:
            page_number: Zero-indexed page number
            
        Returns:
            List of objects on the specified page
        """
        return [obj for obj in self._objects if obj.get_page_number() == page_number]
    
    def find_at_point(self, page_number: int, point: QPointF) -> Optional[PDFObject]:
        """
        Find the topmost object at a given point.
        
        Args:
            page_number: Zero-indexed page number
            point: Point in PDF coordinates
            
        Returns:
            The topmost object containing the point, or None
        """
        # Search from top to bottom (reverse z-order)
        for obj in reversed(self._objects):
            if obj.get_page_number() == page_number and obj.contains_point(point):
                return obj
        return None
    
    def get_selected(self) -> list[PDFObject]:
        """Get all currently selected objects."""
        return [obj for obj in self._objects if obj.is_selected()]
    
    def deselect_all(self) -> None:
        """Deselect all objects."""
        for obj in self._objects:
            obj.set_selected(False)
    
    def bring_forward(self, obj: PDFObject) -> None:
        """
        Bring object one layer forward (increase z-order by 1).
        
        Args:
            obj: Object to move forward
        """
        current_z = obj.get_z_order()
        # Find object above this one
        for other in self._objects:
            if other.get_z_order() == current_z + 1:
                other.set_z_order(current_z)
                obj.set_z_order(current_z + 1)
                self._sort_by_z_order()
                return
    
    def send_backward(self, obj: PDFObject) -> None:
        """
        Send object one layer backward (decrease z-order by 1).
        
        Args:
            obj: Object to move backward
        """
        current_z = obj.get_z_order()
        if current_z == 0:
            return  # Already at bottom
        
        # Find object below this one
        for other in self._objects:
            if other.get_z_order() == current_z - 1:
                other.set_z_order(current_z)
                obj.set_z_order(current_z - 1)
                self._sort_by_z_order()
                return
    
    def bring_to_front(self, obj: PDFObject) -> None:
        """
        Bring object to the front (highest z-order).
        
        Args:
            obj: Object to bring to front
        """
        obj.set_z_order(self._next_z_order)
        self._next_z_order += 1
        self._sort_by_z_order()
    
    def send_to_back(self, obj: PDFObject) -> None:
        """
        Send object to the back (lowest z-order).
        
        Args:
            obj: Object to send to back
        """
        # Shift all objects up by 1
        for other in self._objects:
            other.set_z_order(other.get_z_order() + 1)
        
        # Set this object to 0
        obj.set_z_order(0)
        self._next_z_order += 1
        self._sort_by_z_order()
    
    def _sort_by_z_order(self) -> None:
        """Sort objects by z-order (ascending)."""
        self._objects.sort(key=lambda obj: obj.get_z_order())
