"""
Page thumbnail widget for sidebar pages panel.

Displays a single page thumbnail with page number and visual indicators.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont, QPalette


class PageThumbnailWidget(QWidget):
    """
    Widget representing a single page thumbnail.
    
    Displays thumbnail image, page number, and visual indicators for
    current page, modifications, and annotations. Handles user interactions
    including clicks, hover, and context menu.
    """
    
    # Signals
    clicked = Signal(int)  # page_number
    double_clicked = Signal(int)  # page_number
    context_menu_requested = Signal(int, object)  # page_number, QPoint
    
    def __init__(self, page_number: int, parent=None):
        """
        Initialize thumbnail widget.
        
        Args:
            page_number: Page number (0-indexed)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._page_number = page_number
        self._thumbnail = None
        self._is_current = False
        self._is_selected = False
        self._is_modified = False
        self._has_annotations = False
        self._is_hovered = False
        
        # Hover timer for delayed tooltip
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_hover_preview)
        
        self._setup_ui()
        self._setup_style()
    
    def _setup_ui(self):
        """Set up the widget UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Thumbnail display label
        self._thumbnail_label = QLabel()
        self._thumbnail_label.setAlignment(Qt.AlignCenter)
        self._thumbnail_label.setMinimumSize(100, 120)
        self._thumbnail_label.setScaledContents(False)
        layout.addWidget(self._thumbnail_label)
        
        # Page number label
        self._page_label = QLabel(f"Page {self._page_number + 1}")
        self._page_label.setAlignment(Qt.AlignCenter)
        page_font = QFont()
        page_font.setPointSize(9)
        self._page_label.setFont(page_font)
        layout.addWidget(self._page_label)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        self._thumbnail_label.setMouseTracking(True)
    
    def _setup_style(self):
        """Set up widget styling with enhanced visual effects."""
        self.setAutoFillBackground(True)
        
        # Add subtle shadow effect
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self._update_background()
    
    def _update_background(self):
        """Update widget background based on state."""
        palette = self.palette()
        
        if self._is_selected:
            # Selected: Light blue background
            palette.setColor(QPalette.Window, QColor(200, 220, 255, 100))
        elif self._is_hovered:
            # Hovered: Very light gray
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
        else:
            # Normal: Transparent/default
            palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        
        self.setPalette(palette)
    
    def set_thumbnail(self, pixmap: QPixmap):
        """
        Set the thumbnail image.
        
        Args:
            pixmap: Thumbnail image as QPixmap
        """
        self._thumbnail = pixmap
        if pixmap:
            # Scale pixmap to fit label while preserving aspect ratio
            scaled = pixmap.scaled(
                self._thumbnail_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self._thumbnail_label.setPixmap(scaled)
        else:
            self._thumbnail_label.clear()
        
        # Trigger repaint to show indicators
        self.update()
    
    def set_current(self, is_current: bool):
        """
        Mark this thumbnail as the current page.
        
        Args:
            is_current: True if this is the current page
        """
        self._is_current = is_current
        self.update()  # Repaint to show/hide blue border
    
    def set_selected(self, is_selected: bool):
        """
        Mark this thumbnail as selected.
        
        Args:
            is_selected: True if selected
        """
        self._is_selected = is_selected
        self._update_background()
        self.update()
    
    def set_modified(self, is_modified: bool):
        """
        Mark this thumbnail as containing modifications.
        
        Args:
            is_modified: True if page has been modified
        """
        self._is_modified = is_modified
        self.update()  # Repaint to show/hide orange badge
    
    def set_has_annotations(self, has_annotations: bool):
        """
        Mark this thumbnail as having annotations.
        
        Args:
            has_annotations: True if page has annotations
        """
        self._has_annotations = has_annotations
        self.update()  # Repaint to show/hide yellow star
    
    def get_page_number(self) -> int:
        """
        Get the page number for this thumbnail.
        
        Returns:
            Page number (0-indexed)
        """
        return self._page_number
    
    def is_selected(self) -> bool:
        """
        Check if thumbnail is selected.
        
        Returns:
            True if selected
        """
        return self._is_selected
    
    def paintEvent(self, event):
        """
        Custom paint event to draw borders and indicators.
        
        Args:
            event: Paint event
        """
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw current page indicator (blue border)
        if self._is_current:
            pen = QPen(QColor(0, 120, 215), 3)  # Blue, 3px width
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            rect = self._thumbnail_label.geometry()
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
        
        # Draw modified badge (orange triangle in top-right)
        if self._is_modified:
            badge_size = 16
            rect = self._thumbnail_label.geometry()
            x = rect.right() - badge_size
            y = rect.top()
            
            painter.setBrush(QBrush(QColor(255, 140, 0)))  # Orange
            painter.setPen(Qt.NoPen)
            
            points = [
                (x + badge_size, y),
                (x + badge_size, y + badge_size),
                (x, y)
            ]
            from PySide6.QtCore import QPoint
            qpoints = [QPoint(px, py) for px, py in points]
            from PySide6.QtGui import QPolygon
            painter.drawPolygon(QPolygon(qpoints))
        
        # Draw annotation indicator (yellow star in bottom-right)
        if self._has_annotations:
            star_size = 12
            rect = self._thumbnail_label.geometry()
            x = rect.right() - star_size - 2
            y = rect.bottom() - star_size - 2
            
            painter.setPen(QPen(QColor(255, 215, 0), 2))  # Gold outline
            painter.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow fill
            
            # Draw simple star (circle for simplicity)
            painter.drawEllipse(x, y, star_size, star_size)
            
            # Draw "A" for annotation
            painter.setPen(QColor(0, 0, 0))
            font = QFont()
            font.setPixelSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(x, y, star_size, star_size, Qt.AlignCenter, "A")
    
    def mousePressEvent(self, event):
        """
        Handle mouse press for click detection.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            # Store for click vs drag detection
            self._click_start_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release to emit click signal.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            # Check if this was a click (not a drag)
            if hasattr(self, '_click_start_pos'):
                distance = (event.pos() - self._click_start_pos).manhattanLength()
                if distance < 5:  # Threshold for click vs drag
                    self.clicked.emit(self._page_number)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """
        Handle double-click event.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self._page_number)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        """
        Handle context menu request.
        
        Args:
            event: Context menu event
        """
        self.context_menu_requested.emit(self._page_number, event.globalPos())
        event.accept()
    
    def enterEvent(self, event):
        """
        Handle mouse enter for hover effect.
        
        Args:
            event: Enter event
        """
        self._is_hovered = True
        self._update_background()
        
        # Start timer for delayed hover preview
        self._hover_timer.start(500)  # 500ms delay
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """
        Handle mouse leave to remove hover effect.
        
        Args:
            event: Leave event
        """
        self._is_hovered = False
        self._update_background()
        
        # Cancel hover preview timer
        self._hover_timer.stop()
        
        super().leaveEvent(event)
    
    def _show_hover_preview(self):
        """Show larger thumbnail preview in tooltip with metadata."""
        if not self._thumbnail:
            return
        
        # Create enhanced tooltip with page info
        tooltip_lines = [
            f"<b>Page {self._page_number + 1}</b>",
            f"<small>Size: {self._thumbnail.width()}×{self._thumbnail.height()}px</small>"
        ]
        
        # Add status indicators
        if self._has_annotations:
            tooltip_lines.append("<small>📝 Has annotations</small>")
        if self._is_modified:
            tooltip_lines.append("<small>✏️ Modified</small>")
        if self._is_current:
            tooltip_lines.append("<small>👁️ Current page</small>")
        
        tooltip_html = "<br>".join(tooltip_lines)
        self.setToolTip(tooltip_html)
    
    def sizeHint(self) -> QSize:
        """
        Provide size hint for layout.
        
        Returns:
            Preferred size
        """
        return QSize(140, 180)  # Width, Height for medium thumbnail
