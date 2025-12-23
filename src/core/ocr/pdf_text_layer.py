"""
PDF Text Layer - Inserts searchable text layer into PDF documents.

Takes OCR results and embeds them as an invisible text layer in the PDF,
making scanned documents searchable while preserving the original appearance.

Uses pikepdf for proper PDF text layer creation (battle-tested by OCRmyPDF).
"""

import fitz  # PyMuPDF for reading/image extraction
import pikepdf
from typing import List, Optional
from pathlib import Path
from PySide6.QtCore import QThread, Signal
import io

from .text_extractor import PageOCRResult


class PDFTextLayer:
    """
    Manages insertion of OCR text as searchable layer in PDF documents.
    
    Uses pikepdf to create proper PDF text content streams that are
    searchable and selectable while remaining invisible.
    """
    
    def __init__(self):
        """Initialize PDF text layer manager."""
        self.dpi = 72  # PDF coordinate system DPI
    
    def add_text_layer_to_page(
        self,
        pdf: pikepdf.Pdf,
        page_num: int,
        ocr_result: PageOCRResult
    ) -> bool:
        """
        Add OCR text layer to a single PDF page using pikepdf.
        
        Creates invisible text content that overlays the image,
        making it searchable and selectable.
        
        Args:
            pdf: pikepdf.Pdf object
            page_num: Page number (0-indexed)
            ocr_result: OCR results for the page
            
        Returns:
            True if successful, False otherwise
        """
        try:
            page = pdf.pages[page_num]
            
            # Get page dimensions
            mediabox = page.MediaBox
            page_height = float(mediabox[3] - mediabox[1])
            
            # Build text content stream
            text_commands = []
            text_commands.append(b"BT")  # Begin text
            
            for text_block in ocr_result.text_blocks:
                # Get bounding box
                x1, y1, x2, y2 = text_block.bbox
                
                # Convert coordinates (PDF uses bottom-left origin)
                pdf_x = x1
                pdf_y = page_height - y2  # Flip Y coordinate
                
                # Calculate approximate font size
                text_height = y2 - y1
                font_size = max(1, text_height * 0.8)  # Approximate
                
                # Set text position using text matrix
                # Tm sets the text matrix: [a b c d e f]
                # a=font_scale, d=font_scale, e=x_pos, f=y_pos
                text_commands.append(
                    f"1 0 0 1 {pdf_x:.2f} {pdf_y:.2f} Tm".encode()
                )
                
                # Set font and size
                text_commands.append(
                    f"/Helvetica {font_size:.2f} Tf".encode()
                )
                
                # Set rendering mode to invisible (mode 3)
                text_commands.append(b"3 Tr")
                
                # Escape special PDF string characters
                text = text_block.text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                
                # Add text using Tj operator
                text_commands.append(
                    f"({text}) Tj".encode()
                )
            
            text_commands.append(b"ET")  # End text
            
            # Create content stream
            content_stream = b"\n".join(text_commands)
            
            # Add to page contents
            if '/Contents' in page:
                # Append to existing contents
                existing_contents = page.Contents
                
                # Create new stream for our text
                text_stream = pdf.make_stream(content_stream)
                
                # If existing contents is a single stream, make it an array
                if isinstance(existing_contents, pikepdf.Stream):
                    page.Contents = pdf.make_array([existing_contents, text_stream])
                else:
                    # It's already an array, append to it
                    page.Contents = pdf.make_array([*existing_contents, text_stream])
            else:
                # No existing contents, create new
                page.Contents = pdf.make_stream(content_stream)
            
            return True
            
        except Exception as e:
            print(f"Error adding text layer with pikepdf: {e}")
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
        Create searchable PDF from OCR results using pikepdf.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save output PDF
            ocr_results: List of OCR results for all pages
            compress: Whether to compress output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"DEBUG: Opening PDF with pikepdf: {input_path}")
            
            # Open PDF with pikepdf
            pdf = pikepdf.open(input_path)
            
            print(f"DEBUG: PDF opened, has {len(pdf.pages)} pages")
            
            # Add text layer to each OCR'd page
            for ocr_result in ocr_results:
                page_num = ocr_result.page_number
                print(f"DEBUG: Adding text layer to page {page_num} ({len(ocr_result.text_blocks)} blocks)")
                
                success = self.add_text_layer_to_page(pdf, page_num, ocr_result)
                print(f"DEBUG: Text layer added to page {page_num}: {success}")
            
            # Save with compression
            print(f"DEBUG: Saving searchable PDF to {output_path}")
            
            if compress:
                pdf.save(
                    output_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )
            else:
                pdf.save(output_path)
            
            pdf.close()
            
            print("DEBUG: Searchable PDF saved successfully")
            return True
            
        except Exception as e:
            print(f"Error creating searchable PDF with pikepdf: {e}")
            import traceback
            traceback.print_exc()
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
        try:
            print("DEBUG PDFSaveWorker: Starting save operation with pikepdf")
            print(f"DEBUG: Input: {self.input_path}")
            print(f"DEBUG: Output: {self.output_path}")
            print(f"DEBUG: OCR results: {len(self.ocr_results)} pages")
            
            self.progress_updated.emit(0, 100, "Opening PDF...")
            
            total_pages = len(self.ocr_results)
            if total_pages == 0:
                raise ValueError("No OCR results to save")
            
            # Validate OCR results have text blocks
            total_blocks = sum(len(r.text_blocks) for r in self.ocr_results)
            print(f"DEBUG: Total text blocks across all pages: {total_blocks}")
            
            if total_blocks == 0:
                raise ValueError("OCR results contain no text blocks")
            
            # Open PDF with pikepdf
            self.progress_updated.emit(10, 100, "Loading PDF...")
            pdf = pikepdf.open(self.input_path)
            print(f"DEBUG: Opened PDF with pikepdf - {len(pdf.pages)} pages")
            
            # Get list of page numbers to extract
            page_numbers = sorted(set(r.page_number for r in self.ocr_results))
            print(f"DEBUG: Will process pages: {page_numbers}")
            
            # Create output PDF with only selected pages
            self.progress_updated.emit(20, 100, "Extracting pages...")
            output_pdf = pikepdf.new()
            
            # Copy only OCR'd pages
            for page_num in page_numbers:
                output_pdf.pages.append(pdf.pages[page_num])
            
            print(f"DEBUG: Created output PDF with {len(output_pdf.pages)} pages")
            
            # Close source PDF
            pdf.close()
            
            # Create text layer manager
            text_layer = PDFTextLayer()
            
            # Add text layer to each page in output PDF
            # Map original page numbers to new indices
            pages_with_text = 0
            
            for i, ocr_result in enumerate(self.ocr_results):
                if self._cancelled:
                    print("DEBUG: Save cancelled by user")
                    output_pdf.close()
                    return
                
                # Update progress
                progress = 20 + int((i / total_pages) * 70)  # 20-90%
                self.progress_updated.emit(
                    i + 1,
                    total_pages,
                    f"Adding text layer to page {i + 1} of {total_pages}..."
                )
                
                print(f"DEBUG: Processing OCR result {i} - page {ocr_result.page_number} has {len(ocr_result.text_blocks)} text blocks")
                
                if len(ocr_result.text_blocks) > 0:
                    # Page index in output PDF
                    new_page_index = i
                    success = text_layer.add_text_layer_to_page(
                        output_pdf, 
                        new_page_index, 
                        ocr_result
                    )
                    if success:
                        pages_with_text += 1
                    print(f"DEBUG: Added text layer to output page {new_page_index}: {success}")
            
            print(f"DEBUG: Added text layers to {pages_with_text}/{total_pages} pages")
            
            if self._cancelled:
                output_pdf.close()
                return
            
            # Save output PDF
            self.progress_updated.emit(95, 100, "Saving PDF...")
            print(f"DEBUG: Saving output PDF to {self.output_path}")
            
            if self.compress:
                output_pdf.save(
                    self.output_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )
            else:
                output_pdf.save(self.output_path)
            
            output_pdf.close()
            
            # Verify file was created
            from pathlib import Path
            output_file = Path(self.output_path)
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"DEBUG: Output file size: {file_size} bytes")
                if file_size == 0:
                    raise ValueError("Output PDF is 0 bytes - save failed")
            else:
                raise ValueError("Output PDF was not created")
            
            print("DEBUG: Emitting save_completed signal (success)")
            self.save_completed.emit(True, self.output_path)
            
        except Exception as e:
            error_msg = f"Failed to save PDF: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self.save_completed.emit(False, error_msg)
    
    def cancel(self):
        """Cancel PDF save operation."""
        self._cancelled = True
