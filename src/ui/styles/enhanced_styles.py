"""
Simple PDF Handler - Enhanced Professional Styles

Smooth animations, transitions, and visual polish for professional UX.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


class EnhancedStyles:
    """Enhanced styling with smooth animations and professional polish."""
    
    @staticmethod
    def get_global_transitions() -> str:
        """
        Global CSS transitions for smooth animations.
        Note: Qt StyleSheets don't support transitions like CSS,
        but we can achieve smooth effects through other means.
        """
        return """
            /* Global smooth transitions would go here if Qt supported them */
            /* Instead, we'll use hover states and careful styling */
        """
    
    @staticmethod
    def get_enhanced_button_style() -> str:
        """Enhanced button styles with professional polish."""
        return """
            QPushButton {
                border: 1px solid #D4D4D4;
                border-radius: 6px;
                padding: 8px 16px;
                background-color: white;
                color: #2C2C2C;
                font-size: 13px;
                font-weight: 500;
            }
            
            QPushButton:hover:enabled {
                background-color: #F0F8FF;
                border-color: #2680EB;
                color: #2680EB;
            }
            
            QPushButton:pressed:enabled {
                background-color: #E0F0FF;
            }
            
            QPushButton:disabled {
                background-color: #F5F5F5;
                color: #BEBEBE;
                border-color: #E9E9E9;
            }
            
            QPushButton:checked {
                background-color: #2680EB;
                color: white;
                border-color: #2680EB;
                font-weight: 600;
            }
            
            QPushButton:checked:hover {
                background-color: #1E6FD8;
            }
        """
    
    @staticmethod
    def get_enhanced_icon_button_style() -> str:
        """Enhanced icon button styles (for toolbars, icon rails)."""
        return """
            /* Icon buttons */
            .icon-button {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
                min-width: 36px;
                min-height: 36px;
                font-size: 18px;
            }
            
            .icon-button:hover:enabled {
                background-color: rgba(38, 128, 235, 0.1);
            }
            
            .icon-button:pressed:enabled {
                background-color: rgba(38, 128, 235, 0.2);
            }
            
            .icon-button:checked {
                background-color: #2680EB;
                color: white;
            }
            
            .icon-button:checked:hover {
                background-color: #1E6FD8;
            }
        """
    
    @staticmethod
    def get_enhanced_shadows() -> str:
        """Enhanced shadow styles for depth."""
        return """
            /* AppBar shadow */
            .app-bar {
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            }
            
            /* Toolbar shadow */
            .toolbar {
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
            }
            
            /* Sidebar shadow */
            .sidebar {
                box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
            }
            
            /* Panel shadow */
            .panel {
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }
            
            /* Card shadow */
            .card {
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            }
            
            .card:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        """
    
    @staticmethod
    def get_enhanced_inputs() -> str:
        """Enhanced input field styles."""
        return """
            QLineEdit, QTextEdit, QPlainTextEdit {
                border: 1px solid #D4D4D4;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                color: #2C2C2C;
                font-size: 13px;
                selection-background-color: #2680EB;
                selection-color: white;
            }
            
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
                border-color: #B0B0B0;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #2680EB;
                border-width: 2px;
                padding: 7px 11px;  /* Adjust padding to maintain size */
                outline: none;
            }
            
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
                background-color: #F5F5F5;
                color: #BEBEBE;
                border-color: #E9E9E9;
            }
        """
    
    @staticmethod
    def get_enhanced_scrollbar() -> str:
        """Enhanced scrollbar styles."""
        return """
            QScrollBar:vertical {
                border: none;
                background-color: #F5F5F5;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #D4D4D4;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #B0B0B0;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #909090;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: #F5F5F5;
                height: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #D4D4D4;
                border-radius: 6px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #B0B0B0;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: #909090;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
        """
    
    @staticmethod
    def get_enhanced_tooltips() -> str:
        """Enhanced tooltip styles."""
        return """
            QToolTip {
                background-color: #2C2C2C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
                opacity: 0.95;
            }
        """
    
    @staticmethod
    def get_enhanced_list_items() -> str:
        """Enhanced list and tree item styles."""
        return """
            QListWidget::item, QTreeWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 4px;
                background-color: white;
            }
            
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: #F0F8FF;
            }
            
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #2680EB;
                color: white;
            }
            
            QListWidget::item:selected:hover, QTreeWidget::item:selected:hover {
                background-color: #1E6FD8;
            }
            
            QListWidget, QTreeWidget {
                border: 1px solid #E9E9E9;
                border-radius: 8px;
                background-color: #FAFAFA;
                outline: none;
            }
            
            QListWidget:focus, QTreeWidget:focus {
                border-color: #2680EB;
            }
        """
    
    @staticmethod
    def get_complete_enhanced_stylesheet() -> str:
        """Get complete enhanced stylesheet."""
        return f"""
            /* Enhanced Professional Styles */
            
            {EnhancedStyles.get_enhanced_button_style()}
            {EnhancedStyles.get_enhanced_icon_button_style()}
            {EnhancedStyles.get_enhanced_inputs()}
            {EnhancedStyles.get_enhanced_scrollbar()}
            {EnhancedStyles.get_enhanced_tooltips()}
            {EnhancedStyles.get_enhanced_list_items()}
            
            /* Typography refinements */
            * {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            
            /* Smooth focus outlines */
            *:focus {{
                outline: none;
            }}
            
            /* Better selection colors */
            *::selection {{
                background-color: #2680EB;
                color: white;
            }}
        """
