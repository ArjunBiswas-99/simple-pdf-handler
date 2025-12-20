/*
Simple PDF Handler - Status Bar Component

Displays application status, page info, and theme toggle.

Copyright (C) 2024
Licensed under GNU General Public License v3.0
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../styles"

Rectangle {
    id: statusBar
    
    height: Theme.statusBarHeight
    color: Theme.surface
    
    // Properties for displaying status
    property string statusText: "Ready"
    property int currentPage: 1
    property int totalPages: 0
    property int zoomLevel: 100
    
    // Border at top
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: Theme.border
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingMedium
        anchors.rightMargin: Theme.spacingMedium
        spacing: Theme.spacingLarge
        
        // Page information
        Text {
            text: totalPages > 0 ? "Page " + currentPage + " / " + totalPages : "No document"
            font.family: Typography.primaryFont
            font.pixelSize: Typography.smallSize
            color: Theme.textPrimary
        }
        
        // Separator
        Rectangle {
            width: 1
            height: parent.height * 0.6
            color: Theme.border
        }
        
        // Zoom level
        Text {
            text: "Zoom: " + zoomLevel + "%"
            font.family: Typography.primaryFont
            font.pixelSize: Typography.smallSize
            color: Theme.textPrimary
        }
        
        // Separator
        Rectangle {
            width: 1
            height: parent.height * 0.6
            color: Theme.border
        }
        
        // Status message
        Text {
            Layout.fillWidth: true
            text: statusText
            font.family: Typography.primaryFont
            font.pixelSize: Typography.smallSize
            color: Theme.textSecondary
            elide: Text.ElideRight
        }
        
        // Theme toggle button
        Button {
            id: themeToggle
            text: Theme.isDarkMode ? "☀" : "🌙"
            flat: true
            implicitWidth: Theme.buttonHeight
            implicitHeight: Theme.buttonHeight - 4
            
            ToolTip.visible: hovered
            ToolTip.text: Theme.isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"
            ToolTip.delay: 500
            
            contentItem: Text {
                text: parent.text
                font.pixelSize: Typography.subtitleSize
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            background: Rectangle {
                radius: Theme.radiusSmall
                color: parent.hovered ? Theme.hover : "transparent"
                
                Behavior on color {
                    ColorAnimation { duration: Theme.animationFast }
                }
            }
            
            onClicked: {
                themeManager.toggle_theme()
            }
            
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                acceptedButtons: Qt.NoButton
            }
        }
    }
}
