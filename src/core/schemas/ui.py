"""Defines data schemas for UI elements and fonts."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .gobject_factory import create_gobject_wrapper


@dataclass
class UIElement:
    """Represents a single element in a UI layout."""

    id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UILayout:
    """Represents a layout of UI elements."""

    id: str
    name: str
    elements: List["UIElement"] = field(default_factory=list)


UILayoutGObject = create_gobject_wrapper(UILayout)
