"""
Simple PDF Handler - Viewing Controller

F1: Controls PDF viewing and navigation operations.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional
from PySide6.QtCore import Signal, Slot, Property
from src.core.base_controller import BaseController
from .model import ViewingModel


class ViewingController(BaseController):
    """
    Controls PDF viewing and navigation operations.
    
    Manages document loading, page navigation, zoom controls,
    and text search functionality. Provides mock implementation
    for UI development.
    
    Signals:
        document_loaded: Emitted when document loads (str: file_path)
        page_changed: Emitted when page changes (int: page_number)
        zoom_changed: Emitted when zoom changes (float: zoom_level)
        search_completed: Emitted when search completes (int: result_count)
    """
    
    document_loaded = Signal(str)
    page_changed = Signal(int)
    zoom_changed = Signal(float)
    search_completed = Signal(int)
    
    def __init__(self):
        """Initializes viewing controller with model."""
        super().__init__()
        self._model = ViewingModel()
    
    @Slot(str, result=bool)
    def open_document(self, file_path: str) -> bool:
        """
        Opens PDF document from file path.
        
        Args:
            file_path: Absolute path to PDF file
            
        Returns:
            True if document loaded successfully
        """
        self.emit_start_operation("Opening document...")
        
        success = self._model.load_document(file_path)
        
        if success:
            self.document_loaded.emit(file_path)
            self.page_changed.emit(1)
            self.zoom_changed.emit(100.0)
            self.emit_complete_operation("Document loaded successfully")
        else:
            self.emit_error("Failed to load document")
        
        return success
    
    @Slot(int)
    def goto_page(self, page_number: int) -> None:
        """
        Navigates to specified page number.
        
        Args:
            page_number: Target page number (1-based)
        """
        if self._model.set_current_page(page_number):
            self.page_changed.emit(page_number)
    
    @Slot()
    def goto_first_page(self) -> None:
        """Navigates to first page of document."""
        self.goto_page(1)
    
    @Slot()
    def goto_last_page(self) -> None:
        """Navigates to last page of document."""
        self.goto_page(self._model.total_pages)
    
    @Slot()
    def goto_next_page(self) -> None:
        """Navigates to next page if available."""
        current = self._model.current_page
        if current < self._model.total_pages:
            self.goto_page(current + 1)
    
    @Slot()
    def goto_previous_page(self) -> None:
        """Navigates to previous page if available."""
        current = self._model.current_page
        if current > 1:
            self.goto_page(current - 1)
    
    @Slot(float)
    def set_zoom(self, zoom_level: float) -> None:
        """
        Sets zoom level for document display.
        
        Args:
            zoom_level: Zoom percentage (50-200)
        """
        if self._model.set_zoom_level(zoom_level):
            self.zoom_changed.emit(zoom_level)
    
    @Slot()
    def zoom_in(self) -> None:
        """Increases zoom by 25%."""
        current = self._model.zoom_level
        self.set_zoom(min(200, current + 25))
    
    @Slot()
    def zoom_out(self) -> None:
        """Decreases zoom by 25%."""
        current = self._model.zoom_level
        self.set_zoom(max(50, current - 25))
    
    @Slot(str)
    def search_text(self, query: str) -> None:
        """
        Searches for text in document.
        
        Args:
            query: Search query text
        """
        result_count = self._model.search_text(query)
        self.search_completed.emit(result_count)
        
        if result_count > 0:
            # Navigate to first result
            first_result = self._model.next_search_result()
            if first_result:
                self.goto_page(first_result)
    
    @Slot()
    def next_search_result(self) -> None:
        """Navigates to next search result."""
        next_page = self._model.next_search_result()
        if next_page:
            self.goto_page(next_page)
    
    @Slot()
    def previous_search_result(self) -> None:
        """Navigates to previous search result."""
        prev_page = self._model.previous_search_result()
        if prev_page:
            self.goto_page(prev_page)
    
    @Property(int, notify=page_changed)
    def current_page(self) -> int:
        """Returns current page number."""
        return self._model.current_page
    
    @Property(int, notify=document_loaded)
    def total_pages(self) -> int:
        """Returns total page count."""
        return self._model.total_pages
    
    @Property(float, notify=zoom_changed)
    def zoom_level(self) -> float:
        """Returns current zoom percentage."""
        return self._model.zoom_level
    
    @Property(bool, notify=document_loaded)
    def has_document(self) -> bool:
        """Returns whether a document is loaded."""
        return self._model.has_document
    
    @Property(int, notify=search_completed)
    def search_results_count(self) -> int:
        """Returns number of search results."""
        return self._model.search_results_count
