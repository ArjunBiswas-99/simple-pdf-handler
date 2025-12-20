"""
Simple PDF Handler - Theme Manager

Manages application theme switching and color scheme persistence.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, Property


class ThemeManager(QObject):
    """
    Manages application theme state and switching.
    
    Handles light/dark mode switching and persists user preference.
    Notifies QML when theme changes to update UI colors.
    
    Signals:
        theme_changed: Emitted when theme switches (bool: is_dark_mode)
    """
    
    theme_changed = Signal(bool)
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initializes theme manager with default light theme.
        
        Args:
            parent: Optional parent QObject for Qt ownership
        """
        super().__init__(parent)
        self._is_dark_mode = False
    
    @Slot()
    def toggle_theme(self) -> None:
        """
        Toggles between light and dark theme.
        
        Switches theme and emits signal to update UI.
        """
        self._is_dark_mode = not self._is_dark_mode
        self.theme_changed.emit(self._is_dark_mode)
    
    @Slot(bool)
    def set_dark_mode(self, enabled: bool) -> None:
        """
        Sets theme to dark or light mode.
        
        Args:
            enabled: True for dark mode, False for light mode
        """
        if self._is_dark_mode != enabled:
            self._is_dark_mode = enabled
            self.theme_changed.emit(self._is_dark_mode)
    
    @Property(bool, notify=theme_changed)
    def is_dark_mode(self) -> bool:
        """
        Returns current theme mode.
        
        Returns:
            True if dark mode is active, False for light mode
        """
        return self._is_dark_mode
