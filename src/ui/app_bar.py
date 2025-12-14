"""
Simple PDF Handler - Application Bar Component

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from ui.styles.design_tokens import SIZING, SPACING, TYPOGRAPHY, get_color
from ui.styles.theme_manager import get_theme_manager


class AppBar(QWidget):
    """
    Top application bar with branding and global controls.
    Provides theme toggle, settings, and help functionality.
    """
    
    # Signals
    theme_toggle_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    help_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the AppBar component."""
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager for updates
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the AppBar UI components."""
        # Set fixed height
        self.setFixedHeight(SIZING['appbar_height'])
        
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(SPACING['md'], 0, SPACING['md'], 0)
        layout.setSpacing(SPACING['md'])
        self.setLayout(layout)
        
        # Left section: App icon + title
        self._create_left_section(layout)
        
        # Spacer to push right section to the right
        layout.addStretch()
        
        # Right section: Theme toggle, Settings, Help
        self._create_right_section(layout)
    
    def _create_left_section(self, layout: QHBoxLayout) -> None:
        """
        Create the left section with app icon and title.
        
        Args:
            layout: Main horizontal layout to add to
        """
        # App icon (PDF file icon)
        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)
        
        # App title
        self._title_label = QLabel("Simple PDF Handler")
        title_font = QFont(TYPOGRAPHY['font_family'])
        title_font.setPointSize(TYPOGRAPHY['font_size_title'])
        title_font.setWeight(TYPOGRAPHY['font_weight_semibold'])
        self._title_label.setFont(title_font)
        layout.addWidget(self._title_label)
    
    def _create_right_section(self, layout: QHBoxLayout) -> None:
        """
        Create the right section with control buttons.
        
        Args:
            layout: Main horizontal layout to add to
        """
        # Theme toggle button
        self._theme_btn = QPushButton("🌓")
        self._theme_btn.setToolTip("Toggle theme")
        self._theme_btn.setFixedSize(SIZING['icon_button_size'], SIZING['icon_button_size'])
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self.theme_toggle_clicked.emit)
        layout.addWidget(self._theme_btn)
        
        # Settings button (grayed out - coming soon)
        self._settings_btn = QPushButton("⚙️")
        self._settings_btn.setToolTip("Settings (Coming soon)")
        self._settings_btn.setFixedSize(SIZING['icon_button_size'], SIZING['icon_button_size'])
        self._settings_btn.setEnabled(False)
        self._settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self._settings_btn)
        
        # Help button
        self._help_btn = QPushButton("?")
        self._help_btn.setToolTip("Help & About")
        self._help_btn.setFixedSize(SIZING['icon_button_size'], SIZING['icon_button_size'])
        self._help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._help_btn.clicked.connect(self.help_clicked.emit)
        layout.addWidget(self._help_btn)
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling to the AppBar."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        # Get theme colors
        bg_color = get_color('surface_elevated', is_dark)
        text_color = get_color('text_primary', is_dark)
        border_color = get_color('divider', is_dark)
        button_hover_color = get_color('surface', is_dark)
        
        # AppBar stylesheet
        self.setStyleSheet(f"""
            AppBar {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
        """)
        
        # Title label color
        self._title_label.setStyleSheet(f"color: {text_color};")
        
        # Button styling
        button_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: {text_color};
                font-size: 16px;
            }}
            QPushButton:hover:enabled {{
                background-color: {button_hover_color};
            }}
            QPushButton:disabled {{
                opacity: 0.4;
            }}
        """
        
        self._theme_btn.setStyleSheet(button_style)
        self._settings_btn.setStyleSheet(button_style)
        self._help_btn.setStyleSheet(button_style)
    
    def set_title(self, title: str) -> None:
        """
        Update the application title displayed in the AppBar.
        
        Args:
            title: New title text
        """
        self._title_label.setText(title)
