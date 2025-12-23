"""
Right sidebar component.

Provides formatting controls and document properties panels.
"""

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QComboBox, QPushButton, QFormLayout, QLineEdit,
    QSpinBox, QColorDialog, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from utils.constants import WindowDefaults, Icons, Spacing, Fonts


class RightSidebar(QDockWidget):
    """
    Right sidebar dock widget.
    
    Contains formatting controls and document properties.
    Initially disabled until a document is opened.
    """
    
    # Signals
    format_changed = Signal(dict)  # Emitted when format settings change
    properties_updated = Signal(dict)  # Emitted when properties are saved
    
    def __init__(self, parent=None):
        """
        Initialize right sidebar.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Properties", parent)
        
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable)
        
        self._current_color = QColor("#000000")
        
        self._create_content()
    
    def _create_content(self):
        """Create sidebar content with tabs."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self._create_format_tab()
        self._create_properties_tab()
        
        layout.addWidget(self.tabs)
        
        self.setWidget(container)
        self.setMinimumWidth(WindowDefaults.RIGHT_SIDEBAR_WIDTH)
    
    def _create_format_tab(self):
        """Create format panel for text formatting."""
        format_widget = QWidget()
        layout = QVBoxLayout(format_widget)
        layout.setSpacing(Spacing.MEDIUM)
        layout.setContentsMargins(Spacing.MEDIUM, Spacing.MEDIUM, Spacing.MEDIUM, Spacing.MEDIUM)
        
        # Font section
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Arial", "Times New Roman", "Courier New", "Helvetica",
            "Calibri", "Verdana", "Georgia", "Comic Sans MS"
        ])
        self.font_combo.currentTextChanged.connect(self._on_format_changed)
        font_layout.addRow("Family:", self.font_combo)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(12)
        self.size_spin.setSuffix(" pt")
        self.size_spin.valueChanged.connect(self._on_format_changed)
        font_layout.addRow("Size:", self.size_spin)
        
        layout.addWidget(font_group)
        
        # Color section
        color_group = QGroupBox("Color")
        color_layout = QVBoxLayout(color_group)
        
        color_button_layout = QHBoxLayout()
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 24)
        self.color_preview.setStyleSheet(f"background-color: {self._current_color.name()}; border: 1px solid #ccc;")
        color_button_layout.addWidget(self.color_preview)
        
        color_btn = QPushButton("Choose Color...")
        color_btn.clicked.connect(self._choose_color)
        color_button_layout.addWidget(color_btn)
        color_button_layout.addStretch()
        
        color_layout.addLayout(color_button_layout)
        layout.addWidget(color_group)
        
        # Style section
        style_group = QGroupBox("Style")
        style_layout = QVBoxLayout(style_group)
        
        self.bold_cb = QCheckBox("Bold")
        self.bold_cb.stateChanged.connect(self._on_format_changed)
        style_layout.addWidget(self.bold_cb)
        
        self.italic_cb = QCheckBox("Italic")
        self.italic_cb.stateChanged.connect(self._on_format_changed)
        style_layout.addWidget(self.italic_cb)
        
        self.underline_cb = QCheckBox("Underline")
        self.underline_cb.stateChanged.connect(self._on_format_changed)
        style_layout.addWidget(self.underline_cb)
        
        self.strikethrough_cb = QCheckBox("Strikethrough")
        self.strikethrough_cb.stateChanged.connect(self._on_format_changed)
        style_layout.addWidget(self.strikethrough_cb)
        
        layout.addWidget(style_group)
        
        # Alignment section
        align_group = QGroupBox("Alignment")
        align_layout = QVBoxLayout(align_group)
        
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Left", "Center", "Right", "Justify"])
        self.align_combo.currentTextChanged.connect(self._on_format_changed)
        align_layout.addWidget(self.align_combo)
        
        layout.addWidget(align_group)
        
        # Apply button
        apply_btn = QPushButton("Apply Formatting")
        apply_btn.clicked.connect(self._apply_format)
        layout.addWidget(apply_btn)
        
        # Note
        note = QLabel("Note: Text formatting will be available in Phase 2")
        note.setProperty("secondary", True)
        note.setWordWrap(True)
        layout.addWidget(note)
        
        layout.addStretch()
        
        self.tabs.addTab(format_widget, f"{Icons.FORMAT} Format")
    
    def _create_properties_tab(self):
        """Create properties panel for document metadata."""
        props_widget = QWidget()
        layout = QVBoxLayout(props_widget)
        layout.setSpacing(Spacing.MEDIUM)
        layout.setContentsMargins(Spacing.MEDIUM, Spacing.MEDIUM, Spacing.MEDIUM, Spacing.MEDIUM)
        
        # Metadata section
        metadata_group = QGroupBox("Document Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Document title")
        metadata_layout.addRow("Title:", self.title_input)
        
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Author name")
        metadata_layout.addRow("Author:", self.author_input)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")
        metadata_layout.addRow("Subject:", self.subject_input)
        
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Keywords (comma-separated)")
        metadata_layout.addRow("Keywords:", self.keywords_input)
        
        layout.addWidget(metadata_group)
        
        # Save metadata button
        save_metadata_btn = QPushButton("Save Metadata")
        save_metadata_btn.clicked.connect(self._save_metadata)
        layout.addWidget(save_metadata_btn)
        
        # Document info section
        info_group = QGroupBox("Document Information")
        info_layout = QVBoxLayout(info_group)
        
        self.pages_label = QLabel("Pages: -")
        info_layout.addWidget(self.pages_label)
        
        self.size_label = QLabel("Size: -")
        info_layout.addWidget(self.size_label)
        
        self.version_label = QLabel("PDF Version: -")
        info_layout.addWidget(self.version_label)
        
        self.created_label = QLabel("Created: -")
        info_layout.addWidget(self.created_label)
        
        self.modified_label = QLabel("Modified: -")
        info_layout.addWidget(self.modified_label)
        
        layout.addWidget(info_group)
        
        # Security section
        security_group = QGroupBox("Security")
        security_layout = QVBoxLayout(security_group)
        
        self.encrypted_label = QLabel("Encrypted: No")
        security_layout.addWidget(self.encrypted_label)
        
        self.permissions_label = QLabel("Permissions: Full access")
        self.permissions_label.setWordWrap(True)
        security_layout.addWidget(self.permissions_label)
        
        security_btn = QPushButton("Security Settings...")
        security_btn.clicked.connect(lambda: self._show_coming_soon("Security Settings"))
        security_layout.addWidget(security_btn)
        
        layout.addWidget(security_group)
        
        layout.addStretch()
        
        self.tabs.addTab(props_widget, f"{Icons.PROPERTIES} Properties")
    
    def _choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(
            self._current_color,
            self,
            "Choose Text Color"
        )
        
        if color.isValid():
            self._current_color = color
            self.color_preview.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #ccc;"
            )
            self._on_format_changed()
    
    def _on_format_changed(self):
        """Handle format setting changes."""
        # Collect current format settings
        format_data = {
            'font_family': self.font_combo.currentText(),
            'font_size': self.size_spin.value(),
            'color': self._current_color.name(),
            'bold': self.bold_cb.isChecked(),
            'italic': self.italic_cb.isChecked(),
            'underline': self.underline_cb.isChecked(),
            'strikethrough': self.strikethrough_cb.isChecked(),
            'alignment': self.align_combo.currentText()
        }
        
        # Emit signal
        self.format_changed.emit(format_data)
    
    def _apply_format(self):
        """Apply formatting to selected content."""
        # For Phase 1, show placeholder
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Apply Formatting",
            "Text formatting will be applied in Phase 2.\n\n"
            "This will format the selected text in the document."
        )
    
    def _save_metadata(self):
        """Save document metadata."""
        metadata = {
            'title': self.title_input.text(),
            'author': self.author_input.text(),
            'subject': self.subject_input.text(),
            'keywords': self.keywords_input.text()
        }
        
        # Emit signal
        self.properties_updated.emit(metadata)
        
        # For Phase 1, show placeholder
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Save Metadata",
            "Metadata will be saved to the PDF in Phase 2.\n\n"
            f"Title: {metadata['title']}\n"
            f"Author: {metadata['author']}\n"
            f"Subject: {metadata['subject']}\n"
            f"Keywords: {metadata['keywords']}"
        )
    
    def _show_coming_soon(self, feature: str):
        """
        Show coming soon message.
        
        Args:
            feature: Feature name
        """
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Coming Soon",
            f"{feature} will be available in Phase 2."
        )
    
    def load_document_properties(self, properties: dict):
        """
        Load document properties into the panel.
        
        Args:
            properties: Dictionary of document properties
        """
        # Load metadata
        self.title_input.setText(properties.get('title', ''))
        self.author_input.setText(properties.get('author', ''))
        self.subject_input.setText(properties.get('subject', ''))
        self.keywords_input.setText(properties.get('keywords', ''))
        
        # Load info
        if 'pages' in properties:
            self.pages_label.setText(f"Pages: {properties['pages']}")
        if 'size' in properties:
            self.size_label.setText(f"Size: {properties['size']}")
        if 'version' in properties:
            self.version_label.setText(f"PDF Version: {properties['version']}")
        if 'created' in properties:
            self.created_label.setText(f"Created: {properties['created']}")
        if 'modified' in properties:
            self.modified_label.setText(f"Modified: {properties['modified']}")
        
        # Load security info
        if 'encrypted' in properties:
            encrypted_text = "Yes" if properties['encrypted'] else "No"
            self.encrypted_label.setText(f"Encrypted: {encrypted_text}")
        if 'permissions' in properties:
            self.permissions_label.setText(f"Permissions: {properties['permissions']}")
    
    def clear_properties(self):
        """Clear all property fields."""
        self.title_input.clear()
        self.author_input.clear()
        self.subject_input.clear()
        self.keywords_input.clear()
        
        self.pages_label.setText("Pages: -")
        self.size_label.setText("Size: -")
        self.version_label.setText("PDF Version: -")
        self.created_label.setText("Created: -")
        self.modified_label.setText("Modified: -")
        self.encrypted_label.setText("Encrypted: No")
        self.permissions_label.setText("Permissions: Full access")
    
    def get_format_settings(self) -> dict:
        """
        Get current format settings.
        
        Returns:
            Dictionary of format settings
        """
        return {
            'font_family': self.font_combo.currentText(),
            'font_size': self.size_spin.value(),
            'color': self._current_color.name(),
            'bold': self.bold_cb.isChecked(),
            'italic': self.italic_cb.isChecked(),
            'underline': self.underline_cb.isChecked(),
            'strikethrough': self.strikethrough_cb.isChecked(),
            'alignment': self.align_combo.currentText()
        }
