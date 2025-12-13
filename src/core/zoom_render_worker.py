"""
Simple PDF Handler - Zoom Render Worker

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

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from typing import List


class ZoomRenderWorker(QThread):
    """
    Background worker for rendering PDF pages at a new zoom level.
    Prevents UI freezing when re-rendering large documents.
    """
    
    # Signals for communicating with the main thread
    progress_updated = pyqtSignal(int)  # Progress percentage (0-100)
    page_rendered = pyqtSignal(int, object)  # Page index, QPixmap
    rendering_completed = pyqtSignal(list)  # List of all rendered QPixmaps
    rendering_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, backend, zoom_level: float, page_count: int):
        """
        Initialize the zoom render worker.
        
        Args:
            backend: PyMuPDFBackend instance to render from
            zoom_level: Zoom factor to render at (1.0 = 100%)
            page_count: Total number of pages to render
        """
        super().__init__()
        self._backend = backend
        self._zoom_level = zoom_level
        self._page_count = page_count
        self._cancelled = False
    
    def run(self) -> None:
        """
        Execute the rendering operation in the background thread.
        Renders all pages at the specified zoom level.
        """
        try:
            rendered_pages = []
            
            # Render each page
            for page_num in range(self._page_count):
                # Check if operation was cancelled
                if self._cancelled:
                    return
                
                # Render the page at the new zoom level
                pixmap = self._backend.render_page(page_num, self._zoom_level)
                
                if pixmap is None:
                    self.rendering_failed.emit(f"Failed to render page {page_num + 1}")
                    return
                
                # Store rendered page
                rendered_pages.append(pixmap)
                
                # Emit individual page for progressive display (optional)
                self.page_rendered.emit(page_num, pixmap)
                
                # Calculate and emit progress
                progress = int((page_num + 1) / self._page_count * 100)
                self.progress_updated.emit(progress)
            
            # All pages rendered successfully
            self.rendering_completed.emit(rendered_pages)
            
        except Exception as e:
            error_message = f"Error during zoom rendering: {str(e)}"
            self.rendering_failed.emit(error_message)
    
    def cancel(self) -> None:
        """
        Cancel the rendering operation.
        The worker will stop at the next page boundary.
        """
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """
        Check if the rendering operation was cancelled.
        
        Returns:
            True if cancelled, False otherwise
        """
        return self._cancelled
