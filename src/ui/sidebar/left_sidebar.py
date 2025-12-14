"""
Simple PDF Handler - Left Sidebar Container

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import pyqtSignal
from ui.styles.design_tokens import SIZING, SidebarMode
from ui.styles.theme_manager import get_theme_manager
from .sidebar_icon_rail import SidebarIconRail


class LeftSidebar(QWidget):
    """
    Left sidebar container with icon rail and content panels.
    Total width: 280px (48px rail + 232px content).
    """
    
    # Signals
    panel_changed = pyqtSignal(SidebarMode)
    collapsed = pyqtSignal()  # Emitted when sidebar collapses
    expanded = pyqtSignal()   # Emitted when sidebar expands
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_collapsed = False
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the sidebar UI."""
        self.setFixedWidth(SIZING['sidebar_width'])
        
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Create icon rail
        self._icon_rail = SidebarIconRail()
        self._icon_rail.mode_changed.connect(self._on_mode_changed)
        self._icon_rail.toggle_requested.connect(self.toggle_collapse)
        layout.addWidget(self._icon_rail)
        
        # Create stacked widget for content panels
        self._panel_stack = QStackedWidget()
        layout.addWidget(self._panel_stack)
    
    def add_panel(self, mode: SidebarMode, panel: QWidget) -> None:
        """
        Add a content panel for a specific mode.
        
        Args:
            mode: Sidebar mode this panel belongs to
            panel: Widget to display for this mode
        """
        # Add to stack at the index matching the mode value
        while self._panel_stack.count() <= mode.value:
            # Add placeholder if needed
            self._panel_stack.addWidget(QWidget())
        
        # Set or replace the panel at this mode's index
        if self._panel_stack.count() > mode.value:
            old_widget = self._panel_stack.widget(mode.value)
            if old_widget:
                self._panel_stack.removeWidget(old_widget)
                old_widget.deleteLater()
        
        self._panel_stack.insertWidget(mode.value, panel)
    
    def _on_mode_changed(self, mode: SidebarMode) -> None:
        """Handle mode change from icon rail."""
        # If sidebar is collapsed, expand it when switching panels
        if self._is_collapsed:
            self.expand()
        
        # Switch to the panel for this mode
        self._panel_stack.setCurrentIndex(mode.value)
        
        # Emit signal
        self.panel_changed.emit(mode)
    
    def toggle_collapse(self) -> None:
        """Toggle sidebar between collapsed and expanded states."""
        if self._is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self) -> None:
        """Collapse sidebar to show only icon rail."""
        if self._is_collapsed:
            return
        
        self._is_collapsed = True
        
        # Remove panel stack from layout
        self.layout().removeWidget(self._panel_stack)
        self._panel_stack.hide()
        
        # Set sidebar to icon rail width
        self.setFixedWidth(SIZING['sidebar_rail_width'])
        
        # Emit signal so MainWindow can update splitter
        self.collapsed.emit()
    
    def expand(self) -> None:
        """Expand sidebar to show icon rail and content panel."""
        if not self._is_collapsed:
            return
        
        self._is_collapsed = False
        
        # Add panel stack back to layout
        self.layout().addWidget(self._panel_stack)
        self._panel_stack.show()
        
        # Restore sidebar to full width
        self.setFixedWidth(SIZING['sidebar_width'])
        
        # Emit signal so MainWindow can update splitter
        self.expanded.emit()
    
    def is_collapsed(self) -> bool:
        """Check if sidebar is currently collapsed."""
        return self._is_collapsed
    
    def set_mode(self, mode: SidebarMode) -> None:
        """Programmatically set the active mode."""
        self._icon_rail.set_mode(mode)
        self._panel_stack.setCurrentIndex(mode.value)
    
    def get_current_mode(self) -> SidebarMode:
        """Get the currently active sidebar mode."""
        return SidebarMode(self._panel_stack.currentIndex())
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling."""
        # Sidebar styling is handled by child components
        pass
