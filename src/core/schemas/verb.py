"""Defines the Verb data schema and its GObject wrapper."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass
from .gobject_factory import create_gobject_wrapper

@dataclass
class Verb:
    """Represents a verb that the player can use."""
    id: str
    name: str

VerbGObject = create_gobject_wrapper(Verb)
