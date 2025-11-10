"""Defines the data schema for fonts."""
from dataclasses import dataclass, field
from .gobject_factory import create_gobject_wrapper

@dataclass
class Font:
    """Represents a font in the game."""
    id: str = field(default="")
    name: str = field(default="")
    file_path: str = field(default="")

FontGObject = create_gobject_wrapper(Font)
