"""
Simple PDF Handler - Edit Tools Panel

Provides a comprehensive set of tools for editing PDF documents.
Organized into logical sections: Add Content, Modify, and Arrange.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class EditToolsPanel(QWidget):
    """
    Panel containing editing tools for PDF documents.
    
    This panel is displayed in the right sidebar when Edit mode is active.
    It provides tools organized into three main sections:
    - Add Content: Tools for adding new elements (text, images, pages)
    - Modify: Tools for editing existing elements
    - Arrange: Tools for managing object layering and positioning
    """
    
    # Signals emitted when tools are clicked
    add_text_clicked = pyqtSignal()
    add_image_clicked = pyqtSignal()
    add_page_clicked = pyqtSignal()
    attach_file_clicked = pyqtSignal()
    
    undo_clicked = pyqtSignal()
    redo_clicked = pyqtSignal()
    
    select_object_clicked = pyqtSignal()
    edit_text_clicked = pyqtSignal()
    edit_image_clicked = pyqtSignal()
    delete_object_clicked = pyqtSignal()
    
    bring_forward_clicked = pyqtSignal()
    send_backward_clicked = pyqtSignal()
    bring_to_front_clicked = pyqtSignal()
    send_to_back_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the edit tools panel."""
        super().__init__(parent)
        self._undo_button = None
        self._redo_button = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the panel layout and widgets."""
        # Main layout with spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Undo/Redo at TOP (always visible)
        layout.addWidget(self._create_undo_redo_section())
        
        # Add Content Section
        layout.addWidget(self._create_section_label("📝 ADD CONTENT"))
        layout.addWidget(self._create_add_content_section())
        
        # Modify Section
        layout.addWidget(self._create_section_label("🔧 MODIFY"))
        layout.addWidget(self._create_modify_section())
        
        # Arrange Section
        layout.addWidget(self._create_section_label("🎯 ARRANGE"))
        layout.addWidget(self._create_arrange_section())
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _create_section_label(self, text: str) -> QLabel:
        """
        Create a section header label.
        
        Args:
            text: Section title text
            
        Returns:
            Styled QLabel for section header
        """
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #666666;
                letter-spacing: 0.5px;
                padding: 4px 0px;
            }
        """)
        return label
    
    def _create_add_content_section(self) -> QWidget:
        """
        Create the Add Content section with buttons.
        
        Returns:
            Widget containing add content buttons
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Add Text button
        add_text_btn = self._create_tool_button("Add Text", "T")
        add_text_btn.clicked.connect(self.add_text_clicked.emit)
        layout.addWidget(add_text_btn)
        
        # Add Image button
        add_image_btn = self._create_tool_button("Add Image", "🖼️")
        add_image_btn.clicked.connect(self.add_image_clicked.emit)
        layout.addWidget(add_image_btn)
        
        # Add Blank Page button
        add_page_btn = self._create_tool_button("Add Blank Page", "📄")
        add_page_btn.clicked.connect(self.add_page_clicked.emit)
        layout.addWidget(add_page_btn)
        
        # Attach File button
        attach_file_btn = self._create_tool_button("Attach File", "📎")
        attach_file_btn.clicked.connect(self.attach_file_clicked.emit)
        layout.addWidget(attach_file_btn)
        
        container.setLayout(layout)
        return container
    
    def _create_undo_redo_section(self) -> QWidget:
        """
        Create Undo/Redo buttons at top of panel.
        
        Returns:
            Widget containing undo/redo buttons
        """
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Undo button
        self._undo_button = self._create_tool_button("Undo", "↶")
        self._undo_button.setEnabled(False)
        self._undo_button.clicked.connect(self.undo_clicked.emit)
        layout.addWidget(self._undo_button)
        
        # Redo button
        self._redo_button = self._create_tool_button("Redo", "↷")
        self._redo_button.setEnabled(False)
        self._redo_button.clicked.connect(self.redo_clicked.emit)
        layout.addWidget(self._redo_button)
        
        container.setLayout(layout)
        return container
    
    def _create_modify_section(self) -> QWidget:
        """
        Create the Modify section with buttons.
        
        Returns:
            Widget containing modify buttons
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Select Object button
        select_btn = self._create_tool_button("Select Object", "⬜")
        select_btn.clicked.connect(self.select_object_clicked.emit)
        layout.addWidget(select_btn)
        
        # Edit Text button
        edit_text_btn = self._create_tool_button("Edit Text", "✏️")
        edit_text_btn.clicked.connect(self.edit_text_clicked.emit)
        layout.addWidget(edit_text_btn)
        
        # Edit Image button
        edit_image_btn = self._create_tool_button("Edit Image", "🖼️")
        edit_image_btn.clicked.connect(self.edit_image_clicked.emit)
        layout.addWidget(edit_image_btn)
        
        # Delete button
        delete_btn = self._create_tool_button("Delete", "🗑️")
        delete_btn.clicked.connect(self.delete_object_clicked.emit)
        layout.addWidget(delete_btn)
        
        container.setLayout(layout)
        return container
    
    def _create_arrange_section(self) -> QWidget:
        """
        Create the Arrange section with buttons.
        
        Returns:
            Widget containing arrange buttons
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Bring Forward button
        forward_btn = self._create_tool_button("Bring Forward", "↑")
        forward_btn.clicked.connect(self.bring_forward_clicked.emit)
        layout.addWidget(forward_btn)
        
        # Send Backward button
        backward_btn = self._create_tool_button("Send Backward", "↓")
        backward_btn.clicked.connect(self.send_backward_clicked.emit)
        layout.addWidget(backward_btn)
        
        # Bring to Front button
        to_front_btn = self._create_tool_button("Bring to Front", "⬆️")
        to_front_btn.clicked.connect(self.bring_to_front_clicked.emit)
        layout.addWidget(to_front_btn)
        
        # Send to Back button
        to_back_btn = self._create_tool_button("Send to Back", "⬇️")
        to_back_btn.clicked.connect(self.send_to_back_clicked.emit)
        layout.addWidget(to_back_btn)
        
        container.setLayout(layout)
        return container
    
    def _create_tool_button(self, text: str, icon_text: str) -> QPushButton:
        """
        Create a styled tool button.
        
        Args:
            text: Button label text
            icon_text: Icon or emoji to display
            
        Returns:
            Styled QPushButton
        """
        button = QPushButton(f"{icon_text}  {text}")
        button.setMinimumHeight(36)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-size: 13px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #0078D4;
            }
            QPushButton:pressed {
                background-color: #E8E8E8;
            }
            QPushButton:disabled {
                background-color: #F5F5F5;
                color: #999999;
                border-color: #EEEEEE;
            }
        """)
        return button
    
    def set_tools_enabled(self, enabled: bool) -> None:
        """
        Enable or disable all tools.
        
        Args:
            enabled: True to enable tools, False to disable
        """
        # Enable/disable all buttons in the panel except undo/redo
        # (undo/redo have their own state management)
        for button in self.findChildren(QPushButton):
            if button not in (self._undo_button, self._redo_button):
                button.setEnabled(enabled)
    
    def set_undo_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the undo button.
        
        Args:
            enabled: True to enable, False to disable
        """
        if self._undo_button:
            self._undo_button.setEnabled(enabled)
    
    def set_redo_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the redo button.
        
        Args:
            enabled: True to enable, False to disable
        """
        if self._redo_button:
            self._redo_button.setEnabled(enabled)
