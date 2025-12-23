"""
Text Extractor - Extracts images from PDF pages for OCR processing.

Provides the pipeline from PDF document to OCR-ready images,
including page rendering, image extraction, and preprocessing coordination.
"""

import fitz  # PyMuPDF
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

from .ocr_engine import OCREngine, OCRResult
from .image_processor import ImageProcessor


class PageOCRResult:
    """
    Complete OCR result for a PDF page.
    
    Attributes:
        page_number: Page number (0-indexed)
        text_blocks: List of OCRResult objects
        full_text: Combined text from all blocks
        average_confidence: Average confidence across all blocks
        word_count: Number of words recognized
        processing_time: Time taken to process (seconds)
    """
    
    def __init__(
        self,
        page_number: int,
        text_blocks: List[OCRResult],
        processing_time: float = 0.0
    ):
        """
        Initialize page OCR result.
        
        Args:
            page_number: Page number (0-indexed)
            text_blocks: List of OCR results
            processing_time: Processing time in seconds
        """
        self.page_number = page_number
        self.text_blocks = text_blocks
        self.processing_time = processing_time
        
        # Calculate derived properties
        self.full_text = '\n'.join(block.text for block in text_blocks)
        self.word_count = len(self.full_text.split())
        
        if text_blocks:
            self.average_confidence = sum(
                block.confidence for block in text_blocks
            ) / len(text_blocks)
        else:
            self.average_confidence = 0.0
    
    def __repr__(self) -> str:
        return (
            f"PageOCRResult(page={self.page_number}, "
            f"words={self.word_count}, "
            f"confidence={self.average_confidence:.2f})"
        )


class TextExtractor:
    """
    Extracts and processes text from PDF pages using OCR.
    
    Coordinates the entire pipeline: PDF → Image → Preprocessing → OCR → Results
    """
    
    def __init__(
        self,
        ocr_engine: OCREngine,
        image_processor: Optional[ImageProcessor] = None
    ):
        """
        Initialize text extractor.
        
        Args:
            ocr_engine: OCR engine instance
            image_processor: Image processor instance (optional)
        """
        self.ocr_engine = ocr_engine
        self.image_processor = image_processor or ImageProcessor()
    
    def extract_page_image(
        self,
        pdf_document: fitz.Document,
        page_number: int,
        zoom: float = 2.0
    ) -> np.ndarray:
        """
        Extract a PDF page as an image.
        
        Args:
            pdf_document: PyMuPDF document object
            page_number: Page number (0-indexed)
            zoom: Zoom factor for rendering (2.0 = 200 DPI)
            
        Returns:
            Page image as numpy array (RGB)
        """
        # Load page
        page = pdf_document[page_number]
        
        # Create transformation matrix for desired resolution
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to numpy array
        return np.array(img)
    
    def preprocess_image(
        self,
        image: np.ndarray,
        apply_deskew: bool = True,
        apply_despeckle: bool = True,
        apply_enhancement: bool = True,
        apply_bg_suppression: bool = True
    ) -> np.ndarray:
        """
        Apply preprocessing to image before OCR.
        
        Args:
            image: Input image
            apply_deskew: Whether to straighten image
            apply_despeckle: Whether to remove noise
            apply_enhancement: Whether to enhance contrast
            apply_bg_suppression: Whether to suppress background
            
        Returns:
            Preprocessed image
        """
        return self.image_processor.apply_all_enhancements(
            image,
            deskew=apply_deskew,
            despeckle=apply_despeckle,
            enhance=apply_enhancement,
            suppress_bg=apply_bg_suppression
        )
    
    def extract_text_from_page(
        self,
        pdf_document: fitz.Document,
        page_number: int,
        preprocess: bool = True,
        min_confidence: float = 0.5
    ) -> PageOCRResult:
        """
        Extract text from a single PDF page.
        
        Args:
            pdf_document: PyMuPDF document
            page_number: Page number (0-indexed)
            preprocess: Whether to apply preprocessing
            min_confidence: Minimum confidence threshold
            
        Returns:
            PageOCRResult with recognized text
        """
        import time
        start_time = time.time()
        
        # Extract page as image
        image = self.extract_page_image(pdf_document, page_number)
        
        # Apply preprocessing if requested
        if preprocess:
            image = self.preprocess_image(image)
        
        # Perform OCR
        ocr_results = self.ocr_engine.recognize_text(image, min_confidence)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return PageOCRResult(page_number, ocr_results, processing_time)
    
    def extract_text_from_document(
        self,
        pdf_path: str,
        page_range: Optional[Tuple[int, int]] = None,
        preprocess: bool = True,
        min_confidence: float = 0.5,
        progress_callback: Optional[callable] = None
    ) -> List[PageOCRResult]:
        """
        Extract text from entire PDF document or page range.
        
        Args:
            pdf_path: Path to PDF file
            page_range: Optional (start, end) page numbers (0-indexed)
            preprocess: Whether to apply preprocessing
            min_confidence: Minimum confidence threshold
            progress_callback: Optional callback(page_num, total_pages)
            
        Returns:
            List of PageOCRResult objects
        """
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        
        try:
            # Determine page range
            if page_range:
                start_page, end_page = page_range
                start_page = max(0, start_page)
                end_page = min(end_page, len(pdf_document))
            else:
                start_page = 0
                end_page = len(pdf_document)
            
            total_pages = end_page - start_page
            
            # Process each page
            results = []
            for page_num in range(start_page, end_page):
                # Extract text from page
                result = self.extract_text_from_page(
                    pdf_document,
                    page_num,
                    preprocess,
                    min_confidence
                )
                results.append(result)
                
                # Call progress callback
                if progress_callback:
                    progress_callback(page_num - start_page + 1, total_pages)
            
            return results
            
        finally:
            pdf_document.close()
    
    def has_text_layer(self, pdf_document: fitz.Document, page_number: int) -> bool:
        """
        Check if a PDF page has a text layer.
        
        Args:
            pdf_document: PyMuPDF document
            page_number: Page number (0-indexed)
            
        Returns:
            True if page has extractable text, False if scanned image
        """
        page = pdf_document[page_number]
        text = page.get_text().strip()
        
        # Consider page as scanned if very little or no text
        return len(text) > 50  # Threshold: at least 50 characters
    
    def is_scanned_document(
        self,
        pdf_path: str,
        sample_pages: int = 3
    ) -> bool:
        """
        Determine if PDF is a scanned document (no text layer).
        
        Args:
            pdf_path: Path to PDF file
            sample_pages: Number of pages to sample
            
        Returns:
            True if document appears to be scanned
        """
        pdf_document = fitz.open(pdf_path)
        
        try:
            num_pages = len(pdf_document)
            pages_to_check = min(sample_pages, num_pages)
            
            # Sample evenly distributed pages
            scanned_count = 0
            for i in range(pages_to_check):
                page_num = int(i * num_pages / pages_to_check)
                if not self.has_text_layer(pdf_document, page_num):
                    scanned_count += 1
            
            # Consider scanned if majority of sampled pages have no text
            return scanned_count > (pages_to_check / 2)
            
        finally:
            pdf_document.close()
    
    def get_document_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get information about PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with document metadata
        """
        pdf_document = fitz.open(pdf_path)
        
        try:
            # Check if scanned
            is_scanned = self.is_scanned_document(pdf_path)
            
            # Get basic info
            info = {
                'num_pages': len(pdf_document),
                'is_scanned': is_scanned,
                'file_size_mb': Path(pdf_path).stat().st_size / (1024 * 1024),
                'metadata': pdf_document.metadata,
            }
            
            # Estimate processing time (2-3 seconds per page)
            info['estimated_time_seconds'] = len(pdf_document) * 2.5
            
            return info
            
        finally:
            pdf_document.close()
    
    def extract_images_from_page(
        self,
        pdf_document: fitz.Document,
        page_number: int
    ) -> List[np.ndarray]:
        """
        Extract all images embedded in a PDF page.
        
        Args:
            pdf_document: PyMuPDF document
            page_number: Page number (0-indexed)
            
        Returns:
            List of images as numpy arrays
        """
        page = pdf_document[page_number]
        images = []
        
        # Get list of images on page
        image_list = page.get_images()
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            
            # Extract image
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to numpy array
            np_image = np.array(pil_image)
            images.append(np_image)
        
        return images
    
    def get_page_statistics(
        self,
        result: PageOCRResult
    ) -> Dict[str, Any]:
        """
        Get detailed statistics for a page OCR result.
        
        Args:
            result: PageOCRResult object
            
        Returns:
            Dictionary with statistics
        """
        if not result.text_blocks:
            return {
                'word_count': 0,
                'char_count': 0,
                'line_count': 0,
                'avg_confidence': 0.0,
                'min_confidence': 0.0,
                'max_confidence': 0.0,
                'low_confidence_words': 0,
            }
        
        # Calculate statistics
        confidences = [block.confidence for block in result.text_blocks]
        threshold = 0.75
        
        return {
            'word_count': result.word_count,
            'char_count': len(result.full_text),
            'line_count': len(result.text_blocks),
            'avg_confidence': result.average_confidence,
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'low_confidence_words': sum(
                1 for c in confidences if c < threshold
            ),
            'processing_time': result.processing_time,
        }
