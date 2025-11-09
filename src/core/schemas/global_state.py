"""Defines the GlobalVariable data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from typing import Any, Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class GlobalVariable:
    """Represents a global variable in the game."""

    id: str
    name: str
    type: str
    initial_value: Any
    category: Optional[str] = "Default"


GlobalVariableGObject = create_gobject_wrapper(GlobalVariable)
