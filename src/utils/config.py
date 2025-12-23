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
    
    # File dialog preferences
    def get_last_directory(self) -> str:
        """
        Get last used directory for file dialogs.
        
        Returns:
            Directory path, or home directory if not set
        """
        from pathlib import Path
        default_dir = str(Path.home())
        return self.settings.value("file/last_directory", default_dir, str)
    
    def set_last_directory(self, directory: str) -> None:
        """
        Save last used directory.
        
        Args:
            directory: Directory path
        """
        self.settings.setValue("file/last_directory", directory)
    
    # OCR settings
    def get_ocr_default_language(self) -> str:
        """
        Get default OCR language preference.
        
        Returns:
            Language code ('auto', 'en', 'es', etc.)
        """
        return self.settings.value("ocr/default_language", "auto", str)
    
    def set_ocr_default_language(self, language: str) -> None:
        """
        Save default OCR language.
        
        Args:
            language: Language code
        """
        self.settings.setValue("ocr/default_language", language)
    
    def get_ocr_save_behavior(self) -> str:
        """
        Get OCR save behavior preference.
        
        Returns:
            Save behavior ('always_ask', 'auto_save', 'save_as_new')
        """
        return self.settings.value("ocr/save_behavior", "always_ask", str)
    
    def set_ocr_save_behavior(self, behavior: str) -> None:
        """
        Save OCR save behavior.
        
        Args:
            behavior: Save behavior option
        """
        self.settings.setValue("ocr/save_behavior", behavior)
    
    def get_ocr_auto_deskew(self) -> bool:
        """Get auto-deskew preference."""
        return self.settings.value("ocr/auto_deskew", True, bool)
    
    def set_ocr_auto_deskew(self, enabled: bool) -> None:
        """Save auto-deskew preference."""
        self.settings.setValue("ocr/auto_deskew", enabled)
    
    def get_ocr_despeckle(self) -> bool:
        """Get despeckle preference."""
        return self.settings.value("ocr/despeckle", True, bool)
    
    def set_ocr_despeckle(self, enabled: bool) -> None:
        """Save despeckle preference."""
        self.settings.setValue("ocr/despeckle", enabled)
    
    def get_ocr_enhance_image(self) -> bool:
        """Get image enhancement preference."""
        return self.settings.value("ocr/enhance_image", True, bool)
    
    def set_ocr_enhance_image(self, enabled: bool) -> None:
        """Save image enhancement preference."""
        self.settings.setValue("ocr/enhance_image", enabled)
    
    def get_ocr_compress_output(self) -> bool:
        """Get output compression preference."""
        return self.settings.value("ocr/compress_output", True, bool)
    
    def set_ocr_compress_output(self, enabled: bool) -> None:
        """Save output compression preference."""
        self.settings.setValue("ocr/compress_output", enabled)
    
    def get_ocr_detect_tables(self) -> bool:
        """Get table detection preference."""
        return self.settings.value("ocr/detect_tables", True, bool)
    
    def set_ocr_detect_tables(self, enabled: bool) -> None:
        """Save table detection preference."""
        self.settings.setValue("ocr/detect_tables", enabled)
    
    def get_ocr_highlight_uncertain(self) -> bool:
        """Get uncertain text highlighting preference."""
        return self.settings.value("ocr/highlight_uncertain", True, bool)
    
    def set_ocr_highlight_uncertain(self, enabled: bool) -> None:
        """Save uncertain text highlighting preference."""
        self.settings.setValue("ocr/highlight_uncertain", enabled)
    
    def get_ocr_confidence_threshold(self) -> int:
        """
        Get OCR confidence threshold (0-100).
        
        Returns:
            Threshold percentage
        """
        return self.settings.value("ocr/confidence_threshold", 75, int)
    
    def set_ocr_confidence_threshold(self, threshold: int) -> None:
        """
        Save OCR confidence threshold.
        
        Args:
            threshold: Threshold percentage (0-100)
        """
        self.settings.setValue("ocr/confidence_threshold", threshold)
    
    def get_ocr_installed_languages(self) -> List[str]:
        """
        Get list of installed OCR language codes.
        
        Returns:
            List of language codes
        """
        # Default pre-installed languages
        default_langs = ["en", "es", "zh", "hi", "bn", "de"]
        size = self.settings.beginReadArray("ocr/installed_languages")
        if size == 0:
            self.settings.endArray()
            return default_langs
        
        languages = []
        for i in range(size):
            self.settings.setArrayIndex(i)
            lang = self.settings.value("code", "", str)
            if lang:
                languages.append(lang)
        self.settings.endArray()
        return languages if languages else default_langs
    
    def set_ocr_installed_languages(self, languages: List[str]) -> None:
        """
        Save list of installed OCR languages.
        
        Args:
            languages: List of language codes
        """
        self.settings.beginWriteArray("ocr/installed_languages")
        for i, lang in enumerate(languages):
            self.settings.setArrayIndex(i)
            self.settings.setValue("code", lang)
        self.settings.endArray()
    
    def get_ocr_statistics(self) -> Dict[str, Any]:
        """
        Get OCR usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_ocr_runs": self.settings.value("ocr/stats/total_runs", 0, int),
            "total_pages_processed": self.settings.value("ocr/stats/total_pages", 0, int),
            "total_words_recognized": self.settings.value("ocr/stats/total_words", 0, int),
            "average_confidence": self.settings.value("ocr/stats/avg_confidence", 0.0, float),
        }
    
    def update_ocr_statistics(self, pages: int, words: int, confidence: float) -> None:
        """
        Update OCR statistics after a run.
        
        Args:
            pages: Number of pages processed
            words: Number of words recognized
            confidence: Average confidence score
        """
        stats = self.get_ocr_statistics()
        stats["total_ocr_runs"] += 1
        stats["total_pages_processed"] += pages
        stats["total_words_recognized"] += words
        
        # Update running average confidence
        total_runs = stats["total_ocr_runs"]
        old_avg = stats["average_confidence"]
        stats["average_confidence"] = ((old_avg * (total_runs - 1)) + confidence) / total_runs
        
        self.settings.setValue("ocr/stats/total_runs", stats["total_ocr_runs"])
        self.settings.setValue("ocr/stats/total_pages", stats["total_pages_processed"])
        self.settings.setValue("ocr/stats/total_words", stats["total_words_recognized"])
        self.settings.setValue("ocr/stats/avg_confidence", stats["average_confidence"])
    
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
