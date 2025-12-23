"""
OCR Dialogs - Main dialog interfaces for OCR operations.

Includes OCR configuration dialog, progress tracking, and completion dialogs
with professional UI and comprehensive options.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QCheckBox, QComboBox, QSpinBox, QGroupBox,
    QProgressBar, QTextEdit, QLineEdit, QFileDialog, QButtonGroup,
    QWidget
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont
import random
from pathlib import Path

from utils.constants import (
    Colors, Fonts, Spacing, OCRLanguages, OCRSettings, OCRMessages
)
from utils.config import get_config
from utils.icon_manager import get_icon


class OCRDialog(QDialog):
    """Main OCR configuration dialog with all options."""
    
    ocr_started = Signal(dict)  # OCR parameters
    settings_requested = Signal()
    
    def __init__(self, num_pages: int, current_page: int = 0, parent=None):
        """
        Initialize OCR dialog.
        
        Args:
            num_pages: Total pages in document
            current_page: Current page number (0-indexed)
            parent: Parent widget
        """
        super().__init__(parent)
        self.num_pages = num_pages
        self.current_page = current_page
        self.config = get_config()
        
        self.setWindowTitle("Recognize Text (OCR)")
        self.setMinimumWidth(500)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Pages section
        pages_group = self._create_pages_section()
        layout.addWidget(pages_group)
        
        # Language section
        lang_group = self._create_language_section()
        layout.addWidget(lang_group)
        
        # Output format section
        output_group = self._create_output_section()
        layout.addWidget(output_group)
        
        # Processing options
        process_group = self._create_processing_section()
        layout.addWidget(process_group)
        
        # Advanced features
        advanced_group = self._create_advanced_section()
        layout.addWidget(advanced_group)
        
        # Estimate display
        self.estimate_label = QLabel()
        self.estimate_label.setStyleSheet("padding: 8px; background: #F0F0F0; border-radius: 4px;")
        layout.addWidget(self.estimate_label)
        self._update_estimate()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        settings_btn = QPushButton("Settings...")
        settings_btn.clicked.connect(self.settings_requested.emit)
        button_layout.addWidget(settings_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        start_btn = QPushButton("Start OCR")
        start_btn.setDefault(True)
        start_btn.clicked.connect(self._on_start)
        start_btn.setStyleSheet("""
            QPushButton {
                background: #0078D4;
                color: white;
                padding: 8px 24px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background: #106EBE; }
        """)
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
    
    def _create_pages_section(self) -> QGroupBox:
        """Create pages selection section."""
        group = QGroupBox("📋 PAGES")
        layout = QVBoxLayout(group)
        
        self.page_group = QButtonGroup()
        
        self.all_pages_radio = QRadioButton(f"All pages ({self.num_pages} pages)")
        self.all_pages_radio.setChecked(True)
        self.page_group.addButton(self.all_pages_radio)
        layout.addWidget(self.all_pages_radio)
        
        self.current_page_radio = QRadioButton(f"Current page only (Page {self.current_page + 1})")
        self.page_group.addButton(self.current_page_radio)
        layout.addWidget(self.current_page_radio)
        
        range_layout = QHBoxLayout()
        self.range_radio = QRadioButton("Page range:")
        self.page_group.addButton(self.range_radio)
        range_layout.addWidget(self.range_radio)
        
        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, self.num_pages)
        self.start_spin.setValue(1)
        range_layout.addWidget(self.start_spin)
        
        range_layout.addWidget(QLabel("to"))
        
        self.end_spin = QSpinBox()
        self.end_spin.setRange(1, self.num_pages)
        self.end_spin.setValue(self.num_pages)
        range_layout.addWidget(self.end_spin)
        
        range_layout.addStretch()
        layout.addLayout(range_layout)
        
        return group
    
    def _create_language_section(self) -> QGroupBox:
        """Create language selection section."""
        group = QGroupBox("🌍 LANGUAGE")
        layout = QVBoxLayout(group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        self.language_combo.insertSeparator(1)
        
        for code in OCRLanguages.PRE_INSTALLED:
            name = OCRLanguages.get_language_name(code)
            self.language_combo.addItem(f"{name} ({code})", code)
        
        layout.addWidget(self.language_combo)
        
        installed_label = QLabel(
            f"Installed: {' • '.join(OCRLanguages.get_language_name(c) for c in OCRLanguages.PRE_INSTALLED)}"
        )
        installed_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(installed_label)
        
        return group
    
    def _create_output_section(self) -> QGroupBox:
        """Create output format section."""
        group = QGroupBox("📄 OUTPUT FORMAT")
        layout = QVBoxLayout(group)
        
        self.output_group = QButtonGroup()
        
        self.searchable_radio = QRadioButton("Searchable PDF    (Text layer behind image)")
        self.searchable_radio.setChecked(True)
        self.output_group.addButton(self.searchable_radio)
        layout.addWidget(self.searchable_radio)
        
        self.editable_radio = QRadioButton("Editable Text     (Convert to editable text)")
        self.output_group.addButton(self.editable_radio)
        layout.addWidget(self.editable_radio)
        
        return group
    
    def _create_processing_section(self) -> QGroupBox:
        """Create processing options section."""
        group = QGroupBox("⚙️ PROCESSING OPTIONS")
        layout = QVBoxLayout(group)
        
        self.deskew_check = QCheckBox("Auto-straighten tilted pages")
        self.deskew_check.setChecked(True)
        layout.addWidget(self.deskew_check)
        
        self.despeckle_check = QCheckBox("Remove scan noise and artifacts")
        self.despeckle_check.setChecked(True)
        layout.addWidget(self.despeckle_check)
        
        self.enhance_check = QCheckBox("Enhance image quality")
        self.enhance_check.setChecked(True)
        layout.addWidget(self.enhance_check)
        
        self.compress_check = QCheckBox("Compress output file")
        self.compress_check.setChecked(True)
        layout.addWidget(self.compress_check)
        
        return group
    
    def _create_advanced_section(self) -> QGroupBox:
        """Create advanced features section."""
        group = QGroupBox("📊 ADVANCED FEATURES")
        layout = QVBoxLayout(group)
        
        self.detect_tables_check = QCheckBox("Detect and preserve table structures")
        self.detect_tables_check.setChecked(True)
        layout.addWidget(self.detect_tables_check)
        
        self.highlight_uncertain_check = QCheckBox("Highlight uncertain text for review")
        self.highlight_uncertain_check.setChecked(True)
        layout.addWidget(self.highlight_uncertain_check)
        
        return group
    
    def _load_settings(self):
        """Load settings from config."""
        lang = self.config.get_ocr_default_language()
        idx = self.language_combo.findData(lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        
        self.deskew_check.setChecked(self.config.get_ocr_auto_deskew())
        self.despeckle_check.setChecked(self.config.get_ocr_despeckle())
        self.enhance_check.setChecked(self.config.get_ocr_enhance_image())
        self.compress_check.setChecked(self.config.get_ocr_compress_output())
        self.detect_tables_check.setChecked(self.config.get_ocr_detect_tables())
        self.highlight_uncertain_check.setChecked(self.config.get_ocr_highlight_uncertain())
    
    def _update_estimate(self):
        """Update time/size estimate."""
        pages = self._get_page_count()
        time_estimate = pages * 2.5
        self.estimate_label.setText(
            f"📊 Estimated time: ~{int(time_estimate)} seconds"
        )
    
    def _get_page_count(self) -> int:
        """Get number of pages to process."""
        if self.all_pages_radio.isChecked():
            return self.num_pages
        elif self.current_page_radio.isChecked():
            return 1
        else:
            return self.end_spin.value() - self.start_spin.value() + 1
    
    def _on_start(self):
        """Handle start OCR button."""
        params = {
            'language': self.language_combo.currentData(),
            'page_range': self._get_page_range(),
            'output_format': 'searchable' if self.searchable_radio.isChecked() else 'editable',
            'deskew': self.deskew_check.isChecked(),
            'despeckle': self.despeckle_check.isChecked(),
            'enhance': self.enhance_check.isChecked(),
            'compress': self.compress_check.isChecked(),
            'detect_tables': self.detect_tables_check.isChecked(),
            'highlight_uncertain': self.highlight_uncertain_check.isChecked(),
        }
        
        self.ocr_started.emit(params)
        self.accept()
    
    def _get_page_range(self) -> tuple:
        """Get selected page range."""
        if self.all_pages_radio.isChecked():
            return (0, self.num_pages)
        elif self.current_page_radio.isChecked():
            return (self.current_page, self.current_page + 1)
        else:
            return (self.start_spin.value() - 1, self.end_spin.value())


class OCRProgressDialog(QDialog):
    """Progress dialog for OCR processing with detailed status."""
    
    cancel_requested = Signal()
    
    def __init__(self, total_pages: int, parent=None):
        """
        Initialize progress dialog.
        
        Args:
            total_pages: Total number of pages to process
            parent: Parent widget
        """
        super().__init__(parent)
        self.total_pages = total_pages
        self.current_page = 0
        
        self.setWindowTitle("Processing OCR...")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._setup_ui()
        self._start_tip_rotation()
    
    def _setup_ui(self):
        """Set up progress dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Page indicator
        self.page_label = QLabel(f"Page 0 of {self.total_pages}")
        font = QFont()
        font.setPointSize(Fonts.SIZE_H3)
        font.setWeight(QFont.Weight.DemiBold)
        self.page_label.setFont(font)
        layout.addWidget(self.page_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Current step
        self.step_label = QLabel("Initializing...")
        layout.addWidget(self.step_label)
        
        # Step checklist
        steps_widget = QWidget()
        steps_layout = QVBoxLayout(steps_widget)
        steps_layout.setContentsMargins(Spacing.MEDIUM, 0, 0, 0)
        steps_layout.setSpacing(4)
        
        self.step_labels = []
        steps = [
            "✓ Enhanced image quality",
            "✓ Straightened page",
            "✓ Removed background noise",
            "→ Recognizing text...",
            "⋯ Adding text layer",
            "⋯ Optimizing file size"
        ]
        
        for step in steps:
            label = QLabel(step)
            self.step_labels.append(label)
            steps_layout.addWidget(label)
        
        layout.addWidget(steps_widget)
        
        # Time remaining
        self.time_label = QLabel("Estimated time remaining: calculating...")
        layout.addWidget(self.time_label)
        
        # Tip
        self.tip_label = QLabel()
        self.tip_label.setWordWrap(True)
        self.tip_label.setStyleSheet("""
            padding: 12px;
            background: #F0F8FF;
            border: 1px solid #B0D4F1;
            border-radius: 4px;
            color: #333;
        """)
        layout.addWidget(self.tip_label)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Load settings from config."""
        pass  # Settings loaded in main dialog
    
    def _start_tip_rotation(self):
        """Start rotating tips."""
        self.tip_timer = QTimer()
        self.tip_timer.timeout.connect(self._show_random_tip)
        self.tip_timer.start(8000)
        self._show_random_tip()
    
    def _show_random_tip(self):
        """Show a random OCR tip."""
        tip = random.choice(OCRMessages.TIPS)
        self.tip_label.setText(tip)
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress display."""
        self.current_page = current
        percentage = int((current / total) * 100)
        
        self.page_label.setText(f"Page {current} of {total}")
        self.progress_bar.setValue(percentage)
        self.step_label.setText(message)
        
        # Update time estimate
        remaining = total - current
        time_est = remaining * 2.5
        self.time_label.setText(f"Estimated time remaining: {int(time_est)} seconds")
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.cancel_requested.emit()
        self.reject()


class OCRCompletionDialog(QDialog):
    """Dialog shown when OCR completes with save options."""
    
    save_requested = Signal(str, str)  # save_mode, file_path
    review_requested = Signal()
    
    def __init__(self, statistics: dict, pdf_path: str, parent=None):
        """
        Initialize completion dialog.
        
        Args:
            statistics: OCR result statistics
            pdf_path: Original PDF file path
            parent: Parent widget
        """
        super().__init__(parent)
        self.statistics = statistics
        self.pdf_path = pdf_path
        self.config = get_config()
        
        self.setWindowTitle("OCR Complete!")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up completion dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Success header
        header = QLabel("✓ OCR Complete!")
        font = QFont()
        font.setPointSize(Fonts.SIZE_H2)
        font.setWeight(QFont.Weight.DemiBold)
        header.setFont(font)
        header.setStyleSheet("color: #107C10;")
        layout.addWidget(header)
        
        # Success message
        pages = self.statistics.get('pages_processed', 0)
        layout.addWidget(QLabel(f"✓ Successfully processed {pages} pages"))
        
        # Statistics
        stats_group = QGroupBox("📊 Results")
        stats_layout = QVBoxLayout(stats_group)
        
        words = self.statistics.get('total_words', 0)
        confidence = self.statistics.get('avg_confidence', 0) * 100
        suspicious = self.statistics.get('suspicious_count', 0)
        
        stats_layout.addWidget(QLabel(f"• {words:,} words recognized"))
        stats_layout.addWidget(QLabel(f"• {confidence:.0f}% average confidence"))
        stats_layout.addWidget(QLabel(f"• {suspicious} uncertain words highlighted for review"))
        
        layout.addWidget(stats_group)
        
        # Save options
        save_group = QGroupBox("💾 Save OCR results")
        save_layout = QVBoxLayout(save_group)
        
        self.save_group = QButtonGroup()
        
        self.save_current_radio = QRadioButton("Save to current file")
        self.save_current_radio.setChecked(True)
        self.save_group.addButton(self.save_current_radio)
        save_layout.addWidget(self.save_current_radio)
        
        path_label = QLabel(f"    {Path(self.pdf_path).name} (will be updated)")
        path_label.setStyleSheet("color: #666; font-size: 10pt; margin-left: 20px;")
        save_layout.addWidget(path_label)
        
        save_new_layout = QHBoxLayout()
        self.save_new_radio = QRadioButton("Save as new file")
        self.save_group.addButton(self.save_new_radio)
        save_new_layout.addWidget(self.save_new_radio)
        
        self.new_path_edit = QLineEdit()
        default_name = Path(self.pdf_path).stem + "_OCR.pdf"
        self.new_path_edit.setText(default_name)
        save_new_layout.addWidget(self.new_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        save_new_layout.addWidget(browse_btn)
        save_layout.addLayout(save_new_layout)
        
        self.no_save_radio = QRadioButton("Don't save (temporary - for preview only)")
        self.save_group.addButton(self.no_save_radio)
        save_layout.addWidget(self.no_save_radio)
        
        layout.addWidget(save_group)
        
        # Review option
        self.review_check = QCheckBox("Review uncertain words before saving")
        if suspicious > 0:
            self.review_check.setChecked(True)
        layout.addWidget(self.review_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #0078D4;
                color: white;
                padding: 8px 24px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background: #106EBE; }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_file(self):
        """Browse for save location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save OCR Result",
            self.new_path_edit.text(),
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.new_path_edit.setText(file_path)
    
    def _on_save(self):
        """Handle save button."""
        if self.review_check.isChecked():
            self.review_requested.emit()
            return
        
        save_mode = 'current' if self.save_current_radio.isChecked() else \
                    'new' if self.save_new_radio.isChecked() else 'none'
        
        file_path = self.new_path_edit.text() if save_mode == 'new' else self.pdf_path
        
        self.save_requested.emit(save_mode, file_path)
        self.accept()
