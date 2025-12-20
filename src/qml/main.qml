import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import QtQuick.Dialogs
import "styles"
import "components"

/**
 * Simple PDF Handler - Professional Main Window
 * CEO-Ready Demo UI
 */
ApplicationWindow {
    id: mainWindow
    
    visible: true
    width: 1400
    height: 900
    minimumWidth: 1200
    minimumHeight: 700
    title: "PDF Handler Pro"
    
    color: Colors.background
    
    // Keyboard Shortcuts
    Shortcut {
        sequence: StandardKey.Find  // Ctrl+F on Windows/Linux, Cmd+F on Mac
        onActivated: {
            topBar.focusSearchField()
        }
    }
    
    // File Dialog for opening PDFs
    FileDialog {
        id: openFileDialog
        title: "Open PDF File"
        nameFilters: ["PDF files (*.pdf)", "All files (*)"]
        currentFolder: "file://" + viewingController.get_last_directory()
        
        onAccepted: {
            console.log("Selected file:", selectedFile)
            viewingController.load_pdf_file(selectedFile.toString())
        }
    }
    
    // Remove default window decorations for modern look (optional)
    flags: Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
           Qt.WindowCloseButtonHint
    
    // Listen to viewing controller events
    Connections {
        target: viewingController
        
        function onDocument_opened(filename) {
            topBar.subtitle = filename + " - Page 1 of " + viewingController.page_count
        }
        
        function onPage_changed(current, total) {
            topBar.subtitle = viewingController.filename + " - Page " + current + " of " + total
        }
        
        function onZoom_changed(zoom) {
            statusBarZoomText.text = "Zoom: " + zoom + "%"
        }
    }
    
    // Main Layout
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // Left Sidebar Navigation
        Sidebar {
            id: sidebar
            Layout.fillHeight: true
            
            onItemClicked: function(itemId) {
                console.log("Navigation item clicked:", itemId)
                contentArea.currentView = itemId
                updateTopBarTitle(itemId)
            }
        }
        
        // Main Content Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Colors.background
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                
                // Top Command Bar
                TopBar {
                    id: topBar
                    Layout.fillWidth: true
                    
                    title: "View PDF"
                    subtitle: "No document loaded"
                    
                    onOpenFileClicked: {
                        console.log("Open file clicked")
                        openFileDialog.open()
                    }
                    
                    onSaveClicked: {
                        console.log("Save clicked")
                        fileOperationsController.save_file()
                    }
                    
                    onSearchClicked: function(query) {
                        console.log("Search:", query)
                    }
                }
                
                // Content Stack View
                Rectangle {
                    id: contentArea
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Colors.background
                    
                    property string currentView: "view"
                    
                    // View PDF Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "view"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        // Drop shadow
                        layer.enabled: true
                        layer.effect: ShaderEffect {
                            property color shadowColor: Colors.shadow
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacing6
                            spacing: Theme.spacing4
                            
                            // Toolbar
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Theme.spacing3
                                
                                Text {
                                    text: "PDF Viewer"
                                    font.pixelSize: Typography.titleMediumSize
                                    font.weight: Typography.titleMediumWeight
                                    color: Colors.textPrimary
                                    Layout.fillWidth: true
                                }
                                
                                SecondaryButton {
                                    text: "Zoom In"
                                    iconSource: "+"
                                    onClicked: viewingController.zoom_in()
                                }
                                
                                SecondaryButton {
                                    text: "Zoom Out"
                                    iconSource: "-"
                                    onClicked: viewingController.zoom_out()
                                }
                                
                                SecondaryButton {
                                    text: "Rotate"
                                    iconSource: "↻"
                                    onClicked: viewingController.rotate()
                                }
                                
                                // Divider
                                Rectangle {
                                    Layout.preferredWidth: 1
                                    Layout.preferredHeight: 32
                                    color: Colors.divider
                                }
                                
                                // View Mode Toggle Buttons
                                Text {
                                    text: "View:"
                                    font.pixelSize: Typography.bodySmallSize
                                    color: Colors.textSecondary
                                    Layout.alignment: Qt.AlignVCenter
                                }
                                
                                SecondaryButton {
                                    text: "Single"
                                    iconSource: "📄"
                                    onClicked: viewingController.set_view_mode("single")
                                    // Highlight if active
                                    opacity: viewingController.view_mode === "single" ? 1.0 : 0.6
                                }
                                
                                SecondaryButton {
                                    text: "Two Page"
                                    iconSource: "📄📄"
                                    onClicked: viewingController.set_view_mode("two_page")
                                    opacity: viewingController.view_mode === "two_page" ? 1.0 : 0.6
                                }
                                
                                SecondaryButton {
                                    text: "Scroll"
                                    iconSource: "📜"
                                    onClicked: viewingController.set_view_mode("scroll")
                                    opacity: viewingController.view_mode === "scroll" ? 1.0 : 0.6
                                }
                            }
                            
                            // PDF Viewer Area
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Colors.surfaceVariant
                                radius: Theme.radiusMedium
                                border.color: Colors.border
                                border.width: 1
                                
                                // Show PDF viewer if document loaded, otherwise show empty state
                                PDFViewer {
                                    anchors.fill: parent
                                    anchors.margins: Theme.spacing2
                                    visible: viewingController.document_loaded
                                }
                                
                                // Empty state
                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: Theme.spacing4
                                    visible: !viewingController.document_loaded
                                    
                                    Text {
                                        text: "📄"
                                        font.pixelSize: 72
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    
                                    Text {
                                        text: "PDF Viewer Area"
                                        font.pixelSize: Typography.headlineSmallSize
                                        font.weight: Font.Medium
                                        color: Colors.textPrimary
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    
                                    Text {
                                        text: "Open a PDF file to view it here"
                                        font.pixelSize: Typography.bodyMediumSize
                                        color: Colors.textSecondary
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    
                                    PrimaryButton {
                                        text: "Open PDF"
                                        iconSource: "📂"
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.topMargin: Theme.spacing4
                                        onClicked: {
                                            openFileDialog.open()
                                        }
                                    }
                                }
                            }
                            
                            // Page Navigation
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignHCenter
                                spacing: Theme.spacing3
                                visible: viewingController.document_loaded
                                
                                IconButton {
                                    iconSource: "⟨"
                                    text: "Previous Page"
                                    enabled: viewingController.current_page > 1
                                    onClicked: viewingController.previous_page()
                                }
                                
                                Text {
                                    text: "Page " + viewingController.current_page + " of " + viewingController.page_count
                                    font.pixelSize: Typography.bodyMediumSize
                                    color: Colors.textSecondary
                                }
                                
                                IconButton {
                                    iconSource: "⟩"
                                    text: "Next Page"
                                    enabled: viewingController.current_page < viewingController.page_count
                                    onClicked: viewingController.next_page()
                                }
                            }
                        }
                    }
                    
                    // Edit Content (Placeholder for other views)
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "edit"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "✏️ Edit PDF View\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Annotate Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "annotate"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "💬 Annotate View\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Pages Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "pages"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "📑 Page Management\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Merge Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "merge"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "🔗 Merge PDFs\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Convert Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "convert"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "🔄 Convert PDFs\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // OCR Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "ocr"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "🔍 OCR (Text Recognition)\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Files Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "files"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "📁 File Operations\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Settings Content
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing6
                        visible: contentArea.currentView === "settings"
                        color: Colors.surface
                        radius: Theme.radiusLarge
                        
                        Text {
                            anchors.centerIn: parent
                            text: "⚙️ Settings\n(Coming Soon)"
                            font.pixelSize: Typography.headlineSmallSize
                            color: Colors.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
                
                // Professional Status Bar
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Theme.statusBarHeight
                    color: Colors.surface
                    
                    // Top border
                    Rectangle {
                        anchors.top: parent.top
                        width: parent.width
                        height: 1
                        color: Colors.divider
                    }
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacing6
                        anchors.rightMargin: Theme.spacing6
                        spacing: Theme.spacing4
                        
                        Text {
                            text: "Ready"
                            font.pixelSize: Typography.bodySmallSize
                            color: Colors.textSecondary
                            Layout.fillWidth: true
                        }
                        
                        Text {
                            id: statusBarZoomText
                            text: "Zoom: 100%"
                            font.pixelSize: Typography.bodySmallSize
                            color: Colors.textSecondary
                        }
                        
                        Rectangle {
                            Layout.preferredWidth: 1
                            Layout.preferredHeight: 16
                            color: Colors.divider
                        }
                        
                        Text {
                            text: "v1.0.0"
                            font.pixelSize: Typography.bodySmallSize
                            color: Colors.textTertiary
                        }
                    }
                }
            }
        }
    }
    
    // Helper function to update top bar title
    function updateTopBarTitle(itemId) {
        var titles = {
            "view": "View PDF",
            "edit": "Edit PDF",
            "annotate": "Annotate PDF",
            "pages": "Page Management",
            "merge": "Merge PDFs",
            "convert": "Convert PDF",
            "ocr": "OCR - Text Recognition",
            "files": "File Operations",
            "settings": "Settings"
        }
        topBar.title = titles[itemId] || "PDF Handler"
    }
}
