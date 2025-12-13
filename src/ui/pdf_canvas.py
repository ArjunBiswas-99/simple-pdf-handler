"""
PDF canvas widget for displaying rendered PDF pages.
Provides scrollable view with continuous page layout.
"""

from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from typing import List, Dict, Optional


class PDFCanvas(QScrollArea):
    """
    Scrollable canvas for displaying PDF pages in continuous layout.
    Supports both single page and continuous scrolling modes.
    """
    
    # Signal emitted when the visible page changes during scrolling
    page_changed = pyqtSignal(int)
    
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
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the canvas layout and appearance."""
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #525252;")
        
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
                
                # Apply search highlights if they exist for this page
                if i in self._search_highlights:
                    page_label.set_highlights(
                        self._search_highlights[i],
                        self._current_match,
                        self._zoom_level
                    )
                
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


class HighlightableLabel(QLabel):
    """
    Custom QLabel that can display search highlights over PDF pages.
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
    
    def paintEvent(self, event) -> None:
        """
        Custom paint event to draw highlights over the PDF page.
        
        Args:
            event: Paint event
        """
        # First, let the parent class paint the pixmap
        super().paintEvent(event)
        
        # If no highlights, nothing more to do
        if not self._highlights or not self.pixmap():
            return
        
        # Create painter for drawing highlights
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw each highlight rectangle
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
        
        painter.end()
