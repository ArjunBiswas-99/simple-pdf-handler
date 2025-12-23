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
        
        layout.addWidget(self.tabs)
        
        self.setWidget(container)
        self.setMinimumWidth(WindowDefaults.LEFT_SIDEBAR_WIDTH)
    
    def _create_pages_tab(self):
        """Create pages panel with thumbnails."""
        pages_widget = QWidget()
        layout = QVBoxLayout(pages_widget)
        layout.setSpacing(Spacing.SMALL)
        
        # Header
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
        layout.addLayout(header_layout)
        
        # Thumbnail grid (placeholder)
        self.pages_list = QListWidget()
        self.pages_list.setViewMode(QListWidget.IconMode)
        self.pages_list.setIconSize(self.pages_list.iconSize() * 3)
        self.pages_list.setSpacing(Spacing.SMALL)
        self.pages_list.setResizeMode(QListWidget.Adjust)
        layout.addWidget(self.pages_list)
        
        # Placeholder message
        placeholder = QLabel(f"{Icons.PAGES}\n\nPage Thumbnails\n\n(Generated when PDF is opened)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setProperty("secondary", True)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(pages_widget, f"{Icons.PAGES} Pages")
    
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
        
        self.tabs.addTab(bookmarks_widget, f"{Icons.BOOKMARKS} Bookmarks")
    
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
        
        self.tabs.addTab(comments_widget, f"{Icons.COMMENT} Comments")
    
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
        
        self.tabs.addTab(search_widget, f"{Icons.SEARCH} Search")
    
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
        
        self.tabs.addTab(layers_widget, "📄 Layers")
    
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
    
    def load_pages(self, page_count: int):
        """
        Load page thumbnails.
        
        Args:
            page_count: Number of pages in document
        """
        self.page_counter.setText(f"{page_count} pages")
        # TODO Phase 2: Generate and display thumbnails
    
    def load_bookmarks(self, bookmarks: list):
        """
        Load document bookmarks.
        
        Args:
            bookmarks: List of bookmark data
        """
        self.bookmarks_tree.clear()
        # TODO Phase 2: Populate bookmark tree
    
    def clear(self):
        """Clear all content."""
        self.pages_list.clear()
        self.bookmarks_tree.clear()
        self.comments_list.clear()
        self.layers_list.clear()
        self.page_counter.setText("0 pages")
        self._clear_search()
