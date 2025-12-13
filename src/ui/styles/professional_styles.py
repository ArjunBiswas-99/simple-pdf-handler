"""
Simple PDF Handler - Professional Styling Module

Adobe Acrobat-inspired professional styling for the application.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


class ProfessionalStyles:
    """Professional styling constants and stylesheet generator."""
    
    # Color Palette (Adobe Acrobat inspired)
    PRIMARY_DARK = "#2C2C2C"
    PRIMARY_LIGHT = "#F5F5F5"
    ACCENT_BLUE = "#2680EB"
    HOVER_GRAY = "#E9E9E9"
    BORDER_GRAY = "#D4D4D4"
    TEXT_PRIMARY = "#2C2C2C"
    TEXT_SECONDARY = "#6E6E6E"
    BACKGROUND_WHITE = "#FFFFFF"
    SHADOW_COLOR = "rgba(0, 0, 0, 0.1)"
    
    # Search highlight colors
    HIGHLIGHT_YELLOW = "rgba(255, 235, 59, 0.4)"
    HIGHLIGHT_ORANGE = "rgba(255, 152, 0, 0.5)"
    
    @staticmethod
    def get_main_window_style() -> str:
        """Get stylesheet for main window."""
        return """
            QMainWindow {
                background-color: #F5F5F5;
            }
            
            QStatusBar {
                background-color: #F5F5F5;
                color: #6E6E6E;
                border-top: 1px solid #D4D4D4;
                font-size: 11px;
                padding: 4px 8px;
            }
        """
    
    @staticmethod
    def get_toolbar_style() -> str:
        """Get stylesheet for toolbar."""
        return """
            QToolBar {
                background-color: #FFFFFF;
                border: none;
                border-bottom: 1px solid #D4D4D4;
                spacing: 4px;
                padding: 4px 8px;
            }
            
            QToolBar::separator {
                background-color: #D4D4D4;
                width: 1px;
                margin: 6px 8px;
            }
            
            QToolBar QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                color: #2C2C2C;
                min-width: 32px;
                min-height: 32px;
            }
            
            QToolBar QPushButton:hover {
                background-color: #E9E9E9;
                border-color: #D4D4D4;
            }
            
            QToolBar QPushButton:pressed {
                background-color: #D4D4D4;
            }
            
            QToolBar QPushButton:disabled {
                color: #BEBEBE;
                background-color: transparent;
            }
            
            QToolBar QPushButton:checked {
                background-color: #2680EB;
                color: white;
                border-color: #2680EB;
            }
            
            QToolBar QLineEdit {
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 12px;
            }
            
            QToolBar QLineEdit:focus {
                border-color: #2680EB;
            }
            
            QToolBar QComboBox {
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 12px;
            }
            
            QToolBar QComboBox:hover {
                border-color: #2680EB;
            }
            
            QToolBar QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QToolBar QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            
            QToolBar QLabel {
                color: #6E6E6E;
                font-size: 12px;
            }
        """
    
    @staticmethod
    def get_left_panel_style() -> str:
        """Get stylesheet for left side panel."""
        return """
            LeftSidePanel {
                background-color: #FAFAFA;
                border-right: 1px solid #D4D4D4;
            }
            
            /* Tab bar for panel sections */
            QTabWidget::pane {
                border: none;
                background-color: #FAFAFA;
            }
            
            QTabBar::tab {
                background-color: transparent;
                color: #6E6E6E;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 11px;
                min-width: 60px;
            }
            
            QTabBar::tab:hover {
                color: #2C2C2C;
                background-color: #F0F0F0;
            }
            
            QTabBar::tab:selected {
                color: #2680EB;
                border-bottom: 2px solid #2680EB;
                font-weight: bold;
            }
            
            QTabBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #D4D4D4;
            }
        """
    
    @staticmethod
    def get_search_panel_style() -> str:
        """Get stylesheet for search panel."""
        return """
            SearchPanel {
                background-color: #FAFAFA;
                padding: 12px;
            }
            
            SearchPanel QLineEdit {
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 8px 32px 8px 12px;
                background-color: white;
                font-size: 13px;
                color: #2C2C2C;
            }
            
            SearchPanel QLineEdit:focus {
                border-color: #2680EB;
                outline: none;
            }
            
            SearchPanel QCheckBox {
                color: #6E6E6E;
                font-size: 12px;
                spacing: 6px;
            }
            
            SearchPanel QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #D4D4D4;
                border-radius: 3px;
                background-color: white;
            }
            
            SearchPanel QCheckBox::indicator:checked {
                background-color: #2680EB;
                border-color: #2680EB;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzIDQuMzNMNiAxMS42NkwyLjY3IDguMzNMMy43MyA3LjI3TDYgOS41NEwxMi4yNyAzLjI3TDEzLjMzIDQuMzNaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4=);
            }
            
            SearchPanel QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            
            SearchPanel QListWidget::item {
                padding: 10px 12px;
                border-radius: 4px;
                margin: 2px 0px;
                color: #2C2C2C;
                font-size: 12px;
                background-color: white;
                border: 1px solid #E9E9E9;
            }
            
            SearchPanel QListWidget::item:hover {
                background-color: #F0F8FF;
                border-color: #2680EB;
            }
            
            SearchPanel QListWidget::item:selected {
                background-color: #2680EB;
                color: white;
                border-color: #2680EB;
            }
            
            SearchPanel QPushButton {
                background-color: transparent;
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                color: #2C2C2C;
            }
            
            SearchPanel QPushButton:hover {
                background-color: #E9E9E9;
                border-color: #2680EB;
            }
            
            SearchPanel QPushButton:pressed {
                background-color: #D4D4D4;
            }
            
            SearchPanel QPushButton:disabled {
                color: #BEBEBE;
                border-color: #E9E9E9;
                background-color: transparent;
            }
            
            SearchPanel QLabel {
                color: #6E6E6E;
                font-size: 11px;
            }
            
            SearchPanel QProgressBar {
                border: none;
                background-color: #E9E9E9;
                border-radius: 2px;
                text-align: center;
            }
            
            SearchPanel QProgressBar::chunk {
                background-color: #2680EB;
                border-radius: 2px;
            }
        """
    
    @staticmethod
    def get_canvas_style() -> str:
        """Get stylesheet for PDF canvas."""
        return """
            PDFCanvas {
                background-color: #E0E0E0;
                border: none;
            }
        """
    
    @staticmethod
    def get_complete_stylesheet() -> str:
        """
        Get complete stylesheet for the entire application.
        
        Returns:
            Complete CSS stylesheet
        """
        return f"""
            {ProfessionalStyles.get_main_window_style()}
            {ProfessionalStyles.get_toolbar_style()}
            {ProfessionalStyles.get_left_panel_style()}
            {ProfessionalStyles.get_search_panel_style()}
            {ProfessionalStyles.get_canvas_style()}
        """
