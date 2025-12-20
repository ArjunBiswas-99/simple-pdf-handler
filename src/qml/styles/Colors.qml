pragma Singleton
import QtQuick 6.0

/**
 * Professional Color System
 * Material Design 3 inspired palette
 */
QtObject {
    // Primary Brand Colors
    readonly property color primary: "#1976D2"           // Professional Blue
    readonly property color primaryLight: "#42A5F5"
    readonly property color primaryDark: "#0D47A1"
    readonly property color primaryContainer: "#E3F2FD"
    
    // Secondary Colors
    readonly property color secondary: "#424242"         // Neutral Gray
    readonly property color secondaryLight: "#757575"
    readonly property color secondaryDark: "#212121"
    readonly property color secondaryContainer: "#F5F5F5"
    
    // Accent Colors
    readonly property color accent: "#00BCD4"            // Cyan accent
    readonly property color accentLight: "#4DD0E1"
    readonly property color accentDark: "#0097A7"
    
    // Surface Colors
    readonly property color background: "#FAFAFA"        // Light gray background
    readonly property color surface: "#FFFFFF"           // White surface
    readonly property color surfaceVariant: "#F5F5F5"    // Subtle variant
    readonly property color surfaceContainer: "#EEEEEE"
    
    // Text Colors
    readonly property color textPrimary: "#212121"       // High emphasis
    readonly property color textSecondary: "#757575"     // Medium emphasis
    readonly property color textTertiary: "#9E9E9E"      // Low emphasis
    readonly property color textOnPrimary: "#FFFFFF"     // Text on primary color
    readonly property color textOnAccent: "#FFFFFF"
    
    // Semantic Colors
    readonly property color success: "#4CAF50"
    readonly property color successLight: "#81C784"
    readonly property color warning: "#FF9800"
    readonly property color warningLight: "#FFB74D"
    readonly property color error: "#F44336"
    readonly property color errorLight: "#E57373"
    readonly property color info: "#2196F3"
    readonly property color infoLight: "#64B5F6"
    
    // Border & Divider Colors
    readonly property color border: "#E0E0E0"
    readonly property color borderLight: "#F5F5F5"
    readonly property color divider: "#EEEEEE"
    
    // Shadow Colors
    readonly property color shadow: "#00000029"          // 16% opacity
    readonly property color shadowLight: "#00000014"     // 8% opacity
    readonly property color shadowDark: "#0000003D"      // 24% opacity
    
    // Hover & Active States
    readonly property color hoverOverlay: "#0000000A"    // 4% black overlay
    readonly property color pressedOverlay: "#00000014"  // 8% black overlay
    readonly property color selectedOverlay: "#1976D214" // 8% primary overlay
    
    // Sidebar Colors
    readonly property color sidebarBackground: "#263238" // Dark blue-gray
    readonly property color sidebarHover: "#37474F"
    readonly property color sidebarActive: "#42A5F5"
    readonly property color sidebarText: "#ECEFF1"
    readonly property color sidebarTextSecondary: "#B0BEC5"
    
    // Overlay & Modal
    readonly property color overlay: "#00000080"         // 50% opacity
    readonly property color modalBackground: "#FFFFFF"
    
    // Special Effects
    readonly property color glass: "#FFFFFFCC"           // 80% white for glass effect
    readonly property color glassBlur: "#FFFFFF99"       // 60% white
}
