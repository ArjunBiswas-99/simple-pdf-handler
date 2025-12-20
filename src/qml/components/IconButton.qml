import QtQuick 6.0
import QtQuick.Controls 6.0
import "../styles"

/**
 * Professional Icon Button Component
 * Minimal button with icon only
 */
Button {
    id: control
    
    property string iconSource: "○"
    property int iconSize: Theme.iconLarge
    property bool showTooltip: true
    
    implicitWidth: Theme.buttonHeightMedium
    implicitHeight: Theme.buttonHeightMedium
    
    padding: Theme.spacing2
    
    contentItem: Text {
        text: control.iconSource
        font.pixelSize: control.iconSize
        font.family: "SF Symbols"
        color: control.enabled ? Colors.textPrimary : Colors.textSecondary
        opacity: control.enabled ? 1.0 : Theme.opacityDisabled
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    background: Rectangle {
        color: {
            if (control.pressed) return Colors.pressedOverlay
            if (control.hovered) return Colors.hoverOverlay
            return "transparent"
        }
        radius: Theme.radiusFull
        
        // Smooth transition
        Behavior on color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
        }
    }
    
    // Tooltip
    ToolTip.visible: showTooltip && hovered && text !== ""
    ToolTip.text: text
    ToolTip.delay: 500
    
    // Hover cursor
    hoverEnabled: true
}
