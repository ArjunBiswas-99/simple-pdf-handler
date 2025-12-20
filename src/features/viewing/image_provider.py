"""
Simple PDF Handler - PDF Image Provider

Provides rendered PDF pages to QML as images with caching.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QSize
from typing import Optional, Dict
from collections import OrderedDict


class PDFImageProvider(QQuickImageProvider):
    """
    Image provider that serves rendered PDF pages to QML with LRU caching.
    Supports multiple pages for Two Page and Continuous Scroll modes.
    """
    
    def __init__(self, max_cache_size: int = 50):
        """
        Initialize image provider with page cache.
        
        Args:
            max_cache_size: Maximum number of pages to keep in cache (default 50 for scroll mode)
        """
        super().__init__(QQuickImageProvider.Image)
        self._page_cache: OrderedDict[int, QImage] = OrderedDict()
        self._max_cache_size = max_cache_size
    
    def requestImage(self, id: str, size: QSize, requestedSize: QSize) -> QImage:
        """
        Request image by page number from ID.
        
        Args:
            id: Image identifier (e.g., "page_5" for page 5)
            size: Output parameter for actual size
            requestedSize: Requested size (not used)
            
        Returns:
            QImage of requested page or placeholder
        """
        # Parse page number from ID (format: "page_5?counter=X")
        try:
            # Remove query string if present
            clean_id = id.split('?')[0] if '?' in id else id
            page_num = int(clean_id.split('_')[1]) if '_' in clean_id else 1
        except (IndexError, ValueError):
            page_num = 1
        
        # Check if page is in cache
        if page_num in self._page_cache:
            image = self._page_cache[page_num]
            # Move to end (mark as recently used)
            self._page_cache.move_to_end(page_num)
            
            if size:
                size.setWidth(image.width())
                size.setHeight(image.height())
            return image.copy()
        
        # Return placeholder if page not cached
        empty = QImage(800, 600, QImage.Format_RGB888)
        empty.fill(0xF5F5F5)  # Light gray
        return empty
    
    def set_page_image(self, page_num: int, image: QImage) -> None:
        """
        Cache a rendered page image.
        
        Args:
            page_num: Page number (1-indexed)
            image: QImage of the page
        """
        if image and not image.isNull():
            # Add to cache
            self._page_cache[page_num] = image
            
            # Enforce cache size limit (LRU eviction)
            while len(self._page_cache) > self._max_cache_size:
                # Remove oldest (first) item
                self._page_cache.popitem(last=False)
    
    def get_page_image(self, page_num: int) -> Optional[QImage]:
        """
        Get a cached page image.
        
        Args:
            page_num: Page number (1-indexed)
            
        Returns:
            QImage if cached, None otherwise
        """
        if page_num in self._page_cache:
            # Move to end (mark as recently used)
            self._page_cache.move_to_end(page_num)
            return self._page_cache[page_num]
        return None
    
    def clear_cache(self) -> None:
        """Clear all cached pages."""
        self._page_cache.clear()
    
    def has_page(self, page_num: int) -> bool:
        """Check if a page is cached."""
        return page_num in self._page_cache
