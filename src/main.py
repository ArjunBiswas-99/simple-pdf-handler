"""
Main entry point for the Simple PDF Handler application.

Initializes the application, sets up the theme, and launches the main window.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from utils.config import get_config
from utils.theme_manager import get_theme_manager
from utils.constants import AppInfo
from gui.main_window import MainWindow


def main():
    """
    Initialize and run the application.
    
    Sets up the Qt application with proper configuration, applies the theme,
    and displays the main window.
    """
    # Enable high DPI scaling for better display on high-resolution screens
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName(AppInfo.NAME)
    app.setApplicationVersion(AppInfo.VERSION)
    app.setOrganizationName(AppInfo.ORGANIZATION)
    
    # Get configuration and theme manager
    config = get_config()
    theme_manager = get_theme_manager()
    
    # Load and apply saved theme
    saved_theme = config.get_theme()
    theme_manager.set_theme(saved_theme)
    theme_manager.apply_theme(app)
    
    # Create and show main window
    window = MainWindow()
    
    # Restore window geometry if saved
    geometry = config.get_window_geometry()
    if geometry:
        window.restoreGeometry(geometry)
    
    window.show()
    
    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
