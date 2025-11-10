"""Defines the Verb data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from .gobject_factory import create_gobject_wrapper


@dataclass
class Verb:
    """Represents a verb that the player can use to interact with the world.

    Verbs are the foundation of the game's interaction system, forming the
    classic "Verb + Item" or "Verb + Hotspot" structure.

    Attributes:
        id (str): The unique identifier for the verb (e.g., "use", "look_at").
        name (str): The display name of the verb (e.g., "Use", "Look At").
    """

    id: str
    name: str


VerbGObject = create_gobject_wrapper(Verb)
