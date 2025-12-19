## Shape Drawing Feature - Integration Guide

This guide describes how to complete the shape drawing feature integration.

### Components Created ✅

1. **ShapeDrawingToolbar** (`src/ui/widgets/shape_drawing_toolbar.py`)
   - UI controls for shape type, colors, widths, fill
   - Emits `drawing_started(shape_type, properties)` signal

2. **ShapeDrawingHandler** (`src/ui/pdf_canvas_shape_handler.py`)
   - Handles mouse events for drawing
   - Manages rubber-band preview
   - Returns shape data on completion

3. **Backend Methods** (`src/backend/pymupdf_backend.py`)
   - `add_rectangle_shape()` - Draw rectangles
   - `add_circle_shape()` - Draw circles
   - `add_line_shape()` - Draw lines

4. **AddShapeAction** (`src/core/undo_manager.py`)
   - Undo/redo support for shapes

### Integration Steps Required 🔧

#### Step 1: Add Shape Handler to PDFCanvas

In `src/ui/pdf_canvas.py`, add these changes:

1. **Import the handler:**
```python
from ui.pdf_canvas_shape_handler import ShapeDrawingHandler
```

2. **Initialize in `__init__`:**
```python
# Add after text placement mode initialization
self._shape_handler = ShapeDrawingHandler(self)
```

3. **Add signal:**
```python
# Add with other signals
shape_drawn = pyqtSignal(dict)  # shape_data
```

4. **Modify `mousePressEvent` to check shape mode first:**
```python
def mousePressEvent(self, event) -> None:
    # Check shape drawing mode FIRST
    if self._shape_handler.is_active():
        handled = self._shape_handler.handle_mouse_press(event)
        if handled:
            return
    
    # Then text placement mode
    if self._text_placement_mode and event.button() == Qt.MouseButton.LeftButton:
        # ... existing code ...
```

5. **Modify `mouseMoveEvent`:**
```python
def mouseMoveEvent(self, event) -> None:
    # Check shape drawing mode
    if self._shape_handler.is_active():
        handled = self._shape_handler.handle_mouse_move(event)
        if handled:
            return
    
    # ... existing code ...
```

6. **Modify `mouseReleaseEvent`:**
```python
def mouseReleaseEvent(self, event) -> None:
    # Check shape drawing mode
    if self._shape_handler.is_active():
        handled, shape_data = self._shape_handler.handle_mouse_release(event)
        if handled:
            if shape_data:
                # Emit signal with shape data
