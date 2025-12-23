# Installing OCR Language Models

## Overview

The `requirements.txt` already includes PaddleOCR with full support for 80+ languages. However, language models are **downloaded on first use** to save initial installation size.

## Supported Languages

PaddleOCR supports these languages (and many more):

### Common Languages
- **English** (en) - Pre-installed
- **Chinese Simplified** (ch) - Pre-installed  
- **Chinese Traditional** (chinese_cht)
- **Bengali** (bn)
- **Hindi** (hi)
- **Arabic** (ar)
- **French** (french)
- **German** (german)
- **Japanese** (japan)
- **Korean** (korean)
- **Spanish** (es)
- **Portuguese** (pt)
- **Russian** (ru)

### All Supported Languages
English, Chinese, Chinese Traditional, Afrikaans, Arabic, Azerbaijani, Bosnian, Bulgarian, Bengali, Czech, Welsh, Danish, German, Greek, Spanish, Estonian, Persian, Finnish, French, Irish, Croatian, Hungarian, Indonesian, Icelandic, Italian, Japanese, Korean, Kurdish, Lithuanian, Latvian, Maori, Marathi, Malay, Maltese, Dutch, Norwegian, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Albanian, Swedish, Swahili, Tamil, Telugu, Thai, Tagalog, Turkish, Ukrainian, Urdu, Uzbek, Vietnamese, Occitan

## How Language Models Work

1. **First Use**: When you select a language for OCR, PaddleOCR automatically downloads the model (~8-10MB per language)
2. **Cached**: Models are cached in `~/.paddleocr/` directory
3. **Automatic**: No manual installation needed!

## Installing All Languages at Once (Optional)

If you want to pre-download models for specific languages:

### Method 1: Auto-download on first use
Just run OCR with that language - the model downloads automatically!

### Method 2: Manual pre-download
```bash
# Activate your virtual environment first
cd simple-pdf-handler

# Download specific language models
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='bn')"  # Bengali
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='hi')"  # Hindi
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ar')"  # Arabic
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='fr')"  # French
# ... add more languages as needed
```

### Method 3: Download all common languages
```bash
# Run this Python script to download multiple language models
python -c "
from paddleocr import PaddleOCR
languages = ['en', 'ch', 'bn', 'hi', 'ar', 'fr', 'german', 'japan', 'korean', 'es', 'pt', 'ru']
for lang in languages:
    print(f'Downloading {lang}...')
    try:
        PaddleOCR(lang=lang)
        print(f'✓ {lang} downloaded successfully')
    except Exception as e:
        print(f'✗ {lang} failed: {e}')
"
```

## Troubleshooting

### "No models available for language X"

This usually means:
1. **First run**: Model is being downloaded (wait for completion)
2. **Network issue**: Check internet connection
3. **Typo**: Verify language code is correct

### Model Download Location

Models are stored in:
- **Linux/Mac**: `~/.paddleocr/whl/`
- **Windows**: `C:\Users\<username>\.paddleocr\whl\`

### Disk Space

- Each language model: ~8-10 MB
- All 80+ languages: ~800 MB total
- Pre-installed (en, ch): ~20 MB

## Using Bengali (bn)

Since you want to use Bengali:

1. **First OCR run**: Select "Bengali (bn)" from language dropdown
2. **Wait for download**: First run takes 10-30 seconds to download model
3. **Subsequent runs**: Instant, uses cached model

## Verification

To verify Bengali is working:

```bash
cd simple-pdf-handler
python -c "
from paddleocr import PaddleOCR
print('Initializing Bengali OCR...')
ocr = PaddleOCR(lang='bn')
print('✓ Bengali model ready!')
print('Model location:', ocr.text_detector.__dict__.get('det_model_dir', 'cached'))
"
```

## Full Installation

If you want to ensure everything is set up:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Pre-download Bengali
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='bn')"

# 3. Run the application
python run.py
```

## Performance Notes

- **GPU**: If you have CUDA-enabled GPU, install `paddlepaddle-gpu` for 3-5x faster OCR
- **CPU**: Works fine on CPU, just slower (~2-5 seconds per page)
- **Memory**: Each language model uses ~50-100MB RAM when loaded

## Need Help?

If you encounter issues with specific languages, check:
1. PaddleOCR documentation: https://github.com/PaddlePaddle/PaddleOCR
2. Supported languages list: https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md
