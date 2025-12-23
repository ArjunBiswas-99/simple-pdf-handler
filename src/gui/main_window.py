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
        undo_shortcut = QAction(self)
        undo_shortcut.setShortcut(QKeySequence.Undo)  # Cmd+Z on Mac, Ctrl+Z on Windows/Linux
        undo_shortcut.triggered.connect(self._handle_undo)
        self.addAction(undo_shortcut)
        
        redo_shortcut = QAction(self)
        redo_shortcut.setShortcut(QKeySequence.Redo)  # Cmd+Shift+Z on Mac, Ctrl+Y on Windows/Linux
        redo_shortcut.triggered.connect(self._handle_redo)
        self.addAction(redo_shortcut)
        
        # Add keyboard shortcut for save
        save_shortcut = QAction(self)
        save_shortcut.setShortcut(QKeySequence.Save)  # Cmd+S on Mac, Ctrl+S on Windows/Linux
        save_shortcut.triggered.connect(self._handle_save_file)
        self.addAction(save_shortcut)
    
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
        self.menu_bar_widget.copy_requested.connect(self.content_area.copy_selected_text)
        self.menu_bar_widget.exit_requested.connect(self.close)
        self.menu_bar_widget.zoom_in_requested.connect(self._handle_zoom_in)
        self.menu_bar_widget.zoom_out_requested.connect(self._handle_zoom_out)
        self.menu_bar_widget.theme_toggle_requested.connect(self._handle_theme_toggle)
        self.menu_bar_widget.about_requested.connect(self._show_about_dialog)
        
        # Toolbar actions
        self.toolbar_widget.open_file_requested.connect(self._handle_open_file)
        self.toolbar_widget.save_file_requested.connect(self._handle_save_file)
        self.toolbar_widget.print_requested.connect(self._handle_print)
        self.toolbar_widget.undo_requested.connect(self._handle_undo)
        self.toolbar_widget.redo_requested.connect(self._handle_redo)
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
        
        # Content area signals
        self.content_area.page_changed.connect(self._on_page_changed)
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
