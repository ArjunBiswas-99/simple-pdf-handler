"""
Simple PDF Handler - PDF Canvas Shape Drawing Handler

Handles shape drawing interactions on the PDF canvas.
Manages mouse events for drawing rectangles, circles, and lines.

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from typing import Optional, Tuple
import math


class ShapeDrawingHandler:
    """
    Handles shape drawing mode on PDF canvas.
    Manages rubber-band preview and shape finalization.
    """
    
    def __init__(self, canvas):
        """
        Initialize the shape drawing handler.
        
        Args:
            canvas: PDFCanvas instance
        """
        self._canvas = canvas
        self._drawing_active = False
        self._shape_type = 'rectangle'
        self._shape_properties = {}
        
        # Drawing state
        self._start_point: Optional[QPointF] = None
        self._current_point: Optional[QPointF] = None
        self._drawing_in_progress = False
    
    def enter_drawing_mode(self, shape_type: str, properties: dict) -> None:
        """
        Enter shape drawing mode.
        
        Args:
            shape_type: Type of shape ('rectangle', 'circle', 'line')
            properties: Shape properties (colors, widths, fill)
        """
        self._drawing_active = True
        self._shape_type = shape_type
        self._shape_properties = properties
        
        # Change cursor to crosshair
        self._canvas.setCursor(Qt.CursorShape.CrossCursor)
    
    def exit_drawing_mode(self) -> None:
        """Exit shape drawing mode and restore normal cursor."""
        self._drawing_active = False
        self._start_point = None
        self._current_point = None
        self._drawing_in_progress = False
        self._canvas.setCursor(Qt.CursorShape.ArrowCursor)
        self._canvas.viewport().update()
    
    def is_active(self) -> bool:
        """
        Check if shape drawing mode is active.
        
        Returns:
            True if active, False otherwise
        """
        return self._drawing_active
    
    def handle_mouse_press(self, event) -> bool:
        """
        Handle mouse press event for starting shape drawing.
        
        Args:
            event: QMouseEvent
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self._drawing_active:
            return False
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Start drawing
            self._start_point = event.position()
            self._current_point = event.position()
            self._drawing_in_progress = True
            self._canvas.viewport().update()
            return True
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel drawing mode
            self.exit_drawing_mode()
            return True
        
        return False
    
    def handle_mouse_move(self, event) -> bool:
        """
        Handle mouse move event for rubber-band preview.
        
        Args:
            event: QMouseEvent
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self._drawing_active or not self._drawing_in_progress:
            return False
        
        # Update current point for preview
        self._current_point = event.position()
        self._canvas.viewport().update()
        return True
    
    def handle_mouse_release(self, event) -> Tuple[bool, Optional[dict]]:
        """
        Handle mouse release event for finalizing shape.
        
        Args:
            event: QMouseEvent
            
        Returns:
            Tuple of (handled, shape_data) where:
            - handled: True if event was handled
            - shape_data: Dictionary with shape info if shape was finalized, None otherwise
        """
        if not self._drawing_active or not self._drawing_in_progress:
            return (False, None)
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Finalize shape
            self._current_point = event.position()
            
            # Get page info at release point
            page_info = self._canvas._get_page_at_position(self._current_point)
            if not page_info:
                # Released outside page - cancel
                self._drawing_in_progress = False
                self._canvas.viewport().update()
                return (True, None)
            
            page_num, page_label, _ = page_info
            
            # Convert both points to PDF coordinates
            start_pdf = self._canvas._viewport_to_pdf_coords(self._start_point, page_label)
            end_pdf = self._canvas._viewport_to_pdf_coords(self._current_point, page_label)
            
            if not start_pdf or not end_pdf:
                # Conversion failed - cancel
                self._drawing_in_progress = False
                self._canvas.viewport().update()
                return (True, None)
            
            # Build shape data based on type
            shape_data = {
                'type': self._shape_type,
                'page_number': page_num,
                'properties': self._shape_properties.copy()
            }
            
            if self._shape_type == 'rectangle':
                # Rectangle: store as x0, y0, x1, y1
                shape_data['x0'] = min(start_pdf.x(), end_pdf.x())
                shape_data['y0'] = min(start_pdf.y(), end_pdf.y())
                shape_data['x1'] = max(start_pdf.x(), end_pdf.x())
                shape_data['y1'] = max(start_pdf.y(), end_pdf.y())
                
            elif self._shape_type == 'circle':
                # Circle: calculate center and radius
                center_x = (start_pdf.x() + end_pdf.x()) / 2
                center_y = (start_pdf.y() + end_pdf.y()) / 2
                
                # Calculate radius from distance
                dx = end_pdf.x() - start_pdf.x()
                dy = end_pdf.y() - start_pdf.y()
                radius = math.sqrt(dx * dx + dy * dy) / 2
                
                shape_data['center_x'] = center_x
                shape_data['center_y'] = center_y
                shape_data['radius'] = radius
                
            elif self._shape_type == 'line':
                # Line: store as start and end points
                shape_data['x0'] = start_pdf.x()
                shape_data['y0'] = start_pdf.y()
                shape_data['x1'] = end_pdf.x()
                shape_data['y1'] = end_pdf.y()
            
            # Reset drawing state
            self._drawing_in_progress = False
            self._start_point = None
            self._current_point = None
            self._canvas.viewport().update()
            
            # Exit drawing mode after one shape
            self.exit_drawing_mode()
            
            return (True, shape_data)
        
        return (False, None)
    
    def paint_preview(self, painter: QPainter) -> None:
        """
        Paint rubber-band preview of shape being drawn.
        
        Args:
            painter: QPainter for drawing preview
        """
        if not self._drawing_in_progress or not self._start_point or not self._current_point:
            return
        
        # Get border properties
        border_color = self._shape_properties.get('border_color', QColor(255, 0, 0))
        border_width = self._shape_properties.get('border_width', 2)
        fill_enabled = self._shape_properties.get('fill_enabled', False)
        fill_color = self._shape_properties.get('fill_color', QColor(0, 0, 255, 100))
        
        # Configure pen for border
        pen = QPen(border_color)
        pen.setWidth(border_width)
        pen.setStyle(Qt.PenStyle.DashLine)  # Dashed for preview
        painter.setPen(pen)
        
        # Configure brush for fill
        if fill_enabled and fill_color and self._shape_type != 'line':
            brush = QBrush(fill_color)
            painter.setBrush(brush)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw preview based on shape type
        if self._shape_type == 'rectangle':
            self._paint_rectangle_preview(painter)
        elif self._shape_type == 'circle':
            self._paint_circle_preview(painter)
        elif self._shape_type == 'line':
            self._paint_line_preview(painter)
    
    def _paint_rectangle_preview(self, painter: QPainter) -> None:
        """
        Paint rectangle preview.
        
        Args:
            painter: QPainter for drawing
        """
        # Calculate rectangle bounds
        x = min(self._start_point.x(), self._current_point.x())
        y = min(self._start_point.y(), self._current_point.y())
        width = abs(self._current_point.x() - self._start_point.x())
        height = abs(self._current_point.y() - self._start_point.y())
        
        painter.drawRect(int(x), int(y), int(width), int(height))
    
    def _paint_circle_preview(self, painter: QPainter) -> None:
        """
        Paint circle preview.
        
        Args:
            painter: QPainter for drawing
        """
        # Calculate center and radius
        center_x = (self._start_point.x() + self._current_point.x()) / 2
        center_y = (self._start_point.y() + self._current_point.y()) / 2
        
        dx = self._current_point.x() - self._start_point.x()
        dy = self._current_point.y() - self._start_point.y()
        radius = math.sqrt(dx * dx + dy * dy) / 2
        
        # Draw ellipse (circle) centered at center point
        painter.drawEllipse(
            QPointF(center_x, center_y),
            radius,
            radius
        )
    
    def _paint_line_preview(self, painter: QPainter) -> None:
        """
        Paint line preview.
        
        Args:
            painter: QPainter for drawing
        """
        painter.drawLine(
            self._start_point.toPoint(),
            self._current_point.toPoint()
        )
