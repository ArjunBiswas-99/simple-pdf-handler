"""
Simple PDF Handler - Attachments Panel

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.styles.design_tokens import SPACING, get_color
from ui.styles.theme_manager import get_theme_manager


class AttachmentsPanel(QWidget):
    """
    Attachments panel for sidebar.
    Shows PDF attachments/embedded files.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the panel UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        self.setLayout(layout)
        
        # Title
        title = QLabel("ATTACHMENTS")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Placeholder message
        message = QLabel("No attachments\nor\nComing soon")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: gray; padding: 40px;")
        layout.addWidget(message)
        
        layout.addStretch()
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        bg_color = get_color('surface', is_dark)
        self.setStyleSheet(f"AttachmentsPanel {{ background-color: {bg_color}; }}")
