"""
Toolbar component with ribbon interface.

Provides organized access to tools through tabbed interface.
"""

from PySide6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QVBoxLayout, QToolButton, 
    QLabel, QSizePolicy, QTabWidget, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.constants import Icons, Spacing, Fonts
from utils.icon_manager import get_icon


class Toolbar(QToolBar):
    """
    Application toolbar with ribbon-style interface.
    
    Organizes tools into tabs (Home, Edit, Annotate, Page, Convert).
    Each tab contains grouped buttons for related operations.
    """
    
    # Signals
    open_file_requested = Signal()
    save_file_requested = Signal()
    print_requested = Signal()
    
    undo_requested = Signal()
    redo_requested = Signal()
    
    # Edit actions
    cut_requested = Signal()
    copy_requested = Signal()
    paste_requested = Signal()
    select_all_requested = Signal()
    delete_requested = Signal()
    
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    rotate_requested = Signal()
    
    select_text_toggled = Signal(bool)  # Emitted when select text mode is toggled
    
    # Annotation signals
    highlight_mode_toggled = Signal(bool)  # Emitted when highlight mode is toggled
    annotation_color_changed = Signal(tuple)  # Emitted when annotation color changes (RGB 0-255)
    
    # OCR signal
    quick_ocr_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize toolbar.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Main Toolbar", parent)
        
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(self.iconSize() * 1.2)  # Slightly larger icons
        
        self._document_actions = []
        self._current_tab = "Home"
        self._select_text_button = None  # Reference to select text toggle button
        
        self._create_toolbar()
    
    def _create_toolbar(self):
        """Create the complete toolbar with tab selector and tool groups."""
        # Create container widget
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(Spacing.SMALL, Spacing.SMALL, Spacing.SMALL, Spacing.SMALL)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Tab selector buttons
        self.tab_selector = self._create_tab_selector()
        layout.addWidget(self.tab_selector)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # Tool groups container (will switch based on tab)
        self.tools_container = QWidget()
        self.tools_layout = QHBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(Spacing.MEDIUM)
        layout.addWidget(self.tools_container)
        
        # Create all tab contents
        self.tab_contents = {
            "Home": self._create_home_tools(),
            "Edit": self._create_edit_tools(),
            "Annotate": self._create_annotate_tools(),
            "Page": self._create_page_tools(),
            "Convert": self._create_convert_tools()
        }
        
        # Show Home tab by default
        self._switch_tab("Home")
        
        # Add spacer
        layout.addStretch()
        
        self.addWidget(container)
    
    def _create_tab_selector(self) -> QWidget:
        """
        Create tab selector button group (horizontal ribbon-style).
        
        Returns:
            Widget containing tab buttons
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Button group for exclusive selection
        self.tab_buttons = QButtonGroup(self)
        self.tab_buttons.setExclusive(True)
        
        # Create buttons for each tab with professional styling
        tabs = ["Home", "Edit", "Annotate", "Page", "Convert"]
        for tab in tabs:
            btn = QToolButton()
            btn.setText(tab)
            btn.setCheckable(True)
            btn.setAutoRaise(False)
            btn.setMinimumWidth(80)
            btn.setMinimumHeight(32)
            btn.clicked.connect(lambda checked, t=tab: self._switch_tab(t))
            
            # Apply professional tab button styling
            btn.setStyleSheet("""
                QToolButton {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    border-bottom: 3px solid #d0d0d0;
                    border-radius: 4px 4px 0px 0px;
                    padding: 6px 16px;
                    font-size: 12px;
                    font-weight: 600;
                    color: #606060;
                }
                QToolButton:checked {
                    background-color: #ffffff;
                    border-bottom: 3px solid #0078d4;
                    color: #0078d4;
                }
                QToolButton:hover {
                    background-color: #e8e8e8;
                    color: #0078d4;
                }
            """)
            
            if tab == "Home":
                btn.setChecked(True)
            
            self.tab_buttons.addButton(btn)
            layout.addWidget(btn)
        
        return widget
    
    def _create_separator(self) -> QWidget:
        """
        Create vertical separator.
        
        Returns:
            Separator widget
        """
        separator = QWidget()
        separator.setFixedWidth(2)
        separator.setProperty("separator", True)
        return separator
    
    def _create_home_tools(self) -> QWidget:
        """
        Create Home tab tools.
        
        Returns:
            Widget containing Home tools
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)
        
        # File group
        file_group = self._create_tool_group("File", [
            ("Open", "Open PDF file (Ctrl+O)", self.open_file_requested.emit, False),
            ("Save", "Save document (Ctrl+S)", self.save_file_requested.emit, True),
            ("Print", "Print document (Ctrl+P)", self.print_requested.emit, True),
        ])
        layout.addWidget(file_group)
        
        layout.addWidget(self._create_separator())
        
        # View group
        view_group = self._create_tool_group("View", [
            ("Zoom In", "Zoom in (Ctrl++)", self.zoom_in_requested.emit, True),
            ("Zoom Out", "Zoom out (Ctrl+-)", self.zoom_out_requested.emit, True),
            ("Fit Page", "Fit page to window (Ctrl+0)", lambda: None, True),
        ])
        layout.addWidget(view_group)
        
        layout.addWidget(self._create_separator())
        
        # Rotate group
        rotate_group = self._create_tool_group("Rotate", [
            ("Rotate", "Rotate page (Ctrl+R)", self.rotate_requested.emit, True),
        ])
        layout.addWidget(rotate_group)
        
        return widget
    
    def _create_edit_tools(self) -> QWidget:
        """
        Create Edit tab tools.
        
        Returns:
            Widget containing Edit tools
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Mode selection group with toggle button
        mode_group = self._create_mode_selection_group()
        layout.addWidget(mode_group)
        
        layout.addWidget(self._create_separator())
        
        # Undo/Redo group
        history_group = self._create_tool_group("History", [
            ("Undo", "Undo (Ctrl+Z)", self.undo_requested.emit, True),
            ("Redo", "Redo (Ctrl+Y)", self.redo_requested.emit, True),
        ])
        layout.addWidget(history_group)
        
        layout.addWidget(self._create_separator())
        
        # Clipboard group
        clipboard_group = self._create_tool_group("Clipboard", [
            ("Cut", "Cut selected text (Ctrl+X)", self.cut_requested.emit, True),
            ("Copy", "Copy selected text or image (Ctrl+C)", self.copy_requested.emit, True),
            ("Paste", "Paste from clipboard (Ctrl+V)", self.paste_requested.emit, True),
        ])
        layout.addWidget(clipboard_group)
        
        layout.addWidget(self._create_separator())
        
        # Selection group
        selection_group = self._create_tool_group("Selection", [
            ("Select All", "Select all text on page (Ctrl+A)", self.select_all_requested.emit, True),
            ("Delete", "Delete selected content (Del)", self.delete_requested.emit, True),
        ])
        layout.addWidget(selection_group)
        
        return widget
    
    def _create_mode_selection_group(self) -> QWidget:
        """
        Create mode selection group with Select Text toggle button.
        
        Returns:
            Widget containing mode selection tools
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Group title
        title_label = QLabel("Mode")
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_SMALL)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Select Text toggle button with professional styling
        self._select_text_button = QToolButton()
        self._select_text_button.setText("Select Text")
        self._select_text_button.setToolTip(
            "Toggle text selection mode\n\n"
            "When ON: Click and drag to select text\n"
            "When OFF: Click and drag to pan\n"
            "Tip: Hold Spacebar for temporary pan mode"
        )
        self._select_text_button.setCheckable(True)
        self._select_text_button.setChecked(False)  # Default to pan mode
        self._select_text_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._select_text_button.setAutoRaise(False)
        self._select_text_button.setMinimumWidth(85)
        self._select_text_button.setMinimumHeight(40)
        self._select_text_button.toggled.connect(self.select_text_toggled.emit)
        
        # Apply toggle button styling
        self._select_text_button.setStyleSheet("""
            QToolButton {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 500;
                color: #333333;
            }
            QToolButton:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                color: white;
                font-weight: 600;
            }
            QToolButton:hover {
                background-color: #0078d4;
                border-color: #0078d4;
                color: white;
            }
            QToolButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
            QToolButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
                border-color: #e0e0e0;
            }
        """)
        
        # Add to document actions
        self._document_actions.append(self._select_text_button)
        
        layout.addWidget(self._select_text_button)
        
        return widget
    
    def _create_annotate_tools(self) -> QWidget:
        """
        Create Annotate tab tools with working highlight and colors.
        
        Returns:
            Widget containing Annotate tools
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Highlight group with toggle button and color picker
        highlight_group = self._create_highlight_group()
        layout.addWidget(highlight_group)
        
        layout.addWidget(self._create_separator())
        
        # Markup group (coming soon features)
        markup_group = self._create_tool_group("More Markup", [
            ("Underline", "Underline text (Coming soon)", lambda: self._show_coming_soon("Underline"), True),
            ("Strikeout", "Strikethrough text (Coming soon)", lambda: self._show_coming_soon("Strikethrough"), True),
        ])
        layout.addWidget(markup_group)
        
        layout.addWidget(self._create_separator())
        
        # Comments group
        comments_group = self._create_tool_group("Comments", [
            ("Comment", "Add comment (Coming soon)", lambda: self._show_coming_soon("Comment"), True),
            ("Note", "Add sticky note (Coming soon)", lambda: self._show_coming_soon("Note"), True),
        ])
        layout.addWidget(comments_group)
        
        return widget
    
    def _create_highlight_group(self) -> QWidget:
        """
        Create highlight group with toggle button and color picker.
        
        Returns:
            Widget containing highlight tools
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Group title
        title_label = QLabel("Highlight")
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_SMALL)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Container for button and colors
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Spacing.SMALL)
        
        # Highlight toggle button with professional styling
        self._highlight_button = QToolButton()
        self._highlight_button.setText("Highlight")
        self._highlight_button.setToolTip(
            "Toggle highlight mode\n\n"
            "When ON: Select text to highlight\n"
            "Press ESC to cancel\n"
            "Highlights are saved IN the PDF!"
        )
        self._highlight_button.setCheckable(True)
        self._highlight_button.setChecked(False)
        self._highlight_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._highlight_button.setAutoRaise(False)
        self._highlight_button.setMinimumWidth(75)
        self._highlight_button.setMinimumHeight(40)
        self._highlight_button.toggled.connect(self._on_highlight_toggled)
        
        # Apply professional toggle button styling
        self._highlight_button.setStyleSheet("""
            QToolButton {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 500;
                color: #333333;
            }
            QToolButton:checked {
                background-color: #FFB900;
                border-color: #FFB900;
                color: #333333;
                font-weight: 600;
            }
            QToolButton:hover {
                background-color: #0078d4;
                border-color: #0078d4;
                color: white;
            }
            QToolButton:checked:hover {
                background-color: #FFA500;
                border-color: #FFA500;
            }
            QToolButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
            QToolButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
                border-color: #e0e0e0;
            }
        """)
        
        self._document_actions.append(self._highlight_button)
        content_layout.addWidget(self._highlight_button)
        
        # Color picker (4 colors)
        colors_layout = QVBoxLayout()
        colors_layout.setSpacing(2)
        
        # Row 1: Yellow, Green
        row1 = QHBoxLayout()
        row1.setSpacing(2)
        self._color_yellow = self._create_color_button((255, 255, 0), "Yellow", True)  # Default
        self._color_green = self._create_color_button((0, 255, 0), "Green", False)
        row1.addWidget(self._color_yellow)
        row1.addWidget(self._color_green)
        colors_layout.addLayout(row1)
        
        # Row 2: Blue, Pink
        row2 = QHBoxLayout()
        row2.setSpacing(2)
        self._color_blue = self._create_color_button((0, 191, 255), "Blue", False)
        self._color_pink = self._create_color_button((255, 105, 180), "Pink", False)
        row2.addWidget(self._color_blue)
        row2.addWidget(self._color_pink)
        colors_layout.addLayout(row2)
        
        content_layout.addLayout(colors_layout)
        
        layout.addLayout(content_layout)
        
        # Button group for exclusive color selection
        self._color_button_group = QButtonGroup(self)
        self._color_button_group.setExclusive(True)
        self._color_button_group.addButton(self._color_yellow)
        self._color_button_group.addButton(self._color_green)
        self._color_button_group.addButton(self._color_blue)
        self._color_button_group.addButton(self._color_pink)
        
        return widget
    
    def _create_color_button(self, color_rgb: tuple, name: str, checked: bool) -> QToolButton:
        """
        Create a color selection button.
        
        Args:
            color_rgb: RGB tuple 0-255
            name: Color name for tooltip
            checked: Whether button starts checked
            
        Returns:
            Color button
        """
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setAutoRaise(False)
        btn.setFixedSize(22, 22)
        btn.setToolTip(f"{name} highlight color")
        
        # Set button color using stylesheet
        r, g, b = color_rgb
        btn.setStyleSheet(f"""
            QToolButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #888;
                border-radius: 3px;
            }}
            QToolButton:checked {{
                border: 2px solid #000;
                border-width: 3px;
            }}
            QToolButton:hover {{
                border: 2px solid #000;
            }}
        """)
        
        # Connect to color change
        btn.clicked.connect(lambda: self._on_color_selected(color_rgb))
        
        # Mark as document action
        self._document_actions.append(btn)
        
        return btn
    
    def _on_highlight_toggled(self, checked: bool):
        """
        Handle highlight button toggle.
        
        Args:
            checked: Whether button is checked
        """
        self.highlight_mode_toggled.emit(checked)
    
    def _on_color_selected(self, color_rgb: tuple):
        """
        Handle color button click.
        
        Args:
            color_rgb: RGB tuple 0-255
        """
        self.annotation_color_changed.emit(color_rgb)
    
    def _create_page_tools(self) -> QWidget:
        """
        Create Page tab tools.
        
        Returns:
            Widget containing Page tools
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Organize group
        organize_group = self._create_tool_group("Organize", [
            ("Insert", "Insert page", lambda: self._show_coming_soon("Insert Page"), True),
            ("Delete", "Delete page", lambda: self._show_coming_soon("Delete Page"), True),
            ("Extract", "Extract pages", lambda: self._show_coming_soon("Extract Pages"), True),
        ])
        layout.addWidget(organize_group)
        
        layout.addWidget(self._create_separator())
        
        # Manipulate group
        manipulate_group = self._create_tool_group("Manipulate", [
            ("Rotate", "Rotate page", self.rotate_requested.emit, True),
            ("Crop", "Crop page", lambda: self._show_coming_soon("Crop Page"), True),
            ("Reorder", "Reorder pages", lambda: self._show_coming_soon("Reorder Pages"), True),
        ])
        layout.addWidget(manipulate_group)
        
        return widget
    
    def _create_convert_tools(self) -> QWidget:
        """
        Create Convert tab tools.
        
        Returns:
            Widget containing Convert tools
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Export group
        export_group = self._create_tool_group("Export", [
            ("To Word", "Export to Word", lambda: self._show_coming_soon("Export to Word"), True),
            ("To Excel", "Export to Excel", lambda: self._show_coming_soon("Export to Excel"), True),
            ("To Image", "Export to Image", lambda: self._show_coming_soon("Export to Image"), True),
        ])
        layout.addWidget(export_group)
        
        layout.addWidget(self._create_separator())
        
        # Import group
        import_group = self._create_tool_group("Import", [
            ("From Word", "Import Word doc", lambda: self._show_coming_soon("Import Word"), True),
            ("From Image", "Import image", lambda: self._show_coming_soon("Import Image"), True),
        ])
        layout.addWidget(import_group)
        
        layout.addWidget(self._create_separator())
        
        # OCR group with working button
        ocr_group = self._create_ocr_group()
        layout.addWidget(ocr_group)
        
        return widget
    
    def _create_ocr_group(self) -> QWidget:
        """
        Create OCR tool group with working button.
        
        Returns:
            Widget containing OCR tools
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Group title
        title_label = QLabel("OCR")
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_SMALL)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # OCR button
        ocr_btn = QToolButton()
        ocr_btn.setText("Scan Text")
        ocr_btn.setIcon(get_icon('file_text', 20))
        ocr_btn.setIconSize(ocr_btn.iconSize() * 1.2)
        ocr_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        ocr_btn.setToolTip("Quick OCR - Convert scanned pages to searchable text (Ctrl+Shift+O)")
        ocr_btn.setAutoRaise(False)
        ocr_btn.setMinimumWidth(90)
        ocr_btn.setMinimumHeight(40)
        ocr_btn.clicked.connect(self.quick_ocr_requested.emit)
        
        # Apply professional button styling
        ocr_btn.setStyleSheet("""
            QToolButton {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 500;
                color: #333333;
            }
            QToolButton:hover {
                background-color: #0078d4;
                border-color: #0078d4;
                color: white;
            }
            QToolButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
            QToolButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
                border-color: #e0e0e0;
            }
        """)
        
        self._document_actions.append(ocr_btn)
        layout.addWidget(ocr_btn)
        
        return widget
    
    def _create_tool_group(self, title: str, tools: list) -> QWidget:
        """
        Create a group of tool buttons with professional styling and SVG icons.
        
        Args:
            title: Group title
            tools: List of (text, tooltip, callback, is_document_action) tuples
        
        Returns:
            Widget containing the tool group
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Group title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(Fonts.SIZE_SMALL)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Tool buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.SMALL)
        
        # Icon name mapping (button text -> icon name)
        icon_mapping = {
            'Open': 'file_open',
            'Save': 'save',
            'Print': 'print',
            'Zoom In': 'zoom_in',
            'Zoom Out': 'zoom_out',
            'Fit Page': 'zoom_out',
            'Rotate': 'rotate',
            'Undo': 'undo',
            'Redo': 'redo',
            'Cut': 'cut',
            'Copy': 'copy',
            'Paste': 'paste',
            'Select All': 'select_all',
            'Delete': 'delete',
            'Underline': 'highlight',
            'Strikeout': 'highlight',
            'Comment': 'comment',
            'Note': 'note',
            'Insert': 'pages',
            'Extract': 'pages',
            'Crop': 'pages',
            'Reorder': 'pages',
            'To Word': 'save',
            'To Excel': 'save',
            'To Image': 'save',
            'From Word': 'file_open',
            'From Image': 'file_open',
            'Scan Text': 'search',
        }
        
        for text, tooltip, callback, is_doc_action in tools:
            btn = QToolButton()
            btn.setText(text)
            
            # Add SVG icon if available
            icon_name = icon_mapping.get(text)
            if icon_name:
                icon = get_icon(icon_name, 20)
                btn.setIcon(icon)
                btn.setIconSize(btn.iconSize() * 1.2)
                btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            else:
                btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            
            btn.setToolTip(tooltip)
            btn.setAutoRaise(False)
            btn.setMinimumWidth(70)
            btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            
            # Apply professional button styling
            btn.setStyleSheet("""
                QToolButton {
                    background-color: #f8f8f8;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 11px;
                    font-weight: 500;
                    color: #333333;
                }
                QToolButton:hover {
                    background-color: #0078d4;
                    border-color: #0078d4;
                    color: white;
                }
                QToolButton:pressed {
                    background-color: #005a9e;
                    border-color: #005a9e;
                }
                QToolButton:disabled {
                    background-color: #f0f0f0;
                    color: #a0a0a0;
                    border-color: #e0e0e0;
                }
            """)
            
            if is_doc_action:
                self._document_actions.append(btn)
            
            buttons_layout.addWidget(btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _switch_tab(self, tab_name: str):
        """
        Switch to a different tool tab.
        
        Args:
            tab_name: Name of tab to switch to
        """
        self._current_tab = tab_name
        
        # Clear current tools
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add new tools
        if tab_name in self.tab_contents:
            self.tools_layout.addWidget(self.tab_contents[tab_name])
            self.tab_contents[tab_name].show()
    
    def _show_coming_soon(self, feature: str):
        """
        Show coming soon message.
        
        Args:
            feature: Feature name
        """
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Coming Soon",
            f"{feature} will be available in Phase 2.\n\n"
            "This feature is part of our development roadmap."
        )
    
    def set_document_actions_enabled(self, enabled: bool):
        """
        Enable or disable document-specific actions.
        
        Args:
            enabled: Whether to enable actions
        """
        for action in self._document_actions:
            action.setEnabled(enabled)
    
    def set_select_text_mode(self, enabled: bool):
        """
        Set the select text button state (for syncing with ContentArea).
        
        Args:
            enabled: True to check the button, False to uncheck
        """
        if self._select_text_button:
            # Block signals to avoid circular updates
            self._select_text_button.blockSignals(True)
            self._select_text_button.setChecked(enabled)
            self._select_text_button.blockSignals(False)
