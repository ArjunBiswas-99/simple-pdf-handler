import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../styles"

/**
 * Professional Top Bar Component
 * Command bar with title, search, and actions
 */
Rectangle {
    id: topBar
    
    property string title: "PDF Handler"
    property string subtitle: ""
    
    signal openFileClicked()
    signal saveClicked()
    signal searchClicked(string query)
    
    // Function to focus search field (called by Ctrl+F/Cmd+F)
    function focusSearchField() {
        searchField.forceActiveFocus()
        searchField.selectAll()
    }
    
    height: Theme.topBarHeight
    color: Colors.surface
    
    // Bottom border
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: Colors.divider
    }
    
    // Drop shadow effect
    layer.enabled: true
    layer.effect: ShaderEffect {
        property color shadowColor: Colors.shadowLight
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacing6
        anchors.rightMargin: Theme.spacing6
        spacing: Theme.spacing4
        
        // Title Section
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                text: topBar.title
                font.pixelSize: Typography.titleLargeSize
                font.weight: Typography.titleLargeWeight
                font.family: Typography.fontFamily
                color: Colors.textPrimary
            }
            
            Text {
                text: topBar.subtitle
                font.pixelSize: Typography.bodySmallSize
                font.family: Typography.fontFamily
                color: Colors.textSecondary
                visible: topBar.subtitle !== ""
            }
        }
        
        // Search Bar with Results
        Rectangle {
            Layout.preferredWidth: 400
            Layout.preferredHeight: 40
            radius: Theme.radiusLarge
            color: Colors.surfaceVariant
            border.color: searchField.activeFocus ? Colors.primary : "transparent"
            border.width: 2
            
            Behavior on border.color {
                ColorAnimation { duration: Theme.durationFast }
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacing3
                anchors.rightMargin: Theme.spacing3
                spacing: Theme.spacing2
                
                // Search Icon
                Text {
                    text: "🔍"
                    font.pixelSize: Theme.iconMedium
                    color: Colors.textSecondary
                }
                
                // Search Input
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search in document..."
                    font.pixelSize: Typography.bodyMediumSize
                    font.family: Typography.fontFamily
                    color: Colors.textPrimary
                    
                    background: Rectangle {
                        color: "transparent"
                    }
                    
                    // Debounced search
                    property var searchTimer: Timer {
                        interval: 500
                        onTriggered: {
                            if (searchField.text.length > 0) {
                                viewingController.search_in_pdf(searchField.text, false, false)
                            } else {
                                viewingController.clear_search()
                            }
                        }
                    }
                    
                    onTextChanged: {
                        console.log("Search text changed:", text)
                        if (text.length > 0) {
                            searchTimer.restart()
                        } else {
                            searchTimer.stop()
                            viewingController.clear_search()
                        }
                    }
                    
                    onAccepted: {
                        console.log("Search accepted:", text)
                        searchTimer.stop()
                        if (text.length > 0) {
                            console.log("Calling search_in_pdf with:", text)
                            viewingController.search_in_pdf(text, false, false)
                        }
                    }
                }
                
                // Match Counter
                Text {
                    text: viewingController.search_match_count > 0 ? 
                          (viewingController.current_match_index + " of " + viewingController.search_match_count) : ""
                    font.pixelSize: Typography.bodySmallSize
                    font.family: Typography.fontFamily
                    color: Colors.textSecondary
                    visible: viewingController.search_match_count > 0
                }
                
                // Previous Match Button
                IconButton {
                    iconSource: "⬆️"
                    text: "Previous match"
                    implicitWidth: 30
                    implicitHeight: 30
                    visible: viewingController.search_match_count > 0
                    onClicked: viewingController.previous_search_match()
                }
                
                // Next Match Button
                IconButton {
                    iconSource: "⬇️"
                    text: "Next match"
                    implicitWidth: 30
                    implicitHeight: 30
                    visible: viewingController.search_match_count > 0
                    onClicked: viewingController.next_search_match()
                }
                
                // Clear Search Button
                IconButton {
                    iconSource: "✖️"
                    text: "Clear search"
                    implicitWidth: 30
                    implicitHeight: 30
                    visible: searchField.text.length > 0
                    onClicked: {
                        searchField.text = ""
                        viewingController.clear_search()
                    }
                }
            }
        }
        
        // Action Buttons
        RowLayout {
            spacing: Theme.spacing2
            
            // Open File Button
            IconButton {
                iconSource: "📂"
                text: "Open File"
                onClicked: topBar.openFileClicked()
            }
            
            // Save Button
            PrimaryButton {
                text: "Save"
                iconSource: "💾"
                onClicked: topBar.saveClicked()
                implicitWidth: 100
            }
            
            // Divider
            Rectangle {
                Layout.preferredWidth: 1
                Layout.preferredHeight: 32
                color: Colors.divider
            }
            
            // More Options
            IconButton {
                iconSource: "⋮"
                text: "More options"
            }
        }
    }
}
