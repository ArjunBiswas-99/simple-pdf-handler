"""
Simple PDF Handler - Thumbnail Render Worker

Background thread for rendering page thumbnails.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap


class ThumbnailRenderWorker(QThread):
    """
    Background worker for rendering page thumbnails.
    Renders in batches to avoid UI freeze.
    """
    
    # Signals
    thumbnail_ready = pyqtSignal(int, QPixmap)  # page_number, pixmap
    progress_updated = pyqtSignal(int, int)  # current_page, total_pages
    rendering_completed = pyqtSignal(int)  # total_rendered
    rendering_failed = pyqtSignal(str)  # error_message
    
    def __init__(self, backend, page_count: int, thumbnail_scale: float = 0.25):
        """
        Initialize the thumbnail render worker.
        
        Args:
            backend: PyMuPDFBackend instance
            page_count: Total number of pages to render
            thumbnail_scale: Scale factor for thumbnails (0.25 = 25% of original size)
        """
        super().__init__()
        self._backend = backend
        self._page_count = page_count
        self._thumbnail_scale = thumbnail_scale
        self._cancelled = False
        self._batch_size = 10  # Render 10 pages at a time
    
    def cancel(self):
        """Cancel the rendering operation."""
        self._cancelled = True
    
    def run(self):
        """Run the thumbnail rendering in background."""
        try:
            rendered_count = 0
            
            # Render pages in batches
            for batch_start in range(0, self._page_count, self._batch_size):
                if self._cancelled:
                    break
                
                # Calculate batch end
                batch_end = min(batch_start + self._batch_size, self._page_count)
                
                # Render pages in this batch
                for page_num in range(batch_start, batch_end):
                    if self._cancelled:
                        break
                    
                    # Render thumbnail at reduced scale
                    pixmap = self._backend.render_page(page_num, self._thumbnail_scale)
                    
                    if pixmap and not pixmap.isNull():
                        # Emit thumbnail ready signal
                        self.thumbnail_ready.emit(page_num, pixmap)
                        rendered_count += 1
                        
                        # Update progress
                        self.progress_updated.emit(page_num + 1, self._page_count)
                    else:
                        # Failed to render this page, but continue with others
                        pass
                
                # Small pause between batches to keep UI responsive
                self.msleep(10)
            
            # Emit completion signal
            if not self._cancelled:
                self.rendering_completed.emit(rendered_count)
        
        except Exception as e:
            self.rendering_failed.emit(str(e))
