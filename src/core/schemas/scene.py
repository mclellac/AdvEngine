"""Defines the Scene and Hotspot data schemas and their GObject wrappers."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import List, Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class Hotspot:
    """Represents a clickable area in a scene."""

    id: str
    name: str
    x: int
    y: int
    width: int
    height: int


HotspotGObject = create_gobject_wrapper(Hotspot)


@dataclass
class Scene:
    """Represents a single scene in the game."""

    id: str
    name: str
    background_image: Optional[str] = None
    hotspots: List[Hotspot] = field(default_factory=list)


SceneGObject = create_gobject_wrapper(Scene)
