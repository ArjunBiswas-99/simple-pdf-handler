"""
Simple PDF Handler - Collapsible Left Side Panel

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

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from typing import Optional


class LeftSidePanel(QWidget):
    """
    Main collapsible left side panel that contains multiple accordion sections.
    Can be collapsed/expanded horizontally to save screen space.
    
    This follows the Open/Closed Principle - new sections can be added
    without modifying the core panel logic.
    """
    
    # Signal emitted when panel collapse state changes
    collapsed_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        """
        Initialize the left side panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._is_collapsed = False
        self._default_width = 300
        self._collapsed_width = 0
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the panel layout and appearance."""
        # Set fixed width for panel
        self.setMinimumWidth(self._default_width)
        self.setMaximumWidth(self._default_width)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with collapse button
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Scrollable content area for accordion sections
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for accordion sections
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(1)
        self._content_layout.addStretch()  # Push sections to top
        
        self._scroll_area.setWidget(self._content_widget)
        main_layout.addWidget(self._scroll_area)
        
        # Styling
        self.setStyleSheet("""
            LeftSidePanel {
                background-color: #f5f5f5;
                border-right: 1px solid #d0d0d0;
            }
        """)
    
    def _create_header(self) -> QWidget:
        """
        Create the panel header.
        
        Returns:
            Header widget
        """
        self._header_widget = QWidget()
        self._header_widget.setFixedHeight(40)
        self._header_widget.setStyleSheet("background-color: #e8e8e8; border-bottom: 1px solid #d0d0d0;")
        
        layout = QHBoxLayout(self._header_widget)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Title label
        self._title_label = QLabel("Left Panel")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._title_label.setFont(font)
        layout.addWidget(self._title_label)
        
        layout.addStretch()
        
        return self._header_widget
    
    def add_section(self, section: 'AccordionSection') -> None:
        """
        Add an accordion section to the panel.
        
        Args:
            section: AccordionSection widget to add
        """
        # Insert before the stretch at the end
        count = self._content_layout.count()
        self._content_layout.insertWidget(count - 1, section)
    
    def toggle_collapse(self) -> None:
        """Toggle the collapsed state of the panel."""
        self._is_collapsed = not self._is_collapsed
        
        if self._is_collapsed:
            # Hide the panel completely
            self.setVisible(False)
        else:
            # Show the panel
            self.setVisible(True)
        
        self.collapsed_changed.emit(self._is_collapsed)
    
    def is_collapsed(self) -> bool:
        """
        Check if panel is collapsed.
        
        Returns:
            True if collapsed, False otherwise
        """
        return self._is_collapsed


class AccordionSection(QWidget):
    """
    Reusable accordion section component for left side panel.
    Contains a header that can be clicked to expand/collapse the content.
    
    This follows the Single Responsibility Principle - only handles
    the accordion expand/collapse behavior, not the content itself.
    """
    
    # Signal emitted when section is expanded/collapsed
    expanded_changed = pyqtSignal(bool)
    
    def __init__(self, title: str, icon: str = "", parent=None):
        """
        Initialize the accordion section.
        
        Args:
            title: Title text for the section header
            icon: Optional icon/emoji for the header
            parent: Parent widget
        """
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._is_expanded = False
        self._content_widget: Optional[QWidget] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the accordion section layout."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create header
        self._header = self._create_header()
        layout.addWidget(self._header)
        
        # Content container (initially hidden)
        self._content_container = QWidget()
        self._content_container.setVisible(False)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        layout.addWidget(self._content_container)
        
        # Styling
        self.setStyleSheet("""
            AccordionSection {
                background-color: white;
                border: 1px solid #d0d0d0;
            }
        """)
    
    def _create_header(self) -> QPushButton:
        """
        Create the clickable header for the accordion section.
        
        Returns:
            Header button widget
        """
        header = QPushButton()
        header.setFixedHeight(40)
        header.clicked.connect(self.toggle_expanded)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # Expand/collapse arrow
        self._arrow_label = QLabel("▶")
        self._arrow_label.setFixedWidth(20)
        font = QFont()
        font.setPointSize(10)
        self._arrow_label.setFont(font)
        header_layout.addWidget(self._arrow_label)
        
        # Icon (if provided)
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setFixedWidth(20)
            header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self._title)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Set layout
        header.setLayout(header_layout)
        
        # Styling
        header.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                border: none;
                border-bottom: 1px solid #d0d0d0;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
            }
        """)
        
        return header
    
    def set_content(self, widget: QWidget) -> None:
        """
        Set the content widget for this accordion section.
        
        Args:
            widget: Content widget to display when expanded
        """
        # Remove existing content if any
        if self._content_widget:
            self._content_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()
        
        # Add new content
        self._content_widget = widget
        self._content_layout.addWidget(self._content_widget)
    
    def toggle_expanded(self) -> None:
        """Toggle the expanded state of the accordion section."""
        self._is_expanded = not self._is_expanded
        
        if self._is_expanded:
            self._arrow_label.setText("▼")
            self._content_container.setVisible(True)
        else:
            self._arrow_label.setText("▶")
            self._content_container.setVisible(False)
        
        self.expanded_changed.emit(self._is_expanded)
    
    def set_expanded(self, expanded: bool) -> None:
        """
        Programmatically set the expanded state.
        
        Args:
            expanded: True to expand, False to collapse
        """
        if self._is_expanded != expanded:
            self.toggle_expanded()
    
    def is_expanded(self) -> bool:
        """
        Check if section is expanded.
        
        Returns:
            True if expanded, False otherwise
        """
        return self._is_expanded
