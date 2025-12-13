"""
Simple PDF Handler - Text Search Worker Thread

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

from typing import List
from PyQt6.QtCore import QThread, pyqtSignal, QRectF
from backend.pymupdf_backend import PyMuPDFBackend


class TextSearchWorker(QThread):
    """
    Background thread worker for searching text across PDF pages.
    Prevents UI freezing during search operations on large documents.
    
    This class implements the Interface Segregation Principle by providing
    only search-related signals and methods, keeping the interface focused.
    """
    
    # Signals for communicating with the main thread
    # Reports progress as (current_page, total_pages)
    search_progress = pyqtSignal(int, int)
    
    # Emits when matches are found on a page: (page_number, list_of_match_rects)
    match_found = pyqtSignal(int, list)
    
    # Emits when search completes: (total_matches_found)
    search_completed = pyqtSignal(int)
    
    # Emits when search fails with error message
    search_failed = pyqtSignal(str)
    
    # Emits when search is cancelled by user
    search_cancelled = pyqtSignal()
    
    def __init__(
        self,
        backend: PyMuPDFBackend,
        search_text: str,
        current_page: int,
        case_sensitive: bool = False
    ):
        """
        Initialize the text search worker.
        
        Args:
            backend: PyMuPDFBackend instance to search within
            search_text: Text to search for
            current_page: Current page number to start search from
            case_sensitive: Whether to perform case-sensitive search
        """
        super().__init__()
        
        self._backend = backend
        self._search_text = search_text
        self._current_page = current_page
        self._case_sensitive = case_sensitive
        
        # Flag to support cancellation of long-running searches
        self._cancelled = False
        
        # Track total matches found
        self._total_matches = 0
    
    def run(self) -> None:
        """
        Execute the text search operation in the background thread.
        Searches all pages and emits results incrementally.
        """
        try:
            # Validate inputs
            if not self._backend or not self._backend.is_loaded():
                self.search_failed.emit("No document loaded")
                return
            
            if not self._search_text or not self._search_text.strip():
                self.search_failed.emit("Search text is empty")
                return
            
            page_count = self._backend.get_page_count()
            
            # Search strategy: prioritize current and nearby pages first
            # This provides faster time-to-first-result for user
            search_order = self._calculate_search_order(page_count)
            
            # Search each page in the calculated order
            for index, page_number in enumerate(search_order):
                # Check if search was cancelled
                if self._cancelled:
                    self.search_cancelled.emit()
                    return
                
                # Emit progress update (1-indexed for display)
                self.search_progress.emit(index + 1, page_count)
                
                # Perform search on this page
                matches = self._backend.search_text_in_page(
                    page_number,
                    self._search_text,
                    self._case_sensitive
                )
                
                # If matches found, emit them immediately
                if matches:
                    self._total_matches += len(matches)
                    self.match_found.emit(page_number, matches)
            
            # Search completed successfully
            self.search_completed.emit(self._total_matches)
            
        except Exception as e:
            # Handle any unexpected errors during search
            error_message = f"Search error: {str(e)}"
            self.search_failed.emit(error_message)
    
    def _calculate_search_order(self, page_count: int) -> List[int]:
        """
        Calculate the order in which to search pages.
        Prioritizes current page and nearby pages for faster results.
        
        Args:
            page_count: Total number of pages in document
            
        Returns:
            List of page numbers in search order (0-indexed)
        """
        if page_count == 0:
            return []
        
        # Start with current page
        search_order = [self._current_page]
        
        # Add pages in expanding rings around current page
        # e.g., if current is 5: [5, 6, 4, 7, 3, 8, 2, ...]
        distance = 1
        while len(search_order) < page_count:
            # Try page after current
            next_page = self._current_page + distance
            if next_page < page_count:
                search_order.append(next_page)
            
            # Try page before current
            prev_page = self._current_page - distance
            if prev_page >= 0:
                search_order.append(prev_page)
            
            distance += 1
        
        return search_order
    
    def cancel(self) -> None:
        """
        Request cancellation of the search operation.
        The search will stop at the next page boundary.
        """
        self._cancelled = True
