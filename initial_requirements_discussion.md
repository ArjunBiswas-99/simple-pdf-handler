# Initial Requirements Discussion

**Date:** December 23, 2024  
**Project:** Simple PDF Handler - Professional PDF Management Application  
**Target:** CEO Demo & Production-Ready Application

---

## Executive Summary

Building a professional, cross-platform PDF management application using Python with a modern, enterprise-grade user interface. The application will provide comprehensive PDF viewing, editing, annotation, and conversion capabilities comparable to Adobe Acrobat, but as an open-source solution.

**Development Approach:**
- Build complete UI shell first (all features visible)
- Implement core features F1 & F2 initially
- Features F3-F8 present but marked "Coming Soon"
- Demo-ready from week 1, fully functional core by week 4

---

## Technology Stack

### Core Technologies

**GUI Framework:**
- **PySide6 (Qt6 for Python)** - Version 6.6.0+
- Official Qt implementation with LGPL license
- Professional, native-looking UI on all platforms
- No Node.js/npm dependencies required
- Built-in theming, styling, and modern widgets
- QML support for fluid interfaces
- Cross-platform: Windows, macOS, Linux

**PDF Processing:**
- **PyMuPDF (fitz)** - Version 1.23.0+
  - Primary engine for display, rendering, annotations
  - Fast performance, excellent quality
  - Text selection and extraction
  - Basic editing capabilities

- **pikepdf** - Version 8.0.0+
  - Low-level PDF manipulation
  - Content stream editing
  - Deep PDF structure access

- **pdfplumber** - Version 0.10.0+
  - Advanced text extraction with layout preservation
  - Table detection and parsing
  - Smart content analysis

- **reportlab** - Version 4.0.0+
  - PDF generation from scratch
  - Content reconstruction for complex edits

**Additional Libraries:**
```python
Pillow>=10.0.0              # Image manipulation
pytesseract>=0.3.10         # OCR capabilities
python-docx>=1.1.0          # Word document handling
openpyxl>=3.1.0             # Excel handling
python-dateutil>=2.8.2      # Date utilities
```

### Platform Support
- **Operating Systems:** Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python Version:** 3.8+
- **Architecture:** x64, ARM64 (Apple Silicon)

---

## Feature Requirements

### F1: PDF Viewing and Navigation ✅ (Phase 2 Implementation)
- Open PDF files from local storage
- Accurate rendering (text, images, vector graphics)
- Page navigation (next, previous, first, last, go to page)
- Zoom controls (50%, 75%, 100%, 125%, 150%, 200%, fit width, fit page)
- Text search within document
- Text selection and copying
- Image selection and copying
- Display existing annotations

### F2: PDF Editing ✅ (Phase 3 Implementation)
- Add new text with font customization (font, size, color, style)
- Edit existing text properties where possible
- Insert images into pages
- Resize, move, and delete images
- Move, resize, delete PDF objects
- Change object properties (color, line width, etc.)

### F3: Page Management 🔜 (Future Release)
- Insert pages from other PDFs or blank pages
- Delete specific pages
- Rotate individual pages
- Reorder pages within document
- Crop pages
- Extract pages to new PDF
- Replace pages with content from other PDFs

### F4: Annotation and Markup 🔜 (Future Release)
- Highlight annotations
- Underline and strikethrough
- Sticky notes and comments
- Text boxes and callouts
- Draw shapes (rectangles, circles, lines)
- Standard stamps
- Measure distances and areas

### F5: Merging and Combining 🔜 (Future Release)
- Merge multiple PDFs
- Specify order during merge
- Insert specific pages from one PDF to another

### F6: Conversion 🔜 (Future Release)
**Export from PDF:**
- Word format (.docx)
- Excel format (.xlsx)
- PowerPoint format (.pptx)
- Image formats (JPEG, PNG, TIFF)
- HTML format
- Plain text format

**Import to PDF:**
- From Word documents
- From Excel spreadsheets
- From PowerPoint presentations
- From image files
- From web page content (URL or HTML)

### F7: OCR (Optical Character Recognition) 🔜 (Future Release)
- Perform OCR on scanned PDFs or images
- Make recognized text searchable and selectable
- Save OCR-processed PDFs

### F8: File Management ✅ (Phase 2-3 Implementation)
- Save current PDF document
- Save As (new name or location)
- Print current document
- Print with annotations visible

---

## Text Selection & Editing Approach

### Text Selection (Fully Supported)
**Capabilities:**
- Click and drag selection (any text range)
- Double-click: select word
- Triple-click: select line/paragraph
- Ctrl+A: select all text on page
- Copy to clipboard (Ctrl+C)
- Search and select all occurrences
- Selection persists across zoom/pan
- Works in all modes (view, annotate, edit)

**Technical Implementation:**
- PyMuPDF provides complete text extraction with positioning
- Text stored with coordinates, fonts, sizes
- Smart block detection for logical grouping
- Real-time visual feedback (blue selection overlay)
- Context menu on right-click

### Text Editing (Two-Mode Approach)

**Mode 1: Direct Text Editing (Simple PDFs)**
- For PDFs with clear text structure
- Inline editing where possible
- PyMuPDF + pikepdf content stream manipulation
- Maintains fonts and positioning
- Works for: simple documents, embedded fonts, clear layouts

**Mode 2: Conversion-Based Editing (Complex PDFs)**
- For complex layouts that would break with direct editing
- Extract content with layout preservation (pdfplumber)
- Edit in rich text editor (QTextEdit)
- User warning about potential layout changes
- Regenerate PDF page (reportlab + pikepdf)
- Show before/after preview

**User Experience:**
- Transparent about editing limitations
- Preview changes before applying
- Undo/redo support throughout
- Professional warning dialogs for complex operations

---

## User Experience Design

### Design Philosophy

**Core Principles:**
- **Professional:** Enterprise-grade appearance suitable for CEO presentation
- **Modern:** Contemporary design language (2024 standards)
- **Intuitive:** Zero learning curve, familiar patterns
- **Consistent:** Unified visual language throughout
- **Spacious:** Clean layout with breathing room
- **Responsive:** Smooth animations and transitions
- **Accessible:** Keyboard shortcuts, tooltips, clear hierarchy

**Inspiration Sources:**
- Adobe Acrobat DC (industry standard)
- Microsoft Office Ribbon Interface (organization)
- Foxit PDF Editor (clean functionality)
- Modern design trends (Fluent Design, Material Design principles)

---

## Application Layout

### Overall Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Menu Bar (Traditional menus for discoverability)                │
├─────────────────────────────────────────────────────────────────┤
│  Ribbon Toolbar (Context-sensitive, organized by function)       │
├──────┬──────────────────────────────────────────────────┬───────┤
│      │                                                  │       │
│ Left │          Main PDF Content Area                   │ Right │
│ Side │         (Document Viewer)                        │ Panel │
│ bar  │                                                  │       │
│      │                                                  │       │
├──────┴──────────────────────────────────────────────────┴───────┤
│  Status Bar (Page info, zoom, status indicators)                │
└─────────────────────────────────────────────────────────────────┘
```

### Menu Bar

```
File    Edit    View    Document    Page    Annotate    Convert    Help
```

**File Menu:**
- Open (Ctrl+O)
- Recent Files (submenu)
- Save (Ctrl+S)
- Save As (Ctrl+Shift+S)
- Print (Ctrl+P)
- Close (Ctrl+W)
- Exit (Ctrl+Q)

**Edit Menu:**
- Undo (Ctrl+Z)
- Redo (Ctrl+Y)
- Cut (Ctrl+X)
- Copy (Ctrl+C)
- Paste (Ctrl+V)
- Delete (Del)
- Select All (Ctrl+A)

**View Menu:**
- Zoom In (Ctrl++)
- Zoom Out (Ctrl+-)
- Fit Page (Ctrl+0)
- Fit Width
- Rotate (Ctrl+R)
- View Mode (Single Page, Continuous, Two-Page Spread)
- Show/Hide Panels
- Grid Lines
- Rulers
- Full Screen (F11)

**Document Menu:**
- Properties (Ctrl+D)
- Security Settings
- Optimize Size
- Merge PDFs 🔜
- Split PDF 🔜

**Page Menu:**
- Insert Page 🔜
- Delete Page 🔜
- Extract Pages 🔜
- Rotate Page
- Crop Page 🔜
- Reorder Pages 🔜

**Annotate Menu:**
- Highlight Text
- Underline 🔜
- Strikethrough 🔜
- Add Comment 🔜
- Add Stamp 🔜
- Draw Shapes 🔜
- Measure Tools 🔜

**Convert Menu:**
- Export to Word 🔜
- Export to Excel 🔜
- Export to PowerPoint 🔜
- Export to Image 🔜
- Import from Word 🔜
- Import from Image 🔜
- OCR Document 🔜

**Help Menu:**
- User Guide
- Keyboard Shortcuts
- About
- Check for Updates
- License Information

### Ribbon Toolbar

**Tab Structure:**
- Home (Default view)
- Edit (Text and object editing)
- Annotate (Markup tools)
- Page (Page management)
- Convert (Format conversion)

**Home Tab:**
```
┌─────────────┬─────────────────┬──────────────────┬──────────────┬──────────┐
│   FILE      │     VIEW        │    NAVIGATION    │    TOOLS     │  HELP    │
├─────────────┼─────────────────┼──────────────────┼──────────────┼──────────┤
│ 📂 Open     │ 🔍 Zoom In     │ ⏮️ First        │ 🖊️ Edit     │ ℹ️ Info  │
│ 💾 Save     │ 🔎 Zoom Out    │ ◀️ Previous     │ ✏️ Annotate  │ ⌨️ Keys  │
│ 🖨️ Print    │ ⚲ Fit Page    │ ▶️ Next         │ 📝 Comment   │          │
│ 📤 Export   │ 🔄 Rotate      │ ⏭️ Last         │ 🔧 Tools     │          │
└─────────────┴─────────────────┴──────────────────┴──────────────┴──────────┘
```

**Edit Tab:**
```
┌──────────────┬───────────────┬─────────────────┬──────────────┐
│ TEXT EDIT    │   OBJECTS     │   PROPERTIES    │   ACTIONS    │
├──────────────┼───────────────┼─────────────────┼──────────────┤
│ ✏️ Add Text  │ 🖼️ Add Image  │ 🎨 Font        │ ↩️ Undo      │
│ 📝 Edit Text │ ⬜ Add Shape  │ 📏 Size        │ ↪️ Redo      │
│ 🗑️ Delete    │ ➡️ Add Arrow  │ 🌈 Color       │ 💾 Save      │
└──────────────┴───────────────┴─────────────────┴──────────────┘
```

**Annotate Tab:**
```
┌────────────────┬──────────────┬─────────────┬──────────────┐
│   MARKUP       │   DRAWING    │   COMMENTS  │   STAMPS     │
├────────────────┼──────────────┼─────────────┼──────────────┤
│ 🖍️ Highlight   │ ✏️ Pen       │ 💬 Comment  │ ✓ Approved   │
│ __ Underline   │ ⬜ Rectangle │ 📌 Note     │ ❌ Rejected  │
│ S̶ Strike      │ ⭕ Circle    │ 📎 Attach   │ ⚠️ Review    │
│  (Coming Soon) │ ↗️ Arrow     │ (Coming)    │ (Coming)     │
└────────────────┴──────────────┴─────────────┴──────────────┘
```

**Page Tab:**
```
┌──────────────┬─────────────┬───────────────┬──────────────┐
│  ORGANIZE    │   EXTRACT   │    MODIFY     │   COMBINE    │
├──────────────┼─────────────┼───────────────┼──────────────┤
│ ➕ Insert     │ 📤 Extract  │ 🔄 Rotate     │ 🔗 Merge     │
│ 🗑️ Delete     │ 📋 Copy     │ ✂️ Crop       │ ➕ Combine   │
│ ⬆️ Move Up    │ 💾 Save As  │ 📐 Resize     │ 🧩 Split     │
│  (Coming)     │  (Coming)   │               │  (Coming)    │
└──────────────┴─────────────┴───────────────┴──────────────┘
```

**Convert Tab:**
```
┌────────────────┬──────────────────┬─────────────────┐
│   EXPORT TO    │   IMPORT FROM    │   OPTIONS       │
├────────────────┼──────────────────┼─────────────────┤
│ 📄 Word        │ 📄 Word          │ ⚙️ Settings     │
│ 📊 Excel       │ 🖼️ Image         │ 🎯 Quality      │
│ 📽️ PowerPoint  │ 🌐 Web Page      │ 🔍 OCR          │
│ 🖼️ Image       │                  │                 │
│  (Coming Soon for all)            │  (Coming)       │
└────────────────┴──────────────────┴─────────────────┘
```

### Left Sidebar (Collapsible)

**Panel Tabs:**
- 📑 Pages (Thumbnail view)
- 🔖 Bookmarks (Document navigation)
- 📝 Comments (Annotations list) 🔜
- 🔍 Search (Find in document)
- 📋 Layers (PDF layers) 🔜

**Pages Panel:**
- Grid of page thumbnails
- Current page highlighted
- Click to jump to page
- Right-click for page options
- + Add Page button

**Search Panel:**
- Search text input
- Match case checkbox
- Whole words checkbox
- Results list with page numbers
- Click result to jump

**Width:** 240px (collapsible to 0px)

### Main Content Area

**View Modes:**

1. **Single Page Mode**
   - One page at a time
   - Centered in view
   - Optimal for reading

2. **Continuous Scroll Mode**
   - All pages in vertical scroll
   - Seamless reading experience
   - Most common mode

3. **Two-Page Spread**
   - Side-by-side pages
   - Book-like layout
   - Good for comparing pages

**Interaction Features:**
- Mouse wheel zoom (Ctrl+Wheel)
- Pan with middle mouse or space+drag
- Click and drag text selection
- Context menu on right-click
- Smooth scrolling
- Page number overlay during scroll

**Context Menu (Right-Click):**
- ✂️ Copy Text
- 🖼️ Copy Image
- ─────────────
- 🖍️ Highlight Selection
- __ Underline Text
- 💬 Add Comment
- ─────────────
- 🔍 Search Document
- 📋 Select All
- ─────────────
- Properties

### Right Sidebar (Collapsible)

**Panel Tabs:**
- 🎨 Format (Text/object properties)
- 📋 Properties (Document metadata)
- 🔖 Bookmarks (Navigation) 🔜
- ✎ Annotations (Review) 🔜
- 💬 Comments (Threads) 🔜

**Format Panel (when text selected):**
```
Font Family:    [Arial ▼]
Font Size:      [12 ▼]
Color:          [████████████]
Style:          [B] [I] [U] [S]
Alignment:      [≡] [≣] [≡] [≡]
[Apply Changes]
```

**Properties Panel:**
```
Title:          [Document.pdf]
Author:         [John Doe]
Subject:        [...]
Keywords:       [...]
Pages:          45
Size:           2.3 MB
Created:        2024-12-20
Modified:       2024-12-23
[Edit Metadata]
```

**Width:** 280px (collapsible to 0px)

### Status Bar

**Left Section:**
- Page counter: "Page 1 of 45"
- Clickable for "Go to Page" dialog

**Center Section:**
- Zoom level: "100%"
- Clickable for zoom menu
- Zoom slider

**Right Section:**
- File size: "2.3 MB"
- Modification status: "Modified" / "Saved"
- Security: 🔒 icon if protected
- Status message: "Ready" / "Processing..." / "Saving..."

**Height:** 28px

---

## Visual Design Specification

### Color Palette

**Light Mode (Default):**
```
Primary Colors:
  Background:      #FFFFFF (Pure white)
  Surface:         #F5F5F5 (Light gray panels)
  Primary:         #0078D4 (Microsoft Blue - interactive elements)
  Secondary:       #606060 (Medium gray - secondary text)
  Accent:          #FFB900 (Gold - highlights, warnings)

Text Colors:
  Primary Text:    #1F1F1F (Almost black - main content)
  Secondary Text:  #605E5C (Medium gray - labels, hints)
  Disabled Text:   #A19F9D (Light gray - disabled items)
  Link Text:       #0078D4 (Blue - clickable links)

UI Elements:
  Border:          #E1DFDD (Light border lines)
  Divider:         #EDEBE9 (Section separators)
  Hover:           #F3F2F1 (Hover state background)
  Active:          #E1DFDD (Active/pressed state)
  
Semantic Colors:
  Success:         #107C10 (Green - success messages)
  Warning:         #FFB900 (Amber - warnings)
  Error:           #E81123 (Red - errors)
  Info:            #0078D4 (Blue - informational)
```

**Dark Mode:**
```
Primary Colors:
  Background:      #1E1E1E (Dark gray)
  Surface:         #2D2D2D (Lighter dark - panels)
  Primary:         #0078D4 (Blue - unchanged)
  Secondary:       #A19F9D (Light gray)
  Accent:          #FFB900 (Gold - unchanged)

Text Colors:
  Primary Text:    #FFFFFF (White)
  Secondary Text:  #B3B3B3 (Light gray)
  Disabled Text:   #6D6D6D (Medium gray)
  Link Text:       #4A9EFF (Lighter blue)

UI Elements:
  Border:          #3F3F3F (Medium gray)
  Divider:         #2D2D2D (Dark separator)
  Hover:           #3F3F3F (Hover background)
  Active:          #4D4D4D (Active state)

Semantic Colors:
  Success:         #0F7B0F (Slightly darker green)
  Warning:         #FFB900 (Unchanged)
  Error:           #E81123 (Unchanged)
  Info:            #4A9EFF (Lighter blue)
```

### Typography

**Font Families:**
```
Primary:    Segoe UI (Windows), San Francisco (macOS), Ubuntu (Linux)
Fallback:   -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif
Monospace:  Consolas, Monaco, 'Courier New', monospace
```

**Font Sizes & Weights:**
```
Headings:
  H1: 18pt, Semibold (600)  - Main window title
  H2: 16pt, Semibold (600)  - Section headers
  H3: 14pt, Semibold (600)  - Subsection headers
  H4: 12pt, Semibold (600)  - Panel titles

Body Text:
  Normal:   11pt, Regular (400)  - Main content
  Small:    10pt, Regular (400)  - Secondary info
  Tiny:     9pt, Regular (400)   - Status bar, hints

Buttons:
  Large:    11pt, Semibold (600)  - Primary actions
  Normal:   10pt, Semibold (600)  - Standard buttons
  Small:    9pt, Semibold (600)   - Compact buttons

Special:
  Code:     10pt, Regular (400)   - Monospace
  Caption:  9pt, Regular (400)    - Image captions
```

**Line Height:**
```
Headings:     1.2 (120%)
Body:         1.5 (150%)
Buttons:      1.0 (100%)
Dense:        1.3 (130%) - Compact lists
```

**Letter Spacing:**
```
Headings:     -0.2px (tighter)
Normal:       0px (default)
Uppercase:    0.5px (looser) - All-caps labels
```

### Iconography

**Icon System:**
- **Source:** Material Design Icons + Custom icons
- **Sizes:** 16px (small), 20px (medium), 24px (large), 32px (toolbar), 48px (welcome)
- **Style:** Outlined (not filled) for modern, clean look
- **Color:** Match text color (respect theme)
- **Padding:** 8px around clickable icons

**Icon Categories:**

**File Operations:**
- 📂 Open (folder-open-outline)
- 💾 Save (content-save)
- 🖨️ Print (printer)
- 📤 Export (export)
- 📥 Import (import)

**Navigation:**
- ⏮️ First (page-first)
- ◀️ Previous (chevron-left)
- ▶️ Next (chevron-right)
- ⏭️ Last (page-last)

**View Controls:**
- 🔍 Zoom In (magnify-plus)
- 🔎 Zoom Out (magnify-minus)
- ⚲ Fit Page (fit-to-page)
- 🔄 Rotate (rotate-right)

**Edit Tools:**
- ✏️ Edit (pencil)
- 🖊️ Add Text (text-box)
- 🖼️ Image (image)
- ⬜ Shape (shape)

**Annotations:**
- 🖍️ Highlight (marker)
- 💬 Comment (comment)
- 📌 Note (note)
- ✓ Stamp (check-circle)

**Common:**
- ⚙️ Settings (cog)
- ℹ️ Info (information)
- ⌨️ Keyboard (keyboard)
- 🔒 Security (lock)
- ↩️ Undo (undo)
- ↪️ Redo (redo)

### Button Styles

**Primary Button:**
```css
Background:       #0078D4 (Blue)
Text:            #FFFFFF (White)
Border:          None
Border-radius:   4px
Padding:         8px 16px
Font:            10pt Semibold
Shadow:          0 2px 4px rgba(0,0,0,0.1)

Hover:
  Background:    #106EBE (Darker blue)
  Shadow:        0 4px 8px rgba(0,0,0,0.15)

Active/Pressed:
  Background:    #005A9E (Even darker)
  Shadow:        0 1px 2px rgba(0,0,0,0.2)

Disabled:
  Background:    #F3F2F1 (Light gray)
  Text:          #A19F9D (Gray)
  Shadow:        None
```

**Secondary Button:**
```css
Background:       #F3F2F1 (Light gray)
Text:            #1F1F1F (Dark)
Border:          1px solid #8A8886 (Medium gray)
Border-radius:   4px
Padding:         8px 16px
Font:            10pt Semibold
Shadow:          None

Hover:
  Background:    #E1DFDD
  Border:        1px solid #605E5C

Active:
  Background:    #D2D0CE

Disabled:
  Background:    #F3F2F1
  Text:          #A19F9D
  Border:        1px solid #EDEBE9
```

**Icon Button:**
```css
Size:            32x32px (or 40x40px for large)
Icon:            16x16px (or 20px for large)
Background:      Transparent
Border:          None
Border-radius:   4px
Padding:         8px

Hover:
  Background:    #F3F2F1

Active:
  Background:    #E1DFDD

Selected:
  Background:    #E1DFDD
  Border:        2px solid #0078D4
```

**Toggle Button:**
```css
Similar to icon button, but:
  Selected state has blue background (#0078D4)
  Selected icon is white
```

### Spacing System

**Base Unit:** 8px

```
Micro:      4px   (0.5×)  - Tight spacing, icon padding
Small:      8px   (1×)    - Standard padding
Medium:     16px  (2×)    - Section spacing
Large:      24px  (3×)    - Panel margins
XLarge:     32px  (4×)    - Major section breaks
XXLarge:    48px  (6×)    - Welcome screen spacing
```

**Application:**
- Button padding: 8px vertical, 16px horizontal
- Panel padding: 16px
- Toolbar padding: 8px
- Grid gap: 8px
- Section margin: 24px
- Card padding: 16px
- List item padding: 8px

### Elevation & Shadows

**Shadow Levels:**

```css
Level 1 (Cards, Buttons):
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

Level 2 (Elevated panels):
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);

Level 3 (Dialogs, Modals):
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);

Level 4 (Dropdowns, Menus):
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
```

### Borders & Dividers

```css
Standard Border:
  width: 1px
  style: solid
  color: #E1DFDD (light) / #3F3F3F (dark)

Thick Border:
  width: 2px (for focus, selection)
  color: #0078D4 (primary)

Divider Line:
  height: 1px
  color: #EDEBE9 (light) / #2D2D2D (dark)
```

### Animations & Transitions

**Timing:**
```
Ultra-fast:    100ms  - Instant feedback (hover states)
Fast:          150ms  - Button interactions
Normal:        200ms  - Panel transitions, page changes
Smooth:        250ms  - Sidebar expand/collapse
Slow:          300ms  - Zoom, complex animations
```

**Easing Functions:**
```
ease-out:      Standard for appearing elements
ease-in:       For disappearing elements
ease-in-out:   For transformations (move, scale)
```

**Examples:**
```css
Button hover:
  transition: background-color 150ms ease-out;

Sidebar toggle:
  transition: width 250ms ease-in-out;

Page turn:
  transition: opacity 200ms ease-out;

Zoom:
  transition: transform 300ms ease-in-out;

Tooltip appear:
  transition: opacity 150ms ease-out;
```

**No jarring animations** - all motion is smooth and purposeful

---

## Interaction Patterns

### Keyboard Shortcuts

**File Operations:**
- Ctrl+O: Open file
- Ctrl+S: Save
- Ctrl+Shift+S: Save As
- Ctrl+P: Print
- Ctrl+W: Close document
- Ctrl+Q: Quit application

**Editing:**
- Ctrl+Z: Undo
- Ctrl+Y / Ctrl+Shift+Z: Redo
- Ctrl+X: Cut
- Ctrl+C: Copy
- Ctrl+V: Paste
- Delete: Delete selected
- Ctrl+A: Select all

**Navigation:**
- Page Up / Page Down: Scroll by page
- Home: First page
- End: Last page
- Ctrl+G: Go to page
- Ctrl+F: Find/Search

**View:**
- Ctrl++: Zoom in
- Ctrl+-: Zoom out
- Ctrl+0: Fit to page
- Ctrl+1: 100% zoom
- Ctrl+2: Fit width
- Ctrl+R: Rotate page
- F11: Full screen
- Escape: Exit full screen

**Advanced:**
- Ctrl+Shift+N: New window
- Ctrl+Tab: Next tab (if tabs implemented)
- Ctrl+Shift+Tab: Previous tab

### Mouse Interactions

**Single Click:**
- Select object
- Place cursor
- Activate button

**Double Click:**
- Select word
- Open file (in file list)

**Triple Click:**
- Select line/paragraph

**Click + Drag:**
- Select text
- Move object
- Pan view (with space key held)

**Right Click:**
- Context menu

**Middle Click + Drag:**
- Pan view

**Mouse Wheel:**
- Scroll vertically

**Ctrl + Mouse Wheel:**
- Zoom in/out

**Shift + Mouse Wheel:**
- Scroll horizontally

### Touch Gestures (Future)

- **Pinch:** Zoom in/out
- **Two-finger drag:** Pan
- **Swipe:** Navigate pages
- **Long press:** Context menu

### Tooltips

**Behavior:**
- Appear after 500ms hover
- Disappear immediately on mouse leave
- Include keyboard shortcut if applicable
- Position: Below element (or above if near bottom)
- Animation: Fade in 150ms

**Style:**
```css
Background:     #2D2D2D (dark tooltip)
Text:          #FFFFFF
Font:          9pt Regular
Padding:       6px 10px
Border-radius: 4px
Shadow:        0 2px 8px rgba(0,0,0,0.3)
```

**Example:**
```
┌────────────────┐
│ Open PDF       │
│ Ctrl+O         │
└────────────────┘
```

### Dialog Boxes

**Types:**

**Information Dialog:**
- Icon: ℹ️ (blue)
- Button: OK

**Warning Dialog:**
- Icon: ⚠️ (amber)
- Buttons: OK, Cancel

**Error Dialog:**
- Icon: ❌ (red)
- Button: OK

**Confirmation Dialog:**
- Icon: ❓ (blue)
- Buttons: Yes, No, Cancel

**Style:**
```css
Width:         400px (max)
Padding:       24px
Border-radius: 8px
Shadow:        Level 3
```

### Progress Indicators

**Determinate (known duration):**
- Progress bar with percentage
- Estimated time remaining
- Cancel button

**Indeterminate (unknown duration):**
- Spinning circle
- "Processing..." message
- Cancel button if applicable

**Inline Progress:**
- Small spinner next to action
- Used for quick operations

---

## Welcome Screen

**First Launch Experience:**

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│            📄 Simple PDF Handler                    │
│        Professional PDF Management                  │
│                                                     │
│         Version 1.0.0 | Open Source                │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │          │  │          │  │          │         │
│  │ 📂 Open  │  │ 📁 Recent│  │ 🎓 Tour  │         │
│  │  File    │  │  Files   │  │          │         │
│  │          │  │          │  │          │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                     │
│  Recent Documents:                                  │
│  • 📄 Report_Q4_2024.pdf        2.3 MB             │
│  • 📄 Proposal_ClientA.pdf      1.8 MB             │
│  • 📄 Manual_Product.pdf        5.2 MB             │
│                                                     │
│  Or drag & drop a PDF file here                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Clean, professional appearance
- Quick access to common actions
- Recent files list (last 5)
- Drag & drop support
- Keyboard accessible (Tab navigation)

---

## State Management

### Application States

**No Document Open:**
- Show welcome screen
- Minimal UI (menu bar only)
- File operations enabled
- Edit/view tools disabled

**Document Open - View Mode:**
- Full UI visible
- Navigation tools active
- Editing tools available but not active
- View controls prominent

**Document Open - Edit Mode:**
- Edit tools prominent
- Properties panel active
- Undo/redo visible
- Format controls enabled

**Text Selected:**
- Context menu available
- Copy enabled
- Format panel becomes relevant
- Highlight/annotate options shown

**Processing:**
- Progress indicator visible
- UI partially disabled
- Cancel option available
- Status bar shows progress

### Visual Feedback

**Hover States:**
- Subtle background change
- Shadow elevation (buttons)
- Cursor changes to pointer

**Active/Pressed States:**
- Darker background
- Inset shadow effect
- Visual confirmation of click

**Selection States:**
- Blue highlight (#0078D4)
- Border accent (2px)
- Distinct from hover

**Disabled States:**
- Reduced opacity (0.5)
- Gray text color
- Cursor: not-allowed

**Loading States:**
- Spinner or progress bar
- Disabled interactions
- Clear indication of activity

---

## Accessibility Features

**Keyboard Navigation:**
- Full keyboard access to all features
- Visible focus indicators (2px blue outline)
- Logical tab order
- Escape key closes dialogs

**Screen Reader Support:**
- ARIA labels on all interactive elements
- Alt text for icons and images
- Descriptive button labels
- Status announcements

**Visual Accessibility:**
- High contrast mode support
- Adjustable zoom (up to 200%)
- Clear visual hierarchy
- Sufficient color contrast ratios (WCAG AA)

**Customization:**
- Theme switching (light/dark)
- Font size adjustment
- Interface scaling
- Keyboard shortcut customization

---

## Performance Specifications

### Target Metrics

**File Opening:**
- Small PDFs (<5MB): < 1 second
- Medium PDFs (5-50MB): 1-3 seconds
- Large PDFs (50-100MB): 3-10 seconds
- Show progress bar for files > 5MB

**Page Rendering:**
- Current page: < 100ms
- Adjacent pages (cache): < 50ms
- 60 FPS scrolling maintained

**Zoom Operations:**
- Zoom change: < 200ms
- Smooth animation during zoom

**Search:**
- Index small documents: < 1 second
- Search results: < 500ms per page
- Incremental search update

**Save Operations:**
- Save changes: < 2 seconds for most files
- Show progress for large operations
- Auto-save every 5 minutes (optional)

### Memory Management

**Optimization Strategies:**
- Cache visible pages + 2 before/after
- Unload distant pages from memory
- Compress cached page images
- Limit maximum cache size (500MB)

**Threading:**
- UI thread: interaction only
- Worker threads: PDF operations, rendering
- Background thread: auto-save, indexing

---

## Error Handling

### Error Categories

**File Errors:**
- File not found
- Permission denied
- Corrupt PDF
- Unsupported PDF version
- Password-protected PDF

**Operation Errors:**
- Edit operation failed
- Save failed (disk full, permissions)
- Print error
- Conversion error

**User Errors:**
- Invalid input
- Operation cancelled
- Unsupported action

### Error Presentation

**Error Dialog:**
```
┌────────────────────────────────────┐
│  ❌ Error                          │
├────────────────────────────────────┤
│                                    │
│  Failed to open PDF file           │
│                                    │
│  The file may be corrupted or      │
│  in an unsupported format.         │
│                                    │
│  Details:                          │
│  • Error code: PDF_PARSE_ERROR     │
│  • File: document.pdf              │
│                                    │
│  [📋 Copy Details]  [OK]           │
│                                    │
└────────────────────────────────────┘
```

**Features:**
- Clear error message
- Actionable next steps
- Technical details (collapsible)
- Copy error details option
- Help link if applicable

### Graceful Degradation

**Fallback Strategies:**
- If font not available: use similar font
- If image can't render: show placeholder
- If operation fails: revert to previous state
- Always maintain undo capability

---

## Development Phases

### Phase 1: UI Shell (Week 1) ✅

**Deliverable:** Complete visual interface with all elements present

**Tasks:**
- Main window layout (menu, toolbar, panels, status bar)
- All toolbar buttons and menus (visual only)
- Sidebar panels (Pages, Search, etc.)
- Right panel (Format, Properties)
- Welcome screen
- All dialogs and modals
- Theme implementation (light/dark)
- Icon system setup

**Status:**
- All features visible in UI
- Non-functional features show "Coming Soon"
- Beautiful, demo-ready appearance
- Professional styling throughout

**Demo-Ready:** Yes ✅

### Phase 2: F1 - Viewing & Navigation (Week 2) ✅

**Deliverable:** Functional PDF viewing and navigation

**Implementation:**
- PyMuPDF integration for PDF rendering
- Open file functionality
- Page rendering with quality settings
- Zoom controls (in/out, fit page, fit width, percentage)
- Page navigation (next, prev, first, last, go to page)
- Thumbnail generation and sidebar
- Text search with highlighting
- Text selection and copy to clipboard
- Image selection and extraction
- Scroll modes (single page, continuous)
- View modes (single, two-page spread)
- Rotation controls

**Testing:**
- Test with various PDF types
- Performance testing (file sizes)
- Text selection accuracy
- Search functionality
- Memory usage optimization

**Demo-Ready:** Yes ✅

### Phase 3: F2 - Editing (Weeks 3-4) ✅

**Deliverable:** Text and object editing capabilities

**Implementation:**
- Text editing mode activation
- PDF structure analysis (editability check)
- Direct text editing (simple PDFs)
- Text addition tool
- Font selection and formatting
- Color picker
- Text size adjustment
- Image insertion tool
- Image manipulation (move, resize, delete)
- Object selection and properties
- Undo/redo system
- Format panel integration
- Save functionality
- Save As functionality

**Testing:**
- Edit various PDF types
- Test font handling
- Image insertion quality
- Undo/redo reliability
- Save integrity

**Demo-Ready:** Yes ✅

### Phase 4: Annotation Tools (F4 - Partial) (Week 5) 🔜

**Deliverable:** Basic annotation capabilities

**Implementation:**
- Highlight tool
- Text selection to highlight
- Color picker for highlights
- Comment/note addition
- Basic stamp functionality

**Demo-Ready:** Yes ✅

### Phase 5-8: Advanced Features (F3, F5-F8) (Weeks 6+) 🔜

**Deferred to future releases:**
- Page management (F3)
- Merging/combining (F5)
- Format conversion (F6)
- OCR capabilities (F7)

**Strategy:**
- Build based on user feedback
- Prioritize most-requested features
- Maintain code quality
- Add comprehensive tests

---

## CEO Demo Script

**Duration:** 90 seconds  
**Goal:** Show professional, production-ready application

### Act 1: Opening (10 seconds)
```
1. Launch application
   → Professional welcome screen appears
   → Clean, modern interface
   
2. Click "Open File"
   → Native file dialog
   → Select sample PDF
   
3. PDF loads
   → Smooth loading animation
   → Thumbnail sidebar populates
   → Status bar shows file info
```

### Act 2: Navigation (20 seconds)
```
4. Scroll through pages
   → Smooth, responsive scrolling
   → High-quality rendering
   
5. Use zoom controls
   → Zoom in to 150%
   → Zoom out to 75%
   → Fit to page
   → All transitions smooth
   
6. Thumbnail navigation
   → Click page 10 in sidebar
   → Jump to page instantly
   → Highlight current page
   
7. Search function
   → Search for "revenue"
   → Results highlight in real-time
   → Jump to occurrences
```

### Act 3: Text Interaction (15 seconds)
```
8. Text selection
   → Click and drag to select paragraph
   → Blue highlight overlay
   → Selection smooth and accurate
   
9. Copy text
   → Right-click → Copy
   → Or Ctrl+C
   → Confirmation in status bar
```

### Act 4: Editing (30 seconds)
```
10. Activate Edit mode
    → Click "Edit Text" button
    → UI shifts to edit mode
    → Format panel becomes active
    
11. Add new text
    → Click "Add Text" button
    → Click on page
    → Type "CONFIDENTIAL"
    → Text appears immediately
    
12. Format text
    → Select new text
    → Change font to "Arial"
    → Increase size to 24pt
    → Change color to red
    → Format panel updates in real-time
    
13. Add annotation
    → Select some text
    → Click "Highlight" button
    → Yellow highlight applied
    → Professional appearance
```

### Act 5: Professional Features (10 seconds)
```
14. Show page management panel
    → Display grid of thumbnails
    → Clean, organized view
    
15. Show "Coming Soon" features
    → Point to Merge, Convert, OCR
    → "Full feature set in development"
    → Clear roadmap visible
    
16. Theme toggle (if time)
    → Switch to dark mode
    → Instant, professional transition
    → All elements update cohesively
```

### Act 6: Save & Conclusion (5 seconds)
```
17. Save changes
    → Click "Save" button
    → Progress indicator (brief)
    → "Document saved successfully"
    
18. Final message
    → Status bar: "Ready"
    → All features functional
    → Professional, polished appearance
```

### Talking Points

**For Investor/CEO:**
- "Enterprise-grade PDF management"
- "Open-source, no licensing fees"
- "Cross-platform: Windows, Mac, Linux"
- "Core features functional now"
- "Advanced features in development"
- "Professional quality, free software"
- "Comparable to Adobe Acrobat"
- "Customizable for enterprise needs"

**Technical Highlights:**
- Python-based, maintainable
- Qt framework (industry standard)
- Modern design principles
- SOLID architecture
- Extensible codebase
- Active development

---

## Next Steps

### Immediate Actions

1. **Review & Approval**
   - Review this requirements document
   - Confirm UX design direction
   - Approve tech stack choices

2. **Project Setup**
   - Initialize Git repository
   - Set up project structure
   - Install dependencies
   - Configure development environment

3. **Begin Phase 1**
   - Create main window skeleton
   - Implement layout structure
   - Add menu and toolbar (visual)
   - Style with Qt Style Sheets

### Questions for Clarification

1. **Branding:**
   - Application name finalized as "Simple PDF Handler"?
   - Any logo or branding assets needed?
   - Color scheme adjustments desired?

2. **Platform Priority:**
   - Which platform to develop on first?
   - Target deployment platforms?

3. **Features:**
   - Any features to prioritize differently?
   - Any features to defer further?

4. **Timeline:**
   - Hard deadline for CEO demo?
   - Milestone dates?

---

## Appendix

### Technology References

**PySide6 Documentation:**
- Official docs: https://doc.qt.io/qtforpython-6/
- Qt Widgets: https://doc.qt.io/qt-6/qtwidgets-index.html
- Qt Style Sheets: https://doc.qt.io/qt-6/stylesheet.html

**PyMuPDF Documentation:**
- Official docs: https://pymupdf.readthedocs.io/
- GitHub: https://github.com/pymupdf/PyMuPDF
- Examples: https://pymupdf.readthedocs.io/en/latest/recipes.html

**Design Resources:**
- Material Design: https://material.io/design
- Microsoft Fluent: https://fluent2.microsoft.design/
- Qt Design Guidelines: https://doc.qt.io/qt-6/design-principles.html

### File Structure Preview

```
simple-pdf-handler/
├── README.md
├── LICENSE
├── requirements.txt
├── initial_requirements_discussion.md
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pdf_engine.py
│   │   ├── document.py
│   │   ├── text_editor.py
│   │   └── operations.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── pdf_viewer.py
│   │   ├── toolbar.py
│   │   ├── sidebar.py
│   │   ├── status_bar.py
│   │   ├── welcome_screen.py
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── open_dialog.py
│   │       ├── save_dialog.py
│   │       └── properties_dialog.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── annotation.py
│   │   ├── text_tools.py
│   │   └── image_tools.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── themes.py
│   │   └── helpers.py
│   └── resources/
│       ├── icons/
│       ├── themes/
│       │   ├── light.qss
│       │   └── dark.qss
│       └── images/
├── tests/
│   ├── __init__.py
│   ├── test_pdf_engine.py
│   ├── test_text_editor.py
│   └── test_gui.py
└── docs/
    ├── user_guide.md
    ├── developer_guide.md
    └── api_reference.md
```

---

## Conclusion

This document captures the comprehensive vision for the Simple PDF Handler application. The design prioritizes:

1. **Professional appearance** suitable for CEO presentation
2. **Modern UX** with contemporary design language
3. **Pragmatic implementation** with phased rollout
4. **Clear roadmap** with "Coming Soon" features visible
5. **Solid technical foundation** using proven technologies

The application will compete with commercial PDF editors while remaining open-source and free. The UX design ensures immediate visual appeal, while the phased implementation guarantees functional core features within 4 weeks.

**Status:** Ready to proceed with development ✅

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2024  
**Author:** Development Team  
**Status:** Approved for Implementation
