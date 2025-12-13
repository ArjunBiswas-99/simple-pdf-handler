"""
Application entry point for Simple PDF Handler.
Initializes and launches the main application window.
"""

import sys
import os

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """
    Main function to start the PDF handler application.
    Creates the QApplication instance and displays the main window.
    """
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Simple PDF Handler")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Arjun Biswas")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
