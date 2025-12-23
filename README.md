# Simple PDF Handler

A professional, cross-platform PDF management application built with PySide6 (Qt for Python). Features a modern interface with light/dark themes, comprehensive PDF tools, and an intuitive user experience.

![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-GPL--3.0-orange)

## 🌟 Features

### Current (Phase 1 - GUI Shell)
- ✅ **Professional UI** - Modern, clean interface with intuitive navigation
- ✅ **Light/Dark Themes** - Toggle between themes with persistent preferences
- ✅ **Complete Menu System** - 8 comprehensive menus with keyboard shortcuts
- ✅ **Ribbon Toolbar** - 5 tool tabs (Home, Edit, Annotate, Page, Convert)
- ✅ **Navigation Sidebar** - 5 panels (Pages, Bookmarks, Comments, Search, Layers)
- ✅ **Properties Sidebar** - Format controls and document metadata editing
- ✅ **Welcome Screen** - Quick access to actions and recent files
- ✅ **Status Bar** - Page info, zoom controls, document status
- ✅ **Settings Persistence** - Window state, theme, recent files saved

### Planned (Future Phases)
- 📄 PDF Rendering with PyMuPDF
- ✏️ Annotation Tools (highlight, comment, stamps)
- 📝 Text Editing and Formatting
- 🔄 Page Manipulation (insert, delete, rotate, reorder)
- 📊 Document Conversion (Word, Excel, Images)
- 🔍 Advanced Search with regex
- 🔐 Security and Encryption
- 📤 Export to Multiple Formats
- 🖨️ Print Management

## 📋 Requirements

- Python 3.8 or higher
- PySide6 6.0 or higher

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd simple-pdf-handler
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application

**From project root (recommended):**
```bash
python3 run.py
```

**Or from src directory:**
```bash
cd src
python3 main.py
```

## 📖 Usage

### Basic Navigation

**Opening Files:**
- File → Open (Ctrl+O)
- Click "Open File" on welcome screen
- Drag & drop PDF files (planned)

**Theme Toggle:**
- View → Toggle Dark/Light Theme (Ctrl+Shift+T)

**Zoom Controls:**
- Toolbar: Zoom In/Out buttons
- Status Bar: Zoom slider or dropdown
- Menu: View → Zoom In/Out (Ctrl++/Ctrl+-)

**Sidebars:**
- View → Panels → Left/Right Sidebar
- Click close button on sidebar title

### Keyboard Shortcuts

#### File Operations
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save As
- `Ctrl+P` - Print
- `Ctrl+W` - Close file
- `Ctrl+Q` - Exit

#### Editing
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+A` - Select All

#### View
- `Ctrl++` - Zoom In
- `Ctrl+-` - Zoom Out
- `Ctrl+0` - Fit Page
- `Ctrl+2` - Fit Width
- `Ctrl+R` - Rotate Page
- `F11` - Full Screen
- `Ctrl+Shift+T` - Toggle Theme

#### Help
- `F1` - User Guide

## 🏗️ Architecture

### Project Structure
```
simple-pdf-handler/
├── src/
│   ├── main.py                 # Application entry point
│   ├── utils/                  # Utility modules
│   │   ├── constants.py        # App constants, colors, fonts
│   │   ├── config.py           # Settings management
│   │   └── theme_manager.py    # Theme system
│   └── gui/                    # GUI components
│       ├── main_window.py      # Main window orchestrator
│       ├── menu_bar.py         # Menu system
│       ├── toolbar.py          # Ribbon toolbar
│       ├── left_sidebar.py     # Navigation sidebar
│       ├── right_sidebar.py    # Properties sidebar
│       ├── content_area.py     # PDF display area
│       ├── status_bar.py       # Status and zoom controls
│       └── welcome_screen.py   # Startup screen
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

### Design Patterns

**1. Coordinator Pattern (Main Window)**
- `MainWindow` acts as central coordinator
- Manages communication between components
- Handles application-level state

**2. Signal/Slot Pattern (Qt)**
- Loose coupling between UI components
- Event-driven architecture
- Clean separation of concerns

**3. Singleton Pattern**
- `ThemeManager` - Global theme instance
- `Config` - Global settings instance

**4. Factory Pattern**
- Dynamic stylesheet generation
- Component creation methods

### Key Components

#### Main Window (`main_window.py`)
Central orchestrator that:
- Creates and manages all UI components
- Handles signal routing between components
- Manages document state (open/closed/modified)
- Persists window geometry and preferences

#### Theme Manager (`theme_manager.py`)
Provides:
- Dynamic light/dark theme switching
- Comprehensive stylesheet generation
- Color palette management
- Consistent styling across components

#### Configuration (`config.py`)
Manages:
- User preferences (theme, window state)
- Recent files list
- Sidebar visibility
- Zoom level and view settings

### Component Communication

```
┌─────────────────────────────────────────┐
│           Main Window                    │
│         (Orchestrator)                   │
└─────────┬───────────────────────────────┘
          │
    ┌─────┴─────┬─────────┬──────────┬─────────┐
    │           │         │          │         │
┌───▼──┐  ┌────▼───┐ ┌──▼────┐ ┌───▼────┐ ┌──▼────┐
│Menu  │  │Toolbar │ │Content│ │Sidebar │ │Status │
│Bar   │  │        │ │Area   │ │        │ │Bar    │
└──────┘  └────────┘ └───────┘ └────────┘ └───────┘
   │           │          │          │         │
   └───────────┴──────────┴──────────┴─────────┘
              Signals/Slots
```

### State Management

**Document State:**
- `_current_document` - Path to open document
- `_is_modified` - Unsaved changes flag
- State updates trigger UI element enable/disable

**UI State:**
- Window geometry saved on close
- Sidebar visibility persisted
- Theme preference saved
- Recent files maintained

## 🎨 Customization

### Adding New Menu Items

Edit `src/gui/menu_bar.py`:
```python
def _create_your_menu(self):
    menu = self.addMenu("&YourMenu")
    
    action = QAction("Your Action", self)
    action.setShortcut("Ctrl+Y")
    action.triggered.connect(self.your_signal.emit)
    menu.addAction(action)
```

### Adding Toolbar Buttons

Edit `src/gui/toolbar.py`:
```python
def _create_your_tools(self):
    group = self._create_tool_group("Your Group", [
        ("Icon\nLabel", "Tooltip", callback, is_doc_action)
    ])
    return group
```

### Modifying Theme Colors

Edit `src/utils/constants.py`:
```python
class Colors:
    LIGHT = {
        'primary': '#0078D4',  # Your color
        # ... other colors
    }
```

## 🧪 Development

### Running Tests
```bash
# Unit tests (when available)
pytest tests/

# Run specific test
pytest tests/test_theme.py
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document public methods with docstrings
- Keep functions focused and small

### Adding Dependencies
```bash
# Add to requirements.txt
pip install new-package
pip freeze > requirements.txt
```

## 🐛 Troubleshooting

### Font Warnings
The application now uses macOS system fonts. If you see font warnings:
- Check that your system has the fallback fonts (Arial, sans-serif)
- Warnings are cosmetic and don't affect functionality

### Window Not Appearing
- Check if PySide6 is properly installed: `python -c "import PySide6"`
- Ensure Python 3.8+ is being used: `python --version`
- Try running with: `python -u main.py` for unbuffered output

### Theme Not Persisting
- Check write permissions in user directory
- Settings stored in: `~/.config/SimplePDFHandler/`
- Delete config to reset: `rm -rf ~/.config/SimplePDFHandler/`

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

- **Project**: Simple PDF Handler
- **Version**: 0.1.0-alpha
- **Status**: Phase 1 Complete (GUI Shell)
- **Next Phase**: PDF Rendering and Core Functionality

## 🗺️ Roadmap

### Phase 1: GUI Shell ✅ (Current)
- Professional UI framework
- Theme system
- All menus and toolbars
- Settings persistence

### Phase 2: Core PDF Features (Next)
- PDF rendering with PyMuPDF
- Page navigation
- Zoom and fit modes
- File open/save/export
- Basic annotations

### Phase 3: Advanced Features
- Text editing
- Advanced annotations
- Page manipulation
- Search functionality
- Bookmarks management

### Phase 4: Professional Tools
- Document conversion
- OCR support
- Batch processing
- Security features
- Print management

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)
- UI design inspired by modern PDF applications
- Icons from Unicode emoji set

---

**Note**: This is Phase 1 - GUI Shell implementation. PDF functionality will be added in Phase 2. The current version demonstrates the complete UI/UX with placeholder actions for future features.
