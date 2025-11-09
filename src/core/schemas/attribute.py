"""Defines the Attribute data schema and its GObject wrapper."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass
from .gobject_factory import create_gobject_wrapper

@dataclass
class Attribute:
    """Represents a character attribute."""
    id: str
    name: str
    initial_value: int
    max_value: int

AttributeGObject = create_gobject_wrapper(Attribute)
