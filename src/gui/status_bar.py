"""
Status bar component.

Displays page information, zoom controls, and application status.
"""

from PySide6.QtWidgets import (
    QStatusBar, QLabel, QWidget, QHBoxLayout, 
    QSlider, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.constants import Fonts, Spacing, WindowDefaults


class StatusBar(QStatusBar):
    """
    Application status bar.
    
    Displays document information and provides zoom controls.
    Organized in three sections: left (page info), center (zoom), right (status).
    """
    
    # Signals
    zoom_changed = Signal(float)  # Emitted when zoom level changes
    page_changed = Signal(int)    # Emitted when user requests page change
    
    def __init__(self, parent=None):
        """
        Initialize status bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setFixedHeight(WindowDefaults.STATUS_BAR_HEIGHT)
        
        self._current_page = 0
        self._total_pages = 0
        self._zoom_level = 100.0
        
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
    
    def _create_widgets(self):
        """Create all status bar widgets."""
        # Left section: Page information
        self.page_label = QLabel("No document")
        self.page_label.setMinimumWidth(120)
        
        # Center section: Zoom controls
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(24, 24)
        self.zoom_out_btn.setToolTip("Zoom out")
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.setToolTip("Adjust zoom level")
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(24, 24)
        self.zoom_in_btn.setToolTip("Zoom in")
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems([
            "50%", "75%", "100%", "125%", "150%", "200%",
            "Fit Page", "Fit Width"
        ])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setFixedWidth(100)
        self.zoom_combo.setToolTip("Select zoom level")
        
        # Right section: File info and status
        self.file_size_label = QLabel("")
        self.file_size_label.setMinimumWidth(80)
        
        self.modified_label = QLabel("")
        self.modified_label.setMinimumWidth(80)
        
        self.status_message = QLabel("Ready")
        self.status_message.setMinimumWidth(100)
    
    def _setup_layout(self):
        """Set up status bar layout."""
        # Left widget
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(Spacing.SMALL, 0, Spacing.SMALL, 0)
        left_layout.setSpacing(Spacing.SMALL)
        left_layout.addWidget(self.page_label)
        left_layout.addStretch()
        
        # Center widget
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(Spacing.SMALL, 0, Spacing.SMALL, 0)
        center_layout.setSpacing(Spacing.SMALL)
        center_layout.addWidget(self.zoom_out_btn)
        center_layout.addWidget(self.zoom_slider)
        center_layout.addWidget(self.zoom_in_btn)
        center_layout.addWidget(self.zoom_combo)
        
        # Right widget
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(Spacing.SMALL, 0, Spacing.SMALL, 0)
        right_layout.setSpacing(Spacing.MEDIUM)
        right_layout.addWidget(self.file_size_label)
        right_layout.addWidget(self.modified_label)
        right_layout.addWidget(self.status_message)
        
        # Add to status bar
        self.addWidget(left_widget, 1)
        self.addPermanentWidget(center_widget)
        self.addPermanentWidget(right_widget)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.zoom_slider.valueChanged.connect(self._on_slider_changed)
        self.zoom_combo.currentTextChanged.connect(self._on_combo_changed)
        self.page_label.mousePressEvent = self._on_page_label_clicked
    
    def _zoom_out(self):
        """Decrease zoom level."""
        new_value = max(50, self.zoom_slider.value() - 25)
        self.zoom_slider.setValue(new_value)
    
    def _zoom_in(self):
        """Increase zoom level."""
        new_value = min(200, self.zoom_slider.value() + 25)
        self.zoom_slider.setValue(new_value)
    
    def _on_slider_changed(self, value: int):
        """
        Handle zoom slider change.
        
        Args:
            value: New slider value
        """
        self._zoom_level = float(value)
        self.zoom_combo.setCurrentText(f"{value}%")
        self.zoom_changed.emit(self._zoom_level)
    
    def _on_combo_changed(self, text: str):
        """
        Handle zoom combo box change.
        
        Args:
            text: Selected text
        """
        if text in ["Fit Page", "Fit Width"]:
            # Special zoom modes
            self.zoom_changed.emit(-1 if text == "Fit Page" else -2)
        else:
            # Percentage value
            try:
                value = int(text.rstrip('%'))
                self.zoom_slider.setValue(value)
            except ValueError:
                pass
    
    def _on_page_label_clicked(self, event):
        """
        Handle page label click to show go-to-page dialog.
        
        Args:
            event: Mouse event
        """
        # TODO Phase 2: Show go-to-page dialog
        self.show_message("Go to page dialog (Phase 2)", 2000)
    
    def set_page_info(self, current: int, total: int):
        """
        Update page information display.
        
        Args:
            current: Current page number (1-indexed)
            total: Total number of pages
        """
        self._current_page = current
        self._total_pages = total
        
        if total > 0:
            self.page_label.setText(f"Page {current} of {total}")
        else:
            self.page_label.setText("No document")
    
    def set_zoom_level(self, zoom: float):
        """
        Set zoom level.
        
        Args:
            zoom: Zoom level as percentage
        """
        self._zoom_level = zoom
        int_zoom = int(zoom)
        
        # Update slider if within range
        if 50 <= int_zoom <= 200:
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(int_zoom)
            self.zoom_slider.blockSignals(False)
            self.zoom_combo.setCurrentText(f"{int_zoom}%")
    
    def set_file_size(self, size_bytes: int):
        """
        Display file size.
        
        Args:
            size_bytes: File size in bytes
        """
        if size_bytes == 0:
            self.file_size_label.setText("")
            return
        
        # Format size nicely
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        
        self.file_size_label.setText(size_str)
    
    def set_modified(self, modified: bool):
        """
        Set modification status.
        
        Args:
            modified: Whether document has unsaved changes
        """
        if modified:
            self.modified_label.setText("Modified")
        else:
            self.modified_label.setText("Saved")
    
    def set_secure(self, secure: bool):
        """
        Set security indicator.
        
        Args:
            secure: Whether document is password protected
        """
        # Could add a lock icon indicator
        pass
    
    def show_message(self, message: str, timeout: int = 0):
        """
        Display a temporary status message.
        
        Args:
            message: Message to display
            timeout: Duration in milliseconds (0 = permanent)
        """
        self.status_message.setText(message)
        
        if timeout > 0:
            # Use QTimer to clear message after timeout
            from PySide6.QtCore import QTimer
            QTimer.singleShot(timeout, lambda: self.status_message.setText("Ready"))
    
    def clear_document_info(self):
        """Clear all document-related information."""
        self.set_page_info(0, 0)
        self.set_file_size(0)
        self.modified_label.setText("")
        self.status_message.setText("Ready")
