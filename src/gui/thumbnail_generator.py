"""
Thumbnail generator worker thread.

Generates page thumbnails asynchronously to prevent UI blocking.
Includes smart caching with LRU policy.
"""

from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from PySide6.QtGui import QPixmap
from typing import Dict, Tuple, Optional, List
from collections import OrderedDict


class ThumbnailCache:
    """
    LRU cache for thumbnail pixmaps.
    
    Stores thumbnails with automatic eviction of least recently used items
    when cache size limit is reached.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of thumbnails to cache
        """
        self._cache: OrderedDict[Tuple[int, int], QPixmap] = OrderedDict()
        self._max_size = max_size
        self._mutex = QMutex()
    
    def get(self, page_num: int, thumb_size: int) -> Optional[QPixmap]:
        """
        Get thumbnail from cache.
        
        Args:
            page_num: Page number (0-indexed)
            thumb_size: Thumbnail size in pixels
            
        Returns:
            Cached pixmap or None if not found
        """
        with QMutexLocker(self._mutex):
            key = (page_num, thumb_size)
            if key in self._cache:
                # Move to end (mark as recently used)
                self._cache.move_to_end(key)
                return self._cache[key]
            return None
    
    def put(self, page_num: int, thumb_size: int, pixmap: QPixmap):
        """
        Add thumbnail to cache.
        
        Args:
            page_num: Page number (0-indexed)
            thumb_size: Thumbnail size in pixels
            pixmap: Thumbnail pixmap
        """
        with QMutexLocker(self._mutex):
            key = (page_num, thumb_size)
            
            # Remove oldest if cache is full
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)  # Remove oldest (first) item
            
            # Add to cache (or update if exists)
            self._cache[key] = pixmap
            self._cache.move_to_end(key)  # Mark as most recently used
    
    def clear(self):
        """Clear all cached thumbnails."""
        with QMutexLocker(self._mutex):
            self._cache.clear()
    
    def remove_page(self, page_num: int):
        """
        Remove all cached thumbnails for a specific page.
        
        Args:
            page_num: Page number (0-indexed)
        """
        with QMutexLocker(self._mutex):
            keys_to_remove = [k for k in self._cache.keys() if k[0] == page_num]
            for key in keys_to_remove:
                del self._cache[key]


class ThumbnailGenerator(QThread):
    """
    Worker thread for generating page thumbnails asynchronously.
    
    Generates thumbnails in the background without blocking the UI thread.
    Supports cancellation and priority-based generation for visible pages.
    """
    
    # Signals
    thumbnail_ready = Signal(int, QPixmap)  # page_num, pixmap
    progress_updated = Signal(int, int)  # current, total
    generation_complete = Signal()
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, pdf_document, parent=None):
        """
        Initialize thumbnail generator.
        
        Args:
            pdf_document: PDFDocument instance
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self._pdf_document = pdf_document
        self._cache = ThumbnailCache(max_size=100)
        
        # Generation queue and control
        self._page_queue: List[int] = []
        self._thumb_size = 150
        self._is_cancelled = False
        self._mutex = QMutex()
    
    def generate_thumbnails(self, page_numbers: List[int], thumb_size: int = 150):
        """
        Request thumbnail generation for specific pages.
        
        Args:
            page_numbers: List of page numbers to generate (0-indexed)
            thumb_size: Maximum thumbnail dimension in pixels
        """
        with QMutexLocker(self._mutex):
            self._page_queue = page_numbers.copy()
            self._thumb_size = thumb_size
            self._is_cancelled = False
        
        # Start generation if not already running
        if not self.isRunning():
            self.start()
    
    def cancel(self):
        """Cancel ongoing thumbnail generation."""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
            self._page_queue.clear()
    
    def get_cached_thumbnail(self, page_num: int, thumb_size: int) -> Optional[QPixmap]:
        """
        Get thumbnail from cache without generating.
        
        Args:
            page_num: Page number (0-indexed)
            thumb_size: Thumbnail size in pixels
            
        Returns:
            Cached pixmap or None
        """
        return self._cache.get(page_num, thumb_size)
    
    def clear_cache(self):
        """Clear thumbnail cache."""
        self._cache.clear()
    
    def invalidate_page(self, page_num: int):
        """
        Invalidate cached thumbnails for a specific page.
        
        Used when page content changes (e.g., rotation, annotation).
        
        Args:
            page_num: Page number (0-indexed)
        """
        self._cache.remove_page(page_num)
    
    def run(self):
        """
        Worker thread main loop.
        
        Generates thumbnails for queued pages.
        """
        total = 0
        current = 0
        
        # Get queue snapshot
        with QMutexLocker(self._mutex):
            pages_to_generate = self._page_queue.copy()
            thumb_size = self._thumb_size
            total = len(pages_to_generate)
        
        # Generate thumbnails
        for page_num in pages_to_generate:
            # Check if cancelled
            with QMutexLocker(self._mutex):
                if self._is_cancelled:
                    break
            
            # Check cache first
            cached = self._cache.get(page_num, thumb_size)
            if cached:
                # Already cached, just emit it
                self.thumbnail_ready.emit(page_num, cached)
                current += 1
                self.progress_updated.emit(current, total)
                continue
            
            # Generate thumbnail
            try:
                pixmap = self._pdf_document.render_page_thumbnail(
                    page_num,
                    max_size=thumb_size
                )
                
                if pixmap:
                    # Cache and emit
                    self._cache.put(page_num, thumb_size, pixmap)
                    self.thumbnail_ready.emit(page_num, pixmap)
                else:
                    self.error_occurred.emit(f"Failed to generate thumbnail for page {page_num + 1}")
                
            except Exception as e:
                self.error_occurred.emit(f"Error generating thumbnail for page {page_num + 1}: {str(e)}")
            
            # Update progress
            current += 1
            self.progress_updated.emit(current, total)
        
        # Signal completion
        self.generation_complete.emit()


class PrioritizedThumbnailGenerator(ThumbnailGenerator):
    """
    Extended thumbnail generator with priority support.
    
    Generates visible pages first, then background pages.
    """
    
    def generate_thumbnails_prioritized(
        self,
        visible_pages: List[int],
        background_pages: List[int],
        thumb_size: int = 150
    ):
        """
        Generate thumbnails with priority for visible pages.
        
        Args:
            visible_pages: Pages currently visible (generated first)
            background_pages: Other pages (generated after visible)
            thumb_size: Maximum thumbnail dimension in pixels
        """
        # Combine with visible pages first
        all_pages = visible_pages + [p for p in background_pages if p not in visible_pages]
        self.generate_thumbnails(all_pages, thumb_size)
