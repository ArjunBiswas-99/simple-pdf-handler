"""
Simple PDF Handler - Viewing Controller

F1: Controls PDF viewing operations with settings persistence.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from PySide6.QtCore import Signal, Slot, Property, QUrl
from PySide6.QtGui import QImage
from pathlib import Path
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
    
    # Signals for events
    page_changed = Signal(int, int)  # current, total
    zoom_changed = Signal(int)
    rotation_changed = Signal(int)
    document_opened = Signal(str)  # filename
    pdf_image_updated = Signal(QImage)  # emits rendered page image
    
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
        # Explicitly pass the current page to avoid any caching issues
        image = self._renderer.render_page(self._renderer.current_page)
        if image:
            self._model.set_current_image(image)
            # Update provider FIRST, BEFORE emitting signal
            if self._image_provider:
                self._image_provider.set_image(image)
            # NOW emit signal to QML (provider already has the new image)
            self.pdf_image_updated.emit(image)
    
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
    
    def get_current_image(self) -> QImage:
        """
        Get current rendered page image.
        
        Returns:
            QImage of current page or empty image
        """
        image = self._model.get_current_image()
        return image if image else QImage()
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self._renderer.close_pdf()
