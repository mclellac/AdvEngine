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
    portrait_asset_id: Optional[str] = None

class CharacterGObject(GObject.Object):
    __gtype_name__ = 'CharacterGObject'

    id = GObject.Property(type=str)
    display_name = GObject.Property(type=str)
    dialogue_start_id = GObject.Property(type=str)
    is_merchant = GObject.Property(type=bool, default=False)
    shop_id = GObject.Property(type=str)
    portrait_asset_id = GObject.Property(type=str)

    def __init__(self, character: Character):
        super().__init__()
        self.character_data = character
        self.id = character.id
        self.display_name = character.display_name
        self.dialogue_start_id = character.dialogue_start_id
        self.is_merchant = character.is_merchant
        self.shop_id = character.shop_id
        self.portrait_asset_id = character.portrait_asset_id

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
    width: int = 240
    height: int = 160
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

# --- Cutscene Schemas ---
@dataclass
class CutsceneAction:
    command: str
    parameters: List[str] = field(default_factory=list)

@dataclass
class Cutscene:
    id: str
    name: str
    script: str = ""
    actions: List[CutsceneAction] = field(default_factory=list)

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

# --- Global State Schema ---
@dataclass
class GlobalVariable:
    id: str
    name: str
    type: str  # "bool", "int", "str"
    initial_value: Any
    category: Optional[str] = "Default"

class GlobalVariableGObject(GObject.Object):
    __gtype_name__ = 'GlobalVariableGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)
    initial_value_str = GObject.Property(type=str)
    category = GObject.Property(type=str)

    def __init__(self, variable: GlobalVariable):
        super().__init__()
        self.variable_data = variable
        self.id = variable.id
        self.name = variable.name
        self.type = variable.type
        self.initial_value_str = str(variable.initial_value)
        self.category = variable.category

# --- Verb Schema ---
@dataclass
class Verb:
    id: str
    name: str

class VerbGObject(GObject.Object):
    __gtype_name__ = 'VerbGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, verb: Verb):
        super().__init__()
        self.verb_data = verb
        self.id = verb.id
        self.name = verb.name

# --- Interaction Schemas ---
@dataclass
class Interaction:
    """Represents a game interaction, which links a trigger (like using a verb
    on an item) to a logic graph that defines conditions and actions."""
    id: str
    verb_id: str
    # ID of the LogicGraph containing the conditions and actions for this interaction.
    logic_graph_id: str
    # The primary item for the interaction (e.g., the item being used).
    primary_item_id: Optional[str] = None
    # The secondary item for 'combine' interactions (e.g., use item A on item B).
    secondary_item_id: Optional[str] = None
    # The hotspot that is the target of the interaction.
    target_hotspot_id: Optional[str] = None

@dataclass
class Font:
    id: str
    name: str
    file_path: str

@dataclass
class UIElement:
    id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UILayout:
    id: str
    name: str
    elements: List['UIElement'] = field(default_factory=list)

class UILayoutGObject(GObject.Object):
    __gtype_name__ = 'UILayoutGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, layout: UILayout):
        super().__init__()
        self.layout_data = layout
        self.id = layout.id
        self.name = layout.name

class FontGObject(GObject.Object):
    __gtype_name__ = 'FontGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, font: Font):
        super().__init__()
        self.font_data = font
        self.id = font.id
        self.name = font.name
        self.file_path = font.file_path

@dataclass
class Objective:
    id: str
    name: str
    completed: bool = False

@dataclass
class Quest:
    id: str
    name: str
    objectives: List[Objective] = field(default_factory=list)

class ObjectiveGObject(GObject.Object):
    __gtype_name__ = 'ObjectiveGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    completed = GObject.Property(type=bool, default=False)

    def __init__(self, objective: Objective):
        super().__init__()
        self.objective_data = objective
        self.id = objective.id
        self.name = objective.name
        self.completed = objective.completed

class QuestGObject(GObject.Object):
    __gtype_name__ = 'QuestGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, quest: Quest):
        super().__init__()
        self.quest_data = quest
        self.id = quest.id
        self.name = quest.name

class InteractionGObject(GObject.Object):
    __gtype_name__ = 'InteractionGObject'

    id = GObject.Property(type=str)
    verb_id = GObject.Property(type=str)
    primary_item_id = GObject.Property(type=str)
    secondary_item_id = GObject.Property(type=str)
    target_hotspot_id = GObject.Property(type=str)
    logic_graph_id = GObject.Property(type=str)

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction_data = interaction
        self.id = interaction.id
        self.verb_id = interaction.verb_id
        self.primary_item_id = interaction.primary_item_id
        self.secondary_item_id = interaction.secondary_item_id
        self.target_hotspot_id = interaction.target_hotspot_id
        self.logic_graph_id = interaction.logic_graph_id

# --- Search Result Schema ---
@dataclass
class SearchResult:
    id: str
    name: str
    type: str

class SearchResultGObject(GObject.Object):
    __gtype_name__ = 'SearchResultGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)

    def __init__(self, id: str, name: str, type: str):
        super().__init__()
        self.id = id
        self.name = name
        self.type = type


# A container for all project data
@dataclass
class ProjectData:
    global_variables: List[GlobalVariable] = field(default_factory=list)
    verbs: List[Verb] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    logic_graphs: List[LogicGraph] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)
    audio_files: List[Audio] = field(default_factory=list)
    dialogue_graphs: List[LogicGraph] = field(default_factory=list)
    cutscenes: List[Cutscene] = field(default_factory=list)
    interactions: List[Interaction] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)
    ui_layouts: List['UILayout'] = field(default_factory=list)
    fonts: List['Font'] = field(default_factory=list)
    # UI layouts would also be added here.

class StringGObject(GObject.Object):
    __gtype_name__ = 'StringGObject'
    value = GObject.Property(type=str)

    def __init__(self, value):
        super().__init__()
        self.value = value
