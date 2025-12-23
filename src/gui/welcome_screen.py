"""
Welcome screen component.

Displayed when no document is open, provides quick access to common actions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.constants import AppInfo, Icons, Fonts, Spacing
from utils.config import get_config


class WelcomeScreen(QWidget):
    """
    Welcome screen widget.
    
    Provides a professional landing page with quick access to file operations
    and recent documents. Follows modern application design patterns.
    """
    
    # Signals
    open_file_requested = Signal()
    recent_file_selected = Signal(str)
    show_tour_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize welcome screen.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config = get_config()
        
        self._setup_ui()
        self._load_recent_files()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(Spacing.XXLARGE)
        
        # Title section
        title_layout = self._create_title_section()
        layout.addLayout(title_layout)
        
        # Action buttons
        buttons_layout = self._create_action_buttons()
        layout.addLayout(buttons_layout)
        
        # Recent files section
        recent_section = self._create_recent_section()
        layout.addWidget(recent_section)
        
        # Hint at bottom
        hint_label = QLabel("Or drag & drop a PDF file here")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setProperty("secondary", True)
        layout.addWidget(hint_label)
        
        layout.addStretch()
    
    def _create_title_section(self) -> QVBoxLayout:
        """
        Create title section with app icon and name.
        
        Returns:
            Layout containing title elements
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(Spacing.MEDIUM)
        
        # App icon
        icon_label = QLabel(Icons.PAGES)
        icon_font = QFont()
        icon_font.setPointSize(64)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel(AppInfo.NAME)
        name_font = QFont()
        name_font.setPointSize(Fonts.SIZE_H1)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Description
        desc_label = QLabel(AppInfo.DESCRIPTION)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setProperty("secondary", True)
        layout.addWidget(desc_label)
        
        # Version
        version_label = QLabel(f"Version {AppInfo.VERSION} | Open Source")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setProperty("secondary", True)
        version_font = QFont()
        version_font.setPointSize(Fonts.SIZE_SMALL)
        version_label.setFont(version_font)
        layout.addWidget(version_label)
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """
        Create action buttons row.
        
        Returns:
            Layout containing action buttons
        """
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Open File button
        open_btn = QPushButton(f"{Icons.OPEN} Open File")
        open_btn.setMinimumSize(120, 80)
        open_btn.setToolTip("Open a PDF file (Ctrl+O)")
        open_btn.clicked.connect(self.open_file_requested.emit)
        self._style_action_button(open_btn)
        layout.addWidget(open_btn)
        
        # Recent Files button
        recent_btn = QPushButton(f"{Icons.BOOKMARKS} Recent Files")
        recent_btn.setMinimumSize(120, 80)
        recent_btn.setToolTip("View recently opened files")
        recent_btn.clicked.connect(self._scroll_to_recent)
        self._style_action_button(recent_btn)
        layout.addWidget(recent_btn)
        
        # Quick Tour button
        tour_btn = QPushButton(f"{Icons.INFO} Quick Tour")
        tour_btn.setMinimumSize(120, 80)
        tour_btn.setToolTip("Learn about the application")
        tour_btn.clicked.connect(self.show_tour_requested.emit)
        self._style_action_button(tour_btn)
        layout.addWidget(tour_btn)
        
        return layout
    
    def _style_action_button(self, button: QPushButton):
        """
        Apply styling to action button.
        
        Args:
            button: Button to style
        """
        button.setProperty("secondary", True)
        font = button.font()
        font.setPointSize(Fonts.SIZE_NORMAL)
        font.setWeight(QFont.Weight.DemiBold)
        button.setFont(font)
    
    def _create_recent_section(self) -> QWidget:
        """
        Create recent files section.
        
        Returns:
            Widget containing recent files list
        """
        container = QWidget()
        container.setMaximumWidth(500)
        layout = QVBoxLayout(container)
        layout.setSpacing(Spacing.SMALL)
        
        # Section title
        title_label = QLabel("Recent Documents")
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_H3)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Recent files list
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        self.recent_list.setAlternatingRowColors(True)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_file_clicked)
        layout.addWidget(self.recent_list)
        
        return container
    
    def _load_recent_files(self):
        """Load and display recent files."""
        recent_files = self.config.get_recent_files()
        
        self.recent_list.clear()
        
        if not recent_files:
            item = QListWidgetItem("No recent files")
            item.setFlags(Qt.NoItemFlags)
            self.recent_list.addItem(item)
            return
        
        for file_path in recent_files:
            # Extract filename from path
            filename = file_path.split('/')[-1]
            
            # Create list item
            item = QListWidgetItem(f"{Icons.PAGES} {filename}")
            item.setToolTip(file_path)
            item.setData(Qt.UserRole, file_path)
            self.recent_list.addItem(item)
    
    def _on_recent_file_clicked(self, item: QListWidgetItem):
        """
        Handle recent file selection.
        
        Args:
            item: Selected list item
        """
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.recent_file_selected.emit(file_path)
    
    def _scroll_to_recent(self):
        """Scroll to recent files section."""
        # Simple implementation: just focus the recent list
        self.recent_list.setFocus()
    
    def refresh_recent_files(self):
        """Refresh the recent files list."""
        self._load_recent_files()
    
    def set_drag_drop_enabled(self, enabled: bool):
        """
        Enable or disable drag and drop.
        
        Args:
            enabled: Whether to enable drag and drop
        """
        self.setAcceptDrops(enabled)
    
    def dragEnterEvent(self, event):
        """
        Handle drag enter event.
        
        Args:
            event: Drag event
        """
        if event.mimeData().hasUrls():
            # Check if any URL is a PDF file
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event):
        """
        Handle drop event.
        
        Args:
            event: Drop event
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.recent_file_selected.emit(file_path)
                break
