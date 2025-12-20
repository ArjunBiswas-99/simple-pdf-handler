"""
Simple PDF Handler - Application Core

Main application class that initializes and registers all controllers.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
"""

from typing import Optional
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

from .theme_manager import ThemeManager
from ..features.viewing.controller import ViewingController
from ..features.editing.controller import EditingController
from ..features.page_management.controller import PageManagementController
from ..features.annotation.controller import AnnotationController
from ..features.merging.controller import MergingController
from ..features.conversion.controller import ConversionController
from ..features.ocr.controller import OCRController
from ..features.file_operations.controller import FileOperationsController


class PDFHandlerApp(QObject):
    """
    Main application class that coordinates all components.
    
    Initializes all feature controllers and registers them with QML engine.
    Each controller is exposed to QML for UI interaction.
    """
    
    def __init__(self, engine: QQmlApplicationEngine):
        """
        Initializes application with QML engine.
        
        Args:
            engine: QML application engine for registering context properties
        """
        super().__init__()
        self._engine = engine
        
        # Initialize theme manager
        self._theme_manager = ThemeManager()
        
        # Initialize all feature controllers
        self._viewing_controller = ViewingController()
        self._editing_controller = EditingController()
        self._page_management_controller = PageManagementController()
        self._annotation_controller = AnnotationController()
        self._merging_controller = MergingController()
        self._conversion_controller = ConversionController()
        self._ocr_controller = OCRController()
        self._file_operations_controller = FileOperationsController()
    
    def initialize(self) -> None:
        """
        Registers all controllers with QML engine.
        
        Makes controllers accessible from QML via context properties.
        Each controller is registered with a descriptive name.
        """
        root_context = self._engine.rootContext()
        
        # Register theme manager
        root_context.setContextProperty("themeManager", self._theme_manager)
        
        # Register all feature controllers
        root_context.setContextProperty("viewingController", self._viewing_controller)
        root_context.setContextProperty("editingController", self._editing_controller)
        root_context.setContextProperty("pageManagementController", self._page_management_controller)
        root_context.setContextProperty("annotationController", self._annotation_controller)
        root_context.setContextProperty("mergingController", self._merging_controller)
        root_context.setContextProperty("conversionController", self._conversion_controller)
        root_context.setContextProperty("ocrController", self._ocr_controller)
        root_context.setContextProperty("fileOperationsController", self._file_operations_controller)
    
    @property
    def theme_manager(self) -> ThemeManager:
        """Returns theme manager instance."""
        return self._theme_manager
    
    @property
    def viewing_controller(self) -> ViewingController:
        """Returns viewing controller instance."""
        return self._viewing_controller
    
    @property
    def editing_controller(self) -> EditingController:
        """Returns editing controller instance."""
        return self._editing_controller
    
    @property
    def page_management_controller(self) -> PageManagementController:
        """Returns page management controller instance."""
        return self._page_management_controller
    
    @property
    def annotation_controller(self) -> AnnotationController:
        """Returns annotation controller instance."""
        return self._annotation_controller
    
    @property
    def merging_controller(self) -> MergingController:
        """Returns merging controller instance."""
        return self._merging_controller
    
    @property
    def conversion_controller(self) -> ConversionController:
        """Returns conversion controller instance."""
        return self._conversion_controller
    
    @property
    def ocr_controller(self) -> OCRController:
        """Returns OCR controller instance."""
        return self._ocr_controller
    
    @property
    def file_operations_controller(self) -> FileOperationsController:
        """Returns file operations controller instance."""
        return self._file_operations_controller
