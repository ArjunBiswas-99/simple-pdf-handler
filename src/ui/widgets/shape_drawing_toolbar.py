"""
Simple PDF Handler - Shape Drawing Toolbar

Provides controls for drawing shapes (rectangle, circle, line) on PDF pages.
Users can configure border color, width, fill color, and drawing mode.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter


class ShapeDrawingToolbar(QWidget):
    """
    Toolbar for configuring and activating shape drawing mode.
    
    Provides controls for:
    - Shape type selection (rectangle, circle, line)
    - Border color and width configuration
    - Fill color configuration (for closed shapes)
    - Drawing mode activation
    """
    
    # Signals
    drawing_started = pyqtSignal(str, dict)  # (shape_type, properties)
    
    def __init__(self, parent=None):
        """Initialize the shape drawing toolbar."""
        super().__init__(parent)
        
        # Current drawing properties
        self._shape_type = 'rectangle'
        self._border_color = QColor(255, 0, 0)  # Red
        self._border_width = 2
        self._fill_enabled = False
        self._fill_color = QColor(0, 0, 255, 100)  # Semi-transparent blue
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the toolbar layout and widgets."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Set white background for the widget
        self.setStyleSheet("QWidget { background-color: white; }")
        
        # Section label
        label = QLabel("🔲 DRAW SHAPES")
        label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #666666;
                letter-spacing: 0.5px;
                padding: 4px 0px;
                background-color: transparent;
            }
        """)
        layout.addWidget(label)
        
        # Shape type selector
        layout.addWidget(self._create_shape_selector())
        
        # Border properties
        layout.addWidget(self._create_border_section())
        
        # Fill properties
        layout.addWidget(self._create_fill_section())
        
        # Start drawing button
        self._start_btn = QPushButton("🎨  Start Drawing")
        self._start_btn.setMinimumHeight(40)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start_drawing)
        self._start_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        layout.addWidget(self._start_btn)
        
        # Add stretch
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _create_shape_selector(self) -> QWidget:
        """
        Create shape type selector buttons.
        
        Returns:
            Widget containing shape selector buttons
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel("Shape Type:")
        label.setStyleSheet("color: #333; font-size: 12px;")
        layout.addWidget(label)
        
        # Button group for shapes
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Rectangle button
        self._rect_btn = self._create_shape_button("□", "Rectangle")
        self._rect_btn.setChecked(True)
        self._rect_btn.clicked.connect(lambda: self._on_shape_selected('rectangle'))
        button_layout.addWidget(self._rect_btn)
        
        # Circle button
        self._circle_btn = self._create_shape_button("○", "Circle")
        self._circle_btn.clicked.connect(lambda: self._on_shape_selected('circle'))
        button_layout.addWidget(self._circle_btn)
        
        # Line button
        self._line_btn = self._create_shape_button("─", "Line")
        self._line_btn.clicked.connect(lambda: self._on_shape_selected('line'))
        button_layout.addWidget(self._line_btn)
        
        layout.addLayout(button_layout)
        container.setLayout(layout)
        return container
    
    def _create_shape_button(self, icon_text: str, tooltip: str) -> QPushButton:
        """
        Create a shape selector button.
        
        Args:
            icon_text: Text/symbol to display on button
            tooltip: Tooltip text
            
        Returns:
            Configured QPushButton
        """
        button = QPushButton(icon_text)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setMinimumSize(60, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #DDDDDD;
                border-radius: 6px;
                font-size: 20px;
                color: #333;
            }
            QPushButton:hover {
                border-color: #0078D4;
                background-color: #F5F5F5;
            }
            QPushButton:checked {
                background-color: #E3F2FD;
                border-color: #0078D4;
                color: #0078D4;
            }
        """)
        return button
    
    def _create_border_section(self) -> QWidget:
        """
        Create border properties section.
        
        Returns:
            Widget containing border controls
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel("Border:")
        label.setStyleSheet("color: #333; font-size: 12px;")
        layout.addWidget(label)
        
        # Color and width row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Color button
        self._border_color_btn = self._create_color_button(self._border_color)
        self._border_color_btn.clicked.connect(self._on_select_border_color)
        controls_layout.addWidget(self._border_color_btn)
        
        # Width combo
        self._border_width_combo = QComboBox()
        self._border_width_combo.addItems(['1px', '2px', '3px', '4px', '5px', '6px', '8px', '10px'])
        self._border_width_combo.setCurrentText('2px')
        self._border_width_combo.currentTextChanged.connect(self._on_border_width_changed)
        self._border_width_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background: white;
            }
        """)
        controls_layout.addWidget(self._border_width_combo)
        
        layout.addLayout(controls_layout)
        container.setLayout(layout)
        return container
    
    def _create_fill_section(self) -> QWidget:
        """
        Create fill properties section.
        
        Returns:
            Widget containing fill controls
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Checkbox row
        checkbox_layout = QHBoxLayout()
        
        self._fill_checkbox = QCheckBox("Fill Shape")
        self._fill_checkbox.setStyleSheet("color: #333; font-size: 12px;")
        self._fill_checkbox.stateChanged.connect(self._on_fill_toggled)
        checkbox_layout.addWidget(self._fill_checkbox)
        checkbox_layout.addStretch()
        
        layout.addLayout(checkbox_layout)
        
        # Color button (initially disabled)
        self._fill_color_btn = self._create_color_button(self._fill_color)
        self._fill_color_btn.clicked.connect(self._on_select_fill_color)
        self._fill_color_btn.setEnabled(False)
        layout.addWidget(self._fill_color_btn)
        
        container.setLayout(layout)
        return container
    
    def _create_color_button(self, color: QColor) -> QPushButton:
        """
        Create a color picker button.
        
        Args:
            color: Initial color to display
            
        Returns:
            Configured color button
        """
        button = QPushButton()
        button.setMinimumHeight(32)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Create color icon
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())
        
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover {
                border-color: #0078D4;
            }
        """)
        
        return button
    
    def _on_shape_selected(self, shape_type: str) -> None:
        """
        Handle shape type selection.
        
        Args:
            shape_type: Selected shape type ('rectangle', 'circle', 'line')
        """
        self._shape_type = shape_type
        
        # Update button states
        self._rect_btn.setChecked(shape_type == 'rectangle')
        self._circle_btn.setChecked(shape_type == 'circle')
        self._line_btn.setChecked(shape_type == 'line')
        
        # Disable fill options for line
        if shape_type == 'line':
            self._fill_checkbox.setEnabled(False)
            self._fill_checkbox.setChecked(False)
            self._fill_color_btn.setEnabled(False)
        else:
            self._fill_checkbox.setEnabled(True)
    
    def _on_select_border_color(self) -> None:
        """Handle border color selection."""
        color = QColorDialog.getColor(self._border_color, self, "Select Border Color")
        if color.isValid():
            self._border_color = color
            # Update button icon
            pixmap = QPixmap(24, 24)
            pixmap.fill(color)
            self._border_color_btn.setIcon(QIcon(pixmap))
    
    def _on_border_width_changed(self, text: str) -> None:
        """
        Handle border width change.
        
        Args:
            text: Selected width text (e.g., '2px')
        """
        self._border_width = int(text.replace('px', ''))
    
    def _on_fill_toggled(self, state: int) -> None:
        """
        Handle fill checkbox toggle.
        
        Args:
            state: Checkbox state
        """
        self._fill_enabled = (state == Qt.CheckState.Checked.value)
        self._fill_color_btn.setEnabled(self._fill_enabled)
    
    def _on_select_fill_color(self) -> None:
        """Handle fill color selection."""
        color = QColorDialog.getColor(self._fill_color, self, "Select Fill Color",
                                      QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self._fill_color = color
            # Update button icon
            pixmap = QPixmap(24, 24)
            pixmap.fill(color)
            self._fill_color_btn.setIcon(QIcon(pixmap))
    
    def _on_start_drawing(self) -> None:
        """Handle start drawing button click."""
        # Gather all properties
        properties = {
            'border_color': self._border_color,
            'border_width': self._border_width,
            'fill_enabled': self._fill_enabled,
            'fill_color': self._fill_color if self._fill_enabled else None
        }
        
        # Emit signal with shape type and properties
        self.drawing_started.emit(self._shape_type, properties)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable all controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self._rect_btn.setEnabled(enabled)
        self._circle_btn.setEnabled(enabled)
        self._line_btn.setEnabled(enabled)
        self._border_color_btn.setEnabled(enabled)
        self._border_width_combo.setEnabled(enabled)
        self._fill_checkbox.setEnabled(enabled and self._shape_type != 'line')
        self._fill_color_btn.setEnabled(enabled and self._fill_enabled)
        self._start_btn.setEnabled(enabled)
