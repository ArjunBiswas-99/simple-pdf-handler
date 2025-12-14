"""
Simple PDF Handler - Mode Tabs Component

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

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from ui.styles.design_tokens import AppMode, SIZING, SPACING, TYPOGRAPHY, COLORS, get_color
from ui.styles.theme_manager import get_theme_manager


class ModeTabButton(QPushButton):
    """Custom button for mode tabs with active state styling."""
    
    def __init__(self, mode: AppMode, parent=None):
        """
        Initialize a mode tab button.
        
        Args:
            mode: AppMode enum value
            parent: Parent widget
        """
        super().__init__(mode.value, parent)
        self._mode = mode
        self._is_active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_theme()
        
        # Connect to theme manager for updates
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def set_active(self, active: bool) -> None:
        """
        Set the active state of this tab.
        
        Args:
            active: True if this tab should be active
        """
        self._is_active = active
        self._apply_theme()
    
    def is_active(self) -> bool:
        """Check if this tab is currently active."""
        return self._is_active
    
    def get_mode(self) -> AppMode:
        """Get the AppMode associated with this tab."""
        return self._mode
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling to the tab button."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        # Get theme colors
        bg_color = get_color('surface_elevated', is_dark)
        text_color = get_color('text_primary', is_dark)
        text_secondary = get_color('text_secondary', is_dark)
        border_color = get_color('divider', is_dark)
        hover_color = get_color('surface', is_dark)
        primary_color = COLORS['primary']
        
        # Build stylesheet based on active state
        if self._is_active:
            stylesheet = f"""
                ModeTabButton {{
                    background-color: {bg_color};
                    color: {primary_color};
                    border: none;
                    border-bottom: 3px solid {primary_color};
                    padding: 8px 20px;
                    font-size: {TYPOGRAPHY['font_size_normal']}px;
                    font-weight: {TYPOGRAPHY['font_weight_semibold']};
                }}
                ModeTabButton:hover {{
                    background-color: {hover_color};
                }}
            """
        else:
            stylesheet = f"""
                ModeTabButton {{
                    background-color: {bg_color};
                    color: {text_secondary};
                    border: none;
                    border-bottom: 3px solid transparent;
                    padding: 8px 20px;
                    font-size: {TYPOGRAPHY['font_size_normal']}px;
                    font-weight: {TYPOGRAPHY['font_weight_normal']};
                }}
                ModeTabButton:hover {{
                    background-color: {hover_color};
                    color: {text_color};
                }}
            """
        
        self.setStyleSheet(stylesheet)


class ModeTabs(QWidget):
    """
    Mode selection tabs component.
    Allows switching between different application modes (View, Comment, Edit, etc.)
    """
    
    # Signal emitted when mode changes
    mode_changed = pyqtSignal(AppMode)
    
    def __init__(self, parent=None):
        """Initialize the ModeTabs component."""
        super().__init__(parent)
        self._active_mode = AppMode.VIEW
        self._tab_buttons = {}
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager for updates
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the ModeTabs UI components."""
        # Set fixed height
        self.setFixedHeight(SIZING['mode_tabs_height'])
        
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(SPACING['md'], 0, SPACING['md'], 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Create tab buttons for each mode
        for mode in AppMode:
            tab_button = ModeTabButton(mode)
            tab_button.clicked.connect(lambda checked, m=mode: self._on_tab_clicked(m))
            self._tab_buttons[mode] = tab_button
            layout.addWidget(tab_button)
        
        # Add stretch to push tabs to the left
        layout.addStretch()
        
        # Set initial active tab
        self._tab_buttons[AppMode.VIEW].set_active(True)
    
    def _on_tab_clicked(self, mode: AppMode) -> None:
        """
        Handle tab button click.
        
        Args:
            mode: The mode that was clicked
        """
        # If clicking on non-View mode, show "Coming soon" message
        if mode != AppMode.VIEW:
            QMessageBox.information(
                self,
                "Coming Soon",
                f"{mode.value} mode is not yet implemented.\n\n"
                "This feature will be available in a future update."
            )
            return
        
        # Set the active mode
        self.set_active_mode(mode)
    
    def set_active_mode(self, mode: AppMode) -> None:
        """
        Set the active mode programmatically.
        
        Args:
            mode: AppMode to activate
        """
        if mode == self._active_mode:
            return
        
        # Update active state on all tabs
        for tab_mode, tab_button in self._tab_buttons.items():
            tab_button.set_active(tab_mode == mode)
        
        # Update active mode and emit signal
        self._active_mode = mode
        self.mode_changed.emit(mode)
    
    def get_active_mode(self) -> AppMode:
        """
        Get the currently active mode.
        
        Returns:
            Current AppMode
        """
        return self._active_mode
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling to the ModeTabs container."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        # Get theme colors
        bg_color = get_color('surface_elevated', is_dark)
        border_color = get_color('divider', is_dark)
        
        # ModeTabs container stylesheet
        self.setStyleSheet(f"""
            ModeTabs {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
        """)
