"""
Simple PDF Handler - Viewing Controller

F1: Controls PDF viewing operations with settings persistence.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot, Property, QUrl
from PySide6.QtGui import QImage
from pathlib import Path
import fitz  # PyMuPDF
from src.core.base_controller import BaseController
from src.core.settings_manager import SettingsManager
from .model import ViewingModel
from .pdf_renderer import PDFRenderer


class ViewingController(BaseController):
    """
    Controls PDF viewing operations.
    Implements F1.1 - F1.6 with settings persistence.
    """
    
    # Signals for Property change notifications
    current_page_changed = Signal()
    page_count_changed = Signal()
    zoom_level_changed = Signal()
    document_loaded_changed = Signal()
    filename_changed = Signal()
    view_mode_changed = Signal()
    
    # Signals for events
    page_changed = Signal(int, int)  # current, total
    zoom_changed = Signal(int)
    rotation_changed = Signal(int)
    document_opened = Signal(str)  # filename
    pdf_image_updated = Signal(QImage)  # emits rendered page image
    page_rendered = Signal(int)  # emits when a specific page is rendered
    
    # Search signals (F1.5)
    search_results_changed = Signal()  # Emitted when search results change
    search_result = Signal(list)  # Emits list of (page_num, [(x0,y0,x1,y1),...])
    current_match_changed = Signal()  # Emitted when current match changes
    
    def __init__(self, settings_manager: SettingsManager):
        """
        Initialize viewing controller.
        
        Args:
            settings_manager: Application settings manager
        """
        super().__init__()
        self._model = ViewingModel()
        self._renderer = PDFRenderer()
        self._settings = settings_manager
        self._current_filepath = ""
        self._image_provider = None  # Will be set by app
        
        # Search state (F1.5)
        self._search_results = []  # List of (page_num, [(x0,y0,x1,y1),...])
        self._current_match_index = 0
        self._total_matches = 0
    
    # Properties exposed to QML
    @Property(int, notify=current_page_changed)
    def current_page(self) -> int:
        """Get current page (1-indexed)."""
        return self._model.current_page
    
    @Property(int, notify=page_count_changed)
    def page_count(self) -> int:
        """Get total page count."""
        return self._model.page_count
    
    @Property(int, notify=zoom_level_changed)
    def zoom_level(self) -> int:
        """Get current zoom level."""
        return self._model.zoom_level
    
    @Property(bool, notify=document_loaded_changed)
    def document_loaded(self) -> bool:
        """Check if document is loaded."""
        return self._model.document_loaded
    
    @Property(str, notify=filename_changed)
    def filename(self) -> str:
        """Get current filename."""
        return self._model.filename
    
    @Property(str, notify=view_mode_changed)
    def view_mode(self) -> str:
        """Get current view mode."""
        return self._model.view_mode
    
    # Search properties (F1.5)
    @Property(int, notify=search_results_changed)
    def search_match_count(self) -> int:
        """Get total number of search matches."""
        return self._total_matches
    
    @Property(int, notify=current_match_changed)
    def current_match_index(self) -> int:
        """Get current match index (1-indexed)."""
        return self._current_match_index + 1 if self._total_matches > 0 else 0
    
    @Slot(result=str)
    def get_last_directory(self) -> str:
        """Get last opened directory for file dialog."""
        return self._settings.get_last_directory()
    
    @Slot()
    def open_file(self) -> None:
        """
        F1.1: Trigger file dialog from QML.
        This is a placeholder - actual file dialog is in QML.
        """
        self.emit_start_operation("Opening file dialog...")
    
    @Slot(str)
    def load_pdf_file(self, file_url: str) -> None:
        """
        F1.1: Load PDF file from QML FileDialog.
        
        Args:
            file_url: File URL from QML (file:///path/to/file.pdf)
        """
        # Convert QML file URL to path
        if file_url.startswith('file://'):
            filepath = QUrl(file_url).toLocalFile()
            self._load_pdf(filepath)
    
    def _load_pdf(self, filepath: str) -> None:
        """
        Load PDF file and render first page.
        
        Args:
            filepath: Path to PDF file
        """
        self.emit_start_operation(f"Loading PDF: {Path(filepath).name}...")
        
        # Open PDF with renderer
        if self._renderer.open_pdf(filepath):
            self._current_filepath = filepath
            
            # Update settings
            self._settings.update_last_directory(filepath)
            self._settings.add_recent_file(filepath)
            
            # Update model and emit change signals
            self._model.set_filename(Path(filepath).name)
            self.filename_changed.emit()
            
            self._model.set_page_count(self._renderer.get_page_count())
            self.page_count_changed.emit()
            
            self._model.set_current_page(1)
            self.current_page_changed.emit()
            
            self._model.set_document_loaded(True)
            self.document_loaded_changed.emit()
            
            # Reset zoom and rotation
            self._renderer.set_zoom(100)
            self._renderer.rotation = 0
            self._model.set_zoom_level(100)
            self.zoom_level_changed.emit()
            
            self._model.set_rotation(0)
            
            # Render first page
            self._render_current_page()
            
            self.emit_complete_operation(f"Loaded: {self._model.filename}")
            self.document_opened.emit(self._model.filename)
        else:
            self.emit_error_operation(f"Failed to load PDF: {Path(filepath).name}")
    
    def set_image_provider(self, provider):
        """Set the image provider reference."""
        self._image_provider = provider
    
    def _render_current_page(self) -> None:
        """Render the current page and emit the image."""
        current_page_num = self._model.current_page
        self.render_specific_page(current_page_num)
        
        # Prefetch adjacent pages for smooth navigation
        self._prefetch_adjacent_pages()
    
    @Slot(int)
    def render_specific_page(self, page_num: int) -> None:
        """
        Render a specific page and cache it.
        
        Args:
            page_num: Page number to render (1-indexed)
        """
        if page_num < 1 or page_num > self._model.page_count:
            return
        
        # Convert to 0-indexed for renderer
        page_index = page_num - 1
        
        # Render the page - EXPLICITLY pass the page index
        image = self._renderer.render_page(page_num=page_index)
        if image and self._image_provider:
            # Cache in image provider
            self._image_provider.set_page_image(page_num, image)
            
            # If this is the current page, also update model
            if page_num == self._model.current_page:
                self._model.set_current_image(image)
                self.pdf_image_updated.emit(image)
            
            # Emit signal that page is ready
            self.page_rendered.emit(page_num)
    
    def _prefetch_adjacent_pages(self) -> None:
        """Prefetch pages around current page for smooth navigation."""
        current = self._model.current_page
        page_count = self._model.page_count
        
        # Determine pages to prefetch based on view mode
        pages_to_prefetch = []
        
        if self._model.view_mode == "single":
            # Prefetch next and previous pages
            if current > 1:
                pages_to_prefetch.append(current - 1)
            if current < page_count:
                pages_to_prefetch.append(current + 1)
        
        elif self._model.view_mode == "two_page":
            # Prefetch next two pages
            if current + 1 <= page_count:
                pages_to_prefetch.append(current + 1)
            if current + 2 <= page_count:
                pages_to_prefetch.append(current + 2)
        
        elif self._model.view_mode == "scroll":
            # Prefetch next 3 pages for scrolling
            for i in range(1, 4):
                if current + i <= page_count:
                    pages_to_prefetch.append(current + i)
        
        # Render prefetch pages if not already cached
        for page_num in pages_to_prefetch:
            if self._image_provider and not self._image_provider.has_page(page_num):
                self.render_specific_page(page_num)
    
    @Slot()
    def next_page(self) -> None:
        """F1.3: Navigate to next page."""
        if self._renderer.next_page():
            # Renderer is 0-indexed, model displays 1-indexed
            new_page = self._renderer.current_page + 1
            self._model.set_current_page(new_page)
            self.current_page_changed.emit()
            self._render_current_page()
            self.page_changed.emit(new_page, self._model.page_count)
            self.emit_complete_operation(f"Page {new_page} of {self._model.page_count}")
    
    @Slot()
    def previous_page(self) -> None:
        """F1.3: Navigate to previous page."""
        if self._renderer.previous_page():
            # Renderer is 0-indexed, model displays 1-indexed
            new_page = self._renderer.current_page + 1
            self._model.set_current_page(new_page)
            self.current_page_changed.emit()
            self._render_current_page()
            self.page_changed.emit(new_page, self._model.page_count)
            self.emit_complete_operation(f"Page {new_page} of {self._model.page_count}")
    
    @Slot(int)
    def goto_page(self, page_num: int) -> None:
        """
        F1.3: Jump to specific page.
        
        Args:
            page_num: Page number (1-indexed)
        """
        if self._renderer.set_page(page_num - 1):  # Convert to 0-indexed
            self._model.set_current_page(page_num)
            self.current_page_changed.emit()
            self._render_current_page()
            self.page_changed.emit(self._model.current_page, self._model.page_count)
            self.emit_complete_operation(f"Page {self._model.current_page} of {self._model.page_count}")
    
    @Slot()
    def zoom_in(self) -> None:
        """F1.2: Increase zoom level."""
        new_zoom = self._renderer.zoom_in()
        self._model.set_zoom_level(new_zoom)
        self.zoom_level_changed.emit()
        self._render_current_page()
        self.zoom_changed.emit(new_zoom)
        self.emit_complete_operation(f"Zoom: {new_zoom}%")
    
    @Slot()
    def zoom_out(self) -> None:
        """F1.2: Decrease zoom level."""
        new_zoom = self._renderer.zoom_out()
        self._model.set_zoom_level(new_zoom)
        self.zoom_level_changed.emit()
        self._render_current_page()
        self.zoom_changed.emit(new_zoom)
        self.emit_complete_operation(f"Zoom: {new_zoom}%")
    
    @Slot(int)
    def set_zoom(self, zoom_level: int) -> None:
        """
        F1.2: Set specific zoom level.
        
        Args:
            zoom_level: Zoom percentage (25-400)
        """
        self._renderer.set_zoom(zoom_level)
        self._model.set_zoom_level(zoom_level)
        self.zoom_level_changed.emit()
        self._render_current_page()
        self.zoom_changed.emit(zoom_level)
        self.emit_complete_operation(f"Zoom: {zoom_level}%")
    
    @Slot()
    def rotate(self) -> None:
        """F1.4: Rotate page 90 degrees clockwise."""
        new_rotation = self._renderer.rotate_right()
        self._model.set_rotation(new_rotation)
        self._render_current_page()
        self.rotation_changed.emit(new_rotation)
        self.emit_complete_operation(f"Rotated: {new_rotation}°")
    
    @Slot()
    def rotate_left(self) -> None:
        """F1.4: Rotate page 90 degrees counter-clockwise."""
        new_rotation = self._renderer.rotate_left()
        self._model.set_rotation(new_rotation)
        self._render_current_page()
        self.rotation_changed.emit(new_rotation)
        self.emit_complete_operation(f"Rotated: {new_rotation}°")
    
    @Slot()
    def fit_width(self) -> None:
        """F1.6: Fit page to width (mock for now)."""
        self.emit_complete_operation("Fit to width")
    
    @Slot()
    def fit_height(self) -> None:
        """F1.6: Fit page to height (mock for now)."""
        self.emit_complete_operation("Fit to height")
    
    @Slot()
    def toggle_fullscreen(self) -> None:
        """F1.5: Toggle fullscreen mode (mock for now)."""
        self.emit_complete_operation("Fullscreen toggled")
    
    @Slot(str)
    def set_view_mode(self, mode: str) -> None:
        """
        Set view mode (single, two_page, or scroll).
        
        Args:
            mode: View mode string
        """
        self._model.set_view_mode(mode)
        self.view_mode_changed.emit()
        self.emit_complete_operation(f"View mode: {mode}")
    
    def get_current_image(self) -> QImage:
        """
        Get current rendered page image.
        
        Returns:
            QImage of current page or empty image
        """
        image = self._model.get_current_image()
        return image if image else QImage()
    
    @Slot(str, bool, bool)
    def search_in_pdf(self, query: str, case_sensitive: bool = False, whole_word: bool = False) -> None:
        """
        F1.5: Search for text in the PDF document.
        
        Args:
            query: Search query text
            case_sensitive: Whether search should be case-sensitive
            whole_word: Whether to match whole words only
        """
        print(f"[DEBUG] search_in_pdf called with query: '{query}'")
        print(f"[DEBUG] Document loaded: {self._renderer.document is not None}")
        
        if not self._renderer.document or not query:
            print("[DEBUG] Early return - no document or query")
            self.emit_complete_operation("No search query")
            return
        
        self.emit_start_operation(f"Searching for '{query}'...")
        
        try:
            matches = []
            page_count = self._renderer.get_page_count()
            print(f"[DEBUG] Searching through {page_count} pages")
            
            # Search through all pages
            for page_num in range(page_count):
                page = self._renderer.document[page_num]
                
                # Perform search - use simple search without flags first
                rects = page.search_for(query)
                
                if rects:
                    print(f"[DEBUG] Found {len(rects)} matches on page {page_num + 1}")
                    # Store matches: (1-indexed page, list of rect tuples)
                    rect_data = [(r.x0, r.y0, r.x1, r.y1) for r in rects]
                    matches.append((page_num + 1, rect_data))
            
            # Store and emit results
            self._search_results = matches
            self._total_matches = sum(len(rects) for _, rects in matches)
            self._current_match_index = 0
            
            print(f"[DEBUG] Total matches found: {self._total_matches}")
            print(f"[DEBUG] Emitting signals now...")
            
            if matches:
                self.search_results_changed.emit()
                self.search_result.emit(matches)
                self.current_match_changed.emit()
                
                print(f"[DEBUG] search_match_count property: {self.search_match_count}")
                print(f"[DEBUG] current_match_index property: {self.current_match_index}")
                
                # Navigate to first match
                first_page = matches[0][0]
                self.goto_page(first_page)
                
                self.emit_complete_operation(f"Found {self._total_matches} matches across {len(matches)} pages")
            else:
                self.emit_complete_operation("No matches found")
                self.search_results_changed.emit()
                
        except Exception as e:
            self.emit_error_operation(f"Search error: {str(e)}")
    
    @Slot()
    def next_search_match(self) -> None:
        """F1.5: Navigate to next search match."""
        if not self._search_results or self._total_matches == 0:
            return
        
        # Move to next match
        self._current_match_index = (self._current_match_index + 1) % self._total_matches
        self._navigate_to_current_match()
        self.current_match_changed.emit()
    
    @Slot()
    def previous_search_match(self) -> None:
        """F1.5: Navigate to previous search match."""
        if not self._search_results or self._total_matches == 0:
            return
        
        # Move to previous match
        self._current_match_index = (self._current_match_index - 1) % self._total_matches
        self._navigate_to_current_match()
        self.current_match_changed.emit()
    
    def _navigate_to_current_match(self) -> None:
        """Navigate to the current search match."""
        if not self._search_results:
            return
        
        # Find which page and which match on that page
        match_count = 0
        for page_num, rects in self._search_results:
            if match_count + len(rects) > self._current_match_index:
                # Current match is on this page
                self.goto_page(page_num)
                match_index_on_page = self._current_match_index - match_count
                self.emit_complete_operation(
                    f"Match {self._current_match_index + 1} of {self._total_matches} (Page {page_num})"
                )
                return
            match_count += len(rects)
    
    @Slot()
    def clear_search(self) -> None:
        """F1.5: Clear search results."""
        self._search_results = []
        self._current_match_index = 0
        self._total_matches = 0
        self.search_results_changed.emit()
        self.current_match_changed.emit()
        self.emit_complete_operation("Search cleared")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self._renderer.close_pdf()
