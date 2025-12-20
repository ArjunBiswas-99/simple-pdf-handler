import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../styles"

/**
 * PDF Viewer Component
 * Professional multi-view PDF display with Single, Two Page, and Continuous Scroll modes
 */
Item {
    id: pdfViewer
    
    property int pageCounter: 0
    property bool updatingFromScroll: false  // Flag to prevent circular updates
    
    // Timer to debounce scroll updates
    Timer {
        id: scrollUpdateTimer
        interval: 300  // 300ms debounce
        onTriggered: {
            if (viewingController.view_mode === "scroll") {
                updateCurrentPageFromScroll()
            }
        }
    }
    
    // Update controller's current page based on scroll position
    function updateCurrentPageFromScroll() {
        if (!viewingController.document_loaded || updatingFromScroll) {
            return
        }
        
        var viewportTop = scrollListView.contentY
        var viewportCenter = viewportTop + scrollListView.height / 2
        
        // Find which page is at the center of viewport
        for (var i = 0; i < scrollListView.count; i++) {
            var item = scrollListView.itemAtIndex(i)
            if (item) {
                var itemTop = item.y
                var itemBottom = item.y + item.height
                
                // Check if viewport center is within this item
                if (viewportCenter >= itemTop && viewportCenter < itemBottom) {
                    var newPage = i + 1  // Convert to 1-indexed
                    if (newPage !== viewingController.current_page) {
                        updatingFromScroll = true
                        viewingController.goto_page(newPage)
                        updatingFromScroll = false
                    }
                    break
                }
            }
        }
    }
    
    // Listen to page rendered signal
    Connections {
        target: viewingController
        
        function onPage_rendered(pageNum) {
            // Force refresh of images that were waiting for this page
            pageCounter++
        }
        
        // Handle view mode changes - maintain page position
        function onView_mode_changed() {
            if (viewingController.view_mode === "scroll") {
                // When switching to scroll mode, scroll to current page
                updatingFromScroll = true
                scrollListView.positionViewAtIndex(
                    viewingController.current_page - 1,  // 0-indexed
                    ListView.Beginning
                )
                updatingFromScroll = false
            }
        }
        
        // Handle page navigation in scroll mode
        function onPage_changed(currentPage, totalPages) {
            if (viewingController.view_mode === "scroll" && !updatingFromScroll) {
                // Only scroll if this wasn't triggered by scroll
                scrollListView.positionViewAtIndex(
                    currentPage - 1,  // Convert to 0-indexed
                    ListView.Beginning
                )
            }
        }
    }
    
    // ===== SINGLE PAGE VIEW =====
    ScrollView {
        anchors.fill: parent
        clip: true
        visible: viewingController.view_mode === "single"
        
        contentWidth: singlePageImage.width
        contentHeight: singlePageImage.height
        
        Image {
            id: singlePageImage
            source: viewingController.document_loaded ? 
                    ("image://pdfimage/page_" + viewingController.current_page + "?counter=" + pageCounter) : ""
            cache: false
            asynchronous: true
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent.width < width || parent.height < height ? undefined : parent
            
            BusyIndicator {
                anchors.centerIn: parent
                running: singlePageImage.status === Image.Loading
                visible: running
            }
        }
    }
    
    // ===== TWO PAGE VIEW =====
    ScrollView {
        anchors.fill: parent
        clip: true
        visible: viewingController.view_mode === "two_page"
        
        contentWidth: twoPageRow.width
        contentHeight: twoPageRow.height
        
        Row {
            id: twoPageRow
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter
            
            // Left Page (current page)
            Rectangle {
                width: leftPageImage.width > 0 ? leftPageImage.width : 596
                height: leftPageImage.height > 0 ? leftPageImage.height : 842
                color: Colors.surfaceVariant
                border.color: Colors.border
                border.width: 1
                
                Image {
                    id: leftPageImage
                    anchors.fill: parent
                    source: viewingController.document_loaded ? 
                            ("image://pdfimage/page_" + viewingController.current_page + "?counter=" + pageCounter) : ""
                    cache: false
                    asynchronous: true
                    fillMode: Image.PreserveAspectFit
                    
                    BusyIndicator {
                        anchors.centerIn: parent
                        running: leftPageImage.status === Image.Loading
                        visible: running
                    }
                }
            }
            
            // Right Page (next page)
            Rectangle {
                width: rightPageImage.width > 0 ? rightPageImage.width : 596
                height: rightPageImage.height > 0 ? rightPageImage.height : 842
                color: Colors.surfaceVariant
                border.color: Colors.border
                border.width: 1
                visible: viewingController.current_page < viewingController.page_count
                
                Image {
                    id: rightPageImage
                    anchors.fill: parent
                    source: viewingController.document_loaded && 
                            viewingController.current_page < viewingController.page_count ? 
                            ("image://pdfimage/page_" + (viewingController.current_page + 1) + "?counter=" + pageCounter) : ""
                    cache: false
                    asynchronous: true
                    fillMode: Image.PreserveAspectFit
                    
                    BusyIndicator {
                        anchors.centerIn: parent
                        running: rightPageImage.status === Image.Loading
                        visible: running
                    }
                }
                
                // Show page number overlay on right page
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 10
                    width: pageNumText.width + 10
                    height: pageNumText.height + 10
                    color: Colors.surface
                    opacity: 0.8
                    radius: 4
                    
                    Text {
                        id: pageNumText
                        anchors.centerIn: parent
                        text: "Page " + (viewingController.current_page + 1)
                        font.pixelSize: Typography.bodySmallSize
                        color: Colors.textSecondary
                    }
                }
            }
        }
    }
    
    // ===== CONTINUOUS SCROLL VIEW (ListView with lazy loading) =====
    ListView {
        id: scrollListView
        anchors.fill: parent
        clip: true
        visible: viewingController.view_mode === "scroll"
        
        model: viewingController.document_loaded ? viewingController.page_count : 0
        spacing: 20
        
        // Enable caching for better performance
        cacheBuffer: 2000  // Cache 2000px above and below viewport
        
        ScrollBar.vertical: ScrollBar { }
        
        delegate: Item {
            id: pageDelegate
            required property int index
            width: scrollListView.width - 40
            height: 900
            x: 20  // Center with margins
            
            // Only render when page becomes visible or near visible
            property bool shouldRender: false
            
            // Check if this item is in or near viewport
            onYChanged: checkVisibility()
            Component.onCompleted: checkVisibility()
            
            function checkVisibility() {
                var viewportTop = scrollListView.contentY
                var viewportBottom = viewportTop + scrollListView.height
                var itemTop = y
                var itemBottom = y + height
                var buffer = 1500  // Start rendering 1500px before entering viewport
                
                // Item is visible or will be soon
                if (itemBottom + buffer > viewportTop && itemTop - buffer < viewportBottom) {
                    if (!shouldRender) {
                        shouldRender = true
                        // Request render for this page
                        viewingController.render_specific_page(index + 1)
                    }
                }
            }
            
            Rectangle {
                anchors.fill: parent
                color: Colors.surfaceVariant
                border.color: Colors.border
                border.width: 1
                
                // Page number overlay
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: 10
                    width: scrollPageNum.width + 16
                    height: scrollPageNum.height + 16
                    color: Colors.surface
                    opacity: 0.9
                    radius: 6
                    z: 1
                    
                    Text {
                        id: scrollPageNum
                        anchors.centerIn: parent
                        text: "Page " + (index + 1)
                        font.pixelSize: Typography.bodyMediumSize
                        color: Colors.textPrimary
                    }
                }
                
                Image {
                    id: scrollPageImage
                    anchors.fill: parent
                    anchors.margins: 2
                    source: pageDelegate.shouldRender ? 
                            ("image://pdfimage/page_" + (index + 1) + "?counter=" + pageCounter) : ""
                    cache: false
                    asynchronous: true
                    fillMode: Image.PreserveAspectFit
                    
                    BusyIndicator {
                        anchors.centerIn: parent
                        running: scrollPageImage.status === Image.Loading
                        visible: running
                    }
                    
                    // Placeholder text while loading
                    Text {
                        anchors.centerIn: parent
                        text: scrollPageImage.status === Image.Loading ? "Loading..." : 
                              scrollPageImage.status === Image.Error ? "Error loading page" : 
                              !pageDelegate.shouldRender ? "Scroll to load..." : ""
                        font.pixelSize: Typography.bodyMediumSize
                        color: Colors.textSecondary
                        visible: scrollPageImage.status !== Image.Ready
                    }
                }
            }
        }
        
        // Track scroll position and request renders as user scrolls
        onContentYChanged: {
            // Trigger visibility check for all delegates
            for (var i = 0; i < count; i++) {
                var item = itemAtIndex(i)
                if (item) {
                    item.checkVisibility()
                }
            }
            
            // Update page counter based on scroll position (debounced)
            if (viewingController.view_mode === "scroll") {
                scrollUpdateTimer.restart()
            }
        }
    }
    
    // View mode indicator (top-right corner)
    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        width: 120
        height: 30
        radius: 15
        color: Colors.primary
        opacity: 0.8
        visible: viewingController.document_loaded
        
        Text {
            anchors.centerIn: parent
            text: {
                if (viewingController.view_mode === "single") return "📄 Single"
                if (viewingController.view_mode === "two_page") return "📄📄 Two Page"
                if (viewingController.view_mode === "scroll") return "📜 Scroll"
                return "View Mode"
            }
            font.pixelSize: Typography.bodySmallSize
            color: "white"
        }
    }
}
