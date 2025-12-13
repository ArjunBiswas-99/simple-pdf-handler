"""
Simple PDF Handler - Search Panel Content Widget

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SearchPanel(QWidget):
    """
    Search panel content for the sidebar accordion section.
    Contains search input, options, results list, and navigation controls.
    
    This separates search UI concerns from the search logic and results management.
    """
    
    # Signals for search operations
    search_requested = pyqtSignal(str, bool)  # (search_text, case_sensitive)
    next_match_requested = pyqtSignal()
    previous_match_requested = pyqtSignal()
    result_selected = pyqtSignal(int, int)  # (page_number, match_index)
    
    def __init__(self, parent=None):
        """
        Initialize the search panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the search panel layout and components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Search input section
        input_label = QLabel("Search text:")
        layout.addWidget(input_label)
        
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Enter text to search...")
        self._search_input.returnPressed.connect(self._on_search_enter)
        layout.addWidget(self._search_input)
        
        # Options section
        self._case_sensitive_cb = QCheckBox("Case sensitive")
        layout.addWidget(self._case_sensitive_cb)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self._on_search_clicked)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(search_btn)
        
        # Progress bar (hidden by default)
        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximumHeight(4)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)
        
        # Results section
        results_header = QHBoxLayout()
        results_label = QLabel("Results:")
        results_header.addWidget(results_label)
        
        self._match_counter = QLabel("No matches")
        self._match_counter.setStyleSheet("color: #666;")
        results_header.addWidget(self._match_counter)
        results_header.addStretch()
        
        layout.addLayout(results_header)
        
        # Results list
        self._results_list = QListWidget()
        self._results_list.setAlternatingRowColors(True)
        self._results_list.itemClicked.connect(self._on_result_clicked)
        self._results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                color: #000000;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
                color: #000000;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e5f3ff;
                color: #000000;
            }
        """)
        layout.addWidget(self._results_list)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self._prev_btn = QPushButton("◀ Previous")
        self._prev_btn.setEnabled(False)
        self._prev_btn.clicked.connect(self._on_previous_clicked)
        nav_layout.addWidget(self._prev_btn)
        
        self._next_btn = QPushButton("Next ▶")
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self._on_next_clicked)
        nav_layout.addWidget(self._next_btn)
        
        layout.addLayout(nav_layout)
        
        # Style navigation buttons
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #a0a0a0;
            }
        """
        self._prev_btn.setStyleSheet(button_style)
        self._next_btn.setStyleSheet(button_style)
    
    def _on_search_clicked(self) -> None:
        """Handle search button click."""
        search_text = self._search_input.text().strip()
        if search_text:
            case_sensitive = self._case_sensitive_cb.isChecked()
            self.search_requested.emit(search_text, case_sensitive)
    
    def _on_search_enter(self) -> None:
        """Handle Enter key press in search input."""
        self._on_search_clicked()
    
    def _on_next_clicked(self) -> None:
        """Handle next button click."""
        self.next_match_requested.emit()
    
    def _on_previous_clicked(self) -> None:
        """Handle previous button click."""
        self.previous_match_requested.emit()
    
    def _on_result_clicked(self, item: QListWidgetItem) -> None:
        """
        Handle result item click.
        
        Args:
            item: Clicked list item
        """
        # Extract page number and match index from item data
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            page_num, match_idx = data
            self.result_selected.emit(page_num, match_idx)
    
    def set_progress(self, current: int, total: int) -> None:
        """
        Update search progress.
        
        Args:
            current: Current progress value
            total: Total progress value
        """
        if total > 0:
            progress = int((current / total) * 100)
            self._progress_bar.setValue(progress)
    
    def show_progress(self, show: bool) -> None:
        """
        Show or hide the progress bar.
        
        Args:
            show: True to show, False to hide
        """
        self._progress_bar.setVisible(show)
    
    def set_match_counter(self, text: str) -> None:
        """
        Update the match counter text.
        
        Args:
            text: Counter text to display
        """
        self._match_counter.setText(text)
    
    def clear_results(self) -> None:
        """Clear all search results from the list."""
        self._results_list.clear()
    
    def add_result(self, page_num: int, match_idx: int, context: str, is_current: bool = False) -> None:
        """
        Add a search result to the results list.
        
        Args:
            page_num: Page number (0-indexed)
            match_idx: Match index on the page
            context: Text context showing the match
            is_current: Whether this is the currently selected match
        """
        # Create list item
        item_text = f"Page {page_num + 1}: {context}"
        item = QListWidgetItem(item_text)
        
        # Store page number and match index as item data
        item.setData(Qt.ItemDataRole.UserRole, (page_num, match_idx))
        
        # Highlight current match
        if is_current:
            item.setSelected(True)
            font = QFont()
            font.setBold(True)
            item.setFont(font)
        
        self._results_list.addItem(item)
    
    def update_results_list(self, results: list, current_match_info: tuple = None) -> None:
        """
        Update the entire results list.
        
        Args:
            results: List of (page_num, match_idx, context) tuples
            current_match_info: Tuple of (page_num, match_idx) for current match
        """
        self.clear_results()
        
        current_page = None
        current_idx = None
        if current_match_info:
            current_page, current_idx = current_match_info
        
        for page_num, match_idx, context in results:
            is_current = (page_num == current_page and match_idx == current_idx)
            self.add_result(page_num, match_idx, context, is_current)
    
    def enable_navigation(self, enabled: bool) -> None:
        """
        Enable or disable navigation buttons.
        
        Args:
            enabled: True to enable, False to disable
        """
        self._prev_btn.setEnabled(enabled)
        self._next_btn.setEnabled(enabled)
    
    def get_search_text(self) -> str:
        """
        Get the current search text.
        
        Returns:
            Search text from input field
        """
        return self._search_input.text().strip()
    
    def is_case_sensitive(self) -> bool:
        """
        Check if case-sensitive search is enabled.
        
        Returns:
            True if case-sensitive, False otherwise
        """
        return self._case_sensitive_cb.isChecked()
    
    def focus_search_input(self) -> None:
        """Set focus to the search input field."""
        self._search_input.setFocus()
        self._search_input.selectAll()
