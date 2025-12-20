"""
Simple PDF Handler - Core Module

Contains base classes and application initialization logic.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from .app import PDFHandlerApp
from .base_controller import BaseController
from .theme_manager import ThemeManager

__all__ = ['PDFHandlerApp', 'BaseController', 'ThemeManager']
