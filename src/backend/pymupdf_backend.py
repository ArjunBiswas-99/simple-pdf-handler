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
    
    def get_metadata(self) -> dict:
        """
        Extract PDF metadata (title, author, subject, etc.).
        
        Returns:
            Dictionary containing metadata fields, or empty dict if no document loaded
        """
        if not self._document:
            return {}
        
        try:
            # PyMuPDF provides metadata as a dictionary
            metadata = self._document.metadata
            
            # Return cleaned metadata (remove None values, strip whitespace)
            result = {}
            for key, value in metadata.items():
                if value and isinstance(value, str):
                    cleaned = value.strip()
                    if cleaned:
                        result[key] = cleaned
            
            return result
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {}
    
    def get_bookmarks(self) -> List[Tuple[int, str, int]]:
        """
        Extract bookmarks/outline (table of contents) from PDF.
        
        Returns:
            List of (level, title, page_number) tuples where:
            - level: Indentation level (1 for top level, 2 for nested, etc.)
            - title: Bookmark title text
            - page_number: Target page number (0-indexed)
            Returns empty list if no bookmarks or document not loaded
        """
        if not self._document:
            return []
        
        try:
            # Get table of contents from PyMuPDF
            # Returns list of [level, title, page_num, ...] lists
            toc = self._document.get_toc()
            
            if not toc:
                return []
            
            # Convert to simpler tuple format
            bookmarks = []
            for item in toc:
                if len(item) >= 3:
                    level = item[0]
                    title = item[1]
                    page_num = item[2] - 1  # Convert from 1-indexed to 0-indexed
                    
                    # Validate page number
                    if 0 <= page_num < self._document.page_count:
                        bookmarks.append((level, title, page_num))
            
            return bookmarks
            
        except Exception as e:
            print(f"Error extracting bookmarks: {e}")
            return []
    
    def get_attachments(self) -> List[dict]:
        """
        Get list of file attachments embedded in PDF.
        
        Returns:
            List of attachment info dictionaries (future implementation)
            Empty list for now (stub for future feature)
        """
        # Stub for future implementation
        # Will return list of dicts with keys: name, size, type, data
        return []
    
    def get_page_images(self, page_number: int) -> List[dict]:
        """
        Extract all images from a page with their bounding rectangles.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of dicts with keys:
            - 'rect': QRectF - image bounding box in PDF coordinates
            - 'xref': int - image reference number in PDF
            - 'width': int - image width in pixels
            - 'height': int - image height in pixels
            - 'colorspace': str - color space (e.g., 'DeviceRGB')
            Empty list if no images found or page doesn't exist
        """
        if not self._document:
            return []
        
        if page_number < 0 or page_number >= self._document.page_count:
            return []
        
        try:
            page = self._document[page_number]
            
            # Get list of images on the page
            # Returns list of tuples: (xref, smask, width, height, bpp, colorspace, alt. colorspace, name, filter, referencer)
            image_list = page.get_images(full=True)
            
            if not image_list:
                return []
            
            # Extract image info with bounding rectangles
            images = []
            for img_info in image_list:
                xref = img_info[0]  # Image reference number
                
                # Get image bounding rectangles on the page (can have multiple occurrences)
                # get_image_rects returns list of fitz.Rect objects
                rects = page.get_image_rects(xref)
                
                if rects:
                    # Get image properties
                    width = img_info[2]
                    height = img_info[3]
                    colorspace = img_info[5] if len(img_info) > 5 else "Unknown"
                    
                    # Add an entry for each occurrence of the image on the page
                    for bbox in rects:
                        # Convert fitz.Rect to QRectF
                        rect = QRectF(bbox.x0, bbox.y0, bbox.width, bbox.height)
                        
                        images.append({
                            'rect': rect,
                            'xref': xref,
                            'width': width,
                            'height': height,
                            'colorspace': colorspace
                        })
            
            return images
            
        except Exception as e:
            print(f"Error extracting images from page {page_number}: {e}")
            return []
    
    def extract_image(self, page_number: int, xref: int) -> Optional[QPixmap]:
        """
        Extract a specific image from a page by its xref reference number.
        
        Args:
            page_number: Page number (0-indexed)
            xref: Image reference number from get_page_images()
            
        Returns:
            QPixmap of the extracted image at original resolution,
            or None if extraction fails
        """
        if not self._document:
            return None
        
        if page_number < 0 or page_number >= self._document.page_count:
            return None
        
        try:
            # Extract the image pixmap using xref
            # This gets the raw image data at original resolution
            pix = fitz.Pixmap(self._document, xref)
            
            # Convert CMYK or other color spaces to RGB
            if pix.colorspace and pix.colorspace.name not in ("DeviceRGB", "DeviceGray"):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            
            # Convert to RGB if grayscale (for consistent clipboard format)
            if pix.n < 4:  # Grayscale or RGB without alpha
                # Already in correct format
                pass
            elif pix.n == 4 and pix.alpha:
                # RGBA - convert to RGB by removing alpha
                pix = fitz.Pixmap(fitz.csRGB, pix)
            
            # Determine Qt image format based on components
            if pix.n == 1:
                # Grayscale
                img_format = QImage.Format.Format_Grayscale8
            elif pix.n == 3:
                # RGB
                img_format = QImage.Format.Format_RGB888
            elif pix.n == 4:
                # RGBA
                img_format = QImage.Format.Format_RGBA8888
            else:
                print(f"Unsupported image format: {pix.n} components")
                return None
            
            # Convert to QImage
            qimage = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                img_format
            )
            
            # Convert to QPixmap
            pixmap = QPixmap.fromImage(qimage.copy())
            
            return pixmap
            
        except Exception as e:
            print(f"Error extracting image (xref={xref}) from page {page_number}: {e}")
            return None
