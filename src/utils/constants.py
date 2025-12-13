"""
Simple PDF Handler - Application Constants

Copyright (C) 2024 Arjun Biswas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

# Zoom level constants
# Maps display strings to zoom multipliers
ZOOM_LEVELS = {
    "50%": 0.5,
    "75%": 0.75,
    "100%": 1.0,
    "125%": 1.25,
    "150%": 1.5,
    "200%": 2.0,
}

# Ordered list of zoom level labels for dropdown
ZOOM_LEVEL_LABELS = ["50%", "75%", "100%", "125%", "150%", "200%"]

# Default zoom level on document load
DEFAULT_ZOOM = 1.0

# Minimum and maximum zoom limits
MIN_ZOOM = 0.25  # 25%
MAX_ZOOM = 4.0   # 400%

# Zoom increment for zoom in/out buttons
ZOOM_INCREMENT = 0.25  # 25% steps

# File size threshold for threaded operations (10MB)
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024

# Page count threshold for threaded zoom rendering
LARGE_DOCUMENT_PAGE_THRESHOLD = 10

# Search debounce delay in milliseconds
# Prevents starting search on every keystroke
SEARCH_DEBOUNCE_DELAY = 300
