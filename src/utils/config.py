"""
Application configuration and settings management.

Handles user preferences, window geometry, recent files, and application state persistence.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QSettings


class Config:
    """
    Manages application configuration and user preferences.
    
    Provides centralized access to settings with default values and type safety.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.settings = QSettings("PDFHandler", "SimplePDFHandler")
        self._recent_files: List[str] = []
        self._load_recent_files()
    
    # Theme settings
    def get_theme(self) -> str:
        """
        Get current theme preference.
        
        Returns:
            Theme name ('light' or 'dark')
        """
        return self.settings.value("theme", "light", str)
    
    def set_theme(self, theme: str) -> None:
        """
        Save theme preference.
        
        Args:
            theme: Theme name ('light' or 'dark')
        """
        self.settings.setValue("theme", theme)
    
    # Window geometry
    def get_window_geometry(self) -> Optional[bytes]:
        """
        Get saved window geometry.
        
        Returns:
            Window geometry as bytes, or None if not saved
        """
        return self.settings.value("window/geometry", None)
    
    def set_window_geometry(self, geometry: bytes) -> None:
        """
        Save window geometry.
        
        Args:
            geometry: Window geometry as bytes
        """
        self.settings.setValue("window/geometry", geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        """
        Get saved window state (toolbars, docks, etc.).
        
        Returns:
            Window state as bytes, or None if not saved
        """
        return self.settings.value("window/state", None)
    
    def set_window_state(self, state: bytes) -> None:
        """
        Save window state.
        
        Args:
            state: Window state as bytes
        """
        self.settings.setValue("window/state", state)
    
    # Recent files
    def _load_recent_files(self) -> None:
        """Load recent files list from settings."""
        size = self.settings.beginReadArray("recent_files")
        self._recent_files = []
        for i in range(size):
            self.settings.setArrayIndex(i)
            file_path = self.settings.value("path", "", str)
            if file_path and os.path.exists(file_path):
                self._recent_files.append(file_path)
        self.settings.endArray()
    
    def _save_recent_files(self) -> None:
        """Save recent files list to settings."""
        self.settings.beginWriteArray("recent_files")
        for i, file_path in enumerate(self._recent_files):
            self.settings.setArrayIndex(i)
            self.settings.setValue("path", file_path)
        self.settings.endArray()
    
    def get_recent_files(self) -> List[str]:
        """
        Get list of recently opened files.
        
        Returns:
            List of file paths
        """
        return self._recent_files.copy()
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add file to recent files list.
        
        Args:
            file_path: Path to the file
        """
        # Remove if already exists
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        
        # Add to beginning
        self._recent_files.insert(0, file_path)
        
        # Keep only last 10
        self._recent_files = self._recent_files[:10]
        
        self._save_recent_files()
    
    def clear_recent_files(self) -> None:
        """Clear recent files list."""
        self._recent_files = []
        self._save_recent_files()
    
    # View preferences
    def get_zoom_level(self) -> float:
        """
        Get default zoom level.
        
        Returns:
            Zoom level as percentage (100.0 = 100%)
        """
        return self.settings.value("view/zoom", 100.0, float)
    
    def set_zoom_level(self, zoom: float) -> None:
        """
        Save default zoom level.
        
        Args:
            zoom: Zoom level as percentage
        """
        self.settings.setValue("view/zoom", zoom)
    
    def get_view_mode(self) -> str:
        """
        Get default view mode.
        
        Returns:
            View mode ('single', 'continuous', 'two_page')
        """
        return self.settings.value("view/mode", "continuous", str)
    
    def set_view_mode(self, mode: str) -> None:
        """
        Save view mode preference.
        
        Args:
            mode: View mode name
        """
        self.settings.setValue("view/mode", mode)
    
    # Sidebar preferences
    def get_left_sidebar_visible(self) -> bool:
        """
        Get left sidebar visibility state.
        
        Returns:
            True if visible, False otherwise
        """
        return self.settings.value("sidebar/left_visible", True, bool)
    
    def set_left_sidebar_visible(self, visible: bool) -> None:
        """
        Save left sidebar visibility.
        
        Args:
            visible: Visibility state
        """
        self.settings.setValue("sidebar/left_visible", visible)
    
    def get_right_sidebar_visible(self) -> bool:
        """
        Get right sidebar visibility state.
        
        Returns:
            True if visible, False otherwise
        """
        return self.settings.value("sidebar/right_visible", True, bool)
    
    def set_right_sidebar_visible(self, visible: bool) -> None:
        """
        Save right sidebar visibility.
        
        Args:
            visible: Visibility state
        """
        self.settings.setValue("sidebar/right_visible", visible)
    
    # Auto-save preferences
    def get_auto_save_enabled(self) -> bool:
        """
        Get auto-save preference.
        
        Returns:
            True if auto-save is enabled
        """
        return self.settings.value("editor/auto_save", True, bool)
    
    def set_auto_save_enabled(self, enabled: bool) -> None:
        """
        Save auto-save preference.
        
        Args:
            enabled: Enable/disable auto-save
        """
        self.settings.setValue("editor/auto_save", enabled)
    
    def get_auto_save_interval(self) -> int:
        """
        Get auto-save interval in minutes.
        
        Returns:
            Interval in minutes
        """
        return self.settings.value("editor/auto_save_interval", 5, int)
    
    def set_auto_save_interval(self, minutes: int) -> None:
        """
        Save auto-save interval.
        
        Args:
            minutes: Interval in minutes
        """
        self.settings.setValue("editor/auto_save_interval", minutes)
    
    # Utility methods
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.settings.clear()
        self._recent_files = []
    
    def sync(self) -> None:
        """Force synchronization of settings to persistent storage."""
        self.settings.sync()


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
