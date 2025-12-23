"""
Menu bar component.

Provides main application menus with all actions and keyboard shortcuts.
"""

from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal, Qt

from utils.constants import Icons
from utils.icon_manager import get_icon


class MenuBar(QMenuBar):
    """
    Application menu bar.
    
    Provides organized access to all application features through traditional menus.
    Emits signals for various actions to be handled by the main window.
    """
    
    # Signals for menu actions
    open_file_requested = Signal()
    close_file_requested = Signal()
    save_file_requested = Signal()
    save_as_requested = Signal()
    print_requested = Signal()
    exit_requested = Signal()
    
    undo_requested = Signal()
    redo_requested = Signal()
    copy_requested = Signal()  # Copy selected content (text or image)
    
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    fit_page_requested = Signal()
    fit_width_requested = Signal()
    
    theme_toggle_requested = Signal()
    fullscreen_requested = Signal()
    
    # OCR signals
    quick_ocr_requested = Signal()
    advanced_ocr_requested = Signal()
    ocr_settings_requested = Signal()
    export_ocr_text_requested = Signal()
    export_ocr_word_requested = Signal()
    export_ocr_excel_requested = Signal()
    
    about_requested = Signal()
    help_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize menu bar with all menus.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store actions that need to be enabled/disabled based on document state
        self._document_actions = []
        
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_document_menu()
        self._create_page_menu()
        self._create_annotate_menu()
        self._create_tools_menu()
        self._create_convert_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create File menu with file operations."""
        file_menu = self.addMenu("&File")
        
        # Open
        open_action = QAction(f"{Icons.OPEN} &Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open a PDF file")
        open_action.triggered.connect(self.open_file_requested.emit)
        file_menu.addAction(open_action)
        
        # Recent Files submenu
        recent_menu = file_menu.addMenu("Recent Files")
        recent_menu.setEnabled(False)  # Will be populated dynamically
        
        file_menu.addSeparator()
        
        # Close
        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence.Close)
        close_action.setStatusTip("Close current document")
        close_action.triggered.connect(self.close_file_requested.emit)
        file_menu.addAction(close_action)
        self._document_actions.append(close_action)
        
        file_menu.addSeparator()
        
        # Save
        save_action = QAction(f"{Icons.SAVE} &Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Save current document")
        save_action.triggered.connect(self.save_file_requested.emit)
        file_menu.addAction(save_action)
        self._document_actions.append(save_action)
        
        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Save document with a new name")
        save_as_action.triggered.connect(self.save_as_requested.emit)
        file_menu.addAction(save_as_action)
        self._document_actions.append(save_as_action)
        
        file_menu.addSeparator()
        
        # Print
        print_action = QAction(f"{Icons.PRINT} &Print...", self)
        print_action.setShortcut(QKeySequence.Print)
        print_action.setStatusTip("Print current document")
        print_action.triggered.connect(self.print_requested.emit)
        file_menu.addAction(print_action)
        self._document_actions.append(print_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.exit_requested.emit)
        file_menu.addAction(exit_action)
    
    def _create_edit_menu(self):
        """Create Edit menu with editing operations."""
        edit_menu = self.addMenu("&Edit")
        
        # Undo
        undo_action = QAction(f"{Icons.UNDO} &Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setStatusTip("Undo last action")
        undo_action.triggered.connect(self.undo_requested.emit)
        edit_menu.addAction(undo_action)
        self._document_actions.append(undo_action)
        
        # Redo
        redo_action = QAction(f"{Icons.REDO} &Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.setStatusTip("Redo last undone action")
        redo_action.triggered.connect(self.redo_requested.emit)
        edit_menu.addAction(redo_action)
        self._document_actions.append(redo_action)
        
        edit_menu.addSeparator()
        
        # Cut
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.setStatusTip("Cut selected content")
        cut_action.triggered.connect(lambda: self._show_coming_soon("Cut"))
        edit_menu.addAction(cut_action)
        self._document_actions.append(cut_action)
        
        # Copy
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setStatusTip("Copy selected content")
        copy_action.triggered.connect(self.copy_requested.emit)
        edit_menu.addAction(copy_action)
        self._document_actions.append(copy_action)
        
        # Paste
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.setStatusTip("Paste content from clipboard")
        paste_action.triggered.connect(lambda: self._show_coming_soon("Paste"))
        edit_menu.addAction(paste_action)
        self._document_actions.append(paste_action)
        
        # Delete
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.setStatusTip("Delete selected content")
        delete_action.triggered.connect(lambda: self._show_coming_soon("Delete"))
        edit_menu.addAction(delete_action)
        self._document_actions.append(delete_action)
        
        edit_menu.addSeparator()
        
        # Select All
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.setStatusTip("Select all content")
        select_all_action.triggered.connect(lambda: self._show_coming_soon("Select All"))
        edit_menu.addAction(select_all_action)
        self._document_actions.append(select_all_action)
    
    def _create_view_menu(self):
        """Create View menu with view options."""
        view_menu = self.addMenu("&View")
        
        # Zoom In
        zoom_in_action = QAction(f"{Icons.ZOOM_IN} Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.setStatusTip("Zoom in")
        zoom_in_action.triggered.connect(self.zoom_in_requested.emit)
        view_menu.addAction(zoom_in_action)
        self._document_actions.append(zoom_in_action)
        
        # Zoom Out
        zoom_out_action = QAction(f"{Icons.ZOOM_OUT} Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.setStatusTip("Zoom out")
        zoom_out_action.triggered.connect(self.zoom_out_requested.emit)
        view_menu.addAction(zoom_out_action)
        self._document_actions.append(zoom_out_action)
        
        # Fit Page
        fit_page_action = QAction(f"{Icons.FIT_PAGE} Fit &Page", self)
        fit_page_action.setShortcut("Ctrl+0")
        fit_page_action.setStatusTip("Fit page to window")
        fit_page_action.triggered.connect(self.fit_page_requested.emit)
        view_menu.addAction(fit_page_action)
        self._document_actions.append(fit_page_action)
        
        # Fit Width
        fit_width_action = QAction("Fit &Width", self)
        fit_width_action.setShortcut("Ctrl+2")
        fit_width_action.setStatusTip("Fit page width to window")
        fit_width_action.triggered.connect(self.fit_width_requested.emit)
        view_menu.addAction(fit_width_action)
        self._document_actions.append(fit_width_action)
        
        view_menu.addSeparator()
        
        # Rotate
        rotate_action = QAction(f"{Icons.ROTATE} &Rotate Page", self)
        rotate_action.setShortcut("Ctrl+R")
        rotate_action.setStatusTip("Rotate current page")
        rotate_action.triggered.connect(lambda: self._show_coming_soon("Rotate"))
        view_menu.addAction(rotate_action)
        self._document_actions.append(rotate_action)
        
        view_menu.addSeparator()
        
        # View Mode submenu
        view_mode_menu = view_menu.addMenu("View Mode")
        
        single_page_action = QAction("Single Page", self)
        single_page_action.triggered.connect(lambda: self._show_coming_soon("Single Page View"))
        view_mode_menu.addAction(single_page_action)
        self._document_actions.append(single_page_action)
        
        continuous_action = QAction("Continuous", self)
        continuous_action.triggered.connect(lambda: self._show_coming_soon("Continuous View"))
        view_mode_menu.addAction(continuous_action)
        self._document_actions.append(continuous_action)
        
        two_page_action = QAction("Two-Page Spread", self)
        two_page_action.triggered.connect(lambda: self._show_coming_soon("Two-Page View"))
        view_mode_menu.addAction(two_page_action)
        self._document_actions.append(two_page_action)
        
        view_menu.addSeparator()
        
        # Panels submenu
        panels_menu = view_menu.addMenu("Panels")
        
        left_panel_action = QAction("Left Sidebar", self)
        left_panel_action.setCheckable(True)
        left_panel_action.setChecked(True)
        left_panel_action.triggered.connect(lambda checked: self._toggle_panel("left", checked))
        panels_menu.addAction(left_panel_action)
        
        right_panel_action = QAction("Right Sidebar", self)
        right_panel_action.setCheckable(True)
        right_panel_action.setChecked(True)
        right_panel_action.triggered.connect(lambda checked: self._toggle_panel("right", checked))
        panels_menu.addAction(right_panel_action)
        
        view_menu.addSeparator()
        
        # Theme Toggle
        theme_action = QAction("Toggle Dark/Light Theme", self)
        theme_action.setShortcut("Ctrl+Shift+T")
        theme_action.setStatusTip("Switch between light and dark themes")
        theme_action.triggered.connect(self.theme_toggle_requested.emit)
        view_menu.addAction(theme_action)
        
        # Full Screen
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setStatusTip("Toggle full screen mode")
        fullscreen_action.triggered.connect(self.fullscreen_requested.emit)
        view_menu.addAction(fullscreen_action)
    
    def _create_document_menu(self):
        """Create Document menu with document-level operations."""
        doc_menu = self.addMenu("&Document")
        
        # Properties
        properties_action = QAction(f"{Icons.PROPERTIES} &Properties...", self)
        properties_action.setShortcut("Ctrl+D")
        properties_action.setStatusTip("View and edit document properties")
        properties_action.triggered.connect(lambda: self._show_coming_soon("Document Properties"))
        doc_menu.addAction(properties_action)
        self._document_actions.append(properties_action)
        
        # Security
        security_action = QAction(f"{Icons.SECURITY} Se&curity...", self)
        security_action.setStatusTip("Document security settings")
        security_action.triggered.connect(lambda: self._show_coming_soon("Security Settings"))
        doc_menu.addAction(security_action)
        self._document_actions.append(security_action)
        
        doc_menu.addSeparator()
        
        # Optimize Size
        optimize_action = QAction("&Optimize Size...", self)
        optimize_action.setStatusTip("Optimize document file size")
        optimize_action.triggered.connect(lambda: self._show_coming_soon("Optimize Size"))
        doc_menu.addAction(optimize_action)
        self._document_actions.append(optimize_action)
        
        doc_menu.addSeparator()
        
        # Merge PDFs
        merge_action = QAction("&Merge PDFs... [Coming Soon]", self)
        merge_action.setStatusTip("Merge multiple PDF files (Phase 2)")
        merge_action.triggered.connect(lambda: self._show_coming_soon("Merge PDFs"))
        doc_menu.addAction(merge_action)
        
        # Split PDF
        split_action = QAction("&Split PDF... [Coming Soon]", self)
        split_action.setStatusTip("Split PDF into multiple files (Phase 2)")
        split_action.triggered.connect(lambda: self._show_coming_soon("Split PDF"))
        doc_menu.addAction(split_action)
    
    def _create_page_menu(self):
        """Create Page menu with page operations."""
        page_menu = self.addMenu("&Page")
        
        # Insert Page
        insert_action = QAction("&Insert Page... [Coming Soon]", self)
        insert_action.setStatusTip("Insert a new page (Phase 2)")
        insert_action.triggered.connect(lambda: self._show_coming_soon("Insert Page"))
        page_menu.addAction(insert_action)
        
        # Delete Page
        delete_action = QAction("&Delete Page... [Coming Soon]", self)
        delete_action.setStatusTip("Delete current page (Phase 2)")
        delete_action.triggered.connect(lambda: self._show_coming_soon("Delete Page"))
        page_menu.addAction(delete_action)
        
        # Extract Pages
        extract_action = QAction("&Extract Pages... [Coming Soon]", self)
        extract_action.setStatusTip("Extract pages to new PDF (Phase 2)")
        extract_action.triggered.connect(lambda: self._show_coming_soon("Extract Pages"))
        page_menu.addAction(extract_action)
        
        page_menu.addSeparator()
        
        # Rotate Page
        rotate_page_action = QAction(f"{Icons.ROTATE} &Rotate Page", self)
        rotate_page_action.setShortcut("Ctrl+R")
        rotate_page_action.setStatusTip("Rotate current page")
        rotate_page_action.triggered.connect(lambda: self._show_coming_soon("Rotate Page"))
        page_menu.addAction(rotate_page_action)
        self._document_actions.append(rotate_page_action)
        
        # Crop Page
        crop_action = QAction("&Crop Page... [Coming Soon]", self)
        crop_action.setStatusTip("Crop current page (Phase 2)")
        crop_action.triggered.connect(lambda: self._show_coming_soon("Crop Page"))
        page_menu.addAction(crop_action)
        
        page_menu.addSeparator()
        
        # Reorder Pages
        reorder_action = QAction("Re&order Pages... [Coming Soon]", self)
        reorder_action.setStatusTip("Reorder pages in document (Phase 2)")
        reorder_action.triggered.connect(lambda: self._show_coming_soon("Reorder Pages"))
        page_menu.addAction(reorder_action)
    
    def _create_annotate_menu(self):
        """Create Annotate menu with annotation tools."""
        annotate_menu = self.addMenu("&Annotate")
        
        # Highlight
        highlight_action = QAction(f"{Icons.HIGHLIGHT} &Highlight", self)
        highlight_action.setStatusTip("Highlight selected text")
        highlight_action.triggered.connect(lambda: self._show_coming_soon("Highlight"))
        annotate_menu.addAction(highlight_action)
        self._document_actions.append(highlight_action)
        
        # Underline
        underline_action = QAction("&Underline [Coming Soon]", self)
        underline_action.setStatusTip("Underline selected text (Phase 2)")
        underline_action.triggered.connect(lambda: self._show_coming_soon("Underline"))
        annotate_menu.addAction(underline_action)
        
        # Strikethrough
        strike_action = QAction("&Strikethrough [Coming Soon]", self)
        strike_action.setStatusTip("Strikethrough selected text (Phase 2)")
        strike_action.triggered.connect(lambda: self._show_coming_soon("Strikethrough"))
        annotate_menu.addAction(strike_action)
        
        annotate_menu.addSeparator()
        
        # Add Comment
        comment_action = QAction(f"{Icons.COMMENT} Add &Comment... [Coming Soon]", self)
        comment_action.setStatusTip("Add a comment (Phase 2)")
        comment_action.triggered.connect(lambda: self._show_coming_soon("Add Comment"))
        annotate_menu.addAction(comment_action)
        
        # Add Note
        note_action = QAction(f"{Icons.NOTE} Add &Note... [Coming Soon]", self)
        note_action.setStatusTip("Add a sticky note (Phase 2)")
        note_action.triggered.connect(lambda: self._show_coming_soon("Add Note"))
        annotate_menu.addAction(note_action)
        
        annotate_menu.addSeparator()
        
        # Add Stamp
        stamp_action = QAction(f"{Icons.STAMP} Add &Stamp... [Coming Soon]", self)
        stamp_action.setStatusTip("Add a stamp (Phase 2)")
        stamp_action.triggered.connect(lambda: self._show_coming_soon("Add Stamp"))
        annotate_menu.addAction(stamp_action)
        
        # Draw Shape
        shape_action = QAction("Draw &Shape... [Coming Soon]", self)
        shape_action.setStatusTip("Draw shapes (Phase 2)")
        shape_action.triggered.connect(lambda: self._show_coming_soon("Draw Shape"))
        annotate_menu.addAction(shape_action)
        
        annotate_menu.addSeparator()
        
        # Measure Tool
        measure_action = QAction("&Measure Tool... [Coming Soon]", self)
        measure_action.setStatusTip("Measure distances and areas (Phase 2)")
        measure_action.triggered.connect(lambda: self._show_coming_soon("Measure Tool"))
        annotate_menu.addAction(measure_action)
    
    def _create_tools_menu(self):
        """Create Tools menu with OCR and utility features."""
        tools_menu = self.addMenu("&Tools")
        
        # OCR submenu with comprehensive options
        ocr_menu = tools_menu.addMenu("🔍 OCR (Text Recognition)")
        ocr_menu.setIcon(get_icon('file_text', 20))
        
        # Quick OCR - most common action
        quick_ocr_action = QAction("⚡ Quick OCR (Auto-detect)", self)
        quick_ocr_action.setShortcut("Ctrl+Shift+O")
        quick_ocr_action.setStatusTip("Quick OCR with automatic settings")
        quick_ocr_action.triggered.connect(self.quick_ocr_requested.emit)
        ocr_menu.addAction(quick_ocr_action)
        self._document_actions.append(quick_ocr_action)
        
        # Advanced OCR
        advanced_ocr_action = QAction("⚙️ Advanced OCR Options...", self)
        advanced_ocr_action.setShortcut("Ctrl+Alt+O")
        advanced_ocr_action.setStatusTip("OCR with custom settings and options")
        advanced_ocr_action.triggered.connect(self.advanced_ocr_requested.emit)
        ocr_menu.addAction(advanced_ocr_action)
        self._document_actions.append(advanced_ocr_action)
        
        ocr_menu.addSeparator()
        
        # Export OCR results submenu
        export_ocr_menu = ocr_menu.addMenu("📤 Export OCR Results")
        
        export_text_action = QAction("Plain Text...", self)
        export_text_action.setStatusTip("Export recognized text to TXT file")
        export_text_action.triggered.connect(self.export_ocr_text_requested.emit)
        export_ocr_menu.addAction(export_text_action)
        self._document_actions.append(export_text_action)
        
        export_word_action = QAction("Word Document...", self)
        export_word_action.setStatusTip("Export to Microsoft Word with formatting")
        export_word_action.triggered.connect(self.export_ocr_word_requested.emit)
        export_ocr_menu.addAction(export_word_action)
        self._document_actions.append(export_word_action)
        
        export_excel_action = QAction("Excel Spreadsheet...", self)
        export_excel_action.setStatusTip("Export detected tables to Excel")
        export_excel_action.triggered.connect(self.export_ocr_excel_requested.emit)
        export_ocr_menu.addAction(export_excel_action)
        self._document_actions.append(export_excel_action)
        
        ocr_menu.addSeparator()
        
        # OCR Settings
        ocr_settings_action = QAction("⚙️ OCR Settings...", self)
        ocr_settings_action.setStatusTip("Configure OCR preferences and defaults")
        ocr_settings_action.triggered.connect(self.ocr_settings_requested.emit)
        ocr_menu.addAction(ocr_settings_action)
        
        tools_menu.addSeparator()
        
        # Additional tools can be added here in future
        # (Batch processing, compare documents, etc.)
    
    def _create_convert_menu(self):
        """Create Convert menu with conversion options."""
        convert_menu = self.addMenu("C&onvert")
        
        # Export submenu
        export_menu = convert_menu.addMenu(f"{Icons.EXPORT} Export to")
        
        export_word_action = QAction("Word Document... [Coming Soon]", self)
        export_word_action.triggered.connect(lambda: self._show_coming_soon("Export to Word"))
        export_menu.addAction(export_word_action)
        
        export_excel_action = QAction("Excel Spreadsheet... [Coming Soon]", self)
        export_excel_action.triggered.connect(lambda: self._show_coming_soon("Export to Excel"))
        export_menu.addAction(export_excel_action)
        
        export_ppt_action = QAction("PowerPoint... [Coming Soon]", self)
        export_ppt_action.triggered.connect(lambda: self._show_coming_soon("Export to PowerPoint"))
        export_menu.addAction(export_ppt_action)
        
        export_menu.addSeparator()
        
        export_image_action = QAction("Image... [Coming Soon]", self)
        export_image_action.triggered.connect(lambda: self._show_coming_soon("Export to Image"))
        export_menu.addAction(export_image_action)
        
        export_html_action = QAction("HTML... [Coming Soon]", self)
        export_html_action.triggered.connect(lambda: self._show_coming_soon("Export to HTML"))
        export_menu.addAction(export_html_action)
        
        export_text_action = QAction("Plain Text... [Coming Soon]", self)
        export_text_action.triggered.connect(lambda: self._show_coming_soon("Export to Text"))
        export_menu.addAction(export_text_action)
        
        # Import submenu
        import_menu = convert_menu.addMenu(f"{Icons.IMPORT} Import from")
        
        import_word_action = QAction("Word Document... [Coming Soon]", self)
        import_word_action.triggered.connect(lambda: self._show_coming_soon("Import from Word"))
        import_menu.addAction(import_word_action)
        
        import_image_action = QAction("Image... [Coming Soon]", self)
        import_image_action.triggered.connect(lambda: self._show_coming_soon("Import from Image"))
        import_menu.addAction(import_image_action)
        
        import_web_action = QAction("Web Page... [Coming Soon]", self)
        import_web_action.triggered.connect(lambda: self._show_coming_soon("Import from Web"))
        import_menu.addAction(import_web_action)
        
        convert_menu.addSeparator()
        
        # OCR
        ocr_action = QAction("&OCR Document... [Coming Soon]", self)
        ocr_action.setStatusTip("Perform OCR on scanned document (Phase 2)")
        ocr_action.triggered.connect(lambda: self._show_coming_soon("OCR"))
        convert_menu.addAction(ocr_action)
    
    def _create_help_menu(self):
        """Create Help menu with help options."""
        help_menu = self.addMenu("&Help")
        
        # User Guide
        guide_action = QAction("&User Guide", self)
        guide_action.setShortcut("F1")
        guide_action.setStatusTip("Open user guide")
        guide_action.triggered.connect(self.help_requested.emit)
        help_menu.addAction(guide_action)
        
        # Keyboard Shortcuts
        shortcuts_action = QAction(f"{Icons.KEYBOARD} &Keyboard Shortcuts", self)
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        shortcuts_action.triggered.connect(lambda: self._show_keyboard_shortcuts())
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        # About
        about_action = QAction(f"{Icons.INFO} &About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.about_requested.emit)
        help_menu.addAction(about_action)
        
        # License
        license_action = QAction("&License", self)
        license_action.setStatusTip("View license information")
        license_action.triggered.connect(lambda: self._show_license())
        help_menu.addAction(license_action)
    
    def _show_coming_soon(self, feature: str):
        """
        Show coming soon message for a feature.
        
        Args:
            feature: Feature name
        """
        QMessageBox.information(
            self,
            "Coming Soon",
            f"{feature} will be available in a future release.\n\n"
            "This feature is part of our development roadmap."
        )
    
    def _toggle_panel(self, panel: str, visible: bool):
        """
        Toggle sidebar panel visibility.
        
        Args:
            panel: Panel identifier ('left' or 'right')
            visible: Whether to show or hide
        """
        parent = self.parentWidget()
        if panel == "left" and hasattr(parent, 'left_sidebar'):
            parent.left_sidebar.setVisible(visible)
        elif panel == "right" and hasattr(parent, 'right_sidebar'):
            parent.right_sidebar.setVisible(visible)
    
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts reference."""
        shortcuts_text = """
        <h3>Keyboard Shortcuts</h3>
        
        <h4>File Operations</h4>
        <table>
        <tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Print</td></tr>
        <tr><td><b>Ctrl+W</b></td><td>Close file</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
        </table>
        
        <h4>Editing</h4>
        <table>
        <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
        <tr><td><b>Ctrl+X</b></td><td>Cut</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Copy</td></tr>
        <tr><td><b>Ctrl+V</b></td><td>Paste</td></tr>
        <tr><td><b>Ctrl+A</b></td><td>Select All</td></tr>
        </table>
        
        <h4>View</h4>
        <table>
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Fit Page</td></tr>
        <tr><td><b>Ctrl+2</b></td><td>Fit Width</td></tr>
        <tr><td><b>Ctrl+R</b></td><td>Rotate Page</td></tr>
        <tr><td><b>F11</b></td><td>Full Screen</td></tr>
        <tr><td><b>Ctrl+Shift+T</b></td><td>Toggle Theme</td></tr>
        </table>
        
        <h4>Help</h4>
        <table>
        <tr><td><b>F1</b></td><td>User Guide</td></tr>
        </table>
        """
        
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            shortcuts_text
        )
    
    def _show_license(self):
        """Show license information."""
        from utils.constants import AppInfo
        
        license_text = f"""
        <h3>{AppInfo.NAME}</h3>
        <p>Version {AppInfo.VERSION}</p>
        
        <h4>License: {AppInfo.LICENSE}</h4>
        
        <p>This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.</p>
        
        <p>This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        GNU General Public License for more details.</p>
        
        <p>You should have received a copy of the GNU General Public License
        along with this program. If not, see 
        <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.</p>
        """
        
        QMessageBox.information(
            self,
            "License Information",
            license_text
        )
    
    def set_document_actions_enabled(self, enabled: bool):
        """
        Enable or disable document-specific actions.
        
        Args:
            enabled: Whether to enable actions
        """
        for action in self._document_actions:
            action.setEnabled(enabled)
