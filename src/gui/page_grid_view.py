"""
Page grid view container for displaying thumbnail grid.

Manages layout and viewport-based lazy loading of page thumbnails.
"""

from PySide6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRect, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from typing import List, Dict, Optional

from .page_thumbnail_widget import PageThumbnailWidget


class PageGridView(QScrollArea):
    """
    Scrollable grid view for page thumbnails.
    
    Displays thumbnails in a grid layout with viewport-based lazy loading.
    Only creates and updates visible thumbnails for performance.
    """
    
    # Signals
    page_clicked = Signal(int)  # page_number
    page_double_clicked = Signal(int)  # page_number
    context_menu_requested = Signal(int, object)  # page_number, QPoint
    selection_changed = Signal(list)  # selected_page_numbers
    
    def __init__(self, parent=None):
        """
        Initialize page grid view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._thumbnail_widgets: Dict[int, PageThumbnailWidget] = {}
        self._page_count = 0
        self._current_page = -1
        self._selected_pages = set()
        self._last_clicked_page = -1  # Track for Shift+Click range selection
        self._focused_page = -1  # Track for keyboard navigation
        self._thumbnails_per_row = 2  # Default: medium size
        self._thumb_size = 150
        
        # Viewport lazy loading
        self._visible_buffer = 5  # Render 5 pages above/below viewport
        self._last_viewport_rect = QRect()
        
        # Debounce timer for scroll events
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self._update_visible_thumbnails)
        
        # Scroll animation
        self._scroll_animation = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the scroll area and grid layout."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        self._container = QWidget()
        self._container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWidget(self._container)
        
        # Create grid layout
        self._grid_layout = QGridLayout(self._container)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setContentsMargins(8, 8, 8, 8)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
    
    def set_page_count(self, count: int):
        """
        Set the total number of pages.
        
        Args:
            count: Total page count
        """
        self._page_count = count
        self._rebuild_grid()
    
    def _rebuild_grid(self):
        """Rebuild the thumbnail grid layout."""
        # Clear existing widgets
        self._clear_grid()
        
        # Calculate grid dimensions
        row = 0
        col = 0
        
        # Create placeholder widgets for all pages
        for page_num in range(self._page_count):
            # Create thumbnail widget
            thumb_widget = PageThumbnailWidget(page_num, self._container)
            thumb_widget.clicked.connect(self._on_thumbnail_clicked)
            thumb_widget.double_clicked.connect(self._on_thumbnail_double_clicked)
            thumb_widget.context_menu_requested.connect(self._on_context_menu)
            
            # Add to grid
            self._grid_layout.addWidget(thumb_widget, row, col)
            self._thumbnail_widgets[page_num] = thumb_widget
            
            # Update position for next widget
            col += 1
            if col >= self._thumbnails_per_row:
                col = 0
                row += 1
        
        # Trigger viewport update after layout is complete
        QTimer.singleShot(100, self._update_visible_thumbnails)
    
    def _clear_grid(self):
        """Clear all widgets from grid."""
        # Remove all widgets
        for widget in self._thumbnail_widgets.values():
            self._grid_layout.removeWidget(widget)
            widget.deleteLater()
        
        self._thumbnail_widgets.clear()
    
    def set_thumbnail(self, page_num: int, pixmap):
        """
        Set thumbnail for a specific page.
        
        Args:
            page_num: Page number (0-indexed)
            pixmap: Thumbnail pixmap
        """
        if page_num in self._thumbnail_widgets:
            self._thumbnail_widgets[page_num].set_thumbnail(pixmap)
    
    def set_current_page(self, page_num: int):
        """
        Set the current page indicator.
        
        Args:
            page_num: Page number (0-indexed)
        """
        # Remove current indicator from previous page
        if self._current_page in self._thumbnail_widgets:
            self._thumbnail_widgets[self._current_page].set_current(False)
        
        # Set current indicator on new page
        self._current_page = page_num
        if page_num in self._thumbnail_widgets:
            self._thumbnail_widgets[page_num].set_current(True)
            
            # Auto-scroll to keep current page visible
            self._scroll_to_page(page_num)
    
    def set_page_modified(self, page_num: int, is_modified: bool):
        """
        Set modified indicator for a page.
        
        Args:
            page_num: Page number (0-indexed)
            is_modified: True if page is modified
        """
        if page_num in self._thumbnail_widgets:
            self._thumbnail_widgets[page_num].set_modified(is_modified)
    
    def set_page_has_annotations(self, page_num: int, has_annotations: bool):
        """
        Set annotation indicator for a page.
        
        Args:
            page_num: Page number (0-indexed)
            has_annotations: True if page has annotations
        """
        if page_num in self._thumbnail_widgets:
            self._thumbnail_widgets[page_num].set_has_annotations(has_annotations)
    
    def set_view_mode(self, thumbnails_per_row: int, thumb_size: int):
        """
        Change the grid view mode.
        
        Args:
            thumbnails_per_row: Number of thumbnails per row (1, 2, or 3)
            thumb_size: Thumbnail size in pixels
        """
        self._thumbnails_per_row = thumbnails_per_row
        self._thumb_size = thumb_size
        self._rebuild_grid()
    
    def get_visible_page_range(self) -> tuple:
        """
        Get the range of currently visible pages.
        
        Returns:
            Tuple of (first_visible, last_visible) page numbers
        """
        viewport_rect = self.viewport().rect()
        visible_pages = []
        
        for page_num, widget in self._thumbnail_widgets.items():
            # Get widget position relative to viewport
            widget_pos = widget.mapTo(self.viewport(), widget.rect().topLeft())
            widget_rect = QRect(widget_pos, widget.size())
            
            # Check if widget intersects viewport
            if viewport_rect.intersects(widget_rect):
                visible_pages.append(page_num)
        
        if visible_pages:
            return (min(visible_pages), max(visible_pages))
        return (0, 0)
    
    def get_pages_to_load(self) -> List[int]:
        """
        Get list of pages that should be loaded.
        
        Includes visible pages plus buffer above and below.
        
        Returns:
            List of page numbers to load
        """
        first_visible, last_visible = self.get_visible_page_range()
        
        # Add buffer
        first_load = max(0, first_visible - self._visible_buffer)
        last_load = min(self._page_count - 1, last_visible + self._visible_buffer)
        
        return list(range(first_load, last_load + 1))
    
    def _update_visible_thumbnails(self):
        """Update which thumbnails should be visible/loaded."""
        # This will be called by parent to request thumbnail generation
        # for visible pages
        pass
    
    def _scroll_to_page(self, page_num: int, animate: bool = True):
        """
        Scroll to make a specific page visible with smooth animation.
        
        Args:
            page_num: Page number (0-indexed)
            animate: Whether to animate the scroll (default: True)
        """
        if page_num not in self._thumbnail_widgets:
            return
        
        widget = self._thumbnail_widgets[page_num]
        
        if not animate:
            # Instant scroll
            self.ensureWidgetVisible(widget, 50, 50)
            return
        
        # Calculate target scroll position
        widget_pos = widget.mapTo(self._container, widget.rect().topLeft())
        target_y = widget_pos.y() - (self.viewport().height() // 2) + (widget.height() // 2)
        
        # Clamp to valid range
        scrollbar = self.verticalScrollBar()
        target_y = max(scrollbar.minimum(), min(scrollbar.maximum(), target_y))
        
        # Cancel any existing animation
        if self._scroll_animation and self._scroll_animation.state() == QPropertyAnimation.Running:
            self._scroll_animation.stop()
        
        # Create smooth scroll animation
        self._scroll_animation = QPropertyAnimation(scrollbar, b"value")
        self._scroll_animation.setDuration(300)  # 300ms
        self._scroll_animation.setStartValue(scrollbar.value())
        self._scroll_animation.setEndValue(target_y)
        self._scroll_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._scroll_animation.start()
    
    def _on_scroll(self, value):
        """
        Handle scroll event with debouncing.
        
        Args:
            value: Scroll bar value
        """
        # Debounce scroll events
        self._scroll_timer.start(100)  # 100ms delay
    
    def _on_thumbnail_clicked(self, page_num: int):
        """
        Handle thumbnail click.
        
        Args:
            page_num: Clicked page number
        """
        # Handle selection with Ctrl/Shift modifiers
        from PySide6.QtWidgets import QApplication
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.ControlModifier:
            # Ctrl+Click: Toggle selection
            if page_num in self._selected_pages:
                self._selected_pages.remove(page_num)
                self._thumbnail_widgets[page_num].set_selected(False)
            else:
                self._selected_pages.add(page_num)
                self._thumbnail_widgets[page_num].set_selected(True)
            self._last_clicked_page = page_num
        elif modifiers & Qt.ShiftModifier:
            # Shift+Click: Range selection
            if self._last_clicked_page >= 0:
                # Select range between last clicked and current
                start = min(self._last_clicked_page, page_num)
                end = max(self._last_clicked_page, page_num)
                
                # Clear previous selection
                self._clear_selection()
                
                # Select all pages in range
                for p in range(start, end + 1):
                    if p in self._thumbnail_widgets:
                        self._selected_pages.add(p)
                        self._thumbnail_widgets[p].set_selected(True)
                
                # Emit selection change
                self.selection_changed.emit(self.get_selected_pages())
            else:
                # No previous click, just select this one
                self._selected_pages.add(page_num)
                self._thumbnail_widgets[page_num].set_selected(True)
                self._last_clicked_page = page_num
        else:
            # Normal click: Clear selection and navigate
            self._clear_selection()
            self._last_clicked_page = page_num
            self.page_clicked.emit(page_num)
    
    def _on_thumbnail_double_clicked(self, page_num: int):
        """
        Handle thumbnail double-click.
        
        Args:
            page_num: Double-clicked page number
        """
        self.page_double_clicked.emit(page_num)
    
    def _on_context_menu(self, page_num: int, pos):
        """
        Handle context menu request.
        
        Args:
            page_num: Page number
            pos: Global position for menu
        """
        self.context_menu_requested.emit(page_num, pos)
    
    def _clear_selection(self):
        """Clear all selected thumbnails."""
        for page_num in self._selected_pages:
            if page_num in self._thumbnail_widgets:
                self._thumbnail_widgets[page_num].set_selected(False)
        self._selected_pages.clear()
        self.selection_changed.emit([])
    
    def get_selected_pages(self) -> List[int]:
        """
        Get list of selected page numbers.
        
        Returns:
            List of selected page numbers
        """
        return sorted(list(self._selected_pages))
    
    def keyPressEvent(self, event):
        """
        Handle keyboard navigation.
        
        Args:
            event: Key event
        """
        key = event.key()
        
        # Initialize focused page if not set
        if self._focused_page < 0 and self._page_count > 0:
            self._focused_page = self._current_page if self._current_page >= 0 else 0
        
        if key == Qt.Key_Up:
            # Move focus up (previous row)
            new_focus = self._focused_page - self._thumbnails_per_row
            if new_focus >= 0:
                self._focused_page = new_focus
                self._scroll_to_page(self._focused_page)
            event.accept()
        elif key == Qt.Key_Down:
            # Move focus down (next row)
            new_focus = self._focused_page + self._thumbnails_per_row
            if new_focus < self._page_count:
                self._focused_page = new_focus
                self._scroll_to_page(self._focused_page)
            event.accept()
        elif key == Qt.Key_Left:
            # Move focus left (previous page)
            if self._focused_page > 0:
                self._focused_page -= 1
                self._scroll_to_page(self._focused_page)
            event.accept()
        elif key == Qt.Key_Right:
            # Move focus right (next page)
            if self._focused_page < self._page_count - 1:
                self._focused_page += 1
                self._scroll_to_page(self._focused_page)
            event.accept()
        elif key == Qt.Key_Home:
            # Jump to first page
            self._focused_page = 0
            self._scroll_to_page(self._focused_page)
            event.accept()
        elif key == Qt.Key_End:
            # Jump to last page
            self._focused_page = self._page_count - 1
            self._scroll_to_page(self._focused_page)
            event.accept()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            # Navigate to focused page in main view
            if 0 <= self._focused_page < self._page_count:
                self.page_clicked.emit(self._focused_page)
            event.accept()
        elif key == Qt.Key_PageUp:
            # Scroll up by viewport height
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() - self.viewport().height())
            event.accept()
        elif key == Qt.Key_PageDown:
            # Scroll down by viewport height
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() + self.viewport().height())
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def clear(self):
        """Clear all thumbnails."""
        self._clear_grid()
        self._page_count = 0
        self._current_page = -1
        self._selected_pages.clear()
        self._focused_page = -1
