"""
Application constants including colors, sizes, and configuration values.

Defines the visual design system for consistent UI appearance across the application.
"""

from typing import Dict, Tuple


class Colors:
    """Color definitions for light and dark themes."""
    
    # Light theme colors
    LIGHT = {
        # Primary colors
        'background': '#FFFFFF',
        'surface': '#F5F5F5',
        'primary': '#0078D4',
        'secondary': '#606060',
        'accent': '#FFB900',
        
        # Text colors
        'text_primary': '#1F1F1F',
        'text_secondary': '#605E5C',
        'text_disabled': '#A19F9D',
        'text_link': '#0078D4',
        
        # UI element colors
        'border': '#E1DFDD',
        'divider': '#EDEBE9',
        'hover': '#F3F2F1',
        'active': '#E1DFDD',
        
        # Semantic colors
        'success': '#107C10',
        'warning': '#FFB900',
        'error': '#E81123',
        'info': '#0078D4',
    }
    
    # Dark theme colors
    DARK = {
        # Primary colors
        'background': '#1E1E1E',
        'surface': '#2D2D2D',
        'primary': '#0078D4',
        'secondary': '#A19F9D',
        'accent': '#FFB900',
        
        # Text colors
        'text_primary': '#FFFFFF',
        'text_secondary': '#B3B3B3',
        'text_disabled': '#6D6D6D',
        'text_link': '#4A9EFF',
        
        # UI element colors
        'border': '#3F3F3F',
        'divider': '#2D2D2D',
        'hover': '#3F3F3F',
        'active': '#4D4D4D',
        
        # Semantic colors
        'success': '#0F7B0F',
        'warning': '#FFB900',
        'error': '#E81123',
        'info': '#4A9EFF',
    }


class Fonts:
    """Font family and size definitions."""
    
    # Font families by platform
    FAMILY_PRIMARY = "Segoe UI, -apple-system, BlinkMacSystemFont, Ubuntu, Arial, sans-serif"
    FAMILY_MONOSPACE = "Consolas, Monaco, 'Courier New', monospace"
    
    # Font sizes (in points)
    SIZE_H1 = 18
    SIZE_H2 = 16
    SIZE_H3 = 14
    SIZE_H4 = 12
    SIZE_NORMAL = 11
    SIZE_SMALL = 10
    SIZE_TINY = 9
    
    # Font weights
    WEIGHT_REGULAR = 400
    WEIGHT_SEMIBOLD = 600


class Spacing:
    """Spacing values following 8px base unit system."""
    
    MICRO = 4    # 0.5x - Tight spacing, icon padding
    SMALL = 8    # 1x - Standard padding
    MEDIUM = 16  # 2x - Section spacing
    LARGE = 24   # 3x - Panel margins
    XLARGE = 32  # 4x - Major section breaks
    XXLARGE = 48 # 6x - Welcome screen spacing


class IconSizes:
    """Icon size definitions."""
    
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    TOOLBAR = 32
    WELCOME = 48


class WindowDefaults:
    """Default window dimensions and settings."""
    
    WIDTH = 1280
    HEIGHT = 800
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # Sidebar widths
    LEFT_SIDEBAR_WIDTH = 240
    RIGHT_SIDEBAR_WIDTH = 280
    
    # Status bar height
    STATUS_BAR_HEIGHT = 28


class AnimationDurations:
    """Animation timing in milliseconds."""
    
    ULTRA_FAST = 100  # Hover states
    FAST = 150        # Button interactions
    NORMAL = 200      # Panel transitions
    SMOOTH = 250      # Sidebar expand/collapse
    SLOW = 300        # Zoom, complex animations


class Shadows:
    """Shadow definitions for elevation."""
    
    LEVEL_1 = "0 2px 4px rgba(0, 0, 0, 0.1)"   # Cards, buttons
    LEVEL_2 = "0 4px 8px rgba(0, 0, 0, 0.15)"  # Elevated panels
    LEVEL_3 = "0 8px 16px rgba(0, 0, 0, 0.2)"  # Dialogs, modals
    LEVEL_4 = "0 4px 12px rgba(0, 0, 0, 0.25)" # Dropdowns, menus


class AppInfo:
    """Application metadata."""
    
    NAME = "Simple PDF Handler"
    VERSION = "1.0.0"
    ORGANIZATION = "PDF Handler Development"
    DESCRIPTION = "Professional PDF Management"
    LICENSE = "GNU GPL v3.0"
    WEBSITE = "https://github.com/simple-pdf-handler"


# Unicode icons as fallback (until we load proper icon fonts)
class Icons:
    """Unicode character icons for UI elements."""
    
    # File operations
    OPEN = "📂"
    SAVE = "💾"
    PRINT = "🖨️"
    EXPORT = "📤"
    IMPORT = "📥"
    
    # Navigation
    FIRST = "⏮️"
    PREVIOUS = "◀️"
    NEXT = "▶️"
    LAST = "⏭️"
    
    # View controls
    ZOOM_IN = "🔍"
    ZOOM_OUT = "🔎"
    FIT_PAGE = "⚲"
    ROTATE = "🔄"
    
    # Edit tools
    EDIT = "✏️"
    ADD_TEXT = "🖊️"
    IMAGE = "🖼️"
    SHAPE = "⬜"
    
    # Annotations
    HIGHLIGHT = "🖍️"
    COMMENT = "💬"
    NOTE = "📌"
    STAMP = "✓"
    
    # Common
    SETTINGS = "⚙️"
    INFO = "ℹ️"
    KEYBOARD = "⌨️"
    SECURITY = "🔒"
    UNDO = "↩️"
    REDO = "↪️"
    
    # Panels
    PAGES = "📑"
    BOOKMARKS = "🔖"
    COMMENTS = "📝"
    SEARCH = "🔍"
    LAYERS = "📋"
    FORMAT = "🎨"
    PROPERTIES = "📋"


class OCRLanguages:
    """OCR language definitions and metadata."""
    
    # Pre-installed languages (6 default languages)
    PRE_INSTALLED = ['en', 'es', 'zh', 'hi', 'bn', 'de']
    
    # Language metadata: code -> (name, size_mb)
    LANGUAGES = {
        # Pre-installed
        'en': ('English', 3.5),
        'es': ('Spanish', 4.2),
        'zh': ('Chinese Simplified', 18.1),
        'hi': ('Hindi', 11.2),
        'bn': ('Bengali', 10.8),
        'de': ('German', 4.5),
        
        # Additional available languages
        'fr': ('French', 4.3),
        'it': ('Italian', 4.1),
        'pt': ('Portuguese', 4.2),
        'ru': ('Russian', 12.5),
        'ja': ('Japanese', 15.8),
        'ko': ('Korean', 13.2),
        'ar': ('Arabic', 9.8),
        'th': ('Thai', 8.5),
        'vi': ('Vietnamese', 7.2),
        'nl': ('Dutch', 4.0),
        'pl': ('Polish', 4.8),
        'tr': ('Turkish', 5.1),
        'id': ('Indonesian', 3.9),
        'ms': ('Malay', 3.7),
        'tl': ('Tagalog', 3.8),
    }
    
    @classmethod
    def get_language_name(cls, code: str) -> str:
        """Get human-readable language name."""
        return cls.LANGUAGES.get(code, ('Unknown', 0))[0]
    
    @classmethod
    def get_language_size(cls, code: str) -> float:
        """Get language pack size in MB."""
        return cls.LANGUAGES.get(code, ('Unknown', 0))[1]


class OCRSettings:
    """OCR configuration constants."""
    
    # Output format options
    OUTPUT_SEARCHABLE_PDF = 'searchable_pdf'
    OUTPUT_EDITABLE_TEXT = 'editable_text'
    
    # Save behavior options
    SAVE_ALWAYS_ASK = 'always_ask'
    SAVE_AUTO_SAVE = 'auto_save'
    SAVE_AS_NEW = 'save_as_new'
    
    # Confidence threshold range
    MIN_CONFIDENCE = 0
    MAX_CONFIDENCE = 100
    DEFAULT_CONFIDENCE = 75
    
    # Processing timeout per page (seconds)
    PAGE_TIMEOUT = 30
    
    # Maximum parallel processing threads
    MAX_THREADS = 4


class OCRMessages:
    """User-facing messages for OCR operations."""
    
    # Detection banner
    BANNER_TITLE = "This appears to be a scanned document"
    BANNER_MESSAGE = "Make it searchable and editable with OCR"
    
    # Progress messages
    PROGRESS_PREPARING = "Preparing document..."
    PROGRESS_ENHANCING = "Enhancing image quality..."
    PROGRESS_STRAIGHTENING = "Straightening page..."
    PROGRESS_REMOVING_NOISE = "Removing background noise..."
    PROGRESS_RECOGNIZING = "Recognizing text..."
    PROGRESS_ADDING_LAYER = "Adding text layer..."
    PROGRESS_OPTIMIZING = "Optimizing file size..."
    
    # Success messages
    SUCCESS_TITLE = "OCR Complete!"
    SUCCESS_MESSAGE = "Your document is now searchable and text can be selected."
    
    # Error messages
    ERROR_NO_TEXT = "Could not recognize any text in this document."
    ERROR_LOW_QUALITY = "Image quality is too low for reliable OCR. Please rescan at higher resolution."
    ERROR_LANGUAGE_MISSING = "Language pack not installed. Would you like to download it now?"
    ERROR_PROCESSING = "An error occurred during OCR processing."
    ERROR_SAVE_FAILED = "Failed to save OCR results to file."
    
    # Tips (shown during processing)
    TIPS = [
        "💡 Tip: OCR accuracy is highest with clean, well-lit scans.",
        "💡 Tip: For best results, scan documents at 300 DPI or higher.",
        "💡 Tip: Straight pages work better than tilted scans.",
        "💡 Tip: Remove shadows and background colors before scanning.",
        "💡 Tip: Multi-language documents may need language selection.",
    ]


def get_theme_colors(theme: str = 'light') -> Dict[str, str]:
    """
    Get color palette for specified theme.
    
    Args:
        theme: Theme name ('light' or 'dark')
        
    Returns:
        Dictionary of color values
    """
    return Colors.DARK if theme.lower() == 'dark' else Colors.LIGHT
