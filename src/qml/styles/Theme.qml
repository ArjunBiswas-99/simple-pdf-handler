pragma Singleton
import QtQuick 6.0

/**
 * Professional Theme Configuration
 * Spacing, shadows, borders, and animation settings
 */
QtObject {
    // Spacing Scale (8px base)
    readonly property int spacing0: 0
    readonly property int spacing1: 4
    readonly property int spacing2: 8
    readonly property int spacing3: 12
    readonly property int spacing4: 16
    readonly property int spacing5: 20
    readonly property int spacing6: 24
    readonly property int spacing7: 28
    readonly property int spacing8: 32
    readonly property int spacing10: 40
    readonly property int spacing12: 48
    readonly property int spacing16: 64
    readonly property int spacing20: 80
    
    // Border Radius
    readonly property int radiusSmall: 4
    readonly property int radiusMedium: 8
    readonly property int radiusLarge: 12
    readonly property int radiusXLarge: 16
    readonly property int radiusFull: 9999
    
    // Border Width
    readonly property int borderThin: 1
    readonly property int borderMedium: 2
    readonly property int borderThick: 3
    
    // Elevation (shadow levels)
    readonly property var elevation0: {
        "offsetX": 0,
        "offsetY": 0,
        "radius": 0,
        "spread": 0
    }
    
    readonly property var elevation1: {
        "offsetX": 0,
        "offsetY": 1,
        "radius": 3,
        "spread": 0
    }
    
    readonly property var elevation2: {
        "offsetX": 0,
        "offsetY": 2,
        "radius": 6,
        "spread": 0
    }
    
    readonly property var elevation3: {
        "offsetX": 0,
        "offsetY": 4,
        "radius": 12,
        "spread": 0
    }
    
    readonly property var elevation4: {
        "offsetX": 0,
        "offsetY": 8,
        "radius": 24,
        "spread": 0
    }
    
    readonly property var elevation5: {
        "offsetX": 0,
        "offsetY": 16,
        "radius": 32,
        "spread": 0
    }
    
    // Animation Durations (ms)
    readonly property int durationInstant: 0
    readonly property int durationFast: 150
    readonly property int durationNormal: 250
    readonly property int durationSlow: 350
    readonly property int durationSlower: 500
    
    // Animation Easing
    readonly property int easingStandard: Easing.OutCubic
    readonly property int easingDecelerate: Easing.OutQuad
    readonly property int easingAccelerate: Easing.InQuad
    readonly property int easingEmphasized: Easing.InOutQuad
    
    // Layout Sizes
    readonly property int sidebarWidthExpanded: 240
    readonly property int sidebarWidthCollapsed: 64
    readonly property int topBarHeight: 64
    readonly property int statusBarHeight: 32
    readonly property int toolbarHeight: 56
    
    // Icon Sizes
    readonly property int iconSmall: 16
    readonly property int iconMedium: 20
    readonly property int iconLarge: 24
    readonly property int iconXLarge: 32
    readonly property int iconXXLarge: 48
    
    // Button Sizes
    readonly property int buttonHeightSmall: 32
    readonly property int buttonHeightMedium: 40
    readonly property int buttonHeightLarge: 48
    
    // Input Sizes
    readonly property int inputHeightSmall: 32
    readonly property int inputHeightMedium: 40
    readonly property int inputHeightLarge: 48
    
    // Z-Index Layers
    readonly property int zIndexBase: 0
    readonly property int zIndexDropdown: 1000
    readonly property int zIndexSticky: 1100
    readonly property int zIndexFixed: 1200
    readonly property int zIndexModal: 1300
    readonly property int zIndexPopover: 1400
    readonly property int zIndexTooltip: 1500
    
    // Opacity Levels
    readonly property real opacityDisabled: 0.38
    readonly property real opacitySecondary: 0.60
    readonly property real opacityHover: 0.04
    readonly property real opacityPressed: 0.12
    readonly property real opacitySelected: 0.08
}
