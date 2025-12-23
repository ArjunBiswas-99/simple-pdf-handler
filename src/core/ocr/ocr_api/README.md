# OCR API Test Tool

Simple standalone script to test EasyOCR recognition without the complexity of PDF text layer insertion.

## Purpose

This tool helps you:
- ✅ Verify EasyOCR is recognizing text correctly
- ✅ Test different languages (English, Bengali, Hindi, etc.)
- ✅ See confidence scores and bounding boxes
- ✅ Isolate OCR issues from PDF text layer problems

## Installation

Make sure you have the required dependencies:

```bash
pip install easyocr pymupdf Pillow numpy
```

## Usage

### Basic Usage (English)

```bash
cd simple-pdf-handler/src/core/ocr/ocr_api
python test_ocr.py /path/to/your/document.pdf
```

### Specify Language

```bash
# Bengali
python test_ocr.py /path/to/bengali.pdf bn

# Hindi
python test_ocr.py /path/to/hindi.pdf hi

# English (default)
python test_ocr.py /path/to/english.pdf en
```

## Supported Languages

Common language codes:
- `en` - English
- `bn` - Bengali (বাংলা)
- `hi` - Hindi (हिन्दी)
- `mr` - Marathi (मराठी)
- `ta` - Tamil (தமிழ்)
- `te` - Telugu (తెలుగు)
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- And 70+ more languages

Full list: https://www.jaided.ai/easyocr/

## Output

The script will show:
1. **Initialization time** - How long it takes to load the model
2. **Text blocks** - Each recognized text block with:
   - Recognized text
   - Confidence score (0-100%)
   - Bounding box coordinates
3. **Summary statistics**:
   - Total blocks found
   - Total words
   - Average confidence
   - Complete extracted text

## Example Output

```
======================================================================
OCR TEST SCRIPT
======================================================================
PDF File: test.pdf
Language: bn
======================================================================

Step 1: Extracting first page from PDF...
✓ Extracted page 1 as 2480x3508 image

Step 2: Initializing EasyOCR for language 'bn'...
✓ EasyOCR initialized in 2.3 seconds

Step 3: Running OCR on extracted image...
✓ OCR completed in 5.1 seconds
✓ Found 15 text blocks

======================================================================
OCR RESULTS
======================================================================

[Block 1]
  Text: হ্যালো বিশ্ব
  Confidence: 87.45%
  Bounding Box: [120, 50] → [380, 90]

[Block 2]
  Text: এটি একটি পরীক্ষা
  Confidence: 92.18%
  Bounding Box: [120, 120] → [450, 160]

======================================================================
SUMMARY
======================================================================
Total text blocks: 15
Total words: 42
Average confidence: 89.32%

--- FULL TEXT ---
হ্যালো বিশ্ব এটি একটি পরীক্ষা ...

======================================================================
✓ TEST COMPLETE
======================================================================
```

## Troubleshooting

### "No text detected!"

**Possible causes:**
- Image quality too low (try higher DPI in the script)
- Wrong language selected
- Page actually has no text
- Text is too small or blurry

### Slow Performance

**First run:** EasyOCR downloads models (~100MB per language)
**Subsequent runs:** Should be much faster (models are cached)

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r ../../requirements.txt
```

## Testing Bengali Text

1. Get a PDF with Bengali text
2. Run: `python test_ocr.py your_bengali.pdf bn`
3. Check the output to see if text is recognized correctly
4. If confidence is low (<70%), image quality might be the issue

## Next Steps

If this test shows:
- ✅ **OCR works correctly** → Problem is in PDF text layer insertion (check `pdf_text_layer.py`)
- ❌ **OCR doesn't work** → Need to fix EasyOCR configuration or image preprocessing

## Notes

- This script only tests the **first page** of the PDF
- It extracts the page at 300 DPI (good quality)
- No GPU acceleration is used (runs on CPU)
- Results are printed to console only (not saved)
