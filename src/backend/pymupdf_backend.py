"""
PyMuPDF backend implementation for PDF operations.
Provides concrete implementation of PDF processing using the fitz library.
"""

import fitz
from typing import Optional, Tuple
from PyQt6.QtGui import QImage, QPixmap


class PyMuPDFBackend:
    """
    PyMuPDF (fitz) backend for PDF document operations.
    Handles low-level PDF processing and rendering.
    """
    
    def __init__(self):
        """Initialize the PyMuPDF backend."""
        self._document: Optional[fitz.Document] = None
        self._file_path: Optional[str] = None
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a PDF file into memory.
        
        Args:
            file_path: Absolute path to the PDF file
            
        Returns:
            True if file loaded successfully, False otherwise
        """
        try:
            self._document = fitz.open(file_path)
            self._file_path = file_path
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def close(self) -> None:
        """Close the currently loaded PDF document and release resources."""
        if self._document:
            self._document.close()
            self._document = None
            self._file_path = None
    
    def is_loaded(self) -> bool:
        """
        Check if a PDF document is currently loaded.
        
        Returns:
            True if a document is loaded, False otherwise
        """
        return self._document is not None
    
    def get_page_count(self) -> int:
        """
        Get the total number of pages in the loaded document.
        
        Returns:
            Number of pages, or 0 if no document is loaded
        """
        if not self._document:
            return 0
        return self._document.page_count
    
    def get_file_path(self) -> Optional[str]:
        """
        Get the file path of the currently loaded document.
        
        Returns:
            File path string, or None if no document is loaded
        """
        return self._file_path
    
    def render_page(self, page_number: int, zoom: float = 1.0) -> Optional[QPixmap]:
        """
        Render a specific page as a QPixmap for display.
        
        Args:
            page_number: Page number to render (0-indexed)
            zoom: Zoom factor (1.0 = 100%, 2.0 = 200%, etc.)
            
        Returns:
            QPixmap containing the rendered page, or None if rendering fails
        """
        if not self._document:
            return None
        
        if page_number < 0 or page_number >= self._document.page_count:
            return None
        
        try:
            # Get the page
            page = self._document[page_number]
            
            # Create transformation matrix for zoom
            # Higher DPI = better quality but slower rendering
            matrix = fitz.Matrix(zoom, zoom)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert fitz pixmap to QImage
            img_format = QImage.Format.Format_RGB888
            qimage = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                img_format
            )
            
            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(qimage.copy())
            
            return pixmap
            
        except Exception as e:
            print(f"Error rendering page {page_number}: {e}")
            return None
    
    def get_page_size(self, page_number: int) -> Optional[Tuple[float, float]]:
        """
        Get the dimensions of a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points, or None if page doesn't exist
        """
        if not self._document:
            return None
        
        if page_number < 0 or page_number >= self._document.page_count:
            return None
        
        try:
            page = self._document[page_number]
            rect = page.rect
            return (rect.width, rect.height)
        except Exception as e:
            print(f"Error getting page size: {e}")
            return None
