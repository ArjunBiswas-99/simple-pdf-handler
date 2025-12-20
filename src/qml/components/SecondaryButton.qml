import QtQuick 6.0
import QtQuick.Controls 6.0
import "../styles"

/**
 * Professional Secondary Button Component
 * Outlined button variant
 */
Button {
    id: control
    
    property string iconSource: ""
    property int iconSize: Theme.iconMedium
    
    implicitWidth: Math.max(100, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: Theme.buttonHeightMedium
    
    leftPadding: iconSource ? Theme.spacing4 : Theme.spacing6
    rightPadding: Theme.spacing6
    topPadding: Theme.spacing3
    bottomPadding: Theme.spacing3
    
    font.pixelSize: Typography.labelLargeSize
    font.weight: Typography.labelLargeWeight
    font.family: Typography.fontFamily
    font.letterSpacing: Typography.labelLargeLetterSpacing
    
    contentItem: Row {
        spacing: Theme.spacing2
        
        // Icon (if provided)
        Text {
            visible: control.iconSource !== ""
            text: control.iconSource
            font.pixelSize: control.iconSize
            font.family: "SF Symbols"
            color: control.enabled ? Colors.primary : Colors.textSecondary
            opacity: control.enabled ? 1.0 : Theme.opacityDisabled
            anchors.verticalCenter: parent.verticalCenter
        }
        
        // Button Text
        Text {
            text: control.text
            font: control.font
            color: control.enabled ? Colors.primary : Colors.textSecondary
            opacity: control.enabled ? 1.0 : Theme.opacityDisabled
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    
    background: Rectangle {
        color: {
            if (control.pressed) return Colors.primaryContainer
            if (control.hovered) return Colors.surfaceContainer
            return "transparent"
        }
        radius: Theme.radiusMedium
        border.color: control.enabled ? Colors.border : Colors.borderLight
        border.width: Theme.borderThin
        
        // Smooth transition
        Behavior on color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
        }
        Behavior on border.color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
        }
    }
    
    // Hover cursor
    hoverEnabled: true
}
