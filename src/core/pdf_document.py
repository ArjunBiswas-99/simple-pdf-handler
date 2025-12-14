"""
Simple PDF Handler - PDF Document Abstraction Layer

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

from typing import Optional, Tuple
from PyQt6.QtGui import QPixmap
from backend.pymupdf_backend import PyMuPDFBackend
from utils.constants import ViewMode


class PDFDocument:
    """
    High-level abstraction for PDF document operations.
    Decouples UI from backend implementation details.
    """
    
    def __init__(self):
        """Initialize PDF document with backend."""
        self._backend = PyMuPDFBackend()
        self._current_page: int = 0
        self._zoom_level: float = 1.0
        self._view_mode: ViewMode = ViewMode.CONTINUOUS
    
    def open(self, file_path: str) -> bool:
        """
        Open a PDF file for viewing.
        
        Args:
            file_path: Absolute path to the PDF file
            
        Returns:
            True if file opened successfully, False otherwise
        """
        success = self._backend.load_file(file_path)
        if success:
            self._current_page = 0
            self._zoom_level = 1.0
            self._view_mode = ViewMode.CONTINUOUS
        return success
    
    def close(self) -> None:
        """Close the current document and release resources."""
        self._backend.close()
        self._current_page = 0
        self._zoom_level = 1.0
        self._view_mode = ViewMode.CONTINUOUS
    
    def is_open(self) -> bool:
        """
        Check if a document is currently open.
        
        Returns:
            True if document is open, False otherwise
        """
        return self._backend.is_loaded()
    
    def get_page_count(self) -> int:
        """
        Get total number of pages in the document.
        
        Returns:
            Number of pages, or 0 if no document is open
        """
        return self._backend.get_page_count()
    
    def get_current_page(self) -> int:
        """
        Get the current page number (0-indexed).
        
        Returns:
            Current page number
        """
        return self._current_page
    
    def set_current_page(self, page_number: int) -> bool:
        """
        Set the current page number.
        
        Args:
            page_number: Page number to navigate to (0-indexed)
            
        Returns:
            True if page number is valid, False otherwise
        """
        if 0 <= page_number < self.get_page_count():
            self._current_page = page_number
            return True
        return False
    
    def get_zoom_level(self) -> float:
        """
        Get the current zoom level.
        
        Returns:
            Zoom level as a multiplier (1.0 = 100%)
        """
        return self._zoom_level
    
    def set_zoom_level(self, zoom: float) -> None:
        """
        Set the zoom level for rendering.
        
        Args:
            zoom: Zoom level as a multiplier (1.0 = 100%, 2.0 = 200%, etc.)
        """
        if zoom > 0:
            self._zoom_level = zoom
    
    def render_current_page(self) -> Optional[QPixmap]:
        """
        Render the current page at the current zoom level.
        
        Returns:
            QPixmap of the rendered page, or None if rendering fails
        """
        return self._backend.render_page(self._current_page, self._zoom_level)
    
    def render_page(self, page_number: int, zoom: Optional[float] = None) -> Optional[QPixmap]:
        """
        Render a specific page at a given zoom level.
        
        Args:
            page_number: Page number to render (0-indexed)
            zoom: Zoom level, or None to use current zoom level
            
        Returns:
            QPixmap of the rendered page, or None if rendering fails
        """
        zoom_to_use = zoom if zoom is not None else self._zoom_level
        return self._backend.render_page(page_number, zoom_to_use)
    
    def get_page_size(self, page_number: int) -> Optional[Tuple[float, float]]:
        """
        Get the dimensions of a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points, or None if page doesn't exist
        """
        return self._backend.get_page_size(page_number)
    
    def get_file_path(self) -> Optional[str]:
        """
        Get the file path of the currently open document.
        
        Returns:
            File path string, or None if no document is open
        """
        return self._backend.get_file_path()
    
    def get_view_mode(self) -> ViewMode:
        """
        Get the current view mode.
        
        Returns:
            Current ViewMode enum value
        """
        return self._view_mode
    
    def set_view_mode(self, mode: ViewMode) -> None:
        """
        Set the view mode for displaying pages.
        
        Args:
            mode: ViewMode enum value (CONTINUOUS, SINGLE_PAGE, or FACING)
        """
        self._view_mode = mode
