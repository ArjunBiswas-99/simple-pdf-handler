"""
Simple PDF Handler - Application Entry Point

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
