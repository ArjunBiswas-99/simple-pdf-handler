"""
Simple PDF Handler - Bookmarks Panel

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from ui.styles.design_tokens import SPACING, TYPOGRAPHY, get_color
from ui.styles.theme_manager import get_theme_manager


class BookmarksPanel(QWidget):
    """
    Bookmarks panel for sidebar.
    Shows PDF outline/bookmarks in a tree view.
    """
    
    bookmark_clicked = pyqtSignal(int)  # page number
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bookmarks = []
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the panel UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        layout.setSpacing(SPACING['sm'])
        self.setLayout(layout)
        
        # Title
        self._title = QLabel("BOOKMARKS")
        title_font = QFont(TYPOGRAPHY['font_family'])
        title_font.setPointSize(10)
        title_font.setWeight(TYPOGRAPHY['font_weight_semibold'])
        self._title.setFont(title_font)
        layout.addWidget(self._title)
        
        # Tree widget for bookmarks
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(16)
        self._tree.itemClicked.connect(self._on_bookmark_clicked)
        layout.addWidget(self._tree)
        
        # Empty state message
        self._empty_label = QLabel("No bookmarks")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)
    
    def load_bookmarks(self, bookmarks: list) -> None:
        """
        Load bookmarks into the tree view.
        
        Args:
            bookmarks: List of (level, title, page_number) tuples
        """
        self._bookmarks = bookmarks
        self._tree.clear()
        
        if not bookmarks:
            # Show empty state
            self._tree.hide()
            self._empty_label.show()
            return
        
        # Show tree, hide empty state
        self._tree.show()
        self._empty_label.hide()
        
        # Build tree structure
        # Keep track of parent items at each level
        level_parents = {}
        
        for level, title, page_num in bookmarks:
            # Create tree item
            item = QTreeWidgetItem()
            item.setText(0, title)
            item.setData(0, Qt.ItemDataRole.UserRole, page_num)  # Store page number
            
            # Set tooltip showing page number
            item.setToolTip(0, f"Page {page_num + 1}")
            
            if level == 1:
                # Top level item
                self._tree.addTopLevelItem(item)
                level_parents[level] = item
            else:
                # Nested item - find parent
                parent_level = level - 1
                if parent_level in level_parents:
                    parent = level_parents[parent_level]
                    parent.addChild(item)
                    level_parents[level] = item
                else:
                    # Fallback: add as top level if parent not found
                    self._tree.addTopLevelItem(item)
                    level_parents[level] = item
        
        # Expand all top-level items by default
        for i in range(self._tree.topLevelItemCount()):
            self._tree.topLevelItem(i).setExpanded(True)
    
    def _on_bookmark_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle bookmark item click.
        
        Args:
            item: Clicked tree item
            column: Column index (always 0 for us)
        """
        # Get page number from item data
        page_num = item.data(0, Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.bookmark_clicked.emit(page_num)
    
    def clear(self) -> None:
        """Clear all bookmarks from the tree."""
        self._bookmarks = []
        self._tree.clear()
        self._tree.hide()
        self._empty_label.show()
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        text_color = get_color('text_primary', is_dark)
        text_secondary = get_color('text_secondary', is_dark)
        hover_color = get_color('hover', is_dark)
        selected_color = get_color('primary', is_dark)
        
        self.setStyleSheet(f"""
            BookmarksPanel {{
                background-color: {bg_color};
            }}
        """)
        
        self._title.setStyleSheet(f"color: {text_secondary};")
        self._empty_label.setStyleSheet(f"color: {text_secondary}; padding: 40px;")
        
        # Tree widget styling
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color};
                border: none;
                color: {text_color};
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {hover_color};
            }}
            QTreeWidget::item:selected {{
                background-color: {selected_color};
                color: white;
            }}
            QTreeWidget::branch {{
                background-color: {bg_color};
            }}
        """)
