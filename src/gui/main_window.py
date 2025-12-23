"""
Main application window.

Contains the primary UI structure with menu bar, toolbar, sidebars, content area, and status bar.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QAction

from utils.constants import WindowDefaults, AppInfo, Icons
from utils.config import get_config
from utils.theme_manager import get_theme_manager
from core.pdf_document import PDFDocument

from .menu_bar import MenuBar
from .toolbar import Toolbar
from .left_sidebar import LeftSidebar
from .right_sidebar import RightSidebar
from .content_area import ContentArea
from .status_bar import StatusBar
from .welcome_screen import WelcomeScreen
from .ocr_detection_banner import OCRDetectionBanner
from .ocr_dialogs import OCRDialog, OCRProgressDialog, OCRCompletionDialog
from .ocr_review_settings import OCRReviewDialog, OCRSettingsDialog
from core.ocr.ocr_coordinator import OCRCoordinator, OCRWorker


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Orchestrates all UI components and handles application-level actions.
    Follows the coordinator pattern to manage component interactions.
    """
    
    # Signals for cross-component communication
    document_opened = Signal(str)  # Emitted when a document is opened
    document_closed = Signal()     # Emitted when a document is closed
    theme_changed = Signal(str)    # Emitted when theme is changed
    
    def __init__(self):
        """Initialize the main window with all components."""
        super().__init__()
        
        self.config = get_config()
        self.theme_manager = get_theme_manager()
        
        # PDF document handler
        self.pdf_document = PDFDocument()
        
        # OCR coordinator for text recognition
        self.ocr_coordinator = OCRCoordinator()
        self.ocr_worker = None
        self.ocr_results = None
        
        # State tracking
        self._current_document = None
        self._is_modified = False
        
        self._setup_window()
        self._create_components()
        self._create_layout()
        self._setup_connections()
        self._update_window_state()
    
    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle(AppInfo.NAME)
        self.resize(WindowDefaults.WIDTH, WindowDefaults.HEIGHT)
        self.setMinimumSize(WindowDefaults.MIN_WIDTH, WindowDefaults.MIN_HEIGHT)
        
        # Add keyboard shortcuts for undo/redo
        # Note: QKeySequence standard keys automatically use Cmd on Mac, Ctrl on Windows/Linux
        # Note: Keyboard shortcuts are primarily handled through the menu bar
        # Menu bar shortcuts work natively on macOS and are properly connected
        # to the handler methods in _setup_connections()
    
    def _create_components(self):
        """Create all UI components."""
        # Create menu bar
        self.menu_bar_widget = MenuBar(self)
        self.setMenuBar(self.menu_bar_widget)
        
        # Create toolbar
        self.toolbar_widget = Toolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_widget)
        
        # Create sidebars as dock widgets
        self.left_sidebar = LeftSidebar(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_sidebar)
        
        self.right_sidebar = RightSidebar(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_sidebar)
        
        # Create content area (central widget)
        self.content_area = ContentArea(self)
        
        # Create OCR detection banner (hidden initially)
        self.ocr_banner = OCRDetectionBanner(self)
        self.ocr_banner.hide()
        
        # Create welcome screen
        self.welcome_screen = WelcomeScreen(self)
        
        # Create status bar
        self.status_bar_widget = StatusBar(self)
        self.setStatusBar(self.status_bar_widget)
    
    def _create_layout(self):
        """Set up the central widget layout."""
        # Create central widget container
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # OCR detection banner (shows when scanned PDF detected)
        layout.addWidget(self.ocr_banner)
        
        # Initially show welcome screen
        layout.addWidget(self.welcome_screen)
        
        # Hide content area initially (will show when document opens)
        self.content_area.hide()
        layout.addWidget(self.content_area)
        
        self.setCentralWidget(central_widget)
    
    def _setup_connections(self):
        """Connect signals and slots between components."""
        # Menu bar actions
        self.menu_bar_widget.open_file_requested.connect(self._handle_open_file)
        self.menu_bar_widget.close_file_requested.connect(self._handle_close_file)
        self.menu_bar_widget.save_file_requested.connect(self._handle_save_file)  # Connect Save from menu
        self.menu_bar_widget.undo_requested.connect(self._handle_undo)  # Connect Undo from menu  
        self.menu_bar_widget.redo_requested.connect(self._handle_redo)  # Connect Redo from menu
        self.menu_bar_widget.copy_requested.connect(self.content_area.copy_selected_text)
        self.menu_bar_widget.exit_requested.connect(self.close)
        self.menu_bar_widget.zoom_in_requested.connect(self._handle_zoom_in)
        self.menu_bar_widget.zoom_out_requested.connect(self._handle_zoom_out)
        self.menu_bar_widget.theme_toggle_requested.connect(self._handle_theme_toggle)
        self.menu_bar_widget.about_requested.connect(self._show_about_dialog)
        
        # OCR menu signals
        self.menu_bar_widget.quick_ocr_requested.connect(self._handle_quick_ocr)
        self.menu_bar_widget.advanced_ocr_requested.connect(self._handle_advanced_ocr)
        self.menu_bar_widget.ocr_settings_requested.connect(self._handle_ocr_settings)
        self.menu_bar_widget.export_ocr_text_requested.connect(self._handle_export_ocr_text)
        self.menu_bar_widget.export_ocr_word_requested.connect(self._handle_export_ocr_word)
        self.menu_bar_widget.export_ocr_excel_requested.connect(self._handle_export_ocr_excel)
        
        # OCR banner signals
        self.ocr_banner.quick_ocr_requested.connect(self._handle_quick_ocr)
        self.ocr_banner.advanced_ocr_requested.connect(self._handle_advanced_ocr)
        self.ocr_banner.dismissed.connect(self.ocr_banner.hide)
        
        # Toolbar actions
        self.toolbar_widget.open_file_requested.connect(self._handle_open_file)
        self.toolbar_widget.save_file_requested.connect(self._handle_save_file)
        self.toolbar_widget.print_requested.connect(self._handle_print)
        self.toolbar_widget.undo_requested.connect(self._handle_undo)
        self.toolbar_widget.redo_requested.connect(self._handle_redo)
        self.toolbar_widget.quick_ocr_requested.connect(self._handle_quick_ocr)
        
        # Edit actions from toolbar
        self.toolbar_widget.cut_requested.connect(self.content_area.cut_selected_text)
        self.toolbar_widget.copy_requested.connect(self.content_area.copy_selected_text)
        self.toolbar_widget.paste_requested.connect(self.content_area.paste_from_clipboard)
        self.toolbar_widget.select_all_requested.connect(self.content_area.select_all_text)
        self.toolbar_widget.delete_requested.connect(self.content_area.delete_selected)
        
        self.toolbar_widget.zoom_in_requested.connect(self._handle_zoom_in)
        self.toolbar_widget.zoom_out_requested.connect(self._handle_zoom_out)
        self.toolbar_widget.rotate_requested.connect(self._handle_rotate)
        self.toolbar_widget.select_text_toggled.connect(self.content_area.set_selection_mode)
        
        # Annotation toolbar signals
        self.toolbar_widget.highlight_mode_toggled.connect(self._handle_highlight_mode)
        self.toolbar_widget.annotation_color_changed.connect(self.content_area.set_annotation_color)
        
        # Welcome screen actions
        self.welcome_screen.open_file_requested.connect(self._handle_open_file)
        self.welcome_screen.recent_file_selected.connect(self._handle_open_recent)
        
        # PDF document signals
        self.pdf_document.document_loaded.connect(self._on_document_loaded)
        self.pdf_document.document_closed.connect(self._on_document_closed)
        self.pdf_document.error_occurred.connect(self._on_pdf_error)
        self.pdf_document.document_modified.connect(self._on_document_modified)
        self.pdf_document.undo_redo_changed.connect(self._on_undo_redo_changed)
        
        # Left sidebar signals
        self.left_sidebar.page_selected.connect(self.content_area.go_to_page)
        self.left_sidebar.search_requested.connect(self._handle_search_requested)
        
        # Search panel signals (connect after search_panel is created in left_sidebar)
        # Note: We'll connect these in _on_document_loaded after sidebar is fully initialized
        
        # Content area signals
        self.content_area.page_changed.connect(self._on_page_changed)
        self.content_area.page_changed.connect(self.left_sidebar.set_current_page)
        self.content_area.page_changed.connect(self.left_sidebar.update_bookmark_current_page)
        self.content_area.text_copied.connect(self._on_text_copied)
        self.content_area.text_selected.connect(self._on_text_selected)
        self.content_area.image_selected.connect(self._on_image_selected)
        self.content_area.image_copied.connect(self._on_image_copied)
        self.content_area.selection_mode_changed.connect(self.toolbar_widget.set_select_text_mode)
        
        # Status bar updates
        self.status_bar_widget.zoom_changed.connect(self._handle_zoom_change)
    
    def _update_window_state(self):
        """Update window state based on whether a document is open."""
        has_document = self._current_document is not None
        
        # Show/hide appropriate views
        if has_document:
            self.welcome_screen.hide()
            self.content_area.show()
        else:
            self.content_area.hide()
            self.welcome_screen.show()
        
        # Enable/disable relevant UI elements
        self.menu_bar_widget.set_document_actions_enabled(has_document)
        self.toolbar_widget.set_document_actions_enabled(has_document)
        self.right_sidebar.setEnabled(has_document)
        
        # Update window title with asterisk if modified
        if has_document:
            filename = self._current_document.split('/')[-1]
            # Use pdf_document.is_modified() for dirty state
            modified_marker = "*" if self.pdf_document.is_modified() else ""
            self.setWindowTitle(f"{modified_marker}{filename} - {AppInfo.NAME}")
        else:
            self.setWindowTitle(AppInfo.NAME)
    
    # Action handlers
    def _handle_open_file(self):
        """Handle open file request."""
        from PySide6.QtWidgets import QFileDialog
        
        # Get last used directory
        last_dir = self.config.get_last_directory()
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            last_dir,
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if file_path:
            # Save the directory for next time
            from pathlib import Path
            self.config.set_last_directory(str(Path(file_path).parent))
            
            # Open the document
            self._open_document(file_path)
    
    def _handle_close_file(self):
        """Handle close file request."""
        if not self._current_document:
            return
        
        # Check for unsaved changes
        if self._is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save your changes before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._handle_save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        # Close document
        self._current_document = None
        self._is_modified = False
        self._update_window_state()
        self.document_closed.emit()
    
    def _handle_save_file(self):
        """Handle save file request."""
        if not self._current_document or not self.pdf_document:
            return
        
        # Check if document has unsaved changes
        if not self.pdf_document.is_modified():
            self.status_bar_widget.show_message("No changes to save", 2000)
            return
        
        # Save the document
        if self.pdf_document.save():
            # Save successful
            from pathlib import Path
            filename = Path(self._current_document).name
            self.status_bar_widget.show_message(f"Saved {filename}", 3000)
            
            # Update window title (remove asterisk)
            self._update_window_state()
        else:
            # Save failed (error will be shown via error_occurred signal)
            pass
    
    def _handle_open_recent(self, file_path: str):
        """
        Handle opening a recent file.
        
        Args:
            file_path: Path to the file to open
        """
        # For Phase 1, just show info
        QMessageBox.information(
            self,
            "Open Recent",
            f"Opening recent file:\n{file_path}\n\n"
            "This feature will be fully functional in Phase 2."
        )
    
    def _handle_theme_toggle(self):
        """Toggle between light and dark themes."""
        current_theme = self.theme_manager.get_current_theme()
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        # Apply new theme
        self.theme_manager.set_theme(new_theme)
        self.theme_manager.apply_theme(self.window().windowHandle().screen())
        
        # Save preference
        self.config.set_theme(new_theme)
        
        # Notify components
        self.theme_changed.emit(new_theme)
        
        # Update status
        theme_name = "Dark" if new_theme == 'dark' else "Light"
        self.status_bar_widget.show_message(f"Switched to {theme_name} theme", 2000)
    
    def _handle_print(self):
        """Handle print request."""
        QMessageBox.information(
            self,
            "Print",
            "Printing will be implemented in Phase 2.\n\n"
            "This feature will allow you to print the PDF document."
        )
    
    def _handle_undo(self):
        """Handle undo request."""
        if not self.pdf_document or not self.pdf_document.can_undo():
            return
        
        # Perform undo
        page_number = self.pdf_document.undo()
        
        if page_number is not None:
            # Refresh the affected page
            self.content_area._refresh_page(page_number)
            self.status_bar_widget.show_message("Undone last annotation", 2000)
        else:
            self.status_bar_widget.show_message("Nothing to undo", 2000)
    
    def _handle_redo(self):
        """Handle redo request."""
        if not self.pdf_document or not self.pdf_document.can_redo():
            return
        
        # Perform redo
        page_number = self.pdf_document.redo()
        
        if page_number is not None:
            # Refresh the affected page
            self.content_area._refresh_page(page_number)
            self.status_bar_widget.show_message("Redone annotation", 2000)
        else:
            self.status_bar_widget.show_message("Nothing to redo", 2000)
    
    def _on_undo_redo_changed(self, can_undo: bool, can_redo: bool):
        """
        Handle undo/redo state changes to update button states.
        
        Args:
            can_undo: Whether undo is available
            can_redo: Whether redo is available
        """
        # Buttons are enabled/disabled automatically when document is open/closed
        # This handler can be used for more fine-grained control if needed
        pass
    
    def _handle_zoom_in(self):
        """Handle zoom in request."""
        if not self.pdf_document or not self.pdf_document.is_open:
            return
        
        current_zoom = self.pdf_document.zoom_level
        new_zoom = min(400, current_zoom + 25)  # Max 400%
        
        # Update PDF document zoom
        self.pdf_document.zoom_level = new_zoom
        
        # Re-render all pages at new zoom
        self.content_area.render_all_pages()
        
        # Update status bar
        self.status_bar_widget.set_zoom_level(new_zoom)
        self.status_bar_widget.show_message(f"Zoom: {int(new_zoom)}%", 1000)
    
    def _handle_zoom_out(self):
        """Handle zoom out request."""
        if not self.pdf_document or not self.pdf_document.is_open:
            return
        
        current_zoom = self.pdf_document.zoom_level
        new_zoom = max(25, current_zoom - 25)  # Min 25%
        
        # Update PDF document zoom
        self.pdf_document.zoom_level = new_zoom
        
        # Re-render all pages at new zoom
        self.content_area.render_all_pages()
        
        # Update status bar
        self.status_bar_widget.set_zoom_level(new_zoom)
        self.status_bar_widget.show_message(f"Zoom: {int(new_zoom)}%", 1000)
    
    def _handle_rotate(self):
        """Handle rotate page request."""
        self.status_bar_widget.show_message("Rotate (Phase 2)", 2000)
    
    def _handle_search_requested(self, search_term: str, options: dict):
        """
        Handle search request from sidebar.
        
        Args:
            search_term: Text to search for
            options: Search options dictionary
        """
        if not self.pdf_document or not self.pdf_document.is_open:
            return
        
        # Cancel any existing search
        if hasattr(self, '_search_worker') and self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.wait()
        
        # Show searching message
        self.status_bar_widget.show_message(f"Searching for '{search_term}'...", 0)
        
        # Create and start search worker
        from .search_worker import SearchWorker
        
        self._search_worker = SearchWorker(self.pdf_document, search_term, options)
        self._search_worker.progress_updated.connect(self._on_search_progress)
        self._search_worker.results_ready.connect(self._on_search_results)
        self._search_worker.error_occurred.connect(self._on_search_error)
        self._search_worker.start()
    
    def _on_search_progress(self, current_page: int, total_pages: int):
        """
        Handle search progress update.
        
        Args:
            current_page: Current page being searched
            total_pages: Total number of pages
        """
        # Update progress in sidebar
        percentage = int((current_page / total_pages) * 100)
        self.left_sidebar.search_panel.set_progress(percentage)
        
        # Update status bar
        self.status_bar_widget.show_message(
            f"Searching... {current_page}/{total_pages} pages",
            0
        )
    
    def _on_search_results(self, results: list):
        """
        Handle search results ready.
        
        Args:
            results: List of search result dictionaries
        """
        # Display results in sidebar
        self.left_sidebar.display_search_results(results)
        
        # Highlight all matches on PDF pages
        self.content_area.highlight_search_results(results)
        
        # Update status message
        if results:
            unique_pages = len(set(r['page'] for r in results))
            self.status_bar_widget.show_message(
                f"Found {len(results)} match{'es' if len(results) != 1 else ''} "
                f"on {unique_pages} page{'s' if unique_pages != 1 else ''}",
                5000
            )
        else:
            self.status_bar_widget.show_message("No matches found", 3000)
    
    def _on_search_error(self, error_message: str):
        """
        Handle search error.
        
        Args:
            error_message: Error description
        """
        self.status_bar_widget.show_message(f"Search error: {error_message}", 5000)
        QMessageBox.warning(self, "Search Error", error_message)
    
    def _handle_highlight_mode(self, enabled: bool):
        """
        Handle highlight mode toggle from toolbar.
        
        Args:
            enabled: Whether highlight mode is enabled
        """
        if enabled:
            # Enable highlight mode in content area
            self.content_area.set_annotation_mode('highlight')
            self.status_bar_widget.show_message("Highlight mode ON - Select text to highlight, ESC to cancel", 5000)
        else:
            # Disable highlight mode
            self.content_area.set_annotation_mode(None)
            self.status_bar_widget.show_message("Highlight mode OFF", 2000)
    
    def _handle_zoom_change(self, zoom_level: float):
        """
        Handle zoom level change from status bar.
        
        Args:
            zoom_level: New zoom level as percentage
        """
        if not self.pdf_document or not self.pdf_document.is_open:
            return
        
        # Update PDF document zoom
        self.pdf_document.zoom_level = zoom_level
        
        # Re-render all pages at new zoom
        self.content_area.render_all_pages()
        
        # Show feedback
        self.status_bar_widget.show_message(f"Zoom: {int(zoom_level)}%", 1000)
    
    def _show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            f"About {AppInfo.NAME}",
            f"<h2>{AppInfo.NAME}</h2>"
            f"<p>Version {AppInfo.VERSION}</p>"
            f"<p>{AppInfo.DESCRIPTION}</p>"
            f"<p><b>License:</b> {AppInfo.LICENSE}</p>"
            f"<p><b>Website:</b> <a href='{AppInfo.WEBSITE}'>{AppInfo.WEBSITE}</a></p>"
            "<hr>"
            "<p>A professional, cross-platform PDF management application "
            "built with PySide6.</p>"
        )
    
    def _open_document(self, file_path: str):
        """
        Open a PDF document.
        
        Args:
            file_path: Path to the document to open
        """
        # Try to open the PDF
        if self.pdf_document.open(file_path):
            self._current_document = file_path
            self._is_modified = False
            
            # Add to recent files
            self.config.add_recent_file(file_path)
            
            # Update UI state
            self._update_window_state()
            
            # Notify components
            self.document_opened.emit(file_path)
            
            # Update status
            from pathlib import Path
            filename = Path(file_path).name
            self.status_bar_widget.show_message(f"Opened: {filename}", 3000)
        else:
            # Error opening document (error signal will be emitted)
            pass
    
    def _on_document_loaded(self):
        """Handle successful PDF document loading."""
        # Pass PDF document to content area for continuous rendering
        self.content_area.set_pdf_document(self.pdf_document)
        
        # Update status bar with page info
        self.status_bar_widget.set_page_info(1, self.pdf_document.page_count)
        
        # Load page thumbnails in sidebar
        self.left_sidebar.load_pages(self.pdf_document.page_count, self.pdf_document)
        
        # Load bookmarks in sidebar
        bookmarks = self.pdf_document.get_bookmarks()
        self.left_sidebar.load_bookmarks(bookmarks)
        
        # Connect search result selection signal
        self.left_sidebar.search_panel.result_selected.connect(self._on_search_result_clicked)
        
        # Connect clear highlights signal
        self.left_sidebar.search_panel.clear_highlights.connect(self.content_area.clear_search_highlights)
        
        # Check if document is scanned and show OCR banner
        if self.ocr_coordinator.is_scanned_document(self._current_document):
            self.ocr_banner.show_banner()
            self.status_bar_widget.show_message("📄 Scanned document detected - OCR available", 5000)
    
    def _on_search_result_clicked(self, page_num: int, bbox: tuple):
        """
        Handle search result click - navigate and highlight.
        
        Args:
            page_num: Page number (0-indexed)
            bbox: Bounding box of match
        """
        # Navigate to page
        self.content_area.go_to_page(page_num)
        
        # Highlight this specific match (orange)
        self.content_area.highlight_current_search_match(page_num, bbox)
    
    def _on_document_closed(self):
        """Handle PDF document closing."""
        # Clear content area
        self.content_area.clear_content()
        
        # Reset status bar
        self.status_bar_widget.set_page_info(0, 0)
    
    def _on_pdf_error(self, error_message: str):
        """
        Handle PDF errors.
        
        Args:
            error_message: Error description
        """
        QMessageBox.critical(
            self,
            "PDF Error",
            f"An error occurred:\n\n{error_message}"
        )
    
    def _on_page_changed(self, page_number: int):
        """
        Handle page change in content area.
        
        Args:
            page_number: New page number (0-indexed)
        """
        # Update status bar
        self.status_bar_widget.set_page_info(page_number + 1, self.pdf_document.page_count)
    
    def _on_text_copied(self, message: str):
        """
        Handle text copied event from content area.
        
        Args:
            message: Feedback message to display
        """
        # Show message in status bar
        self.status_bar_widget.show_message(message, 3000)
    
    def _on_text_selected(self, message: str):
        """
        Handle text selected event from content area.
        
        Args:
            message: Feedback message to display
        """
        # Show message in status bar
        self.status_bar_widget.show_message(message, 5000)  # Longer duration for selection message
    
    def _on_image_selected(self, message: str):
        """
        Handle image selected event from content area.
        
        Args:
            message: Feedback message to display
        """
        # Show message in status bar
        self.status_bar_widget.show_message(message, 5000)
    
    def _on_image_copied(self, message: str):
        """
        Handle image copied event from content area.
        
        Args:
            message: Feedback message to display
        """
        # Show message in status bar
        self.status_bar_widget.show_message(message, 3000)
    
    def _on_document_modified(self, is_modified: bool):
        """
        Handle document modified state change.
        
        Args:
            is_modified: Whether document has unsaved changes
        """
        # Update window title to show/hide asterisk
        self._update_window_state()
    
    def _render_current_page(self):
        """Render the current page and display it."""
        if not self.pdf_document.is_open:
            return
        
        # Get current page
        page_num = self.pdf_document.current_page
        
        # Render page
        pixmap = self.pdf_document.render_page(page_num)
        
        if pixmap:
            # Display in content area
            self.content_area.display_page(pixmap, page_num)
    
    # OCR workflow handlers
    def _handle_quick_ocr(self):
        """Handle quick OCR with automatic settings."""
        if not self._current_document:
            return
        
        # Check if document actually needs OCR
        if not self.ocr_coordinator.is_scanned_document(self._current_document):
            # Document already has text layer
            reply = QMessageBox.question(
                self,
                "OCR Not Recommended",
                "This PDF already has a searchable text layer.\n\n"
                "OCR is designed for scanned/image-only PDFs without text.\n"
                "Running OCR on this document is:\n"
                "• Unnecessary (text is already searchable)\n"
                "• Time-consuming (may take several minutes)\n"
                "• Potentially less accurate than existing text\n\n"
                "Do you still want to proceed with OCR?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                self.status_bar_widget.show_message("OCR cancelled - document already has text", 3000)
                return
        
        # Get current page for context
        current_page = self.content_area.current_page if hasattr(self.content_area, 'current_page') else 0
        
        # Show OCR dialog in Quick mode (all defaults)
        dialog = OCRDialog(self.pdf_document.page_count, current_page, self)
        dialog.ocr_started.connect(self._start_ocr_processing)
        dialog.exec()
    
    def _handle_advanced_ocr(self):
        """Handle OCR with advanced options dialog."""
        if not self._current_document:
            return
        
        current_page = self.content_area.current_page if hasattr(self.content_area, 'current_page') else 0
        
        # Show full OCR configuration dialog
        dialog = OCRDialog(self.pdf_document.page_count, current_page, self)
        dialog.ocr_started.connect(self._start_ocr_processing)
        dialog.settings_requested.connect(self._handle_ocr_settings)
        dialog.exec()
    
    def _start_ocr_processing(self, params: dict):
        """
        Start OCR processing with given parameters.
        
        Args:
            params: OCR configuration dictionary
        """
        # Create progress dialog
        page_range = params['page_range']
        total_pages = page_range[1] - page_range[0]
        
        progress_dialog = OCRProgressDialog(total_pages, self)
        
        # Create OCR worker
        self.ocr_worker = OCRWorker(
            self._current_document,
            params['language'],
            page_range,
            params.get('enhance', True)
        )
        
        # Connect worker signals
        self.ocr_worker.progress_updated.connect(progress_dialog.update_progress)
        self.ocr_worker.ocr_completed.connect(
            lambda results, stats: self._on_ocr_completed(results, stats, progress_dialog, params)
        )
        self.ocr_worker.error_occurred.connect(
            lambda error: self._on_ocr_error(error, progress_dialog)
        )
        
        # Connect cancel
        progress_dialog.cancel_requested.connect(self.ocr_worker.cancel)
        
        # Start processing
        self.ocr_worker.start()
        progress_dialog.exec()
    
    def _on_ocr_completed(self, results: list, statistics: dict, progress_dialog, params: dict):
        """
        Handle OCR completion.
        
        Args:
            results: OCR results list
            statistics: Result statistics
            progress_dialog: Progress dialog to close
            params: Original OCR parameters
        """
        # Close progress dialog
        progress_dialog.accept()
        
        # Store results
        self.ocr_results = results
        
        # Show completion dialog
        completion_dialog = OCRCompletionDialog(statistics, self._current_document, self)
        completion_dialog.save_requested.connect(
            lambda mode, path: self._save_ocr_results(results, mode, path, params)
        )
        completion_dialog.review_requested.connect(
            lambda: self._review_ocr_results(results, statistics)
        )
        completion_dialog.exec()
    
    def _on_ocr_error(self, error: str, progress_dialog):
        """
        Handle OCR error.
        
        Args:
            error: Error message
            progress_dialog: Progress dialog to close
        """
        progress_dialog.reject()
        QMessageBox.critical(self, "OCR Error", f"OCR processing failed:\n\n{error}")
    
    def _save_ocr_results(self, results: list, mode: str, file_path: str, params: dict):
        """
        Save OCR results to file.
        
        Args:
            results: OCR results
            mode: Save mode ('current', 'new', 'none')
            file_path: Output file path
            params: OCR parameters
        """
        if mode == 'none':
            self.status_bar_widget.show_message("OCR preview mode - not saved", 3000)
            return

        # Validate OCR results have actual text
        total_text_blocks = sum(len(r.text_blocks) for r in results)
        total_text = ''.join(r.full_text for r in results).strip()
        
        print(f"DEBUG: Saving OCR results - {len(results)} pages, {total_text_blocks} text blocks, {len(total_text)} chars")
        
        if total_text_blocks == 0 or len(total_text) == 0:
            QMessageBox.warning(
                self,
                "No Text Found",
                "OCR did not find any text in the document.\n\n"
                "This could mean:\n"
                "• The PDF pages are blank\n"
                "• The image quality is too poor\n"
                "• The language setting is incorrect\n\n"
                "Cannot create searchable PDF without text."
            )
            return

        # Create searchable PDF using background worker to avoid UI freeze
        from core.ocr import PDFSaveWorker
        from PySide6.QtWidgets import QProgressDialog
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Creating searchable PDF...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Saving PDF")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        # Create and configure worker
        save_worker = PDFSaveWorker(
            self._current_document,
            file_path,
            results,
            compress=params.get('compress', True)
        )
        
        # Connect signals
        def update_progress(current, total, message):
            progress_dialog.setLabelText(message)
            progress = int((current / total) * 100) if total > 0 else 0
            progress_dialog.setValue(progress)
        
        def on_save_completed(success, result):
            progress_dialog.close()
            save_worker.quit()
            save_worker.wait()
            
            if success:
                from pathlib import Path
                filename = Path(file_path).name
                self.status_bar_widget.show_message(f"✓ Saved searchable PDF: {filename}", 5000)
                
                # If saved to current file, reload
                if mode == 'current':
                    self._open_document(file_path)
            else:
                QMessageBox.critical(self, "Save Error", f"Failed to save PDF:\n{result}")
        
        save_worker.progress_updated.connect(update_progress)
        save_worker.save_completed.connect(on_save_completed)
        progress_dialog.canceled.connect(save_worker.cancel)
        
        # Start worker
        save_worker.start()
    
    def _review_ocr_results(self, results: list, statistics: dict):
        """
        Open review dialog for uncertain words.
        
        Args:
            results: OCR results
            statistics: Result statistics
        """
        suspicious = statistics.get('suspicious_words', [])
        if not suspicious:
            self.status_bar_widget.show_message("No uncertain words to review", 3000)
            return
        
        review_dialog = OCRReviewDialog(suspicious, self)
        review_dialog.correction_applied.connect(self._apply_ocr_correction)
        review_dialog.review_completed.connect(
            lambda: self.status_bar_widget.show_message("✓ Review completed", 3000)
        )
        review_dialog.exec()
    
    def _apply_ocr_correction(self, word_index: int, correction: str):
        """
        Apply correction to OCR result.
        
        Args:
            word_index: Index of word to correct
            correction: Corrected text
        """
        # Update OCR results with correction
        self.status_bar_widget.show_message(f"✓ Correction applied: {correction}", 2000)
    
    def _handle_ocr_settings(self):
        """Show OCR settings dialog."""
        dialog = OCRSettingsDialog(self)
        if dialog.exec():
            self.status_bar_widget.show_message("OCR settings saved", 2000)
    
    def _handle_export_ocr_text(self):
        """Export OCR results to text file."""
        if not self.ocr_results:
            QMessageBox.information(
                self, "No OCR Results",
                "Please run OCR on the document first."
            )
            return
        
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Text", "", "Text Files (*.txt)"
        )
        
        if file_path:
            if self.ocr_coordinator.export_handler.export_to_text(self.ocr_results, file_path):
                self.status_bar_widget.show_message(f"✓ Exported to text", 3000)
    
    def _handle_export_ocr_word(self):
        """Export OCR results to Word document."""
        if not self.ocr_results:
            QMessageBox.information(
                self, "No OCR Results",
                "Please run OCR on the document first."
            )
            return
        
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Word", "", "Word Documents (*.docx)"
        )
        
        if file_path:
            if self.ocr_coordinator.export_handler.export_to_word(self.ocr_results, file_path):
                self.status_bar_widget.show_message(f"✓ Exported to Word", 3000)
    
    def _handle_export_ocr_excel(self):
        """Export OCR tables to Excel."""
        if not self.ocr_results:
            QMessageBox.information(
                self, "No OCR Results",
                "Please run OCR on the document first."
            )
            return
        
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Tables to Excel", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            # Extract tables from results (placeholder)
            tables = []
            if self.ocr_coordinator.export_handler.export_tables_to_excel(tables, file_path):
                self.status_bar_widget.show_message(f"✓ Exported tables to Excel", 3000)
    
    # Window event handlers
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        # Check for unsaved changes using pdf_document
        if self.pdf_document and self.pdf_document.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save your changes before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._handle_save_file()
                if self.pdf_document.is_modified():  # Save was cancelled or failed
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        # Save window geometry
        self.config.set_window_geometry(self.saveGeometry())
        self.config.set_window_state(self.saveState())
        
        # Save sidebar visibility
        self.config.set_left_sidebar_visible(self.left_sidebar.isVisible())
        self.config.set_right_sidebar_visible(self.right_sidebar.isVisible())
        
        # Sync configuration
        self.config.sync()
        
        event.accept()
    
    # Public methods for external control
    def set_modified(self, modified: bool):
        """
        Set document modified state.
        
        Args:
            modified: Whether document has unsaved changes
        """
        self._is_modified = modified
        self._update_window_state()
    
    def get_current_document(self) -> str:
        """
        Get currently open document path.
        
        Returns:
            Document path or None
        """
        return self._current_document
