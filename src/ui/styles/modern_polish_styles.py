"""
Simple PDF Handler - Modern Polish Styles

MS Word EXACT UI replication - Microsoft Office colors and design.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


class ModernPolishStyles:
    """
    MS Word exact UI replication.
    Uses Microsoft Office's actual colors and design patterns from Office 365.
    """
    
    @staticmethod
    def get_appbar_style() -> str:
        """MS Word AppBar - exact Microsoft colors."""
        return """
            AppBar {
                background-color: #F3F2F1;
                border-bottom: 1px solid #D2D0CE;
            }
            
            /* Dark theme */
            AppBar[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            /* AppBar buttons - MS Word style */
            AppBar QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 8px 12px;
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
                min-width: 32px;
                min-height: 32px;
            }
            
            AppBar QPushButton:hover:enabled {
                background-color: #F3F2F1;
            }
            
            AppBar QPushButton:pressed:enabled {
                background-color: #E1DFDD;
            }
            
            /* Dark theme buttons */
            AppBar[dark="true"] QPushButton {
                color: #E0E0E0;
            }
            
            AppBar[dark="true"] QPushButton:hover:enabled {
                background-color: #3F3F3F;
            }
            
            AppBar[dark="true"] QPushButton:pressed:enabled {
                background-color: #4A4A4A;
            }
        """
    
    @staticmethod
    def get_toolbar_style() -> str:
        """MS Word EXACT toolbar - Ribbon appearance with Microsoft colors."""
        return """
            /* Toolbar container - MS Word Ribbon color */
            ViewToolbar, QToolBar {
                background-color: #FAFAFA;
                border-bottom: 1px solid #D2D0CE;
                padding: 6px 12px;
            }
            
            /* Dark theme */
            ViewToolbar[dark="true"], QToolBar[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            /* Toolbar buttons - EXACT MS Word button style */
            ViewToolbar QPushButton, QToolBar QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 8px 12px;
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 11px;
                min-height: 28px;
            }
            
            ViewToolbar QPushButton:hover:enabled, QToolBar QPushButton:hover:enabled {
                background-color: #F3F2F1;
            }
            
            ViewToolbar QPushButton:pressed:enabled, QToolBar QPushButton:pressed:enabled {
                background-color: #E1DFDD;
            }
            
            ViewToolbar QPushButton:disabled, QToolBar QPushButton:disabled {
                color: #A19F9D;
                background-color: transparent;
            }
            
            ViewToolbar QPushButton:checked, QToolBar QPushButton:checked {
                background-color: #EDEBE9;
                color: #0078D4;
                border-left: 3px solid #0078D4;
                padding-left: 9px;
            }
            
            /* Dark theme toolbar buttons */
            ViewToolbar[dark="true"] QPushButton, QToolBar[dark="true"] QPushButton {
                color: #E0E0E0;
            }
            
            ViewToolbar[dark="true"] QPushButton:hover:enabled, QToolBar[dark="true"] QPushButton:hover:enabled {
                background-color: #3F3F3F;
            }
            
            ViewToolbar[dark="true"] QPushButton:pressed:enabled, QToolBar[dark="true"] QPushButton:pressed:enabled {
                background-color: #4A4A4A;
            }
            
            ViewToolbar[dark="true"] QPushButton:disabled, QToolBar[dark="true"] QPushButton:disabled {
                color: #666666;
            }
            
            /* Toolbar separators - MS Word group dividers */
            ViewToolbar QFrame[frameShape="4"], QToolBar QFrame[frameShape="4"] {
                background-color: #D2D0CE;
                max-width: 1px;
                min-height: 20px;
                margin: 6px 10px;
            }
            
            ViewToolbar[dark="true"] QFrame[frameShape="4"], QToolBar[dark="true"] QFrame[frameShape="4"] {
                background-color: #3F3F3F;
            }
            
            /* Toolbar combo boxes - MS Word dropdowns */
            ViewToolbar QComboBox, QToolBar QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D2D0CE;
                border-radius: 2px;
                padding: 5px 10px;
                min-height: 24px;
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 11px;
            }
            
            ViewToolbar QComboBox:hover, QToolBar QComboBox:hover {
                border-color: #A19F9D;
                background-color: #F3F2F1;
            }
            
            ViewToolbar QComboBox:focus, QToolBar QComboBox:focus {
                border-color: #0078D4;
                border-width: 1px;
            }
            
            ViewToolbar QComboBox::drop-down, QToolBar QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            ViewToolbar QComboBox::down-arrow, QToolBar QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 5px solid #323130;
                margin-right: 6px;
            }
            
            /* Dark theme combo boxes */
            ViewToolbar[dark="true"] QComboBox, QToolBar[dark="true"] QComboBox {
                background-color: #3A3A3A;
                border-color: #555555;
                color: #E0E0E0;
            }
            
            ViewToolbar[dark="true"] QComboBox::down-arrow, QToolBar[dark="true"] QComboBox::down-arrow {
                border-top-color: #E0E0E0;
            }
            
            /* Toolbar line edits - MS Word input fields */
            ViewToolbar QLineEdit, QToolBar QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D2D0CE;
                border-radius: 2px;
                padding: 5px 8px;
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 11px;
                min-height: 24px;
            }
            
            ViewToolbar QLineEdit:hover, QToolBar QLineEdit:hover {
                border-color: #A19F9D;
                background-color: #F3F2F1;
            }
            
            ViewToolbar QLineEdit:focus, QToolBar QLineEdit:focus {
                border-color: #0078D4;
                border-width: 1px;
            }
            
            ViewToolbar[dark="true"] QLineEdit, QToolBar[dark="true"] QLineEdit {
                background-color: #3A3A3A;
                border-color: #555555;
                color: #E0E0E0;
            }
            
            /* Toolbar labels - MS Word text */
            ViewToolbar QLabel, QToolBar QLabel {
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 11px;
                padding: 0 4px;
            }
            
            ViewToolbar[dark="true"] QLabel, QToolBar[dark="true"] QLabel {
                color: #E0E0E0;
            }
        """
    
    @staticmethod
    def get_mode_tabs_style() -> str:
        """MS Word EXACT tab style - Ribbon tabs."""
        return """
            ModeTabs {
                background-color: #F3F2F1;
                border-bottom: 1px solid #D2D0CE;
            }
            
            ModeTabs[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            ModeTabs QPushButton {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                padding: 10px 20px;
                color: #323130;
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 12px;
            }
            
            ModeTabs QPushButton:hover {
                background-color: #F3F2F1;
            }
            
            ModeTabs QPushButton:checked {
                color: #0078D4;
                border-bottom: 2px solid #0078D4;
                background-color: #FFFFFF;
            }
            
            /* Dark theme */
            ModeTabs[dark="true"] QPushButton {
                color: #A0A0A0;
            }
            
            ModeTabs[dark="true"] QPushButton:hover {
                background-color: #3F3F3F;
                color: #E0E0E0;
            }
            
            ModeTabs[dark="true"] QPushButton:checked {
                color: #4CA8FF;
                border-bottom-color: #4CA8FF;
            }
        """
    
    @staticmethod
    def get_complete_modern_stylesheet() -> str:
        """Get complete MS Word stylesheet."""
        return f"""
            /* ============================================
               MS WORD EXACT STYLES - OFFICE 365
               ============================================ */
            
            {ModernPolishStyles.get_appbar_style()}
            {ModernPolishStyles.get_toolbar_style()}
            {ModernPolishStyles.get_mode_tabs_style()}
            
            /* Global typography - Segoe UI (MS Word font) */
            * {{
                font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            }}
            
            QMainWindow {{
                background-color: #FFFFFF;
            }}
            
            QMainWindow[dark="true"] {{
                background-color: #1E1E1E;
            }}
        """
