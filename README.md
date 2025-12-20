# Simple PDF Handler

A cross-platform PDF management application built with Python and QML.

## Features (F1-F8)

- **F1: Viewing & Navigation** - View PDFs with zoom, search, page navigation
- **F2: Editing** - Text and image editing
- **F3: Page Management** - Insert, delete, rotate, reorder pages
- **F4: Annotation** - Highlights, notes, shapes, stamps
- **F5: Merging** - Combine multiple PDFs
- **F6: Conversion** - Convert to/from various formats
- **F7: OCR** - Optical character recognition
- **F8: File Operations** - Open, save, print

## Tech Stack

- Python 3.8+ with PySide6
- QML for UI
- PyMuPDF for PDF processing

## Project Structure

```
simple-pdf-handler/
├── main.py                 # Entry point
├── requirements.txt
├── src/
│   ├── core/              # App framework, base classes, theme
│   ├── features/          # F1-F8 feature modules
│   └── qml/              # UI components and styles
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Development Status

**Phase 1: UI Foundation** ✅
- Core architecture with MVC pattern
- Theme system (light/dark mode)
- All 8 feature controllers with mock backends
- Basic QML UI structure

**Phase 2: Complete UI** (In Progress)
- Implement full QML interfaces for F1-F8
- Wire up all controller signals/slots

**Phase 3: Backend Integration** (Planned)
- Replace mocks with real PDF operations
- File I/O and error handling

## Architecture

Each feature follows modular structure:
```
features/[feature]/
├── controller.py    # Python logic (QObject)
├── model.py        # Data state
└── qml/            # UI components (to be created)
```

**Design Principles**: SOLID, DRY, KISS, YAGNI, Law of Demeter

## License

GNU General Public License v3.0
