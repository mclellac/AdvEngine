"""Defines utility GObject wrappers."""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject

class StringGObject(GObject.Object):
    """A GObject wrapper for a simple Python string."""
    __gtype_name__ = 'StringGObject'
    value = GObject.Property(type=str)

    def __init__(self, value):
        super().__init__()
        self.value = value
