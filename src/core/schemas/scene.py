"""Defines the Scene and Hotspot data schemas and their GObject wrappers."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import List, Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class Hotspot:
    """Represents a clickable area or region of interest within a Scene.

    Attributes:
        id (str): The unique identifier for the hotspot.
        name (str): The display name of the hotspot.
        x (int): The x-coordinate of the top-left corner of the hotspot.
        y (int): The y-coordinate of the top-left corner of the hotspot.
        width (int): The width of the hotspot.
        height (int): The height of the hotspot.
    """

    id: str
    name: str
    x: int
    y: int
    width: int
    height: int


HotspotGObject = create_gobject_wrapper(Hotspot)


@dataclass
class Scene:
    """Represents a single location or screen in the game.

    Attributes:
        id (str): The unique identifier for the scene.
        name (str): The display name of the scene.
        background_image (Optional[str]): The asset ID for the scene's
            background image.
        hotspots (List[Hotspot]): A list of hotspots within the scene.
    """

    id: str
    name: str
    background_image: Optional[str] = None
    hotspots: List[Hotspot] = field(default_factory=list)


SceneGObject = create_gobject_wrapper(Scene)
