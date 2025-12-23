"""
Bookmark tree widget component.

Displays PDF bookmarks in a hierarchical tree structure.
"""

from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QLineEdit,
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel,
    QTreeWidgetItemIterator
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QBrush, QColor, QIcon


class BookmarkTreeWidget(QTreeWidget):
    """
    Custom tree widget for displaying PDF bookmarks.
    
    Features:
    - Hierarchical display with visual indicators
    - Click to navigate
    - Search/filter functionality
    - Expand/collapse controls
    - Context menu
    """
    
    # Signals
    bookmark_clicked = Signal(int, float)  # page_number, top_position
    bookmark_double_clicked = Signal(int, float)
    
    def __init__(self, parent=None):
        """
        Initialize bookmark tree widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Configure tree
        self.setHeaderHidden(True)
        self.setIndentation(25)  # More space for bigger arrows
        self.setAnimated(True)  # Smooth expand/collapse
        self.setExpandsOnDoubleClick(False)  # We handle double-click
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Make the branch clickable area larger
        self.setStyleSheet("""
            QTreeWidget {
                outline: 0;
            }
            QTreeWidget::branch {
                background: palette(base);
                width: 20px;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
        """)
        
        # Use built-in arrows with proper coloring
        # This ensures arrows are visible in both light and dark themes
        self.setStyleSheet("""
            QTreeWidget {
                outline: 0;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
        """)
        
        # Override the item delegate to draw custom arrows
        from PySide6.QtWidgets import QStyledItemDelegate
        from PySide6.QtGui import QPainter, QPen
        from PySide6.QtCore import QRect, QPoint
        
        class ArrowDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                super().paint(painter, option, index)
                
                # Draw arrow for items with children
                item = self.parent().itemFromIndex(index)
                if item and item.childCount() > 0:
                    painter.save()
                    
                    # Set arrow color (dark gray for visibility)
                    pen = QPen(QColor(80, 80, 80))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # Calculate arrow position (left side of item)
                    rect = option.rect
                    arrow_x = rect.left() - 12
                    arrow_y = rect.center().y()
                    
                    # Draw LARGER arrow based on expansion state
                    if item.isExpanded():
                        # Down arrow (▼) - BIGGER
                        points = [
                            QPoint(arrow_x - 6, arrow_y - 3),
                            QPoint(arrow_x + 6, arrow_y - 3),
                            QPoint(arrow_x, arrow_y + 4)
                        ]
                    else:
                        # Right arrow (▶) - BIGGER
                        points = [
                            QPoint(arrow_x - 3, arrow_y - 6),
                            QPoint(arrow_x - 3, arrow_y + 6),
                            QPoint(arrow_x + 4, arrow_y)
                        ]
                    
                    painter.setBrush(QColor(80, 80, 80))
                    painter.drawPolygon(points)
                    
                    painter.restore()
        
        self.setItemDelegate(ArrowDelegate(self))
        
        # Track bookmarks data
        self._bookmarks = []
        self._current_page = -1
        self._search_filter = ""
        
        # Expansion state
        self._expanded_items = set()  # Track expanded bookmark titles
        
        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
    
    def load_bookmarks(self, bookmarks: list):
        """
        Load and display bookmarks.
        
        Args:
            bookmarks: List of bookmark dictionaries from PDFDocument
        """
        self._bookmarks = bookmarks
        self.clear()
        self._expanded_items.clear()
        
        if not bookmarks:
            return
        
        # Build tree recursively
        self._build_tree_recursive(bookmarks, None)
        
        # Auto-expand first level
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                item.setExpanded(True)
    
    def _build_tree_recursive(self, bookmarks: list, parent_item: QTreeWidgetItem):
        """
        Recursively build bookmark tree.
        
        Args:
            bookmarks: List of bookmark dictionaries
            parent_item: Parent tree item (None for top-level)
        """
        for bookmark in bookmarks:
            # Create tree item
            if parent_item:
                item = QTreeWidgetItem(parent_item)
            else:
                item = QTreeWidgetItem(self)
            
            # Store bookmark data
            item.setData(0, Qt.UserRole, bookmark)
            
            # Set text with icon
            title = bookmark['title']
            page = bookmark['page']
            has_children = len(bookmark.get('children', [])) > 0
            
            # Choose icon based on whether it has children
            icon = "📁" if has_children else "📄"
            display_text = f"{icon} {title}"
            
            item.setText(0, display_text)
            item.setToolTip(0, f"{title}\nPage {page + 1}")
            
            # Style based on level
            level = bookmark['level']
            self._style_item(item, level, has_children)
            
            # Recursively add children
            children = bookmark.get('children', [])
            if children:
                self._build_tree_recursive(children, item)
    
    def _style_item(self, item: QTreeWidgetItem, level: int, has_children: bool):
        """
        Apply visual styling to tree item based on hierarchy level.
        
        Args:
            item: Tree widget item
            level: Hierarchy level (1=top, 2=child, etc.)
            has_children: Whether item has children
        """
        font = QFont()
        
        # Top-level bookmarks: larger, bold
        if level == 1:
            font.setPointSize(11)
            font.setWeight(QFont.Weight.DemiBold)
            item.setFont(0, font)
        # Second level: slightly larger
        elif level == 2:
            font.setPointSize(10)
            item.setFont(0, font)
        # Deeper levels: normal
        else:
            font.setPointSize(9)
            item.setFont(0, font)
        
        # Parent items: darker text
        if has_children:
            item.setForeground(0, QBrush(QColor(50, 50, 50)))
        else:
            item.setForeground(0, QBrush(QColor(80, 80, 80)))
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle bookmark item click.
        
        Args:
            item: Clicked item
            column: Column number
        """
        bookmark = item.data(0, Qt.UserRole)
        if bookmark:
            page = bookmark['page']
            top = bookmark.get('top', 0)
            self.bookmark_clicked.emit(page, top)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle bookmark item double-click.
        
        Args:
            item: Double-clicked item
            column: Column number
        """
        bookmark = item.data(0, Qt.UserRole)
        if bookmark:
            page = bookmark['page']
            top = bookmark.get('top', 0)
            self.bookmark_double_clicked.emit(page, top)
    
    def _on_item_expanded(self, item: QTreeWidgetItem):
        """Track expanded items."""
        bookmark = item.data(0, Qt.UserRole)
        if bookmark:
            self._expanded_items.add(bookmark['title'])
    
    def _on_item_collapsed(self, item: QTreeWidgetItem):
        """Track collapsed items."""
        bookmark = item.data(0, Qt.UserRole)
        if bookmark:
            self._expanded_items.discard(bookmark['title'])
    
    def set_current_page(self, page_num: int):
        """
        Update current page indicator.
        
        Args:
            page_num: Current page number (0-indexed)
        """
        self._current_page = page_num
        self._update_current_indicator()
    
    def _update_current_indicator(self):
        """Update visual indicator for current page's bookmark."""
        # Find and highlight bookmark for current page
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            bookmark = item.data(0, Qt.UserRole)
            if bookmark and bookmark['page'] == self._current_page:
                # Highlight this item
                item.setBackground(0, QBrush(QColor(173, 216, 230, 100)))  # Light blue
            else:
                # Clear background
                item.setBackground(0, QBrush(Qt.transparent))
            iterator += 1
    
    def expand_all_bookmarks(self):
        """Expand all bookmark items."""
        self.expandAll()
        
        # Track all as expanded
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            bookmark = item.data(0, Qt.UserRole)
            if bookmark:
                self._expanded_items.add(bookmark['title'])
            iterator += 1
    
    def collapse_all_bookmarks(self):
        """Collapse all bookmark items."""
        self.collapseAll()
        self._expanded_items.clear()
    
    def expand_to_page(self, page_num: int):
        """
        Expand tree to show bookmark for specific page.
        
        Args:
            page_num: Page number (0-indexed)
        """
        # Find item for this page
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            bookmark = item.data(0, Qt.UserRole)
            if bookmark and bookmark['page'] == page_num:
                # Expand all parents
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()
                
                # Scroll to item
                self.scrollToItem(item)
                return
            iterator += 1
    
    def filter_bookmarks(self, search_text: str):
        """
        Filter visible bookmarks by search text.
        
        Args:
            search_text: Text to search for (case-insensitive)
        """
        self._search_filter = search_text.lower()
        
        if not search_text:
            # Show all items
            iterator = QTreeWidgetItemIterator(self)
            while iterator.value():
                iterator.value().setHidden(False)
                iterator += 1
            return
        
        # Hide items that don't match, show those that do
        iterator = QTreeWidgetItemIterator(self)
        match_count = 0
        
        while iterator.value():
            item = iterator.value()
            bookmark = item.data(0, Qt.UserRole)
            
            if bookmark:
                title = bookmark['title'].lower()
                matches = search_text in title
                
                if matches:
                    match_count += 1
                    # Show this item and all parents
                    item.setHidden(False)
                    parent = item.parent()
                    while parent:
                        parent.setHidden(False)
                        parent.setExpanded(True)  # Auto-expand parents
                        parent = parent.parent()
                else:
                    # Hide if no children match
                    if not self._has_matching_children(item, search_text):
                        item.setHidden(True)
            
            iterator += 1
        
        return match_count
    
    def _has_matching_children(self, item: QTreeWidgetItem, search_text: str) -> bool:
        """
        Check if item has any children matching search.
        
        Args:
            item: Tree item to check
            search_text: Search text
            
        Returns:
            True if any children match
        """
        for i in range(item.childCount()):
            child = item.child(i)
            bookmark = child.data(0, Qt.UserRole)
            if bookmark:
                if search_text in bookmark['title'].lower():
                    return True
                if self._has_matching_children(child, search_text):
                    return True
        return False
    
    def _show_context_menu(self, position):
        """
        Show context menu for bookmark.
        
        Args:
            position: Menu position
        """
        item = self.itemAt(position)
        if not item:
            return
        
        bookmark = item.data(0, Qt.UserRole)
        if not bookmark:
            return
        
        menu = QMenu(self)
        
        # Go to bookmark
        page = bookmark['page']
        go_action = menu.addAction(f"📄 Go to Page {page + 1}")
        go_action.triggered.connect(lambda: self.bookmark_clicked.emit(page, bookmark.get('top', 0)))
        
        menu.addSeparator()
        
        # Expand/collapse actions (if has children)
        if item.childCount() > 0:
            if item.isExpanded():
                collapse_action = menu.addAction("Collapse")
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
            else:
                expand_action = menu.addAction("Expand")
                expand_action.triggered.connect(lambda: item.setExpanded(True))
            
            menu.addSeparator()
        
        # Copy bookmark title
        copy_action = menu.addAction("Copy Title")
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(bookmark['title']))
        
        # Future features (Phase 3)
        menu.addSeparator()
        add_action = menu.addAction("Add Child Bookmark [Phase 3]")
        add_action.setEnabled(False)
        
        edit_action = menu.addAction("Edit Bookmark [Phase 3]")
        edit_action.setEnabled(False)
        
        delete_action = menu.addAction("Delete Bookmark [Phase 3]")
        delete_action.setEnabled(False)
        
        menu.exec(self.mapToGlobal(position))
    
    def _copy_to_clipboard(self, text: str):
        """
        Copy text to clipboard.
        
        Args:
            text: Text to copy
        """
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    def get_bookmark_count(self) -> int:
        """
        Get total number of bookmarks.
        
        Returns:
            Total bookmark count
        """
        count = 0
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            count += 1
            iterator += 1
        return count


class BookmarkPanel(QWidget):
    """
    Complete bookmark panel with tree, search, and controls.
    """
    
    # Signals
    bookmark_selected = Signal(int, float)  # page, top
    
    def __init__(self, parent=None):
        """Initialize bookmark panel."""
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Header with title and count
        header_layout = QHBoxLayout()
        
        title = QLabel("Bookmarks")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 bookmarks")
        self.count_label.setProperty("secondary", True)
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search bookmarks...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        # Fix clear button positioning and visibility
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 4px 24px 4px 4px;
                min-height: 24px;
            }
            QLineEdit QToolButton {
                border: none;
                padding: 2px;
                margin-right: 2px;
            }
        """)
        
        layout.addWidget(self.search_input)
        
        # Results count (shown during search)
        self.results_label = QLabel()
        self.results_label.setProperty("secondary", True)
        self.results_label.hide()
        layout.addWidget(self.results_label)
        
        # Bookmark tree
        self.tree = BookmarkTreeWidget()
        self.tree.bookmark_clicked.connect(self.bookmark_selected.emit)
        self.tree.bookmark_double_clicked.connect(self.bookmark_selected.emit)
        layout.addWidget(self.tree)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.tree.expand_all_bookmarks)
        button_layout.addWidget(self.expand_all_btn)
        
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.tree.collapse_all_bookmarks)
        button_layout.addWidget(self.collapse_all_btn)
        
        layout.addLayout(button_layout)
        
        # Search debounce timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
    
    def load_bookmarks(self, bookmarks: list):
        """
        Load bookmarks into tree.
        
        Args:
            bookmarks: List of bookmark dictionaries
        """
        self.tree.load_bookmarks(bookmarks)
        count = self.tree.get_bookmark_count()
        self.count_label.setText(f"{count} bookmark{'s' if count != 1 else ''}")
        
        # Enable/disable buttons
        has_bookmarks = count > 0
        self.expand_all_btn.setEnabled(has_bookmarks)
        self.collapse_all_btn.setEnabled(has_bookmarks)
        self.search_input.setEnabled(has_bookmarks)
    
    def set_current_page(self, page_num: int):
        """Update current page indicator."""
        self.tree.set_current_page(page_num)
    
    def clear(self):
        """Clear all bookmarks."""
        self.tree.clear()
        self.count_label.setText("0 bookmarks")
        self.search_input.clear()
        self.results_label.hide()
        self.expand_all_btn.setEnabled(False)
        self.collapse_all_btn.setEnabled(False)
        self.search_input.setEnabled(False)
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debounce."""
        self._search_timer.stop()
        if text:
            self._search_timer.start(300)  # 300ms debounce
        else:
            self._perform_search()  # Clear immediately
    
    def _perform_search(self):
        """Perform bookmark search/filter."""
        search_text = self.search_input.text()
        
        if search_text:
            match_count = self.tree.filter_bookmarks(search_text)
            self.results_label.setText(f"{match_count} match{'es' if match_count != 1 else ''}")
            self.results_label.show()
        else:
            self.tree.filter_bookmarks("")
            self.results_label.hide()
