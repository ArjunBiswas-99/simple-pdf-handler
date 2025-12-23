"""
OCR Engine - Core text recognition functionality.

Provides the primary interface to PaddleOCR for text recognition with
support for multiple languages and configurable recognition parameters.
"""

import os
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import numpy as np
from PIL import Image


class OCRResult:
    """
    Represents the result of OCR on a single text region.
    
    Attributes:
        text: Recognized text content
        confidence: Recognition confidence score (0-1)
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        language: Language code used for recognition
    """
    
    def __init__(self, text: str, confidence: float, bbox: List[float], language: str = 'en'):
        """
        Initialize OCR result.
        
        Args:
            text: Recognized text
            confidence: Confidence score (0.0 to 1.0)
            bbox: Bounding box [x1, y1, x2, y2]
            language: Language code
        """
        self.text = text
        self.confidence = confidence
        self.bbox = bbox
        self.language = language
    
    def __repr__(self) -> str:
        return f"OCRResult(text='{self.text[:30]}...', confidence={self.confidence:.2f})"


class OCREngine:
    """
    Main OCR engine using PaddleOCR for text recognition.
    
    Handles initialization of the OCR model, language selection,
    and text recognition with confidence scoring.
    """
    
    def __init__(self, language: str = 'en', use_gpu: bool = False):
        """
        Initialize OCR engine.
        
        Args:
            language: Language code for OCR ('en', 'es', 'zh', etc.)
            use_gpu: Whether to use GPU acceleration (if available)
        """
        # Convert 'auto' to 'en' as PaddleOCR doesn't support auto-detection
        # English models work well for most Latin-script languages
        if language == 'auto':
            language = 'en'
        
        self.language = language
        self.use_gpu = use_gpu
        self._ocr_instance = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """
        Initialize PaddleOCR instance.
        
        Lazy initialization to avoid loading the model until needed.
        """
        try:
            from paddleocr import PaddleOCR
            
            # Initialize PaddleOCR with specified language
            # Using minimal parameters for maximum compatibility
            self._ocr_instance = PaddleOCR(
                use_angle_cls=True,  # Enable text orientation detection
                lang=self.language,
            )
            
        except ImportError:
            raise ImportError(
                "PaddleOCR not installed. Please install with: pip install paddleocr"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OCR engine: {str(e)}")
    
    def set_language(self, language: str) -> None:
        """
        Change OCR language.
        
        Args:
            language: New language code
        """
        if language != self.language:
            self.language = language
            self._initialize_engine()
    
    def recognize_text(
        self,
        image: np.ndarray,
        min_confidence: float = 0.5
    ) -> List[OCRResult]:
        """
        Perform OCR on an image.
        
        Args:
            image: Image as numpy array (RGB or grayscale)
            min_confidence: Minimum confidence threshold for results
            
        Returns:
            List of OCRResult objects with recognized text
        """
        if self._ocr_instance is None:
            raise RuntimeError("OCR engine not initialized")
        
        try:
            # Run OCR
            results = self._ocr_instance.ocr(image)
            
            # Parse results with flexible structure handling
            ocr_results = []
            if results and len(results) > 0:
                # Handle both list and nested list structures
                lines = results[0] if isinstance(results[0], list) else results
                
                if lines:
                    for line in lines:
                        try:
                            # Try to extract data - format may vary by version
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                bbox = line[0]
                                text_info = line[1]
                                
                                # Extract text and confidence
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text = str(text_info[0]) if text_info[0] else ""
                                    confidence = float(text_info[1]) if text_info[1] else 0.0
                                elif isinstance(text_info, str):
                                    text = text_info
                                    confidence = 1.0  # Default if no confidence provided
                                else:
                                    continue  # Skip malformed entries
                                
                                # Skip empty text
                                if not text or not text.strip():
                                    continue
                                
                                # Filter by confidence threshold
                                if confidence >= min_confidence:
                                    # Convert bbox to simple format [x1, y1, x2, y2]
                                    if isinstance(bbox, list) and len(bbox) >= 4:
                                        x_coords = [point[0] for point in bbox if isinstance(point, (list, tuple))]
                                        y_coords = [point[1] for point in bbox if isinstance(point, (list, tuple))]
                                        
                                        if x_coords and y_coords:
                                            simple_bbox = [
                                                min(x_coords),
                                                min(y_coords),
                                                max(x_coords),
                                                max(y_coords)
                                            ]
                                        else:
                                            simple_bbox = [0, 0, 100, 100]  # Default bbox
                                    else:
                                        simple_bbox = [0, 0, 100, 100]  # Default bbox
                                    
                                    ocr_results.append(OCRResult(
                                        text=text,
                                        confidence=confidence,
                                        bbox=simple_bbox,
                                        language=self.language
                                    ))
                        except (IndexError, ValueError, TypeError) as parse_error:
                            # Skip malformed lines but continue processing
                            continue
            
            return ocr_results
            
        except Exception as e:
            raise RuntimeError(f"OCR recognition failed: {str(e)}")
    
    def recognize_region(
        self,
        image: np.ndarray,
        region: Tuple[int, int, int, int]
    ) -> Optional[OCRResult]:
        """
        Perform OCR on a specific region of an image.
        
        Args:
            image: Full image as numpy array
            region: Region coordinates (x1, y1, x2, y2)
            
        Returns:
            OCRResult for the region, or None if no text found
        """
        x1, y1, x2, y2 = region
        
        # Extract region
        region_image = image[y1:y2, x1:x2]
        
        # Run OCR on region
        results = self.recognize_text(region_image)
        
        # Adjust bounding boxes to full image coordinates
        for result in results:
            result.bbox = [
                result.bbox[0] + x1,
                result.bbox[1] + y1,
                result.bbox[2] + x1,
                result.bbox[3] + y1
            ]
        
        # Return combined result if multiple lines found
        if results:
            combined_text = ' '.join(r.text for r in results)
            avg_confidence = sum(r.confidence for r in results) / len(results)
            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                bbox=[x1, y1, x2, y2],
                language=self.language
            )
        
        return None
    
    def get_text_only(
        self,
        image: np.ndarray,
        min_confidence: float = 0.5
    ) -> str:
        """
        Get recognized text as a single string.
        
        Args:
            image: Image as numpy array
            min_confidence: Minimum confidence threshold
            
        Returns:
            Combined recognized text
        """
        results = self.recognize_text(image, min_confidence)
        return '\n'.join(r.text for r in results)
    
    def get_average_confidence(
        self,
        image: np.ndarray
    ) -> float:
        """
        Get average confidence score for all recognized text.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Average confidence (0.0 to 1.0)
        """
        results = self.recognize_text(image, min_confidence=0.0)
        
        if not results:
            return 0.0
        
        return sum(r.confidence for r in results) / len(results)
    
    def detect_language(
        self,
        image: np.ndarray
    ) -> str:
        """
        Attempt to detect the language of text in the image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Detected language code (or 'unknown')
        """
        # Try OCR with current language
        results = self.recognize_text(image, min_confidence=0.3)
        
        if not results:
            return 'unknown'
        
        # Analyze character patterns for language detection
        text = ' '.join(r.text for r in results)
        
        # Simple heuristics for common languages
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'zh'  # Chinese
        elif any('\u0600' <= char <= '\u06ff' for char in text):
            return 'ar'  # Arabic
        elif any('\u0900' <= char <= '\u097f' for char in text):
            return 'hi'  # Hindi
        elif any('\u0980' <= char <= '\u09ff' for char in text):
            return 'bn'  # Bengali
        elif any('\u3040' <= char <= '\u30ff' for char in text):
            return 'ja'  # Japanese
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return 'ko'  # Korean
        else:
            return 'en'  # Default to English for Latin scripts
    
    def cleanup(self) -> None:
        """Clean up OCR engine resources."""
        self._ocr_instance = None
    
    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()
