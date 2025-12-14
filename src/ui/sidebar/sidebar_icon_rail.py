"""
Simple PDF Handler - Sidebar Icon Rail

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from ui.styles.design_tokens import SIZING, SPACING, get_color, SidebarMode
from ui.styles.theme_manager import get_theme_manager


class SidebarIconRail(QWidget):
    """
    Icon rail for sidebar with 4 mode buttons.
    48px wide vertical strip with icons for Pages, Bookmarks, Search, Attachments.
    """
    
    mode_changed = pyqtSignal(SidebarMode)
    toggle_requested = pyqtSignal()  # Emitted when same button is clicked to toggle collapse
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = SidebarMode.PAGES
        self._buttons = {}
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the icon rail UI."""
        self.setFixedWidth(SIZING['sidebar_rail_width'])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, SPACING['sm'], 0, SPACING['sm'])
        layout.setSpacing(SPACING['xs'])
        self.setLayout(layout)
        
        # Create icon buttons with professional Unicode symbols
        self._create_icon_button(SidebarMode.PAGES, "☰", "Pages", layout)
        self._create_icon_button(SidebarMode.BOOKMARKS, "★", "Bookmarks", layout)
        self._create_icon_button(SidebarMode.SEARCH, "⌕", "Search", layout)
        self._create_icon_button(SidebarMode.ATTACHMENTS, "◉", "Attachments", layout)
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
        # Set initial active button
        self._buttons[SidebarMode.PAGES].setChecked(True)
    
    def _create_icon_button(self, mode: SidebarMode, icon: str, tooltip: str, layout: QVBoxLayout) -> None:
        """Create an icon button for the rail."""
        button = QPushButton(icon)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        # Larger button size for better icon display (44x44 fits well in 48px rail)
        button.setFixedSize(44, 44)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: self._on_button_clicked(mode))
        
        self._buttons[mode] = button
        layout.addWidget(button)
    
    def _on_button_clicked(self, mode: SidebarMode) -> None:
        """Handle icon button click."""
        if mode == self._current_mode:
            # Same button clicked - request toggle (collapse/expand)
            self.toggle_requested.emit()
        else:
            # Different button clicked - switch panel
            # Uncheck previous button
            self._buttons[self._current_mode].setChecked(False)
            
            # Check new button
            self._buttons[mode].setChecked(True)
            self._current_mode = mode
            
            # Emit signal to switch panel
            self.mode_changed.emit(mode)
    
    def set_mode(self, mode: SidebarMode) -> None:
        """Programmatically set the active mode."""
        if mode != self._current_mode and mode in self._buttons:
            self._buttons[self._current_mode].setChecked(False)
            self._buttons[mode].setChecked(True)
            self._current_mode = mode
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        border_color = get_color('divider', is_dark)
        text_color = get_color('text_primary', is_dark)
        active_color = get_color('primary', is_dark)
        hover_color = get_color('hover', is_dark)
        
        self.setStyleSheet(f"""
            SidebarIconRail {{
                background-color: {bg_color};
                border-right: 1px solid {border_color};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: {text_color};
                font-size: 24px;
                padding: 0px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:checked {{
                background-color: {active_color};
                color: white;
            }}
        """)
