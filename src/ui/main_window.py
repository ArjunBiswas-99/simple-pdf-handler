"""
Simple PDF Handler - Main Application Window

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

import os
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QMenuBar, QMenu, QStatusBar,
    QToolBar, QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from ui.pdf_canvas import PDFCanvas
from ui.progress_dialog import ProgressDialog
from core.pdf_document import PDFDocument
from core.pdf_loader_worker import PDFLoaderWorker
from core.zoom_render_worker import ZoomRenderWorker
from ui.styles.theme_manager import get_theme_manager
from ui.styles.themes import ThemeType
from utils.constants import (
    ZOOM_LEVELS, ZOOM_LEVEL_LABELS, DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM,
    ZOOM_INCREMENT, LARGE_FILE_THRESHOLD, LARGE_DOCUMENT_PAGE_THRESHOLD
)


class MainWindow(QMainWindow):
    """
    Main application window.
    Manages the user interface and coordinates between components.
    """
    
    # File size threshold for using threaded loading (10MB)
    LARGE_FILE_THRESHOLD = 10 * 1024 * 1024
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self._document = PDFDocument()
        self._loader_worker = None
        self._zoom_worker = None
        self._setup_ui()
        self._update_window_title()
    
    def _setup_ui(self) -> None:
        """Configure the main window layout and components."""
        self.setWindowTitle("Simple PDF Handler")
        self.setMinimumSize(1000, 700)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create PDF canvas as central widget
        self._canvas = PDFCanvas()
        self._canvas.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self.setCentralWidget(self._canvas)
        
        # Create status bar
        self._create_status_bar()
        
        # Create progress dialog
        self._progress_dialog = ProgressDialog(self)
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
    
    def _create_menu_bar(self) -> None:
        """Create and configure the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a PDF file")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Close action
        close_action = QAction("&Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.setStatusTip("Close the current document")
        close_action.triggered.connect(self._on_close_document)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Theme toggle action
        self._theme_action = QAction("🌓 Switch to Dark Theme", self)
        self._theme_action.setStatusTip("Toggle between light and dark themes")
        self._theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(self._theme_action)
        
        view_menu.addSeparator()
        
        # Placeholder for future view options
        view_action = QAction("View Options (Coming Soon)", self)
        view_action.setEnabled(False)
        view_menu.addAction(view_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Simple PDF Handler")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self) -> None:
        """Create and configure the navigation toolbar."""
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # First page button
        self._first_page_btn = QPushButton("⏮ First")
        self._first_page_btn.setEnabled(False)
        self._first_page_btn.clicked.connect(self._go_to_first_page)
        toolbar.addWidget(self._first_page_btn)
        
        # Previous page button
        self._prev_page_btn = QPushButton("◀ Previous")
        self._prev_page_btn.setEnabled(False)
        self._prev_page_btn.clicked.connect(self._go_to_previous_page)
        toolbar.addWidget(self._prev_page_btn)
        
        # Page number input
        toolbar.addWidget(QLabel("  Page: "))
        self._page_input = QLineEdit()
        self._page_input.setMaximumWidth(60)
        self._page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_input.setEnabled(False)
        self._page_input.returnPressed.connect(self._on_page_input_changed)
        toolbar.addWidget(self._page_input)
        
        # Total pages label
        self._page_count_label = QLabel(" of 0")
        toolbar.addWidget(self._page_count_label)
        
        # Next page button
        self._next_page_btn = QPushButton("Next ▶")
        self._next_page_btn.setEnabled(False)
        self._next_page_btn.clicked.connect(self._go_to_next_page)
        toolbar.addWidget(self._next_page_btn)
        
        # Last page button
        self._last_page_btn = QPushButton("Last ⏭")
        self._last_page_btn.setEnabled(False)
        self._last_page_btn.clicked.connect(self._go_to_last_page)
        toolbar.addWidget(self._last_page_btn)
        
        # Add separator
        toolbar.addSeparator()
        
        # Zoom out button
        self._zoom_out_btn = QPushButton("🔍−")
        self._zoom_out_btn.setEnabled(False)
        self._zoom_out_btn.setStatusTip("Zoom out")
        self._zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar.addWidget(self._zoom_out_btn)
        
        # Zoom level dropdown
        toolbar.addWidget(QLabel(" "))
        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(ZOOM_LEVEL_LABELS)
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.setEnabled(False)
        self._zoom_combo.setMinimumWidth(85)
        self._zoom_combo.setMaximumWidth(95)
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_combo_changed)
        toolbar.addWidget(self._zoom_combo)
        
        # Zoom in button
        self._zoom_in_btn = QPushButton("🔍+")
        self._zoom_in_btn.setEnabled(False)
        self._zoom_in_btn.setStatusTip("Zoom in")
        self._zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar.addWidget(self._zoom_in_btn)
        
        toolbar.addWidget(QLabel("  "))
        
        # Fit width button
        self._fit_width_btn = QPushButton("Fit Width")
        self._fit_width_btn.setEnabled(False)
        self._fit_width_btn.setStatusTip("Fit page width to window")
        self._fit_width_btn.clicked.connect(self._fit_width)
        toolbar.addWidget(self._fit_width_btn)
        
        # Fit page button
        self._fit_page_btn = QPushButton("Fit Page")
        self._fit_page_btn.setEnabled(False)
        self._fit_page_btn.setStatusTip("Fit entire page to window")
        self._fit_page_btn.clicked.connect(self._fit_page)
        toolbar.addWidget(self._fit_page_btn)
    
    def _create_status_bar(self) -> None:
        """Create and configure the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts for navigation."""
        # Previous page shortcuts
        prev_shortcut1 = QAction(self)
        prev_shortcut1.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_shortcut1.triggered.connect(self._go_to_previous_page)
        self.addAction(prev_shortcut1)
        
        prev_shortcut2 = QAction(self)
        prev_shortcut2.setShortcut(QKeySequence(Qt.Key.Key_PageUp))
        prev_shortcut2.triggered.connect(self._go_to_previous_page)
        self.addAction(prev_shortcut2)
        
        # Next page shortcuts
        next_shortcut1 = QAction(self)
        next_shortcut1.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_shortcut1.triggered.connect(self._go_to_next_page)
        self.addAction(next_shortcut1)
        
        next_shortcut2 = QAction(self)
        next_shortcut2.setShortcut(QKeySequence(Qt.Key.Key_PageDown))
        next_shortcut2.triggered.connect(self._go_to_next_page)
        self.addAction(next_shortcut2)
        
        # First page shortcut
        first_shortcut = QAction(self)
        first_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Home))
        first_shortcut.triggered.connect(self._go_to_first_page)
        self.addAction(first_shortcut)
        
        # Last page shortcut
        last_shortcut = QAction(self)
        last_shortcut.setShortcut(QKeySequence(Qt.Key.Key_End))
        last_shortcut.triggered.connect(self._go_to_last_page)
        self.addAction(last_shortcut)
    
    def _on_open_file(self) -> None:
        """Handle file open action."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Check file size to decide loading strategy
        file_size = os.path.getsize(file_path)
        
        if file_size >= self.LARGE_FILE_THRESHOLD:
            # Large file - use threaded loading
            self._load_file_async(file_path, file_size)
        else:
            # Small file - load synchronously
            self._load_file_sync(file_path)
    
    def _load_file_sync(self, file_path: str) -> None:
        """
        Load a PDF file synchronously (for small files).
        
        Args:
            file_path: Path to the PDF file
        """
        self._status_bar.showMessage("Loading PDF...")
        
        # Close existing document
        if self._document.is_open():
            self._document.close()
        
        # Open the file
        success = self._document.open(file_path)
        
        if success:
            self._on_document_loaded()
        else:
            self._show_error("Failed to open PDF file")
            self._status_bar.showMessage("Failed to load PDF")
    
    def _load_file_async(self, file_path: str, file_size: int) -> None:
        """
        Load a PDF file asynchronously using a background thread.
        
        Args:
            file_path: Path to the PDF file
            file_size: Size of the file in bytes
        """
        # Create and configure worker thread
        self._loader_worker = PDFLoaderWorker(file_path)
        self._loader_worker.progress_updated.connect(self._progress_dialog.update_progress)
        self._loader_worker.loading_completed.connect(self._on_async_loading_completed)
        self._loader_worker.loading_failed.connect(self._on_async_loading_failed)
        
        # Set file info in progress dialog
        size_mb = file_size / (1024 * 1024)
        self._progress_dialog.set_file_info(f"File size: {size_mb:.1f} MB")
        
        # Show progress dialog and start loading
        self._progress_dialog.reset()
        self._progress_dialog.show()
        self._loader_worker.start()
    
    def _on_async_loading_completed(self, backend) -> None:
        """
        Handle successful completion of asynchronous loading.
        
        Args:
            backend: Loaded PyMuPDFBackend instance
        """
        # Close progress dialog
        self._progress_dialog.accept()
        
        # Close existing document and use the new backend
        if self._document.is_open():
            self._document.close()
        
        # Transfer the backend to the document
        self._document._backend = backend
        self._document._current_page = 0
        self._document._zoom_level = 1.0
        
        self._on_document_loaded()
    
    def _on_async_loading_failed(self, error_message: str) -> None:
        """
        Handle failure of asynchronous loading.
        
        Args:
            error_message: Error description
        """
        self._progress_dialog.reject()
        self._show_error(f"Failed to load PDF: {error_message}")
        self._status_bar.showMessage("Failed to load PDF")
    
    def _on_document_loaded(self) -> None:
        """Handle successful document loading."""
        page_count = self._document.get_page_count()
        file_name = os.path.basename(self._document.get_file_path())
        
        # Update window title
        self._update_window_title(file_name)
        
        # Enable navigation and zoom controls
        self._update_navigation_controls()
        self._enable_zoom_controls()
        
        # Reset zoom to 100%
        self._document.set_zoom_level(DEFAULT_ZOOM)
        self._zoom_combo.setCurrentText("100%")
        
        # Render and display all pages in continuous mode
        self._render_all_pages()
        
        self._status_bar.showMessage(f"Loaded: {file_name} ({page_count} pages)")
    
    def _on_close_document(self) -> None:
        """Handle document close action."""
        if self._document.is_open():
            self._document.close()
            self._canvas.clear()
            self._update_window_title()
            self._disable_navigation_controls()
            self._disable_zoom_controls()
            self._status_bar.showMessage("Document closed")
    
    def _go_to_first_page(self) -> None:
        """Navigate to the first page of the document."""
        if not self._document.is_open():
            return
        
        if self._document.set_current_page(0):
            self._canvas.scroll_to_page(0)
            self._update_navigation_controls()
    
    def _go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        if not self._document.is_open():
            return
        
        current = self._document.get_current_page()
        if current > 0:
            if self._document.set_current_page(current - 1):
                self._canvas.scroll_to_page(current - 1)
                self._update_navigation_controls()
    
    def _go_to_next_page(self) -> None:
        """Navigate to the next page."""
        if not self._document.is_open():
            return
        
        current = self._document.get_current_page()
        page_count = self._document.get_page_count()
        if current < page_count - 1:
            if self._document.set_current_page(current + 1):
                self._canvas.scroll_to_page(current + 1)
                self._update_navigation_controls()
    
    def _go_to_last_page(self) -> None:
        """Navigate to the last page of the document."""
        if not self._document.is_open():
            return
        
        last_page = self._document.get_page_count() - 1
        if self._document.set_current_page(last_page):
            self._canvas.scroll_to_page(last_page)
            self._update_navigation_controls()
    
    def _on_page_input_changed(self) -> None:
        """Handle manual page number input."""
        if not self._document.is_open():
            return
        
        try:
            # Get user input (1-indexed)
            page_num = int(self._page_input.text())
            # Convert to 0-indexed
            page_index = page_num - 1
            
            if self._document.set_current_page(page_index):
                self._canvas.scroll_to_page(page_index)
                self._update_navigation_controls()
            else:
                # Invalid page number, reset to current
                current = self._document.get_current_page()
                self._page_input.setText(str(current + 1))
        except ValueError:
            # Invalid input, reset to current page
            current = self._document.get_current_page()
            self._page_input.setText(str(current + 1))
    
    def _render_all_pages(self) -> None:
        """Render and display all pages in continuous scrolling mode."""
        page_count = self._document.get_page_count()
        pixmaps = []
        
        self._status_bar.showMessage(f"Rendering {page_count} pages...")
        
        # Render all pages
        for page_num in range(page_count):
            pixmap = self._document.render_page(page_num)
            if pixmap:
                pixmaps.append(pixmap)
            else:
                self._show_error(f"Failed to render page {page_num + 1}")
                return
        
        # Display all pages in continuous layout
        self._canvas.display_pages(pixmaps)
        
        # Scroll to first page
        self._canvas.scroll_to_page(0)
    
    def _update_navigation_controls(self) -> None:
        """Update the state of navigation controls based on current page."""
        if not self._document.is_open():
            self._disable_navigation_controls()
            return
        
        current_page = self._document.get_current_page()
        page_count = self._document.get_page_count()
        
        # Update page input and label
        self._page_input.setText(str(current_page + 1))
        self._page_count_label.setText(f" of {page_count}")
        
        # Enable controls
        self._page_input.setEnabled(True)
        
        # Enable/disable navigation buttons based on current position
        self._first_page_btn.setEnabled(current_page > 0)
        self._prev_page_btn.setEnabled(current_page > 0)
        self._next_page_btn.setEnabled(current_page < page_count - 1)
        self._last_page_btn.setEnabled(current_page < page_count - 1)
    
    def _disable_navigation_controls(self) -> None:
        """Disable all navigation controls when no document is loaded."""
        self._page_input.setEnabled(False)
        self._page_input.setText("")
        self._page_count_label.setText(" of 0")
        self._first_page_btn.setEnabled(False)
        self._prev_page_btn.setEnabled(False)
        self._next_page_btn.setEnabled(False)
        self._last_page_btn.setEnabled(False)
    
    def _on_scroll(self) -> None:
        """Handle scroll events to update current page tracking."""
        if not self._document.is_open():
            return
        
        # Get the currently visible page from the canvas
        visible_page = self._canvas.get_visible_page()
        
        # Update document's current page if it changed
        if visible_page != self._document.get_current_page():
            self._document.set_current_page(visible_page)
            self._update_navigation_controls()
    
    def _on_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        theme_manager = get_theme_manager()
        new_theme = theme_manager.toggle_theme()
        
        # Update menu action text
        if new_theme == ThemeType.DARK:
            self._theme_action.setText("☀️ Switch to Light Theme")
            self._status_bar.showMessage("Dark theme activated")
        else:
            self._theme_action.setText("🌓 Switch to Dark Theme")
            self._status_bar.showMessage("Light theme activated")
        
        # Update canvas background color based on theme
        self._update_canvas_background()
    
    def _update_canvas_background(self) -> None:
        """Update canvas background color based on current theme."""
        theme_manager = get_theme_manager()
        
        if theme_manager.is_dark_theme():
            self._canvas.setStyleSheet("background-color: #1A1A1A;")
        else:
            self._canvas.setStyleSheet("background-color: #525252;")
    
    def _on_about(self) -> None:
        """Display about dialog."""
        QMessageBox.about(
            self,
            "About Simple PDF Handler",
            "<h3>Simple PDF Handler</h3>"
            "<p>Version 0.1.0</p>"
            "<p>A professional PDF manipulation application built with Python and PyQt6.</p>"
            "<p>Created by Arjun Biswas</p>"
        )
    
    def _show_error(self, message: str) -> None:
        """
        Display an error message dialog.
        
        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Error", message)
    
    def _update_window_title(self, file_name: str = None) -> None:
        """
        Update the window title with current document name.
        
        Args:
            file_name: Name of the currently open file, or None if no file is open
        """
        if file_name:
            self.setWindowTitle(f"{file_name} - Simple PDF Handler")
        else:
            self.setWindowTitle("Simple PDF Handler")
    
    def _enable_zoom_controls(self) -> None:
        """Enable zoom controls when a document is loaded."""
        self._zoom_in_btn.setEnabled(True)
        self._zoom_out_btn.setEnabled(True)
        self._zoom_combo.setEnabled(True)
        self._fit_width_btn.setEnabled(True)
        self._fit_page_btn.setEnabled(True)
    
    def _disable_zoom_controls(self) -> None:
        """Disable zoom controls when no document is loaded."""
        self._zoom_in_btn.setEnabled(False)
        self._zoom_out_btn.setEnabled(False)
        self._zoom_combo.setEnabled(False)
        self._fit_width_btn.setEnabled(False)
        self._fit_page_btn.setEnabled(False)
    
    def _on_zoom_combo_changed(self, text: str) -> None:
        """
        Handle zoom level selection from dropdown.
        
        Args:
            text: Selected zoom level text (e.g., "100%")
        """
        if not self._document.is_open():
            return
        
        # Get zoom level from text
        zoom_level = ZOOM_LEVELS.get(text)
        if zoom_level is None:
            return
        
        # Apply the new zoom level
        self._apply_zoom(zoom_level)
    
    def _zoom_in(self) -> None:
        """Increase zoom level by one step."""
        if not self._document.is_open():
            return
        
        current_zoom = self._document.get_zoom_level()
        new_zoom = min(current_zoom + ZOOM_INCREMENT, MAX_ZOOM)
        
        if new_zoom != current_zoom:
            self._apply_zoom(new_zoom)
            self._update_zoom_display(new_zoom)
    
    def _zoom_out(self) -> None:
        """Decrease zoom level by one step."""
        if not self._document.is_open():
            return
        
        current_zoom = self._document.get_zoom_level()
        new_zoom = max(current_zoom - ZOOM_INCREMENT, MIN_ZOOM)
        
        if new_zoom != current_zoom:
            self._apply_zoom(new_zoom)
            self._update_zoom_display(new_zoom)
    
    def _fit_width(self) -> None:
        """Calculate and apply zoom to fit page width to window."""
        if not self._document.is_open():
            return
        
        # Get the first page dimensions
        page_size = self._document.get_page_size(0)
        if not page_size:
            return
        
        page_width, _ = page_size
        
        # Calculate zoom to fit width (accounting for margins)
        canvas_width = self._canvas.viewport().width() - 40  # 20px margins on each side
        zoom = canvas_width / page_width
        
        # Clamp to min/max zoom
        zoom = max(MIN_ZOOM, min(zoom, MAX_ZOOM))
        
        self._apply_zoom(zoom)
        self._update_zoom_display(zoom)
    
    def _fit_page(self) -> None:
        """Calculate and apply zoom to fit entire page in window."""
        if not self._document.is_open():
            return
        
        # Get the first page dimensions
        page_size = self._document.get_page_size(0)
        if not page_size:
            return
        
        page_width, page_height = page_size
        
        # Calculate zoom to fit both dimensions (accounting for margins)
        canvas_width = self._canvas.viewport().width() - 40
        canvas_height = self._canvas.viewport().height() - 40
        
        zoom_width = canvas_width / page_width
        zoom_height = canvas_height / page_height
        
        # Use the smaller zoom to ensure entire page fits
        zoom = min(zoom_width, zoom_height)
        
        # Clamp to min/max zoom
        zoom = max(MIN_ZOOM, min(zoom, MAX_ZOOM))
        
        self._apply_zoom(zoom)
        self._update_zoom_display(zoom)
    
    def _apply_zoom(self, new_zoom: float) -> None:
        """
        Apply a new zoom level and re-render the document.
        Uses threading for large documents to keep UI responsive.
        
        Args:
            new_zoom: Zoom level to apply (e.g., 1.0 for 100%)
        """
        if not self._document.is_open():
            return
        
        # Cancel any ongoing zoom rendering
        if self._zoom_worker and self._zoom_worker.isRunning():
            self._zoom_worker.cancel()
            self._zoom_worker.wait()
        
        # Remember current page to restore scroll position
        current_page = self._document.get_current_page()
        
        # Update zoom level in document
        self._document.set_zoom_level(new_zoom)
        
        page_count = self._document.get_page_count()
        
        # Decide whether to use threading based on document size
        if page_count <= LARGE_DOCUMENT_PAGE_THRESHOLD:
            # Small document - render synchronously
            self._render_zoom_sync(current_page, new_zoom)
        else:
            # Large document - render asynchronously with progress dialog
            self._render_zoom_async(current_page, new_zoom)
    
    def _render_zoom_sync(self, current_page: int, zoom: float) -> None:
        """
        Render all pages at new zoom level synchronously.
        
        Args:
            current_page: Page number to scroll back to after rendering
            zoom: Zoom level to render at
        """
        self._status_bar.showMessage(f"Applying zoom: {int(zoom * 100)}%...")
        
        # Re-render all pages
        self._render_all_pages()
        
        # Restore scroll position
        self._canvas.scroll_to_page(current_page)
        
        self._status_bar.showMessage(f"Zoom: {int(zoom * 100)}%")
    
    def _render_zoom_async(self, current_page: int, zoom: float) -> None:
        """
        Render all pages at new zoom level asynchronously using background thread.
        
        Args:
            current_page: Page number to scroll back to after rendering
            zoom: Zoom level to render at
        """
        page_count = self._document.get_page_count()
        
        # Create zoom render worker
        self._zoom_worker = ZoomRenderWorker(
            self._document._backend,
            zoom,
            page_count
        )
        
        # Connect signals
        self._zoom_worker.progress_updated.connect(self._progress_dialog.update_progress)
        self._zoom_worker.rendering_completed.connect(
            lambda pixmaps: self._on_zoom_rendering_completed(pixmaps, current_page, zoom)
        )
        self._zoom_worker.rendering_failed.connect(self._on_zoom_rendering_failed)
        
        # Configure and show progress dialog
        self._progress_dialog.set_status(f"Rendering at {int(zoom * 100)}%...")
        self._progress_dialog.set_file_info(f"Rendering {page_count} pages")
        self._progress_dialog.reset()
        self._progress_dialog.show()
        
        # Start rendering in background
        self._zoom_worker.start()
    
    def _on_zoom_rendering_completed(self, pixmaps: list, current_page: int, zoom: float) -> None:
        """
        Handle completion of asynchronous zoom rendering.
        
        Args:
            pixmaps: List of rendered page pixmaps
            current_page: Page to scroll to
            zoom: Zoom level that was applied
        """
        # Close progress dialog
        self._progress_dialog.accept()
        
        # Display the rendered pages
        self._canvas.display_pages(pixmaps)
        
        # Restore scroll position
        self._canvas.scroll_to_page(current_page)
        
        # Update status
        self._status_bar.showMessage(f"Zoom: {int(zoom * 100)}%")
    
    def _on_zoom_rendering_failed(self, error_message: str) -> None:
        """
        Handle failure of asynchronous zoom rendering.
        
        Args:
            error_message: Error description
        """
        self._progress_dialog.reject()
        self._show_error(f"Failed to render at new zoom: {error_message}")
        self._status_bar.showMessage("Zoom rendering failed")
    
    def _update_zoom_display(self, zoom: float) -> None:
        """
        Update the zoom display in the UI.
        
        Args:
            zoom: Current zoom level
        """
        zoom_percent = int(zoom * 100)
        zoom_text = f"{zoom_percent}%"
        
        # Update combo box if the value is in the list
        if zoom_text in ZOOM_LEVEL_LABELS:
            # Temporarily disconnect signal to avoid recursion
            self._zoom_combo.blockSignals(True)
            self._zoom_combo.setCurrentText(zoom_text)
            self._zoom_combo.blockSignals(False)
        else:
            # Custom zoom level - show in combo but don't select
            self._zoom_combo.blockSignals(True)
            self._zoom_combo.setCurrentText(zoom_text)
            self._zoom_combo.blockSignals(False)
    
    def closeEvent(self, event) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        # Clean up document resources
        if self._document.is_open():
            self._document.close()
        
        # Stop any running worker threads
        if self._loader_worker and self._loader_worker.isRunning():
            self._loader_worker.quit()
            self._loader_worker.wait()
        
        if self._zoom_worker and self._zoom_worker.isRunning():
            self._zoom_worker.cancel()
            self._zoom_worker.wait()
        
        event.accept()
