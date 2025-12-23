"""
Background search worker thread.

Performs PDF text search in background to keep UI responsive.
"""

from PySide6.QtCore import QThread, Signal


class SearchWorker(QThread):
    """
    Background worker for PDF text search.
    
    Performs search operation in separate thread to prevent UI blocking.
    Emits progress updates as pages are searched.
    """
    
    # Signals
    progress_updated = Signal(int, int)  # current_page, total_pages
    results_ready = Signal(list)  # search results
    error_occurred = Signal(str)  # error message
    
    def __init__(self, pdf_document, search_term: str, options: dict, parent=None):
        """
        Initialize search worker.
        
        Args:
            pdf_document: PDFDocument instance to search
            search_term: Text to search for
            options: Search options dictionary
            parent: Parent object
        """
        super().__init__(parent)
        
        self._pdf_document = pdf_document
        self._search_term = search_term
        self._options = options
        self._cancelled = False
    
    def run(self):
        """Execute search in background thread."""
        try:
            if not self._pdf_document or not self._pdf_document.is_open:
                self.error_occurred.emit("No document open")
                return
            
            # Perform search with progress updates
            results = self._search_with_progress()
            
            if not self._cancelled:
                self.results_ready.emit(results)
                
        except Exception as e:
            if not self._cancelled:
                self.error_occurred.emit(f"Search failed: {str(e)}")
    
    def _search_with_progress(self) -> list:
        """
        Perform search with progress updates.
        
        Returns:
            List of search results
        """
        import fitz  # PyMuPDF
        
        results = []
        page_count = self._pdf_document.page_count
        
        match_case = self._options.get('match_case', False)
        whole_words = self._options.get('whole_words', False)
        use_regex = self._options.get('regex', False)
        
        # Search each page
        for page_num in range(page_count):
            if self._cancelled:
                break
            
            # Emit progress
            self.progress_updated.emit(page_num + 1, page_count)
            
            # Get page
            page = self._pdf_document._doc[page_num]
            
            # Perform search based on options
            if use_regex:
                # Regex search
                page_text = page.get_text()
                
                import re
                if match_case:
                    pattern = re.compile(self._search_term)
                else:
                    pattern = re.compile(self._search_term, re.IGNORECASE)
                
                matches = list(pattern.finditer(page_text))
                
                for match_idx, match in enumerate(matches):
                    matched_text = match.group()
                    
                    # Find text on page to get bbox
                    text_instances = page.search_for(matched_text, quads=True)
                    
                    if text_instances:
                        for quad in text_instances:
                            bbox = (quad.ul.x, quad.ul.y, quad.lr.x, quad.lr.y)
                            context = self._get_search_context(page_text, match.start(), match.end())
                            
                            results.append({
                                'page': page_num,
                                'text': matched_text,
                                'bbox': bbox,
                                'context': context,
                                'instance': match_idx
                            })
                            break  # Only first instance
            else:
                # Standard search
                search_query = self._search_term
                if whole_words:
                    search_query = f" {self._search_term} "
                
                # Perform search
                text_instances = page.search_for(search_query, quads=True)
                
                # If whole words and no results, try with single boundary
                if whole_words and not text_instances:
                    text_instances = page.search_for(f"{self._search_term} ", quads=True)
                    if not text_instances:
                        text_instances = page.search_for(f" {self._search_term}", quads=True)
                
                # Get page text for context
                page_text = page.get_text()
                
                # Process each match
                for inst_idx, quad in enumerate(text_instances):
                    if self._cancelled:
                        break
                    
                    bbox = (quad.ul.x, quad.ul.y, quad.lr.x, quad.lr.y)
                    
                    # Extract matched text
                    matched_text = page.get_textbox(bbox).strip()
                    if not matched_text:
                        matched_text = self._search_term
                    
                    # Get context
                    context = self._get_search_context_from_bbox(page, bbox, page_text)
                    
                    results.append({
                        'page': page_num,
                        'text': matched_text,
                        'bbox': bbox,
                        'context': context,
                        'instance': inst_idx
                    })
        
        return results
    
    def _get_search_context(self, text: str, start: int, end: int, context_chars: int = 50) -> str:
        """
        Get context around a search match.
        
        Args:
            text: Full text
            start: Match start position
            end: Match end position
            context_chars: Characters before/after to include
            
        Returns:
            Context string with **match** markers
        """
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)
        
        before = text[context_start:start]
        match = text[start:end]
        after = text[end:context_end]
        
        if context_start > 0:
            before = "..." + before.lstrip()
        if context_end < len(text):
            after = after.rstrip() + "..."
        
        return f"{before}**{match}**{after}"
    
    def _get_search_context_from_bbox(self, page, bbox: tuple, page_text: str, context_chars: int = 50) -> str:
        """
        Get context around a search match using bbox.
        
        Args:
            page: PyMuPDF page object
            bbox: Bounding box (x0, y0, x1, y1)
            page_text: Full page text
            context_chars: Characters before/after to include
            
        Returns:
            Context string with **match** markers
        """
        try:
            matched_text = page.get_textbox(bbox).strip()
            
            # Find match position in page text
            match_pos = page_text.lower().find(matched_text.lower())
            
            if match_pos == -1:
                return f"...{matched_text}..."
            
            return self._get_search_context(page_text, match_pos, match_pos + len(matched_text), context_chars)
            
        except:
            matched_text = page.get_textbox(bbox).strip()
            return f"...{matched_text}..."
    
    def cancel(self):
        """Cancel the search operation."""
        self._cancelled = True
