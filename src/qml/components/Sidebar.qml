import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../styles"

/**
 * Professional Sidebar Navigation
 * Collapsible sidebar with navigation items
 */
Rectangle {
    id: sidebar
    
    property bool expanded: true
    property string activeItem: "view"
    
    signal itemClicked(string itemId)
    
    width: expanded ? Theme.sidebarWidthExpanded : Theme.sidebarWidthCollapsed
    color: Colors.sidebarBackground
    
    // Smooth width animation
    Behavior on width {
        NumberAnimation { 
            duration: Theme.durationNormal
            easing.type: Theme.easingEmphasized 
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
        
        // Header with logo/title and collapse button
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.topBarHeight
            color: "transparent"
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacing4
                anchors.rightMargin: Theme.spacing4
                spacing: Theme.spacing3
                
                // App Logo/Icon
                Text {
                    text: "📄"
                    font.pixelSize: Theme.iconXLarge
                    visible: sidebar.expanded
                    color: Colors.sidebarText
                }
                
                // App Title
                Text {
                    text: "PDF Handler"
                    font.pixelSize: Typography.titleMediumSize
                    font.weight: Typography.titleMediumWeight
                    font.family: Typography.fontFamily
                    color: Colors.sidebarText
                    visible: sidebar.expanded
                    Layout.fillWidth: true
                }
                
                // Collapse/Expand Toggle
                IconButton {
                    iconSource: sidebar.expanded ? "«" : "»"
                    iconSize: Theme.iconMedium
                    text: sidebar.expanded ? "Collapse" : "Expand"
                    onClicked: sidebar.expanded = !sidebar.expanded
                    
                    contentItem: Text {
                        text: parent.iconSource
                        font.pixelSize: parent.iconSize
                        color: Colors.sidebarText
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    background: Rectangle {
                        color: parent.hovered ? Colors.sidebarHover : "transparent"
                        radius: Theme.radiusMedium
                        
                        Behavior on color {
                            ColorAnimation { duration: Theme.durationFast }
                        }
                    }
                }
            }
        }
        
        // Divider
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            Layout.leftMargin: Theme.spacing4
            Layout.rightMargin: Theme.spacing4
            color: Colors.sidebarTextSecondary
            opacity: 0.2
        }
        
        // Navigation Items
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            
            ColumnLayout {
                width: parent.width
                spacing: Theme.spacing1
                
                // View Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "👁"
                    labelText: "View PDF"
                    itemId: "view"
                    isActive: sidebar.activeItem === "view"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "view"
                        sidebar.itemClicked("view")
                    }
                }
                
                // Edit Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "✏️"
                    labelText: "Edit PDF"
                    itemId: "edit"
                    isActive: sidebar.activeItem === "edit"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "edit"
                        sidebar.itemClicked("edit")
                    }
                }
                
                // Annotate Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "💬"
                    labelText: "Annotate"
                    itemId: "annotate"
                    isActive: sidebar.activeItem === "annotate"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "annotate"
                        sidebar.itemClicked("annotate")
                    }
                }
                
                // Pages Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "📑"
                    labelText: "Pages"
                    itemId: "pages"
                    isActive: sidebar.activeItem === "pages"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "pages"
                        sidebar.itemClicked("pages")
                    }
                }
                
                // Merge Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "🔗"
                    labelText: "Merge PDFs"
                    itemId: "merge"
                    isActive: sidebar.activeItem === "merge"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "merge"
                        sidebar.itemClicked("merge")
                    }
                }
                
                // Convert Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "🔄"
                    labelText: "Convert"
                    itemId: "convert"
                    isActive: sidebar.activeItem === "convert"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "convert"
                        sidebar.itemClicked("convert")
                    }
                }
                
                // OCR Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "🔍"
                    labelText: "OCR"
                    itemId: "ocr"
                    isActive: sidebar.activeItem === "ocr"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "ocr"
                        sidebar.itemClicked("ocr")
                    }
                }
                
                // Files Section
                SidebarItem {
                    Layout.fillWidth: true
                    iconText: "📁"
                    labelText: "Files"
                    itemId: "files"
                    isActive: sidebar.activeItem === "files"
                    isExpanded: sidebar.expanded
                    onClicked: {
                        sidebar.activeItem = "files"
                        sidebar.itemClicked("files")
                    }
                }
                
                Item { Layout.fillHeight: true }
            }
        }
        
        // Bottom section - Settings
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.topBarHeight
            color: "transparent"
            
            SidebarItem {
                anchors.fill: parent
                iconText: "⚙️"
                labelText: "Settings"
                itemId: "settings"
                isActive: sidebar.activeItem === "settings"
                isExpanded: sidebar.expanded
                onClicked: {
                    sidebar.activeItem = "settings"
                    sidebar.itemClicked("settings")
                }
            }
        }
    }
    
    // Right border
    Rectangle {
        anchors.right: parent.right
        width: 1
        height: parent.height
        color: Colors.divider
    }
}
