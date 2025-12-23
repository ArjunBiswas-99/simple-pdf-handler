"""
Table Detector - Detects and extracts table structures from images.

Identifies tables in document images and preserves their structure
during OCR processing for accurate data extraction.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TableCell:
    """
    Represents a single cell in a detected table.
    
    Attributes:
        row: Row index
        col: Column index
        bbox: Bounding box [x1, y1, x2, y2]
        text: Cell text content (if OCR performed)
    """
    row: int
    col: int
    bbox: List[int]
    text: str = ""


@dataclass
class TableStructure:
    """
    Represents a detected table structure.
    
    Attributes:
        bbox: Table bounding box [x1, y1, x2, y2]
        rows: Number of rows
        cols: Number of columns
        cells: List of TableCell objects
        confidence: Detection confidence score
    """
    bbox: List[int]
    rows: int
    cols: int
    cells: List[TableCell]
    confidence: float = 0.0


class TableDetector:
    """
    Detects and extracts table structures from document images.
    
    Uses computer vision techniques to identify table boundaries,
    grid lines, and cell structures.
    """
    
    def __init__(self):
        """Initialize table detector with default parameters."""
        self.min_table_area = 10000  # Minimum area in pixels
        self.line_threshold = 50  # Minimum line length
        self.cell_padding = 5  # Padding around cells
    
    def detect_tables(
        self,
        image: np.ndarray,
        min_confidence: float = 0.5
    ) -> List[TableStructure]:
        """
        Detect all tables in an image.
        
        Args:
            image: Input image as numpy array
            min_confidence: Minimum detection confidence
            
        Returns:
            List of detected TableStructure objects
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Threshold image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Detect horizontal and vertical lines
        horizontal_lines = self._detect_horizontal_lines(binary)
        vertical_lines = self._detect_vertical_lines(binary)
        
        # Find table regions
        table_mask = cv2.bitwise_or(horizontal_lines, vertical_lines)
        tables = self._find_table_regions(table_mask, image.shape)
        
        # Extract structure for each table
        table_structures = []
        for table_bbox in tables:
            structure = self._extract_table_structure(
                binary,
                table_bbox,
                horizontal_lines,
                vertical_lines
            )
            
            if structure and structure.confidence >= min_confidence:
                table_structures.append(structure)
        
        return table_structures
    
    def _detect_horizontal_lines(
        self,
        binary_image: np.ndarray
    ) -> np.ndarray:
        """
        Detect horizontal lines in binary image.
        
        Args:
            binary_image: Binary input image
            
        Returns:
            Image with horizontal lines
        """
        # Create horizontal kernel
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (binary_image.shape[1] // 30, 1)
        )
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(
            binary_image,
            cv2.MORPH_OPEN,
            horizontal_kernel,
            iterations=2
        )
        
        return horizontal_lines
    
    def _detect_vertical_lines(
        self,
        binary_image: np.ndarray
    ) -> np.ndarray:
        """
        Detect vertical lines in binary image.
        
        Args:
            binary_image: Binary input image
            
        Returns:
            Image with vertical lines
        """
        # Create vertical kernel
        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (1, binary_image.shape[0] // 30)
        )
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(
            binary_image,
            cv2.MORPH_OPEN,
            vertical_kernel,
            iterations=2
        )
        
        return vertical_lines
    
    def _find_table_regions(
        self,
        table_mask: np.ndarray,
        image_shape: Tuple[int, int]
    ) -> List[List[int]]:
        """
        Find bounding boxes of table regions.
        
        Args:
            table_mask: Binary mask with table lines
            image_shape: Original image shape
            
        Returns:
            List of table bounding boxes [x1, y1, x2, y2]
        """
        # Find contours
        contours, _ = cv2.findContours(
            table_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        tables = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum area
            if area < self.min_table_area:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Ensure reasonable aspect ratio
            aspect_ratio = w / h
            if aspect_ratio < 0.5 or aspect_ratio > 10:
                continue
            
            tables.append([x, y, x + w, y + h])
        
        return tables
    
    def _extract_table_structure(
        self,
        binary_image: np.ndarray,
        table_bbox: List[int],
        horizontal_lines: np.ndarray,
        vertical_lines: np.ndarray
    ) -> Optional[TableStructure]:
        """
        Extract structure (rows/cols/cells) from a table region.
        
        Args:
            binary_image: Binary image
            table_bbox: Table bounding box
            horizontal_lines: Detected horizontal lines
            vertical_lines: Detected vertical lines
            
        Returns:
            TableStructure object or None
        """
        x1, y1, x2, y2 = table_bbox
        
        # Extract table region
        h_lines = horizontal_lines[y1:y2, x1:x2]
        v_lines = vertical_lines[y1:y2, x1:x2]
        
        # Find row and column boundaries
        row_boundaries = self._find_line_positions(h_lines, axis=0)
        col_boundaries = self._find_line_positions(v_lines, axis=1)
        
        if len(row_boundaries) < 2 or len(col_boundaries) < 2:
            return None
        
        rows = len(row_boundaries) - 1
        cols = len(col_boundaries) - 1
        
        # Create cells
        cells = []
        for r in range(rows):
            for c in range(cols):
                cell_bbox = [
                    x1 + col_boundaries[c],
                    y1 + row_boundaries[r],
                    x1 + col_boundaries[c + 1],
                    y1 + row_boundaries[r + 1]
                ]
                cells.append(TableCell(r, c, cell_bbox))
        
        # Calculate confidence based on regularity
        confidence = self._calculate_table_confidence(
            rows, cols, row_boundaries, col_boundaries
        )
        
        return TableStructure(
            bbox=table_bbox,
            rows=rows,
            cols=cols,
            cells=cells,
            confidence=confidence
        )
    
    def _find_line_positions(
        self,
        line_image: np.ndarray,
        axis: int
    ) -> List[int]:
        """
        Find positions of lines along an axis.
        
        Args:
            line_image: Image with lines
            axis: Axis to sum along (0=horizontal, 1=vertical)
            
        Returns:
            List of line positions
        """
        # Sum along axis to find line positions
        projection = np.sum(line_image, axis=axis)
        
        # Threshold to find peaks
        threshold = np.max(projection) * 0.3
        positions = np.where(projection > threshold)[0]
        
        if len(positions) == 0:
            return []
        
        # Group nearby positions
        grouped = []
        current_group = [positions[0]]
        
        for pos in positions[1:]:
            if pos - current_group[-1] <= 5:
                current_group.append(pos)
            else:
                grouped.append(int(np.mean(current_group)))
                current_group = [pos]
        
        grouped.append(int(np.mean(current_group)))
        
        return sorted(grouped)
    
    def _calculate_table_confidence(
        self,
        rows: int,
        cols: int,
        row_boundaries: List[int],
        col_boundaries: List[int]
    ) -> float:
        """
        Calculate confidence score for detected table.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            row_boundaries: Row boundary positions
            col_boundaries: Column boundary positions
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 1.0
        
        # Penalize if too few rows/cols
        if rows < 2 or cols < 2:
            confidence *= 0.5
        
        # Check row spacing regularity
        if len(row_boundaries) > 2:
            row_spacings = np.diff(row_boundaries)
            row_std = np.std(row_spacings)
            row_mean = np.mean(row_spacings)
            if row_mean > 0:
                row_regularity = 1.0 - min(row_std / row_mean, 1.0)
                confidence *= (0.5 + 0.5 * row_regularity)
        
        # Check column spacing regularity
        if len(col_boundaries) > 2:
            col_spacings = np.diff(col_boundaries)
            col_std = np.std(col_spacings)
            col_mean = np.mean(col_spacings)
            if col_mean > 0:
                col_regularity = 1.0 - min(col_std / col_mean, 1.0)
                confidence *= (0.5 + 0.5 * col_regularity)
        
        return min(confidence, 1.0)
    
    def extract_table_to_list(
        self,
        table: TableStructure,
        include_empty: bool = True
    ) -> List[List[str]]:
        """
        Convert table structure to 2D list of text.
        
        Args:
            table: TableStructure object
            include_empty: Whether to include empty cells
            
        Returns:
            2D list representing table data
        """
        # Initialize grid
        grid = [['' for _ in range(table.cols)] for _ in range(table.rows)]
        
        # Fill grid with cell text
        for cell in table.cells:
            if include_empty or cell.text:
                grid[cell.row][cell.col] = cell.text
        
        return grid
    
    def table_to_markdown(
        self,
        table: TableStructure
    ) -> str:
        """
        Convert table to Markdown format.
        
        Args:
            table: TableStructure object
            
        Returns:
            Markdown table string
        """
        grid = self.extract_table_to_list(table)
        
        if not grid:
            return ""
        
        lines = []
        
        # Header row
        lines.append('| ' + ' | '.join(grid[0]) + ' |')
        
        # Separator
        lines.append('| ' + ' | '.join(['---'] * table.cols) + ' |')
        
        # Data rows
        for row in grid[1:]:
            lines.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(lines)
    
    def table_to_csv(
        self,
        table: TableStructure,
        delimiter: str = ','
    ) -> str:
        """
        Convert table to CSV format.
        
        Args:
            table: TableStructure object
            delimiter: CSV delimiter
            
        Returns:
            CSV string
        """
        grid = self.extract_table_to_list(table)
        
        lines = []
        for row in grid:
            # Escape cells containing delimiter or quotes
            escaped_row = []
            for cell in row:
                if delimiter in cell or '"' in cell:
                    cell = '"' + cell.replace('"', '""') + '"'
                escaped_row.append(cell)
            lines.append(delimiter.join(escaped_row))
        
        return '\n'.join(lines)
