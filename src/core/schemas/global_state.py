"""Defines the GlobalVariable data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from typing import Any, Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class GlobalVariable:
    """Represents a global variable used for tracking game state.

    These variables can be used in conditions to control game logic, track
    quest progress, or store player choices.

    Attributes:
        id (str): The unique identifier for the variable (e.g., "quest_1_done").
        name (str): The display name of the variable.
        type (str): The data type of the variable (e.g., "bool", "int", "str").
        initial_value (Any): The value the variable should have at the start
            of the game.
        category (Optional[str]): A category for organizing variables in the
            editor. Defaults to "Default".
    """

    id: str
    name: str
    type: str
    initial_value: Any
    category: Optional[str] = "Default"


GlobalVariableGObject = create_gobject_wrapper(GlobalVariable)
