pragma Singleton
import QtQuick 6.0

/**
 * Professional Typography System
 * Material Design 3 type scale
 */
QtObject {
    // Display Styles (Large headings)
    readonly property int displayLargeSize: 57
    readonly property int displayLargeWeight: Font.Normal
    readonly property real displayLargeLetterSpacing: -0.25
    
    readonly property int displayMediumSize: 45
    readonly property int displayMediumWeight: Font.Normal
    readonly property real displayMediumLetterSpacing: 0
    
    readonly property int displaySmallSize: 36
    readonly property int displaySmallWeight: Font.Normal
    readonly property real displaySmallLetterSpacing: 0
    
    // Headline Styles
    readonly property int headlineLargeSize: 32
    readonly property int headlineLargeWeight: Font.Normal
    readonly property real headlineLargeLetterSpacing: 0
    
    readonly property int headlineMediumSize: 28
    readonly property int headlineMediumWeight: Font.Normal
    readonly property real headlineMediumLetterSpacing: 0
    
    readonly property int headlineSmallSize: 24
    readonly property int headlineSmallWeight: Font.Normal
    readonly property real headlineSmallLetterSpacing: 0
    
    // Title Styles
    readonly property int titleLargeSize: 22
    readonly property int titleLargeWeight: Font.Normal
    readonly property real titleLargeLetterSpacing: 0
    
    readonly property int titleMediumSize: 16
    readonly property int titleMediumWeight: Font.Medium
    readonly property real titleMediumLetterSpacing: 0.15
    
    readonly property int titleSmallSize: 14
    readonly property int titleSmallWeight: Font.Medium
    readonly property real titleSmallLetterSpacing: 0.1
    
    // Body Styles
    readonly property int bodyLargeSize: 16
    readonly property int bodyLargeWeight: Font.Normal
    readonly property real bodyLargeLetterSpacing: 0.5
    
    readonly property int bodyMediumSize: 14
    readonly property int bodyMediumWeight: Font.Normal
    readonly property real bodyMediumLetterSpacing: 0.25
    
    readonly property int bodySmallSize: 12
    readonly property int bodySmallWeight: Font.Normal
    readonly property real bodySmallLetterSpacing: 0.4
    
    // Label Styles
    readonly property int labelLargeSize: 14
    readonly property int labelLargeWeight: Font.Medium
    readonly property real labelLargeLetterSpacing: 0.1
    
    readonly property int labelMediumSize: 12
    readonly property int labelMediumWeight: Font.Medium
    readonly property real labelMediumLetterSpacing: 0.5
    
    readonly property int labelSmallSize: 11
    readonly property int labelSmallWeight: Font.Medium
    readonly property real labelSmallLetterSpacing: 0.5
    
    // Font Family
    readonly property string fontFamily: "SF Pro Display"    // macOS default
    readonly property string fontFamilyFallback: "Roboto"    // Fallback
    
    // Line Heights (as multipliers)
    readonly property real lineHeightTight: 1.2
    readonly property real lineHeightNormal: 1.5
    readonly property real lineHeightRelaxed: 1.75
}
