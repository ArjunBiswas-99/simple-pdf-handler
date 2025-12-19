"""
Simple PDF Handler - Edit Tools Panel

Provides essential tools for editing PDF documents.
Streamlined interface with only the most frequently used editing tools.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.widgets import ShapeDrawingToolbar


class EditToolsPanel(QWidget):
    """
    Panel containing essential editing tools for PDF documents.
    
    This panel is displayed in the right sidebar when Edit mode is active.
    Provides streamlined tools organized into sections:
    - Undo/Redo: Quick access to undo and redo operations
    - Content Tools: Add text, images, pages, and files
    - Edit Pages: Toggle page editing mode (delete, add, reorder)
    """
    
    # Content tool signals
    add_text_clicked = pyqtSignal()
    add_image_clicked = pyqtSignal()
    add_blank_page_clicked = pyqtSignal()
    attach_file_clicked = pyqtSignal()
    edit_text_clicked = pyqtSignal()
    
    # Page editing signals
    edit_pages_toggled = pyqtSignal(bool)  # True when entering edit mode, False when exiting
    
    # Undo/redo signals
    undo_clicked = pyqtSignal()
    redo_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the edit tools panel."""
        super().__init__(parent)
        self._undo_button = None
        self._redo_button = None
        self._edit_pages_button = None
        self._pages_edit_mode_active = False
        self._shape_toolbar = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the panel layout and widgets with scroll area."""
        # Create scroll area for the panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create container widget for all content
        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(20)
        
        # Undo/Redo Section (Always at top)
        content_layout.addWidget(self._create_undo_redo_section())
        
        # Add separator
        content_layout.addWidget(self._create_separator())
        
        # Content Tools Section
        content_layout.addWidget(self._create_section_label("📝 CONTENT TOOLS"))
        content_layout.addWidget(self._create_content_tools_section())
        
        # Add separator
        content_layout.addWidget(self._create_separator())
        
        # Shape Drawing Section
        self._shape_toolbar = ShapeDrawingToolbar()
        content_layout.addWidget(self._shape_toolbar)
        
        # Add separator
        content_layout.addWidget(self._create_separator())
        
        # Edit Pages Toggle Button
        content_layout.addWidget(self._create_edit_pages_section())
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set container as scroll area's widget
        scroll_area.setWidget(container)
        
        # Set scroll area as the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
    def _create_separator(self) -> QWidget:
        """
        Create a horizontal separator line.
        
        Returns:
            Widget acting as visual separator
        """
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #EEEEEE;")
        return separator
    
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
    
    def _create_undo_redo_section(self) -> QWidget:
        """
        Create Undo/Redo buttons section.
        Placed at top for quick access.
        
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
        self._undo_button.setToolTip("Undo last action (Ctrl+Z)")
        self._undo_button.clicked.connect(self.undo_clicked.emit)
        layout.addWidget(self._undo_button)
        
        # Redo button
        self._redo_button = self._create_tool_button("Redo", "↷")
        self._redo_button.setEnabled(False)
        self._redo_button.setToolTip("Redo last undone action (Ctrl+Shift+Z)")
        self._redo_button.clicked.connect(self.redo_clicked.emit)
        layout.addWidget(self._redo_button)
        
        container.setLayout(layout)
        return container
    
    def _create_content_tools_section(self) -> QWidget:
        """
        Create the content tools section with essential editing buttons.
        
        Returns:
            Widget containing content tool buttons
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Add Text button
        add_text_btn = self._create_tool_button("Add Text", "T")
        add_text_btn.setToolTip("Click on PDF to add text")
        add_text_btn.clicked.connect(self.add_text_clicked.emit)
        layout.addWidget(add_text_btn)
        
        # Add Image button
        add_image_btn = self._create_tool_button("Add Image", "🖼️")
        add_image_btn.setToolTip("Add image to PDF page (Coming soon)")
        add_image_btn.clicked.connect(self.add_image_clicked.emit)
        layout.addWidget(add_image_btn)
        
        # Add Blank Page button
        add_blank_page_btn = self._create_tool_button("Add Blank Page", "📄")
        add_blank_page_btn.setToolTip("Insert a blank page at the end")
        add_blank_page_btn.clicked.connect(self.add_blank_page_clicked.emit)
        layout.addWidget(add_blank_page_btn)
        
        # Attach File button
        attach_file_btn = self._create_tool_button("Attach File", "📎")
        attach_file_btn.setToolTip("Attach file to PDF (Coming soon)")
        attach_file_btn.clicked.connect(self.attach_file_clicked.emit)
        layout.addWidget(attach_file_btn)
        
        # Edit Text button
        edit_text_btn = self._create_tool_button("Edit Text", "✏️")
        edit_text_btn.setToolTip("Edit existing text (Coming soon)")
        edit_text_btn.clicked.connect(self.edit_text_clicked.emit)
        layout.addWidget(edit_text_btn)
        
        container.setLayout(layout)
        return container
    
    def _create_edit_pages_section(self) -> QWidget:
        """
        Create the Edit Pages toggle button section.
        
        Returns:
            Widget containing edit pages toggle button
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Section label
        label = QLabel("📄 PAGE MANAGEMENT")
        label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #666666;
                letter-spacing: 0.5px;
                padding: 4px 0px;
            }
        """)
        layout.addWidget(label)
        
        # Edit Pages toggle button
        self._edit_pages_button = self._create_toggle_button("Edit Pages", "✂️")
        self._edit_pages_button.setToolTip("Enable page editing: delete, add, and reorder pages")
        self._edit_pages_button.clicked.connect(self._on_edit_pages_clicked)
        layout.addWidget(self._edit_pages_button)
        
        container.setLayout(layout)
        return container
    
    def _on_edit_pages_clicked(self) -> None:
        """Handle edit pages button click to toggle edit mode."""
        # Toggle state
        self._pages_edit_mode_active = not self._pages_edit_mode_active
        
        # Update button appearance and text
        if self._pages_edit_mode_active:
            self._edit_pages_button.setText("🛑  Stop Editing")
            self._edit_pages_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFF3CD;
                    border: 2px solid #FFC107;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 600;
                    color: #856404;
                }
                QPushButton:hover {
                    background-color: #FFE69C;
                    border-color: #FFB300;
                }
                QPushButton:pressed {
                    background-color: #FFD54F;
                }
            """)
        else:
            self._edit_pages_button.setText("✂️  Edit Pages")
            self._edit_pages_button.setStyleSheet(self._get_default_button_style())
        
        # Emit signal with new state
        self.edit_pages_toggled.emit(self._pages_edit_mode_active)
    
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
        button.setStyleSheet(self._get_default_button_style())
        return button
    
    def _create_toggle_button(self, text: str, icon_text: str) -> QPushButton:
        """
        Create a styled toggle button for Edit Pages.
        
        Args:
            text: Button label text
            icon_text: Icon or emoji to display
            
        Returns:
            Styled QPushButton that changes appearance when toggled
        """
        button = QPushButton(f"{icon_text}  {text}")
        button.setMinimumHeight(40)  # Slightly taller for prominence
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(self._get_default_button_style())
        return button
    
    def _get_default_button_style(self) -> str:
        """
        Get default button stylesheet.
        
        Returns:
            CSS stylesheet string
        """
        return """
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
        """
    
    def set_tools_enabled(self, enabled: bool) -> None:
        """
        Enable or disable content tools.
        Does not affect undo/redo or edit pages toggle.
        
        Args:
            enabled: True to enable tools, False to disable
        """
        # Enable/disable all buttons except undo/redo and edit pages
        for button in self.findChildren(QPushButton):
            if button not in (self._undo_button, self._redo_button, self._edit_pages_button):
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
    
    def is_pages_edit_mode_active(self) -> bool:
        """
        Check if page editing mode is currently active.
        
        Returns:
            True if in page edit mode, False otherwise
        """
        return self._pages_edit_mode_active
    
    def exit_pages_edit_mode(self) -> None:
        """
        Programmatically exit page editing mode.
        Updates button state without emitting signal.
        """
        if self._pages_edit_mode_active:
            self._pages_edit_mode_active = False
            self._edit_pages_button.setText("✂️  Edit Pages")
            self._edit_pages_button.setStyleSheet(self._get_default_button_style())
    
    def get_shape_toolbar(self) -> ShapeDrawingToolbar:
        """
        Get the shape drawing toolbar instance.
        
        Returns:
            ShapeDrawingToolbar instance
        """
        return self._shape_toolbar
