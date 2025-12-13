"""
Simple PDF Handler - Text Selection Manager

Manages text selection state and extraction logic for PDF documents.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from typing import Optional, List, Tuple
from PyQt6.QtCore import QPointF, QRectF


class TextSelectionManager:
    """
    Manages text selection state and provides methods for text extraction.
    
    This class follows the Single Responsibility Principle by only handling
    selection state and text extraction logic.
    """
    
    def __init__(self):
        """Initialize the text selection manager."""
        self._is_selecting = False
        self._selection_start: Optional[QPointF] = None
        self._selection_end: Optional[QPointF] = None
        self._selection_page: Optional[int] = None
        self._selection_rect: Optional[QRectF] = None
        self._selected_text: str = ""
    
    def start_selection(self, point: QPointF, page_number: int) -> None:
        """
        Start a new text selection.
        
        Args:
            point: Starting point of selection in PDF coordinates
            page_number: Page number where selection starts (0-indexed)
        """
        self._is_selecting = True
        self._selection_start = point
        self._selection_end = point
        self._selection_page = page_number
        self._update_selection_rect()
    
    def update_selection(self, point: QPointF) -> None:
        """
        Update the current selection endpoint.
        
        Args:
            point: Current point in PDF coordinates
        """
        if not self._is_selecting:
            return
        
        self._selection_end = point
        self._update_selection_rect()
    
    def end_selection(self) -> None:
        """Finalize the current selection."""
        self._is_selecting = False
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._is_selecting = False
        self._selection_start = None
        self._selection_end = None
        self._selection_page = None
        self._selection_rect = None
        self._selected_text = ""
    
    def has_selection(self) -> bool:
        """
        Check if there is an active selection.
        
        Returns:
            True if selection exists, False otherwise
        """
        return self._selection_rect is not None and not self._selection_rect.isEmpty()
    
    def is_selecting(self) -> bool:
        """
        Check if selection is currently in progress.
        
        Returns:
            True if actively selecting, False otherwise
        """
        return self._is_selecting
    
    def get_selection_rect(self) -> Optional[QRectF]:
        """
        Get the current selection rectangle in PDF coordinates.
        
        Returns:
            QRectF representing selection area, or None if no selection
        """
        return self._selection_rect
    
    def get_selection_page(self) -> Optional[int]:
        """
        Get the page number of the current selection.
        
        Returns:
            Page number (0-indexed), or None if no selection
        """
        return self._selection_page
    
    def _update_selection_rect(self) -> None:
        """Update the selection rectangle based on start and end points."""
        if not self._selection_start or not self._selection_end:
            self._selection_rect = None
            return
        
        # Calculate rectangle from two points
        x1 = min(self._selection_start.x(), self._selection_end.x())
        y1 = min(self._selection_start.y(), self._selection_end.y())
        x2 = max(self._selection_start.x(), self._selection_end.x())
        y2 = max(self._selection_start.y(), self._selection_end.y())
        
        self._selection_rect = QRectF(x1, y1, x2 - x1, y2 - y1)
    
    def extract_text_from_words(
        self, 
        words: List[Tuple[float, float, float, float, str]]
    ) -> str:
        """
        Extract text from words that intersect with the selection rectangle.
        
        Args:
            words: List of (x0, y0, x1, y1, word_text) tuples
            
        Returns:
            Extracted text as string with words in reading order
        """
        if not self._selection_rect or not words:
            return ""
        
        # Find words that intersect with selection
        selected_words = []
        for x0, y0, x1, y1, text in words:
            word_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
            if self._selection_rect.intersects(word_rect):
                selected_words.append((x0, y0, x1, y1, text))
        
        if not selected_words:
            return ""
        
        # Sort words by position (top-to-bottom, left-to-right)
        selected_words.sort(key=lambda w: (w[1], w[0]))  # Sort by y0, then x0
        
        # Combine words into text with appropriate spacing
        text_parts = []
        prev_y = None
        prev_x = None
        
        for x0, y0, x1, y1, word in selected_words:
            # If we're on a new line (y coordinate changed significantly)
            if prev_y is not None and abs(y0 - prev_y) > 5:  # 5 points threshold
                text_parts.append('\n')
            # If same line but gap between words
            elif prev_x is not None and prev_y is not None:
                # Check if there's a gap between words
                if x0 - prev_x > 5:  # 5 points threshold for word spacing
                    text_parts.append(' ')
            
            text_parts.append(word)
            prev_y = y0
            prev_x = x1
        
        self._selected_text = ''.join(text_parts)
        return self._selected_text
    
    def extract_text_from_blocks(
        self, 
        blocks: List[Tuple[float, float, float, float, str]]
    ) -> str:
        """
        Extract text from blocks that intersect with the selection rectangle.
        
        Args:
            blocks: List of (x0, y0, x1, y1, block_text) tuples
            
        Returns:
            Extracted text as string with blocks in reading order
        """
        if not self._selection_rect or not blocks:
            return ""
        
        # Find blocks that intersect with selection
        selected_blocks = []
        for x0, y0, x1, y1, text in blocks:
            block_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
            if self._selection_rect.intersects(block_rect):
                selected_blocks.append((y0, x0, text))  # Store with coordinates for sorting
        
        if not selected_blocks:
            return ""
        
        # Sort blocks by position (top-to-bottom, left-to-right)
        selected_blocks.sort(key=lambda b: (b[0], b[1]))
        
        # Combine block texts
        text_parts = [block[2] for block in selected_blocks]
        self._selected_text = '\n'.join(text_parts)
        return self._selected_text
    
    def get_selected_text(self) -> str:
        """
        Get the currently selected text.
        
        Returns:
            Selected text string, or empty string if no selection
        """
        return self._selected_text
    
    def set_selected_text(self, text: str) -> None:
        """
        Manually set the selected text (used after extraction).
        
        Args:
            text: Text to set as selected
        """
        self._selected_text = text
