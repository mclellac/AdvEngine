"""Defines the Attribute data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from .gobject_factory import create_gobject_wrapper


@dataclass
class Attribute:
    """Represents a character attribute or statistic.

    Attributes:
        id (str): The unique identifier for the attribute (e.g., "strength",
            "health").
        name (str): The display name of the attribute (e.g., "Strength").
        initial_value (int): The starting value of this attribute for a new
            character.
        max_value (int): The maximum possible value for this attribute.
    """

    id: str
    name: str
    initial_value: int
    max_value: int


AttributeGObject = create_gobject_wrapper(Attribute)
