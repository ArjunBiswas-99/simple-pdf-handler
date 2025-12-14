"""
Simple PDF Handler - Right Properties Panel

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget,
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles.design_tokens import SPACING, SIZING, get_color
from ui.styles.theme_manager import get_theme_manager


class PropertyRow(QWidget):
    """A single property row with label and value."""
    
    def __init__(self, label: str, value: str = "", parent=None):
        super().__init__(parent)
        self._setup_ui(label, value)
    
    def _setup_ui(self, label: str, value: str):
        """Set up the property row UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, SPACING['sm'])
        layout.setSpacing(SPACING['xs'])
        self.setLayout(layout)
        
        # Label (small, secondary color)
        self._label = QLabel(label)
        self._label.setProperty("class", "property-label")
        layout.addWidget(self._label)
        
        # Value (normal, primary color)
        self._value = QLabel(value)
        self._value.setProperty("class", "property-value")
        self._value.setWordWrap(True)
        layout.addWidget(self._value)
    
    def set_value(self, value: str):
        """Update the property value."""
        self._value.setText(value)


class DocumentPropertiesPanel(QWidget):
    """Panel showing document metadata and properties."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        """Set up the document properties UI."""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        layout.setSpacing(SPACING['md'])
        self.setLayout(layout)
        
        # Title
        title = QLabel("Document Properties")
        title.setProperty("class", "panel-title")
        layout.addWidget(title)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Properties container
        props_widget = QWidget()
        props_layout = QVBoxLayout()
        props_layout.setContentsMargins(0, 0, 0, 0)
        props_layout.setSpacing(SPACING['sm'])
        props_widget.setLayout(props_layout)
        
        # Create property rows
        self._filename_row = PropertyRow("File Name")
        self._filesize_row = PropertyRow("File Size")
        self._pages_row = PropertyRow("Pages")
        self._created_row = PropertyRow("Created")
        self._modified_row = PropertyRow("Modified")
        self._title_row = PropertyRow("Title")
        self._author_row = PropertyRow("Author")
        self._subject_row = PropertyRow("Subject")
        
        props_layout.addWidget(self._filename_row)
        props_layout.addWidget(self._filesize_row)
        props_layout.addWidget(self._pages_row)
        props_layout.addWidget(self._separator())
        props_layout.addWidget(self._created_row)
        props_layout.addWidget(self._modified_row)
        props_layout.addWidget(self._separator())
        props_layout.addWidget(self._title_row)
        props_layout.addWidget(self._author_row)
        props_layout.addWidget(self._subject_row)
        props_layout.addStretch()
        
        scroll.setWidget(props_widget)
        layout.addWidget(scroll)
    
    def _separator(self) -> QFrame:
        """Create a horizontal separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line
    
    def update_properties(self, doc_info: dict):
        """
        Update displayed properties.
        
        Args:
            doc_info: Dictionary with keys: filename, filesize, pages, 
                     created, modified, title, author, subject
        """
        self._filename_row.set_value(doc_info.get('filename', 'N/A'))
        self._filesize_row.set_value(doc_info.get('filesize', 'N/A'))
        self._pages_row.set_value(doc_info.get('pages', 'N/A'))
        self._created_row.set_value(doc_info.get('created', 'N/A'))
        self._modified_row.set_value(doc_info.get('modified', 'N/A'))
        self._title_row.set_value(doc_info.get('title', 'N/A'))
        self._author_row.set_value(doc_info.get('author', 'N/A'))
        self._subject_row.set_value(doc_info.get('subject', 'N/A'))
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        text_primary = get_color('text_primary', is_dark)
        text_secondary = get_color('text_secondary', is_dark)
        
        self.setStyleSheet(f"""
            DocumentPropertiesPanel {{
                background-color: {bg_color};
            }}
            QLabel[class="panel-title"] {{
                font-size: 15px;
                font-weight: 600;
                color: {text_primary};
            }}
            QLabel[class="property-label"] {{
                font-size: 11px;
                color: {text_secondary};
                font-weight: 500;
            }}
            QLabel[class="property-value"] {{
                font-size: 13px;
                color: {text_primary};
            }}
        """)


class EmptyStatePanel(QWidget):
    """Panel shown when no document is open."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        """Set up the empty state UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(SPACING['lg'], SPACING['xxl'], SPACING['lg'], SPACING['xxl'])
        layout.setSpacing(SPACING['md'])
        self.setLayout(layout)
        
        layout.addStretch()
        
        # Icon
        icon = QLabel("📄")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon)
        
        # Message
        message = QLabel("No document open")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setProperty("class", "empty-message")
        layout.addWidget(message)
        
        # Hint
        hint = QLabel("Open a PDF to view properties")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setProperty("class", "empty-hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        
        layout.addStretch()
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        text_primary = get_color('text_primary', is_dark)
        text_secondary = get_color('text_secondary', is_dark)
        
        self.setStyleSheet(f"""
            EmptyStatePanel {{
                background-color: {bg_color};
            }}
            QLabel[class="empty-message"] {{
                font-size: 15px;
                font-weight: 500;
                color: {text_primary};
            }}
            QLabel[class="empty-hint"] {{
                font-size: 13px;
                color: {text_secondary};
            }}
        """)


class RightPanel(QWidget):
    """
    Right properties panel that shows contextual information.
    Collapsible with smooth animations.
    """
    
    # Signals
    toggled = pyqtSignal(bool)  # Emitted when panel is shown/hidden
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_visible = True
        self._setup_ui()
        self._apply_theme()
        
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        """Set up the right panel UI."""
        self.setFixedWidth(SIZING['right_panel_width'])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Stacked widget for different views
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)
        
        # Create views
        self._empty_panel = EmptyStatePanel()
        self._doc_props_panel = DocumentPropertiesPanel()
        
        # Add to stack
        self._stack.addWidget(self._empty_panel)
        self._stack.addWidget(self._doc_props_panel)
        
        # Start with empty state
        self._stack.setCurrentWidget(self._empty_panel)
    
    def show_empty_state(self):
        """Show the empty state (no document open)."""
        self._stack.setCurrentWidget(self._empty_panel)
    
    def show_document_properties(self, doc_info: dict):
        """
        Show document properties.
        
        Args:
            doc_info: Dictionary with document metadata
        """
        self._doc_props_panel.update_properties(doc_info)
        self._stack.setCurrentWidget(self._doc_props_panel)
    
    def toggle_visibility(self):
        """Toggle panel visibility."""
        self._is_visible = not self._is_visible
        if self._is_visible:
            self.show()
        else:
            self.hide()
        self.toggled.emit(self._is_visible)
    
    def is_visible_panel(self) -> bool:
        """Check if panel is currently visible."""
        return self._is_visible
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        bg_color = get_color('surface', is_dark)
        border_color = get_color('divider', is_dark)
        
        self.setStyleSheet(f"""
            RightPanel {{
                background-color: {bg_color};
                border-left: 1px solid {border_color};
            }}
        """)
