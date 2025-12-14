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
