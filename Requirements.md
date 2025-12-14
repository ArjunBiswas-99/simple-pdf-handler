# Requirements for Simple PDF Handler

## Functional Requirements

### F1: PDF Viewing and Navigation
*   **F1.1:** ✅ The application shall allow users to open PDF files from local storage.
*   **F1.2:** ✅ The application shall render PDF content accurately, including text, images, and basic vector graphics.
*   **F1.3:** ✅ The application shall support navigation between pages (next, previous, first, last, go to specific page number).
*   **F1.4:** ✅ The application shall support zooming in and out of the PDF view (e.g., 50%, 75%, 100%, 125%, 150%, 200%, fit width, fit page).
*   **F1.5:** ✅ The application shall allow users to search for text within the current PDF document.
*   **F1.6:** ✅ The application shall allow users to select and copy text from the PDF.
*   **F1.7:** ⬜ The application shall allow users to select and copy images from the PDF.
*   **F1.8:** ⬜ The application shall display existing annotations and comments in the PDF.

### F2: PDF Editing
*   **F2.1:** ⬜ The application shall allow users to add new text to a PDF page (specifying font, size, color, style).
*   **F2.2:** ⬜ The application shall allow users to edit existing text properties (font, size, color, style) where possible.
*   **F2.3:** ⬜ The application shall allow users to insert images into a PDF page.
*   **F2.4:** ⬜ The application shall allow users to resize, move, and delete images within a PDF page.
*   **F2.5:** ⬜ The application shall allow users to move, resize, and delete objects within a PDF page.
*   **F2.6:** ⬜ The application shall allow users to change object properties (color, line width, etc.).

### F3: Page Management
*   **F3.1:** ⬜ The application shall allow users to insert pages from other PDF files or blank pages into the current document.
*   **F3.2:** ⬜ The application shall allow users to delete specific pages from the current document.
*   **F3.3:** ⬜ The application shall allow users to rotate individual pages.
*   **F3.4:** ⬜ The application shall allow users to reorder pages within the document.
*   **F3.5:** ⬜ The application shall allow users to crop pages.
*   **F3.6:** ⬜ The application shall allow users to extract specific pages into a new PDF file.
*   **F3.7:** ⬜ The application shall allow users to replace a page with content from another PDF.

### F4: Annotation and Markup
*   **F4.1:** ⬜ The application shall allow users to add highlight annotations.
*   **F4.2:** ⬜ The application shall allow users to add underline and strikethrough annotations.
*   **F4.3:** ⬜ The application shall allow users to add sticky notes and comments.
*   **F4.4:** ⬜ The application shall allow users to add text boxes and callouts.
*   **F4.5:** ⬜ The application shall allow users to draw shapes (rectangles, circles, lines) on a page.
*   **F4.6:** ⬜ The application shall allow users to add standard stamps to a page.
*   **F4.7:** ⬜ The application shall allow users to measure distances and areas on a page.

### F5: Merging and Combining
*   **F5.1:** ⬜ The application shall allow users to merge multiple PDF files into a single PDF document.
*   **F5.2:** ⬜ The application shall allow users to specify the order of files during the merge process.
*   **F5.3:** ⬜ The application shall allow users to insert specific pages from one PDF file into another PDF file.

### F6: Conversion
*   **F6.1:** ⬜ The application shall allow users to convert a PDF file to Word format.
*   **F6.2:** ⬜ The application shall allow users to convert a PDF file to Excel format.
*   **F6.3:** ⬜ The application shall allow users to convert a PDF file to PowerPoint format.
*   **F6.4:** ⬜ The application shall allow users to convert a PDF file to image formats (JPEG, PNG, TIFF).
*   **F6.5:** ⬜ The application shall allow users to convert a PDF file to HTML format.
*   **F6.6:** ⬜ The application shall allow users to convert a PDF file to plain text format.
*   **F6.7:** ⬜ The application shall allow users to create a PDF file from a Word document.
*   **F6.8:** ⬜ The application shall allow users to create a PDF file from an Excel document.
*   **F6.9:** ⬜ The application shall allow users to create a PDF file from a PowerPoint presentation.
*   **F6.10:** ⬜ The application shall allow users to create a PDF file from image files.
*   **F6.11:** ⬜ The application shall allow users to create a PDF file from web page content (URL or HTML input).

### F7: OCR (Optical Character Recognition)
*   **F7.1:** ⬜ The application shall allow users to perform OCR on scanned PDF documents or images.
*   **F7.2:** ⬜ The application shall make the recognized text searchable and selectable within the PDF.
*   **F7.3:** ⬜ The application shall allow users to save the OCR-processed PDF.

### F8: File Management
*   **F8.1:** ⬜ The application shall allow users to save the current PDF document.
*   **F8.2:** ⬜ The application shall allow users to save the current PDF document with a new name or location (Save As).
*   **F8.3:** ⬜ The application shall allow users to print the current PDF document.
*   **F8.4:** ⬜ The application shall allow users to print the current PDF document with annotations visible.

## Technical Requirements

### T1: Platform Compatibility
*   **T1.1:** ✅ The application shall run on Windows, macOS, and Linux operating systems.
*   **T1.2:** ✅ The application shall be implemented in Python 3.8 or higher.

### T2: GUI Framework
*   **T2.1:** ✅ The application shall use PyQt6 as the GUI framework.
*   **T2.2:** ✅ The application shall provide a clean, professional, and intuitive user interface.
*   **T2.3:** ✅ The application shall support standard UI elements like menu bars, toolbars, status bars, and dialogs.

### T3: PDF Processing Libraries
*   **T3.1:** ✅ The application shall use PyMuPDF (fitz) for PDF processing operations.
*   **T3.2:** ✅ The application shall implement an abstraction layer to decouple UI from backend implementation.

### T4: Performance
*   **T4.1:** ✅ The application shall render PDF pages efficiently, even for moderately large files (up to 50MB).
*   **T4.2:** ✅ The application shall handle file operations (open, save, merge) without significant delays for files under 100MB.
*   **T4.3:** ✅ The application shall use threading for large file operations to prevent UI freezing.

### T5: Error Handling
*   **T5.1:** ✅ The application shall provide meaningful error messages to the user when file operations fail (e.g., file not found, permission denied).
*   **T5.2:** ✅ The application shall handle invalid PDF files gracefully without crashing.

### T6: Security
*   **T6.1:** ✅ The application shall not execute JavaScript embedded within PDFs for security reasons.
*   **T6.2:** ✅ The application shall validate user inputs where applicable to prevent potential security vulnerabilities.

### T7: Design Principles
*   **T7.1:** ✅ The application shall follow SOLID principles for maintainable and scalable code structure.
*   **T7.2:** ✅ The application shall implement a Model-View-Controller (MVC) pattern to separate UI logic from business logic.
*   **T7.3:** ✅ The application shall apply Gestalt principles (proximity, similarity, continuity, closure) in the user interface design for intuitive user experience.

### T8: Code Quality
*   **T8.1:** ✅ The application shall include professional docstrings for all classes and functions.
*   **T8.2:** ✅ The application shall use type hints for function parameters and return values.
*   **T8.3:** ✅ The application shall follow single responsibility principle for all components.

### T9: Licensing
*   **T9.1:** ✅ The application shall be licensed under GNU General Public License v3.0.
*   **T9.2:** ✅ All source files shall include appropriate copyright and license headers.
*   **T9.3:** ✅ The application shall properly attribute third-party dependencies and their licenses.

---

## UX Overhaul Implementation Checklist

### Overview
Transform the application from a simple viewer to a modern, mode-based PDF application with a professional interface inspired by Adobe Acrobat DC. This overhaul introduces AppBar, ModeTabs, ContextToolbars, enhanced sidebar, and right properties panel while preserving all existing functionality.

### Target UI Layout

#### Main Window Structure
```
┌─────────────────────────────────────────────────────────────────┐
│ AppBar: [Icon] Simple PDF Handler    [🌓 Theme] [⚙️] [?]       │
├─────────────────────────────────────────────────────────────────┤
│ ModeTabs: [View] [Comment] [Edit] [Organize] [Convert & OCR]   │
├─────────────────────────────────────────────────────────────────┤
│ ContextToolbar (changes based on active mode)                  │
│ [Open][Save][SaveAs▼][Print] || [|<][<][Page:__][/][##][>][>|] │
├────────┬──────────────────────────────────────────┬────────────┤
│ Left   │                                          │   Right    │
│ Side   │        Document Canvas                   │   Panel    │
│ bar    │     (PDF pages on dark stage)            │ (Collap-   │
│        │                                          │  sible)    │
│ [📄]   │                                          │            │
│ [🔖]   │                                          │            │
│ [🔍]   │                                          │            │
│ [📎]   │                                          │            │
├────────┴──────────────────────────────────────────┴────────────┤
│ StatusBar: A4 210×297mm | Page 3 of 25 | Zoom: 100%  Mode:View│
└─────────────────────────────────────────────────────────────────┘
```

#### Left Sidebar Detail (280px wide)
```
┌─────────┬───────────────────────────────┐
│ Icon    │ Active Panel Content          │
│ Rail    │                               │
│ (48px)  │ (232px)                       │
│         │                               │
│  [📄]   │  PAGES                        │ ← When Pages selected
│         │  ┌──────────────────────┐     │
│  [🔖]   │  │ [Thumbnail 1]        │     │
│         │  │ Page 1 (current)     │     │
│  [🔍]   │  ├──────────────────────┤     │
│         │  │ [Thumbnail 2]        │     │
│  [📎]   │  │ Page 2               │     │
│         │  ├──────────────────────┤     │
│         │  │ [Thumbnail 3]        │     │
│         │  │ Page 3               │     │
│         │  └──────────────────────┘     │
│         │  ⋮ (scrollable)               │
└─────────┴───────────────────────────────┘

┌─────────┬───────────────────────────────┐
│  [📄]   │  BOOKMARKS                    │ ← When Bookmarks selected
│         │  ┌──────────────────────┐     │
│  [🔖]   │  │ ▼ Chapter 1          │     │
│         │  │   ├─ Section 1.1     │     │
│  [🔍]   │  │   └─ Section 1.2     │     │
│         │  │ ▼ Chapter 2          │     │
│  [📎]   │  │   ├─ Section 2.1     │     │
│         │  │   └─ Section 2.2     │     │
│         │  │ ► Chapter 3          │     │
│         │  └──────────────────────┘     │
└─────────┴───────────────────────────────┘

┌─────────┬───────────────────────────────┐
│  [📄]   │  SEARCH                       │ ← When Search selected
│         │  ┌──────────────────────┐     │
│  [🔖]   │  │ [🔍 Search text...] │     │
│         │  └──────────────────────┘     │
│  [🔍]   │  ☑ Match case                │
│         │  ☐ Whole words                │
│  [📎]   │                               │
│         │  Results (3 matches):         │
│         │  • Page 2: "...text..."       │
│         │  • Page 5: "...text..."       │
│         │  • Page 8: "...text..."       │
└─────────┴───────────────────────────────┘
```

#### Context Toolbar Layouts by Mode

**View Mode:**
```
[📂 Open][💾 Save][💾 SaveAs▼][🖨️ Print] || [❘◀][◀][Page:__][/][##][▶][▶❘]
|| [Fit Page][Fit Width][−][100%▼][+] || [Single][Continuous][Facing]
|| [⟲ Rotate Left][⟳ Rotate Right]
```

**Comment Mode:**
```
[Highlight][Underline][Strikethrough] || [Note][Text Box][Callout]
|| [Rectangle][Ellipse][Line][Arrow][Freehand] || [Stamp▼] || [Distance][Area]
```

**Edit Mode:**
```
[Select][Edit Text][Edit Image] || [Add Text][Add Image]
|| [Forward][Backward][Align▼][Distribute▼] || [Delete][Duplicate]
```

**Organize Mode:**
```
[Insert▼][Delete][Duplicate] || [⟲][⟳][↑][↓]
|| [Extract▼][Replace] || [Merge PDFs...]
```

**Convert & OCR Mode:**
```
[To Word][To Excel][To PPT][To Images▼][To HTML][To Text]
|| [From File▼][From Images][From URL] || [Recognize Text▼]
```

#### Right Panel Detail (280px wide, collapsible)
```
┌────────────────────────────┐
│  HIGHLIGHT PROPERTIES      │ ← When annotation selected
│  ┌──────────────────────┐  │
│  │ Color:               │  │
│  │ [■][■][■][■][■][■]   │  │
│  └──────────────────────┘  │
│  Opacity: [  60%  ▓▓▓▓ ]   │
│  ┌──────────────────────┐  │
│  │ Author: [________]   │  │
│  └──────────────────────┘  │
│  ┌──────────────────────┐  │
│  │ Comment:             │  │
│  │ [________________]   │  │
│  │ [________________]   │  │
│  └──────────────────────┘  │
└────────────────────────────┘

┌────────────────────────────┐
│    No selection            │ ← Default state in View mode
│                            │
│  (or panel hidden)         │
│                            │
└────────────────────────────┘
```

#### Status Bar Detail
```
┌─────────────────────────────────────────────────────────────────┐
│ A4 210×297 mm        │  Page 3 of 25  │  Zoom: 100%  Mode: View│
│ (Left section)       │ (Center)       │ (Right section)        │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Foundation & Design System
*   **UX1.1:** ⬜ Create design tokens system (colors, spacing, sizing constants) in `src/ui/styles/design_tokens.py`
*   **UX1.2:** ⬜ Update existing theme system to integrate new design tokens
*   **UX1.3:** ⬜ Define AppMode enum (View, Comment, Edit, Organize, Convert & OCR)
*   **UX1.4:** ⬜ Define SidebarMode enum (Pages, Bookmarks, Search, Attachments)

### Phase 2: Top Bar Components
*   **UX2.1:** ⬜ Create AppBar component (`src/ui/app_bar.py`) to replace menu bar
    *   Left section: App icon + "Simple PDF Handler" title
    *   Right section: Theme toggle, Settings button (grayed), Help button
*   **UX2.2:** ⬜ Create ModeTabs component (`src/ui/mode_tabs.py`) with 5 mode tabs
    *   Implement tab switching visual states (active/inactive/hover)
    *   Emit mode_changed signal when tab clicked
*   **UX2.3:** ⬜ Connect AppBar signals to MainWindow (theme toggle, help dialog)

### Phase 3: Context Toolbars
*   **UX3.1:** ⬜ Create toolbar base structure (`src/ui/toolbars/__init__.py`)
*   **UX3.2:** ⬜ Implement View Toolbar (`src/ui/toolbars/view_toolbar.py`) with full functionality
    *   File group: Open (working), Save/SaveAs/Print (grayed)
    *   Navigation group: First/Prev/Next/Last page + page input (all working)
    *   Zoom group: Fit Page/Fit Width/Zoom Out/Zoom Dropdown/Zoom In (all working)
    *   Layout group: Single Page (grayed), Continuous (active), Facing (grayed)
    *   Rotate group: Rotate Left/Right (both grayed)
*   **UX3.3:** ⬜ Create stub toolbars with grayed buttons and "Coming soon" tooltips
    *   Comment Toolbar (`src/ui/toolbars/comment_toolbar.py`)
    *   Edit Toolbar (`src/ui/toolbars/edit_toolbar.py`)
    *   Organize Toolbar (`src/ui/toolbars/organize_toolbar.py`)
    *   Convert & OCR Toolbar (`src/ui/toolbars/convert_toolbar.py`)
*   **UX3.4:** ⬜ Connect all View Toolbar signals to existing MainWindow methods

### Phase 4: Left Sidebar Structure
*   **UX4.1:** ⬜ Create LeftSidebar container (`src/ui/sidebar/left_sidebar.py`)
    *   48px icon rail + 232px content panel
*   **UX4.2:** ⬜ Create SidebarIconRail component (`src/ui/sidebar/sidebar_icon_rail.py`)
    *   4 icon buttons: Pages, Bookmarks, Search, Attachments
    *   Implement active state highlighting
*   **UX4.3:** ⬜ Set up QStackedWidget for switchable content panels

### Phase 5: Sidebar Content Panels
*   **UX5.1:** ⬜ Create Pages/Thumbnails Panel (`src/ui/sidebar/panels/pages_panel.py`)
    *   Scrollable list of page thumbnails with lazy loading
    *   Render thumbnails on-demand (visible pages + buffer)
    *   Highlight current page, emit page_clicked signal
*   **UX5.2:** ⬜ Create Bookmarks Panel (`src/ui/sidebar/panels/bookmarks_panel.py`)
    *   Tree view with expand/collapse functionality
    *   Load bookmarks from PDF outline/TOC
    *   Show "No bookmarks" empty state when applicable
    *   Emit bookmark_clicked signal with page number
*   **UX5.3:** ⬜ Refactor existing Search Panel (`src/ui/sidebar/panels/search_panel.py`)
    *   Move from accordion to sidebar panel
    *   Update styling to match new design
    *   Preserve all existing search functionality
*   **UX5.4:** ⬜ Create Attachments Panel stub (`src/ui/sidebar/panels/attachments_panel.py`)
    *   Show "No attachments" or "Coming soon" message
*   **UX5.5:** ⬜ Connect all panel signals to MainWindow

### Phase 6: Right Properties Panel
*   **UX6.1:** ⬜ Create RightPanel component (`src/ui/right_panel.py`)
    *   Collapsible panel with smooth animations
    *   Default state: Hidden or shows "No selection"
*   **UX6.2:** ⬜ Add toggle button for showing/hiding right panel
*   **UX6.3:** ⬜ Create empty state display ("No selection" message)
*   **UX6.4:** ⬜ Prepare stubs for future property panels (highlight, text, object properties)

### Phase 7: Status Bar Enhancement
*   **UX7.1:** ⬜ Create new StatusBar component (`src/ui/status_bar_new.py`)
    *   Left section: Page size display (e.g., "A4 210×297 mm")
    *   Center section: Current page info (e.g., "Page 3 of 25")
    *   Right section: Zoom level and mode (e.g., "Zoom: 100%   Mode: View")
*   **UX7.2:** ⬜ Implement update methods for dynamic content

### Phase 8: Backend Enhancements
*   **UX8.1:** ⬜ Add `get_bookmarks()` method to PyMuPDFBackend
    *   Return list of (level, title, page_number) tuples from PDF TOC
*   **UX8.2:** ⬜ Add `get_attachments()` method stub to PyMuPDFBackend
    *   Return empty list for now (future implementation)
*   **UX8.3:** ⬜ Optimize thumbnail rendering for lazy loading

### Phase 9: MainWindow Integration
*   **UX9.1:** ⬜ Refactor MainWindow layout structure
    *   Remove old menu bar and toolbar
    *   Add AppBar at top
    *   Add ModeTabs below AppBar
    *   Add QStackedWidget for context toolbars
    *   Update splitter: LeftSidebar | Canvas | RightPanel
    *   Add new StatusBar at bottom
*   **UX9.2:** ⬜ Implement mode switching logic
    *   Connect ModeTabs.mode_changed to toolbar switching
    *   Update status bar to show current mode
*   **UX9.3:** ⬜ Connect all toolbar signals to existing methods
    *   File operations, navigation, zoom, layout controls
*   **UX9.4:** ⬜ Connect sidebar panel signals
    *   Pages panel page selection
    *   Bookmarks navigation
    *   Search functionality (already exists, just reconnect)
*   **UX9.5:** ⬜ Implement keyboard shortcuts compatibility
    *   Ensure all existing shortcuts still work
    *   Add new shortcuts if needed (e.g., Ctrl+B for sidebar toggle)

### Phase 10: Polish & Cleanup
*   **UX10.1:** ⬜ Remove unused old UI code (old toolbar, menu bar, accordion panel)
*   **UX10.2:** ⬜ Test all existing functionality still works
    *   Open/close documents
    *   Page navigation (all methods)
    *   Zoom controls (all methods)
    *   Text search and highlighting
    *   Text selection and copying
    *   Theme switching
*   **UX10.3:** ⬜ Test new functionality
    *   Mode tab switching
    *   Sidebar panel switching
    *   Thumbnail navigation
    *   Bookmark navigation
    *   Right panel toggle
*   **UX10.4:** ⬜ Verify lazy loading performance
    *   Large documents (1000+ pages) load quickly
    *   Thumbnails render on-demand
    *   Canvas rendering still performant
*   **UX10.5:** ⬜ Update documentation
    *   README.md with new UI description
    *   Screenshots of new interface
    *   Keyboard shortcuts reference
*   **UX10.6:** ⬜ Final visual polish
    *   Consistent spacing and alignment
    *   Smooth animations and transitions
    *   Proper focus states and hover effects
    *   Accessibility considerations

### Phase 11: Future Enhancements (Post-MVP)
*   **UX11.1:** ⬜ Implement Comment mode functionality (F4 features)
*   **UX11.2:** ⬜ Implement Edit mode functionality (F2 features)
*   **UX11.3:** ⬜ Implement Organize mode functionality (F3, F5 features)
*   **UX11.4:** ⬜ Implement Convert & OCR mode functionality (F6, F7 features)
*   **UX11.5:** ⬜ Add right panel property editors for each mode
*   **UX11.6:** ⬜ Implement Save, Save As, and Print functionality
*   **UX11.7:** ⬜ Implement page rotation functionality
*   **UX11.8:** ⬜ Implement Single Page and Facing page view modes
*   **UX11.9:** ⬜ Implement attachments panel functionality
*   **UX11.10:** ⬜ Add context menus and additional polish features
