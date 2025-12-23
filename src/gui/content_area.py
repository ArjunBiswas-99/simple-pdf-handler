"""
Content area component.

Displays PDF document content or placeholder when no document is open.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.constants import Fonts, Spacing, Icons


class ContentArea(QWidget):
    """
    Main content display area.
    
    Shows PDF document content or a placeholder message when no document is open.
    In Phase 1, displays a placeholder. Phase 2 will add actual PDF rendering.
    """
    
    def __init__(self, parent=None):
        """
        Initialize content area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create scroll area for future PDF content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Create placeholder widget
        self.placeholder = self._create_placeholder()
        self.scroll_area.setWidget(self.placeholder)
        
        layout.addWidget(self.scroll_area)
    
    def _create_placeholder(self) -> QWidget:
        """
        Create placeholder widget shown when no document is open.
        
        Returns:
            Placeholder widget
        """
        placeholder = QWidget()
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        placeholder_layout.setSpacing(Spacing.LARGE)
        
        # Icon
        icon_label = QLabel(Icons.PAGES)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel("No document open")
        message_font = QFont()
        message_font.setPointSize(Fonts.SIZE_H2)
        message_font.setWeight(QFont.Weight.DemiBold)
        message_label.setFont(message_font)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setProperty("secondary", True)
        placeholder_layout.addWidget(message_label)
        
        # Hint
        hint_label = QLabel("Open a PDF file to get started")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setProperty("secondary", True)
        placeholder_layout.addWidget(hint_label)
        
        return placeholder
    
    def set_document(self, document_path: str):
        """
        Set the document to display.
        
        Args:
            document_path: Path to PDF document
        
        Note:
            Phase 1: Creates placeholder for document rendering
            Phase 2: Will implement actual PDF rendering
        """
        # TODO Phase 2: Implement actual PDF rendering
        # For now, just show a message that document would be displayed
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel(f"PDF Document:\n{document_path}\n\nRendering will be implemented in Phase 2")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.scroll_area.setWidget(placeholder)
    
    def clear_document(self):
        """Clear the document and show placeholder."""
        self.scroll_area.setWidget(self.placeholder)
