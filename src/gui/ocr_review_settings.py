"""
OCR Review and Settings - Word correction and preferences dialogs.

Provides interactive correction interface for uncertain OCR results
and comprehensive settings management.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QCheckBox, QSlider, QGroupBox, QListWidget,
    QLineEdit, QTextEdit, QWidget, QButtonGroup, QComboBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from utils.constants import Colors, Fonts, Spacing, OCRLanguages
from utils.config import get_config
from utils.icon_manager import get_icon


class OCRReviewDialog(QDialog):
    """Interactive dialog for reviewing and correcting uncertain OCR words."""
    
    correction_applied = Signal(int, str)  # word_index, correction
    review_completed = Signal()
    
    def __init__(self, suspicious_words: list, parent=None):
        """
        Initialize review dialog.
        
        Args:
            suspicious_words: List of suspicious word dicts
            parent: Parent widget
        """
        super().__init__(parent)
        self.suspicious_words = suspicious_words
        self.current_index = 0
        self.corrections = {}
        
        self.setWindowTitle("Review OCR Results")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._show_current_word()
    
    def _setup_ui(self):
        """Set up review dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Header
        header_layout = QHBoxLayout()
        self.header_label = QLabel()
        font = QFont()
        font.setPointSize(Fonts.SIZE_H3)
        font.setWeight(QFont.Weight.DemiBold)
        self.header_label.setFont(font)
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        
        # Navigation
        prev_btn = QPushButton("◀ Prev")
        prev_btn.clicked.connect(self._previous_word)
        header_layout.addWidget(prev_btn)
        
        next_btn = QPushButton("Next ▶")
        next_btn.clicked.connect(self._next_word)
        header_layout.addWidget(next_btn)
        
        layout.addLayout(header_layout)
        
        # Context display
        context_group = QGroupBox("Context")
        context_layout = QVBoxLayout(context_group)
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setMaximumHeight(100)
        context_layout.addWidget(self.context_text)
        layout.addWidget(context_group)
        
        # Uncertain word display
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Uncertain text:"))
        self.word_label = QLabel()
        font = QFont()
        font.setPointSize(Fonts.SIZE_H3)
        font.setWeight(QFont.Weight.DemiBold)
        self.word_label.setFont(font)
        word_layout.addWidget(self.word_label)
        word_layout.addStretch()
        
        self.confidence_label = QLabel()
        word_layout.addWidget(self.confidence_label)
        layout.addLayout(word_layout)
        
        # Suggestions
        suggestions_group = QGroupBox("Suggestions")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        self.suggestion_group = QButtonGroup()
        self.suggestion_radios = []
        
        for i in range(4):
            radio = QRadioButton()
            self.suggestion_group.addButton(radio)
            self.suggestion_radios.append(radio)
            suggestions_layout.addWidget(radio)
        
        custom_layout = QHBoxLayout()
        self.custom_radio = QRadioButton("Custom:")
        self.suggestion_group.addButton(self.custom_radio)
        custom_layout.addWidget(self.custom_radio)
        
        self.custom_edit = QLineEdit()
        custom_layout.addWidget(self.custom_edit)
        suggestions_layout.addLayout(custom_layout)
        
        layout.addWidget(suggestions_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        skip_btn = QPushButton("Skip")
        skip_btn.clicked.connect(self._next_word)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        apply_next_btn = QPushButton("Apply & Next")
        apply_next_btn.clicked.connect(self._apply_and_next)
        button_layout.addWidget(apply_next_btn)
        
        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._on_done)
        done_btn.setStyleSheet("""
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
        button_layout.addWidget(done_btn)
        
        layout.addLayout(button_layout)
    
    def _show_current_word(self):
        """Display current uncertain word."""
        if self.current_index >= len(self.suspicious_words):
            self._on_done()
            return
        
        word_data = self.suspicious_words[self.current_index]
        
        # Update header
        self.header_label.setText(
            f"Uncertain Word {self.current_index + 1} of {len(self.suspicious_words)}"
        )
        
        # Show word
        self.word_label.setText(f'"{word_data["text"]}"')
        self.confidence_label.setText(f"Confidence: {int(word_data['confidence'] * 100)}%")
        
        # Show context (placeholder)
        self.context_text.setPlainText(
            f"...surrounding text context for '{word_data['text']}'..."
        )
        
        # Generate suggestions
        suggestions = [
            word_data["text"],
            word_data["text"].lower(),
            word_data["text"].capitalize(),
            "Keep as is"
        ]
        
        for i, (radio, suggestion) in enumerate(zip(self.suggestion_radios, suggestions)):
            radio.setText(suggestion)
            if i == 0:
                radio.setChecked(True)
    
    def _previous_word(self):
        """Go to previous word."""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_word()
    
    def _next_word(self):
        """Go to next word."""
        if self.current_index < len(self.suspicious_words) - 1:
            self.current_index += 1
            self._show_current_word()
    
    def _apply_and_next(self):
        """Apply correction and move to next."""
        correction = self._get_selected_correction()
        self.correction_applied.emit(self.current_index, correction)
        self.corrections[self.current_index] = correction
        self._next_word()
    
    def _get_selected_correction(self) -> str:
        """Get selected correction text."""
        if self.custom_radio.isChecked():
            return self.custom_edit.text()
        
        for radio in self.suggestion_radios:
            if radio.isChecked():
                return radio.text()
        
        return self.suspicious_words[self.current_index]["text"]
    
    def _on_done(self):
        """Handle done button."""
        self.review_completed.emit()
        self.accept()


class OCRSettingsDialog(QDialog):
    """Comprehensive OCR settings and preferences dialog."""
    
    def __init__(self, parent=None):
        """Initialize settings dialog."""
        super().__init__(parent)
        self.config = get_config()
        
        self.setWindowTitle("OCR Settings")
        self.setMinimumWidth(550)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up settings dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MEDIUM)
        
        # Default language
        lang_group = QGroupBox("🌍 DEFAULT LANGUAGE")
        lang_layout = QVBoxLayout(lang_group)
        self.language_combo = QComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        for code in OCRLanguages.PRE_INSTALLED:
            name = OCRLanguages.get_language_name(code)
            self.language_combo.addItem(f"{name}", code)
        lang_layout.addWidget(self.language_combo)
        layout.addWidget(lang_group)
        
        # Save behavior
        save_group = QGroupBox("📋 AFTER OCR COMPLETION")
        save_layout = QVBoxLayout(save_group)
        self.save_combo = QComboBox()
        self.save_combo.addItems([
            "Always ask what to do",
            "Auto-save to current file",
            "Save as new file"
        ])
        save_layout.addWidget(self.save_combo)
        layout.addWidget(save_group)
        
        # Default processing
        process_group = QGroupBox("⚙️ DEFAULT PROCESSING OPTIONS")
        process_layout = QVBoxLayout(process_group)
        
        self.deskew_check = QCheckBox("Auto-straighten tilted pages")
        process_layout.addWidget(self.deskew_check)
        
        self.despeckle_check = QCheckBox("Remove scan noise")
        process_layout.addWidget(self.despeckle_check)
        
        self.enhance_check = QCheckBox("Enhance image quality")
        process_layout.addWidget(self.enhance_check)
        
        self.compress_check = QCheckBox("Compress output file")
        process_layout.addWidget(self.compress_check)
        
        self.tables_check = QCheckBox("Detect tables")
        process_layout.addWidget(self.tables_check)
        
        self.highlight_check = QCheckBox("Highlight uncertain text")
        process_layout.addWidget(self.highlight_check)
        
        layout.addWidget(process_group)
        
        # Confidence threshold
        threshold_group = QGroupBox("🎯 CONFIDENCE THRESHOLD")
        threshold_layout = QVBoxLayout(threshold_group)
        
        threshold_layout.addWidget(QLabel("Words below this confidence will be highlighted:"))
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Low"))
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(75)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(25)
        self.threshold_slider.valueChanged.connect(self._update_threshold_label)
        slider_layout.addWidget(self.threshold_slider)
        
        slider_layout.addWidget(QLabel("High"))
        threshold_layout.addLayout(slider_layout)
        
        self.threshold_value_label = QLabel("75%")
        self.threshold_value_label.setAlignment(Qt.AlignCenter)
        threshold_layout.addWidget(self.threshold_value_label)
        
        layout.addWidget(threshold_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_settings)
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
    
    def _load_settings(self):
        """Load current settings."""
        lang = self.config.get_ocr_default_language()
        idx = self.language_combo.findData(lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        
        save_behavior = self.config.get_ocr_save_behavior()
        if save_behavior == 'always_ask':
            self.save_combo.setCurrentIndex(0)
        elif save_behavior == 'auto_save':
            self.save_combo.setCurrentIndex(1)
        else:
            self.save_combo.setCurrentIndex(2)
        
        self.deskew_check.setChecked(self.config.get_ocr_auto_deskew())
        self.despeckle_check.setChecked(self.config.get_ocr_despeckle())
        self.enhance_check.setChecked(self.config.get_ocr_enhance_image())
        self.compress_check.setChecked(self.config.get_ocr_compress_output())
        self.tables_check.setChecked(self.config.get_ocr_detect_tables())
        self.highlight_check.setChecked(self.config.get_ocr_highlight_uncertain())
        
        threshold = self.config.get_ocr_confidence_threshold()
        self.threshold_slider.setValue(threshold)
    
    def _update_threshold_label(self, value: int):
        """Update threshold label."""
        self.threshold_value_label.setText(f"{value}%")
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        self.language_combo.setCurrentIndex(0)
        self.save_combo.setCurrentIndex(0)
        self.deskew_check.setChecked(True)
        self.despeckle_check.setChecked(True)
        self.enhance_check.setChecked(True)
        self.compress_check.setChecked(True)
        self.tables_check.setChecked(True)
        self.highlight_check.setChecked(True)
        self.threshold_slider.setValue(75)
    
    def _save_settings(self):
        """Save settings to config."""
        self.config.set_ocr_default_language(self.language_combo.currentData())
        
        save_idx = self.save_combo.currentIndex()
        save_behavior = ['always_ask', 'auto_save', 'save_as_new'][save_idx]
        self.config.set_ocr_save_behavior(save_behavior)
        
        self.config.set_ocr_auto_deskew(self.deskew_check.isChecked())
        self.config.set_ocr_despeckle(self.despeckle_check.isChecked())
        self.config.set_ocr_enhance_image(self.enhance_check.isChecked())
        self.config.set_ocr_compress_output(self.compress_check.isChecked())
        self.config.set_ocr_detect_tables(self.tables_check.isChecked())
        self.config.set_ocr_highlight_uncertain(self.highlight_check.isChecked())
        self.config.set_ocr_confidence_threshold(self.threshold_slider.value())
        
        self.config.sync()
        self.accept()
    
    def _show_current_word(self):
        """Display current uncertain word."""
        pass  # Implementation details
    
    def _previous_word(self):
        """Navigate to previous word."""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_word()
    
    def _next_word(self):
        """Navigate to next word."""
        if self.current_index < len(self.suspicious_words) - 1:
            self.current_index += 1
            self._show_current_word()
        else:
            self._on_done()
    
    def _on_done(self):
        """Complete review."""
        self.review_completed.emit()
        self.accept()
