"""Defines the Character data schema and its GObject wrapper."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .gobject_factory import create_gobject_wrapper


@dataclass
class Character:
    """Represents an in-game character, such as an NPC or the player.

    Attributes:
        id (str): The unique identifier for the character.
        display_name (str): The name of the character as shown in-game.
        dialogue_start_id (str): The ID of the dialogue graph that should be
            triggered when the player interacts with this character.
        is_merchant (bool): If True, this character can buy and sell items.
        shop_id (Optional[str]): The ID of the shop inventory, if the
            character is a merchant.
        portrait_asset_id (Optional[str]): The asset ID for the character's
            dialogue portrait.
        sprite_sheet_asset_id (Optional[str]): The asset ID for the character's
            in-game sprite sheet.
        animations (Dict[str, Any]): A dictionary defining the character's
            animations.
    """

    id: str
    display_name: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]
    portrait_asset_id: Optional[str] = None
    sprite_sheet_asset_id: Optional[str] = None
    animations: Dict[str, Any] = field(default_factory=dict)


CharacterGObject = create_gobject_wrapper(Character)
