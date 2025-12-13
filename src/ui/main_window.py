"""
Main application window for the PDF handler.
Integrates all UI components and manages application state.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QMenuBar, QMenu, QStatusBar,
    QToolBar, QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from ui.pdf_canvas import PDFCanvas
from ui.progress_dialog import ProgressDialog
from core.pdf_document import PDFDocument
from core.pdf_loader_worker import PDFLoaderWorker


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
        
        # Enable navigation controls
        self._update_navigation_controls()
        
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
        
        event.accept()
