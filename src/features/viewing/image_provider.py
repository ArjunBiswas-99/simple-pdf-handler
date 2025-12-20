"""
Simple PDF Handler - PDF Image Provider

Provides rendered PDF pages to QML as images.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QSize
from typing import Optional


class PDFImageProvider(QQuickImageProvider):
    """
    Image provider that serves rendered PDF pages to QML.
    """
    
    def __init__(self):
        """Initialize image provider."""
        super().__init__(QQuickImageProvider.Image)
        self._current_image: Optional[QImage] = None
    
    def requestImage(self, id: str, size: QSize, requestedSize: QSize) -> QImage:
        """
        Request image by ID.
        
        Args:
            id: Image identifier (not used, always returns current page)
            size: Output parameter for actual size
            requestedSize: Requested size (not used)
            
        Returns:
            QImage of current page
        """
        if self._current_image and not self._current_image.isNull():
            if size:
                size.setWidth(self._current_image.width())
                size.setHeight(self._current_image.height())
            # Return a copy to avoid threading issues
            return self._current_image.copy()
        
        # Return empty image if no PDF loaded
        empty = QImage(800, 600, QImage.Format_RGB888)
        empty.fill(0xF5F5F5)  # Light gray
        return empty
    
    def set_image(self, image: QImage) -> None:
        """
        Set the current image to serve.
        
        Args:
            image: QImage to serve
        """
        self._current_image = image
