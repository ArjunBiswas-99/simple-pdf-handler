"""
Simple PDF Handler - Sidebar Panels Module

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

from .pages_panel import PagesPanel
from .bookmarks_panel import BookmarksPanel
from .search_panel import SearchPanel
from .attachments_panel import AttachmentsPanel

__all__ = ['PagesPanel', 'BookmarksPanel', 'SearchPanel', 'AttachmentsPanel']
