"""
Simple PDF Handler - Search Results Manager

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

from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QRectF


class SearchResultsManager:
    """
    Manages search results across all pages in a document.
    Provides navigation between matches and tracks current selection.
    
    This class follows the Single Responsibility Principle by handling
    only search result storage and navigation logic.
    """
    
    def __init__(self):
        """Initialize the search results manager."""
        # Dictionary mapping page numbers to lists of match rectangles
        self._results: Dict[int, List[QRectF]] = {}
        
        # Flat list of (page_number, rect_index) tuples for navigation
        self._match_sequence: List[Tuple[int, int]] = []
        
        # Index of currently selected match in _match_sequence
        self._current_match_index: int = -1
        
        # Total number of matches across all pages
        self._total_matches: int = 0
    
    def clear(self) -> None:
        """Clear all search results and reset state."""
        self._results.clear()
        self._match_sequence.clear()
        self._current_match_index = -1
        self._total_matches = 0
    
    def add_page_results(self, page_number: int, matches: List[QRectF]) -> None:
        """
        Add search results for a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            matches: List of QRectF objects representing match locations
        """
        if not matches:
            return
        
        # Store results for this page
        self._results[page_number] = matches
        
        # Add each match to the navigation sequence
        for rect_index in range(len(matches)):
            self._match_sequence.append((page_number, rect_index))
        
        # Update total count
        self._total_matches = len(self._match_sequence)
        
        # If this is the first match found, set it as current
        if self._current_match_index == -1 and self._total_matches > 0:
            self._current_match_index = 0
    
    def get_page_results(self, page_number: int) -> List[QRectF]:
        """
        Get all search results for a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of match rectangles for the page, or empty list if no matches
        """
        return self._results.get(page_number, [])
    
    def has_results(self) -> bool:
        """
        Check if any search results exist.
        
        Returns:
            True if there are search results, False otherwise
        """
        return self._total_matches > 0
    
    def get_total_matches(self) -> int:
        """
        Get the total number of matches across all pages.
        
        Returns:
            Total match count
        """
        return self._total_matches
    
    def get_current_match_info(self) -> Optional[Tuple[int, QRectF, int]]:
        """
        Get information about the currently selected match.
        
        Returns:
            Tuple of (page_number, rect, match_number) where match_number is 1-indexed,
            or None if no match is selected
        """
        if not self.has_results() or self._current_match_index < 0:
            return None
        
        page_number, rect_index = self._match_sequence[self._current_match_index]
        rect = self._results[page_number][rect_index]
        
        # Match number is 1-indexed for display
        match_number = self._current_match_index + 1
        
        return (page_number, rect, match_number)
    
    def go_to_next_match(self) -> Optional[Tuple[int, QRectF, int]]:
        """
        Navigate to the next search match.
        Wraps around to first match if at the end.
        
        Returns:
            Tuple of (page_number, rect, match_number) for the next match,
            or None if no matches exist
        """
        if not self.has_results():
            return None
        
        # Move to next match (wrap around if at end)
        self._current_match_index = (self._current_match_index + 1) % self._total_matches
        
        return self.get_current_match_info()
    
    def go_to_previous_match(self) -> Optional[Tuple[int, QRectF, int]]:
        """
        Navigate to the previous search match.
        Wraps around to last match if at the beginning.
        
        Returns:
            Tuple of (page_number, rect, match_number) for the previous match,
            or None if no matches exist
        """
        if not self.has_results():
            return None
        
        # Move to previous match (wrap around if at beginning)
        self._current_match_index = (self._current_match_index - 1) % self._total_matches
        
        return self.get_current_match_info()
    
    def go_to_first_match(self) -> Optional[Tuple[int, QRectF, int]]:
        """
        Navigate to the first search match.
        
        Returns:
            Tuple of (page_number, rect, match_number) for the first match,
            or None if no matches exist
        """
        if not self.has_results():
            return None
        
        self._current_match_index = 0
        return self.get_current_match_info()
    
    def go_to_last_match(self) -> Optional[Tuple[int, QRectF, int]]:
        """
        Navigate to the last search match.
        
        Returns:
            Tuple of (page_number, rect, match_number) for the last match,
            or None if no matches exist
        """
        if not self.has_results():
            return None
        
        self._current_match_index = self._total_matches - 1
        return self.get_current_match_info()
    
    def get_pages_with_matches(self) -> List[int]:
        """
        Get a list of all page numbers that have search matches.
        
        Returns:
            Sorted list of page numbers (0-indexed)
        """
        return sorted(self._results.keys())
