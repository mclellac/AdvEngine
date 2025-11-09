"""Defines the Character data schema and its GObject wrapper."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .gobject_factory import create_gobject_wrapper

@dataclass
class Character:
    """Represents an in-game character."""
    id: str
    display_name: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]
    portrait_asset_id: Optional[str] = None
    sprite_sheet_asset_id: Optional[str] = None
    animations: Dict[str, Any] = field(default_factory=dict)

CharacterGObject = create_gobject_wrapper(Character)
