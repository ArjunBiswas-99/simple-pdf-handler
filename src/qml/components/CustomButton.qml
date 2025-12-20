/*
Simple PDF Handler - Custom Button Component

Reusable button with consistent styling and hover effects.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../styles"

Button {
    id: control
    
    // Custom properties
    property color backgroundColor: Theme.primary
    property color textColor: "#FFFFFF"
    property color hoverColor: Qt.lighter(backgroundColor, 1.1)
    property int radius: Theme.radiusMedium
    
    implicitWidth: Math.max(100, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: Theme.buttonHeight
    
    padding: Theme.spacingMedium
    
    contentItem: Text {
        text: control.text
        font.family: Typography.primaryFont
        font.pixelSize: Typography.bodySize
        font.weight: Typography.medium
        color: control.enabled ? textColor : Theme.textSecondary
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    
    background: Rectangle {
        id: buttonBackground
        radius: control.radius
        color: control.enabled ? 
            (control.down ? Qt.darker(backgroundColor, 1.1) : 
             control.hovered ? hoverColor : backgroundColor) : 
            Theme.surface
        border.color: control.enabled ? backgroundColor : Theme.border
        border.width: control.flat ? 0 : 1
        
        Behavior on color {
            ColorAnimation { duration: Theme.animationFast }
        }
    }
    
    // Cursor changes on hover
    MouseArea {
        anchors.fill: parent
        cursorShape: control.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        acceptedButtons: Qt.NoButton
    }
}
