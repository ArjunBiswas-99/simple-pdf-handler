"""
Left sidebar component.

Provides document navigation through pages, bookmarks, search, comments, and layers.
"""

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTabWidget,
    QListWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCheckBox, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.constants import WindowDefaults, Icons, Spacing, Fonts


class LeftSidebar(QDockWidget):
    """
    Left sidebar dock widget.
    
    Contains tabbed panels for pages, bookmarks, search, comments, and layers.
    Provides navigation and document exploration features.
    """
    
    # Signals
    page_selected = Signal(int)  # Emitted when page is selected
    bookmark_selected = Signal(str)  # Emitted when bookmark is selected
    search_requested = Signal(str, dict)  # Emitted when search is performed
    
    def __init__(self, parent=None):
        """
        Initialize left sidebar.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Navigation", parent)
        
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable)
        
        self._create_content()
    
    def _create_content(self):
        """Create sidebar content with tabs."""
        from PySide6.QtWidgets import QScrollArea, QFrame
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)
        
        # Add all tabs
        self._create_pages_tab()
        self._create_bookmarks_tab()
        self._create_comments_tab()
        self._create_search_tab()
        self._create_layers_tab()
        
        # Wrap tab widget in scroll area for small screens
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tabs)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Clean look, no border
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Only vertical scroll
        
        layout.addWidget(scroll_area)
        
        self.setWidget(container)
        self.setMinimumWidth(WindowDefaults.LEFT_SIDEBAR_WIDTH)
    
    def _create_pages_tab(self):
        """Create professional pages panel with thumbnail grid."""
        from .page_grid_view import PageGridView
        from .thumbnail_generator import ThumbnailGenerator
        
        pages_widget = QWidget()
        layout = QVBoxLayout(pages_widget)
        layout.setSpacing(Spacing.SMALL)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Header with page counter and view mode dropdown
        header_layout = QHBoxLayout()
        title = QLabel("Pages")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Page counter
        self.page_counter = QLabel("0 pages")
        self.page_counter.setProperty("secondary", True)
        header_layout.addWidget(self.page_counter)
        
        # View mode dropdown
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Small", "Medium", "Large"])
        self.view_mode_combo.setCurrentIndex(1)  # Default: Medium
        self.view_mode_combo.currentIndexChanged.connect(self._on_view_mode_changed)
        self.view_mode_combo.setMaximumWidth(100)
        header_layout.addWidget(self.view_mode_combo)
        
        layout.addLayout(header_layout)
        
        # Create page grid view
        self.pages_grid = PageGridView()
        self.pages_grid.page_clicked.connect(self._on_page_clicked)
        self.pages_grid.page_double_clicked.connect(self._on_page_double_clicked)
        self.pages_grid.context_menu_requested.connect(self._on_page_context_menu)
        layout.addWidget(self.pages_grid)
        
        # Placeholder message (shown when no document open)
        self.pages_placeholder = QLabel(
            f"{Icons.PAGES}\n\nPage Thumbnails\n\n"
            "(Generated when PDF is opened)"
        )
        self.pages_placeholder.setAlignment(Qt.AlignCenter)
        self.pages_placeholder.setProperty("secondary", True)
        layout.addWidget(self.pages_placeholder)
        
        # Initially hide grid, show placeholder
        self.pages_grid.hide()
        self.pages_placeholder.show()
        
        # Thumbnail generator (will be set when document loads)
        self.thumbnail_generator = None
        
        self.tabs.addTab(pages_widget, Icons.PAGES)
        self.tabs.setTabToolTip(0, "Pages")
    
    def _create_bookmarks_tab(self):
        """Create bookmarks panel with tree view."""
        bookmarks_widget = QWidget()
        layout = QVBoxLayout(bookmarks_widget)
        layout.setSpacing(Spacing.SMALL)
        
        # Header
        title = QLabel("Bookmarks")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Bookmarks tree
        self.bookmarks_tree = QTreeWidget()
        self.bookmarks_tree.setHeaderHidden(True)
        self.bookmarks_tree.setIndentation(20)
        layout.addWidget(self.bookmarks_tree)
        
        # Placeholder message
        placeholder = QLabel(f"{Icons.BOOKMARKS}\n\nNo bookmarks\n\n(Bookmarks from PDF will appear here)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setProperty("secondary", True)
        layout.addWidget(placeholder)
        
        # Action buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(lambda: self._show_coming_soon("Add Bookmark"))
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._show_coming_soon("Edit Bookmark"))
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self._show_coming_soon("Delete Bookmark"))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.tabs.addTab(bookmarks_widget, Icons.BOOKMARKS)
        self.tabs.setTabToolTip(1, "Bookmarks")
    
    def _create_comments_tab(self):
        """Create comments panel."""
        comments_widget = QWidget()
        layout = QVBoxLayout(comments_widget)
        layout.setSpacing(Spacing.SMALL)
        
        # Header with filter
        header_layout = QHBoxLayout()
        title = QLabel("Comments")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter dropdown
        self.comments_filter = QComboBox()
        self.comments_filter.addItems(["All", "By Me", "By Others", "Unresolved"])
        header_layout.addWidget(self.comments_filter)
        layout.addLayout(header_layout)
        
        # Comments list
        self.comments_list = QListWidget()
        layout.addWidget(self.comments_list)
        
        # Placeholder
        placeholder = QLabel(f"{Icons.COMMENT}\n\nNo comments\n\n(Annotations will appear here)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setProperty("secondary", True)
        layout.addWidget(placeholder)
        
        # Sort options
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        sort_label.setProperty("secondary", True)
        sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Page", "Date", "Author", "Type"])
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        
        layout.addLayout(sort_layout)
        
        self.tabs.addTab(comments_widget, Icons.COMMENT)
        self.tabs.setTabToolTip(2, "Comments")
    
    def _create_search_tab(self):
        """Create search panel."""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)
        layout.setSpacing(Spacing.SMALL)
        
        # Header
        title = QLabel("Search Document")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.returnPressed.connect(self._perform_search)
        layout.addWidget(self.search_input)
        
        # Search options
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(Spacing.SMALL)
        
        self.match_case_cb = QCheckBox("Match case")
        options_layout.addWidget(self.match_case_cb)
        
        self.whole_words_cb = QCheckBox("Whole words only")
        options_layout.addWidget(self.whole_words_cb)
        
        self.regex_cb = QCheckBox("Regular expression")
        options_layout.addWidget(self.regex_cb)
        
        layout.addWidget(options_group)
        
        # Search buttons
        button_layout = QHBoxLayout()
        
        search_btn = QPushButton(f"{Icons.SEARCH} Find All")
        search_btn.clicked.connect(self._perform_search)
        button_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_search)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Results section
        results_label = QLabel("Results:")
        results_label.setProperty("secondary", True)
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._on_result_selected)
        layout.addWidget(self.results_list)
        
        # Results count
        self.results_count = QLabel("0 matches")
        self.results_count.setProperty("secondary", True)
        self.results_count.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.results_count)
        
        self.tabs.addTab(search_widget, Icons.SEARCH)
        self.tabs.setTabToolTip(3, "Search")
    
    def _create_layers_tab(self):
        """Create layers panel for advanced PDFs."""
        layers_widget = QWidget()
        layout = QVBoxLayout(layers_widget)
        layout.setSpacing(Spacing.SMALL)
        
        # Header
        title = QLabel("Layers")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Control visibility of optional content layers")
        desc.setProperty("secondary", True)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Layers list
        self.layers_list = QTreeWidget()
        self.layers_list.setHeaderLabels(["Layer", "Visible"])
        self.layers_list.setColumnWidth(0, 150)
        layout.addWidget(self.layers_list)
        
        # Placeholder
        placeholder = QLabel(f"📄\n\nNo layers\n\n(This PDF has no optional content layers)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setProperty("secondary", True)
        layout.addWidget(placeholder)
        
        # Actions
        action_layout = QHBoxLayout()
        show_all_btn = QPushButton("Show All")
        show_all_btn.clicked.connect(lambda: self._show_coming_soon("Show All Layers"))
        action_layout.addWidget(show_all_btn)
        
        hide_all_btn = QPushButton("Hide All")
        hide_all_btn.clicked.connect(lambda: self._show_coming_soon("Hide All Layers"))
        action_layout.addWidget(hide_all_btn)
        
        layout.addLayout(action_layout)
        
        self.tabs.addTab(layers_widget, "📄")
        self.tabs.setTabToolTip(4, "Layers")
    
    def _perform_search(self):
        """Perform search with current settings."""
        search_text = self.search_input.text()
        if not search_text:
            return
        
        options = {
            'match_case': self.match_case_cb.isChecked(),
            'whole_words': self.whole_words_cb.isChecked(),
            'regex': self.regex_cb.isChecked()
        }
        
        # Emit signal
        self.search_requested.emit(search_text, options)
        
        # For Phase 1, show placeholder
        self.results_list.clear()
        self.results_list.addItem("Search will be functional in Phase 2")
        self.results_count.setText("Phase 2 feature")
    
    def _clear_search(self):
        """Clear search results."""
        self.search_input.clear()
        self.results_list.clear()
        self.results_count.setText("0 matches")
    
    def _on_result_selected(self, item):
        """
        Handle search result selection.
        
        Args:
            item: Selected list item
        """
        # TODO Phase 2: Navigate to result
        pass
    
    def _show_coming_soon(self, feature: str):
        """
        Show coming soon message.
        
        Args:
            feature: Feature name
        """
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Coming Soon",
            f"{feature} will be available in Phase 2."
        )
    
    def _on_view_mode_changed(self, index: int):
        """Handle view mode dropdown change."""
        # Map index to thumbnails per row and size
        view_modes = {
            0: (3, 100),   # Small: 3 per row, 100px
            1: (2, 150),   # Medium: 2 per row, 150px
            2: (1, 200),   # Large: 1 per row, 200px
        }
        
        if index in view_modes:
            thumbs_per_row, thumb_size = view_modes[index]
            self.pages_grid.set_view_mode(thumbs_per_row, thumb_size)
            
            # Regenerate ALL thumbnails at new size if document is open
            if self.thumbnail_generator:
                # Get all pages instead of just visible ones
                all_pages = list(range(self.pages_grid._page_count))
                self.thumbnail_generator.generate_thumbnails(all_pages, thumb_size)
    
    def _on_page_clicked(self, page_num: int):
        """Handle page thumbnail click - emit signal for navigation."""
        self.page_selected.emit(page_num)
    
    def _on_page_double_clicked(self, page_num: int):
        """Handle page thumbnail double-click."""
        self.page_selected.emit(page_num)
    
    def _on_page_context_menu(self, page_num: int, pos):
        """Handle page thumbnail context menu request."""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # Add menu actions
        go_action = menu.addAction(f"{Icons.PAGES} Go to Page {page_num + 1}")
        go_action.triggered.connect(lambda: self.page_selected.emit(page_num))
        
        menu.addSeparator()
        
        # Phase 2 features (placeholders)
        insert_before = menu.addAction("Insert Page Before [Phase 2]")
        insert_before.triggered.connect(lambda: self._show_coming_soon("Insert Page Before"))
        
        insert_after = menu.addAction("Insert Page After [Phase 2]")
        insert_after.triggered.connect(lambda: self._show_coming_soon("Insert Page After"))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete Page [Phase 2]")
        delete_action.triggered.connect(lambda: self._show_coming_soon("Delete Page"))
        
        rotate_action = menu.addAction("Rotate Page 90° [Phase 2]")
        rotate_action.triggered.connect(lambda: self._show_coming_soon("Rotate Page"))
        
        menu.addSeparator()
        
        extract_action = menu.addAction("Extract Page [Phase 2]")
        extract_action.triggered.connect(lambda: self._show_coming_soon("Extract Page"))
        
        duplicate_action = menu.addAction("Duplicate Page [Phase 2]")
        duplicate_action.triggered.connect(lambda: self._show_coming_soon("Duplicate Page"))
        
        menu.exec(pos)
    
    def load_pages(self, page_count: int, pdf_document):
        """
        Load page thumbnails for document.
        
        Args:
            page_count: Number of pages in document
            pdf_document: PDFDocument instance for thumbnail generation
        """
        from .thumbnail_generator import ThumbnailGenerator
        
        # Update counter
        self.page_counter.setText(f"{page_count} pages")
        
        # Show grid, hide placeholder
        self.pages_placeholder.hide()
        self.pages_grid.show()
        
        # Set page count in grid
        self.pages_grid.set_page_count(page_count)
        
        # Create thumbnail generator
        if self.thumbnail_generator:
            self.thumbnail_generator.cancel()
            self.thumbnail_generator.deleteLater()
        
        self.thumbnail_generator = ThumbnailGenerator(pdf_document, self)
        self.thumbnail_generator.thumbnail_ready.connect(self._on_thumbnail_ready)
        self.thumbnail_generator.progress_updated.connect(self._on_generation_progress)
        
        # Start generating thumbnails for visible pages
        pages_to_load = self.pages_grid.get_pages_to_load()
        current_mode = self.view_mode_combo.currentIndex()
        view_modes = {0: 100, 1: 150, 2: 200}
        thumb_size = view_modes.get(current_mode, 150)
        
        self.thumbnail_generator.generate_thumbnails(pages_to_load, thumb_size)
    
    def _on_thumbnail_ready(self, page_num: int, pixmap):
        """Handle thumbnail generation complete."""
        self.pages_grid.set_thumbnail(page_num, pixmap)
    
    def _on_generation_progress(self, current: int, total: int):
        """Handle thumbnail generation progress."""
        # Could show progress indicator here (Step 12)
        pass
    
    def set_current_page(self, page_num: int):
        """Update current page indicator in grid."""
        self.pages_grid.set_current_page(page_num)
    
    def update_page_annotations(self, page_num: int, has_annotations: bool):
        """Update annotation indicator for a page."""
        self.pages_grid.set_page_has_annotations(page_num, has_annotations)
    
    def load_bookmarks(self, bookmarks: list):
        """
        Load document bookmarks.
        
        Args:
            bookmarks: List of bookmark data
        """
        self.bookmarks_tree.clear()
        # TODO Phase 2: Populate bookmark tree
    
    def clear(self):
        """Clear all content when document is closed."""
        # Clear pages grid
        self.pages_grid.clear()
        self.pages_grid.hide()
        self.pages_placeholder.show()
        
        # Cancel thumbnail generation
        if self.thumbnail_generator:
            self.thumbnail_generator.cancel()
            self.thumbnail_generator = None
        
        # Clear other tabs
        self.bookmarks_tree.clear()
        self.comments_list.clear()
        self.layers_list.clear()
        self.page_counter.setText("0 pages")
        self._clear_search()
