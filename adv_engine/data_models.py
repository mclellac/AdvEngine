from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from gi.repository import GObject

# Schema for ItemData.csv
@dataclass
class Item:
    id: str
    name: str
    type: str
    buy_price: int
    sell_price: int

class ItemGObject(GObject.Object):
    __gtype_name__ = 'ItemGObject'

    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)
    buy_price = GObject.Property(type=int)
    sell_price = GObject.Property(type=int)

    def __init__(self, item: Item):
        super().__init__()
        self.id = item.id
        self.name = item.name
        self.type = item.type
        self.buy_price = item.buy_price
        self.sell_price = item.sell_price

# Schema for Attributes.csv
@dataclass
class Attribute:
    id: str
    name: str
    initial_value: int
    max_value: int

class AttributeGObject(GObject.Object):
    __gtype_name__ = 'AttributeGObject'

    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    initial_value = GObject.Property(type=int)
    max_value = GObject.Property(type=int)

    def __init__(self, attribute: Attribute):
        super().__init__()
        self.id = attribute.id
        self.name = attribute.name
        self.initial_value = attribute.initial_value
        self.max_value = attribute.max_value

# Schema for CharacterData.csv
@dataclass
class Character:
    id: str
    default_animation: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]

class CharacterGObject(GObject.Object):
    __gtype_name__ = 'CharacterGObject'

    id = GObject.Property(type=str)
    default_animation = GObject.Property(type=str)
    dialogue_start_id = GObject.Property(type=str)
    is_merchant = GObject.Property(type=bool, default=False)
    shop_id = GObject.Property(type=str)

    def __init__(self, character: Character):
        super().__init__()
        self.id = character.id
        self.default_animation = character.default_animation
        self.dialogue_start_id = character.dialogue_start_id
        self.is_merchant = character.is_merchant
        self.shop_id = character.shop_id

# --- Interaction Matrix Schemas (InteractionMatrix.json) ---

@dataclass
class Condition:
    # Using a generic dict-like structure for now, as it's quite variable.
    # A more robust implementation could use subclasses for different condition types.
    raw_data: Dict[str, Any]

@dataclass
class Action:
    command: str
    parameters: Dict[str, Any]

@dataclass
class Interaction:
    scene_id: str
    target_hotspot_id: str
    used_item_id: Optional[str]
    priority: int
    conditions: List[Condition] = field(default_factory=list)
    actions_on_success: List[Action] = field(default_factory=list)
    fallback_dialogue_id: Optional[str] = None

# A container for all project data
@dataclass
class ProjectData:
    items: List[Item] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    interaction_matrix: List[Interaction] = field(default_factory=list)
    # Dialogue graphs and UI layouts would also be added here.
