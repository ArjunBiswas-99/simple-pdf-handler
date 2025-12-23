"""
PDF Document handler using PyMuPDF.

Manages PDF file operations, rendering, and caching.
"""

import fitz  # PyMuPDF
from typing import Optional, Dict, Tuple
from pathlib import Path
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, Signal


class PDFDocument(QObject):
    """
    PDF document handler.
    
    Manages PDF file loading, rendering, and basic operations.
    Uses LRU cache for rendered pages to optimize memory usage.
    """
    
    # Signals
    document_loaded = Signal()
    document_closed = Signal()
    page_rendered = Signal(int)  # page_number
    error_occurred = Signal(str)  # error_message
    
    def __init__(self):
        """Initialize PDF document handler."""
        super().__init__()
        
        self._doc: Optional[fitz.Document] = None
        self._file_path: Optional[str] = None
        self._page_count: int = 0
        self._current_page: int = 0
        self._zoom_level: float = 100.0  # percentage
        self._rotation_angles: Dict[int, int] = {}  # page_num: angle
        self._page_cache: Dict[Tuple[int, float, int], QPixmap] = {}  # (page, zoom, rotation): pixmap
        self._max_cache_size: int = 10  # Maximum cached pages
        
    def open(self, file_path: str) -> bool:
        """
        Open a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Close any existing document
            self.close()
            
            # Validate file exists
            if not Path(file_path).exists():
                self.error_occurred.emit(f"File not found: {file_path}")
                return False
            
            # Open PDF document
            self._doc = fitz.open(file_path)
            self._file_path = file_path
            self._page_count = len(self._doc)
            self._current_page = 0
            self._rotation_angles = {}
            self._page_cache = {}
            
            # Emit success signal
            self.document_loaded.emit()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to open PDF: {str(e)}")
            return False
    
    def close(self):
        """Close the current document."""
        if self._doc:
            self._doc.close()
            self._doc = None
            self._file_path = None
            self._page_count = 0
            self._current_page = 0
            self._rotation_angles = {}
            self._page_cache = {}
            self.document_closed.emit()
    
    def render_page(self, page_number: int, zoom: Optional[float] = None, 
                   rotation: Optional[int] = None) -> Optional[QPixmap]:
        """
        Render a specific page to QPixmap.
        
        Args:
            page_number: Page number (0-indexed)
            zoom: Zoom level as percentage (default: current zoom)
            rotation: Rotation angle in degrees (default: current rotation)
            
        Returns:
            QPixmap of rendered page, or None if error
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return None
        
        # Use current values if not specified
        if zoom is None:
            zoom = self._zoom_level
        if rotation is None:
            rotation = self._rotation_angles.get(page_number, 0)
        
        # Check cache
        cache_key = (page_number, zoom, rotation)
        if cache_key in self._page_cache:
            return self._page_cache[cache_key]
        
        try:
            # Get page
            page = self._doc[page_number]
            
            # Calculate matrix for zoom and rotation
            zoom_factor = zoom / 100.0
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Apply rotation if needed
            if rotation:
                mat = mat.prerotate(rotation)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to QImage
            img_format = QImage.Format_RGB888 if pix.n == 3 else QImage.Format_RGBA8888
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
            
            # Convert to QPixmap
            pixmap = QPixmap.fromImage(qimage)
            
            # Cache the rendered page
            self._cache_page(cache_key, pixmap)
            
            # Emit signal
            self.page_rendered.emit(page_number)
            
            return pixmap
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to render page {page_number + 1}: {str(e)}")
            return None
    
    def _cache_page(self, key: Tuple[int, float, int], pixmap: QPixmap):
        """
        Cache a rendered page with LRU policy.
        
        Args:
            key: Cache key (page_num, zoom, rotation)
            pixmap: Rendered pixmap
        """
        # If cache is full, remove oldest entry
        if len(self._page_cache) >= self._max_cache_size:
            # Remove first (oldest) item
            oldest_key = next(iter(self._page_cache))
            del self._page_cache[oldest_key]
        
        self._page_cache[key] = pixmap
    
    def clear_cache(self):
        """Clear the page cache."""
        self._page_cache = {}
    
    def get_page_size(self, page_number: int) -> Optional[Tuple[float, float]]:
        """
        Get page dimensions.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points, or None if error
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return None
        
        try:
            page = self._doc[page_number]
            rect = page.rect
            return (rect.width, rect.height)
        except Exception:
            return None
    
    def get_metadata(self) -> Dict[str, str]:
        """
        Get PDF metadata.
        
        Returns:
            Dictionary of metadata
        """
        if not self._doc:
            return {}
        
        return {
            'title': self._doc.metadata.get('title', ''),
            'author': self._doc.metadata.get('author', ''),
            'subject': self._doc.metadata.get('subject', ''),
            'keywords': self._doc.metadata.get('keywords', ''),
            'creator': self._doc.metadata.get('creator', ''),
            'producer': self._doc.metadata.get('producer', ''),
            'created': self._doc.metadata.get('creationDate', ''),
            'modified': self._doc.metadata.get('modDate', ''),
        }
    
    # Properties
    @property
    def is_open(self) -> bool:
        """Check if document is open."""
        return self._doc is not None
    
    @property
    def file_path(self) -> Optional[str]:
        """Get current file path."""
        return self._file_path
    
    @property
    def page_count(self) -> int:
        """Get total page count."""
        return self._page_count
    
    @property
    def current_page(self) -> int:
        """Get current page number (0-indexed)."""
        return self._current_page
    
    @current_page.setter
    def current_page(self, page_num: int):
        """Set current page number."""
        if 0 <= page_num < self._page_count:
            self._current_page = page_num
    
    @property
    def zoom_level(self) -> float:
        """Get current zoom level."""
        return self._zoom_level
    
    @zoom_level.setter
    def zoom_level(self, zoom: float):
        """Set zoom level."""
        self._zoom_level = max(25.0, min(400.0, zoom))  # Clamp between 25% and 400%
        self.clear_cache()  # Clear cache when zoom changes
    
    def rotate_page(self, page_number: int, angle: int):
        """
        Set rotation for a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            angle: Rotation angle in degrees (0, 90, 180, 270)
        """
        if 0 <= page_number < self._page_count:
            # Normalize angle to 0-360 range
            angle = angle % 360
            self._rotation_angles[page_number] = angle
            
            # Clear cache for this page
            keys_to_remove = [k for k in self._page_cache.keys() if k[0] == page_number]
            for key in keys_to_remove:
                del self._page_cache[key]
    
    def get_page_rotation(self, page_number: int) -> int:
        """
        Get rotation angle for a page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Rotation angle in degrees
        """
        return self._rotation_angles.get(page_number, 0)
    
    def get_text_in_rect(self, page_number: int, rect: Tuple[float, float, float, float]) -> str:
        """
        Extract text within a rectangle on a page.
        
        Args:
            page_number: Page number (0-indexed)
            rect: Tuple of (x0, y0, x1, y1) in PDF coordinates
            
        Returns:
            Extracted text as string
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return ""
        
        try:
            page = self._doc[page_number]
            
            # Get all words with their bounding boxes
            words = page.get_text("words")  # Returns: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
            
            # Find words that intersect with selection rectangle
            x0, y0, x1, y1 = rect
            selected_words = []
            
            for word_info in words:
                wx0, wy0, wx1, wy1 = word_info[:4]
                word_text = word_info[4]
                
                # Check if word intersects with selection rectangle
                if not (wx1 < x0 or wx0 > x1 or wy1 < y0 or wy0 > y1):
                    # Store word with its position for sorting
                    selected_words.append((wy0, wx0, word_text, word_info[6]))  # y, x, text, line_no
            
            # Sort by line number, then by x position
            selected_words.sort(key=lambda w: (w[3], w[0], w[1]))
            
            # Group words by line and join with spaces
            if not selected_words:
                return ""
            
            lines = []
            current_line = []
            current_line_no = selected_words[0][3]
            
            for _, _, text, line_no in selected_words:
                if line_no != current_line_no:
                    # New line
                    lines.append(" ".join(current_line))
                    current_line = [text]
                    current_line_no = line_no
                else:
                    current_line.append(text)
            
            # Add last line
            if current_line:
                lines.append(" ".join(current_line))
            
            return "\n".join(lines)
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to extract text: {str(e)}")
            return ""
    
    def get_word_boxes_in_rect(self, page_number: int, rect: Tuple[float, float, float, float]) -> list:
        """
        Get bounding boxes of words within a rectangle on a page.
        
        Args:
            page_number: Page number (0-indexed)
            rect: Tuple of (x0, y0, x1, y1) in PDF coordinates
            
        Returns:
            List of tuples: [(x0, y0, x1, y1, "word"), ...]
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return []
        
        try:
            page = self._doc[page_number]
            
            # Get all words with their bounding boxes
            words = page.get_text("words")
            
            # Find words that intersect with selection rectangle
            x0, y0, x1, y1 = rect
            word_boxes = []
            
            for word_info in words:
                wx0, wy0, wx1, wy1 = word_info[:4]
                word_text = word_info[4]
                
                # Check if word intersects with selection rectangle
                if not (wx1 < x0 or wx0 > x1 or wy1 < y0 or wy0 > y1):
                    word_boxes.append((wx0, wy0, wx1, wy1, word_text))
            
            return word_boxes
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to get word boxes: {str(e)}")
            return []
    
    def get_images_on_page(self, page_number: int) -> list:
        """
        Get bounding boxes of images on a page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of tuples: [(x0, y0, x1, y1, xref, width, height), ...]
            where xref is the image reference number
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return []
        
        try:
            page = self._doc[page_number]
            
            # Get all images on the page
            image_list = page.get_images()
            image_info = []
            
            for img in image_list:
                xref = img[0]  # Image reference number
                
                # Get image bounding box
                try:
                    # Get all image instances on the page
                    img_instances = page.get_image_rects(xref)
                    
                    for rect in img_instances:
                        # rect is a fitz.Rect object
                        x0, y0, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
                        
                        # Get image dimensions
                        pix = fitz.Pixmap(self._doc, xref)
                        width = pix.width
                        height = pix.height
                        pix = None  # Free memory
                        
                        image_info.append((x0, y0, x1, y1, xref, width, height))
                except:
                    continue
            
            return image_info
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to get images: {str(e)}")
            return []
    
    def get_image_data(self, page_number: int, xref: int) -> Optional[QPixmap]:
        """
        Extract image data from PDF.
        
        Args:
            page_number: Page number (0-indexed)
            xref: Image reference number
            
        Returns:
            QPixmap of the image, or None if error
        """
        if not self._doc or page_number < 0 or page_number >= self._page_count:
            return None
        
        try:
            # Extract image
            pix = fitz.Pixmap(self._doc, xref)
            
            # Convert to RGB if needed (remove alpha channel)
            if pix.alpha:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            
            # Convert to QImage
            img_format = QImage.Format_RGB888
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
            
            # Convert to QPixmap
            pixmap = QPixmap.fromImage(qimage.copy())  # Copy to detach from pixmap data
            
            pix = None  # Free memory
            
            return pixmap
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to extract image: {str(e)}")
            return None
