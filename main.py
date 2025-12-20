"""
Simple PDF Handler - Application Entry Point

Main application launcher that initializes the QML engine and registers controllers.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from src.core.app import PDFHandlerApp


def main() -> int:
    """
    Application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Create Qt application instance
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("SimplePDFHandler")
    app.setApplicationName("Simple PDF Handler")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Initialize application and register controllers
    pdf_app = PDFHandlerApp(engine)
    pdf_app.initialize()
    
    # Load main QML file
    qml_file = Path(__file__).parent / "src" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return -1
    
    # Start application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
