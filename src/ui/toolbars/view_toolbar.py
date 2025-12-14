"""
Simple PDF Handler - View Mode Toolbar

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
    QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QFrame, QMenu, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
from ui.styles.design_tokens import SIZING, SPACING, get_color
from ui.styles.theme_manager import get_theme_manager
from utils.constants import ZOOM_LEVELS, ZOOM_LEVEL_LABELS


class ViewToolbar(QWidget):
    """
    View mode toolbar with file operations, navigation, and zoom controls.
    Provides all functionality needed for viewing PDF documents.
    """
    
    # File operation signals
    open_file = pyqtSignal()
    save_file = pyqtSignal()
    save_file_as = pyqtSignal()
    print_file = pyqtSignal()
    
    # Navigation signals
    first_page = pyqtSignal()
    previous_page = pyqtSignal()
    next_page = pyqtSignal()
    last_page = pyqtSignal()
    page_changed = pyqtSignal(int)  # page number (1-indexed for display)
    
    # Zoom signals
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()
    zoom_changed = pyqtSignal(str)  # zoom text like "100%"
    fit_width = pyqtSignal()
    fit_page = pyqtSignal()
    
    # Layout signals
    single_page = pyqtSignal()
    continuous_page = pyqtSignal()
    facing_page = pyqtSignal()
    
    # Rotate signals
    rotate_left = pyqtSignal()
    rotate_right = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the View Toolbar."""
        super().__init__(parent)
        
        # Track responsive state
        self._overflow_active = False
        self._scroll_active = False
        
        self._setup_ui()
        self._apply_theme()
        
        # Connect to theme manager for updates
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self) -> None:
        """Set up the toolbar UI components."""
        # Set fixed height
        self.setFixedHeight(SIZING['toolbar_height'])
        
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(SPACING['md'], SPACING['sm'], SPACING['md'], SPACING['sm'])
        layout.setSpacing(SPACING['sm'])
        self.setLayout(layout)
        
        # File operations group
        self._create_file_group(layout)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # Navigation group
        self._create_navigation_group(layout)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # Zoom group
        self._create_zoom_group(layout)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # Layout group
        self._create_layout_group(layout)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # Rotate group
        self._create_rotate_group(layout)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        # Create overflow menu (initially hidden)
        self._create_overflow_menu(layout)
        
        # Apply size policies to buttons for better responsiveness
        self._apply_button_size_policies()
    
    def _create_overflow_menu(self, layout: QHBoxLayout) -> None:
        """Create overflow menu for less critical actions."""
        self._overflow_btn = QPushButton("⋯ More")
        self._overflow_btn.setToolTip("More options")
        self._overflow_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._overflow_btn.hide()  # Initially hidden
        
        # Create menu
        menu = QMenu(self)
        
        # Add file operations
        menu.addAction("Save", self.save_file.emit)
        menu.addAction("Save As...", self.save_file_as.emit)
        menu.addAction("Print", self.print_file.emit)
        menu.addSeparator()
        
        # Add navigation
        menu.addAction("First Page", self.first_page.emit)
        menu.addAction("Last Page", self.last_page.emit)
        menu.addSeparator()
        
        # Add layout modes
        menu.addAction("Single Page", self.single_page.emit)
        menu.addAction("Facing Pages", self.facing_page.emit)
        menu.addSeparator()
        
        # Add rotate
        menu.addAction("Rotate Left", self.rotate_left.emit)
        menu.addAction("Rotate Right", self.rotate_right.emit)
        
        self._overflow_btn.setMenu(menu)
        layout.addWidget(self._overflow_btn)
    
    def _apply_button_size_policies(self) -> None:
        """Apply size policies to buttons for responsive behavior."""
        # Buttons that can shrink
        shrinkable_buttons = [
            self._open_btn, self._save_btn, self._save_as_btn, self._print_btn,
            self._first_page_btn, self._prev_page_btn, self._next_page_btn, self._last_page_btn,
            self._fit_page_btn, self._fit_width_btn, self._zoom_out_btn, self._zoom_in_btn,
            self._single_page_btn, self._continuous_page_btn, self._facing_page_btn,
            self._rotate_left_btn, self._rotate_right_btn
        ]
        
        for button in shrinkable_buttons:
            button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            button.setMinimumWidth(40)  # Don't shrink below 40px
    
    def resizeEvent(self, event) -> None:
        """
        Handle resize events to adapt toolbar layout.
        
        Args:
            event: Resize event
        """
        # Call parent first to ensure proper resize handling
        super().resizeEvent(event)
        
        # Get toolbar width
        width = self.width()
        
        # Determine responsive tier
        if width < 800:
            # Tier 3: Narrow - Show overflow + enable horizontal scroll hint
            self._activate_overflow_mode()
            self._scroll_active = True
        elif width < 1200:
            # Tier 2: Medium - Show overflow menu
            self._activate_overflow_mode()
            self._scroll_active = False
        else:
            # Tier 1: Wide - Show all buttons
            self._deactivate_overflow_mode()
            self._scroll_active = False
        
        # Force layout update after responsive changes
        self.layout().update()
        self.updateGeometry()
    
    def _activate_overflow_mode(self) -> None:
        """Activate overflow menu mode - hide less critical buttons."""
        if self._overflow_active:
            return
        
        self._overflow_active = True
        
        # Hide less critical buttons
        self._save_btn.hide()
        self._save_as_btn.hide()
        self._print_btn.hide()
        self._first_page_btn.hide()
        self._last_page_btn.hide()
        self._single_page_btn.hide()
        self._facing_page_btn.hide()
        self._rotate_left_btn.hide()
        self._rotate_right_btn.hide()
        
        # Show overflow button
        self._overflow_btn.show()
    
    def _deactivate_overflow_mode(self) -> None:
        """Deactivate overflow mode - show all buttons."""
        if not self._overflow_active:
            return
        
        self._overflow_active = False
        
        # List of buttons to restore
        buttons_to_restore = [
            self._save_btn, self._save_as_btn, self._print_btn,
            self._first_page_btn, self._last_page_btn,
            self._single_page_btn, self._facing_page_btn,
            self._rotate_left_btn, self._rotate_right_btn
        ]
        
        # Show all buttons and force size recalculation
        for button in buttons_to_restore:
            button.show()
            button.adjustSize()  # Force size recalculation
        
        # Hide overflow button
        self._overflow_btn.hide()
        
        # Force immediate layout update
        self.layout().activate()
    
    def _create_file_group(self, layout: QHBoxLayout) -> None:
        """Create file operations buttons."""
        # Open button
        self._open_btn = QPushButton("📂 Open")
        self._open_btn.setToolTip("Open PDF file (Ctrl+O)")
        self._open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_btn.clicked.connect(self.open_file.emit)
        layout.addWidget(self._open_btn)
        
        # Save button (grayed out)
        self._save_btn = QPushButton("💾 Save")
        self._save_btn.setToolTip("Save document (Coming soon)")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self.save_file.emit)
        layout.addWidget(self._save_btn)
        
        # Save As button (grayed out)
        self._save_as_btn = QPushButton("💾 Save As▼")
        self._save_as_btn.setToolTip("Save document as (Coming soon)")
        self._save_as_btn.setEnabled(False)
        self._save_as_btn.clicked.connect(self.save_file_as.emit)
        layout.addWidget(self._save_as_btn)
        
        # Print button (grayed out)
        self._print_btn = QPushButton("🖨️ Print")
        self._print_btn.setToolTip("Print document (Coming soon)")
        self._print_btn.setEnabled(False)
        self._print_btn.clicked.connect(self.print_file.emit)
        layout.addWidget(self._print_btn)
    
    def _create_navigation_group(self, layout: QHBoxLayout) -> None:
        """Create navigation controls."""
        # First page button - clean icon
        self._first_page_btn = QPushButton("⟪")
        self._first_page_btn.setToolTip("Go to first page (Home)")
        self._first_page_btn.setEnabled(False)
        self._first_page_btn.setFixedWidth(40)
        self._first_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._first_page_btn.clicked.connect(self.first_page.emit)
        layout.addWidget(self._first_page_btn)
        
        # Previous page button - clean icon
        self._prev_page_btn = QPushButton("◀")
        self._prev_page_btn.setToolTip("Previous page (←)")
        self._prev_page_btn.setEnabled(False)
        self._prev_page_btn.setFixedWidth(40)
        self._prev_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_page_btn.clicked.connect(self.previous_page.emit)
        layout.addWidget(self._prev_page_btn)
        
        # Page number input
        self._page_input = QLineEdit()
        self._page_input.setFixedWidth(50)
        self._page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_input.setPlaceholderText("1")
        self._page_input.setEnabled(False)
        self._page_input.returnPressed.connect(self._on_page_input_changed)
        layout.addWidget(self._page_input)
        
        # Page count label
        self._page_count_label = QLabel("/ 0")
        self._page_count_label.setStyleSheet("color: #646464; padding: 0 4px;")
        layout.addWidget(self._page_count_label)
        
        # Next page button - clean icon
        self._next_page_btn = QPushButton("▶")
        self._next_page_btn.setToolTip("Next page (→)")
        self._next_page_btn.setEnabled(False)
        self._next_page_btn.setFixedWidth(40)
        self._next_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_page_btn.clicked.connect(self.next_page.emit)
        layout.addWidget(self._next_page_btn)
        
        # Last page button - clean icon
        self._last_page_btn = QPushButton("⟫")
        self._last_page_btn.setToolTip("Go to last page (End)")
        self._last_page_btn.setEnabled(False)
        self._last_page_btn.setFixedWidth(40)
        self._last_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._last_page_btn.clicked.connect(self.last_page.emit)
        layout.addWidget(self._last_page_btn)
    
    def _create_zoom_group(self, layout: QHBoxLayout) -> None:
        """Create zoom controls."""
        # Fit Page button - icon symbol
        self._fit_page_btn = QPushButton("⬜")
        self._fit_page_btn.setToolTip("Fit entire page to window")
        self._fit_page_btn.setEnabled(False)
        self._fit_page_btn.setFixedWidth(40)
        self._fit_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fit_page_btn.clicked.connect(self.fit_page.emit)
        layout.addWidget(self._fit_page_btn)
        
        # Fit Width button - icon symbol
        self._fit_width_btn = QPushButton("↔")
        self._fit_width_btn.setToolTip("Fit page width to window")
        self._fit_width_btn.setEnabled(False)
        self._fit_width_btn.setFixedWidth(40)
        self._fit_width_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fit_width_btn.clicked.connect(self.fit_width.emit)
        layout.addWidget(self._fit_width_btn)
        
        # Zoom out button - icon symbol
        self._zoom_out_btn = QPushButton("−")
        self._zoom_out_btn.setToolTip("Decrease zoom level")
        self._zoom_out_btn.setEnabled(False)
        self._zoom_out_btn.setFixedWidth(40)
        self._zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._zoom_out_btn.clicked.connect(self.zoom_out.emit)
        layout.addWidget(self._zoom_out_btn)
        
        # Zoom level dropdown
        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(ZOOM_LEVEL_LABELS)
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.setEnabled(False)
        self._zoom_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._zoom_combo.setMinimumWidth(80)
        self._zoom_combo.setMaximumWidth(100)
        self._zoom_combo.currentTextChanged.connect(self.zoom_changed.emit)
        layout.addWidget(self._zoom_combo)
        
        # Zoom in button - icon symbol
        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setToolTip("Increase zoom level")
        self._zoom_in_btn.setEnabled(False)
        self._zoom_in_btn.setFixedWidth(40)
        self._zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._zoom_in_btn.clicked.connect(self.zoom_in.emit)
        layout.addWidget(self._zoom_in_btn)
    
    def _create_layout_group(self, layout: QHBoxLayout) -> None:
        """Create layout mode buttons."""
        # Single page button (grayed out)
        self._single_page_btn = QPushButton("Single")
        self._single_page_btn.setToolTip("Single page view (Coming soon)")
        self._single_page_btn.setEnabled(False)
        self._single_page_btn.clicked.connect(self.single_page.emit)
        layout.addWidget(self._single_page_btn)
        
        # Continuous page button (active)
        self._continuous_page_btn = QPushButton("Continuous")
        self._continuous_page_btn.setToolTip("Continuous scrolling view (Active)")
        self._continuous_page_btn.setCheckable(True)
        self._continuous_page_btn.setChecked(True)
        self._continuous_page_btn.clicked.connect(self.continuous_page.emit)
        layout.addWidget(self._continuous_page_btn)
        
        # Facing page button (grayed out)
        self._facing_page_btn = QPushButton("Facing")
        self._facing_page_btn.setToolTip("Facing pages view (Coming soon)")
        self._facing_page_btn.setEnabled(False)
        self._facing_page_btn.clicked.connect(self.facing_page.emit)
        layout.addWidget(self._facing_page_btn)
    
    def _create_rotate_group(self, layout: QHBoxLayout) -> None:
        """Create page rotation buttons."""
        # Rotate left button - icon symbol
        self._rotate_left_btn = QPushButton("↶")
        self._rotate_left_btn.setToolTip("Rotate page counterclockwise (Coming soon)")
        self._rotate_left_btn.setEnabled(False)
        self._rotate_left_btn.setFixedWidth(40)
        self._rotate_left_btn.clicked.connect(self.rotate_left.emit)
        layout.addWidget(self._rotate_left_btn)
        
        # Rotate right button - icon symbol
        self._rotate_right_btn = QPushButton("↷")
        self._rotate_right_btn.setToolTip("Rotate page clockwise (Coming soon)")
        self._rotate_right_btn.setEnabled(False)
        self._rotate_right_btn.setFixedWidth(40)
        self._rotate_right_btn.clicked.connect(self.rotate_right.emit)
        layout.addWidget(self._rotate_right_btn)
    
    def _create_separator(self) -> QFrame:
        """Create a vertical separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    
    def _on_page_input_changed(self) -> None:
        """Handle manual page number input."""
        try:
            page_num = int(self._page_input.text())
            self.page_changed.emit(page_num)
        except ValueError:
            pass  # Invalid input, ignore
    
    def _apply_theme(self) -> None:
        """Apply theme-aware styling to the toolbar."""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        
        # Get theme colors
        bg_color = get_color('surface', is_dark)
        border_color = get_color('divider', is_dark)
        
        # Toolbar background
        self.setStyleSheet(f"""
            ViewToolbar {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
        """)
    
    # Public methods for updating toolbar state
    
    def set_page_info(self, current_page: int, total_pages: int) -> None:
        """
        Update page number display.
        
        Args:
            current_page: Current page number (0-indexed internally, displayed as 1-indexed)
            total_pages: Total number of pages
        """
        self._page_input.setText(str(current_page + 1))
        self._page_count_label.setText(f"/ {total_pages}")
    
    def set_navigation_enabled(self, enabled: bool) -> None:
        """Enable or disable navigation controls."""
        self._page_input.setEnabled(enabled)
    
    def set_navigation_buttons_state(self, can_go_prev: bool, can_go_next: bool) -> None:
        """
        Update navigation button enabled state.
        
        Args:
            can_go_prev: Whether previous/first buttons should be enabled
            can_go_next: Whether next/last buttons should be enabled
        """
        self._first_page_btn.setEnabled(can_go_prev)
        self._prev_page_btn.setEnabled(can_go_prev)
        self._next_page_btn.setEnabled(can_go_next)
        self._last_page_btn.setEnabled(can_go_next)
    
    def set_zoom_level(self, zoom_text: str) -> None:
        """
        Update zoom level display.
        
        Args:
            zoom_text: Zoom level text (e.g., "100%")
        """
        # Block signals to prevent triggering zoom_changed
        self._zoom_combo.blockSignals(True)
        self._zoom_combo.setCurrentText(zoom_text)
        self._zoom_combo.blockSignals(False)
    
    def set_zoom_enabled(self, enabled: bool) -> None:
        """Enable or disable zoom controls."""
        self._zoom_in_btn.setEnabled(enabled)
        self._zoom_out_btn.setEnabled(enabled)
        self._zoom_combo.setEnabled(enabled)
        self._fit_width_btn.setEnabled(enabled)
        self._fit_page_btn.setEnabled(enabled)
