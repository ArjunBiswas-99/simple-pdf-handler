"""
Simple PDF Handler - Inline Text Editor

An inline text editor that appears directly on the PDF canvas at the
clicked position, allowing users to type text with real-time formatting.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QKeyEvent, QTextCharFormat


class InlineTextEditor(QTextEdit):
    """
    Inline text editor for adding text directly on PDF canvas.
    
    Appears at the clicked position on the PDF, allowing users to type
    text with real-time preview and formatting. Supports multi-line text
    with Ctrl+Enter to commit.
    """
    
    # Signals
    text_committed = pyqtSignal(str, dict)  # text content, format properties
    edit_cancelled = pyqtSignal()
    
    def __init__(self, initial_format: dict, parent=None):
        """
        Initialize the inline text editor.
        
        Args:
            initial_format: Initial format properties (font, size, color, etc.)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store format properties
        self._format = initial_format.copy()
        
        # Configure editor
        self._setup_editor()
        
        # Apply initial formatting
        self._apply_format()
    
    def _setup_editor(self) -> None:
        """Configure the text editor appearance and behavior."""
        # Set minimum size (will grow with content)
        self.setMinimumSize(QSize(200, 40))
        self.setMaximumSize(QSize(600, 400))
        
        # Enable word wrap
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Set placeholder text
        self.setPlaceholderText("Type text here... (Ctrl+Enter to finish, Esc to cancel)")
        
        # Remove scrollbars for cleaner look
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Apply professional styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid #0078D4;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 12pt;
            }
            QTextEdit:focus {
                border-color: #005A9E;
                box-shadow: 0 0 8px rgba(0, 120, 212, 0.3);
            }
        """)
        
        # Auto-focus on creation
        self.setFocus()
    
    def _apply_format(self) -> None:
        """Apply current format properties to the text editor."""
        # Create text format
        char_format = QTextCharFormat()
        
        # Set font
        font = QFont()
        font.setFamily(self._format.get('font', 'Helvetica'))
        font.setPointSize(self._format.get('size', 12))
        font.setBold(self._format.get('bold', False))
        font.setItalic(self._format.get('italic', False))
        font.setUnderline(self._format.get('underline', False))
        char_format.setFont(font)
        
        # Set color
        color = self._format.get('color', QColor(0, 0, 0))
        char_format.setForeground(color)
        
        # Apply format to current text
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.Document)
        cursor.setCharFormat(char_format)
        
        # Set as default format for new text
        self.setCurrentCharFormat(char_format)
        
        # Move cursor to end
        cursor.clearSelection()
        cursor.movePosition(cursor.MoveOperation.End)
        self.setTextCursor(cursor)
    
    def update_format(self, format_properties: dict) -> None:
        """
        Update text formatting in real-time.
        
        Args:
            format_properties: New format properties to apply
        """
        # Update internal format
        self._format.update(format_properties)
        
        # Apply to editor
        self._apply_format()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle keyboard input.
        
        Ctrl+Enter: Commit text
        Escape: Cancel editing
        Enter: New line (normal behavior)
        
        Args:
            event: Key event
        """
        # Check for Ctrl+Enter (commit)
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Ctrl+Enter pressed - commit text
                self._commit_text()
                return
        
        # Check for Escape (cancel)
        if event.key() == Qt.Key.Key_Escape:
            self.edit_cancelled.emit()
            return
        
        # Pass other keys to default handler (including plain Enter for new line)
        super().keyPressEvent(event)
        
        # Auto-resize based on content
        self._adjust_size()
    
    def _adjust_size(self) -> None:
        """Adjust editor size based on content."""
        # Get content size
        doc_size = self.document().size()
        
        # Calculate required height (add padding)
        required_height = int(doc_size.height()) + 20
        required_width = int(doc_size.width()) + 20
        
        # Clamp to min/max
        new_height = max(40, min(400, required_height))
        new_width = max(200, min(600, required_width))
        
        # Update size
        self.setFixedSize(new_width, new_height)
    
    def _commit_text(self) -> None:
        """Commit the entered text and close editor."""
        text = self.toPlainText().strip()
        
        if not text:
            # Empty text - treat as cancel
            self.edit_cancelled.emit()
            return
        
        # Emit signal with text and format
        self.text_committed.emit(text, self._format.copy())
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.toPlainText()
    
    def get_format(self) -> dict:
        """Get the current format properties."""
        return self._format.copy()
