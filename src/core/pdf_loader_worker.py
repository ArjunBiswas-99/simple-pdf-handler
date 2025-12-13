"""
Background worker for loading PDF files.
Handles asynchronous PDF loading to prevent UI freezing for large files.
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from backend.pymupdf_backend import PyMuPDFBackend


class PDFLoaderWorker(QThread):
    """
    Background thread worker for loading PDF files.
    Emits signals to communicate loading progress and results to the UI.
    """
    
    # Signals for communicating with the main thread
    progress_updated = pyqtSignal(int)  # Progress percentage (0-100)
    loading_completed = pyqtSignal(object)  # Backend object when successful
    loading_failed = pyqtSignal(str)  # Error message on failure
    
    def __init__(self, file_path: str):
        """
        Initialize the PDF loader worker.
        
        Args:
            file_path: Absolute path to the PDF file to load
        """
        super().__init__()
        self._file_path = file_path
        self._backend: PyMuPDFBackend = None
    
    def run(self) -> None:
        """
        Execute the PDF loading operation in the background thread.
        This method runs in a separate thread and communicates via signals.
        """
        try:
            # Validate file exists
            if not os.path.exists(self._file_path):
                self.loading_failed.emit("File not found")
                return
            
            # Get file size for progress estimation
            file_size = os.path.getsize(self._file_path)
            
            # Initial progress
            self.progress_updated.emit(10)
            
            # Create backend instance
            self._backend = PyMuPDFBackend()
            
            # Load the PDF file
            self.progress_updated.emit(30)
            success = self._backend.load_file(self._file_path)
            
            if not success:
                self.loading_failed.emit("Failed to open PDF file")
                return
            
            # Verify the document loaded correctly
            self.progress_updated.emit(60)
            page_count = self._backend.get_page_count()
            
            if page_count == 0:
                self.loading_failed.emit("PDF file appears to be empty")
                return
            
            # Pre-render first page for faster initial display
            self.progress_updated.emit(80)
            first_page = self._backend.render_page(0, 1.0)
            
            if first_page is None:
                self.loading_failed.emit("Failed to render PDF pages")
                return
            
            # Loading complete
            self.progress_updated.emit(100)
            self.loading_completed.emit(self._backend)
            
        except Exception as e:
            # Handle any unexpected errors
            error_message = f"Error loading PDF: {str(e)}"
            self.loading_failed.emit(error_message)
    
    def get_backend(self) -> PyMuPDFBackend:
        """
        Get the loaded backend instance.
        
        Returns:
            PyMuPDFBackend instance, or None if not loaded
        """
        return self._backend
