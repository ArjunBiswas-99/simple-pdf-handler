"""
Simple PDF Handler - Pages/Thumbnails Panel

Displays thumbnail previews of all pages with support for:
- Page selection and navigation
- Edit mode with delete/add page controls
- Drag-and-drop page reordering

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData, QPoint
from PyQt6.QtGui import QPixmap, QDrag
from ui.styles.design_tokens import SPACING, get_color
from ui.styles.theme_manager import get_theme_manager
from ui.sidebar.panels.page_thumbnail_widget import PageThumbnailWidget


class PagesPanel(QWidget):
    """
    Pages/Thumbnails panel for sidebar.
    
    Shows thumbnail previews of all pages with lazy loading.
    Supports edit mode with overlay controls for page management
    and drag-and-drop reordering.
    """
    
    # Navigation signal
    page_clicked = pyqtSignal(int)  # page number (0-indexed)
    
    # Edit mode signals
    delete_page_requested = pyqtSignal(int)  # page number to delete
    insert_page_requested = pyqtSignal(int)  # position to insert blank page
    move_page_requested = pyqtSignal(int, int)  # from_page, to_page
    
    def __init__(self, parent=None):
        """Initialize the pages panel."""
        super().__init__(parent)
        self._thumbnail_widgets = []  # List of PageThumbnailWidget
        self._current_page = -1
        self._edit_mode = False
        
        # Drag and drop state
        self._drag_start_position = None
        self._dragging_page = None
        
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
        
        # Enable drag and drop (will be controlled by edit mode)
        self.setAcceptDrops(False)  # Disabled by default
    
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
            
            # Connect edit mode signals
            thumbnail.delete_page_requested.connect(self._on_delete_page_requested)
            thumbnail.add_page_above_requested.connect(self._on_add_page_requested)
            
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
    
    def set_edit_mode(self, enabled: bool) -> None:
        """
        Enable or disable edit mode.
        Shows overlay controls and enables drag-and-drop when enabled.
        
        Args:
            enabled: True to enable edit mode, False to disable
        """
        self._edit_mode = enabled
        
        # Update all thumbnail widgets
        for thumbnail in self._thumbnail_widgets:
            thumbnail.set_edit_mode(enabled)
        
        # Enable/disable drag and drop
        self.setAcceptDrops(enabled)
        
        # Update cursor for thumbnails in edit mode
        for thumbnail in self._thumbnail_widgets:
            if enabled:
                thumbnail.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                thumbnail.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _on_delete_page_requested(self, page_number: int) -> None:
        """
        Handle delete page request from thumbnail overlay button.
        
        Args:
            page_number: Page to delete (0-indexed)
        """
        self.delete_page_requested.emit(page_number)
    
    def _on_add_page_requested(self, position: int) -> None:
        """
        Handle add page request from thumbnail overlay button.
        
        Args:
            position: Position to insert blank page before (0-indexed)
        """
        self.insert_page_requested.emit(position)
    
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
        # In edit mode, clicking starts drag (handled by mousePressEvent)
        # In normal mode, clicking navigates
        if not self._edit_mode:
            self.page_clicked.emit(page_number)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag-and-drop initiation."""
        if not self._edit_mode:
            super().mousePressEvent(event)
            return
        
        # Find which thumbnail was clicked
        child = self.childAt(event.pos())
        if not child:
            super().mousePressEvent(event)
            return
        
        # Find the thumbnail widget
        thumbnail = None
        while child:
            if isinstance(child, PageThumbnailWidget):
                thumbnail = child
                break
            child = child.parent()
        
        if thumbnail:
            self._drag_start_position = event.pos()
            self._dragging_page = thumbnail.get_page_number()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag-and-drop."""
        if not self._edit_mode or not self._drag_start_position:
            super().mouseMoveEvent(event)
            return
        
        # Check if moved far enough to start drag
        if (event.pos() - self._drag_start_position).manhattanLength() < 10:
            super().mouseMoveEvent(event)
            return
        
        # Start drag operation
        if self._dragging_page is not None and 0 <= self._dragging_page < len(self._thumbnail_widgets):
            thumbnail = self._thumbnail_widgets[self._dragging_page]
            
            # Create drag object
            drag = QDrag(thumbnail)
            mime_data = QMimeData()
            mime_data.setText(str(self._dragging_page))
            drag.setMimeData(mime_data)
            
            # Set drag pixmap (thumbnail preview)
            if thumbnail._thumbnail_pixmap:
                drag.setPixmap(thumbnail._thumbnail_pixmap.scaled(
                    80, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            
            # Change cursor
            thumbnail.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            # Execute drag
            drag.exec(Qt.DropAction.MoveAction)
            
            # Reset cursor
            thumbnail.setCursor(Qt.CursorShape.OpenHandCursor)
            self._drag_start_position = None
            self._dragging_page = None
    
    def dragEnterEvent(self, event):
        """Handle drag enter for drop target."""
        if self._edit_mode and event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move to show drop indicator."""
        if self._edit_mode:
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop to reorder pages."""
        if not self._edit_mode:
            return
        
        # Get source page number
        source_page = int(event.mimeData().text())
        
        # Find target position based on drop location
        drop_pos = event.position().toPoint()  # PyQt6 uses position() instead of pos()
        target_page = self._get_drop_target_page(drop_pos)
        
        if target_page is not None and target_page != source_page:
            # Emit move signal
            self.move_page_requested.emit(source_page, target_page)
            event.acceptProposedAction()
    
    def _get_drop_target_page(self, pos: QPoint) -> int:
        """
        Determine target page number based on drop position.
        
        Args:
            pos: Drop position
            
        Returns:
            Target page number, or None if invalid
        """
        # Map position to scroll area coordinates
        scroll_pos = self._scroll_area.mapFrom(self, pos)
        container_pos = self._thumbnails_container.mapFrom(self._scroll_area, scroll_pos)
        
        # Find which thumbnail is at this position
        for i, thumbnail in enumerate(self._thumbnail_widgets):
            thumb_geometry = thumbnail.geometry()
            if thumb_geometry.contains(container_pos):
                # Drop on thumbnail - check if top half or bottom half
                mid_y = thumb_geometry.center().y()
                if container_pos.y() < mid_y:
                    return i  # Insert before this page
                else:
                    return i + 1  # Insert after this page
        
        # Default to end
        return len(self._thumbnail_widgets)
    
    def update_page_numbers_after_reorder(self) -> None:
        """Update page numbers on all thumbnails after reordering."""
        for i, thumbnail in enumerate(self._thumbnail_widgets):
            thumbnail.update_page_number(i)
    
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
        
        # Reset edit mode
        self._edit_mode = False
        self.setAcceptDrops(False)
    
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
