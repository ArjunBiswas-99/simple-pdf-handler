"""
Simple PDF Handler - Qt StyleSheet Generator

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

from .themes import ThemeType, get_theme_colors


def generate_stylesheet(theme_type: ThemeType) -> str:
    """
    Generate complete QSS stylesheet for the specified theme.
    
    Args:
        theme_type: Theme to generate stylesheet for
        
    Returns:
        Complete QSS stylesheet as string
    """
    colors = get_theme_colors(theme_type)
    
    return f"""
/* ===== MAIN WINDOW ===== */
QMainWindow {{
    background-color: {colors['background']};
    color: {colors['text_primary']};
}}

/* ===== MENU BAR ===== */
QMenuBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary']}, stop:1 {colors['primary_dark']});
    color: {colors['text_on_primary']};
    padding: 6px;
    border: none;
    font-size: 11pt;
    font-weight: 500;
}}

QMenuBar::item {{
    background: transparent;
    padding: 8px 16px;
    border-radius: 4px;
    margin: 2px;
}}

QMenuBar::item:selected {{
    background: rgba(255, 255, 255, 0.2);
}}

QMenuBar::item:pressed {{
    background: rgba(255, 255, 255, 0.3);
}}

/* ===== MENU DROPDOWNS ===== */
QMenu {{
    background-color: {colors['surface']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 6px;
    padding: 8px;
}}

QMenu::item {{
    padding: 8px 24px 8px 16px;
    border-radius: 4px;
    margin: 2px;
}}

QMenu::item:selected {{
    background-color: {colors['hover']};
}}

QMenu::separator {{
    height: 1px;
    background: {colors['border']};
    margin: 6px 16px;
}}

/* ===== TOOLBAR ===== */
QToolBar {{
    background: {colors['surface']};
    border: none;
    border-bottom: 2px solid {colors['primary']};
    spacing: 10px;
    padding: 10px;
}}

QToolBar::separator {{
    background: {colors['border']};
    width: 2px;
    margin: 4px 8px;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary']}, stop:1 {colors['primary_dark']});
    color: {colors['text_on_primary']};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 10pt;
    min-height: 28px;
}}

QPushButton:hover {{
    background: {colors['primary_light']};
}}

QPushButton:pressed {{
    background: {colors['primary_dark']};
    padding-top: 9px;
    padding-bottom: 7px;
}}

QPushButton:disabled {{
    background: {colors['disabled']};
    color: {colors['text_secondary']};
}}

/* ===== COMBO BOX (Zoom Dropdown) ===== */
QComboBox {{
    background: {colors['surface']};
    border: 2px solid {colors['primary']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {colors['text_primary']};
    font-weight: bold;
    font-size: 10pt;
    min-height: 28px;
}}

QComboBox:hover {{
    border-color: {colors['primary_light']};
    background: {colors['hover']};
}}

QComboBox:disabled {{
    background: {colors['disabled']};
    border-color: {colors['border']};
    color: {colors['text_secondary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 25px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {colors['text_primary']};
    width: 0px;
    height: 0px;
}}

QComboBox QAbstractItemView {{
    background: {colors['surface']};
    color: {colors['text_primary']};
    border: 2px solid {colors['primary']};
    border-radius: 4px;
    padding: 4px;
    selection-background-color: {colors['primary']};
    selection-color: {colors['text_on_primary']};
}}

/* ===== LINE EDIT (Page Input) ===== */
QLineEdit {{
    background: {colors['surface']};
    border: 2px solid {colors['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {colors['text_primary']};
    font-weight: bold;
    font-size: 10pt;
    min-height: 28px;
}}

QLineEdit:focus {{
    border-color: {colors['primary']};
}}

QLineEdit:disabled {{
    background: {colors['disabled']};
    color: {colors['text_secondary']};
}}

/* ===== LABELS ===== */
QLabel {{
    color: {colors['text_primary']};
    font-size: 10pt;
    background: transparent;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['surface']}, stop:1 {colors['background']});
    color: {colors['text_primary']};
    border-top: 1px solid {colors['border']};
    padding: 6px;
    font-size: 10pt;
}}

/* ===== SCROLL AREA (PDF Canvas) ===== */
QScrollArea {{
    background-color: {colors['canvas_bg']};
    border: none;
}}

QScrollBar:vertical {{
    background: {colors['background']};
    width: 14px;
    margin: 0;
    border-radius: 7px;
}}

QScrollBar::handle:vertical {{
    background: {colors['primary']};
    min-height: 30px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {colors['primary_light']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: {colors['background']};
    height: 14px;
    margin: 0;
    border-radius: 7px;
}}

QScrollBar::handle:horizontal {{
    background: {colors['primary']};
    min-width: 30px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {colors['primary_light']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ===== DIALOG BOXES ===== */
QDialog {{
    background-color: {colors['background']};
    color: {colors['text_primary']};
}}

QMessageBox {{
    background-color: {colors['surface']};
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    background: {colors['background']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
    text-align: center;
    color: {colors['text_primary']};
    font-weight: bold;
    height: 24px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors['primary']}, stop:1 {colors['primary_light']});
    border-radius: 6px;
    margin: 2px;
}}

/* ===== TOOLTIPS ===== */
QToolTip {{
    background-color: {colors['surface']};
    color: {colors['text_primary']};
    border: 1px solid {colors['primary']};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10pt;
}}
"""
