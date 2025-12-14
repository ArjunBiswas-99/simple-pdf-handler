"""
Simple PDF Handler - Pages/Thumbnails Panel

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from ui.styles.design_tokens import SPACING, get_color
from ui.styles.theme_manager import get_theme_manager
from ui.sidebar.panels.page_thumbnail_widget import PageThumbnailWidget


class PagesPanel(QWidget):
    """
    Pages/Thumbnails panel for sidebar.
    Shows thumbnail previews of all pages with lazy loading.
    """
    
    page_clicked = pyqtSignal(int)  # page number (0-indexed)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thumbnail_widgets = []  # List of PageThumbnailWidget
        self._current_page = -1
        
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the panel UI."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Title section
        title_container = QWidget()
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['sm'])
        title_container.setLayout(title_layout)
        
        title = QLabel("PAGES")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        title_layout.addWidget(title)
        
        main_layout.addWidget(title_container)
        
        # Scroll area for thumbnails
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(self._scroll_area)
        
        # Container widget for thumbnails
        self._thumbnails_container = QWidget()
        self._thumbnails_layout = QVBoxLayout()
        self._thumbnails_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        self._thumbnails_layout.setSpacing(SPACING['sm'])
        self._thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._thumbnails_container.setLayout(self._thumbnails_layout)
        
        self._scroll_area.setWidget(self._thumbnails_container)
        
        # Empty state message (shown when no document loaded)
        self._empty_label = QLabel("No document loaded")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: gray; padding: 40px;")
        self._thumbnails_layout.addWidget(self._empty_label)
    
    def load_pages(self, page_count: int) -> None:
        """
        Initialize thumbnail widgets for all pages.
        
        Args:
            page_count: Total number of pages in document
        """
        # Clear existing thumbnails
        self.clear()
        
        # Hide empty label
        self._empty_label.hide()
        
        # Create thumbnail widget for each page
        for page_num in range(page_count):
            thumbnail = PageThumbnailWidget(page_num)
            thumbnail.clicked.connect(self._on_thumbnail_clicked)
            
            self._thumbnail_widgets.append(thumbnail)
            self._thumbnails_layout.addWidget(thumbnail)
        
        # Add stretch at the end to keep thumbnails at top
        self._thumbnails_layout.addStretch()
    
    def set_thumbnail(self, page_number: int, pixmap: QPixmap) -> None:
        """
        Set the thumbnail image for a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            pixmap: Rendered thumbnail pixmap
        """
        if 0 <= page_number < len(self._thumbnail_widgets):
            self._thumbnail_widgets[page_number].set_thumbnail(pixmap)
    
    def set_current_page(self, page_number: int) -> None:
        """
        Update the currently selected page.
        
        Args:
            page_number: Page number (0-indexed)
        """
        if page_number == self._current_page:
            return
        
        # Deselect previous page
        if 0 <= self._current_page < len(self._thumbnail_widgets):
            self._thumbnail_widgets[self._current_page].set_selected(False)
        
        # Select new page
        self._current_page = page_number
        if 0 <= page_number < len(self._thumbnail_widgets):
            self._thumbnail_widgets[page_number].set_selected(True)
            
            # Auto-scroll to show selected thumbnail
            self._scroll_to_thumbnail(page_number)
    
    def _scroll_to_thumbnail(self, page_number: int) -> None:
        """
        Scroll to make a specific thumbnail visible.
        
        Args:
            page_number: Page number (0-indexed)
        """
        if 0 <= page_number < len(self._thumbnail_widgets):
            thumbnail = self._thumbnail_widgets[page_number]
            # Ensure thumbnail is visible in scroll area
            self._scroll_area.ensureWidgetVisible(thumbnail, 50, 50)
    
    def _on_thumbnail_clicked(self, page_number: int) -> None:
        """
        Handle thumbnail click.
        
        Args:
            page_number: Clicked page number (0-indexed)
        """
        self.page_clicked.emit(page_number)
    
    def clear(self) -> None:
        """Clear all thumbnails."""
        # Remove all thumbnail widgets
        for thumbnail in self._thumbnail_widgets:
            self._thumbnails_layout.removeWidget(thumbnail)
            thumbnail.deleteLater()
        
        self._thumbnail_widgets.clear()
        self._current_page = -1
        
        # Show empty label
        self._empty_label.show()
    
    def get_thumbnail_count(self) -> int:
        """Get the number of loaded thumbnails."""
        return len(self._thumbnail_widgets)
    
    def get_loading_thumbnails(self) -> list:
        """Get list of page numbers that are still loading."""
        return [
            i for i, thumb in enumerate(self._thumbnail_widgets)
            if thumb.is_loading()
        ]
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        bg_color = get_color('surface', is_dark)
        
        self.setStyleSheet(f"""
            PagesPanel {{
                background-color: {bg_color};
            }}
        """)
        
        self._scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {bg_color};
                border: none;
            }}
        """)
        
        self._thumbnails_container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
            }}
        """)
