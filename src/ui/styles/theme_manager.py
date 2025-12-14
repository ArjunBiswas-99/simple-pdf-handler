"""
Simple PDF Handler - Theme Manager

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

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from .themes import ThemeType
from .stylesheets import generate_stylesheet


class ThemeManager(QObject):
    """
    Manages application themes and provides theme switching functionality.
    Centralizes theme application across the entire application.
    """
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(ThemeType)
    
    def __init__(self):
        """Initialize the theme manager with default light theme."""
        super().__init__()
        self._current_theme = ThemeType.LIGHT
        self._app = None
    
    def set_application(self, app: QApplication) -> None:
        """
        Set the QApplication instance to apply themes to.
        
        Args:
            app: QApplication instance
        """
        self._app = app
    
    def get_current_theme(self) -> ThemeType:
        """
        Get the currently active theme.
        
        Returns:
            Current theme type
        """
        return self._current_theme
    
    def apply_theme(self, theme_type: ThemeType) -> None:
        """
        Apply the specified theme to the application.
        
        Args:
            theme_type: Theme to apply
        """
        if not self._app:
            raise RuntimeError("Application not set. Call set_application() first.")
        
        # Generate stylesheet for the theme
        stylesheet = generate_stylesheet(theme_type)
        
        # Apply to application
        self._app.setStyleSheet(stylesheet)
        
        # Update current theme
        old_theme = self._current_theme
        self._current_theme = theme_type
        
        # Emit signal if theme actually changed
        if old_theme != theme_type:
            self.theme_changed.emit(theme_type)
    
    def toggle_theme(self) -> ThemeType:
        """
        Toggle between light and dark themes.
        
        Returns:
            The newly active theme type
        """
        new_theme = (
            ThemeType.DARK 
            if self._current_theme == ThemeType.LIGHT 
            else ThemeType.LIGHT
        )
        self.apply_theme(new_theme)
        return new_theme
    
    def is_dark_theme(self) -> bool:
        """
        Check if dark theme is currently active.
        
        Returns:
            True if dark theme is active, False otherwise
        """
        return self._current_theme == ThemeType.DARK


# Global theme manager instance
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance.
    
    Returns:
        Global ThemeManager instance
    """
    return _theme_manager
