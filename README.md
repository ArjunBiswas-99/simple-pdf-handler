# Simple PDF Handler
by Arjun Biswas

A professional Python-based desktop application that provides a clean and intuitive interface for comprehensive PDF manipulation. Built with modern architecture and cross-platform compatibility in mind.

## Current Features (v0.1.0)

### ✅ Viewing & Rendering (F1.1, F1.2)
* Open PDF files from local storage
* High-quality rendering of text, images, and vector graphics
* Intelligent loading with threading support for large files (>10MB)
* Professional UI with menu bar and status bar
* Placeholder display when no document is loaded
* Error handling with user-friendly messages

### 🚧 Coming Soon
* Page navigation (next, previous, first, last, go to page)
* Zoom controls (50%, 75%, 100%, 125%, 150%, fit width, fit page)
* Text search within documents
* Text and image selection/copying
* Advanced editing and annotation features
* Page management and manipulation
* Document conversion capabilities
* OCR for scanned documents

## Technology Stack

* **Language:** Python 3.8+
* **GUI Framework:** PyQt6 - Cross-platform, professional UI framework
* **PDF Processing:** PyMuPDF (fitz) - Fast, comprehensive PDF operations
* **Platform Support:** Windows, macOS, Linux

## Architecture

The application follows a modular, layered architecture:

```
src/
├── backend/         # PDF processing implementations
│   └── pymupdf_backend.py    # PyMuPDF wrapper
├── core/            # Business logic layer
│   ├── pdf_document.py       # Document abstraction
│   └── pdf_loader_worker.py  # Async loading with QThread
├── ui/              # User interface components
│   ├── main_window.py        # Main application window
│   ├── pdf_canvas.py         # PDF display widget
│   └── progress_dialog.py    # Loading progress dialog
└── main.py          # Application entry point
```

### Design Principles

* **Separation of Concerns:** UI, business logic, and backend are decoupled
* **Abstraction Layer:** PDF operations are abstracted from implementation details
* **Modularity:** Each component has a single, well-defined responsibility
* **Extensibility:** Easy to swap backends or add new features
* **Threading:** Background loading for large files prevents UI freezing
* **Professional Code:** Type hints, comprehensive docstrings, error handling

## Installation

### Prerequisites

* Python 3.8 or higher
* pip (Python package manager)

### Setup

1. Clone or download the repository:
```bash
cd simple-pdf-handler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python src/main.py
```

Or from the project root:
```bash
cd simple-pdf-handler
python src/main.py
```

### Opening PDF Files

1. Launch the application
2. Click **File → Open** (or press `Ctrl+O`)
3. Select a PDF file from your system
4. The PDF will be displayed in the canvas

**Smart Loading:**
* Files under 10MB load instantly (synchronous)
* Files over 10MB show a progress dialog (asynchronous with threading)

### Keyboard Shortcuts

* `Ctrl+O` - Open PDF file
* `Ctrl+W` - Close current document
* `Ctrl+Q` - Exit application

## Project Structure

```
simple-pdf-handler/
├── src/                    # Source code
│   ├── backend/           # PDF backend implementations
│   ├── core/              # Core business logic
│   ├── ui/                # User interface components
│   └── main.py            # Application entry point
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── Requirements.md       # Detailed feature requirements
```

## Development

### Code Style

* Professional docstrings for all classes and functions
* Type hints for function parameters and return values
* Single responsibility per function/method
* Modular, decoupled components
* Comprehensive error handling

### Threading

Large PDF files (>10MB) are loaded asynchronously using `QThread`:
* Prevents UI freezing during loading
* Shows progress dialog with status updates
* Allows cancellation of long operations
* Pre-renders first page for instant display

### Adding Features

The abstraction layer makes it easy to add features:

1. **Backend operations** - Add methods to `PyMuPDFBackend`
2. **Business logic** - Add methods to `PDFDocument`
3. **UI components** - Create new widgets in `ui/`
4. **Integration** - Wire up in `MainWindow`

## Troubleshooting

### "Module not found" errors
Make sure you're running from the correct directory and have installed dependencies:
```bash
cd simple-pdf-handler
pip install -r requirements.txt
python src/main.py
```

### PDF won't open
* Verify the file is a valid PDF
* Check file permissions
* Try a different PDF file
* Check console output for detailed error messages

### Application crashes
* Ensure Python 3.8+ is installed
* Verify PyQt6 and PyMuPDF are properly installed
* Check for corrupted PDF files

## Contributing

This is a personal project by Arjun Biswas. Future enhancements will implement the complete feature set outlined in Requirements.md.

## License

This project is for educational and personal use.

## Version History

* **v0.1.0** (Current) - Initial release with basic viewing capabilities (F1.1, F1.2)
  - Open and render PDF files
  - Threaded loading for large files
  - Professional UI with menu system
  - Cross-platform support

## Roadmap

### Phase 1: Viewing & Navigation (In Progress)
- [x] F1.1 - Open PDF files
- [x] F1.2 - Render PDF content
- [ ] F1.3 - Page navigation
- [ ] F1.4 - Zoom controls
- [ ] F1.5 - Text search
- [ ] F1.6 - Text selection
- [ ] F1.7 - Image selection
- [ ] F1.8 - Display annotations

### Phase 2: Editing & Annotation
* Text editing and formatting
* Image insertion and manipulation
* Annotation tools (highlights, comments, shapes)

### Phase 3: Advanced Features
* Page management (insert, delete, rotate, reorder)
* Document merging and splitting
* Format conversion (PDF to/from various formats)
* OCR capabilities

---

**Author:** Arjun Biswas  
**Version:** 0.1.0  
**Last Updated:** December 2024
