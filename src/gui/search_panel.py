"""
Search panel component for PDF text search.

Provides advanced search functionality with results display and navigation.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QLabel, QCheckBox, QComboBox, QProgressBar,
    QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor

from utils.constants import Icons, Spacing
from utils.icon_manager import get_icon


class SearchResultItem(QWidget):
    """
    Custom widget for displaying a search result.
    
    Shows page number, matched text, and context snippet.
    """
    
    clicked = Signal(int, tuple)  # page_num, bbox
    
    def __init__(self, page_num: int, text: str, context: str, bbox: tuple, parent=None):
        """
        Initialize search result item.
        
        Args:
            page_num: Page number (0-indexed)
            text: Matched text
            context: Context snippet
            bbox: Bounding box (x0, y0, x1, y1)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._page_num = page_num
        self._bbox = bbox
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Page number header
        header_layout = QHBoxLayout()
        
        page_label = QLabel(f"📄 Page {page_num + 1}")
        page_font = QFont()
        page_font.setWeight(QFont.Weight.DemiBold)
        page_font.setPointSize(10)
        page_label.setFont(page_font)
        page_label.setStyleSheet("color: #0066cc;")
        header_layout.addWidget(page_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Context with highlighted match
        context_label = QLabel(self._format_context(context))
        context_label.setWordWrap(True)
        context_label.setTextFormat(Qt.RichText)
        context_label.setStyleSheet("color: #333; padding: 4px;")
        layout.addWidget(context_label)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            SearchResultItem {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            SearchResultItem:hover {
                background: #f0f7ff;
                border-color: #0066cc;
            }
        """)
    
    def _format_context(self, context: str) -> str:
        """
        Format context string with HTML highlighting.
        
        Args:
            context: Context string with **match** markers
            
        Returns:
            HTML formatted string
        """
        # Replace **match** with HTML bold and yellow highlight
        parts = context.split("**")
        result = ""
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                result += part
            else:
                # Matched text - highlight in yellow
                result += f'<span style="background-color: #ffeb3b; font-weight: bold; padding: 2px 4px; border-radius: 2px;">{part}</span>'
        
        return result
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._page_num, self._bbox)
        super().mousePressEvent(event)


class SearchPanel(QWidget):
    """
    Advanced search panel for PDF documents.
    
    Features:
    - Full-text search with options (case, words, regex)
    - Results list with context
    - Previous/next navigation
    - Search history
    - Export results
    """
    
    # Signals
    search_requested = Signal(str, dict)  # search_term, options
    result_selected = Signal(int, tuple)  # page_num, bbox
    clear_highlights = Signal()
    
    def __init__(self, parent=None):
        """Initialize search panel."""
        super().__init__(parent)
        
        self._results = []  # List of search results
        self._current_index = -1  # Current result index
        self._search_history = []  # Recent searches
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the search panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.SMALL)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Search Document")
        title_font = QFont()
        title_font.setWeight(QFont.Weight.DemiBold)
        title_font.setPointSize(11)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Search input with history dropdown
        input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.returnPressed.connect(self._on_search_clicked)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 28px 6px 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        input_layout.addWidget(self.search_input)
        
        # History dropdown button with icon
        self.history_btn = QPushButton("🕐 ⏷")
        self.history_btn.setFixedWidth(50)
        self.history_btn.setFixedHeight(28)
        self.history_btn.setToolTip("Search history")
        self.history_btn.setStyleSheet("""
            QPushButton {
                background: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background: #e0e0e0;
                border-color: #0066cc;
            }
            QPushButton:pressed {
                background: #d0d0d0;
            }
        """)
        self.history_btn.clicked.connect(self._show_history_menu)
        input_layout.addWidget(self.history_btn)
        
        layout.addLayout(input_layout)
        
        # Options section (collapsible)
        options_frame = QFrame()
        options_frame.setFrameShape(QFrame.StyledPanel)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(8, 8, 8, 8)
        options_layout.setSpacing(6)
        
        # Search options checkboxes
        self.match_case_cb = QCheckBox("Match case")
        self.whole_words_cb = QCheckBox("Whole words only")
        self.regex_cb = QCheckBox("Regular expression")
        
        options_layout.addWidget(self.match_case_cb)
        options_layout.addWidget(self.whole_words_cb)
        options_layout.addWidget(self.regex_cb)
        
        layout.addWidget(options_frame)
        
        # Search buttons
        button_layout = QHBoxLayout()
        
        self.search_btn = QPushButton("Find All")
        self.search_btn.setIcon(get_icon('search', 16))
        self.search_btn.clicked.connect(self._on_search_clicked)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0052a3;
            }
            QPushButton:pressed {
                background: #003d7a;
            }
            QPushButton:disabled {
                background: #ccc;
            }
        """)
        button_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Searching... %p%")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Results header with navigation
        results_header_layout = QHBoxLayout()
        
        self.results_label = QLabel("Results:")
        results_label_font = QFont()
        results_label_font.setWeight(QFont.Weight.DemiBold)
        self.results_label.setFont(results_label_font)
        results_header_layout.addWidget(self.results_label)
        
        results_header_layout.addStretch()
        
        # Navigation buttons
        self.prev_btn = QPushButton("↑ Prev")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self._on_previous_clicked)
        self.prev_btn.setFixedWidth(70)
        results_header_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next ↓")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.next_btn.setFixedWidth(70)
        results_header_layout.addWidget(self.next_btn)
        
        layout.addLayout(results_header_layout)
        
        # Results count and statistics
        self.results_count = QLabel("0 matches")
        self.results_count.setProperty("secondary", True)
        self.results_count.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(self.results_count)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setSpacing(4)
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #fafafa;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
        """)
        layout.addWidget(self.results_list)
        
        # Export buttons (bottom)
        export_layout = QHBoxLayout()
        
        self.export_txt_btn = QPushButton("📄 Export TXT")
        self.export_txt_btn.setEnabled(False)
        self.export_txt_btn.clicked.connect(self._on_export_txt)
        export_layout.addWidget(self.export_txt_btn)
        
        self.export_csv_btn = QPushButton("📊 Export CSV")
        self.export_csv_btn.setEnabled(False)
        self.export_csv_btn.clicked.connect(self._on_export_csv)
        export_layout.addWidget(self.export_csv_btn)
        
        layout.addLayout(export_layout)
    
    def _on_search_text_changed(self, text: str):
        """Handle search input text change."""
        # Enable/disable search button
        self.search_btn.setEnabled(bool(text.strip()))
    
    def _on_search_clicked(self):
        """Handle search button click."""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            return
        
        # Add to history
        if search_term not in self._search_history:
            self._search_history.insert(0, search_term)
            # Keep only last 10 searches
            self._search_history = self._search_history[:10]
        
        # Get options
        options = {
            'match_case': self.match_case_cb.isChecked(),
            'whole_words': self.whole_words_cb.isChecked(),
            'regex': self.regex_cb.isChecked()
        }
        
        # Show progress
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # Emit search signal
        self.search_requested.emit(search_term, options)
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.search_input.clear()
        self.clear_results()
        self.clear_highlights.emit()
    
    def _on_previous_clicked(self):
        """Navigate to previous search result."""
        if self._current_index > 0:
            self._current_index -= 1
            self._select_result(self._current_index)
    
    def _on_next_clicked(self):
        """Navigate to next search result."""
        if self._current_index < len(self._results) - 1:
            self._current_index += 1
            self._select_result(self._current_index)
    
    def _select_result(self, index: int):
        """
        Select and navigate to a result.
        
        Args:
            index: Result index
        """
        if 0 <= index < len(self._results):
            result = self._results[index]
            
            # Update list selection
            self.results_list.setCurrentRow(index)
            
            # Update navigation buttons
            self.prev_btn.setEnabled(index > 0)
            self.next_btn.setEnabled(index < len(self._results) - 1)
            
            # Update count display
            self._update_results_count()
            
            # Emit signal
            self.result_selected.emit(result['page'], result['bbox'])
    
    def _show_history_menu(self):
        """Show search history dropdown menu."""
        if not self._search_history:
            return
        
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        for term in self._search_history:
            action = menu.addAction(term)
            action.triggered.connect(lambda checked=False, t=term: self._use_history_item(t))
        
        menu.addSeparator()
        
        clear_action = menu.addAction("Clear History")
        clear_action.triggered.connect(self._clear_history)
        
        # Show menu below button
        menu.exec(self.history_btn.mapToGlobal(self.history_btn.rect().bottomLeft()))
    
    def _use_history_item(self, term: str):
        """Use a search term from history."""
        self.search_input.setText(term)
        self._on_search_clicked()
    
    def _clear_history(self):
        """Clear search history."""
        self._search_history = []
    
    def display_results(self, results: list):
        """
        Display search results.
        
        Args:
            results: List of search result dictionaries
        """
        self._results = results
        self._current_index = 0 if results else -1
        
        # Clear existing results
        self.results_list.clear()
        
        # Hide progress
        self.progress_bar.hide()
        
        if not results:
            # Show no results message
            self.results_count.setText("No matches found")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.export_txt_btn.setEnabled(False)
            self.export_csv_btn.setEnabled(False)
            return
        
        # Add results to list
        for result in results:
            # Create custom widget for result
            result_widget = SearchResultItem(
                result['page'],
                result['text'],
                result['context'],
                result['bbox']
            )
            result_widget.clicked.connect(lambda p, b: self.result_selected.emit(p, b))
            
            # Add to list
            item = QListWidgetItem(self.results_list)
            item.setSizeHint(result_widget.sizeHint())
            self.results_list.setItemWidget(item, result_widget)
        
        # Update count
        self._update_results_count()
        
        # Enable navigation and export
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(len(results) > 1)
        self.export_txt_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        
        # Select first result
        if results:
            self._select_result(0)
    
    def _update_results_count(self):
        """Update results count label."""
        total = len(self._results)
        
        if total == 0:
            self.results_count.setText("No matches found")
        else:
            # Count unique pages
            unique_pages = len(set(r['page'] for r in self._results))
            
            if self._current_index >= 0:
                self.results_count.setText(
                    f"Match {self._current_index + 1} of {total} "
                    f"({unique_pages} page{'s' if unique_pages != 1 else ''})"
                )
            else:
                self.results_count.setText(
                    f"{total} match{'es' if total != 1 else ''} "
                    f"on {unique_pages} page{'s' if unique_pages != 1 else ''}"
                )
    
    def clear_results(self):
        """Clear search results."""
        self._results = []
        self._current_index = -1
        self.results_list.clear()
        self.results_count.setText("0 matches")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.export_txt_btn.setEnabled(False)
        self.export_csv_btn.setEnabled(False)
        self.progress_bar.hide()
    
    def set_progress(self, value: int):
        """
        Set search progress.
        
        Args:
            value: Progress percentage (0-100)
        """
        self.progress_bar.setValue(value)
    
    def _on_export_txt(self):
        """Export results to text file."""
        if not self._results:
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Search Results",
            "search_results.txt",
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Search Results\n")
                    f.write(f"{'=' * 50}\n\n")
                    f.write(f"Search term: {self.search_input.text()}\n")
                    f.write(f"Total matches: {len(self._results)}\n\n")
                    
                    for i, result in enumerate(self._results, 1):
                        f.write(f"Match {i}:\n")
                        f.write(f"  Page: {result['page'] + 1}\n")
                        f.write(f"  Text: {result['text']}\n")
                        f.write(f"  Context: {result['context'].replace('**', '')}\n")
                        f.write(f"\n")
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Export Failed", f"Failed to export results:\n{str(e)}")
    
    def _on_export_csv(self):
        """Export results to CSV file."""
        if not self._results:
            return
        
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Search Results",
            "search_results.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['Match #', 'Page', 'Text', 'Context'])
                    
                    # Write results
                    for i, result in enumerate(self._results, 1):
                        writer.writerow([
                            i,
                            result['page'] + 1,
                            result['text'],
                            result['context'].replace('**', '')
                        ])
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Export Failed", f"Failed to export results:\n{str(e)}")
