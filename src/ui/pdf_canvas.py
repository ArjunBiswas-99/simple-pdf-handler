"""
PDF canvas widget for displaying rendered PDF pages.
Provides scrollable view with continuous page layout.
"""

from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QCursor
from typing import List, Dict, Optional, Tuple


class PDFCanvas(QScrollArea):
    """
    Scrollable canvas for displaying PDF pages in continuous layout.
    Supports both single page and continuous scrolling modes.
    """
    
    # Signal emitted when the visible page changes during scrolling
    page_changed = pyqtSignal(int)
    
    # Signal emitted when text is selected
    text_selected = pyqtSignal(str)  # selected_text
    
    def __init__(self, parent=None):
        """
        Initialize the PDF canvas.
        
        Args:
            parent: Parent widget, or None for top-level widget
        """
        super().__init__(parent)
        self._page_labels: List[QLabel] = []
        self._continuous_mode = True
        
        # Search highlighting support
        # Dictionary mapping page numbers to lists of search result rectangles
        self._search_highlights: Dict[int, List[QRectF]] = {}
        # Current match rectangle to highlight differently
        self._current_match: Optional[tuple] = None  # (page_number, rect)
        # Zoom level used for coordinate scaling
        self._zoom_level: float = 1.0
        
        # Text selection support
        self._selection_enabled = True
        self._is_selecting = False
        self._selection_start: Optional[QPointF] = None
        self._selection_current: Optional[QPointF] = None
        self._selection_page: Optional[int] = None
        self._selection_rect: Optional[QRectF] = None
        self._selected_text: str = ""
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the canvas layout and appearance."""
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #525252;")
        
        # Enable mouse tracking for cursor changes
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        
        # Create container widget for pages
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._container_layout.setSpacing(10)  # Space between pages
        self._container_layout.setContentsMargins(20, 20, 20, 20)
        
        self.setWidget(self._container)
        
        # Display placeholder when no document is loaded
        self._show_placeholder()
    
    def _show_placeholder(self) -> None:
        """Display placeholder text when no PDF is loaded."""
        # Clear any existing page labels
        self._clear_pages()
        
        # Create placeholder label
        placeholder = QLabel("No PDF loaded\n\nFile → Open to load a PDF document")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(
            "background-color: white; "
            "border: 2px dashed #ccc; "
            "color: #888; "
            "font-size: 14px; "
            "padding: 40px;"
        )
        self._container_layout.addWidget(placeholder)
        self._page_labels = [placeholder]
    
    def display_pages(self, pixmaps: List[QPixmap]) -> None:
        """
        Display multiple PDF pages in continuous scrolling layout.
        
        Args:
            pixmaps: List of QPixmaps, one for each page
        """
        # Clear existing pages
        self._clear_pages()
        
        # Create a label for each page
        for i, pixmap in enumerate(pixmaps):
            if pixmap and not pixmap.isNull():
                # Create custom label that supports painting highlights
                page_label = HighlightableLabel(i)
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Enable mouse tracking for this label
                page_label.setMouseTracking(True)
                
                # Apply search highlights if they exist for this page
                if i in self._search_highlights:
                    page_label.set_highlights(
                        self._search_highlights[i],
                        self._current_match,
                        self._zoom_level
                    )
                
                # Set selection rectangle if on this page
                if self._selection_page == i and self._selection_rect:
                    page_label.set_selection(self._selection_rect, self._zoom_level)
                
                page_label.setPixmap(pixmap)
                page_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
                page_label.setScaledContents(False)
                
                self._container_layout.addWidget(page_label)
                self._page_labels.append(page_label)
    
    def display_single_page(self, pixmap: QPixmap) -> None:
        """
        Display a single PDF page (for single page mode).
        
        Args:
            pixmap: QPixmap containing the rendered page
        """
        # Clear existing pages
        self._clear_pages()
        
        if pixmap and not pixmap.isNull():
            page_label = QLabel()
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label.setPixmap(pixmap)
            page_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
            page_label.setScaledContents(False)
            
            self._container_layout.addWidget(page_label)
            self._page_labels = [page_label]
        else:
            self._show_error("Failed to render page")
    
    def _show_error(self, message: str) -> None:
        """
        Display an error message on the canvas.
        
        Args:
            message: Error message to display
        """
        self._clear_pages()
        
        error_label = QLabel(f"Error: {message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet(
            "background-color: #ffeeee; "
            "border: 2px solid #ff0000; "
            "color: #cc0000; "
            "font-size: 14px; "
            "padding: 40px;"
        )
        self._container_layout.addWidget(error_label)
        self._page_labels = [error_label]
    
    def _clear_pages(self) -> None:
        """Remove all page labels from the layout."""
        # Remove all widgets from layout
        while self._container_layout.count():
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._page_labels.clear()
    
    def clear(self) -> None:
        """Clear the canvas and show placeholder."""
        self._show_placeholder()
    
    def scroll_to_page(self, page_index: int) -> None:
        """
        Scroll to make a specific page visible.
        
        Args:
            page_index: Index of the page to scroll to (0-indexed)
        """
        if 0 <= page_index < len(self._page_labels):
            # Scroll to the specified page label
            widget = self._page_labels[page_index]
            self.ensureWidgetVisible(widget, 0, 0)
    
    def get_visible_page(self) -> int:
        """
        Determine which page is currently most visible in the viewport.
        
        Returns:
            Index of the currently visible page (0-indexed)
        """
        if not self._page_labels:
            return 0
        
        # Get viewport rectangle
        viewport_rect = self.viewport().rect()
        viewport_center = viewport_rect.center()
        
        # Find which page label is closest to the viewport center
        min_distance = float('inf')
        visible_page = 0
        
        for i, label in enumerate(self._page_labels):
            if label.pixmap() is None:
                continue
            
            # Get label position relative to viewport
            label_pos = label.mapTo(self.viewport(), label.rect().center())
            
            # Calculate distance from viewport center
            distance = abs(label_pos.y() - viewport_center.y())
            
            if distance < min_distance:
                min_distance = distance
                visible_page = i
        
        return visible_page
    
    def has_content(self) -> bool:
        """
        Check if the canvas currently displays content.
        
        Returns:
            True if content is displayed, False otherwise
        """
        return len(self._page_labels) > 0 and self._page_labels[0].pixmap() is not None
    
    def set_search_highlights(
        self,
        highlights: Dict[int, List[QRectF]],
        current_match: Optional[tuple],
        zoom_level: float
    ) -> None:
        """
        Set search result highlights to display on pages.
        
        Args:
            highlights: Dictionary mapping page numbers to lists of match rectangles
            current_match: Tuple of (page_number, rect) for the current match, or None
            zoom_level: Current zoom level for coordinate scaling
        """
        self._search_highlights = highlights
        self._current_match = current_match
        self._zoom_level = zoom_level
        
        # Update all existing page labels with highlights
        for i, label in enumerate(self._page_labels):
            if isinstance(label, HighlightableLabel):
                if i in self._search_highlights:
                    label.set_highlights(
                        self._search_highlights[i],
                        self._current_match,
                        self._zoom_level
                    )
                else:
                    label.clear_highlights()
                
                # Trigger repaint
                label.update()
    
    def clear_search_highlights(self) -> None:
        """Clear all search highlights from the canvas."""
        self._search_highlights.clear()
        self._current_match = None
        
        # Clear highlights from all page labels
        for label in self._page_labels:
            if isinstance(label, HighlightableLabel):
                label.clear_highlights()
                label.update()
    
    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press event to start text selection.
        
        Args:
            event: Mouse event
        """
        if not self._selection_enabled or event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        
        # Get which page was clicked
        page_info = self._get_page_at_position(event.pos())
        if page_info is None:
            super().mousePressEvent(event)
            return
        
        page_num, page_label, point_in_page = page_info
        
        # Convert to PDF coordinates (accounting for zoom)
        pdf_point = QPointF(
            point_in_page.x() / self._zoom_level,
            point_in_page.y() / self._zoom_level
        )
        
        # Start selection
        self._is_selecting = True
        self._selection_start = pdf_point
        self._selection_current = pdf_point
        self._selection_page = page_num
        self._update_selection_rect()
        
        # Update display
        if isinstance(page_label, HighlightableLabel):
            page_label.set_selection(self._selection_rect, self._zoom_level)
            page_label.update()
        
        event.accept()
    
    def mouseMoveEvent(self, event) -> None:
        """
        Handle mouse move event to update selection or change cursor.
        
        Args:
            event: Mouse event
        """
        # Change cursor when over text
        page_info = self._get_page_at_position(event.pos())
        if page_info is not None and self._selection_enabled:
            self.viewport().setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        else:
            self.viewport().setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
        # Update selection if actively selecting
        if self._is_selecting and page_info is not None:
            page_num, page_label, point_in_page = page_info
            
            # Only continue selection on the same page
            if page_num == self._selection_page:
                # Convert to PDF coordinates
                pdf_point = QPointF(
                    point_in_page.x() / self._zoom_level,
                    point_in_page.y() / self._zoom_level
                )
                
                self._selection_current = pdf_point
                self._update_selection_rect()
                
                # Update display
                if isinstance(page_label, HighlightableLabel):
                    page_label.set_selection(self._selection_rect, self._zoom_level)
                    page_label.update()
            
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """
        Handle mouse release event to finalize text selection.
        
        Args:
            event: Mouse event
        """
        if self._is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = False
            
            # If selection is too small, clear it
            if self._selection_rect and (
                self._selection_rect.width() < 5 or 
                self._selection_rect.height() < 5
            ):
                self.clear_selection()
            
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def _get_page_at_position(self, pos) -> Optional[Tuple[int, QLabel, QPointF]]:
        """
        Get the page label and relative position for a viewport position.
        
        Args:
            pos: Position in viewport coordinates
            
        Returns:
            Tuple of (page_number, page_label, point_in_page) or None
        """
        # Convert viewport position to container position
        container_pos = self.widget().mapFromParent(pos)
        
        # Check each page label
        for i, label in enumerate(self._page_labels):
            if not isinstance(label, HighlightableLabel) or not label.pixmap():
                continue
            
            # Check if position is within this label
            label_rect = label.geometry()
            if label_rect.contains(container_pos):
                # Get position relative to label
                point_in_label = label.mapFrom(self.widget(), container_pos)
                return (i, label, QPointF(point_in_label))
        
        return None
    
    def _update_selection_rect(self) -> None:
        """Update the selection rectangle based on start and current points."""
        if not self._selection_start or not self._selection_current:
            self._selection_rect = None
            return
        
        x1 = min(self._selection_start.x(), self._selection_current.x())
        y1 = min(self._selection_start.y(), self._selection_current.y())
        x2 = max(self._selection_start.x(), self._selection_current.x())
        y2 = max(self._selection_start.y(), self._selection_current.y())
        
        self._selection_rect = QRectF(x1, y1, x2 - x1, y2 - y1)
    
    def get_selection_info(self) -> Optional[Tuple[int, QRectF]]:
        """
        Get current selection information.
        
        Returns:
            Tuple of (page_number, selection_rect) or None if no selection
        """
        if self._selection_page is not None and self._selection_rect:
            return (self._selection_page, self._selection_rect)
        return None
    
    def clear_selection(self) -> None:
        """Clear the current text selection."""
        self._is_selecting = False
        self._selection_start = None
        self._selection_current = None
        page_to_update = self._selection_page
        self._selection_page = None
        self._selection_rect = None
        self._selected_text = ""
        
        # Update the affected page label
        if page_to_update is not None and 0 <= page_to_update < len(self._page_labels):
            label = self._page_labels[page_to_update]
            if isinstance(label, HighlightableLabel):
                label.clear_selection()
                label.update()
    
    def set_selection_enabled(self, enabled: bool) -> None:
        """
        Enable or disable text selection.
        
        Args:
            enabled: True to enable selection, False to disable
        """
        self._selection_enabled = enabled
        if not enabled:
            self.clear_selection()
    
    def set_zoom_level(self, zoom_level: float) -> None:
        """
        Update the zoom level for coordinate calculations.
        
        Args:
            zoom_level: New zoom level
        """
        self._zoom_level = zoom_level


class HighlightableLabel(QLabel):
    """
    Custom QLabel that can display search highlights and text selection over PDF pages.
    Separates highlighting concerns from the main canvas widget.
    """
    
    def __init__(self, page_number: int, parent=None):
        """
        Initialize the highlightable label.
        
        Args:
            page_number: Page number this label represents (0-indexed)
            parent: Parent widget
        """
        super().__init__(parent)
        self._page_number = page_number
        self._highlights: List[QRectF] = []
        self._current_match: Optional[tuple] = None
        self._zoom_level: float = 1.0
        self._selection_rect: Optional[QRectF] = None
    
    def set_highlights(
        self,
        highlights: List[QRectF],
        current_match: Optional[tuple],
        zoom_level: float
    ) -> None:
        """
        Set search highlights to display on this page.
        
        Args:
            highlights: List of rectangles to highlight
            current_match: Tuple of (page_number, rect) for current match
            zoom_level: Zoom level for coordinate scaling
        """
        self._highlights = highlights
        self._current_match = current_match
        self._zoom_level = zoom_level
    
    def clear_highlights(self) -> None:
        """Clear all highlights from this label."""
        self._highlights.clear()
        self._current_match = None
    
    def set_selection(self, selection_rect: Optional[QRectF], zoom_level: float) -> None:
        """
        Set text selection rectangle to display on this page.
        
        Args:
            selection_rect: Rectangle to show as selection (in PDF coordinates)
            zoom_level: Zoom level for coordinate scaling
        """
        self._selection_rect = selection_rect
        self._zoom_level = zoom_level
    
    def clear_selection(self) -> None:
        """Clear the text selection from this label."""
        self._selection_rect = None
    
    def paintEvent(self, event) -> None:
        """
        Custom paint event to draw highlights and selection over the PDF page.
        
        Args:
            event: Paint event
        """
        # First, let the parent class paint the pixmap
        super().paintEvent(event)
        
        # If no highlights or selection, nothing more to do
        if (not self._highlights and not self._selection_rect) or not self.pixmap():
            return
        
        # Create painter for drawing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw search highlights first (so selection appears on top)
        for rect in self._highlights:
            # Scale rectangle to current zoom level
            scaled_rect = QRectF(
                rect.x() * self._zoom_level,
                rect.y() * self._zoom_level,
                rect.width() * self._zoom_level,
                rect.height() * self._zoom_level
            )
            
            # Check if this is the current match
            is_current = (
                self._current_match is not None and
                self._current_match[0] == self._page_number and
                self._current_match[1] == rect
            )
            
            # Different colors for current match vs. other matches
            if is_current:
                # Current match: orange with higher opacity
                painter.setBrush(QColor(255, 165, 0, 120))  # Orange
                painter.setPen(QPen(QColor(255, 140, 0), 2))  # Dark orange border
            else:
                # Other matches: yellow with lower opacity
                painter.setBrush(QColor(255, 255, 0, 80))  # Yellow
                painter.setPen(QPen(QColor(255, 215, 0), 1))  # Gold border
            
            # Draw the highlight rectangle
            painter.drawRect(scaled_rect)
        
        # Draw text selection on top
        if self._selection_rect:
            scaled_selection = QRectF(
                self._selection_rect.x() * self._zoom_level,
                self._selection_rect.y() * self._zoom_level,
                self._selection_rect.width() * self._zoom_level,
                self._selection_rect.height() * self._zoom_level
            )
            
            # Selection: semi-transparent blue
            painter.setBrush(QColor(38, 128, 235, 60))  # Professional blue
            painter.setPen(QPen(QColor(38, 128, 235, 180), 1))
            painter.drawRect(scaled_selection)
        
        painter.end()
