"""
OCR (Optical Character Recognition) module.

Provides comprehensive OCR capabilities for PDF documents including:
- Text recognition with multiple language support
- Image preprocessing (deskew, despeckle, enhancement)
- Table detection and structure preservation
- Confidence scoring and verification
- Export to multiple formats (Word, Excel, Text)

This module uses EasyOCR as the primary OCR engine for high accuracy
and performance across 80+ languages including Bengali, Chinese, and more.
"""

# Version info
__version__ = "1.0.0"
__author__ = "Simple PDF Handler Team"

# Core OCR functionality
from .ocr_engine import OCREngine, OCRResult
from .image_processor import ImageProcessor
from .text_extractor import TextExtractor, PageOCRResult
from .table_detector import TableDetector, TableStructure
from .pdf_text_layer import PDFTextLayer, PDFSaveWorker
from .ocr_coordinator import OCRCoordinator, OCRWorker

__all__ = [
    'OCREngine',
    'OCRResult',
    'ImageProcessor',
    'TextExtractor',
    'PageOCRResult',
    'TableDetector',
    'TableStructure',
    'PDFTextLayer',
    'PDFSaveWorker',
    'OCRCoordinator',
    'OCRWorker',
]
