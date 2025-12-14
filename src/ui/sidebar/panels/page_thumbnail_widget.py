"""
Simple PDF Handler - Page Thumbnail Widget

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor
from ui.styles.design_tokens import get_color
from ui.styles.theme_manager import get_theme_manager


class PageThumbnailWidget(QWidget):
    """
    Widget displaying a single page thumbnail with page number.
    Supports selected and hover states.
    """
    
    clicked = pyqtSignal(int)  # Emits page number when clicked
    
    def __init__(self, page_number: int, parent=None):
        """
        Initialize thumbnail widget.
        
        Args:
            page_number: Page number (0-indexed)
            parent: Parent widget
        """
        super().__init__(parent)
        self._page_number = page_number
        self._is_selected = False
        self._thumbnail_pixmap = None
        self._is_loading = True
        
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        # Fixed size for consistent grid layout
        self.setFixedSize(150, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)
        
        # Thumbnail display area
        self._thumbnail_label = QLabel()
        self._thumbnail_label.setFixedSize(142, 170)
        self._thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumbnail_label.setScaledContents(False)
        layout.addWidget(self._thumbnail_label)
        
        # Page number label
        self._page_label = QLabel(f"Page {self._page_number + 1}")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setStyleSheet("font-size: 11px; font-weight: 500;")
        layout.addWidget(self._page_label)
        
        # Show loading placeholder initially
        self._show_placeholder()
    
    def _show_placeholder(self) -> None:
        """Show loading placeholder."""
        # Create a simple gray placeholder
        placeholder = QPixmap(142, 170)
        placeholder.fill(QColor(240, 240, 240))
        
        # Draw "Loading..." text
        painter = QPainter(placeholder)
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(placeholder.rect(), Qt.AlignmentFlag.AlignCenter, "Loading...")
        painter.end()
        
        self._thumbnail_label.setPixmap(placeholder)
    
    def set_thumbnail(self, pixmap: QPixmap) -> None:
        """
        Set the thumbnail image.
        
        Args:
            pixmap: Rendered page pixmap
        """
        if pixmap and not pixmap.isNull():
            # Scale to fit label while maintaining aspect ratio
            scaled = pixmap.scaled(
                142, 170,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._thumbnail_label.setPixmap(scaled)
            self._thumbnail_pixmap = pixmap
            self._is_loading = False
            self.update()  # Trigger repaint for border
    
    def set_selected(self, selected: bool) -> None:
        """
        Set selection state.
        
        Args:
            selected: Whether this thumbnail is selected
        """
        if self._is_selected != selected:
            self._is_selected = selected
            self._apply_theme()  # Update styling
    
    def is_selected(self) -> bool:
        """Check if thumbnail is selected."""
        return self._is_selected
    
    def get_page_number(self) -> int:
        """Get the page number for this thumbnail."""
        return self._page_number
    
    def is_loading(self) -> bool:
        """Check if thumbnail is still loading."""
        return self._is_loading
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._page_number)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        if not self._is_selected:
            self._apply_hover_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        if not self._is_selected:
            self._apply_theme()
        super().leaveEvent(event)
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        # Get theme colors
        bg_color = get_color('surface', is_dark)
        text_color = get_color('text_primary', is_dark)
        
        if self._is_selected:
            # Selected state - blue border
            border_color = get_color('primary', is_dark)
            border_width = "3px"
            bg_color = get_color('surface_elevated', is_dark)
        else:
            # Normal state - subtle border
            border_color = get_color('divider', is_dark)
            border_width = "1px"
        
        self.setStyleSheet(f"""
            PageThumbnailWidget {{
                background-color: {bg_color};
                border: {border_width} solid {border_color};
                border-radius: 6px;
            }}
        """)
        
        self._page_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 500;
            color: {text_color};
        """)
    
    def _apply_hover_style(self) -> None:
        """Apply hover state styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface_elevated', is_dark)
        border_color = get_color('primary', is_dark)
        
        self.setStyleSheet(f"""
            PageThumbnailWidget {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 6px;
            }}
        """)
