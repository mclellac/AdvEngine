"""Defines the Item data schema and its GObject wrapper."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass
from typing import Optional
from .gobject_factory import create_gobject_wrapper

@dataclass
class Item:
    """Represents an in-game item."""
    id: str
    name: str
    type: str
    buy_price: int
    sell_price: int
    description: Optional[str] = ""

ItemGObject = create_gobject_wrapper(Item)
