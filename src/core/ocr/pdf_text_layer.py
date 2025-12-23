"""
PDF Text Layer - Inserts searchable text layer into PDF documents.

Takes OCR results and embeds them as an invisible text layer in the PDF,
making scanned documents searchable while preserving the original appearance.
"""

import fitz  # PyMuPDF
from typing import List, Optional
from pathlib import Path
from PySide6.QtCore import QThread, Signal

from .text_extractor import PageOCRResult


class PDFTextLayer:
    """
    Manages insertion of OCR text as searchable layer in PDF documents.
    
    Creates invisible text overlay that matches the visual appearance,
    enabling text search and selection in scanned documents.
    """
    
    def __init__(self):
        """Initialize PDF text layer manager."""
        self.text_opacity = 0.0  # Invisible text
        self.preserve_original = True
    
    def add_text_layer_to_page(
        self,
        page: fitz.Page,
        ocr_result: PageOCRResult,
        font_size: float = 12.0
    ) -> bool:
        """
        Add OCR text layer to a single PDF page.
        
        Args:
            page: PyMuPDF page object
            ocr_result: OCR results for the page
            font_size: Base font size for text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use insert_text instead of insert_textbox for proper searchable text layer
            for text_block in ocr_result.text_blocks:
                # Get bounding box
                x1, y1, x2, y2 = text_block.bbox
                
                # Insert text at position using insert_text (more reliable for searchable text)
                # Use bottom-left corner as insertion point (PyMuPDF convention)
                point = fitz.Point(x1, y2)
                
                # Insert invisible text that can be searched and selected
                page.insert_text(
                    point,
                    text_block.text,
                    fontsize=font_size,
                    color=(1, 1, 1),  # White text (invisible on white background)
                    overlay=True,
                    render_mode=3  # Fill text with rendering mode for searchability
                )
            
            return True
            
        except Exception as e:
            print(f"Error adding text layer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_searchable_pdf(
        self,
        input_path: str,
        output_path: str,
        ocr_results: List[PageOCRResult],
        compress: bool = True
    ) -> bool:
        """
        Create searchable PDF from OCR results.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save output PDF
            ocr_results: List of OCR results for all pages
            compress: Whether to compress output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open input PDF
            doc = fitz.open(input_path)
            
            # Add text layer to each page
            for ocr_result in ocr_results:
                page = doc[ocr_result.page_number]
                self.add_text_layer_to_page(page, ocr_result)
            
            # Save with compression
            if compress:
                doc.save(
                    output_path,
                    garbage=4,  # Maximum compression
                    deflate=True,
                    clean=True
                )
            else:
                doc.save(output_path)
            
            doc.close()
            return True
            
        except Exception as e:
            print(f"Error creating searchable PDF: {e}")
            return False
    
    def optimize_pdf_size(
        self,
        pdf_path: str,
        output_path: Optional[str] = None
    ) -> bool:
        """
        Optimize PDF file size after OCR.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Output path (or overwrite if None)
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(pdf_path)
            
            if output_path is None:
                output_path = pdf_path
            
            # Save with maximum compression
            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True,
                pretty=False
            )
            
            doc.close()
            return True
            
        except Exception as e:
            print(f"Error optimizing PDF: {e}")
            return False


class PDFSaveWorker(QThread):
    """Background worker thread for PDF saving operations."""
    
    # Signals
    progress_updated = Signal(int, int, str)  # current, total, message
    save_completed = Signal(bool, str)  # success, output_path or error message
    
    def __init__(
        self,
        input_path: str,
        output_path: str,
        ocr_results: List[PageOCRResult],
        compress: bool = True
    ):
        """
        Initialize PDF save worker.
        
        Args:
            input_path: Input PDF path
            output_path: Output PDF path
            ocr_results: List of OCR results for all pages
            compress: Whether to compress output
        """
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.ocr_results = ocr_results
        self.compress = compress
        self._cancelled = False
    
    def run(self):
        """Execute PDF save operation in background thread."""
        source_doc = None
        output_doc = None
        try:
            print("DEBUG PDFSaveWorker: Starting save operation")
            print(f"DEBUG: Input: {self.input_path}")
            print(f"DEBUG: Output: {self.output_path}")
            print(f"DEBUG: OCR results: {len(self.ocr_results)} pages")
            
            self.progress_updated.emit(0, 100, "Opening PDF...")
            
            # Open source PDF
            source_doc = fitz.open(self.input_path)
            print(f"DEBUG: Opened source PDF - {len(source_doc)} pages")
            
            total_pages = len(self.ocr_results)
            if total_pages == 0:
                raise ValueError("No OCR results to save")
            
            # Validate OCR results have text blocks
            total_blocks = sum(len(r.text_blocks) for r in self.ocr_results)
            print(f"DEBUG: Total text blocks across all pages: {total_blocks}")
            
            if total_blocks == 0:
                raise ValueError("OCR results contain no text blocks")
            
            # Create NEW output PDF with only OCR'd pages
            output_doc = fitz.open()
            print(f"DEBUG: Created new output PDF")
            
            # Get list of page numbers to extract
            page_numbers = sorted(set(r.page_number for r in self.ocr_results))
            print(f"DEBUG: Extracting pages: {page_numbers}")
            
            # Copy only the OCR'd pages from source to output
            self.progress_updated.emit(10, 100, "Extracting pages...")
            output_doc.insert_pdf(source_doc, from_page=min(page_numbers), to_page=max(page_numbers))
            print(f"DEBUG: Copied {len(output_doc)} pages to output PDF")
            
            # Create text layer manager
            text_layer = PDFTextLayer()
            
            # Add text layer to each page in the NEW document
            # Map original page numbers to new document indices
            pages_with_text = 0
            for i, ocr_result in enumerate(self.ocr_results):
                if self._cancelled:
                    print("DEBUG: Save cancelled by user")
                    if source_doc:
                        source_doc.close()
                    if output_doc:
                        output_doc.close()
                    return
                
                # Update progress
                progress = 10 + int((i / total_pages) * 80)  # 10-90% for page processing
                self.progress_updated.emit(
                    i + 1,
                    total_pages,
                    f"Adding text layer to page {i + 1} of {total_pages}..."
                )
                
                # Debug: Show what we're processing
                print(f"DEBUG: OCR result {i} - page {ocr_result.page_number} has {len(ocr_result.text_blocks)} text blocks")
                
                if len(ocr_result.text_blocks) > 0:
                    # Map to new document index (pages are sequential starting from 0)
                    new_page_index = i
                    if new_page_index < len(output_doc):
                        page = output_doc[new_page_index]
                        success = text_layer.add_text_layer_to_page(page, ocr_result)
                        if success:
                            pages_with_text += 1
                        print(f"DEBUG: Added text layer to output page {new_page_index}: {success}")
            
            print(f"DEBUG: Added text layers to {pages_with_text}/{total_pages} pages")
            
            if self._cancelled:
                if source_doc:
                    source_doc.close()
                if output_doc:
                    output_doc.close()
                return
            
            # Close source document (no longer needed)
            source_doc.close()
            source_doc = None
            
            # Save output document with compression
            self.progress_updated.emit(95, 100, "Saving PDF...")
            print(f"DEBUG: Saving output document to {self.output_path}")
            print(f"DEBUG: Output document has {len(output_doc)} pages")
            
            # Always use maximum compression for output (it's a new small PDF)
            if self.compress:
                output_doc.save(
                    self.output_path,
                    garbage=4,  # Maximum compression
                    deflate=True,
                    clean=True
                )
            else:
                output_doc.save(self.output_path)
            
            print("DEBUG: PDF saved successfully")
            output_doc.close()
            
            # Verify file was created and has content
            from pathlib import Path
            output_file = Path(self.output_path)
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"DEBUG: Output file size: {file_size} bytes")
                if file_size == 0:
                    raise ValueError("Output PDF is 0 bytes - save failed")
            else:
                raise ValueError("Output PDF was not created")
            
            # Emit success
            print("DEBUG: Emitting save_completed signal (success)")
            self.save_completed.emit(True, self.output_path)
            
        except Exception as e:
            error_msg = f"Failed to save PDF: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Clean up both documents
            if source_doc:
                try:
                    source_doc.close()
                except:
                    pass
            
            if output_doc:
                try:
                    output_doc.close()
                except:
                    pass
            
            self.save_completed.emit(False, error_msg)
    
    def cancel(self):
        """Cancel PDF save operation."""
        self._cancelled = True
