"""
Simple PDF Handler - Theme Definitions

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

from enum import Enum
from typing import Dict


class ThemeType(Enum):
    """Available theme types."""
    LIGHT = "light"
    DARK = "dark"


class LightTheme:
    """
    Professional Blue Light Theme.
    Modern, clean appearance suitable for extended use.
    """
    
    # Primary colors
    PRIMARY = "#2196F3"  # Modern Blue
    PRIMARY_DARK = "#1976D2"  # Darker Blue
    PRIMARY_LIGHT = "#64B5F6"  # Lighter Blue
    ACCENT = "#FFC107"  # Amber accent
    
    # Background colors
    BACKGROUND = "#F5F5F5"  # Light Gray
    SURFACE = "#FFFFFF"  # White
    CANVAS_BG = "#525252"  # Dark Gray (for PDF background)
    
    # Text colors
    TEXT_PRIMARY = "#212121"  # Dark Gray
    TEXT_SECONDARY = "#757575"  # Medium Gray
    TEXT_ON_PRIMARY = "#FFFFFF"  # White
    
    # UI element colors
    BORDER = "#E0E0E0"  # Light Border
    HOVER = "#BBDEFB"  # Light Blue
    DISABLED = "#BDBDBD"  # Gray
    
    # Status colors
    SUCCESS = "#4CAF50"  # Green
    WARNING = "#FF9800"  # Orange
    ERROR = "#F44336"  # Red


class DarkTheme:
    """
    Modern Dark Theme.
    Reduces eye strain in low-light conditions.
    """
    
    # Primary colors
    PRIMARY = "#1E88E5"  # Bright Blue
    PRIMARY_DARK = "#1565C0"  # Darker Blue
    PRIMARY_LIGHT = "#42A5F5"  # Lighter Blue
    ACCENT = "#FFC107"  # Amber accent
    
    # Background colors
    BACKGROUND = "#263238"  # Dark Blue-Gray
    SURFACE = "#37474F"  # Lighter Dark
    CANVAS_BG = "#1A1A1A"  # Almost Black
    
    # Text colors
    TEXT_PRIMARY = "#ECEFF1"  # Light Text
    TEXT_SECONDARY = "#B0BEC5"  # Medium Light
    TEXT_ON_PRIMARY = "#FFFFFF"  # White
    
    # UI element colors
    BORDER = "#455A64"  # Dark Border
    HOVER = "#546E7A"  # Lighter Dark
    DISABLED = "#607D8B"  # Muted
    
    # Status colors
    SUCCESS = "#66BB6A"  # Light Green
    WARNING = "#FFA726"  # Light Orange
    ERROR = "#EF5350"  # Light Red


def get_theme_colors(theme_type: ThemeType) -> Dict[str, str]:
    """
    Get color dictionary for the specified theme.
    
    Args:
        theme_type: Type of theme to get colors for
        
    Returns:
        Dictionary mapping color names to hex values
    """
    theme_class = LightTheme if theme_type == ThemeType.LIGHT else DarkTheme
    
    return {
        "primary": theme_class.PRIMARY,
        "primary_dark": theme_class.PRIMARY_DARK,
        "primary_light": theme_class.PRIMARY_LIGHT,
        "accent": theme_class.ACCENT,
        "background": theme_class.BACKGROUND,
        "surface": theme_class.SURFACE,
        "canvas_bg": theme_class.CANVAS_BG,
        "text_primary": theme_class.TEXT_PRIMARY,
        "text_secondary": theme_class.TEXT_SECONDARY,
        "text_on_primary": theme_class.TEXT_ON_PRIMARY,
        "border": theme_class.BORDER,
        "hover": theme_class.HOVER,
        "disabled": theme_class.DISABLED,
        "success": theme_class.SUCCESS,
        "warning": theme_class.WARNING,
        "error": theme_class.ERROR,
    }
