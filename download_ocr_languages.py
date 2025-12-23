#!/usr/bin/env python3
"""
OCR Language Model Downloader

Downloads PaddleOCR language models for offline use.
Run this script to pre-download models before using OCR.
"""

import sys
from paddleocr import PaddleOCR


def download_language(lang_code: str, lang_name: str) -> bool:
    """
    Download a specific language model.
    
    Args:
        lang_code: Language code (e.g., 'bn', 'hi')
        lang_name: Human-readable language name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading {lang_name} ({lang_code})...", end=" ", flush=True)
        ocr = PaddleOCR(lang=lang_code, show_log=False)
        print("✓ Downloaded successfully")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    """Main function to download language models."""
    print("=" * 60)
    print("PaddleOCR Language Model Downloader")
    print("=" * 60)
    print()
    
    # Common languages to download
    languages = [
        ('en', 'English'),
        ('ch', 'Chinese Simplified'),
        ('bn', 'Bengali'),
        ('hi', 'Hindi'),
        ('ar', 'Arabic'),
        ('french', 'French'),
        ('german', 'German'),
        ('japan', 'Japanese'),
        ('korean', 'Korean'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
    ]
    
    print("This will download OCR models for the following languages:")
    for code, name in languages:
        print(f"  • {name} ({code})")
    print()
    print(f"Total download size: ~{len(languages) * 10} MB")
    print()
    
    # Ask for confirmation
    response = input("Continue? (y/n): ").strip().lower()
    if response not in ('y', 'yes'):
        print("Download cancelled.")
        return
    
    print()
    print("Downloading models...")
    print("-" * 60)
    
    # Download each language
    success_count = 0
    for lang_code, lang_name in languages:
        if download_language(lang_code, lang_name):
            success_count += 1
    
    print("-" * 60)
    print()
    print(f"✓ Successfully downloaded {success_count}/{len(languages)} language models")
    print()
    
    if success_count < len(languages):
        print("Some downloads failed. Check your internet connection and try again.")
        sys.exit(1)
    else:
        print("All language models downloaded successfully!")
        print("You can now use OCR with any of these languages.")
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
