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
        
        // Search Bar
        Rectangle {
            Layout.preferredWidth: 300
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
                    
                    onAccepted: topBar.searchClicked(text)
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
