"""Defines the data schema for search results."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass
from .gobject_factory import create_gobject_wrapper

@dataclass
class SearchResult:
    """Represents a single search result."""
    id: str
    name: str
    type: str

SearchResultGObject = create_gobject_wrapper(SearchResult)
