"""
Simple PDF Handler - Page Thumbnail Widget

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor
from ui.styles.design_tokens import get_color
from ui.styles.theme_manager import get_theme_manager


class PageThumbnailWidget(QWidget):
    """
    Widget displaying a single page thumbnail with page number.
    Supports selected state, hover effects, and edit mode with overlay buttons.
    
    In edit mode, displays red (delete) and yellow (add) circular buttons
    for page management operations.
    """
    
    # Signals
    clicked = pyqtSignal(int)  # Emits page number when clicked
    delete_page_requested = pyqtSignal(int)  # Emits page number to delete
    add_page_above_requested = pyqtSignal(int)  # Emits position to insert page before
    
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
        self._edit_mode = False
        
        # Overlay buttons (created on demand)
        self._delete_button = None
        self._add_button = None
        
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
            self.update()
    
    def set_selected(self, selected: bool) -> None:
        """
        Set selection state.
        
        Args:
            selected: Whether this thumbnail is selected
        """
        if self._is_selected != selected:
            self._is_selected = selected
            self._apply_theme()
    
    def set_edit_mode(self, enabled: bool) -> None:
        """
        Enable or disable edit mode.
        Shows/hides overlay buttons for page operations.
        
        Args:
            enabled: True to show edit controls, False to hide
        """
        self._edit_mode = enabled
        
        if enabled:
            self._create_overlay_buttons()
        else:
            self._remove_overlay_buttons()
    
    def _create_overlay_buttons(self) -> None:
        """Create and position overlay buttons for edit mode."""
        if self._delete_button or self._add_button:
            return  # Already created
        
        # Delete button (red circle with X) - top right
        self._delete_button = QPushButton("×", self)
        self._delete_button.setFixedSize(28, 28)
        self._delete_button.setToolTip("Delete this page")
        self._delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                border: 2px solid white;
                border-radius: 14px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #C82333;
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
        """)
        
        # Position in top-right corner
        self._delete_button.move(118, 6)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        self._delete_button.show()
        self._delete_button.raise_()
        
        # Add page button (yellow circle with +) - top left
        self._add_button = QPushButton("+", self)
        self._add_button.setFixedSize(28, 28)
        self._add_button.setToolTip("Add blank page above this page")
        self._add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                border: 2px solid white;
                border-radius: 14px;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #FFB300;
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: #FFA000;
            }
        """)
        
        # Position in top-left corner
        self._add_button.move(6, 6)
        self._add_button.clicked.connect(self._on_add_clicked)
        self._add_button.show()
        self._add_button.raise_()
    
    def _remove_overlay_buttons(self) -> None:
        """Remove overlay buttons when exiting edit mode."""
        if self._delete_button:
            self._delete_button.deleteLater()
            self._delete_button = None
        
        if self._add_button:
            self._add_button.deleteLater()
            self._add_button = None
    
    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        self.delete_page_requested.emit(self._page_number)
    
    def _on_add_clicked(self) -> None:
        """Handle add page button click."""
        self.add_page_above_requested.emit(self._page_number)
    
    def is_selected(self) -> bool:
        """Check if thumbnail is selected."""
        return self._is_selected
    
    def get_page_number(self) -> int:
        """Get the page number for this thumbnail."""
        return self._page_number
    
    def update_page_number(self, new_number: int) -> None:
        """
        Update the page number after reordering.
        
        Args:
            new_number: New page number (0-indexed)
        """
        self._page_number = new_number
        self._page_label.setText(f"Page {new_number + 1}")
    
    def is_loading(self) -> bool:
        """Check if thumbnail is still loading."""
        return self._is_loading
    
    def mousePressEvent(self, event):
        """Handle mouse click - only for thumbnail selection, not overlay buttons."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is on overlay buttons
            if self._edit_mode and (self._delete_button or self._add_button):
                # Let overlay buttons handle their own clicks
                # Don't emit clicked signal if overlay button will handle it
                pass
            else:
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
