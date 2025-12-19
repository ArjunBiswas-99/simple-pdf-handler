"""
Text placement handler for PDFCanvas - separated for clarity.
This module contains the _handle_text_placement_click method.
"""

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor


def handle_text_placement_click(canvas, event):
    """
    Handle mouse click in text placement mode.
    Shows inline editor and format toolbar at click position.
    
    Args:
        canvas: PDFCanvas instance
        event: Mouse event
    """
    from ui.widgets import InlineTextEditor, TextFormatToolbar
    
    # Get click position
    click_pos = event.pos()
    
    # Get which page was clicked
    page_info = canvas._get_page_at_position(click_pos)
    if not page_info:
        return
    
    page_num, page_label, point_in_page = page_info
    
    # Convert to PDF coordinates
    pdf_x = point_in_page.x() / canvas._zoom_level
    pdf_y = point_in_page.y() / canvas._zoom_level
    
    # Create format toolbar
    initial_format = {
        'font': 'Helvetica',
        'size': 12,
        'color': QColor(0, 0, 0),
        'bold': False,
        'italic': False,
        'underline': False
    }
    
    canvas._format_toolbar = TextFormatToolbar(canvas)
    canvas._format_toolbar.set_format_properties(initial_format)
    
    # Position toolbar above click point (in canvas coordinates)
    toolbar_x = click_pos.x() - canvas._format_toolbar.width() // 2
    toolbar_y = click_pos.y() - canvas._format_toolbar.height() - 10
    
    # Map to viewport coordinates
    viewport_pos = canvas.viewport().mapFromParent(click_pos)
    toolbar_x = viewport_pos.x() - canvas._format_toolbar.width() // 2
    toolbar_y = viewport_pos.y() - canvas._format_toolbar.height() - 10
    
    # Position toolbar in viewport
    canvas._format_toolbar.setParent(canvas.viewport())
    canvas._format_toolbar.move(max(0, toolbar_x), max(0, toolbar_y))
    canvas._format_toolbar.show()
    canvas._format_toolbar.raise_()
    
    # Create inline editor
    canvas._inline_editor = InlineTextEditor(initial_format, canvas.viewport())
    editor_x = viewport_pos.x()
    editor_y = viewport_pos.y()
    canvas._inline_editor.move(editor_x, editor_y)
    canvas._inline_editor.show()
    canvas._inline_editor.raise_()
    canvas._inline_editor.setFocus()
    
    # Connect signals
    canvas._format_toolbar.format_changed.connect(canvas._inline_editor.update_format)
    canvas._format_toolbar.done_clicked.connect(
        lambda: commit_text(canvas, page_num, pdf_x, pdf_y)
    )
    canvas._format_toolbar.cancel_clicked.connect(lambda: cancel_text(canvas))
    canvas._inline_editor.text_committed.connect(
        lambda t, f: commit_text(canvas, page_num, pdf_x, pdf_y)
    )
    canvas._inline_editor.edit_cancelled.connect(lambda: cancel_text(canvas))


def commit_text(canvas, page_num, pdf_x, pdf_y):
    """
    Commit text and notify parent.
    
    Args:
        canvas: PDFCanvas instance
        page_num: Page number
        pdf_x, pdf_y: PDF coordinates
    """
    if not canvas._inline_editor:
        return
    
    text = canvas._inline_editor.get_text()
    format_props = canvas._inline_editor.get_format()
    
    if text.strip():
        # Notify parent (MainWindow)
        parent = canvas.parent()
        while parent and not hasattr(parent, '_on_text_committed'):
            parent = parent.parent()
        
        if parent and hasattr(parent, '_on_text_committed'):
            parent._on_text_committed(text, format_props, page_num, pdf_x, pdf_y)
    
    # Clean up
    canvas.exit_text_placement_mode()


def cancel_text(canvas):
    """
    Cancel text placement.
    
    Args:
        canvas: PDFCanvas instance
    """
    canvas.exit_text_placement_mode()
