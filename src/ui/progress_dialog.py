"""
Progress dialog for displaying loading status.
Shows progress bar and status messages during long-running operations.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    """
    Modal dialog displaying progress for long-running operations.
    Used primarily for loading large PDF files.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent widget, or None for top-level dialog
        """
        super().__init__(parent)
        self._setup_ui()
        self._is_cancelled = False
    
    def _setup_ui(self) -> None:
        """Configure the dialog layout and widgets."""
        self.setWindowTitle("Loading PDF")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Status label
        self._status_label = QLabel("Opening PDF file...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)
        
        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)
        
        # File info label
        self._info_label = QLabel("")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self._info_label)
        
        # Cancel button
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(self._cancel_button)
        
        self.setLayout(layout)
    
    def update_progress(self, value: int) -> None:
        """
        Update the progress bar value.
        
        Args:
            value: Progress percentage (0-100)
        """
        self._progress_bar.setValue(value)
        
        # Update status message based on progress
        if value < 30:
            self._status_label.setText("Opening PDF file...")
        elif value < 60:
            self._status_label.setText("Loading document...")
        elif value < 90:
            self._status_label.setText("Preparing pages...")
        else:
            self._status_label.setText("Almost done...")
    
    def set_status(self, message: str) -> None:
        """
        Set the status message displayed to the user.
        
        Args:
            message: Status message to display
        """
        self._status_label.setText(message)
    
    def set_file_info(self, info: str) -> None:
        """
        Set additional file information to display.
        
        Args:
            info: Information text (e.g., file size, page count)
        """
        self._info_label.setText(info)
    
    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self._is_cancelled = True
        self._cancel_button.setEnabled(False)
        self._status_label.setText("Cancelling...")
        self.reject()
    
    def is_cancelled(self) -> bool:
        """
        Check if the operation was cancelled by the user.
        
        Returns:
            True if cancelled, False otherwise
        """
        return self._is_cancelled
    
    def reset(self) -> None:
        """Reset the dialog to initial state."""
        self._progress_bar.setValue(0)
        self._status_label.setText("Opening PDF file...")
        self._info_label.setText("")
        self._cancel_button.setEnabled(True)
        self._is_cancelled = False
