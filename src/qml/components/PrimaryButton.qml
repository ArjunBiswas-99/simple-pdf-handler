import QtQuick 6.0
import QtQuick.Controls 6.0
import "../styles"

/**
 * Professional Primary Button Component
 * Material Design 3 inspired filled button
 */
Button {
    id: control
    
    property string iconSource: ""
    property int iconSize: Theme.iconMedium
    
    implicitWidth: Math.max(120, contentItem.implicitWidth + leftPadding + rightPadding)
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
            font.family: "SF Symbols"  // macOS icon font
            color: control.enabled ? Colors.textOnPrimary : Colors.textOnPrimary
            opacity: control.enabled ? 1.0 : Theme.opacityDisabled
            anchors.verticalCenter: parent.verticalCenter
        }
        
        // Button Text
        Text {
            text: control.text
            font: control.font
            color: control.enabled ? Colors.textOnPrimary : Colors.textOnPrimary
            opacity: control.enabled ? 1.0 : Theme.opacityDisabled
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    
    background: Rectangle {
        color: {
            if (!control.enabled) return Colors.secondaryContainer
            if (control.pressed) return Colors.primaryDark
            if (control.hovered) return Colors.primaryLight
            return Colors.primary
        }
        radius: Theme.radiusMedium
        
        // Elevation shadow
        layer.enabled: control.enabled && !control.pressed
        layer.effect: ShaderEffect {
            property color shadowColor: Colors.shadow
        }
        
        // Drop shadow using border for simple effect
        Rectangle {
            anchors.fill: parent
            anchors.margins: -2
            color: "transparent"
            border.color: control.enabled && control.hovered ? Colors.shadowLight : "transparent"
            border.width: 2
            radius: parent.radius + 2
            z: -1
        }
        
        // Smooth transition
        Behavior on color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
        }
    }
    
    // Hover cursor
    hoverEnabled: true
}
