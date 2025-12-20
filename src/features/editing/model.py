"""
Simple PDF Handler - Editing Model

Data model for PDF editing state.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional, Dict, Any


class EditingModel:
    """
    Stores state for PDF editing operations.
    
    Maintains text and image editing state.
    Mock implementation for UI development.
    """
    
    def __init__(self):
        """Initializes model with default values."""
        self._current_font: str = "Arial"
        self._current_font_size: int = 12
        self._current_color: str = "#000000"
        self._is_bold: bool = False
        self._is_italic: bool = False
        self._is_underline: bool = False
    
    def set_font(self, font_name: str) -> None:
        """Sets current font."""
        self._current_font = font_name
    
    def set_font_size(self, size: int) -> None:
        """Sets current font size."""
        self._current_font_size = max(8, min(72, size))
    
    def set_color(self, color: str) -> None:
        """Sets current text color."""
        self._current_color = color
    
    @property
    def current_font(self) -> str:
        """Returns current font name."""
        return self._current_font
    
    @property
    def current_font_size(self) -> int:
        """Returns current font size."""
        return self._current_font_size
    
    @property
    def current_color(self) -> str:
        """Returns current text color."""
        return self._current_color
