import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../styles"

/**
 * Professional Sidebar Navigation Item
 * Individual navigation item with icon and label
 */
Button {
    id: control
    
    property string iconText: "○"
    property string labelText: "Item"
    property string itemId: ""
    property bool isActive: false
    property bool isExpanded: true
    
    implicitHeight: 48
    
    padding: 0
    
    contentItem: RowLayout {
        spacing: Theme.spacing3
        
        Item { width: Theme.spacing4 }  // Left padding
        
        // Icon
        Text {
            text: control.iconText
            font.pixelSize: Theme.iconLarge
            color: control.isActive ? Colors.sidebarActive : Colors.sidebarText
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: Theme.iconLarge
            horizontalAlignment: Text.AlignHCenter
            
            Behavior on color {
                ColorAnimation { duration: Theme.durationFast }
            }
        }
        
        // Label (only when expanded)
        Text {
            text: control.labelText
            font.pixelSize: Typography.bodyMediumSize
            font.weight: control.isActive ? Font.Medium : Font.Normal
            font.family: Typography.fontFamily
            color: control.isActive ? Colors.sidebarActive : Colors.sidebarText
            visible: control.isExpanded
            opacity: control.isExpanded ? 1.0 : 0.0
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            elide: Text.ElideRight
            
            Behavior on color {
                ColorAnimation { duration: Theme.durationFast }
            }
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.durationFast }
            }
        }
        
        Item { width: Theme.spacing4 }  // Right padding
    }
    
    background: Rectangle {
        color: {
            if (control.isActive) return Colors.sidebarHover
            if (control.hovered) return Colors.sidebarHover
            return "transparent"
        }
        radius: Theme.radiusMedium
        
        // Active indicator (left border)
        Rectangle {
            visible: control.isActive
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            width: 3
            height: parent.height * 0.6
            radius: 2
            color: Colors.sidebarActive
        }
        
        // Smooth transition
        Behavior on color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
        }
    }
    
    // Hover cursor
    hoverEnabled: true
}
