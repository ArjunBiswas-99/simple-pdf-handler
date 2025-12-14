"""
Simple PDF Handler - Design Tokens System

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

import platform
from enum import Enum


def get_system_font() -> str:
    """
    Get the most professional system font for the current platform.
    
    Returns:
        Font family name optimized for the current OS
    """
    system = platform.system()
    
    if system == 'Windows':
        # Segoe UI - Microsoft's flagship UI font
        return 'Segoe UI'
    elif system == 'Darwin':  # macOS
        # Use .AppleSystemUIFont for native macOS system font
        # Falls back to Helvetica which is always available on macOS
        return '.AppleSystemUIFont, Helvetica Neue, Helvetica'
    else:  # Linux
        # Ubuntu and Roboto are excellent professional fonts
        return 'Ubuntu, Roboto'


class AppMode(Enum):
    """Application modes for different PDF operations"""
    VIEW = "View"
    COMMENT = "Comment"
    EDIT = "Edit"
    ORGANIZE = "Organize"
    CONVERT_OCR = "Convert & OCR"


class SidebarMode(Enum):
    """Sidebar panel modes"""
    PAGES = 0
    BOOKMARKS = 1
    SEARCH = 2
    ATTACHMENTS = 3


# Colors - Organized by theme
COLORS = {
    # Primary colors
    'primary': '#0066CC',
    'primary_hover': '#0052A3',
    'primary_pressed': '#003D7A',
    'accent': '#FF6B35',
    'accent_hover': '#E55A2B',
    
    # Light theme
    'background_light': '#FFFFFF',
    'surface_light': '#F5F5F5',
    'surface_elevated_light': '#FAFAFA',
    'hover_light': '#E8E8E8',
    'text_primary_light': '#212121',
    'text_secondary_light': '#757575',
    'text_disabled_light': '#BDBDBD',
    'border_light': '#E0E0E0',
    'border_hover_light': '#BDBDBD',
    'divider_light': '#E0E0E0',
    
    # Dark theme
    'background_dark': '#1E1E1E',
    'surface_dark': '#2B2B2B',
    'surface_elevated_dark': '#333333',
    'hover_dark': '#3A3A3A',
    'text_primary_dark': '#E0E0E0',
    'text_secondary_dark': '#A0A0A0',
    'text_disabled_dark': '#5A5A5A',
    'border_dark': '#404040',
    'border_hover_dark': '#606060',
    'divider_dark': '#404040',
    
    # Semantic colors (theme-independent)
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',
    
    # Search highlight colors
    'highlight': '#FFF176',
    'highlight_current': '#FFD54F',
    'highlight_border': '#FBC02D',
    
    # Canvas background (PDF viewer area)
    'canvas_bg_light': '#525252',
    'canvas_bg_dark': '#1A1A1A',
}


# Spacing - Using 8px grid system
SPACING = {
    'xs': 4,      # Extra small
    'sm': 8,      # Small
    'md': 16,     # Medium (base unit)
    'lg': 24,     # Large
    'xl': 32,     # Extra large
    'xxl': 48,    # Extra extra large
}


# Sizing - Component dimensions
SIZING = {
    # Top bar
    'appbar_height': 48,
    'mode_tabs_height': 40,
    'toolbar_height': 48,
    
    # Sidebar
    'sidebar_rail_width': 48,
    'sidebar_content_width': 232,
    'sidebar_width': 280,  # 48 + 232
    'sidebar_min_width': 48,     # When collapsed
    
    # Right panel
    'right_panel_width': 280,
    'right_panel_min_width': 0,  # When collapsed
    
    # Bottom bar
    'status_bar_height': 24,
    
    # Button sizes
    'button_height': 32,
    'button_min_width': 32,
    'icon_button_size': 32,
    
    # Input sizes
    'input_height': 28,
    'combo_min_width': 75,
    'combo_max_width': 85,
}


# Typography
TYPOGRAPHY = {
    # Use platform-specific professional font with fallbacks
    'font_family': f'{get_system_font()}, sans-serif',
    
    # Font sizes
    'font_size_small': 11,
    'font_size_normal': 13,
    'font_size_large': 15,
    'font_size_title': 18,
    'font_size_heading': 16,
    
    # Font weights
    'font_weight_normal': 400,
    'font_weight_medium': 500,
    'font_weight_semibold': 600,
    'font_weight_bold': 700,
    
    # Line heights
    'line_height_tight': 1.2,
    'line_height_normal': 1.5,
    'line_height_relaxed': 1.75,
}


# Border radius
BORDER_RADIUS = {
    'none': 0,
    'small': 4,
    'medium': 6,
    'large': 8,
    'xlarge': 12,
    'round': 9999,  # Fully rounded
}


# Shadows
SHADOWS = {
    'none': 'none',
    'small': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.06)',
    'medium': '0 2px 6px rgba(0, 0, 0, 0.16), 0 2px 4px rgba(0, 0, 0, 0.08)',
    'large': '0 4px 12px rgba(0, 0, 0, 0.20), 0 4px 8px rgba(0, 0, 0, 0.10)',
    'xlarge': '0 8px 24px rgba(0, 0, 0, 0.24), 0 8px 16px rgba(0, 0, 0, 0.12)',
}


# Animation durations (milliseconds)
ANIMATION = {
    'instant': 0,
    'fast': 150,
    'normal': 250,
    'slow': 350,
    'very_slow': 500,
}


# Z-index layers
Z_INDEX = {
    'base': 0,
    'dropdown': 100,
    'sticky': 200,
    'fixed': 300,
    'modal_backdrop': 400,
    'modal': 500,
    'popover': 600,
    'tooltip': 700,
}


# Icon sizes (for emoji/unicode icons)
ICON_SIZES = {
    'small': 14,
    'medium': 16,
    'large': 20,
    'xlarge': 24,
}


def get_color(key: str, is_dark_theme: bool = False) -> str:
    """
    Get a color value with theme awareness.
    
    Args:
        key: Color key (without _light or _dark suffix)
        is_dark_theme: Whether dark theme is active
        
    Returns:
        Color hex value
    """
    # Check if key has theme variants
    theme_suffix = '_dark' if is_dark_theme else '_light'
    theme_key = f"{key}{theme_suffix}"
    
    if theme_key in COLORS:
        return COLORS[theme_key]
    
    # Return key as-is if no theme variant exists
    return COLORS.get(key, '#000000')


def get_spacing(size: str) -> int:
    """Get spacing value by size name"""
    return SPACING.get(size, SPACING['md'])


def get_sizing(key: str) -> int:
    """Get sizing value by key"""
    return SIZING.get(key, 0)


def get_font_size(size: str) -> int:
    """Get font size value"""
    key = f"font_size_{size}"
    return TYPOGRAPHY.get(key, TYPOGRAPHY['font_size_normal'])


def get_border_radius(size: str) -> int:
    """Get border radius value"""
    return BORDER_RADIUS.get(size, BORDER_RADIUS['medium'])
