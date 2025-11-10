"""Defines the Item data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass
from typing import Optional
from .gobject_factory import create_gobject_wrapper


@dataclass
class Item:
    """Represents an in-game item that can be collected or used.

    Attributes:
        id (str): The unique identifier for the item.
        name (str): The display name of the item.
        type (str): The category or type of the item (e.g., "key",
            "consumable").
        buy_price (int): The price to purchase the item from a vendor.
        sell_price (int): The price to sell the item to a vendor.
        description (Optional[str]): A description of the item, often used for
            in-game UI or flavor text.
    """

    id: str
    name: str
    type: str
    buy_price: int
    sell_price: int
    description: Optional[str] = ""


ItemGObject = create_gobject_wrapper(Item)
