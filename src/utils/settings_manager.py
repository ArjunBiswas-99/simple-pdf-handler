"""
Simple PDF Handler - Settings Manager

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

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class SettingsManager:
    """
    Manages application settings persistence.
    Stores user preferences like last opened directory, window size, etc.
    """
    
    def __init__(self):
        """Initialize the settings manager."""
        # Get user's home directory for settings storage
        self._settings_dir = Path.home() / ".simple-pdf-handler"
        self._settings_file = self._settings_dir / "settings.json"
        self._settings: Dict[str, Any] = {}
        
        # Create settings directory if it doesn't exist
        self._settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from disk."""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
                self._settings = {}
        else:
            # Initialize with default settings
            self._settings = self._get_default_settings()
    
    def _save_settings(self) -> None:
        """Save settings to disk."""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings.
        
        Returns:
            Dictionary of default settings
        """
        return {
            "last_open_directory": str(Path.home()),
            "theme": "light",
            "window_geometry": None,
            "recent_files": []
        }
    
    def get_last_open_directory(self) -> str:
        """
        Get the last directory from which a file was opened.
        
        Returns:
            Path to the last opened directory
        """
        last_dir = self._settings.get("last_open_directory", str(Path.home()))
        
        # Verify directory still exists, otherwise return home
        if not os.path.isdir(last_dir):
            return str(Path.home())
        
        return last_dir
    
    def set_last_open_directory(self, directory: str) -> None:
        """
        Save the last directory from which a file was opened.
        
        Args:
            directory: Path to the directory
        """
        # Ensure it's a directory (extract directory from file path if needed)
        if os.path.isfile(directory):
            directory = os.path.dirname(directory)
        
        self._settings["last_open_directory"] = directory
        self._save_settings()
    
    def get_theme(self) -> str:
        """
        Get the current theme preference.
        
        Returns:
            Theme name ("light" or "dark")
        """
        return self._settings.get("theme", "light")
    
    def set_theme(self, theme: str) -> None:
        """
        Save the theme preference.
        
        Args:
            theme: Theme name ("light" or "dark")
        """
        self._settings["theme"] = theme
        self._save_settings()
    
    def get_window_geometry(self) -> Optional[Dict[str, int]]:
        """
        Get saved window geometry.
        
        Returns:
            Dictionary with x, y, width, height or None
        """
        return self._settings.get("window_geometry")
    
    def set_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """
        Save window geometry.
        
        Args:
            x: Window x position
            y: Window y position
            width: Window width
            height: Window height
        """
        self._settings["window_geometry"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self._save_settings()
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            file_path: Path to the file
        """
        recent_files = self._settings.get("recent_files", [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only last 10 files
        self._settings["recent_files"] = recent_files[:10]
        self._save_settings()
    
    def get_recent_files(self) -> list:
        """
        Get list of recently opened files.
        
        Returns:
            List of file paths
        """
        recent_files = self._settings.get("recent_files", [])
        
        # Filter out files that no longer exist
        existing_files = [f for f in recent_files if os.path.isfile(f)]
        
        # Update list if any files were removed
        if len(existing_files) != len(recent_files):
            self._settings["recent_files"] = existing_files
            self._save_settings()
        
        return existing_files
    
    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self._settings["recent_files"] = []
        self._save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self._settings = self._get_default_settings()
        self._save_settings()


# Global settings manager instance
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """
    Get the global settings manager instance.
    
    Returns:
        Global SettingsManager instance
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
