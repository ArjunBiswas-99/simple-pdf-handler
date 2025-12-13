"""
Simple PDF Handler - PyMuPDF Backend Implementation

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

import fitz
from typing import Optional, Tuple, List
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QRectF


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
    
    def search_text_in_page(
        self, 
        page_number: int, 
        search_text: str, 
        case_sensitive: bool = False
    ) -> List[QRectF]:
        """
        Search for text in a specific page and return bounding rectangles.
        
        Args:
            page_number: Page number to search (0-indexed)
            search_text: Text to search for
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of QRectF objects representing text match locations,
            or empty list if no matches found or page doesn't exist
        """
        if not self._document:
            return []
        
        if page_number < 0 or page_number >= self._document.page_count:
            return []
        
        if not search_text:
            return []
        
        try:
            page = self._document[page_number]
            
            # PyMuPDF search flags
            # TEXT_PRESERVE_WHITESPACE: Preserve whitespace in text extraction
            # TEXT_PRESERVE_LIGATURES: Handle ligatures correctly
            flags = fitz.TEXT_PRESERVE_WHITESPACE | fitz.TEXT_PRESERVE_LIGATURES
            
            # Perform text search
            # search_for returns list of Rect objects for each match
            search_results = page.search_for(search_text, flags=flags)
            
            # If case-insensitive search needed and no results, try again
            # PyMuPDF's search_for is case-sensitive by default
            if not case_sensitive and not search_results:
                # Try lowercase version
                search_results = page.search_for(search_text.lower(), flags=flags)
                if not search_results:
                    # Try uppercase version
                    search_results = page.search_for(search_text.upper(), flags=flags)
            
            # Convert fitz.Rect objects to QRectF for Qt compatibility
            qt_rects = []
            for rect in search_results:
                # fitz.Rect has x0, y0, x1, y1 coordinates
                qrect = QRectF(rect.x0, rect.y0, rect.width, rect.height)
                qt_rects.append(qrect)
            
            return qt_rects
            
        except Exception as e:
            print(f"Error searching text on page {page_number}: {e}")
            return []
    
    def get_page_text(self, page_number: int) -> Optional[str]:
        """
        Extract all text from a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Extracted text as string, or None if extraction fails
        """
        if not self._document:
            return None
        
        if page_number < 0 or page_number >= self._document.page_count:
            return None
        
        try:
            page = self._document[page_number]
            # Extract text with preserved layout
            text = page.get_text("text")
            return text
        except Exception as e:
            print(f"Error extracting text from page {page_number}: {e}")
            return None
    
    def get_text_blocks(self, page_number: int) -> List[Tuple[float, float, float, float, str]]:
        """
        Get text blocks with their bounding coordinates from a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of tuples (x0, y0, x1, y1, text) where:
            - x0, y0: top-left corner coordinates
            - x1, y1: bottom-right corner coordinates
            - text: the text content of the block
            Returns empty list if extraction fails or no text found
        """
        if not self._document:
            return []
        
        if page_number < 0 or page_number >= self._document.page_count:
            return []
        
        try:
            page = self._document[page_number]
            # Get text blocks with coordinates
            # Format: (x0, y0, x1, y1, "text", block_no, block_type)
            # block_type: 0=text, 1=image
            blocks = page.get_text("blocks")
            
            # Filter to only text blocks and extract relevant info
            text_blocks = []
            for block in blocks:
                if len(block) >= 5:  # Ensure block has enough elements
                    x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
                    # Only include text blocks (not images)
                    if isinstance(text, str) and text.strip():
                        text_blocks.append((x0, y0, x1, y1, text.strip()))
            
            return text_blocks
            
        except Exception as e:
            print(f"Error extracting text blocks from page {page_number}: {e}")
            return []
    
    def get_text_words(self, page_number: int) -> List[Tuple[float, float, float, float, str]]:
        """
        Get individual words with their bounding coordinates from a specific page.
        Provides finer granularity than get_text_blocks for more precise selection.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of tuples (x0, y0, x1, y1, word) where:
            - x0, y0: top-left corner coordinates
            - x1, y1: bottom-right corner coordinates
            - word: the individual word
            Returns empty list if extraction fails or no text found
        """
        if not self._document:
            return []
        
        if page_number < 0 or page_number >= self._document.page_count:
            return []
        
        try:
            page = self._document[page_number]
            
            # Get words with coordinates
            # Format: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
            words = page.get_text("words")
            
            # Extract relevant info
            word_list = []
            for word in words:
                if len(word) >= 5:  # Ensure word has enough elements
                    x0, y0, x1, y1, text = word[0], word[1], word[2], word[3], word[4]
                    if text.strip():
                        word_list.append((x0, y0, x1, y1, text))
            
            return word_list
            
        except Exception as e:
            print(f"Error extracting words from page {page_number}: {e}")
            return []
