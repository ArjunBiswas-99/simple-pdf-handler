"""
OCR Detection Banner - Smart banner for scanned document detection.

Automatically appears when a scanned PDF is opened, offering quick OCR options.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from utils.constants import Colors, Fonts, Spacing, Shadows
from utils.icon_manager import get_icon


class OCRDetectionBanner(QFrame):
    """
    Smart banner that appears when scanned document is detected.
    
    Provides quick access to OCR functionality with minimal user friction.
    """
    
    # Signals
    quick_ocr_requested = Signal()
    advanced_ocr_requested = Signal()
    dismissed = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize OCR detection banner.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Set up banner user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.MEDIUM, Spacing.SMALL, Spacing.MEDIUM, Spacing.SMALL)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(get_icon('file_text', 32).pixmap(32, 32))
        layout.addWidget(icon_label)
        
        # Message
        message_layout = QHBoxLayout()
        message_layout.setSpacing(Spacing.MICRO)
        
        title_label = QLabel("📄 This appears to be a scanned document")
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_H4)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Make it searchable and editable with OCR")
        subtitle_font = QFont()
        subtitle_font.setPointSize(Fonts.SIZE_SMALL)
        
        message_widget = QWidget()
        message_vlayout = QHBoxLayout(message_widget)
        message_vlayout.setContentsMargins(0, 0, 0, 0)
        message_vlayout.setSpacing(Spacing.SMALL)
        message_vlayout.addWidget(title_label)
        message_vlayout.addWidget(QLabel("•"))
        message_vlayout.addWidget(subtitle_label)
        message_vlayout.addStretch()
        
        layout.addWidget(message_widget, 1)
        
        # Quick OCR button
        self.quick_btn = QPushButton("Quick OCR")
        self.quick_btn.setIcon(get_icon('search', 20))
        self.quick_btn.clicked.connect(self.quick_ocr_requested.emit)
        self.quick_btn.setMinimumWidth(120)
        layout.addWidget(self.quick_btn)
        
        # Advanced button
        self.advanced_btn = QPushButton("Advanced Options...")
        self.advanced_btn.setIcon(get_icon('settings', 20))
        self.advanced_btn.clicked.connect(self.advanced_ocr_requested.emit)
        self.advanced_btn.setMinimumWidth(160)
        layout.addWidget(self.advanced_btn)
        
        # Dismiss button
        self.dismiss_btn = QPushButton("✕")
        self.dismiss_btn.setFixedSize(32, 32)
        self.dismiss_btn.clicked.connect(self._on_dismiss)
        self.dismiss_btn.setToolTip("Dismiss banner")
        layout.addWidget(self.dismiss_btn)
    
    def _apply_styling(self):
        """Apply visual styling to banner."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            OCRDetectionBanner {{
                background-color: #FFF4CE;
                border: 1px solid #FFD700;
                border-radius: 4px;
                padding: {Spacing.SMALL}px;
            }}
            QPushButton {{
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: {Fonts.SIZE_NORMAL}pt;
            }}
            QPushButton:hover {{
                background-color: #F0F0F0;
                border-color: #0078D4;
            }}
            QPushButton:pressed {{
                background-color: #E0E0E0;
            }}
            QPushButton#quick_btn {{
                background-color: #0078D4;
                color: white;
                border: none;
                font-weight: {Fonts.WEIGHT_SEMIBOLD};
            }}
            QPushButton#quick_btn:hover {{
                background-color: #106EBE;
            }}
        """)
        
        self.quick_btn.setObjectName("quick_btn")
    
    def _on_dismiss(self):
        """Handle dismiss button click."""
        self.dismissed.emit()
        self.hide()
    
    def show_banner(self):
        """Show the banner with animation."""
        self.show()
        self.setMaximumHeight(60)
    
    def hide_banner(self):
        """Hide the banner."""
        self.hide()
