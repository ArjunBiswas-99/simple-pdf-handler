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
import unicodedata
import re
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QMenuBar, QMenu, QStatusBar,
    QToolBar, QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout, QComboBox,
    QSplitter, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QAction, QKeySequence, QPixmap
from ui.pdf_canvas import PDFCanvas
from ui.progress_dialog import ProgressDialog
from ui.left_side_panel import LeftSidePanel, AccordionSection
from ui.search_panel import SearchPanel
from core.pdf_document import PDFDocument
from core.pdf_loader_worker import PDFLoaderWorker
from core.zoom_render_worker import ZoomRenderWorker
from core.text_search_worker import TextSearchWorker
from core.search_results_manager import SearchResultsManager
from ui.styles.theme_manager import get_theme_manager
from ui.styles.themes import ThemeType
from ui.styles.professional_styles import ProfessionalStyles
from utils.constants import (
    ZOOM_LEVELS, ZOOM_LEVEL_LABELS, DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM,
    ZOOM_INCREMENT, LARGE_FILE_THRESHOLD, LARGE_DOCUMENT_PAGE_THRESHOLD,
    SEARCH_DEBOUNCE_DELAY
)
from utils.settings_manager import get_settings_manager


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
        
        # Search functionality
        self._search_worker = None
        self._search_results = SearchResultsManager()
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._execute_search)
        
        # Track search panel for direct access
        self._search_panel = None
        self._search_section = None
        
        # Text selection support
        self._selection_enabled = True
        
        # On-demand rendering support
        self._rendered_pages = set()  # Track which pages have been rendered
        self._lazy_rendering_active = False
        self._render_debounce_timer = QTimer()
        self._render_debounce_timer.setSingleShot(True)
        self._render_debounce_timer.timeout.connect(self._render_visible_pages)
        
        self._setup_ui()
        self._update_window_title()
    
    def _setup_ui(self) -> None:
        """Configure the main window layout and components."""
        self.setWindowTitle("Simple PDF Handler")
        self.setMinimumSize(1000, 700)
        
        # Apply professional stylesheet
        self.setStyleSheet(ProfessionalStyles.get_complete_stylesheet())
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create navigation toolbar
        self._create_toolbar()
        
        # Create main content area with sidebar and canvas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create sidebar
        self._left_panel = LeftSidePanel()
        splitter.addWidget(self._left_panel)
        
        # Create PDF canvas
        self._canvas = PDFCanvas()
        self._canvas.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._canvas.text_selected.connect(self._on_text_selected)
        self._canvas.zoom_requested.connect(self._on_zoom_requested)
        splitter.addWidget(self._canvas)
        
        # Set splitter properties
        splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        splitter.setStretchFactor(1, 1)  # Canvas stretches
        splitter.setSizes([300, 700])     # Initial sizes
        
        # Set as central widget
        self.setCentralWidget(splitter)
        
        # Create and add search section to sidebar
        self._create_search_section()
        
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
        
        # Left panel toggle button (icon only)
        self._panel_toggle_btn = QPushButton("☰")
        self._panel_toggle_btn.setToolTip("Toggle left panel (Ctrl+B)")
        self._panel_toggle_btn.setCheckable(True)
        self._panel_toggle_btn.setChecked(True)
        self._panel_toggle_btn.clicked.connect(self._toggle_left_panel)
        toolbar.addWidget(self._panel_toggle_btn)
        
        toolbar.addSeparator()
        
        # First page button (icon only)
        self._first_page_btn = QPushButton("⏮")
        self._first_page_btn.setToolTip("First page")
        self._first_page_btn.setEnabled(False)
        self._first_page_btn.clicked.connect(self._go_to_first_page)
        toolbar.addWidget(self._first_page_btn)
        
        # Previous page button (icon only)
        self._prev_page_btn = QPushButton("◀")
        self._prev_page_btn.setToolTip("Previous page (←)")
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
        
        # Next page button (icon only)
        self._next_page_btn = QPushButton("▶")
        self._next_page_btn.setToolTip("Next page (→)")
        self._next_page_btn.setEnabled(False)
        self._next_page_btn.clicked.connect(self._go_to_next_page)
        toolbar.addWidget(self._next_page_btn)
        
        # Last page button (icon only)
        self._last_page_btn = QPushButton("⏭")
        self._last_page_btn.setToolTip("Last page")
        self._last_page_btn.setEnabled(False)
        self._last_page_btn.clicked.connect(self._go_to_last_page)
        toolbar.addWidget(self._last_page_btn)
        
        # Add separator
        toolbar.addSeparator()
        
        # Zoom out button (icon only)
        self._zoom_out_btn = QPushButton("−")
        self._zoom_out_btn.setToolTip("Zoom out")
        self._zoom_out_btn.setEnabled(False)
        self._zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar.addWidget(self._zoom_out_btn)
        
        # Zoom level dropdown
        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(ZOOM_LEVEL_LABELS)
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.setEnabled(False)
        self._zoom_combo.setMinimumWidth(75)
        self._zoom_combo.setMaximumWidth(85)
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_combo_changed)
        toolbar.addWidget(self._zoom_combo)
        
        # Zoom in button (icon only)
        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setToolTip("Zoom in")
        self._zoom_in_btn.setEnabled(False)
        self._zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar.addWidget(self._zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Fit width button (icon only)
        self._fit_width_btn = QPushButton("⬌")
        self._fit_width_btn.setToolTip("Fit page width")
        self._fit_width_btn.setEnabled(False)
        self._fit_width_btn.clicked.connect(self._fit_width)
        toolbar.addWidget(self._fit_width_btn)
        
        # Fit page button (icon only)
        self._fit_page_btn = QPushButton("⬓")
        self._fit_page_btn.setToolTip("Fit entire page")
        self._fit_page_btn.setEnabled(False)
        self._fit_page_btn.clicked.connect(self._fit_page)
        toolbar.addWidget(self._fit_page_btn)
    
    def _create_search_section(self) -> None:
        """Create and configure the search accordion section."""
        # Create search panel
        self._search_panel = SearchPanel()
        
        # Connect search panel signals
        self._search_panel.search_requested.connect(self._on_search_requested)
        self._search_panel.next_match_requested.connect(self._find_next)
        self._search_panel.previous_match_requested.connect(self._find_previous)
        self._search_panel.result_selected.connect(self._on_search_result_selected)
        
        # Create accordion section
        self._search_section = AccordionSection("Search", "🔍")
        self._search_section.set_content(self._search_panel)
        
        # Start expanded
        self._search_section.set_expanded(True)
        
        # Add to sidebar
        self._left_panel.add_section(self._search_section)
    
    def _create_status_bar(self) -> None:
        """Create and configure the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts for navigation and search."""
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
        
        # Search shortcuts
        find_shortcut = QAction(self)
        find_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        find_shortcut.triggered.connect(self._focus_search)
        self.addAction(find_shortcut)
        
        find_next_shortcut = QAction(self)
        find_next_shortcut.setShortcut(QKeySequence(Qt.Key.Key_F3))
        find_next_shortcut.triggered.connect(self._find_next)
        self.addAction(find_next_shortcut)
        
        find_prev_shortcut = QAction(self)
        find_prev_shortcut.setShortcut(QKeySequence("Shift+F3"))
        find_prev_shortcut.triggered.connect(self._find_previous)
        self.addAction(find_prev_shortcut)
        
        # Panel toggle shortcut
        panel_toggle_shortcut = QAction(self)
        panel_toggle_shortcut.setShortcut(QKeySequence("Ctrl+B"))
        panel_toggle_shortcut.triggered.connect(self._toggle_left_panel)
        self.addAction(panel_toggle_shortcut)
        
        # Text selection shortcuts
        copy_shortcut = QAction(self)
        copy_shortcut.setShortcut(QKeySequence("Ctrl+C"))
        copy_shortcut.triggered.connect(self._copy_selected_text)
        self.addAction(copy_shortcut)
        
        escape_shortcut = QAction(self)
        escape_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        escape_shortcut.triggered.connect(self._clear_selection)
        self.addAction(escape_shortcut)
    
    def _toggle_left_panel(self) -> None:
        """Toggle the visibility of the left side panel."""
        if self._left_panel:
            self._left_panel.toggle_collapse()
            # Update button state
            self._panel_toggle_btn.setChecked(not self._left_panel.is_collapsed())
    
    def _on_open_file(self) -> None:
        """Handle file open action."""
        # Get settings manager to retrieve last directory
        settings = get_settings_manager()
        last_dir = settings.get_last_open_directory()
        
        # Show file dialog starting from last opened directory
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            last_dir,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Save the directory for next time
        settings.set_last_open_directory(file_path)
        
        # Add to recent files
        settings.add_recent_file(file_path)
        
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
        
        # Update canvas zoom level
        self._canvas.set_zoom_level(DEFAULT_ZOOM)
        
        # Use lazy rendering for large documents to avoid UI freeze
        if page_count > 50:
            self._render_initial_pages_lazy()
        else:
            # Small document - render all pages
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
    
    def _render_initial_pages_lazy(self) -> None:
        """
        Render initial pages lazily for large documents to avoid UI freeze.
        Only renders first 20 pages, creates placeholders for rest.
        """
        page_count = self._document.get_page_count()
        zoom = self._document.get_zoom_level()
        
        # Render first 20 pages only
        initial_render_count = min(20, page_count)
        
        self._status_bar.showMessage(f"Rendering initial {initial_render_count} of {page_count} pages...")
        
        # Track rendered pages
        self._rendered_pages.clear()
        for i in range(initial_render_count):
            self._rendered_pages.add(i)
        
        pixmaps = []
        for page_num in range(page_count):
            if page_num < initial_render_count:
                # Render first pages
                pixmap = self._document.render_page(page_num)
                pixmaps.append(pixmap if pixmap else QPixmap())
            else:
                # Create placeholder for remaining pages
                page_size = self._document.get_page_size(page_num)
                if page_size:
                    width, height = page_size
                    scaled_width = int(width * zoom)
                    scaled_height = int(height * zoom)
                    placeholder = QPixmap(scaled_width, scaled_height)
                    placeholder.fill(Qt.GlobalColor.white)
                    pixmaps.append(placeholder)
                else:
                    pixmaps.append(QPixmap())
        
        # Display all pages (with placeholders)
        self._canvas.display_pages(pixmaps)
        
        # Scroll to first page
        self._canvas.scroll_to_page(0)
        
        # Enable lazy rendering mode
        self._lazy_rendering_active = True
        
        self._status_bar.showMessage(f"Loaded: {page_count} pages (Lazy rendering active)")
    
    def _render_visible_pages(self) -> None:
        """
        Render pages that are currently visible in the viewport.
        Renders 20 pages at a time (10 before, 10 after current page).
        """
        if not self._lazy_rendering_active or not self._document.is_open():
            return
        
        current_page = self._document.get_current_page()
        page_count = self._document.get_page_count()
        zoom = self._document.get_zoom_level()
        
        # Determine range of pages to render (current ± 10 pages)
        window_size = 10
        start_page = max(0, current_page - window_size)
        end_page = min(page_count, current_page + window_size + 1)
        
        # Find pages that need rendering
        pages_to_render = []
        for page_num in range(start_page, end_page):
            if page_num not in self._rendered_pages:
                pages_to_render.append(page_num)
        
        if not pages_to_render:
            return  # All visible pages already rendered
        
        print(f"[LAZY RENDER] Rendering pages {pages_to_render[0]}-{pages_to_render[-1]} ({len(pages_to_render)} pages)")
        
        # Render these pages
        for page_num in pages_to_render:
            pixmap = self._document.render_page(page_num)
            if pixmap:
                # Replace the placeholder with actual rendered page
                page_label = self._canvas._page_labels[page_num]
                page_label.setPixmap(pixmap)
                self._rendered_pages.add(page_num)
                print(f"[LAZY RENDER] Rendered page {page_num + 1}")
        
        # Update status
        rendered_count = len(self._rendered_pages)
        self._status_bar.showMessage(
            f"Rendered {rendered_count}/{page_count} pages", 
            2000
        )
    
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
        """Handle scroll events to update current page tracking and trigger on-demand rendering."""
        if not self._document.is_open():
            return
        
        # Get the currently visible page from the canvas
        visible_page = self._canvas.get_visible_page()
        
        # Update document's current page if it changed
        if visible_page != self._document.get_current_page():
            self._document.set_current_page(visible_page)
            self._update_navigation_controls()
        
        # Trigger on-demand rendering if lazy rendering is active
        if self._lazy_rendering_active:
            # Use debounce timer to avoid rendering on every scroll event
            self._render_debounce_timer.stop()
            self._render_debounce_timer.start(200)  # 200ms delay
    
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
        Render pages at new zoom level.
        For large documents, only renders visible pages for instant zoom.
        
        Args:
            current_page: Page number to scroll back to after rendering
            zoom: Zoom level to render at
        """
        page_count = self._document.get_page_count()
        print(f"[ZOOM DEBUG] Starting zoom to {int(zoom * 100)}%, page count: {page_count}, current page: {current_page}")
        
        self._status_bar.showMessage(f"Rendering pages at {int(zoom * 100)}%...")
        
        # Update canvas zoom level
        self._canvas.set_zoom_level(zoom)
        
        # For very large documents (>50 pages), use lazy rendering
        if page_count > 50:
            # Only render a window of pages around current page
            window_size = 10  # Render 10 pages before and after
            start_page = max(0, current_page - window_size)
            end_page = min(page_count, current_page + window_size + 1)
            
            # IMPORTANT: Clear rendered pages tracking since we're at a new zoom level
            # All old pages at old zoom level are now invalid
            self._rendered_pages.clear()
            
            # PROGRESSIVE RENDERING: Update pages one by one instead of batch display
            # This keeps old pages visible while rendering new ones
            print(f"[ZOOM DEBUG] Progressive rendering: pages {start_page}-{end_page-1}")
            
            # First, update placeholders for ALL pages to new zoom size
            # This resizes existing labels without clearing content
            for page_num in range(page_count):
                page_size = self._document.get_page_size(page_num)
                if page_size:
                    width, height = page_size
                    scaled_width = int(width * zoom)
                    scaled_height = int(height * zoom)
                    
                    # Get existing label
                    if page_num < len(self._canvas._page_labels):
                        label = self._canvas._page_labels[page_num]
                        # If this page is outside visible window, create placeholder
                        if page_num < start_page or page_num >= end_page:
                            placeholder = QPixmap(scaled_width, scaled_height)
                            placeholder.fill(Qt.GlobalColor.white)
                            label.setPixmap(placeholder)
            
            QApplication.processEvents()  # Update placeholders
            
            # Now render visible pages progressively
            for i, page_num in enumerate(range(start_page, end_page)):
                # Render page
                pixmap = self._document.render_page(page_num)
                if pixmap and page_num < len(self._canvas._page_labels):
                    # Update individual label (old page stays visible until replaced!)
                    label = self._canvas._page_labels[page_num]
                    label.setPixmap(pixmap)
                    self._rendered_pages.add(page_num)
                    
                    # Update status bar
                    self._status_bar.showMessage(f"Rendering page {page_num + 1} at {int(zoom * 100)}%... ({i+1}/{end_page-start_page})")
                    QApplication.processEvents()  # Show this page immediately!
            
            print(f"[ZOOM DEBUG] Progressive rendering complete")
            
            # IMPORTANT: Use QTimer to ensure scroll happens after display is complete
            QTimer.singleShot(0, lambda: self._canvas.scroll_to_page(current_page))
            
            # Keep lazy rendering active so scrolling triggers more rendering
            self._lazy_rendering_active = True
            
            self._status_bar.showMessage(f"Zoom: {int(zoom * 100)}% (Lazy rendering active)")
        else:
            # Small document - render all pages
            self._render_all_pages()
            self._status_bar.showMessage(f"Zoom: {int(zoom * 100)}%")
            
            # Restore scroll position for small documents too
            QTimer.singleShot(0, lambda: self._canvas.scroll_to_page(current_page))
    
    def _render_zoom_async(self, current_page: int, zoom: float) -> None:
        """
        Render pages at new zoom level asynchronously.
        For very large documents, uses lazy rendering even in async mode.
        
        Args:
            current_page: Page number to scroll back to after rendering
            zoom: Zoom level to render at
        """
        page_count = self._document.get_page_count()
        
        # For very large documents, skip progress dialog and use lazy rendering
        if page_count > 200:
            # Use synchronous lazy rendering - it's fast enough
            self._render_zoom_sync(current_page, zoom)
            return
        
        # For moderately large documents (100-200 pages), use threaded rendering
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
        
        # Update canvas zoom level
        self._canvas.set_zoom_level(zoom)
        
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
    
    def _focus_search(self) -> None:
        """Focus the search panel and expand if collapsed."""
        if not self._document.is_open():
            return
        
        # Expand sidebar if collapsed
        if self._left_panel.is_collapsed():
            self._left_panel.toggle_collapse()
        
        # Expand search section if collapsed
        if not self._search_section.is_expanded():
            self._search_section.set_expanded(True)
        
        # Focus search input
        self._search_panel.focus_search_input()
    
    def _on_search_requested(self, search_text: str, case_sensitive: bool) -> None:
        """
        Handle search request from search panel.
        
        Args:
            search_text: Text to search for
            case_sensitive: Whether search is case-sensitive
        """
        if not self._document.is_open() or not search_text:
            return
        
        # Execute search with debouncing
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(SEARCH_DEBOUNCE_DELAY)
    
    def _on_search_result_selected(self, page_num: int, match_idx: int) -> None:
        """
        Handle selection of a search result from the results list.
        
        Args:
            page_num: Page number of the selected result
            match_idx: Match index on the page
        """
        # Find the match in results and navigate to it
        results = self._search_results.get_page_results(page_num)
        if match_idx < len(results):
            # Update current match to the selected one
            # We need to find the global match index
            pages_with_matches = self._search_results.get_pages_with_matches()
            global_idx = 0
            for p in pages_with_matches:
                if p == page_num:
                    global_idx += match_idx
                    break
                global_idx += len(self._search_results.get_page_results(p))
            
            # Navigate to this match
            self._search_results._current_match_index = global_idx
            self._update_search_highlights()
            self._jump_to_current_match()
            self._update_match_counter()
    
    def _execute_search(self) -> None:
        """Execute the text search operation in background thread."""
        search_text = self._search_panel.get_search_text()
        
        if not search_text or not self._document.is_open():
            return
        
        # Cancel any ongoing search
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.wait()
        
        # Clear previous results
        self._search_results.clear()
        self._canvas.clear_search_highlights()
        
        # Create and configure search worker
        self._search_worker = TextSearchWorker(
            self._document._backend,
            search_text,
            self._document.get_current_page(),
            self._search_panel.is_case_sensitive()
        )
        
        # Connect signals
        self._search_worker.search_progress.connect(self._on_search_progress)
        self._search_worker.match_found.connect(self._on_match_found)
        self._search_worker.search_completed.connect(self._on_search_completed)
        self._search_worker.search_failed.connect(self._on_search_failed)
        self._search_worker.search_cancelled.connect(self._on_search_cancelled)
        
        # Show progress and start search
        self._search_panel.show_progress(True)
        self._search_panel.set_progress(0, 100)
        self._search_panel.set_match_counter("Searching...")
        self._status_bar.showMessage(f"Searching for '{search_text}'...")
        
        # Start search in background
        self._search_worker.start()
    
    def _on_search_progress(self, current_page: int, total_pages: int) -> None:
        """
        Handle search progress updates.
        
        Args:
            current_page: Current page being searched (1-indexed for display)
            total_pages: Total number of pages
        """
        self._search_panel.set_progress(current_page, total_pages)
    
    def _on_match_found(self, page_number: int, matches: list) -> None:
        """
        Handle matches found on a page during search.
        
        Args:
            page_number: Page number where matches were found (0-indexed)
            matches: List of QRectF objects for match locations
        """
        # Add results to manager
        self._search_results.add_page_results(page_number, matches)
        
        # Update match counter
        total_matches = self._search_results.get_total_matches()
        self._search_panel.set_match_counter(f"{total_matches} match{'es' if total_matches != 1 else ''}")
        
        # If this is the first match, jump to it and show highlights
        if total_matches == 1:
            self._update_search_highlights()
            self._jump_to_current_match()
            self._update_results_list()
    
    def _on_search_completed(self, total_matches: int) -> None:
        """
        Handle search completion.
        
        Args:
            total_matches: Total number of matches found
        """
        # Hide progress
        self._search_panel.show_progress(False)
        
        # Update UI based on results
        if total_matches > 0:
            self._search_panel.set_match_counter(f"{total_matches} match{'es' if total_matches != 1 else ''}")
            self._search_panel.enable_navigation(True)
            self._status_bar.showMessage(f"Found {total_matches} match{'es' if total_matches != 1 else ''}")
            
            # Update results list and highlights
            self._update_search_highlights()
            self._update_results_list()
        else:
            self._search_panel.set_match_counter("No matches found")
            self._search_panel.enable_navigation(False)
            self._status_bar.showMessage("No matches found")
            self._search_panel.clear_results()
    
    def _on_search_failed(self, error_message: str) -> None:
        """
        Handle search failure.
        
        Args:
            error_message: Error description
        """
        self._search_panel.show_progress(False)
        self._search_panel.set_match_counter("Search failed")
        self._status_bar.showMessage(f"Search failed: {error_message}")
    
    def _on_search_cancelled(self) -> None:
        """Handle search cancellation."""
        self._search_panel.show_progress(False)
        
        # Show results found so far
        total_matches = self._search_results.get_total_matches()
        if total_matches > 0:
            self._search_panel.set_match_counter(f"{total_matches} match{'es' if total_matches != 1 else ''} (partial)")
            self._search_panel.enable_navigation(True)
            self._update_search_highlights()
            self._update_results_list()
        else:
            self._search_panel.set_match_counter("Search cancelled")
        
        self._status_bar.showMessage("Search cancelled")
    
    def _find_next(self) -> None:
        """Navigate to the next search match."""
        if not self._search_results.has_results():
            return
        
        match_info = self._search_results.go_to_next_match()
        if match_info:
            self._update_search_highlights()
            self._jump_to_current_match()
            
            # Update match counter with current position
            page_num, rect, match_num = match_info
            total = self._search_results.get_total_matches()
            self._search_panel.set_match_counter(f"{match_num} of {total}")
            self._update_results_list()
    
    def _find_previous(self) -> None:
        """Navigate to the previous search match."""
        if not self._search_results.has_results():
            return
        
        match_info = self._search_results.go_to_previous_match()
        if match_info:
            self._update_search_highlights()
            self._jump_to_current_match()
            
            # Update match counter with current position
            page_num, rect, match_num = match_info
            total = self._search_results.get_total_matches()
            self._search_panel.set_match_counter(f"{match_num} of {total}")
            self._update_results_list()
    
    def _update_search_highlights(self) -> None:
        """Update search highlights on the canvas."""
        if not self._search_results.has_results():
            return
        
        # Get current match info
        current_match = None
        match_info = self._search_results.get_current_match_info()
        if match_info:
            page_num, rect, _ = match_info
            current_match = (page_num, rect)
        
        # Build highlights dictionary
        highlights = {}
        for page_num in self._search_results.get_pages_with_matches():
            highlights[page_num] = self._search_results.get_page_results(page_num)
        
        # Update canvas with highlights
        zoom_level = self._document.get_zoom_level()
        self._canvas.set_search_highlights(highlights, current_match, zoom_level)
    
    def _update_results_list(self) -> None:
        """Update the search results list in the search panel."""
        if not self._search_results.has_results():
            return
        
        # Get current match info
        current_match_info = None
        match_info = self._search_results.get_current_match_info()
        if match_info:
            page_num, rect, _ = match_info
            # Find the match index on this page
            page_results = self._search_results.get_page_results(page_num)
            match_idx = page_results.index(rect) if rect in page_results else 0
            current_match_info = (page_num, match_idx)
        
        # Build results list with context
        results_with_context = []
        for page_num in self._search_results.get_pages_with_matches():
            page_results = self._search_results.get_page_results(page_num)
            # Get page text for context
            page_text = self._document._backend.get_page_text(page_num)
            
            for idx, rect in enumerate(page_results):
                # Extract context around the match (simplified - just show page number)
                # In a real implementation, we'd extract text around the rect coordinates
                context = f"Match on page {page_num + 1}"
                if page_text:
                    # Simple context extraction (first 50 chars of page text)
                    context = page_text[:50].replace('\n', ' ').strip() + "..."
                
                results_with_context.append((page_num, idx, context))
        
        # Update the results list
        self._search_panel.update_results_list(results_with_context, current_match_info)
    
    def _update_match_counter(self) -> None:
        """Update the match counter display."""
        if not self._search_results.has_results():
            self._search_panel.set_match_counter("No matches")
            return
        
        match_info = self._search_results.get_current_match_info()
        if match_info:
            _, _, match_num = match_info
            total = self._search_results.get_total_matches()
            self._search_panel.set_match_counter(f"{match_num} of {total}")
    
    def _jump_to_current_match(self) -> None:
        """Scroll to and highlight the current search match."""
        match_info = self._search_results.get_current_match_info()
        if not match_info:
            return
        
        page_num, rect, _ = match_info
        
        # Navigate to the page containing the match
        if self._document.set_current_page(page_num):
            self._canvas.scroll_to_page(page_num)
            self._update_navigation_controls()
    
    def _on_text_selected(self, selected_text: str) -> None:
        """
        Handle text selection signal from canvas.
        
        Args:
            selected_text: The selected text or special command
        """
        print(f"[DEBUG] _on_text_selected called with: {selected_text}")
        
        # Handle word selection request from double-click
        if selected_text == "WORD_SELECTION_REQUEST":
            print("[DEBUG] Processing word selection request")
            # Automatically perform word selection
            self._copy_selected_text()
    
    def _on_zoom_requested(self, zoom_in: bool) -> None:
        """
        Handle zoom request from canvas (Ctrl/Cmd + Mouse wheel).
        
        Args:
            zoom_in: True to zoom in, False to zoom out
        """
        if zoom_in:
            self._zoom_in()
        else:
            self._zoom_out()
    
    def _copy_selected_text(self) -> None:
        """Copy currently selected text to clipboard."""
        print("\n[COPY DEBUG] _copy_selected_text called")
        
        if not self._document.is_open():
            print("[COPY DEBUG] No document open")
            return
        
        # Get selection info from canvas
        selection_info = self._canvas.get_selection_info()
        if not selection_info:
            print("[COPY DEBUG] No selection info from canvas")
            return
        
        page_num, selection_rect = selection_info
        print(f"[COPY DEBUG] Selection on page {page_num}, rect: {selection_rect}")
        print(f"[COPY DEBUG] Rect dimensions: width={selection_rect.width():.2f}, height={selection_rect.height():.2f}")
        
        # Get text words from the selected page
        words = self._document._backend.get_text_words(page_num)
        if not words:
            print("[COPY DEBUG] No words on page")
            return
        
        print(f"[COPY DEBUG] Got {len(words)} words from page")
        
        # Check if selection rect is small (indicates smart selection from double/triple click)
        # vs large (indicates drag selection)
        is_smart_selection = (selection_rect.width() <= 10 and selection_rect.height() <= 10)
        print(f"[COPY DEBUG] Is smart selection: {is_smart_selection}")
        
        if is_smart_selection:
            # Smart selection (double or triple click) - determine which by checking line
            print("[COPY DEBUG] Using smart selection path (word/line)")
            # First try word selection
            word_text = self._select_word_at_rect(words, selection_rect, page_num)
            if word_text:
                print(f"[COPY DEBUG] Selected word: '{word_text}'")
                selected_text = word_text
            else:
                # If no word found, try line selection
                print("[COPY DEBUG] No word found, trying line selection")
                selected_text = self._select_line_at_rect(words, selection_rect, page_num)
        else:
            # Normal drag selection
            print("[COPY DEBUG] Using drag selection path")
            selected_text = self._extract_text_from_selection(words, selection_rect)
        
        print(f"[COPY DEBUG] Final selected text: '{selected_text}' (len={len(selected_text)})")
        
        if selected_text:
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)
            
            # Show feedback
            self._status_bar.showMessage(f"Copied {len(selected_text)} characters to clipboard", 2000)
            print(f"[COPY DEBUG] Copied to clipboard successfully\n")
        else:
            print("[COPY DEBUG] No text selected, nothing copied\n")
    
    def _calculate_avg_char_width(self, words: list) -> float:
        """
        Calculate average character width from a list of words.
        Uses dynamic calculation based on actual word dimensions.
        
        Args:
            words: List of (x0, y0, x1, y1, word_text) tuples
            
        Returns:
            Average character width in PDF coordinates
        """
        if not words:
            return 5.0  # Default fallback
        
        total_width = 0
        total_chars = 0
        
        for x0, y0, x1, y1, text in words:
            word_width = x1 - x0
            # Count actual characters (excluding zero-width joiners, combining marks)
            char_count = len([c for c in text if unicodedata.category(c) not in ('Mn', 'Cf')])
            if char_count > 0:
                total_width += word_width
                total_chars += char_count
        
        if total_chars > 0:
            return total_width / total_chars
        return 5.0  # Fallback
    
    def _is_unicode_word_boundary(self, prev_word: str, curr_word: str) -> bool:
        """
        Check if there should be a word boundary between two words using Unicode properties.
        Handles complex scripts (Devanagari, Arabic, etc.) correctly.
        
        Args:
            prev_word: Previous word text
            curr_word: Current word text
            
        Returns:
            True if a space should be added between words
        """
        if not prev_word or not curr_word:
            return False
        
        # Get last char of previous word and first char of current word
        last_char = prev_word[-1]
        first_char = curr_word[0]
        
        # Check for script-specific joining behavior
        last_cat = unicodedata.category(last_char)
        first_cat = unicodedata.category(first_char)
        
        # Combining marks should not have space before them
        if first_cat in ('Mn', 'Mc', 'Me'):
            return False
        
        # Format characters (zero-width joiners, etc.) should not add space
        if last_cat == 'Cf' or first_cat == 'Cf':
            return False
        
        # Check for Devanagari/Bengali virama (halant) - word continues
        if ord(last_char) in (0x094D, 0x09CD, 0x0A4D, 0x0ACD, 0x0B4D, 0x0BCD):
            return False
        
        # Check for Arabic joining characters
        if 0x0600 <= ord(last_char) <= 0x06FF or 0x0600 <= ord(first_char) <= 0x06FF:
            # Arabic has complex joining rules, be conservative
            return True
        
        # Default: add space between words
        return True
    
    def _extract_text_from_selection(self, words: list, selection_rect) -> str:
        """
        Extract text from words that intersect with selection rectangle.
        Uses Unicode-aware spacing with character-width-based detection.
        
        Args:
            words: List of (x0, y0, x1, y1, word_text) tuples
            selection_rect: Selection rectangle in PDF coordinates
            
        Returns:
            Extracted text string with proper spacing for all languages
        """
        if not words or not selection_rect:
            return ""
        
        print("\n" + "="*80)
        print("[BENGALI DEBUG] Starting text extraction")
        print(f"[BENGALI DEBUG] Total words on page: {len(words)}")
        
        # Find words that intersect with selection
        selected_words = []
        for x0, y0, x1, y1, text in words:
            # Check if word intersects with selection
            sel_left = selection_rect.left()
            sel_right = selection_rect.right()
            sel_top = selection_rect.top()
            sel_bottom = selection_rect.bottom()
            
            # Check intersection
            if (x0 < sel_right and x1 > sel_left and
                y0 < sel_bottom and y1 > sel_top):
                selected_words.append((x0, y0, x1, y1, text))
                print(f"[BENGALI DEBUG] Selected word: '{text}' | Bounds: ({x0:.2f}, {y0:.2f}) -> ({x1:.2f}, {y1:.2f}) | Width: {x1-x0:.2f}")
        
        if not selected_words:
            print("[BENGALI DEBUG] No words selected")
            return ""
        
        print(f"\n[BENGALI DEBUG] Total selected words: {len(selected_words)}")
        
        # Calculate average character width for dynamic spacing threshold
        avg_char_width = self._calculate_avg_char_width(selected_words)
        print(f"[BENGALI DEBUG] Average character width: {avg_char_width:.2f}")
        
        # Use character-width-based threshold instead of fixed 2 pixels
        # Typically, word spacing is 0.5-1.0x the character width
        space_threshold = avg_char_width * 0.6
        print(f"[BENGALI DEBUG] Space threshold (60% of avg): {space_threshold:.2f}")
        
        # Sort words by position (top-to-bottom, left-to-right)
        # Use rounded Y values to group words on same line
        selected_words.sort(key=lambda w: (round(w[1]), w[0]))
        
        # Combine words into text with proper spacing
        text_parts = []
        prev_y_mid = None
        prev_x_end = None
        prev_word = None
        
        print("\n[BENGALI DEBUG] Processing words for spacing:")
        for i, (x0, y0, x1, y1, word) in enumerate(selected_words):
            # Calculate word center Y and height
            y_mid = (y0 + y1) / 2
            word_height = y1 - y0
            
            # Determine if this is a new line
            # Use word height as threshold (more reliable than fixed points)
            is_new_line = (prev_y_mid is not None and 
                          abs(y_mid - prev_y_mid) > word_height * 0.3)
            
            if is_new_line:
                # New line detected
                print(f"  [{i}] '{word}' -> NEW LINE (Y diff: {abs(y_mid - prev_y_mid):.2f})")
                text_parts.append('\n')
            elif prev_x_end is not None and prev_word is not None:
                # Same line - check if there's a gap between words
                gap = x0 - prev_x_end
                
                # Check both pixel gap AND Unicode word boundaries
                unicode_boundary = self._is_unicode_word_boundary(prev_word, word)
                needs_space = gap > space_threshold or unicode_boundary
                
                print(f"  [{i}] '{word}' | Gap: {gap:.2f}px | Unicode boundary: {unicode_boundary} | Add space: {needs_space}")
                
                # Debug Unicode properties
                if word:
                    first_char = word[0]
                    print(f"       First char: '{first_char}' (U+{ord(first_char):04X}) Category: {unicodedata.category(first_char)} Name: {unicodedata.name(first_char, 'UNKNOWN')}")
                if prev_word:
                    last_char = prev_word[-1]
                    print(f"       Prev last char: '{last_char}' (U+{ord(last_char):04X}) Category: {unicodedata.category(last_char)} Name: {unicodedata.name(last_char, 'UNKNOWN')}")
                
                if needs_space:
                    text_parts.append(' ')
            else:
                print(f"  [{i}] '{word}' -> FIRST WORD")
            
            text_parts.append(word)
            prev_y_mid = y_mid
            prev_x_end = x1
            prev_word = word
        
        result = ''.join(text_parts)
        print(f"\n[BENGALI DEBUG] Final text: '{result}'")
        print(f"[BENGALI DEBUG] Text length: {len(result)} characters")
        print("="*80 + "\n")
        
        return result
    
    def _select_word_at_rect(self, words: list, click_rect, page_num: int) -> str:
        """
        Find and select the word at the click point.
        
        Args:
            words: List of (x0, y0, x1, y1, word_text) tuples
            click_rect: Small rectangle around click point
            page_num: Page number
            
        Returns:
            Selected word text
        """
        # Find word that intersects with click rect
        click_x = click_rect.center().x()
        click_y = click_rect.center().y()
        
        for x0, y0, x1, y1, word_text in words:
            # Check if click point is within word bounds
            if x0 <= click_x <= x1 and y0 <= click_y <= y1:
                # Found the word - create selection rect for it
                word_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
                self._canvas.set_selection_rect(word_rect)
                return word_text
        
        return ""
    
    def _select_line_at_rect(self, words: list, click_rect, page_num: int) -> str:
        """
        Find and select all words on the same line as the click point.
        Uses Unicode-aware spacing for multi-language support.
        
        Args:
            words: List of (x0, y0, x1, y1, word_text) tuples
            click_rect: Small rectangle around click point
            page_num: Page number
            
        Returns:
            Selected line text with proper spacing
        """
        # Find the word at click point first
        click_y = click_rect.center().y()
        
        # Find all words on the same line (similar Y coordinate)
        line_words = []
        for x0, y0, x1, y1, word_text in words:
            y_mid = (y0 + y1) / 2
            # If word's Y coordinate is close to click Y, it's on same line
            if abs(y_mid - click_y) < (y1 - y0):  # Within one word height
                line_words.append((x0, y0, x1, y1, word_text))
        
        if not line_words:
            return ""
        
        # Sort words left to right
        line_words.sort(key=lambda w: w[0])
        
        # Find bounding box of all words on line
        min_x = min(w[0] for w in line_words)
        min_y = min(w[1] for w in line_words)
        max_x = max(w[2] for w in line_words)
        max_y = max(w[3] for w in line_words)
        
        # Create selection rect for entire line
        line_rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        self._canvas.set_selection_rect(line_rect)
        
        # Calculate character width for this line
        avg_char_width = self._calculate_avg_char_width(line_words)
        space_threshold = avg_char_width * 0.6
        
        # Extract text from line words with Unicode-aware spacing
        text_parts = []
        prev_x_end = None
        prev_word = None
        
        for x0, y0, x1, y1, word in line_words:
            if prev_x_end is not None and prev_word is not None:
                gap = x0 - prev_x_end
                
                # Check both pixel gap AND Unicode word boundaries
                needs_space = (
                    gap > space_threshold or 
                    self._is_unicode_word_boundary(prev_word, word)
                )
                
                if needs_space:
                    text_parts.append(' ')
            
            text_parts.append(word)
            prev_x_end = x1
            prev_word = word
        
        return ''.join(text_parts)
    
    def _clear_selection(self) -> None:
        """Clear the current text selection."""
        self._canvas.clear_selection()
        self._status_bar.showMessage("Selection cleared", 1000)
    
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
        
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.wait()
        
        event.accept()
