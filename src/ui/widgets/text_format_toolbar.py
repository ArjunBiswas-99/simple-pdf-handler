"""
Simple PDF Handler - Floating Text Format Toolbar

A floating toolbar that appears during inline text editing, providing
real-time controls for font, size, style, and color formatting.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QPushButton, QColorDialog, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon


class TextFormatToolbar(QWidget):
    """
    Floating toolbar for text formatting during inline editing.
    
    Provides controls for font family, size, style (bold/italic/underline),
    color, and commit/cancel actions. Designed to appear above the inline
    text editor for easy access.
    """
    
    # Signals
    format_changed = pyqtSignal(dict)  # Emits updated format properties
    done_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    
    # Available fonts (PDF standard fonts for maximum compatibility)
    FONTS = ["Helvetica", "Times-Roman", "Courier"]
    
    # Available sizes
    SIZES = ["8", "10", "12", "14", "16", "18", "24", "36", "48", "72"]
    
    def __init__(self, parent=None):
        """Initialize the format toolbar with default styling."""
        super().__init__(parent)
        
        # Current format properties
        self._current_font = "Helvetica"
        self._current_size = 12
        self._current_color = QColor(0, 0, 0)  # Black
        self._bold = False
        self._italic = False
        self._underline = False
        
        self._setup_ui()
        
        # Make toolbar float above other widgets
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
    
    def _setup_ui(self) -> None:
        """Set up the toolbar layout and controls."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Font selector
        self._font_combo = QComboBox()
        self._font_combo.addItems(self.FONTS)
        self._font_combo.setCurrentText("Helvetica")
        self._font_combo.setMinimumWidth(120)
        self._font_combo.currentTextChanged.connect(self._on_font_changed)
        layout.addWidget(self._font_combo)
        
        # Size selector
        self._size_combo = QComboBox()
        self._size_combo.addItems(self.SIZES)
        self._size_combo.setCurrentText("12")
        self._size_combo.setMinimumWidth(60)
        self._size_combo.currentTextChanged.connect(self._on_size_changed)
        layout.addWidget(self._size_combo)
        
        # Separator
        layout.addSpacing(8)
        
        # Bold button
        self._bold_btn = QPushButton("B")
        self._bold_btn.setCheckable(True)
        self._bold_btn.setFixedSize(32, 32)
        self._bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self._bold_btn.toggled.connect(self._on_bold_toggled)
        layout.addWidget(self._bold_btn)
        
        # Italic button
        self._italic_btn = QPushButton("I")
        self._italic_btn.setCheckable(True)
        self._italic_btn.setFixedSize(32, 32)
        italic_font = QFont("Arial", 10)
        italic_font.setItalic(True)
        self._italic_btn.setFont(italic_font)
        self._italic_btn.toggled.connect(self._on_italic_toggled)
        layout.addWidget(self._italic_btn)
        
        # Underline button
        self._underline_btn = QPushButton("U")
        self._underline_btn.setCheckable(True)
        self._underline_btn.setFixedSize(32, 32)
        underline_font = QFont("Arial", 10)
        underline_font.setUnderline(True)
        self._underline_btn.setFont(underline_font)
        self._underline_btn.toggled.connect(self._on_underline_toggled)
        layout.addWidget(self._underline_btn)
        
        # Separator
        layout.addSpacing(8)
        
        # Color button
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(32, 32)
        self._color_btn.clicked.connect(self._on_color_clicked)
        self._update_color_button()
        layout.addWidget(self._color_btn)
        
        # Separator
        layout.addSpacing(12)
        
        # Done button
        self._done_btn = QPushButton("✓ Done")
        self._done_btn.setMinimumWidth(70)
        self._done_btn.clicked.connect(self.done_clicked.emit)
        layout.addWidget(self._done_btn)
        
        # Cancel button
        self._cancel_btn = QPushButton("✕ Cancel")
        self._cancel_btn.setMinimumWidth(70)
        self._cancel_btn.clicked.connect(self.cancel_clicked.emit)
        layout.addWidget(self._cancel_btn)
        
        self.setLayout(layout)
        
        # Apply professional styling
        self.setStyleSheet("""
            TextFormatToolbar {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
            }
            QComboBox {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #0078D4;
            }
            QPushButton {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #0078D4;
            }
            QPushButton:checked {
                background-color: #0078D4;
                color: white;
                border-color: #0078D4;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
    
    def _on_font_changed(self, font_name: str) -> None:
        """Handle font selection change."""
        self._current_font = font_name
        self._emit_format_changed()
    
    def _on_size_changed(self, size_text: str) -> None:
        """Handle font size change."""
        try:
            self._current_size = int(size_text)
            self._emit_format_changed()
        except ValueError:
            pass
    
    def _on_bold_toggled(self, checked: bool) -> None:
        """Handle bold toggle."""
        self._bold = checked
        self._emit_format_changed()
    
    def _on_italic_toggled(self, checked: bool) -> None:
        """Handle italic toggle."""
        self._italic = checked
        self._emit_format_changed()
    
    def _on_underline_toggled(self, checked: bool) -> None:
        """Handle underline toggle."""
        self._underline = checked
        self._emit_format_changed()
    
    def _on_color_clicked(self) -> None:
        """Show color picker dialog."""
        color = QColorDialog.getColor(
            self._current_color,
            self,
            "Select Text Color"
        )
        
        if color.isValid():
            self._current_color = color
            self._update_color_button()
            self._emit_format_changed()
    
    def _update_color_button(self) -> None:
        """Update color button to show current color."""
        rgb = self._current_color.getRgb()[:3]
        self._color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});
                border: 2px solid #CCCCCC;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #0078D4;
            }}
        """)
    
    def _emit_format_changed(self) -> None:
        """Emit format changed signal with current properties."""
        properties = self.get_format_properties()
        self.format_changed.emit(properties)
    
    def get_format_properties(self) -> dict:
        """
        Get current format properties.
        
        Returns:
            Dictionary with font, size, color, bold, italic, underline
        """
        return {
            'font': self._current_font,
            'size': self._current_size,
            'color': self._current_color,
            'bold': self._bold,
            'italic': self._italic,
            'underline': self._underline
        }
    
    def set_format_properties(self, properties: dict) -> None:
        """
        Set format properties programmatically.
        
        Args:
            properties: Dictionary with format properties
        """
        # Block signals to avoid triggering format_changed during setup
        self._font_combo.blockSignals(True)
        self._size_combo.blockSignals(True)
        self._bold_btn.blockSignals(True)
        self._italic_btn.blockSignals(True)
        self._underline_btn.blockSignals(True)
        
        # Update UI controls
        if 'font' in properties:
            self._current_font = properties['font']
            self._font_combo.setCurrentText(self._current_font)
        
        if 'size' in properties:
            self._current_size = properties['size']
            self._size_combo.setCurrentText(str(self._current_size))
        
        if 'color' in properties:
            self._current_color = properties['color']
            self._update_color_button()
        
        if 'bold' in properties:
            self._bold = properties['bold']
            self._bold_btn.setChecked(self._bold)
        
        if 'italic' in properties:
            self._italic = properties['italic']
            self._italic_btn.setChecked(self._italic)
        
        if 'underline' in properties:
            self._underline = properties['underline']
            self._underline_btn.setChecked(self._underline)
        
        # Re-enable signals
        self._font_combo.blockSignals(False)
        self._size_combo.blockSignals(False)
        self._bold_btn.blockSignals(False)
        self._italic_btn.blockSignals(False)
        self._underline_btn.blockSignals(False)
