#!/usr/bin/env python3
"""
OCR Test Script - Quick verification tool for EasyOCR

Tests OCR recognition on a PDF file and prints results to console.
This isolates OCR recognition from PDF text layer insertion.

Usage:
    python test_ocr.py /path/to/your/file.pdf [language]
    
Examples:
    python test_ocr.py document.pdf
    python test_ocr.py document.pdf en
    python test_ocr.py bengali_doc.pdf bn
"""

import sys
import os
from pathlib import Path
import time

# Add parent directories to path so we can import from src
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(src_dir))

import fitz  # PyMuPDF
from PIL import Image
import io
import easyocr


def extract_page_as_image(pdf_path, page_num=0, dpi=300):
    """
    Extract a page from PDF as PIL Image.
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number to extract (0-indexed)
        dpi: Resolution for image extraction
        
    Returns:
        PIL Image object
    """
    doc = fitz.open(pdf_path)
    
    if page_num >= len(doc):
        print(f"Error: Page {page_num} doesn't exist. PDF has {len(doc)} pages.")
        doc.close()
        return None
    
    page = doc[page_num]
    
    # Convert page to image at specified DPI
    mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default DPI
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    
    doc.close()
    
    print(f"✓ Extracted page {page_num + 1} as {img.size[0]}x{img.size[1]} image")
    return img


def test_ocr(pdf_path, language='en'):
    """
    Test OCR on first page of PDF.
    
    Args:
        pdf_path: Path to PDF file
        language: Language code (en, bn, hi, etc.)
    """
    print("\n" + "="*70)
    print("OCR TEST SCRIPT")
    print("="*70)
    print(f"PDF File: {pdf_path}")
    print(f"Language: {language}")
    print("="*70 + "\n")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return
    
    # Extract first page as image
    print("Step 1: Extracting first page from PDF...")
    img = extract_page_as_image(pdf_path, page_num=0)
    
    if img is None:
        return
    
    # Initialize EasyOCR
    print(f"\nStep 2: Initializing EasyOCR for language '{language}'...")
    start_time = time.time()
    
    try:
        reader = easyocr.Reader([language], gpu=False)
        init_time = time.time() - start_time
        print(f"✓ EasyOCR initialized in {init_time:.1f} seconds")
    except Exception as e:
        print(f"❌ Error initializing EasyOCR: {e}")
        return
    
    # Run OCR
    print("\nStep 3: Running OCR on extracted image...")
    ocr_start = time.time()
    
    try:
        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np
        img_array = np.array(img)
        
        results = reader.readtext(img_array)
        ocr_time = time.time() - ocr_start
        
        print(f"✓ OCR completed in {ocr_time:.1f} seconds")
        print(f"✓ Found {len(results)} text blocks")
        
    except Exception as e:
        print(f"❌ Error during OCR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "="*70)
    print("OCR RESULTS")
    print("="*70)
    
    if not results:
        print("\n❌ No text detected!")
        print("\nPossible reasons:")
        print("  - Image quality too low")
        print("  - Wrong language selected")
        print("  - Page contains no text")
        return
    
    total_text = []
    
    for i, (bbox, text, confidence) in enumerate(results, 1):
        print(f"\n[Block {i}]")
        print(f"  Text: {text}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Bounding Box: {bbox[0]} → {bbox[2]}")
        
        total_text.append(text)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total text blocks: {len(results)}")
    print(f"Total words: {sum(len(text.split()) for _, text, _ in results)}")
    
    avg_confidence = sum(conf for _, _, conf in results) / len(results)
    print(f"Average confidence: {avg_confidence:.2%}")
    
    print("\n--- FULL TEXT ---")
    print(" ".join(total_text))
    
    print("\n" + "="*70)
    print("✓ TEST COMPLETE")
    print("="*70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <pdf_file> [language]")
        print("\nExamples:")
        print("  python test_ocr.py document.pdf")
        print("  python test_ocr.py document.pdf en")
        print("  python test_ocr.py bengali.pdf bn")
        print("\nSupported languages: en (English), bn (Bengali), hi (Hindi), etc.")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en'
    
    test_ocr(pdf_path, language)


if __name__ == "__main__":
    main()
