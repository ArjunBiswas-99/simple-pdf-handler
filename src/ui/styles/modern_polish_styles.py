"""
Simple PDF Handler - Modern Polish Styles

MS Word-inspired professional UI with crisp buttons, good contrast, and smooth interactions.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


class ModernPolishStyles:
    """
    MS Word-inspired modern UI styles.
    Focuses on: clarity, contrast, professionalism, and smooth interactions.
    """
    
    @staticmethod
    def get_appbar_style() -> str:
        """Solid, professional AppBar style."""
        return """
            AppBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #DCDCDC;
            }
            
            /* Dark theme */
            AppBar[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            /* AppBar buttons */
            AppBar QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 10px;
                color: #323232;
                font-size: 16px;
                min-width: 36px;
                min-height: 36px;
            }
            
            AppBar QPushButton:hover:enabled {
                background-color: #F3F3F3;
                border-color: #D4D4D4;
            }
            
            AppBar QPushButton:pressed:enabled {
                background-color: #E8E8E8;
            }
            
            /* Dark theme buttons */
            AppBar[dark="true"] QPushButton {
                color: #E0E0E0;
            }
            
            AppBar[dark="true"] QPushButton:hover:enabled {
                background-color: #3F3F3F;
                border-color: #555555;
            }
            
            AppBar[dark="true"] QPushButton:pressed:enabled {
                background-color: #4A4A4A;
            }
        """
    
    @staticmethod
    def get_toolbar_style() -> str:
        """MS Word-inspired toolbar style with solid backgrounds and crisp buttons."""
        return """
            /* Toolbar container */
            ViewToolbar, QToolBar {
                background-color: #F8F8F8;
                border-bottom: 1px solid #DCDCDC;
                padding: 4px 8px;
            }
            
            /* Dark theme */
            ViewToolbar[dark="true"], QToolBar[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            /* Toolbar buttons - MS Word style */
            ViewToolbar QPushButton, QToolBar QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 12px;
                color: #323232;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
            }
            
            ViewToolbar QPushButton:hover:enabled, QToolBar QPushButton:hover:enabled {
                background-color: #E8F4FD;
                border-color: #CCE4F7;
            }
            
            ViewToolbar QPushButton:pressed:enabled, QToolBar QPushButton:pressed:enabled {
                background-color: #D0E8F7;
                border-color: #B8D6EB;
            }
            
            ViewToolbar QPushButton:disabled, QToolBar QPushButton:disabled {
                color: #BEBEBE;
                background-color: transparent;
            }
            
            ViewToolbar QPushButton:checked, QToolBar QPushButton:checked {
                background-color: #2680EB;
                color: white;
                border-color: #2680EB;
                font-weight: 600;
            }
            
            /* Dark theme toolbar buttons */
            ViewToolbar[dark="true"] QPushButton, QToolBar[dark="true"] QPushButton {
                color: #E0E0E0;
            }
            
            ViewToolbar[dark="true"] QPushButton:hover:enabled, QToolBar[dark="true"] QPushButton:hover:enabled {
                background-color: #3F3F3F;
                border-color: #555555;
            }
            
            ViewToolbar[dark="true"] QPushButton:pressed:enabled, QToolBar[dark="true"] QPushButton:pressed:enabled {
                background-color: #4A4A4A;
            }
            
            ViewToolbar[dark="true"] QPushButton:disabled, QToolBar[dark="true"] QPushButton:disabled {
                color: #666666;
            }
            
            /* Toolbar separators */
            ViewToolbar QFrame[frameShape="4"], QToolBar QFrame[frameShape="4"] {
                background-color: #DCDCDC;
                max-width: 1px;
                min-height: 24px;
                margin: 4px 8px;
            }
            
            ViewToolbar[dark="true"] QFrame[frameShape="4"], QToolBar[dark="true"] QFrame[frameShape="4"] {
                background-color: #3F3F3F;
            }
            
            /* Toolbar combo boxes */
            ViewToolbar QComboBox, QToolBar QComboBox {
                background-color: white;
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 6px 12px;
                min-height: 32px;
                color: #323232;
            }
            
            ViewToolbar QComboBox:hover, QToolBar QComboBox:hover {
                border-color: #B0B0B0;
            }
            
            ViewToolbar QComboBox:focus, QToolBar QComboBox:focus {
                border-color: #2680EB;
                border-width: 2px;
            }
            
            ViewToolbar QComboBox::drop-down, QToolBar QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            
            ViewToolbar QComboBox::down-arrow, QToolBar QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #323232;
                margin-right: 8px;
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
            
            /* Toolbar line edits */
            ViewToolbar QLineEdit, QToolBar QLineEdit {
                background-color: white;
                border: 1px solid #D4D4D4;
                border-radius: 4px;
                padding: 6px 8px;
                color: #323232;
                min-height: 32px;
            }
            
            ViewToolbar QLineEdit:hover, QToolBar QLineEdit:hover {
                border-color: #B0B0B0;
            }
            
            ViewToolbar QLineEdit:focus, QToolBar QLineEdit:focus {
                border-color: #2680EB;
                border-width: 2px;
                padding: 5px 7px;
            }
            
            ViewToolbar[dark="true"] QLineEdit, QToolBar[dark="true"] QLineEdit {
                background-color: #3A3A3A;
                border-color: #555555;
                color: #E0E0E0;
            }
        """
    
    @staticmethod
    def get_mode_tabs_style() -> str:
        """MS Word-style mode tabs."""
        return """
            ModeTabs {
                background-color: #F8F8F8;
                border-bottom: 1px solid #DCDCDC;
            }
            
            ModeTabs[dark="true"] {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3F3F3F;
            }
            
            ModeTabs QPushButton {
                background-color: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                padding: 10px 20px;
                color: #646464;
                font-size: 14px;
                font-weight: 500;
            }
            
            ModeTabs QPushButton:hover {
                background-color: #EFEFEF;
                color: #323232;
            }
            
            ModeTabs QPushButton:checked {
                color: #2680EB;
                border-bottom: 3px solid #2680EB;
                background-color: transparent;
                font-weight: 600;
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
        """Get complete modern polish stylesheet."""
        return f"""
            /* ============================================
               MODERN POLISH STYLES - MS WORD INSPIRED
               ============================================ */
            
            {ModernPolishStyles.get_appbar_style()}
            {ModernPolishStyles.get_toolbar_style()}
            {ModernPolishStyles.get_mode_tabs_style()}
            
            /* Global improvements */
            * {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            
            QMainWindow {{
                background-color: #FFFFFF;
            }}
            
            QMainWindow[dark="true"] {{
                background-color: #1E1E1E;
            }}
        """
