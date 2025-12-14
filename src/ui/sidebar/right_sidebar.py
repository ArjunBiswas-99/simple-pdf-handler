"""
Simple PDF Handler - Right Sidebar Component

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles.design_tokens import SIZING, get_color
from ui.styles.theme_manager import get_theme_manager


class RightSidebarIconRail(QWidget):
    """
    Icon rail for right sidebar with clickable panel icons.
    Positioned on the RIGHT edge of the sidebar.
    """
    
    # Signals
    icon_clicked = pyqtSignal(int)  # Emits panel index when icon clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_panel = 0
        self._icon_buttons = []
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        """Set up the icon rail UI."""
        from PyQt6.QtWidgets import QVBoxLayout, QPushButton
        
        self.setFixedWidth(SIZING['sidebar_rail_width'])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Create icon buttons (start with 1, can add more later)
        icons = [
            ("ⓘ", "Properties"),
            # Future panels can be added here
            # ("📝", "Notes"),
            # ("🎨", "Appearance"),
            # ("⚙️", "Settings"),
        ]
        
        for idx, (icon, tooltip) in enumerate(icons):
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(SIZING['icon_button_size'] + 12, SIZING['icon_button_size'] + 12)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._on_icon_clicked(i))
            
            self._icon_buttons.append(btn)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Set first button as active
        if self._icon_buttons:
            self._icon_buttons[0].setChecked(True)
        
        layout.addStretch()
    
    def _on_icon_clicked(self, panel_index: int):
        """Handle icon button click."""
        # If clicking the already active panel, emit signal to toggle collapse
        if panel_index == self._active_panel and self._icon_buttons[panel_index].isChecked():
            # Don't uncheck the button here - parent will handle collapse
            pass
        
        # Update active panel
        self._active_panel = panel_index
        
        # Update button states
        for i, btn in enumerate(self._icon_buttons):
            btn.setChecked(i == panel_index)
        
        # Emit signal
        self.icon_clicked.emit(panel_index)
    
    def set_active_panel(self, panel_index: int):
        """Set the active panel index."""
        if 0 <= panel_index < len(self._icon_buttons):
            self._active_panel = panel_index
            for i, btn in enumerate(self._icon_buttons):
                btn.setChecked(i == panel_index)
    
    def get_active_panel(self) -> int:
        """Get currently active panel index."""
        return self._active_panel
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        text_color = get_color('text_primary', is_dark)
        hover_color = get_color('hover', is_dark)
        active_color = get_color('primary', is_dark)
        
        self.setStyleSheet(f"""
            RightSidebarIconRail {{
                background-color: {bg_color};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: {text_color};
                font-size: 20px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:checked {{
                background-color: {active_color};
            }}
        """)


class RightSidebar(QWidget):
    """
    Right sidebar with icon rail and content panels.
    Mirrors left sidebar behavior with collapsible functionality.
    """
    
    # Signals
    collapsed = pyqtSignal()
    expanded = pyqtSignal()
    panel_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_collapsed = True  # Start collapsed
        self._panels = {}
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        """Set up the sidebar UI."""
        # Main horizontal layout: Content | IconRail
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Content panel (left side of right sidebar)
        self._content_stack = QStackedWidget()
        self._content_stack.setFixedWidth(SIZING['sidebar_content_width'])
        layout.addWidget(self._content_stack)
        
        # Icon rail (right edge)
        self._icon_rail = RightSidebarIconRail()
        self._icon_rail.icon_clicked.connect(self._on_icon_clicked)
        layout.addWidget(self._icon_rail)
        
        # Start collapsed (only show icon rail)
        self._content_stack.hide()
        self.setFixedWidth(SIZING['sidebar_rail_width'])
    
    def add_panel(self, panel_index: int, panel_widget: QWidget):
        """
        Add a panel to the sidebar.
        
        Args:
            panel_index: Index for this panel (0, 1, 2, etc.)
            panel_widget: Widget to display in this panel
        """
        self._panels[panel_index] = panel_widget
        self._content_stack.addWidget(panel_widget)
    
    def _on_icon_clicked(self, panel_index: int):
        """Handle icon rail button click."""
        current_panel = self._icon_rail.get_active_panel()
        
        # If clicking the same panel while expanded, collapse
        if panel_index == current_panel and not self._is_collapsed:
            self._collapse()
        else:
            # Switch to clicked panel and expand if collapsed
            if self._is_collapsed:
                self._expand()
            
            # Switch to selected panel
            self._content_stack.setCurrentIndex(panel_index)
            self.panel_changed.emit(panel_index)
    
    def _collapse(self):
        """Collapse the sidebar to show only icon rail."""
        if self._is_collapsed:
            return
        
        self._content_stack.hide()
        self.setFixedWidth(SIZING['sidebar_rail_width'])
        self._is_collapsed = True
        self.collapsed.emit()
    
    def _expand(self):
        """Expand the sidebar to show content panel."""
        if not self._is_collapsed:
            return
        
        self._content_stack.show()
        self.setFixedWidth(SIZING['sidebar_width'])
        self._is_collapsed = False
        self.expanded.emit()
    
    def is_collapsed(self) -> bool:
        """Check if sidebar is currently collapsed."""
        return self._is_collapsed
    
    def set_active_panel(self, panel_index: int):
        """
        Set the active panel and expand sidebar if collapsed.
        
        Args:
            panel_index: Index of panel to activate
        """
        if panel_index in self._panels:
            self._icon_rail.set_active_panel(panel_index)
            self._content_stack.setCurrentIndex(panel_index)
            if self._is_collapsed:
                self._expand()
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        border_color = get_color('divider', is_dark)
        
        self.setStyleSheet(f"""
            RightSidebar {{
                background-color: {bg_color};
                border-left: 1px solid {border_color};
            }}
        """)
