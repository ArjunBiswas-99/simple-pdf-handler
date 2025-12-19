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
    QSplitter, QApplication, QVBoxLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QAction, QKeySequence, QPixmap, QCloseEvent
from ui.pdf_canvas import PDFCanvas
from ui.progress_dialog import ProgressDialog
from ui.app_bar import AppBar
from ui.mode_tabs import ModeTabs
from ui.toolbars.view_toolbar import ViewToolbar
from ui.sidebar.left_sidebar import LeftSidebar
from ui.sidebar.panels.pages_panel import PagesPanel
from ui.sidebar.panels.bookmarks_panel import BookmarksPanel
from ui.sidebar.panels.search_panel import SearchPanel as SidebarSearchPanel
from ui.sidebar.panels.attachments_panel import AttachmentsPanel
from ui.sidebar.panels.edit_tools_panel import EditToolsPanel
from ui.sidebar.right_sidebar import RightSidebar
from ui.right_panel import DocumentPropertiesPanel
from ui.widgets import InlineTextEditor, TextFormatToolbar
from ui.styles.design_tokens import AppMode, SidebarMode, SIZING
from core.pdf_document import PDFDocument
from core.pdf_loader_worker import PDFLoaderWorker
from core.zoom_render_worker import ZoomRenderWorker
from core.text_search_worker import TextSearchWorker
from core.thumbnail_render_worker import ThumbnailRenderWorker
from core.search_results_manager import SearchResultsManager
from ui.styles.theme_manager import get_theme_manager
from ui.styles.themes import ThemeType
from ui.styles.professional_styles import ProfessionalStyles
from ui.styles.enhanced_styles import EnhancedStyles
from utils.constants import (
    ZOOM_LEVELS, ZOOM_LEVEL_LABELS, DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM,
    ZOOM_INCREMENT, LARGE_FILE_THRESHOLD, LARGE_DOCUMENT_PAGE_THRESHOLD,
    SEARCH_DEBOUNCE_DELAY, ViewMode
)
from utils.settings_manager import get_settings_manager


class MainWindow(QMainWindow):
    """
    Main application window.
    Manages the user interface and coordinates between components.
    """
    
    # File size threshold for using threaded loading (5MB)
    # Lowered from 10MB to ensure better responsiveness for larger files
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self._document = PDFDocument()
        self._loader_worker = None
        self._zoom_worker = None
        self._thumbnail_worker = None
        
        # Undo/Redo manager
        from core.undo_manager import UndoManager
        self._undo_manager = UndoManager()
        
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
        
        # Connect document state changes to window title updates
        self._document.document_state_changed.connect(self._on_document_state_changed)
    
    def _setup_ui(self) -> None:
        """Configure the main window layout and components."""
        self.setWindowTitle("Simple PDF Handler")
        self.setMinimumSize(1000, 700)
        
        # Apply modern polish styles (MS Word-inspired)
        from ui.styles.modern_polish_styles import ModernPolishStyles
        base_styles = ProfessionalStyles.get_complete_stylesheet()
        enhanced_styles = EnhancedStyles.get_complete_enhanced_stylesheet()
        modern_styles = ModernPolishStyles.get_complete_modern_stylesheet()
        self.setStyleSheet(base_styles + "\n" + enhanced_styles + "\n" + modern_styles)
        
        # Create main container widget with vertical layout
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_container.setLayout(main_layout)
        
        # Create AppBar (replaces menu bar)
        self._app_bar = AppBar()
        self._app_bar.theme_toggle_clicked.connect(self._on_toggle_theme)
        self._app_bar.help_clicked.connect(self._on_about)
        main_layout.addWidget(self._app_bar)
        
        # Create ModeTabs
        self._mode_tabs = ModeTabs()
        self._mode_tabs.mode_changed.connect(self._on_mode_changed)
        main_layout.addWidget(self._mode_tabs)
        
        # Create View Toolbar (context toolbar for View mode)
        self._view_toolbar = ViewToolbar()
        self._connect_view_toolbar_signals()
        
        # Wrap toolbar in scroll area for horizontal scrolling at narrow widths
        toolbar_scroll = QScrollArea()
        toolbar_scroll.setWidget(self._view_toolbar)
        toolbar_scroll.setWidgetResizable(True)
        toolbar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        toolbar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        toolbar_scroll.setMaximumHeight(SIZING['toolbar_height'] + 10)
        toolbar_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        main_layout.addWidget(toolbar_scroll)
        
        # Create main content area with sidebar and canvas
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create NEW sidebar with panels
        self._new_sidebar = LeftSidebar()
        self._setup_sidebar_panels()
        
        # Connect sidebar collapse/expand signals
        self._new_sidebar.collapsed.connect(self._on_sidebar_collapsed)
        self._new_sidebar.expanded.connect(self._on_sidebar_expanded)
        
        self._main_splitter.addWidget(self._new_sidebar)
        
        # Create PDF canvas
        self._canvas = PDFCanvas()
        self._canvas.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._canvas.text_selected.connect(self._on_text_selected)
        self._canvas.zoom_requested.connect(self._on_zoom_requested)
        self._canvas.image_selected.connect(self._on_image_selected)
        self._canvas.shape_drawn.connect(self._on_shape_drawn)
        self._main_splitter.addWidget(self._canvas)
        
        # Create Right Sidebar (mirrors left sidebar)
        self._right_sidebar = RightSidebar()
        self._setup_right_sidebar_panels()
        
        # Connect right sidebar signals
        self._right_sidebar.collapsed.connect(self._on_right_sidebar_collapsed)
        self._right_sidebar.expanded.connect(self._on_right_sidebar_expanded)
        
        self._main_splitter.addWidget(self._right_sidebar)
        
        # Set splitter properties
        self._main_splitter.setStretchFactor(0, 0)  # Left sidebar doesn't stretch
        self._main_splitter.setStretchFactor(1, 1)  # Canvas stretches
        self._main_splitter.setStretchFactor(2, 0)  # Right sidebar doesn't stretch
        self._main_splitter.setSizes([280, 980, 48])  # Initial sizes (right sidebar collapsed to icon rail)
        
        # Add splitter to main layout
        main_layout.addWidget(self._main_splitter)
        
        # Set main container as central widget
        self.setCentralWidget(main_container)
        
        # Create status bar
        self._create_status_bar()
        
        # Create progress dialog
        self._progress_dialog = ProgressDialog(self)
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
    
    def _create_status_bar(self) -> None:
        """Create and configure the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")
    
    def _connect_view_toolbar_signals(self) -> None:
        """Connect View Toolbar signals to MainWindow handlers."""
        # File operations
        self._view_toolbar.open_file.connect(self._on_open_file)
        self._view_toolbar.save_file.connect(self._on_save)
        
        # Navigation
        self._view_toolbar.first_page.connect(self._go_to_first_page)
        self._view_toolbar.previous_page.connect(self._go_to_previous_page)
        self._view_toolbar.next_page.connect(self._go_to_next_page)
        self._view_toolbar.last_page.connect(self._go_to_last_page)
        self._view_toolbar.page_changed.connect(self._on_toolbar_page_changed)
        
        # Zoom
        self._view_toolbar.zoom_in.connect(self._zoom_in)
        self._view_toolbar.zoom_out.connect(self._zoom_out)
        self._view_toolbar.zoom_changed.connect(self._on_toolbar_zoom_changed)
        self._view_toolbar.fit_width.connect(self._fit_width)
        self._view_toolbar.fit_page.connect(self._fit_page)
    
    def _on_toolbar_page_changed(self, page_num: int) -> None:
        """
        Handle page change from toolbar input.
        
        Args:
            page_num: Page number (1-indexed from user input)
        """
        if not self._document.is_open():
            return
        
        # Convert to 0-indexed
        page_index = page_num - 1
        
        if self._document.set_current_page(page_index):
            self._canvas.scroll_to_page(page_index)
            self._update_navigation_controls()
            self._update_view_toolbar_state()
            self._update_pages_panel_selection()
    
    def _on_toolbar_zoom_changed(self, text: str) -> None:
        """
        Handle zoom level change from toolbar.
        
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
    
    def _update_view_toolbar_state(self) -> None:
        """Update View Toolbar state based on current document."""
        if not self._document.is_open():
            # Disable toolbar controls
            self._view_toolbar.set_navigation_enabled(False)
            self._view_toolbar.set_navigation_buttons_state(False, False)
            self._view_toolbar.set_zoom_enabled(False)
            self._view_toolbar.set_layout_mode_enabled(False)
            self._view_toolbar.set_page_info(0, 0)
            return
        
        current_page = self._document.get_current_page()
        page_count = self._document.get_page_count()
        
        # Update page info
        self._view_toolbar.set_page_info(current_page, page_count)
        
        # Enable navigation
        self._view_toolbar.set_navigation_enabled(True)
        
        # Update navigation buttons
        can_go_prev = current_page > 0
        can_go_next = current_page < page_count - 1
        self._view_toolbar.set_navigation_buttons_state(can_go_prev, can_go_next)
        
        # Enable zoom controls
        self._view_toolbar.set_zoom_enabled(True)
        
        # Enable layout mode buttons
        self._view_toolbar.set_layout_mode_enabled(True)
        
        # Update zoom display
        zoom = self._document.get_zoom_level()
        zoom_text = f"{int(zoom * 100)}%"
        self._view_toolbar.set_zoom_level(zoom_text)
    
    def _setup_sidebar_panels(self) -> None:
        """Set up all sidebar panels."""
        # Create panels
        pages_panel = PagesPanel()
        bookmarks_panel = BookmarksPanel()
        search_panel = SidebarSearchPanel()
        attachments_panel = AttachmentsPanel()
        
        # Connect pages panel signals
        pages_panel.page_clicked.connect(self._on_page_thumbnail_clicked)
        pages_panel.delete_page_requested.connect(self._on_delete_page_requested)
        pages_panel.insert_page_requested.connect(self._on_insert_page_requested)
        pages_panel.move_page_requested.connect(self._on_move_page_requested)
        
        # Connect search panel signals
        search_panel.search_requested.connect(self._on_search_requested)
        search_panel.next_match_requested.connect(self._find_next)
        search_panel.previous_match_requested.connect(self._find_previous)
        search_panel.result_selected.connect(self._on_search_result_selected)
        
        # Connect bookmarks panel signals
        bookmarks_panel.bookmark_clicked.connect(self._on_bookmark_clicked)
        
        # Connect layout mode signals from toolbar
        self._view_toolbar.single_page.connect(self._set_single_page_mode)
        self._view_toolbar.continuous_page.connect(self._set_continuous_mode)
        self._view_toolbar.facing_page.connect(self._set_facing_pages_mode)
        
        # Store references to panels for updates
        self._pages_panel = pages_panel
        self._sidebar_search_panel = search_panel
        self._bookmarks_panel = bookmarks_panel
        
        # Add panels to sidebar
        self._new_sidebar.add_panel(SidebarMode.PAGES, pages_panel)
        self._new_sidebar.add_panel(SidebarMode.BOOKMARKS, bookmarks_panel)
        self._new_sidebar.add_panel(SidebarMode.SEARCH, search_panel)
        self._new_sidebar.add_panel(SidebarMode.ATTACHMENTS, attachments_panel)
    
    def _setup_right_sidebar_panels(self) -> None:
        """Set up right sidebar panels."""
        # Create document properties panel
        doc_props_panel = DocumentPropertiesPanel()
        
        # Create edit tools panel
        edit_tools_panel = EditToolsPanel()
        
        # Store reference FIRST before connecting signals
        self._edit_tools_panel = edit_tools_panel
        
        # Connect edit tools signals
        edit_tools_panel.add_text_clicked.connect(self._on_add_text)
        edit_tools_panel.add_image_clicked.connect(self._on_add_image)
        edit_tools_panel.add_blank_page_clicked.connect(self._on_add_blank_page)
        edit_tools_panel.attach_file_clicked.connect(self._on_attach_file)
        edit_tools_panel.edit_text_clicked.connect(self._on_edit_text)
        edit_tools_panel.undo_clicked.connect(self._on_undo)
        edit_tools_panel.redo_clicked.connect(self._on_redo)
        edit_tools_panel.edit_pages_toggled.connect(self._on_edit_pages_toggled)
        
        # Connect shape drawing toolbar
        shape_toolbar = edit_tools_panel.get_shape_toolbar()
        shape_toolbar.drawing_started.connect(self._on_shape_drawing_started)
        
        # Connect canvas shape_drawn signal (note: canvas is created later in _setup_ui)
        # This connection will be made after canvas is created
        
        # Connect undo manager signals - CRITICAL: This enables/disables buttons
        self._undo_manager.can_undo_changed.connect(edit_tools_panel.set_undo_enabled)
        self._undo_manager.can_redo_changed.connect(edit_tools_panel.set_redo_enabled)
        
        # Also manually check initial state and enable if needed
        if self._undo_manager.can_undo():
            edit_tools_panel.set_undo_enabled(True)
        if self._undo_manager.can_redo():
            edit_tools_panel.set_redo_enabled(True)
        
        # Store references for updates
        self._doc_props_panel = doc_props_panel
        
        # Add to right sidebar
        # Panel index 0 = Properties
        # Panel index 1 = Edit Tools
        self._right_sidebar.add_panel(0, doc_props_panel)
        self._right_sidebar.add_panel(1, edit_tools_panel)
    
    def _on_mode_changed(self, mode: AppMode) -> None:
        """
        Handle mode change from ModeTabs.
        
        Args:
            mode: The new active mode
        """
        self._status_bar.showMessage(f"Switched to {mode.value} mode", 2000)
        
        # Switch behavior based on mode
        if mode == AppMode.EDIT:
            # Switch to Edit mode
            self._enter_edit_mode()
        else:
            # Switch back to View mode (or other modes)
            self._exit_edit_mode()
    
    def _enter_edit_mode(self) -> None:
        """
        Enter Edit mode.
        Shows Edit Tools panel and prepares canvas for editing.
        """
        if not self._document.is_open():
            self._status_bar.showMessage("Please open a PDF file first", 3000)
            # Switch back to View mode
            self._mode_tabs.set_mode(AppMode.VIEW)
            return
        
        # Switch right sidebar to Edit Tools panel (index 1)
        self._right_sidebar.set_active_panel(1)
        
        # Enable edit tools (document is open)
        if hasattr(self, '_edit_tools_panel'):
            self._edit_tools_panel.set_tools_enabled(True)
        
        self._status_bar.showMessage("Edit mode active - Use right panel tools to edit PDF", 3000)
    
    def _disable_edit_tools(self) -> None:
        """Disable all edit tools when no document is open."""
        if hasattr(self, '_edit_tools_panel'):
            self._edit_tools_panel.set_tools_enabled(False)
    
    def _exit_edit_mode(self) -> None:
        """
        Exit Edit mode.
        Returns to Properties panel.
        """
        # Switch right sidebar back to Properties panel (index 0)
        self._right_sidebar.set_active_panel(0)
        
        self._status_bar.showMessage("Edit mode exited", 2000)
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts for navigation and search."""
        # File operations shortcuts (since menu bar is hidden)
        open_shortcut = QAction(self)
        open_shortcut.setShortcut(QKeySequence("Ctrl+O"))
        open_shortcut.triggered.connect(self._on_open_file)
        self.addAction(open_shortcut)
        
        close_shortcut = QAction(self)
        close_shortcut.setShortcut(QKeySequence("Ctrl+W"))
        close_shortcut.triggered.connect(self._on_close_document)
        self.addAction(close_shortcut)
        
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
        
        # Text selection shortcuts
        copy_shortcut = QAction(self)
        copy_shortcut.setShortcut(QKeySequence("Ctrl+C"))
        copy_shortcut.triggered.connect(self._copy_selected_text)
        self.addAction(copy_shortcut)
        
        escape_shortcut = QAction(self)
        escape_shortcut.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        escape_shortcut.triggered.connect(self._clear_selection)
        self.addAction(escape_shortcut)
        
        # Save shortcut
        save_shortcut = QAction(self)
        save_shortcut.setShortcut(QKeySequence("Ctrl+S"))
        save_shortcut.triggered.connect(self._on_save)
        self.addAction(save_shortcut)
        
        # Undo shortcut (Ctrl+Z / Cmd+Z)
        undo_shortcut = QAction(self)
        undo_shortcut.setShortcut(QKeySequence("Ctrl+Z"))
        undo_shortcut.triggered.connect(self._on_undo)
        self.addAction(undo_shortcut)
        
        # Redo shortcut (Ctrl+Shift+Z / Cmd+Shift+Z)
        redo_shortcut = QAction(self)
        redo_shortcut.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        redo_shortcut.triggered.connect(self._on_redo)
        self.addAction(redo_shortcut)
    
    def _on_open_file(self) -> None:
        """Handle file open action."""
        # Check if current document has unsaved changes
        if self._document.is_open():
            state_manager = self._document.get_state_manager()
            
            if state_manager.is_dirty():
                # Document has unsaved changes - ask user
                file_path = self._document.get_file_path()
                file_name = os.path.basename(file_path) if file_path else "Untitled"
                
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"Do you want to save changes to \"{file_name}\" before opening a new file?",
                    QMessageBox.StandardButton.Save | 
                    QMessageBox.StandardButton.Discard | 
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    # Save current document first
                    self._on_save()
                elif reply == QMessageBox.StandardButton.Cancel:
                    # User cancelled - don't open new file
                    return
                # If Discard, continue with opening new file
        
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
        
        # Show immediate feedback in status bar
        self._status_bar.showMessage("Preparing to open PDF...")
        QApplication.processEvents()  # Force UI update
        
        # Check file size to decide loading strategy
        file_size = os.path.getsize(file_path)
        
        if file_size >= self.LARGE_FILE_THRESHOLD:
            # Large file - use threaded loading with immediate progress dialog
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
        # Show progress dialog IMMEDIATELY (before any heavy operations)
        size_mb = file_size / (1024 * 1024)
        file_name = os.path.basename(file_path)
        
        self._progress_dialog.reset()
        self._progress_dialog.set_status(f"Opening {file_name}...")
        self._progress_dialog.set_file_info(f"File size: {size_mb:.1f} MB")
        self._progress_dialog.show()
        
        # Force UI update to show dialog immediately
        QApplication.processEvents()
        
        # Create and configure worker thread
        self._loader_worker = PDFLoaderWorker(file_path)
        self._loader_worker.progress_updated.connect(self._progress_dialog.update_progress)
        self._loader_worker.loading_completed.connect(self._on_async_loading_completed)
        self._loader_worker.loading_failed.connect(self._on_async_loading_failed)
        
        # Start loading in background
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
        
        # Enable Save As button (document is now open)
        self._view_toolbar.set_save_as_enabled(True)
        
        # Update View Toolbar state
        self._update_view_toolbar_state()
        
        # Enable navigation and zoom controls (old toolbar - will be removed later)
        self._update_navigation_controls()
        self._enable_zoom_controls()
        
        # Reset zoom to 100%
        self._document.set_zoom_level(DEFAULT_ZOOM)
        if hasattr(self, '_zoom_combo'):
            self._zoom_combo.setCurrentText("100%")
        
        # Update canvas zoom level
        self._canvas.set_zoom_level(DEFAULT_ZOOM)
        
        # Update right panel with document properties
        self._update_right_panel()
        
        # Load bookmarks into sidebar
        self._load_bookmarks()
        
        # Reset Edit Pages mode to off when new document is loaded
        if hasattr(self, '_edit_tools_panel'):
            self._edit_tools_panel.exit_pages_edit_mode()
        if hasattr(self, '_pages_panel'):
            self._pages_panel.set_edit_mode(False)
        
        # Initialize pages panel with page count
        self._load_pages_panel()
        
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
            self._update_view_toolbar_state()
            self._disable_navigation_controls()
            self._disable_zoom_controls()
            
            # Disable Save/Save As buttons
            self._view_toolbar.set_save_enabled(False)
            self._view_toolbar.set_save_as_enabled(False)
            
            # Disable edit tools when no document is open
            self._disable_edit_tools()
            
            # Clear bookmarks
            if hasattr(self, '_bookmarks_panel'):
                self._bookmarks_panel.clear()
            
            # Clear pages panel
            if hasattr(self, '_pages_panel'):
                self._pages_panel.clear()
            
            self._status_bar.showMessage("Document closed")
    
    def _go_to_first_page(self) -> None:
        """Navigate to the first page of the document."""
        if not self._document.is_open():
            return
        
        if self._document.set_current_page(0):
            self._canvas.scroll_to_page(0)
            self._update_navigation_controls()
            self._update_pages_panel_selection()
    
    def _go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        if not self._document.is_open():
            return
        
        current = self._document.get_current_page()
        if current > 0:
            if self._document.set_current_page(current - 1):
                self._canvas.scroll_to_page(current - 1)
                self._update_navigation_controls()
                self._update_pages_panel_selection()
    
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
                self._update_pages_panel_selection()
    
    def _go_to_last_page(self) -> None:
        """Navigate to the last page of the document."""
        if not self._document.is_open():
            return
        
        last_page = self._document.get_page_count() - 1
        if self._document.set_current_page(last_page):
            self._canvas.scroll_to_page(last_page)
            self._update_navigation_controls()
            self._update_pages_panel_selection()
    
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
                self._update_pages_panel_selection()
            else:
                # Invalid page number, reset to current
                current = self._document.get_current_page()
                self._page_input.setText(str(current + 1))
        except ValueError:
            # Invalid input, reset to current page
            current = self._document.get_current_page()
            self._page_input.setText(str(current + 1))
    
    def _render_all_pages(self, preserve_page: bool = False) -> None:
        """
        Render and display all pages in continuous scrolling mode.
        
        Args:
            preserve_page: If True, scroll to current page instead of first page
        """
        page_count = self._document.get_page_count()
        current_page = self._document.get_current_page() if preserve_page else 0
        pixmaps = []
        
        self._status_bar.showMessage(f"Rendering {page_count} pages...")
        
        # Render all pages and load images for each page
        for page_num in range(page_count):
            pixmap = self._document.render_page(page_num)
            if pixmap:
                pixmaps.append(pixmap)
                # Load images for this page
                self._load_page_images(page_num)
            else:
                self._show_error(f"Failed to render page {page_num + 1}")
                return
        
        # Display all pages in continuous layout
        self._canvas.display_pages(pixmaps)
        
        # Scroll to appropriate page
        self._canvas.scroll_to_page(current_page)
    
    def _load_page_images(self, page_num: int) -> None:
        """
        Load and cache images for a specific page.
        
        Args:
            page_num: Page number (0-indexed)
        """
        # Get images from document
        images = self._document.get_page_images(page_num)
        
        # Pass to canvas for caching
        self._canvas.load_page_images(page_num, images)
    
    def _render_initial_pages_lazy(self, preserve_page: bool = False) -> None:
        """
        Render initial pages lazily for large documents to avoid UI freeze.
        Only renders first 20 pages, creates placeholders for rest.
        
        Args:
            preserve_page: If True, render around current page instead of starting from 0
        """
        page_count = self._document.get_page_count()
        zoom = self._document.get_zoom_level()
        current_page = self._document.get_current_page() if preserve_page else 0
        
        # Clear image cache for fresh render
        self._canvas.clear_page_images()
        
        # Render pages around current page (current ± 10 pages)
        window_size = 10
        render_start = max(0, current_page - window_size)
        render_end = min(page_count, current_page + window_size + 1)
        
        self._status_bar.showMessage(f"Rendering pages {render_start+1} to {render_end} of {page_count}...")
        
        # Track rendered pages
        self._rendered_pages.clear()
        for i in range(render_start, render_end):
            self._rendered_pages.add(i)
        
        pixmaps = []
        for page_num in range(page_count):
            if render_start <= page_num < render_end:
                # Render pages in window
                pixmap = self._document.render_page(page_num)
                pixmaps.append(pixmap if pixmap else QPixmap())
                # Load images for this page
                self._load_page_images(page_num)
            else:
                # Create placeholder for other pages
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
        
        # Scroll to current page
        self._canvas.scroll_to_page(current_page)
        
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
        
        # Render these pages and load their images
        for page_num in pages_to_render:
            pixmap = self._document.render_page(page_num)
            if pixmap:
                # Replace the placeholder with actual rendered page
                page_label = self._canvas._page_labels[page_num]
                page_label.setPixmap(pixmap)
                self._rendered_pages.add(page_num)
                # Load images for this page
                self._load_page_images(page_num)
        
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
        
        # Update View Toolbar (new)
        self._update_view_toolbar_state()
        
        # Old toolbar controls - skip if they don't exist
        if hasattr(self, '_page_input'):
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
        # Update View Toolbar (new)
        self._update_view_toolbar_state()
        
        # Old toolbar controls - skip if they don't exist
        if hasattr(self, '_page_input'):
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
            self._update_view_toolbar_state()
            self._update_pages_panel_selection()
        
        # Trigger on-demand rendering if lazy rendering is active
        if self._lazy_rendering_active:
            # Use debounce timer to avoid rendering on every scroll event
            self._render_debounce_timer.stop()
            self._render_debounce_timer.start(200)  # 200ms delay
    
    def _on_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        theme_manager = get_theme_manager()
        new_theme = theme_manager.toggle_theme()
        
        # Show status message
        if new_theme == ThemeType.DARK:
            self._status_bar.showMessage("Dark theme activated")
        else:
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
    
    def _on_sidebar_collapsed(self) -> None:
        """Handle left sidebar collapse - update splitter sizes."""
        # Get current sizes
        canvas_width = self._main_splitter.sizes()[1]
        right_width = self._main_splitter.sizes()[2]
        
        # Give canvas the space from collapsed sidebar (280 - 48 = 232 pixels)
        new_canvas_width = canvas_width + 232
        
        # Update sizes: left collapses to 48px, canvas grows, right unchanged
        self._main_splitter.setSizes([48, new_canvas_width, right_width])
    
    def _on_sidebar_expanded(self) -> None:
        """Handle left sidebar expand - update splitter sizes."""
        # Get current sizes
        canvas_width = self._main_splitter.sizes()[1]
        right_width = self._main_splitter.sizes()[2]
        
        # Take space from canvas for expanded sidebar (280 - 48 = 232 pixels)
        new_canvas_width = canvas_width - 232
        
        # Update sizes: left expands to 280px, canvas shrinks, right unchanged
        self._main_splitter.setSizes([280, new_canvas_width, right_width])
    
    def _on_right_sidebar_collapsed(self) -> None:
        """Handle right sidebar collapse - update splitter sizes."""
        # Get current sizes
        left_width = self._main_splitter.sizes()[0]
        canvas_width = self._main_splitter.sizes()[1]
        
        # Give canvas the space from collapsed sidebar (280 - 48 = 232 pixels)
        new_canvas_width = canvas_width + 232
        
        # Update sizes: left unchanged, canvas grows, right collapses to 48px
        self._main_splitter.setSizes([left_width, new_canvas_width, 48])
    
    def _on_right_sidebar_expanded(self) -> None:
        """Handle right sidebar expand - update splitter sizes."""
        # Get current sizes
        left_width = self._main_splitter.sizes()[0]
        canvas_width = self._main_splitter.sizes()[1]
        
        # Take space from canvas for expanded sidebar (280 - 48 = 232 pixels)
        new_canvas_width = canvas_width - 232
        
        # Update sizes: left unchanged, canvas shrinks, right expands to 280px
        self._main_splitter.setSizes([left_width, new_canvas_width, 280])
    
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
        Adds asterisk (*) suffix if document has unsaved changes.
        
        Args:
            file_name: Name of the currently open file, or None if no file is open
        """
        if file_name:
            # Check if document is dirty (has unsaved changes)
            state_manager = self._document.get_state_manager()
            dirty_marker = "*" if state_manager.is_dirty() else ""
            self.setWindowTitle(f"{file_name}{dirty_marker} - Simple PDF Handler")
        else:
            self.setWindowTitle("Simple PDF Handler")
    
    def _on_document_state_changed(self, is_dirty: bool) -> None:
        """
        Handle document dirty state change.
        Updates window title and Save button state.
        
        Args:
            is_dirty: True if document has unsaved changes, False otherwise
        """
        # Get current file name and update title
        file_path = self._document.get_file_path()
        if file_path:
            file_name = os.path.basename(file_path)
            self._update_window_title(file_name)
        
        # Enable/disable Save button based on dirty state
        self._view_toolbar.set_save_enabled(is_dirty)
    
    def _enable_zoom_controls(self) -> None:
        """Enable zoom controls when a document is loaded."""
        # View toolbar handles this now via _update_view_toolbar_state
        if hasattr(self, '_zoom_in_btn'):
            self._zoom_in_btn.setEnabled(True)
            self._zoom_out_btn.setEnabled(True)
            self._zoom_combo.setEnabled(True)
            self._fit_width_btn.setEnabled(True)
            self._fit_page_btn.setEnabled(True)
    
    def _disable_zoom_controls(self) -> None:
        """Disable zoom controls when no document is loaded."""
        # View toolbar handles this now via _update_view_toolbar_state
        if hasattr(self, '_zoom_in_btn'):
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
        
        self._status_bar.showMessage(f"Rendering pages at {int(zoom * 100)}%...")
        
        # Clear image cache for fresh render
        self._canvas.clear_page_images()
        
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
        
        # Update View Toolbar
        self._view_toolbar.set_zoom_level(zoom_text)
        
        # Update old combo box if it exists
        if hasattr(self, '_zoom_combo'):
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
        
        # Switch to search panel in sidebar
        self._new_sidebar.set_mode(SidebarMode.SEARCH)
        
        # Expand if collapsed
        if self._new_sidebar.is_collapsed():
            self._new_sidebar.expand()
        
        # Focus search input
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.focus_search_input()
    
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
        # Get search text from sidebar panel
        search_text = None
        case_sensitive = False
        
        if hasattr(self, '_sidebar_search_panel'):
            search_text = self._sidebar_search_panel.get_search_text()
            case_sensitive = self._sidebar_search_panel.is_case_sensitive()
        
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
            case_sensitive
        )
        
        # Connect signals
        self._search_worker.search_progress.connect(self._on_search_progress)
        self._search_worker.match_found.connect(self._on_match_found)
        self._search_worker.search_completed.connect(self._on_search_completed)
        self._search_worker.search_failed.connect(self._on_search_failed)
        self._search_worker.search_cancelled.connect(self._on_search_cancelled)
        
        # Update search panel
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.show_progress(True)
            self._sidebar_search_panel.set_progress(0, 100)
            self._sidebar_search_panel.set_match_counter("Searching...")
        
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
        # Update search panel
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.set_progress(current_page, total_pages)
    
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
        match_text = f"{total_matches} match{'es' if total_matches != 1 else ''}"
        
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.set_match_counter(match_text)
        
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
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.show_progress(False)
        
        # Update UI based on results
        if total_matches > 0:
            match_text = f"{total_matches} match{'es' if total_matches != 1 else ''}"
            
            # Update panel
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter(match_text)
                self._sidebar_search_panel.enable_navigation(True)
            
            self._status_bar.showMessage(f"Found {match_text}")
            
            # Update results list and highlights
            self._update_search_highlights()
            self._update_results_list()
        else:
            # Update panel
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter("No matches found")
                self._sidebar_search_panel.enable_navigation(False)
                self._sidebar_search_panel.clear_results()
            
            self._status_bar.showMessage("No matches found")
    
    def _on_search_failed(self, error_message: str) -> None:
        """
        Handle search failure.
        
        Args:
            error_message: Error description
        """
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.show_progress(False)
            self._sidebar_search_panel.set_match_counter("Search failed")
        self._status_bar.showMessage(f"Search failed: {error_message}")
    
    def _on_search_cancelled(self) -> None:
        """Handle search cancellation."""
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.show_progress(False)
            
            # Show results found so far
            total_matches = self._search_results.get_total_matches()
            if total_matches > 0:
                self._sidebar_search_panel.set_match_counter(f"{total_matches} match{'es' if total_matches != 1 else ''} (partial)")
                self._sidebar_search_panel.enable_navigation(True)
                self._update_search_highlights()
                self._update_results_list()
            else:
                self._sidebar_search_panel.set_match_counter("Search cancelled")
        
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
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter(f"{match_num} of {total}")
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
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter(f"{match_num} of {total}")
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
        if hasattr(self, '_sidebar_search_panel'):
            self._sidebar_search_panel.update_results_list(results_with_context, current_match_info)
    
    def _update_match_counter(self) -> None:
        """Update the match counter display."""
        if not self._search_results.has_results():
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter("No matches")
            return
        
        match_info = self._search_results.get_current_match_info()
        if match_info:
            _, _, match_num = match_info
            total = self._search_results.get_total_matches()
            if hasattr(self, '_sidebar_search_panel'):
                self._sidebar_search_panel.set_match_counter(f"{match_num} of {total}")
    
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
        # Handle word selection request from double-click
        if selected_text == "WORD_SELECTION_REQUEST":
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
    
    def _on_image_selected(self, page_num: int, image_info: dict) -> None:
        """
        Handle image selection signal from canvas.
        
        Args:
            page_num: Page number containing the selected image (0-indexed)
            image_info: Dictionary with image information (rect, xref, width, height, colorspace)
        """
        # Show image dimensions in status bar
        width = image_info.get('width', 'unknown')
        height = image_info.get('height', 'unknown')
        self._status_bar.showMessage(
            f"Image selected: {width}×{height}px (Press Ctrl+C to copy)", 
            3000
        )
    
    def _copy_selected_text(self) -> None:
        """Copy currently selected text or image to clipboard."""
        if not self._document.is_open():
            return
        
        # Check if an image is selected first
        selected_image = self._canvas.get_selected_image()
        if selected_image:
            self._copy_selected_image()
            return
        
        # Get text selection info from canvas
        selection_info = self._canvas.get_selection_info()
        if not selection_info:
            return
        
        page_num, selection_rect = selection_info
        
        # Get text words from the selected page
        words = self._document._backend.get_text_words(page_num)
        if not words:
            return
        
        # Check if selection rect is small (indicates smart selection from double/triple click)
        # vs large (indicates drag selection)
        is_smart_selection = (selection_rect.width() <= 10 and selection_rect.height() <= 10)
        
        if is_smart_selection:
            # Smart selection (double or triple click) - determine which by checking line
            # First try word selection
            word_text = self._select_word_at_rect(words, selection_rect, page_num)
            if word_text:
                selected_text = word_text
            else:
                # If no word found, try line selection
                selected_text = self._select_line_at_rect(words, selection_rect, page_num)
        else:
            # Normal drag selection
            selected_text = self._extract_text_from_selection(words, selection_rect)
        
        if selected_text:
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)
            
            # Show feedback
            self._status_bar.showMessage(f"Copied {len(selected_text)} characters to clipboard", 2000)
    
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
        
        if not selected_words:
            return ""
        
        # Calculate average character width for dynamic spacing threshold
        avg_char_width = self._calculate_avg_char_width(selected_words)
        
        # Use character-width-based threshold instead of fixed 2 pixels
        # Typically, word spacing is 0.5-1.0x the character width
        space_threshold = avg_char_width * 0.6
        
        # Sort words by position (top-to-bottom, left-to-right)
        # Use rounded Y values to group words on same line
        selected_words.sort(key=lambda w: (round(w[1]), w[0]))
        
        # Combine words into text with proper spacing
        text_parts = []
        prev_y_mid = None
        prev_x_end = None
        prev_word = None
        
        for x0, y0, x1, y1, word in selected_words:
            # Calculate word center Y and height
            y_mid = (y0 + y1) / 2
            word_height = y1 - y0
            
            # Determine if this is a new line
            # Use word height as threshold (more reliable than fixed points)
            is_new_line = (prev_y_mid is not None and 
                          abs(y_mid - prev_y_mid) > word_height * 0.3)
            
            if is_new_line:
                # New line detected
                text_parts.append('\n')
            elif prev_x_end is not None and prev_word is not None:
                # Same line - check if there's a gap between words
                gap = x0 - prev_x_end
                
                # Check both pixel gap AND Unicode word boundaries
                unicode_boundary = self._is_unicode_word_boundary(prev_word, word)
                needs_space = gap > space_threshold or unicode_boundary
                
                if needs_space:
                    text_parts.append(' ')
            
            text_parts.append(word)
            prev_y_mid = y_mid
            prev_x_end = x1
            prev_word = word
        
        return ''.join(text_parts)
    
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
    
    def _update_right_panel(self) -> None:
        """Update right sidebar with current document information."""
        if not self._document.is_open():
            return
        
        # Extract document metadata
        doc_info = self._extract_document_metadata()
        
        # Update document properties panel
        if hasattr(self, '_doc_props_panel'):
            self._doc_props_panel.update_properties(doc_info)
    
    def _extract_document_metadata(self) -> dict:
        """
        Extract metadata from current document.
        
        Returns:
            Dictionary with document metadata
        """
        if not self._document.is_open():
            return {}
        
        file_path = self._document.get_file_path()
        file_name = os.path.basename(file_path)
        
        # Get file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
        except:
            size_str = "N/A"
        
        # Get file timestamps
        try:
            import datetime
            created_time = os.path.getctime(file_path)
            modified_time = os.path.getmtime(file_path)
            created_str = datetime.datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M")
            modified_str = datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M")
        except:
            created_str = "N/A"
            modified_str = "N/A"
        
        # Get PDF metadata from backend
        metadata = self._document._backend.get_metadata()
        
        return {
            'filename': file_name,
            'filesize': size_str,
            'pages': str(self._document.get_page_count()),
            'created': created_str,
            'modified': modified_str,
            'title': metadata.get('title', 'N/A'),
            'author': metadata.get('author', 'N/A'),
            'subject': metadata.get('subject', 'N/A'),
        }
    
    def _load_bookmarks(self) -> None:
        """Load bookmarks from current document into bookmarks panel."""
        if not self._document.is_open():
            return
        
        if not hasattr(self, '_bookmarks_panel'):
            return
        
        # Get bookmarks from backend
        bookmarks = self._document._backend.get_bookmarks()
        
        # Load into panel
        self._bookmarks_panel.load_bookmarks(bookmarks)
    
    def _on_bookmark_clicked(self, page_num: int) -> None:
        """
        Handle bookmark click - navigate to page.
        
        Args:
            page_num: Page number to navigate to (0-indexed)
        """
        if not self._document.is_open():
            return
        
        # Navigate to the bookmarked page
        if self._document.set_current_page(page_num):
            self._canvas.scroll_to_page(page_num)
            self._update_navigation_controls()
            self._update_view_toolbar_state()
            self._update_pages_panel_selection()
            self._status_bar.showMessage(f"Jumped to page {page_num + 1}", 2000)
    
    def _on_page_thumbnail_clicked(self, page_num: int) -> None:
        """
        Handle thumbnail click from pages panel - navigate to page.
        
        Args:
            page_num: Page number to navigate to (0-indexed)
        """
        if not self._document.is_open():
            return
        
        # Navigate to the clicked page
        if self._document.set_current_page(page_num):
            # Re-render based on current view mode
            view_mode = self._document.get_view_mode()
            
            if view_mode == ViewMode.SINGLE_PAGE:
                # Single page mode - render just this page
                pixmap = self._document.render_page(page_num)
                if pixmap:
                    self._canvas.display_single_page(pixmap, page_num)
            elif view_mode == ViewMode.FACING:
                # Facing pages mode - render appropriate pair
                if page_num == 0:
                    # Show cover page alone
                    pixmap = self._document.render_page(0)
                    if pixmap:
                        self._canvas.display_facing_pages(pixmap, None, 0, None)
                else:
                    # Determine page pair
                    if page_num % 2 == 1:
                        left_page = page_num
                        right_page = page_num + 1 if page_num + 1 < self._document.get_page_count() else None
                    else:
                        left_page = page_num - 1
                        right_page = page_num
                    
                    left_pixmap = self._document.render_page(left_page)
                    right_pixmap = self._document.render_page(right_page) if right_page is not None else None
                    
                    if left_pixmap:
                        self._canvas.display_facing_pages(left_pixmap, right_pixmap, left_page, right_page)
            else:
                # Continuous mode - just scroll to page
                self._canvas.scroll_to_page(page_num)
            
            self._update_navigation_controls()
            self._update_view_toolbar_state()
            self._status_bar.showMessage(f"Jumped to page {page_num + 1}", 2000)
    
    def _load_pages_panel(self) -> None:
        """Initialize pages panel with current document pages."""
        if not self._document.is_open() or not hasattr(self, '_pages_panel'):
            return
        
        page_count = self._document.get_page_count()
        
        # Initialize thumbnail widgets
        self._pages_panel.load_pages(page_count)
        
        # Set current page selection
        self._update_pages_panel_selection()
        
        # Start rendering thumbnails in background
        self._start_thumbnail_rendering()
    
    def _start_thumbnail_rendering(self) -> None:
        """Start background rendering of page thumbnails."""
        if not self._document.is_open() or not hasattr(self, '_pages_panel'):
            return
        
        # Cancel any existing thumbnail rendering
        if self._thumbnail_worker and self._thumbnail_worker.isRunning():
            self._thumbnail_worker.cancel()
            self._thumbnail_worker.wait()
        
        page_count = self._document.get_page_count()
        
        # Create thumbnail render worker
        self._thumbnail_worker = ThumbnailRenderWorker(
            self._document._backend,
            page_count,
            thumbnail_scale=0.25  # 25% of original size for thumbnails
        )
        
        # Connect signals
        self._thumbnail_worker.thumbnail_ready.connect(self._on_thumbnail_ready)
        self._thumbnail_worker.progress_updated.connect(self._on_thumbnail_progress)
        self._thumbnail_worker.rendering_completed.connect(self._on_thumbnail_rendering_completed)
        self._thumbnail_worker.rendering_failed.connect(self._on_thumbnail_rendering_failed)
        
        # Start rendering
        self._thumbnail_worker.start()
        self._status_bar.showMessage(f"Rendering thumbnails for {page_count} pages...")
    
    def _on_thumbnail_ready(self, page_number: int, pixmap: QPixmap) -> None:
        """
        Handle thumbnail ready signal.
        
        Args:
            page_number: Page number (0-indexed)
            pixmap: Rendered thumbnail pixmap
        """
        if hasattr(self, '_pages_panel'):
            self._pages_panel.set_thumbnail(page_number, pixmap)
    
    def _on_thumbnail_progress(self, current_page: int, total_pages: int) -> None:
        """
        Handle thumbnail rendering progress.
        
        Args:
            current_page: Current page being rendered (1-indexed for display)
            total_pages: Total number of pages
        """
        progress_percent = int((current_page / total_pages) * 100)
        self._status_bar.showMessage(
            f"Rendering thumbnails: {current_page}/{total_pages} ({progress_percent}%)"
        )
    
    def _on_thumbnail_rendering_completed(self, total_rendered: int) -> None:
        """
        Handle completion of thumbnail rendering.
        
        Args:
            total_rendered: Total number of thumbnails rendered
        """
        self._status_bar.showMessage(
            f"Thumbnails rendered: {total_rendered} pages", 3000
        )
    
    def _on_thumbnail_rendering_failed(self, error_message: str) -> None:
        """
        Handle thumbnail rendering failure.
        
        Args:
            error_message: Error description
        """
        self._status_bar.showMessage(f"Thumbnail rendering failed: {error_message}")
    
    def _refresh_page_thumbnail(self, page_number: int) -> None:
        """
        Re-render a specific page's thumbnail to show recent changes.
        Used for live updates after edits.
        
        Args:
            page_number: Page number to refresh (0-indexed)
        """
        if not self._document.is_open() or not hasattr(self, '_pages_panel'):
            return
        
        # Render thumbnail at 25% scale
        thumbnail_scale = 0.25
        pixmap = self._document._backend.render_page(page_number, thumbnail_scale)
        
        if pixmap:
            # Update the thumbnail in pages panel
            self._pages_panel.set_thumbnail(page_number, pixmap)
    
    def _update_pages_panel_selection(self) -> None:
        """Update pages panel to highlight current page."""
        if not self._document.is_open() or not hasattr(self, '_pages_panel'):
            return
        
        current_page = self._document.get_current_page()
        self._pages_panel.set_current_page(current_page)
    
    def _copy_selected_image(self) -> None:
        """Copy currently selected image to clipboard."""
        if not self._document.is_open():
            return
        
        # Get selected image info from canvas
        selected_image = self._canvas.get_selected_image()
        if not selected_image:
            return
        
        page_num, image_info = selected_image
        xref = image_info['xref']
        
        # Show extracting status
        self._status_bar.showMessage("Extracting image...")
        QApplication.processEvents()
        
        # Extract image at original resolution
        pixmap = self._document.extract_image(page_num, xref)
        
        if pixmap and not pixmap.isNull():
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            # Show success feedback
            width = pixmap.width()
            height = pixmap.height()
            self._status_bar.showMessage(
                f"Copied image ({width}×{height}px) to clipboard", 
                3000
            )
        else:
            # Failed to extract image
            self._show_error("Failed to extract image from PDF")
            self._status_bar.showMessage("Image extraction failed")
    
    def _clear_selection(self) -> None:
        """Clear the current text or image selection."""
        # Clear text selection
        self._canvas.clear_selection()
        
        # Clear image selection
        self._canvas.clear_image_selection()
        
        self._status_bar.showMessage("Selection cleared", 1000)
    
    def _on_save(self) -> None:
        """Handle Ctrl+S save shortcut."""
        if not self._document.is_open():
            return
        
        if not self._document.get_state_manager().is_dirty():
            self._status_bar.showMessage("No changes to save", 2000)
            return
        
        # Get file path before saving
        file_path = self._document.get_file_path()
        current_page = self._document.get_current_page()
        
        # Save the document
        success = self._document.save()
        
        if success:
            self._status_bar.showMessage("Document saved successfully", 2000)
            
            # Re-open the document to continue working
            # (PyMuPDF closes the document after save)
            if self._document.open(file_path):
                # Restore the current page
                self._document.set_current_page(current_page)
                
                # Re-render current view to show the saved state
                self._render_current_view()
            else:
                self._show_error("Document saved but failed to re-open")
        else:
            self._show_error("Failed to save document")
    
    def _set_single_page_mode(self) -> None:
        """Switch to single page view mode."""
        if not self._document.is_open():
            return
        
        # Clear image cache for fresh render
        self._canvas.clear_page_images()
        
        # Update document view mode
        self._document.set_view_mode(ViewMode.SINGLE_PAGE)
        
        # Update toolbar button states
        self._view_toolbar._single_page_btn.setChecked(True)
        self._view_toolbar._continuous_page_btn.setChecked(False)
        self._view_toolbar._facing_page_btn.setChecked(False)
        
        # Re-render in single page mode
        current_page = self._document.get_current_page()
        pixmap = self._document.render_page(current_page)
        if pixmap:
            # Load images for this page
            self._load_page_images(current_page)
            self._canvas.display_single_page(pixmap, current_page)
            self._status_bar.showMessage("Single page mode activated", 2000)
        
        # Update navigation IMMEDIATELY
        self._update_navigation_controls()
        self._update_view_toolbar_state()
        
        # Delay thumbnail selection update to ensure canvas has updated
        QTimer.singleShot(50, self._update_pages_panel_selection)
    
    def _set_continuous_mode(self) -> None:
        """Switch to continuous scrolling view mode."""
        if not self._document.is_open():
            return
        
        # Store current page BEFORE mode switch
        current_page = self._document.get_current_page()
        
        # Temporarily block scroll signals to prevent interference during rendering
        self._canvas.verticalScrollBar().blockSignals(True)
        
        # Update document view mode
        self._document.set_view_mode(ViewMode.CONTINUOUS)
        
        # Update toolbar button states
        self._view_toolbar._single_page_btn.setChecked(False)
        self._view_toolbar._continuous_page_btn.setChecked(True)
        self._view_toolbar._facing_page_btn.setChecked(False)
        
        # Re-render in continuous mode, preserving current page
        page_count = self._document.get_page_count()
        
        if page_count > 50:
            self._render_initial_pages_lazy(preserve_page=True)
        else:
            self._render_all_pages(preserve_page=True)
        
        # Force process events to ensure layout is calculated
        QApplication.processEvents()
        
        # Re-enable scroll signals AFTER scrolling
        self._canvas.verticalScrollBar().blockSignals(False)
        
        # Ensure we're still on the same page after rendering
        self._document.set_current_page(current_page)
        
        self._status_bar.showMessage("Continuous view mode activated", 2000)
        
        # Update navigation IMMEDIATELY
        self._update_navigation_controls()
        self._update_view_toolbar_state()
        
        # Delay thumbnail selection update to ensure scroll completes
        QTimer.singleShot(200, self._update_pages_panel_selection)
    
    def _set_facing_pages_mode(self) -> None:
        """Switch to facing pages view mode (two pages side-by-side)."""
        if not self._document.is_open():
            return
        
        # Clear image cache for fresh render
        self._canvas.clear_page_images()
        
        # Store current page BEFORE mode switch
        current_page = self._document.get_current_page()
        
        # Update document view mode
        self._document.set_view_mode(ViewMode.FACING)
        
        # Update toolbar button states
        self._view_toolbar._single_page_btn.setChecked(False)
        self._view_toolbar._continuous_page_btn.setChecked(False)
        self._view_toolbar._facing_page_btn.setChecked(True)
        
        # Render facing pages
        # In facing mode, show page pairs
        # First page (page 0) is shown alone (cover)
        # Then pages are paired: 1-2, 3-4, 5-6, etc.
        
        if current_page == 0:
            # Show only first page (cover)
            pixmap = self._document.render_page(0)
            if pixmap:
                # Load images for cover page
                self._load_page_images(0)
                self._canvas.display_facing_pages(pixmap, None, 0, None)
        else:
            # Determine which pair to show
            # For odd pages (1, 3, 5...), show with next page (1-2, 3-4, 5-6)
            # For even pages (2, 4, 6...), show with previous page (1-2, 3-4, 5-6)
            if current_page % 2 == 1:
                # Odd page - show with next page
                left_page = current_page
                right_page = current_page + 1 if current_page + 1 < self._document.get_page_count() else None
            else:
                # Even page - show with previous page
                left_page = current_page - 1
                right_page = current_page
            
            # Render both pages
            left_pixmap = self._document.render_page(left_page)
            right_pixmap = self._document.render_page(right_page) if right_page is not None else None
            
            if left_pixmap:
                # Load images for both pages
                self._load_page_images(left_page)
                if right_page is not None:
                    self._load_page_images(right_page)
                self._canvas.display_facing_pages(left_pixmap, right_pixmap, left_page, right_page)
        
        # Ensure current page is preserved in document
        self._document.set_current_page(current_page)
        
        self._status_bar.showMessage("Facing pages mode activated", 2000)
        
        # Update navigation IMMEDIATELY
        self._update_navigation_controls()
        self._update_view_toolbar_state()
        
        # Delay thumbnail selection update to ensure canvas has updated
        QTimer.singleShot(50, self._update_pages_panel_selection)
    
    def _on_add_text(self) -> None:
        """Handle Add Text button click from Edit Tools panel."""
        if not self._document.is_open():
            self._status_bar.showMessage("Please open a PDF first", 2000)
            return
        
        # Enter text placement mode
        self._canvas.enter_text_placement_mode()
        self._status_bar.showMessage("Click on the page where you want to add text", 0)
    
    def _on_text_committed(self, text: str, format_props: dict, page_num: int, pdf_x: float, pdf_y: float) -> None:
        """
        Handle text committed from inline editor.
        
        Args:
            text: Text content
            format_props: Format properties (font, size, color, etc.)
            page_num: Page number where text was added
            pdf_x, pdf_y: PDF coordinates
        """
        # Convert Qt color to PDF color (0-1 range)
        qt_color = format_props['color']
        pdf_color = (qt_color.red() / 255.0, qt_color.green() / 255.0, qt_color.blue() / 255.0)
        
        # Map font name to PDF font
        font_map = {
            'Helvetica': 'helv',
            'Times-Roman': 'times',
            'Courier': 'cour'
        }
        pdf_font = font_map.get(format_props['font'], 'helv')
        
        # Add text annotation to PDF
        annot_xref = self._document.add_text_annotation(
            page_num,
            pdf_x,
            pdf_y,
            text,
            font_name=pdf_font,
            font_size=format_props['size'],
            color=pdf_color
        )
        
        if annot_xref:
            # Mark document as modified (enables save)
            self._document.get_state_manager().mark_dirty()
            
            # Create and record undo action
            from core.undo_manager import AddTextAction
            action = AddTextAction(
                page_num,
                pdf_x,
                pdf_y,
                text,
                pdf_font,
                format_props['size'],
                pdf_color,
                annot_xref
            )
            self._undo_manager.record_action(action)
            
            # Create TextObject for tracking
            from core.pdf_object import TextObject
            from PyQt6.QtCore import QPointF
            
            # Create position point
            position = QPointF(pdf_x, pdf_y)
            
            # Create TextObject with correct signature
            text_obj = TextObject(
                page_number=page_num,
                position=position,
                content=text
            )
            
            # Set font properties
            text_obj.set_font_name(format_props['font'])
            text_obj.set_font_size(format_props['size'])
            text_obj.set_color(format_props['color'])
            text_obj.set_bold(format_props.get('bold', False))
            text_obj.set_italic(format_props.get('italic', False))
            text_obj.set_underline(format_props.get('underline', False))
            
            # Store the annotation reference
            text_obj.set_annotation_id(annot_xref)
            
            # Add to document's object collection
            self._document.get_objects().add(text_obj)
            
            # Re-render the page to show new text in main canvas
            self._render_current_view()
            
            # LIVE UPDATE: Re-render the thumbnail for this page
            self._refresh_page_thumbnail(page_num)
            
            self._status_bar.showMessage(f"Text added to page {page_num + 1}", 2000)
        else:
            self._status_bar.showMessage("Failed to add text", 2000)
    
    def _render_current_view(self) -> None:
        """Re-render current view mode to show changes."""
        view_mode = self._document.get_view_mode()
        current_page = self._document.get_current_page()
        
        if view_mode == ViewMode.CONTINUOUS:
            # Re-render all pages
            page_count = self._document.get_page_count()
            if page_count > 50:
                self._render_initial_pages_lazy(preserve_page=True)
            else:
                self._render_all_pages(preserve_page=True)
        elif view_mode == ViewMode.SINGLE_PAGE:
            # Re-render current page
            pixmap = self._document.render_page(current_page)
            if pixmap:
                self._canvas.display_single_page(pixmap, current_page)
        elif view_mode == ViewMode.FACING:
            # Re-render facing pages
            self._set_facing_pages_mode()
    
    def _on_add_image(self) -> None:
        """Handle Add Image button click from Edit Tools panel."""
        self._status_bar.showMessage("Add Image - Coming in Phase 3", 2000)
    
    def _on_add_blank_page(self) -> None:
        """
        Handle Add Blank Page button click.
        Inserts a blank A4 page at the end of the document.
        """
        if not self._document.is_open():
            self._status_bar.showMessage("Please open a PDF first", 2000)
            return
        
        # Insert blank page at end
        page_count = self._document.get_page_count()
        success = self._document._backend.insert_blank_page(page_count)
        
        if success:
            # Mark document as dirty
            self._document.get_state_manager().mark_dirty()
            
            # Record undo action
            from core.undo_manager import InsertPageAction
            action = InsertPageAction(page_count)
            self._undo_manager.record_action(action)
            
            # Reload pages panel to show new page
            self._load_pages_panel()
            
            # Re-render current view
            self._render_current_view()
            
            self._status_bar.showMessage(f"Added blank page {page_count + 1}", 2000)
        else:
            self._show_error("Failed to add blank page")
    
    def _on_attach_file(self) -> None:
        """Handle Attach File button click from Edit Tools panel."""
        self._status_bar.showMessage("Attach File - Coming in Phase 3", 2000)
    
    def _on_edit_text(self) -> None:
        """Handle Edit Text button click from Edit Tools panel."""
        self._status_bar.showMessage("Edit Text - Coming soon", 2000)
    
    def _on_shape_drawing_started(self, shape_type: str, properties: dict) -> None:
        """
        Handle shape drawing mode activation from toolbar.
        
        Args:
            shape_type: Type of shape to draw ('rectangle', 'circle', 'line')
            properties: Shape properties (colors, widths, fill)
        """
        if not self._document.is_open():
            self._status_bar.showMessage("Please open a PDF first", 2000)
            return
        
        # Enter shape drawing mode on canvas
        self._canvas.enter_shape_drawing_mode(shape_type, properties)
        self._status_bar.showMessage(
            f"Click and drag to draw {shape_type}. Right-click to cancel.", 
            0
        )
    
    def _on_shape_drawn(self, shape_data: dict) -> None:
        """
        Handle shape completion - add to PDF and record for undo.
        
        Args:
            shape_data: Dictionary containing shape type, coordinates, and properties
        """
        if not self._document.is_open():
            return
        
        # Extract shape info
        shape_type = shape_data.get('type')
        page_num = shape_data.get('page_number')
        props = shape_data.get('properties', {})
        
        # CRITICAL: Capture page snapshot BEFORE drawing for undo support
        backend = self._document._backend
        page_snapshot = backend.capture_page_snapshot(page_num)
        
        # Convert QColor to RGB tuples (0-1 range)
        border_color = props.get('border_color')
        if border_color:
            border_rgb = (
                border_color.red() / 255.0,
                border_color.green() / 255.0,
                border_color.blue() / 255.0
            )
        else:
            border_rgb = (0, 0, 0)
        
        border_width = props.get('border_width', 2)
        
        # Get fill color if enabled
        fill_rgba = None
        if props.get('fill_enabled') and props.get('fill_color'):
            fill_color = props.get('fill_color')
            fill_rgba = (
                fill_color.red() / 255.0,
                fill_color.green() / 255.0,
                fill_color.blue() / 255.0,
                fill_color.alpha() / 255.0
            )
        
        # Call appropriate backend method
        backend = self._document._backend
        success = False
        
        if shape_type == 'rectangle':
            success = backend.add_rectangle_shape(
                page_num,
                shape_data['x0'],
                shape_data['y0'],
                shape_data['x1'],
                shape_data['y1'],
                border_rgb,
                border_width,
                fill_rgba
            )
        elif shape_type == 'circle':
            success = backend.add_circle_shape(
                page_num,
                shape_data['center_x'],
                shape_data['center_y'],
                shape_data['radius'],
                border_rgb,
                border_width,
                fill_rgba
            )
        elif shape_type == 'line':
            success = backend.add_line_shape(
                page_num,
                shape_data['x0'],
                shape_data['y0'],
                shape_data['x1'],
                shape_data['y1'],
                border_rgb,
                border_width
            )
        
        if success:
            # Mark document as modified
            self._document.get_state_manager().mark_dirty()
            
            # Create undo action with page snapshot
            from core.undo_manager import AddShapeAction
            action = AddShapeAction(shape_data, page_snapshot)
            self._undo_manager.record_action(action)
            
            # Re-render the page to show new shape
            self._render_current_view()
            
            # Refresh thumbnail for this page
            self._refresh_page_thumbnail(page_num)
            
            # Show success message
            self._status_bar.showMessage(f"{shape_type.capitalize()} added to page {page_num + 1}", 2000)
        else:
            self._status_bar.showMessage(f"Failed to add {shape_type}", 2000)
    
    def _on_edit_pages_toggled(self, enabled: bool) -> None:
        """
        Handle Edit Pages mode toggle.
        Shows/hides page editing controls on thumbnails.
        
        Args:
            enabled: True when entering edit mode, False when exiting
        """
        if not self._document.is_open():
            return
        
        # Update pages panel edit mode
        if hasattr(self, '_pages_panel'):
            self._pages_panel.set_edit_mode(enabled)
        
        # Switch to pages panel if entering edit mode
        if enabled:
            self._new_sidebar.set_mode(SidebarMode.PAGES)
            if self._new_sidebar.is_collapsed():
                self._new_sidebar.expand()
            self._status_bar.showMessage("Page editing active - Use overlay buttons or drag to reorder", 0)
        else:
            self._status_bar.showMessage("Page editing disabled", 2000)
    
    def _on_delete_page_requested(self, page_number: int) -> None:
        """
        Handle delete page request from pages panel overlay button.
        
        Args:
            page_number: Page to delete (0-indexed)
        """
        if not self._document.is_open():
            return
        
        page_count = self._document.get_page_count()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Page",
            f"Are you sure you want to delete page {page_number + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Check if edit mode is currently active
        edit_mode_active = False
        if hasattr(self, '_pages_panel'):
            edit_mode_active = self._pages_panel._edit_mode
        
        # Perform deletion (returns success and page data for undo)
        success, page_data = self._document._backend.delete_page(page_number)
        
        if success:
            # Mark document as dirty
            self._document.get_state_manager().mark_dirty()
            
            # Record undo action with captured page data
            from core.undo_manager import DeletePageAction
            action = DeletePageAction(page_number, page_data)
            self._undo_manager.record_action(action)
            
            # Reload pages panel
            self._load_pages_panel()
            
            # Restore edit mode if it was active
            if edit_mode_active and hasattr(self, '_pages_panel'):
                self._pages_panel.set_edit_mode(True)
            
            # Adjust current page if needed
            if page_number <= self._document.get_current_page():
                new_page = max(0, self._document.get_current_page() - 1)
                self._document.set_current_page(new_page)
            
            # Re-render view
            self._render_current_view()
            
            self._status_bar.showMessage(f"Deleted page {page_number + 1}", 2000)
        else:
            self._show_error("Failed to delete page")
    
    def _on_insert_page_requested(self, position: int) -> None:
        """
        Handle insert page request from pages panel overlay button.
        Inserts a blank page at the specified position.
        
        Args:
            position: Position to insert blank page before (0-indexed)
        """
        if not self._document.is_open():
            return
        
        # Check if edit mode is currently active
        edit_mode_active = False
        if hasattr(self, '_pages_panel'):
            edit_mode_active = self._pages_panel._edit_mode
        
        # Insert blank page
        success = self._document._backend.insert_blank_page(position)
        
        if success:
            # Mark document as dirty
            self._document.get_state_manager().mark_dirty()
            
            # Record undo action
            from core.undo_manager import InsertPageAction
            action = InsertPageAction(position)
            self._undo_manager.record_action(action)
            
            # Reload pages panel
            self._load_pages_panel()
            
            # Restore edit mode if it was active
            if edit_mode_active and hasattr(self, '_pages_panel'):
                self._pages_panel.set_edit_mode(True)
            
            # Re-render view
            self._render_current_view()
            
            self._status_bar.showMessage(f"Inserted blank page at position {position + 1}", 2000)
        else:
            self._show_error("Failed to insert page")
    
    def _on_move_page_requested(self, from_page: int, to_page: int) -> None:
        """
        Handle move page request from pages panel drag-and-drop.
        Reorders pages in the document.
        
        Args:
            from_page: Source page number (0-indexed)
            to_page: Destination page number (0-indexed)
        """
        if not self._document.is_open():
            return
        
        # Perform move
        success = self._document._backend.move_page(from_page, to_page)
        
        if success:
            # Mark document as dirty
            self._document.get_state_manager().mark_dirty()
            
            # Record undo action
            from core.undo_manager import MovePageAction
            action = MovePageAction(from_page, to_page)
            self._undo_manager.record_action(action)
            
            # Update page numbers on thumbnails
            if hasattr(self, '_pages_panel'):
                self._pages_panel.update_page_numbers_after_reorder()
            
            # Reload thumbnail rendering to reflect new order
            self._start_thumbnail_rendering()
            
            # Re-render view
            self._render_current_view()
            
            self._status_bar.showMessage(f"Moved page {from_page + 1} to position {to_page + 1}", 2000)
        else:
            self._show_error("Failed to move page")
    
    def _on_undo(self) -> None:
        """Handle undo request (Ctrl+Z or button click)."""
        if not self._document.is_open():
            return
        
        if not self._undo_manager.can_undo():
            self._status_bar.showMessage("Nothing to undo", 1000)
            return
        
        # Check if edit mode is currently active
        edit_mode_active = False
        if hasattr(self, '_pages_panel'):
            edit_mode_active = self._pages_panel._edit_mode
        
        # Perform undo
        page_num = self._undo_manager.undo(self._document._backend)
        
        if page_num is not None:
            # Reload pages panel to update thumbnails
            self._load_pages_panel()
            
            # Restore edit mode if it was active
            if edit_mode_active and hasattr(self, '_pages_panel'):
                self._pages_panel.set_edit_mode(True)
            
            # Re-render the affected page
            self._render_current_view()
            
            self._status_bar.showMessage("Undo successful", 2000)
        else:
            self._status_bar.showMessage("Undo failed", 2000)
    
    def _on_redo(self) -> None:
        """Handle redo request (Ctrl+Shift+Z or button click)."""
        if not self._document.is_open():
            return
        
        if not self._undo_manager.can_redo():
            self._status_bar.showMessage("Nothing to redo", 1000)
            return
        
        # Perform redo
        page_num = self._undo_manager.redo(self._document._backend)
        
        if page_num is not None:
            # Re-render the affected page
            self._render_current_view()
            self._status_bar.showMessage("Redo successful", 2000)
        else:
            self._status_bar.showMessage("Redo failed", 2000)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.
        Shows save dialog if document has unsaved changes.
        
        Args:
            event: Close event
        """
        # Check if document has unsaved changes
        if self._document.is_open():
            state_manager = self._document.get_state_manager()
            
            if state_manager.is_dirty():
                # Document has unsaved changes - show save dialog
                file_path = self._document.get_file_path()
                file_name = os.path.basename(file_path) if file_path else "Untitled"
                
                # Create message box with save/don't save/cancel options
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"Do you want to save changes to \"{file_name}\"?",
                    QMessageBox.StandardButton.Save | 
                    QMessageBox.StandardButton.Discard | 
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save  # Default button
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    # User wants to save - trigger save operation
                    # TODO: Implement save functionality in Phase 2
                    # For now, just accept the close
                    self._status_bar.showMessage("Save not yet implemented")
                    # Uncomment this when save is implemented:
                    # if not self._save_document():
                    #     event.ignore()  # Save failed, don't close
                    #     return
                    pass
                    
                elif reply == QMessageBox.StandardButton.Cancel:
                    # User cancelled - don't close
                    event.ignore()
                    return
                
                # If Discard, continue with close
            
            # Close the document
            self._document.close()
        
        # Stop any running worker threads
        if self._loader_worker and self._loader_worker.isRunning():
            self._loader_worker.quit()
            self._loader_worker.wait()
        
        if self._zoom_worker and self._zoom_worker.isRunning():
            self._zoom_worker.cancel()
            self._zoom_worker.wait()
        
        if self._thumbnail_worker and self._thumbnail_worker.isRunning():
            self._thumbnail_worker.cancel()
            self._thumbnail_worker.wait()
        
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.wait()
        
        event.accept()
