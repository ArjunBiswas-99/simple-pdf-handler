import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../styles"

/**
 * PDF Viewer Component
 * Displays rendered PDF pages from image provider
 */
Item {
    id: pdfViewer
    
    property int refreshCounter: 0
    property bool imageReady: false
    
    // Listen to viewing controller signals
    Connections {
        target: viewingController
        
        function onPdf_image_updated() {
            // Mark image as ready and increment counter to force refresh
            pdfViewer.imageReady = true
            pdfViewer.refreshCounter++
        }
    }
    
    // Scrollable area for PDF
    ScrollView {
        anchors.fill: parent
        clip: true
        
        contentWidth: pdfImage.width
        contentHeight: pdfImage.height
        
        // PDF Image - only show when we have an actual image ready
        Image {
            id: pdfImage
            
            // Use image provider with counter to force refresh
            // Only set source when imageReady to avoid showing placeholder
            source: pdfViewer.imageReady ? ("image://pdfimage/page_" + pdfViewer.refreshCounter) : ""
            
            cache: false
            asynchronous: true
            fillMode: Image.PreserveAspectFit
            visible: pdfViewer.imageReady
            
            // Center in scroll view if smaller than viewport
            anchors.centerIn: parent.width < width || parent.height < height ? undefined : parent
            
            onStatusChanged: {
                if (status === Image.Error) {
                    console.log("Error loading PDF image")
                } else if (status === Image.Ready) {
                    console.log("PDF image loaded:", width, "x", height)
                }
            }
            
            // Loading indicator
            BusyIndicator {
                anchors.centerIn: parent
                running: pdfImage.status === Image.Loading
                visible: running
            }
        }
    }
}
