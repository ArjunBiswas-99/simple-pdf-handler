"""
Simple PDF Handler - Settings Manager

Manages application settings and preferences.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class SettingsManager:
    """Manages application settings stored in JSON file."""
    
    def __init__(self, settings_file: str = "settings.json"):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings file relative to app directory
        """
        # Get app directory (where main.py is located)
        app_dir = Path(__file__).parent.parent.parent
        self.settings_path = app_dir / settings_file
        
        # Default settings
        self.defaults = {
            "last_directory": str(Path.home() / "Documents"),
            "window_size": {
                "width": 1400,
                "height": 900
            },
            "recent_files": [],
            "max_recent_files": 10,
            "default_zoom": 100,
            "remember_zoom": True,
            "remember_page": True
        }
        
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file or create with defaults.
        
        Returns:
            Dictionary of settings
        """
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.defaults, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}. Using defaults.")
                return self.defaults.copy()
        else:
            # Create settings file with defaults
            self.save_settings(self.defaults)
            return self.defaults.copy()
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """
        Save settings to file.
        
        Args:
            settings: Settings to save (if None, saves current settings)
            
        Returns:
            True if successful, False otherwise
        """
        if settings is None:
            settings = self.settings
            
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key (supports dot notation like 'window_size.width')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key (supports dot notation)
            value: Value to set
            save: Whether to save settings immediately
            
        Returns:
            True if successful
        """
        keys = key.split('.')
        target = self.settings
        
        # Navigate to the nested location
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
        
        if save:
            return self.save_settings()
        return True
    
    def add_recent_file(self, filepath: str) -> None:
        """
        Add file to recent files list.
        
        Args:
            filepath: Path to file
        """
        recent = self.get('recent_files', [])
        
        # Remove if already in list
        if filepath in recent:
            recent.remove(filepath)
        
        # Add to front
        recent.insert(0, filepath)
        
        # Limit to max recent files
        max_recent = self.get('max_recent_files', 10)
        recent = recent[:max_recent]
        
        self.set('recent_files', recent, save=True)
    
    def update_last_directory(self, filepath: str) -> None:
        """
        Update last directory from file path.
        
        Args:
            filepath: Full path to file
        """
        directory = str(Path(filepath).parent)
        self.set('last_directory', directory, save=True)
    
    def get_last_directory(self) -> str:
        """
        Get last opened directory.
        
        Returns:
            Directory path as string
        """
        last_dir = self.get('last_directory')
        
        # Verify directory exists, otherwise use home
        if not Path(last_dir).exists():
            last_dir = str(Path.home() / "Documents")
            self.set('last_directory', last_dir, save=True)
        
        return last_dir
