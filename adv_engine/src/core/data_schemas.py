import gi
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
    description: Optional[str] = ""

class ItemGObject(GObject.Object):
    __gtype_name__ = 'ItemGObject'

    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)
    buy_price = GObject.Property(type=int)
    sell_price = GObject.Property(type=int)
    description = GObject.Property(type=str)

    def __init__(self, item: Item):
        super().__init__()
        self.item = item
        self.id = item.id
        self.name = item.name
        self.type = item.type
        self.buy_price = item.buy_price
        self.sell_price = item.sell_price
        self.description = item.description

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
        self.attribute_data = attribute
        self.id = attribute.id
        self.name = attribute.name
        self.initial_value = attribute.initial_value
        self.max_value = attribute.max_value

# Schema for CharacterData.csv
@dataclass
class Character:
    id: str
    display_name: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]

class CharacterGObject(GObject.Object):
    __gtype_name__ = 'CharacterGObject'

    id = GObject.Property(type=str)
    display_name = GObject.Property(type=str)
    dialogue_start_id = GObject.Property(type=str)
    is_merchant = GObject.Property(type=bool, default=False)
    shop_id = GObject.Property(type=str)

    def __init__(self, character: Character):
        super().__init__()
        self.character_data = character
        self.id = character.id
        self.display_name = character.display_name
        self.dialogue_start_id = character.dialogue_start_id
        self.is_merchant = character.is_merchant
        self.shop_id = character.shop_id

# --- Scene Schemas ---

@dataclass
class Hotspot:
    id: str
    name: str
    x: int
    y: int
    width: int
    height: int

class HotspotGObject(GObject.Object):
    __gtype_name__ = 'HotspotGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    x = GObject.Property(type=int)
    y = GObject.Property(type=int)
    width = GObject.Property(type=int)
    height = GObject.Property(type=int)

    def __init__(self, hotspot: Hotspot):
        super().__init__()
        self.hotspot_data = hotspot
        self.id = hotspot.id
        self.name = hotspot.name
        self.x = hotspot.x
        self.y = hotspot.y
        self.width = hotspot.width
        self.height = hotspot.height

@dataclass
class Scene:
    id: str
    name: str
    background_image: Optional[str] = None
    hotspots: List[Hotspot] = field(default_factory=list)

class SceneGObject(GObject.Object):
    __gtype_name__ = 'SceneGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    background_image = GObject.Property(type=str)

    def __init__(self, scene: Scene):
        super().__init__()
        self.id = scene.id
        self.name = scene.name
        self.background_image = scene.background_image
        self.scene_data = scene # Store the original dataclass for access to hotspots

# --- Logic Editor Schemas (Node-Based) ---

@dataclass
class LogicNode:
    id: str
    node_type: str
    x: int
    y: int
    inputs: List[str] = field(default_factory=list)  # List of connected node IDs
    outputs: List[str] = field(default_factory=list) # List of connected node IDs

@dataclass
class DialogueNode(LogicNode):
    character_id: str = ""
    dialogue_text: str = ""

@dataclass
class ConditionNode(LogicNode):
    # e.g., "check_variable", "check_attribute"
    condition_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActionNode(LogicNode):
    # e.g., "SET_VARIABLE", "INVENTORY_ADD"
    action_command: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LogicGraph:
    id: str
    name: str
    nodes: List[LogicNode] = field(default_factory=list)

# --- Asset Schemas ---
@dataclass
class Asset:
    id: str
    name: str
    asset_type: str # "sprite", "animation", "sound"
    file_path: str

@dataclass
class Animation(Asset):
    frame_count: int
    frame_rate: int
    frames: List[str] = field(default_factory=list)

# --- Audio Schemas ---
@dataclass
class Audio(Asset):
    duration: float # in seconds

# A container for all project data
@dataclass
class ProjectData:
    items: List[Item] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    logic_graphs: List[LogicGraph] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)
    audio_files: List[Audio] = field(default_factory=list)
    # Dialogue graphs and UI layouts would also be added here.

class StringGObject(GObject.Object):
    __gtype_name__ = 'StringGObject'
    value = GObject.Property(type=str)

    def __init__(self, value):
        super().__init__()
        self.value = value
