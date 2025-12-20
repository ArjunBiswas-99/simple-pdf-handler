"""
Simple PDF Handler - Viewing Model

Data model for PDF document viewing state.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional, List


class ViewingModel:
    """
    Stores state for PDF viewing operations.
    
    Maintains current document state including page navigation,
    zoom level, and search results. Mock implementation provides
    simulated data for UI development.
    
    Attributes:
        file_path: Path to currently loaded PDF
        total_pages: Total number of pages in document
        current_page: Currently displayed page number
        zoom_level: Current zoom percentage
        search_query: Current search text
        search_results: List of page numbers containing search matches
    """
    
    def __init__(self):
        """Initializes model with default values."""
        self._file_path: Optional[str] = None
        self._total_pages: int = 0
        self._current_page: int = 1
        self._zoom_level: float = 100.0
        self._search_query: str = ""
        self._search_results: List[int] = []
        self._current_search_index: int = -1
    
    def load_document(self, file_path: str) -> bool:
        """
        Simulates loading a PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if load simulation successful
        """
        self._file_path = file_path
        self._total_pages = 10  # Mock: simulate 10 page document
        self._current_page = 1
        self._zoom_level = 100.0
        self._search_query = ""
        self._search_results = []
        return True
    
    def set_current_page(self, page_number: int) -> bool:
        """
        Updates current page if valid.
        
        Args:
            page_number: Target page number (1-based)
            
        Returns:
            True if page number is valid and updated
        """
        if 1 <= page_number <= self._total_pages:
            self._current_page = page_number
            return True
        return False
    
    def set_zoom_level(self, zoom: float) -> bool:
        """
        Updates zoom level if within valid range.
        
        Args:
            zoom: Zoom percentage (50-200)
            
        Returns:
            True if zoom is valid and updated
        """
        if 50 <= zoom <= 200:
            self._zoom_level = zoom
            return True
        return False
    
    def search_text(self, query: str) -> int:
        """
        Simulates searching for text in document.
        
        Args:
            query: Search query text
            
        Returns:
            Number of matches found
        """
        self._search_query = query
        
        if not query:
            self._search_results = []
            self._current_search_index = -1
            return 0
        
        # Mock: simulate finding results on pages 2, 5, and 8
        self._search_results = [2, 5, 8]
        self._current_search_index = 0 if self._search_results else -1
        return len(self._search_results)
    
    def next_search_result(self) -> Optional[int]:
        """
        Moves to next search result.
        
        Returns:
            Page number of next result, or None if no more results
        """
        if not self._search_results:
            return None
        
        self._current_search_index = (self._current_search_index + 1) % len(self._search_results)
        return self._search_results[self._current_search_index]
    
    def previous_search_result(self) -> Optional[int]:
        """
        Moves to previous search result.
        
        Returns:
            Page number of previous result, or None if no results
        """
        if not self._search_results:
            return None
        
        self._current_search_index = (self._current_search_index - 1) % len(self._search_results)
        return self._search_results[self._current_search_index]
    
    @property
    def file_path(self) -> Optional[str]:
        """Returns path to current document."""
        return self._file_path
    
    @property
    def current_page(self) -> int:
        """Returns current page number."""
        return self._current_page
    
    @property
    def total_pages(self) -> int:
        """Returns total page count."""
        return self._total_pages
    
    @property
    def zoom_level(self) -> float:
        """Returns current zoom percentage."""
        return self._zoom_level
    
    @property
    def search_results_count(self) -> int:
        """Returns number of search results."""
        return len(self._search_results)
    
    @property
    def has_document(self) -> bool:
        """Returns whether a document is loaded."""
        return self._file_path is not None and self._total_pages > 0
