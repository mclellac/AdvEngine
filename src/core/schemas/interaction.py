"""Defines the Interaction data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from typing import Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class Interaction:
    """Represents an interaction between a verb and one or two items."""

    id: str
    verb_id: str
    logic_graph_id: str
    primary_item_id: Optional[str] = None
    secondary_item_id: Optional[str] = None
    target_hotspot_id: Optional[str] = None


InteractionGObject = create_gobject_wrapper(Interaction)
