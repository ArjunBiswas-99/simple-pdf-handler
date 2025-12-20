"""
Simple PDF Handler - PDF Renderer

Handles PDF rendering using PyMuPDF (fitz).

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

import fitz  # PyMuPDF
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QByteArray
from typing import Optional, Tuple


class PDFRenderer:
    """Renders PDF pages using PyMuPDF."""
    
    def __init__(self):
        """Initialize PDF renderer."""
        self.document: Optional[fitz.Document] = None
        self.current_page = 0
        self.zoom_level = 100  # Percentage
        self.rotation = 0  # Degrees: 0, 90, 180, 270
    
    def open_pdf(self, filepath: str) -> bool:
        """
        Open a PDF file.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.document = fitz.open(filepath)
            self.current_page = 0
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            self.document = None
            return False
    
    def close_pdf(self) -> None:
        """Close the currently open PDF."""
        if self.document:
            self.document.close()
            self.document = None
            self.current_page = 0
    
    def get_page_count(self) -> int:
        """
        Get total number of pages.
        
        Returns:
            Number of pages or 0 if no document open
        """
        if self.document:
            return len(self.document)
        return 0
    
    def set_page(self, page_num: int) -> bool:
        """
        Set current page number.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            True if valid page number
        """
        if self.document and 0 <= page_num < len(self.document):
            self.current_page = page_num
            return True
        return False
    
    def next_page(self) -> bool:
        """
        Go to next page.
        
        Returns:
            True if moved to next page
        """
        if self.document and self.current_page < len(self.document) - 1:
            self.current_page += 1
            return True
        return False
    
    def previous_page(self) -> bool:
        """
        Go to previous page.
        
        Returns:
            True if moved to previous page
        """
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def set_zoom(self, zoom_level: int) -> None:
        """
        Set zoom level.
        
        Args:
            zoom_level: Zoom percentage (e.g., 100, 125, 150, 200)
        """
        self.zoom_level = max(25, min(400, zoom_level))  # Clamp between 25% and 400%
    
    def zoom_in(self) -> int:
        """
        Increase zoom level.
        
        Returns:
            New zoom level
        """
        zoom_steps = [50, 75, 100, 125, 150, 175, 200, 250, 300, 400]
        current_idx = min(range(len(zoom_steps)), 
                         key=lambda i: abs(zoom_steps[i] - self.zoom_level))
        
        if current_idx < len(zoom_steps) - 1:
            self.zoom_level = zoom_steps[current_idx + 1]
        
        return self.zoom_level
    
    def zoom_out(self) -> int:
        """
        Decrease zoom level.
        
        Returns:
            New zoom level
        """
        zoom_steps = [50, 75, 100, 125, 150, 175, 200, 250, 300, 400]
        current_idx = min(range(len(zoom_steps)), 
                         key=lambda i: abs(zoom_steps[i] - self.zoom_level))
        
        if current_idx > 0:
            self.zoom_level = zoom_steps[current_idx - 1]
        
        return self.zoom_level
    
    def rotate(self, degrees: int) -> None:
        """
        Set rotation.
        
        Args:
            degrees: Rotation in degrees (0, 90, 180, 270)
        """
        self.rotation = degrees % 360
    
    def rotate_right(self) -> int:
        """
        Rotate 90 degrees clockwise.
        
        Returns:
            New rotation value
        """
        self.rotation = (self.rotation + 90) % 360
        return self.rotation
    
    def rotate_left(self) -> int:
        """
        Rotate 90 degrees counter-clockwise.
        
        Returns:
            New rotation value
        """
        self.rotation = (self.rotation - 90) % 360
        return self.rotation
    
    def render_page(self, page_num: Optional[int] = None) -> Optional[QImage]:
        """
        Render a page as QImage.
        
        Args:
            page_num: Page number to render (uses current page if None)
            
        Returns:
            QImage of rendered page or None if error
        """
        if not self.document:
            return None
        
        if page_num is None:
            page_num = self.current_page
        
        if not (0 <= page_num < len(self.document)):
            return None
        
        try:
            page = self.document[page_num]
            
            # Calculate zoom matrix
            zoom_factor = self.zoom_level / 100.0
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Apply rotation
            if self.rotation != 0:
                mat = mat * fitz.Matrix(self.rotation)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to QImage
            img_data = pix.samples
            qimage = QImage(
                img_data,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format_RGB888
            )
            
            # Make a copy since img_data will be freed
            return qimage.copy()
            
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None
    
    def get_page_size(self, page_num: Optional[int] = None) -> Tuple[int, int]:
        """
        Get page dimensions.
        
        Args:
            page_num: Page number (uses current page if None)
            
        Returns:
            Tuple of (width, height) or (0, 0) if error
        """
        if not self.document:
            return (0, 0)
        
        if page_num is None:
            page_num = self.current_page
        
        if not (0 <= page_num < len(self.document)):
            return (0, 0)
        
        try:
            page = self.document[page_num]
            rect = page.rect
            return (int(rect.width), int(rect.height))
        except:
            return (0, 0)
    
    def get_document_info(self) -> dict:
        """
        Get PDF document metadata.
        
        Returns:
            Dictionary with metadata
        """
        if not self.document:
            return {}
        
        try:
            metadata = self.document.metadata
            return {
                'title': metadata.get('title', 'Unknown'),
                'author': metadata.get('author', 'Unknown'),
                'subject': metadata.get('subject', ''),
                'keywords': metadata.get('keywords', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'mod_date': metadata.get('modDate', ''),
                'page_count': len(self.document)
            }
        except:
            return {'page_count': len(self.document) if self.document else 0}
