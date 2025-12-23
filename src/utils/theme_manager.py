"""
Theme management for the application.

Handles light/dark theme switching and stylesheet generation.
"""

from typing import Dict
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from .constants import Colors, Fonts, Spacing, Shadows, AnimationDurations


class ThemeManager:
    """
    Manages application themes and generates stylesheets.
    
    Provides dynamic theme switching between light and dark modes
    with consistent styling across all UI components.
    """
    
    def __init__(self):
        """Initialize theme manager with default theme."""
        self._current_theme = 'light'
        self._colors = Colors.LIGHT
    
    def get_current_theme(self) -> str:
        """
        Get current theme name.
        
        Returns:
            Theme name ('light' or 'dark')
        """
        return self._current_theme
    
    def set_theme(self, theme: str) -> None:
        """
        Set application theme.
        
        Args:
            theme: Theme name ('light' or 'dark')
        """
        self._current_theme = theme.lower()
        self._colors = Colors.DARK if self._current_theme == 'dark' else Colors.LIGHT
    
    def apply_theme(self, app: QApplication) -> None:
        """
        Apply current theme to application.
        
        Args:
            app: QApplication instance
        """
        # Generate and apply stylesheet
        stylesheet = self._generate_stylesheet()
        app.setStyleSheet(stylesheet)
        
        # Set application palette
        palette = self._generate_palette()
        app.setPalette(palette)
    
    def _generate_palette(self) -> QPalette:
        """
        Generate Qt palette for current theme.
        
        Returns:
            QPalette configured for current theme
        """
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(self._colors['background']))
        palette.setColor(QPalette.WindowText, QColor(self._colors['text_primary']))
        
        # Base colors
        palette.setColor(QPalette.Base, QColor(self._colors['background']))
        palette.setColor(QPalette.AlternateBase, QColor(self._colors['surface']))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(self._colors['text_primary']))
        palette.setColor(QPalette.BrightText, QColor(self._colors['text_primary']))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(self._colors['surface']))
        palette.setColor(QPalette.ButtonText, QColor(self._colors['text_primary']))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(self._colors['primary']))
        palette.setColor(QPalette.HighlightedText, QColor('#FFFFFF'))
        
        # Link colors
        palette.setColor(QPalette.Link, QColor(self._colors['text_link']))
        palette.setColor(QPalette.LinkVisited, QColor(self._colors['text_link']))
        
        return palette
    
    def _generate_stylesheet(self) -> str:
        """
        Generate complete stylesheet for current theme.
        
        Returns:
            CSS stylesheet as string
        """
        c = self._colors  # Shorthand for colors
        
        return f"""
        /* ===== Global Styles ===== */
        QWidget {{
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: {Fonts.SIZE_NORMAL}pt;
            color: {c['text_primary']};
            background-color: {c['background']};
        }}
        
        /* ===== Main Window ===== */
        QMainWindow {{
            background-color: {c['background']};
        }}
        
        QMainWindow::separator {{
            background-color: {c['border']};
            width: 1px;
            height: 1px;
        }}
        
        /* ===== Menu Bar ===== */
        QMenuBar {{
            background-color: {c['surface']};
            border-bottom: 1px solid {c['border']};
            padding: {Spacing.MICRO}px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: {Spacing.SMALL}px {Spacing.MEDIUM}px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {c['hover']};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {c['active']};
        }}
        
        /* ===== Menus ===== */
        QMenu {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: {Spacing.MICRO}px;
        }}
        
        QMenu::item {{
            padding: {Spacing.SMALL}px {Spacing.LARGE}px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {c['hover']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {c['divider']};
            margin: {Spacing.MICRO}px 0px;
        }}
        
        /* ===== Toolbar ===== */
        QToolBar {{
            background-color: {c['surface']};
            border: none;
            border-bottom: 1px solid {c['border']};
            spacing: {Spacing.SMALL}px;
            padding: {Spacing.SMALL}px;
        }}
        
        QToolBar::separator {{
            background-color: {c['divider']};
            width: 1px;
            margin: {Spacing.MICRO}px {Spacing.SMALL}px;
        }}
        
        /* ===== Tool Buttons ===== */
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: {Spacing.SMALL}px;
            min-width: 32px;
            min-height: 32px;
        }}
        
        QToolButton:hover {{
            background-color: {c['hover']};
        }}
        
        QToolButton:pressed {{
            background-color: {c['active']};
        }}
        
        QToolButton:checked {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-bottom: 2px solid {c['primary']};
            border-radius: 4px 4px 0px 0px;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}
        
        QToolButton:disabled {{
            color: {c['text_disabled']};
        }}
        
        /* ===== Push Buttons ===== */
        QPushButton {{
            background-color: {c['primary']};
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: {Spacing.SMALL}px {Spacing.MEDIUM}px;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}
        
        QPushButton:hover {{
            background-color: #106EBE;
        }}
        
        QPushButton:pressed {{
            background-color: #005A9E;
        }}
        
        QPushButton:disabled {{
            background-color: {c['surface']};
            color: {c['text_disabled']};
        }}
        
        QPushButton[secondary="true"] {{
            background-color: {c['surface']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
        }}
        
        QPushButton[secondary="true"]:hover {{
            background-color: {c['hover']};
        }}
        
        QPushButton[secondary="true"]:pressed {{
            background-color: {c['active']};
        }}
        
        /* ===== Dock Widgets (Sidebars) ===== */
        QDockWidget {{
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
            border: none;
        }}
        
        QDockWidget::title {{
            background-color: {c['surface']};
            border-bottom: 1px solid {c['border']};
            padding: {Spacing.SMALL}px;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}
        
        QDockWidget > QWidget {{
            background-color: {c['surface']};
        }}
        
        /* ===== Tab Widget ===== */
        QTabWidget::pane {{
            border: 1px solid {c['border']};
            border-radius: 4px;
            background-color: {c['background']};
        }}
        
        QTabBar::tab {{
            background-color: {c['surface']};
            color: {c['text_secondary']};
            border: 1px solid {c['border']};
            border-bottom: none;
            padding: {Spacing.SMALL}px {Spacing.MEDIUM}px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c['background']};
            color: {c['text_primary']};
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c['hover']};
        }}
        
        /* ===== Scroll Bar ===== */
        QScrollBar:vertical {{
            background-color: {c['surface']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['border']};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['secondary']};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {c['surface']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {c['border']};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {c['secondary']};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* ===== Line Edit ===== */
        QLineEdit {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: {Spacing.SMALL}px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {c['primary']};
        }}
        
        QLineEdit:disabled {{
            background-color: {c['surface']};
            color: {c['text_disabled']};
        }}
        
        /* ===== Text Edit ===== */
        QTextEdit, QPlainTextEdit {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
        }}
        
        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {c['primary']};
        }}
        
        /* ===== Combo Box ===== */
        QComboBox {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: {Spacing.SMALL}px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border-color: {c['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            padding-right: {Spacing.SMALL}px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            selection-background-color: {c['hover']};
        }}
        
        /* ===== Spin Box ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: {Spacing.SMALL}px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c['primary']};
        }}
        
        /* ===== Slider ===== */
        QSlider::groove:horizontal {{
            background-color: {c['border']};
            height: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {c['primary']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: #106EBE;
        }}
        
        /* ===== Status Bar ===== */
        QStatusBar {{
            background-color: {c['surface']};
            border-top: 1px solid {c['border']};
            color: {c['text_secondary']};
        }}
        
        QStatusBar::item {{
            border: none;
        }}
        
        /* ===== Labels ===== */
        QLabel {{
            background-color: transparent;
            color: {c['text_primary']};
        }}
        
        QLabel[heading="true"] {{
            font-size: {Fonts.SIZE_H3}pt;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}
        
        QLabel[secondary="true"] {{
            color: {c['text_secondary']};
        }}
        
        /* ===== List Widget ===== */
        QListWidget {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
        }}
        
        QListWidget::item {{
            padding: {Spacing.SMALL}px;
            border-radius: 4px;
        }}
        
        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}
        
        QListWidget::item:selected {{
            background-color: {c['primary']};
            color: #FFFFFF;
        }}
        
        /* ===== Tree Widget ===== */
        QTreeWidget {{
            background-color: {c['background']};
            border: 1px solid {c['border']};
            border-radius: 4px;
        }}
        
        QTreeWidget::item {{
            padding: {Spacing.MICRO}px;
        }}
        
        QTreeWidget::item:hover {{
            background-color: {c['hover']};
        }}
        
        QTreeWidget::item:selected {{
            background-color: {c['primary']};
            color: #FFFFFF;
        }}
        
        /* ===== Splitter ===== */
        QSplitter::handle {{
            background-color: {c['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        
        /* ===== Dialog ===== */
        QDialog {{
            background-color: {c['background']};
        }}
        
        /* ===== Message Box ===== */
        QMessageBox {{
            background-color: {c['background']};
        }}
        
        QMessageBox QLabel {{
            color: {c['text_primary']};
        }}
        
        /* ===== Tool Tip ===== */
        QToolTip {{
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 6px 10px;
        }}
        """
    
    def get_colors(self) -> Dict[str, str]:
        """
        Get current theme color palette.
        
        Returns:
            Dictionary of color values
        """
        return self._colors.copy()


# Global theme manager instance
_theme_manager_instance = None


def get_theme_manager() -> ThemeManager:
    """
    Get global theme manager instance.
    
    Returns:
        ThemeManager instance
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance
