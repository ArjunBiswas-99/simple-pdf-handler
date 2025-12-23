"""
Image Processor - Image preprocessing for improved OCR accuracy.

Provides various image enhancement techniques including deskewing,
despeckling, contrast enhancement, and background removal to optimize
images for OCR recognition.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional


class ImageProcessor:
    """
    Image preprocessing utilities for OCR optimization.
    
    Applies various enhancement techniques to improve OCR accuracy
    on scanned documents and low-quality images.
    """
    
    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV format.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            OpenCV image (BGR format)
        """
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array and BGR
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        """
        Convert OpenCV image to PIL format.
        
        Args:
            cv2_image: OpenCV image (BGR format)
            
        Returns:
            PIL Image object
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    @staticmethod
    def deskew_image(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
        """
        Automatically straighten tilted/skewed images.
        
        Uses Hough line detection to find the dominant angle and
        rotates the image to correct the skew.
        
        Args:
            image: Input image as numpy array
            max_angle: Maximum expected skew angle in degrees
            
        Returns:
            Deskewed image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find coordinates of all white pixels
        coords = np.column_stack(np.where(binary > 0))
        
        if len(coords) == 0:
            return image
        
        # Get minimum area rectangle
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        
        # Adjust angle
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90
        
        # Only correct if within expected range
        if abs(angle) > max_angle:
            return image
        
        # Rotate image
        if abs(angle) > 0.5:  # Only rotate if angle is significant
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        
        return image
    
    @staticmethod
    def despeckle_image(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Remove noise and speckles from image.
        
        Uses morphological operations and bilateral filtering to
        remove scan artifacts while preserving edges.
        
        Args:
            image: Input image
            kernel_size: Size of morphological kernel (odd number)
            
        Returns:
            Despeckled image
        """
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Convert to grayscale for morphological operations
        if len(denoised.shape) == 3:
            gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
        else:
            gray = denoised.copy()
        
        # Apply morphological opening to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        # Convert back to original format
        if len(image.shape) == 3:
            return cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR)
        return opening
    
    @staticmethod
    def enhance_image(
        image: np.ndarray,
        contrast: float = 1.5,
        brightness: int = 0
    ) -> np.ndarray:
        """
        Enhance image contrast and brightness for better OCR.
        
        Args:
            image: Input image
            contrast: Contrast multiplier (1.0 = no change, >1.0 = increase)
            brightness: Brightness adjustment (-100 to 100)
            
        Returns:
            Enhanced image
        """
        # Apply contrast and brightness adjustment
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        
        # Apply adaptive histogram equalization for better contrast
        if len(adjusted.shape) == 3:
            # Convert to LAB color space
            lab = cv2.cvtColor(adjusted, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge back
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale - apply CLAHE directly
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(adjusted)
        
        return enhanced
    
    @staticmethod
    def suppress_background(
        image: np.ndarray,
        threshold: int = 200
    ) -> np.ndarray:
        """
        Remove or lighten background colors.
        
        Converts colored backgrounds to white to improve OCR accuracy.
        
        Args:
            image: Input image
            threshold: Brightness threshold for background (0-255)
            
        Returns:
            Image with suppressed background
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )
        
        # Convert back to color if needed
        if len(image.shape) == 3:
            result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        else:
            result = binary
        
        return result
    
    @staticmethod
    def auto_rotate(image: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Detect and correct image orientation.
        
        Args:
            image: Input image
            
        Returns:
            Tuple of (rotated_image, rotation_angle)
            where rotation_angle is 0, 90, 180, or 270
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Detect text orientation using edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Use Hough Line Transform to find dominant lines
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None or len(lines) == 0:
            return image, 0
        
        # Calculate dominant angle
        angles = []
        for line in lines[:20]:  # Use top 20 lines
            rho, theta = line[0]
            angle = np.degrees(theta)
            angles.append(angle)
        
        # Find most common orientation
        median_angle = np.median(angles)
        
        # Determine rotation needed
        if 80 < median_angle < 100:
            rotation = 0
        elif 170 < median_angle or median_angle < 10:
            rotation = 90
        elif 80 < median_angle < 100:
            rotation = 180
        else:
            rotation = 270
        
        # Rotate if needed
        if rotation != 0:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, rotation, 1.0)
            
            # Calculate new dimensions
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            
            # Adjust rotation matrix
            M[0, 2] += (new_w / 2) - center[0]
            M[1, 2] += (new_h / 2) - center[1]
            
            rotated = cv2.warpAffine(image, M, (new_w, new_h), borderValue=(255, 255, 255))
            return rotated, rotation
        
        return image, 0
    
    @staticmethod
    def apply_all_enhancements(
        image: np.ndarray,
        deskew: bool = True,
        despeckle: bool = True,
        enhance: bool = True,
        suppress_bg: bool = True
    ) -> np.ndarray:
        """
        Apply all preprocessing enhancements in optimal order.
        
        Args:
            image: Input image
            deskew: Whether to apply deskewing
            despeckle: Whether to apply despeckling
            enhance: Whether to apply enhancement
            suppress_bg: Whether to suppress background
            
        Returns:
            Fully preprocessed image
        """
        result = image.copy()
        
        # Apply enhancements in optimal order
        if deskew:
            result = ImageProcessor.deskew_image(result)
        
        if despeckle:
            result = ImageProcessor.despeckle_image(result)
        
        if enhance:
            result = ImageProcessor.enhance_image(result)
        
        if suppress_bg:
            result = ImageProcessor.suppress_background(result)
        
        return result
    
    @staticmethod
    def resize_for_ocr(
        image: np.ndarray,
        target_dpi: int = 300
    ) -> np.ndarray:
        """
        Resize image to optimal DPI for OCR.
        
        Args:
            image: Input image
            target_dpi: Target DPI (default 300, optimal for OCR)
            
        Returns:
            Resized image
        """
        # Get current dimensions
        height, width = image.shape[:2]
        
        # Assume 72 DPI if not specified
        current_dpi = 72
        scale_factor = target_dpi / current_dpi
        
        # Only upscale if image is too small
        if scale_factor > 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            resized = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )
            return resized
        
        return image
