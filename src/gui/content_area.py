"""
Content area component for PDF display.

Uses QGraphicsView for rendering PDF pages with continuous scrolling support.
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter

from utils.constants import Icons


class ContentArea(QGraphicsView):
    """
    PDF content display area using QGraphicsView.
    
    Provides continuous scrolling through all pages with zoom support.
    Designed to support future editing with selection rectangles.
    """
    
    # Signals
    page_changed = Signal(int)  # Emitted when visible page changes
    zoom_changed = Signal(float)  # Emitted when zoom changes
    text_copied = Signal(str)  # Emitted when text is copied (word count message)
    text_selected = Signal(str)  # Emitted when text is selected (word count message)
    image_selected = Signal(str)  # Emitted when image is selected
    image_copied = Signal(str)  # Emitted when image is copied
    selection_mode_changed = Signal(bool)  # Emitted when selection mode changes
    
    def __init__(self, parent=None):
        """
        Initialize content area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create graphics scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Configure view
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # State for multi-page display
        self._page_items: List[QGraphicsPixmapItem] = []
        self._page_positions: List[float] = []  # Y positions of each page
        self._current_page: int = 0
        self._pdf_document = None  # Reference to PDF document
        self._page_spacing = 10  # Space between pages in pixels
        
        # Text selection state
        self._selection_mode = False  # Toggle between select and pan modes
        self._is_selecting = False
        self._selection_start = None
        self._selection_end = None
        self._selection_rect_item = None  # Blue rectangle while dragging
        self._spacebar_pressed = False  # For temporary pan mode
        
        # Persistent selection state
        self._selected_text = ""  # The selected text content
        self._selected_word_rects = []  # List of QGraphicsRectItem for yellow highlights
        self._selection_data = None  # Store selection coordinates for copying
        
        # Image selection state
        self._selected_image = None  # Tuple: (page_num, xref, width, height, pixmap)
        self._selected_image_border = None  # QGraphicsRectItem for orange border
        
        # Show placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder when no document is open."""
        self.scene.clear()
        self._page_items = []
        self._page_positions = []
        
        # Create placeholder text
        placeholder = self.scene.addText(
            f"{Icons.PAGES}\n\nNo Document Open\n\n"
            "Use File → Open or drag & drop a PDF"
        )
        placeholder.setDefaultTextColor(Qt.gray)
        
        # Center the placeholder
        rect = placeholder.boundingRect()
        placeholder.setPos(-rect.width()/2, -rect.height()/2)
    
    def set_pdf_document(self, pdf_document):
        """
        Set the PDF document to display.
        
        Args:
            pdf_document: PDFDocument instance
        """
        self._pdf_document = pdf_document
        self.render_all_pages()
    
    def render_all_pages(self):
        """Set up page structure and render visible pages only (lazy loading)."""
        if not self._pdf_document or not self._pdf_document.is_open:
            return
        
        # Save current page to restore position after re-render
        saved_page = self._current_page
        
        # Clear selection references BEFORE scene.clear() to avoid dangling references
        self._selected_word_rects = []
        self._selected_text = ""
        self._selected_image_border = None
        self._selected_image = None
        
        # Clear existing content
        self.scene.clear()
        self._page_items = []
        self._page_positions = []
        
        # Calculate page positions and create placeholders
        y_offset = 0
        max_width = 0
        
        for page_num in range(self._pdf_document.page_count):
            # Get page size to calculate position
            page_size = self._pdf_document.get_page_size(page_num)
            
            if page_size:
                width, height = page_size
                zoom_factor = self._pdf_document.zoom_level / 100.0
                rendered_width = width * zoom_factor
                rendered_height = height * zoom_factor
                
                # Create placeholder item (will be replaced with actual render on-demand)
                from PySide6.QtWidgets import QGraphicsRectItem
                from PySide6.QtGui import QBrush, QColor, QPen
                
                placeholder = QGraphicsRectItem(0, y_offset, rendered_width, rendered_height)
                placeholder.setBrush(QBrush(QColor(240, 240, 240)))  # Light gray
                placeholder.setPen(QPen(QColor(200, 200, 200)))
                self.scene.addItem(placeholder)
                
                # Store placeholder and position
                self._page_items.append(placeholder)
                self._page_positions.append(y_offset)
                
                # Update max width and y offset
                max_width = max(max_width, rendered_width)
                y_offset += rendered_height + self._page_spacing
        
        # Update scene rect to fit all pages
        if self._page_items:
            total_height = y_offset - self._page_spacing
            self.scene.setSceneRect(0, 0, max_width, total_height)
            
            # Render only visible pages
            self._render_visible_pages()
            
            # Restore to saved page (don't jump to page 1!)
            if saved_page < len(self._page_positions):
                self.go_to_page(saved_page)
            else:
                # Scroll to top only if this is first load
                self.verticalScrollBar().setValue(0)
            
            # Update current page
            self._update_current_page()
    
    def display_page(self, pixmap: QPixmap, page_number: int):
        """
        Display a single rendered PDF page (legacy method for compatibility).
        
        Args:
            pixmap: Rendered page as QPixmap
            page_number: Page number being displayed
        """
        # For now, just render all pages - this maintains compatibility
        # but we should transition to using render_all_pages() directly
        if self._pdf_document:
            self.render_all_pages()
    
    def clear_content(self):
        """Clear the content area."""
        self._show_placeholder()
        self._page_items = []
        self._page_positions = []
        self._current_page = 0
        self._pdf_document = None
    
    def set_selection_mode(self, enabled: bool):
        """
        Enable or disable text selection mode.
        
        Args:
            enabled: True for selection mode, False for pan mode
        """
        if self._selection_mode != enabled:
            self._selection_mode = enabled
            self._update_cursor_and_drag_mode()
            self.selection_mode_changed.emit(enabled)
    
    def get_selection_mode(self) -> bool:
        """
        Get current selection mode state.
        
        Returns:
            True if in selection mode, False otherwise
        """
        return self._selection_mode
    
    def _update_cursor_and_drag_mode(self):
        """Update cursor and drag mode based on current state."""
        # Check if spacebar is pressed for temporary pan
        in_pan_mode = (not self._selection_mode) or self._spacebar_pressed
        
        if in_pan_mode:
            # Pan mode: hand cursor and drag enabled
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.OpenHandCursor)
        else:
            # Selection mode: text cursor and no drag
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().setCursor(Qt.IBeamCursor)
    
    def get_current_page(self) -> int:
        """
        Get currently visible page number.
        
        Returns:
            Page number (0-indexed)
        """
        return self._current_page
    
    def _update_current_page(self):
        """Update current page based on scroll position."""
        if not self._page_positions:
            return
        
        # Get center of viewport in scene coordinates
        viewport_center = self.mapToScene(
            self.viewport().rect().center()
        )
        center_y = viewport_center.y()
        
        # Find which page is at the center
        for i, y_pos in enumerate(self._page_positions):
            if i < len(self._page_positions) - 1:
                next_y = self._page_positions[i + 1]
                if y_pos <= center_y < next_y:
                    if self._current_page != i:
                        self._current_page = i
                        self.page_changed.emit(i)
                    return
            else:
                # Last page
                if center_y >= y_pos:
                    if self._current_page != i:
                        self._current_page = i
                        self.page_changed.emit(i)
                    return
    
    def scrollContentsBy(self, dx: int, dy: int):
        """
        Override scroll event to update current page and render visible pages.
        
        Args:
            dx: Horizontal scroll delta
            dy: Vertical scroll delta
        """
        super().scrollContentsBy(dx, dy)
        self._render_visible_pages()  # Lazy render on scroll
        self._update_current_page()
    
    def _get_visible_page_range(self):
        """
        Get the range of pages currently visible in the viewport.
        
        Returns:
            Tuple of (first_visible_page, last_visible_page) or (0, 0) if none
        """
        if not self._page_positions:
            return (0, 0)
        
        # Get viewport rectangle in scene coordinates
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        viewport_top = viewport_rect.top()
        viewport_bottom = viewport_rect.bottom()
        
        # Add buffer: render 1 page above and below visible area
        buffer_pages = 1
        
        first_page = None
        last_page = None
        
        for page_num, y_pos in enumerate(self._page_positions):
            if page_num < len(self._page_items):
                page_item = self._page_items[page_num]
                
                # Get page height (might be placeholder or rendered)
                if isinstance(page_item, QGraphicsPixmapItem):
                    page_height = page_item.pixmap().height()
                else:
                    page_height = page_item.rect().height()
                
                page_bottom = y_pos + page_height
                
                # Check if page is visible (or near visible)
                if page_bottom >= viewport_top and y_pos <= viewport_bottom:
                    if first_page is None:
                        first_page = max(0, page_num - buffer_pages)
                    last_page = min(len(self._page_positions) - 1, page_num + buffer_pages)
        
        if first_page is not None and last_page is not None:
            return (first_page, last_page)
        
        return (0, 0)
    
    def _render_visible_pages(self):
        """Render only the pages currently visible in the viewport."""
        if not self._pdf_document or not self._pdf_document.is_open:
            return
        
        first_page, last_page = self._get_visible_page_range()
        
        for page_num in range(first_page, last_page + 1):
            if page_num < len(self._page_items):
                page_item = self._page_items[page_num]
                
                # Check if this is still a placeholder (not yet rendered)
                if not isinstance(page_item, QGraphicsPixmapItem):
                    # Render this page
                    pixmap = self._pdf_document.render_page(page_num)
                    
                    if pixmap and not pixmap.isNull():
                        # Remove placeholder
                        self.scene.removeItem(page_item)
                        
                        # Add rendered pixmap
                        rendered_item = self.scene.addPixmap(pixmap)
                        rendered_item.setPos(0, self._page_positions[page_num])
                        
                        # Replace in list
                        self._page_items[page_num] = rendered_item
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.scale(1.25, 1.25)
        self._emit_zoom_change()
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.scale(0.8, 0.8)
        self._emit_zoom_change()
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.resetTransform()
        self._emit_zoom_change()
    
    def fit_to_width(self):
        """Fit page to view width."""
        if self._page_items:
            # Fit first page width to view
            first_item = self._page_items[0]
            self.fitInView(first_item, Qt.KeepAspectRatioByExpanding)
            self._emit_zoom_change()
    
    def fit_to_page(self):
        """Fit entire page in view."""
        if self._page_items:
            # Fit first page to view
            first_item = self._page_items[0]
            self.fitInView(first_item, Qt.KeepAspectRatio)
            self._emit_zoom_change()
    
    def go_to_page(self, page_number: int):
        """
        Scroll to a specific page.
        
        Args:
            page_number: Page number (0-indexed)
        """
        if 0 <= page_number < len(self._page_positions):
            y_pos = self._page_positions[page_number]
            self.verticalScrollBar().setValue(int(y_pos))
            self._current_page = page_number
            self.page_changed.emit(page_number)
    
    def _emit_zoom_change(self):
        """Emit zoom change signal with current zoom level."""
        # Calculate approximate zoom level from transform
        transform = self.transform()
        zoom = transform.m11() * 100  # Get horizontal scale factor
        self.zoom_changed.emit(zoom)
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel events for zooming.
        
        Args:
            event: Wheel event
        """
        # Ctrl + Wheel = Zoom
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press for image/text selection or panning.
        
        Args:
            event: Mouse press event
        """
        if event.button() == Qt.LeftButton:
            # Check if in selection mode and not holding spacebar
            if self._selection_mode and not self._spacebar_pressed:
                # Selection mode: Check if click is on an image first
                click_pos = self.mapToScene(event.pos())
                image_info = self._find_image_at_position(click_pos)
                
                if image_info:
                    # Click on image: Select it
                    self._select_image(image_info)
                    event.accept()
                else:
                    # Click on text area: Start text selection
                    self.setDragMode(QGraphicsView.NoDrag)
                    self._is_selecting = True
                    self._selection_start = click_pos
                    self._selection_end = self._selection_start
                    
                    # Remove old selection rectangle if exists
                    if self._selection_rect_item:
                        self.scene.removeItem(self._selection_rect_item)
                        self._selection_rect_item = None
                    
                    event.accept()
            else:
                # Pan mode: Enable dragging
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move for text selection.
        
        Args:
            event: Mouse move event
        """
        if self._is_selecting:
            # Update selection end point
            self._selection_end = self.mapToScene(event.pos())
            
            # Remove old selection rectangle
            if self._selection_rect_item:
                self.scene.removeItem(self._selection_rect_item)
            
            # Draw new selection rectangle
            self._draw_selection_rect()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release to complete text selection.
        
        Args:
            event: Mouse release event
        """
        if self._is_selecting and event.button() == Qt.LeftButton:
            self._is_selecting = False
            
            # Extract text and show highlights (NO auto-copy)
            self._complete_selection()
            
            # Remove blue rectangle
            if self._selection_rect_item:
                self.scene.removeItem(self._selection_rect_item)
                self._selection_rect_item = None
            
            event.accept()
        elif event.button() == Qt.LeftButton and self._selection_mode:
            # Only clear if clicking on empty area (not on an image)
            click_pos = self.mapToScene(event.pos())
            image_info = self._find_image_at_position(click_pos)
            
            if not image_info and not (self._selected_text or self._selected_image):
                # Clicked on empty area with no selection - do nothing
                super().mouseReleaseEvent(event)
            elif not image_info:
                # Clicked on empty area with existing selection - clear it
                self.clear_selection()
                super().mouseReleaseEvent(event)
            else:
                # Clicked on image - already handled in mousePressEvent
                event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def _draw_selection_rect(self):
        """Draw the current selection rectangle."""
        if not self._selection_start or not self._selection_end:
            return
        
        from PySide6.QtWidgets import QGraphicsRectItem
        from PySide6.QtGui import QColor, QPen, QBrush
        
        # Calculate rectangle
        x1, y1 = self._selection_start.x(), self._selection_start.y()
        x2, y2 = self._selection_end.x(), self._selection_end.y()
        
        rect = QRectF(
            min(x1, x2), min(y1, y2),
            abs(x2 - x1), abs(y2 - y1)
        )
        
        # Create rectangle item
        self._selection_rect_item = QGraphicsRectItem(rect)
        
        # Style: Blue with 30% opacity
        color = QColor(0, 120, 215, 76)  # RGBA: Blue with ~30% alpha
        self._selection_rect_item.setBrush(QBrush(color))
        self._selection_rect_item.setPen(QPen(QColor(0, 120, 215), 1))
        
        # Add to scene
        self.scene.addItem(self._selection_rect_item)
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event: Key event
        """
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            # Spacebar pressed: Temporarily enable pan mode
            if not self._spacebar_pressed:
                self._spacebar_pressed = True
                self._update_cursor_and_drag_mode()
            event.accept()
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            # Ctrl+C: Copy selected text
            self.copy_selected_text()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            # ESC: Clear selection
            self.clear_selection()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """
        Handle key release events.
        
        Args:
            event: Key event
        """
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            # Spacebar released: Return to previous mode
            if self._spacebar_pressed:
                self._spacebar_pressed = False
                self._update_cursor_and_drag_mode()
            event.accept()
        else:
            super().keyReleaseEvent(event)
    
    def _complete_selection(self):
        """Complete text selection and draw persistent highlights (NO auto-copy)."""
        if not self._pdf_document or not self._selection_start or not self._selection_end:
            return
        
        # Clear any previous selection
        self.clear_selection()
        
        from PySide6.QtWidgets import QGraphicsRectItem
        from PySide6.QtGui import QColor, QPen, QBrush
        
        # Get selection rectangle in scene coordinates
        x1, y1 = self._selection_start.x(), self._selection_start.y()
        x2, y2 = self._selection_end.x(), self._selection_end.y()
        
        # Normalize coordinates
        sel_x0, sel_x1 = min(x1, x2), max(x1, x2)
        sel_y0, sel_y1 = min(y1, y2), max(y1, y2)
        
        # Find which page(s) the selection spans and get word boxes
        selected_text_parts = []
        zoom_factor = self._pdf_document.zoom_level / 100.0
        
        for page_num, page_y_offset in enumerate(self._page_positions):
            if page_num < len(self._page_items):
                page_item = self._page_items[page_num]
                
                # Get page height (handle both pixmaps and placeholders)
                if isinstance(page_item, QGraphicsPixmapItem):
                    page_height = page_item.pixmap().height()
                else:
                    page_height = page_item.rect().height()
                
                page_bottom = page_y_offset + page_height
                
                # Check if selection intersects this page
                if sel_y1 >= page_y_offset and sel_y0 <= page_bottom:
                    # Calculate selection within this page (in scene coordinates)
                    page_sel_y0 = max(0, sel_y0 - page_y_offset)
                    page_sel_y1 = min(page_height, sel_y1 - page_y_offset)
                    
                    # Convert to PDF coordinates
                    pdf_x0 = sel_x0 / zoom_factor
                    pdf_y0 = page_sel_y0 / zoom_factor
                    pdf_x1 = sel_x1 / zoom_factor
                    pdf_y1 = page_sel_y1 / zoom_factor
                    
                    # Get text for this page
                    text = self._pdf_document.get_text_in_rect(
                        page_num, (pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                    )
                    if text:
                        selected_text_parts.append(text)
                    
                    # Get word bounding boxes for highlighting
                    word_boxes = self._pdf_document.get_word_boxes_in_rect(
                        page_num, (pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                    )
                    
                    # Draw yellow highlights for each word
                    for wx0, wy0, wx1, wy1, word_text in word_boxes:
                        # Convert word box to scene coordinates
                        scene_x0 = wx0 * zoom_factor
                        scene_y0 = (wy0 * zoom_factor) + page_y_offset
                        scene_x1 = wx1 * zoom_factor
                        scene_y1 = (wy1 * zoom_factor) + page_y_offset
                        
                        # Create highlight rectangle
                        highlight_rect = QRectF(scene_x0, scene_y0, scene_x1 - scene_x0, scene_y1 - scene_y0)
                        highlight_item = QGraphicsRectItem(highlight_rect)
                        
                        # Style: Yellow with 40% opacity
                        yellow_color = QColor(255, 255, 0, 102)  # RGBA: Yellow with 40% alpha
                        highlight_item.setBrush(QBrush(yellow_color))
                        highlight_item.setPen(QPen(Qt.NoPen))
                        
                        # Add to scene and track
                        self.scene.addItem(highlight_item)
                        self._selected_word_rects.append(highlight_item)
        
        # Store selected text
        self._selected_text = "\n".join(selected_text_parts)
        
        if self._selected_text:
            # Emit signal for status bar feedback (NOT copied, just selected)
            word_count = len(self._selected_text.split())
            self.text_selected.emit(f"Selected {word_count} words - Press Ctrl+C to copy")
    
    def clear_selection(self):
        """Clear the current text or image selection and highlights."""
        # Remove text highlight rectangles (check if still in scene)
        for rect_item in self._selected_word_rects:
            if rect_item.scene() is not None:  # Only remove if still in scene
                self.scene.removeItem(rect_item)
        
        self._selected_word_rects = []
        self._selected_text = ""
        self._selection_data = None
        
        # Remove image border (check if still in scene)
        if self._selected_image_border and self._selected_image_border.scene() is not None:
            self.scene.removeItem(self._selected_image_border)
        self._selected_image_border = None
        
        self._selected_image = None
    
    def copy_selected_text(self):
        """Copy the currently selected text or image to clipboard."""
        # Check if we have a selected image
        if self._selected_image:
            self._copy_selected_image()
        elif self._selected_text:
            # Copy text
            from PySide6.QtWidgets import QApplication
            
            clipboard = QApplication.clipboard()
            clipboard.setText(self._selected_text)
            
            # Emit signal for status bar feedback
            word_count = len(self._selected_text.split())
            self.text_copied.emit(f"Copied {word_count} words to clipboard")
    
    def _find_image_at_position(self, scene_pos: QPointF):
        """
        Find if click position is on an image.
        
        Args:
            scene_pos: Click position in scene coordinates
            
        Returns:
            Tuple (page_num, x0, y0, x1, y1, xref, width, height) or None
        """
        if not self._pdf_document:
            return None
        
        # Find which page the click is on
        zoom_factor = self._pdf_document.zoom_level / 100.0
        
        for page_num, page_y_offset in enumerate(self._page_positions):
            if page_num < len(self._page_items):
                page_item = self._page_items[page_num]
                
                # Get page height (handle both pixmaps and placeholders)
                if isinstance(page_item, QGraphicsPixmapItem):
                    page_height = page_item.pixmap().height()
                else:
                    page_height = page_item.rect().height()
                
                page_bottom = page_y_offset + page_height
                
                # Check if click is on this page
                if page_y_offset <= scene_pos.y() <= page_bottom:
                    # Convert click position to PDF coordinates
                    page_click_y = scene_pos.y() - page_y_offset
                    pdf_x = scene_pos.x() / zoom_factor
                    pdf_y = page_click_y / zoom_factor
                    
                    # Get images on this page
                    images = self._pdf_document.get_images_on_page(page_num)
                    
                    # Check if click is within any image
                    for img_x0, img_y0, img_x1, img_y1, xref, width, height in images:
                        if img_x0 <= pdf_x <= img_x1 and img_y0 <= pdf_y <= img_y1:
                            return (page_num, img_x0, img_y0, img_x1, img_y1, xref, width, height)
        
        return None
    
    def _select_image(self, image_info):
        """
        Select an image and draw border highlight.
        
        Args:
            image_info: Tuple (page_num, x0, y0, x1, y1, xref, width, height)
        """
        # Clear any previous selection (text or image)
        self.clear_selection()
        
        from PySide6.QtWidgets import QGraphicsRectItem
        from PySide6.QtGui import QColor, QPen
        
        page_num, img_x0, img_y0, img_x1, img_y1, xref, width, height = image_info
        
        # Get the image data
        image_pixmap = self._pdf_document.get_image_data(page_num, xref)
        
        # Store selected image info
        self._selected_image = (page_num, xref, width, height, image_pixmap)
        
        # Convert image rectangle to scene coordinates
        zoom_factor = self._pdf_document.zoom_level / 100.0
        page_y_offset = self._page_positions[page_num]
        
        scene_x0 = img_x0 * zoom_factor
        scene_y0 = (img_y0 * zoom_factor) + page_y_offset
        scene_x1 = img_x1 * zoom_factor
        scene_y1 = (img_y1 * zoom_factor) + page_y_offset
        
        # Create border rectangle
        border_rect = QRectF(scene_x0, scene_y0, scene_x1 - scene_x0, scene_y1 - scene_y0)
        self._selected_image_border = QGraphicsRectItem(border_rect)
        
        # Style: Orange border, no fill, 3px width
        orange_color = QColor(255, 102, 0)  # Orange
        self._selected_image_border.setPen(QPen(orange_color, 3))
        self._selected_image_border.setBrush(Qt.NoBrush)
        
        # Add to scene
        self.scene.addItem(self._selected_image_border)
        
        # Emit signal for status bar
        self.image_selected.emit(f"Image selected ({width}x{height} px) - Press Ctrl+C to copy")
    
    def _copy_selected_image(self):
        """Copy the selected image to clipboard."""
        if not self._selected_image:
            return
        
        from PySide6.QtWidgets import QApplication
        
        page_num, xref, width, height, image_pixmap = self._selected_image
        
        if image_pixmap:
            # Copy image to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(image_pixmap)
            
            # Emit signal for status bar
            self.image_copied.emit(f"Copied image ({width}x{height} px) to clipboard")
