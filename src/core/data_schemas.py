"""Defines all data structures for the AdvEngine application.

This module contains all the Python `dataclasses` that represent the core
data entities of an AdvEngine project, such as Items, Characters, Scenes,
and Logic Graphs.

For each core dataclass, a corresponding `GObject.Object` wrapper class is
also defined. These wrappers are essential for integrating the Python data
objects with the GTK user interface, particularly for use in `Gio.ListStore`
and other GTK models. This allows for clean property binding and automatic
UI updates when the underlying data changes.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import json

# --- Core Data Schemas ---

@dataclass
class Item:
    """Represents an in-game item.

    Attributes:
        id (str): A unique identifier for the item.
        name (str): The display name of the item.
        type (str): The category or type of the item.
        buy_price (int): The price to purchase the item.
        sell_price (int): The price to sell the item.
        description (Optional[str]): A description of the item.
    """
    id: str
    name: str
    type: str
    buy_price: int
    sell_price: int
    description: Optional[str] = ""

class ItemGObject(GObject.Object):
    """GObject wrapper for the Item dataclass.

    This class provides a GObject-compatible interface for the Item dataclass,
    allowing it to be used in GTK models and views. It exposes each field of
    the Item dataclass as a GObject property and ensures that any changes to
    the GObject properties are reflected in the underlying Item instance.
    """
    __gtype_name__ = 'ItemGObject'
    id = GObject.Property(type=str, default="")
    name = GObject.Property(type=str, default="")
    type = GObject.Property(type=str, default="")
    buy_price = GObject.Property(type=int, default=0)
    sell_price = GObject.Property(type=int, default=0)
    description = GObject.Property(type=str, default="")

    def __init__(self, item: Item):
        """Initializes the ItemGObject.

        Args:
            item (Item): The Item dataclass instance to wrap.
        """
        super().__init__()
        self.item = item
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(item, prop_name):
                setattr(self, prop_name, getattr(item, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        """Handles the 'notify' signal to update the underlying dataclass.

        Args:
            obj (GObject.Object): The object that emitted the signal.
            pspec (GObject.ParamSpec): The property specification.
        """
        py_attr_name = pspec.name.replace('-', '_')
        if hasattr(self.item, py_attr_name):
            setattr(self.item, py_attr_name, getattr(self, py_attr_name))

@dataclass
class Attribute:
    """Represents a character attribute.

    Attributes:
        id (str): A unique identifier for the attribute.
        name (str): The display name of the attribute.
        initial_value (int): The starting value of the attribute.
        max_value (int): The maximum value of the attribute.
    """
    id: str
    name: str
    initial_value: int
    max_value: int

class AttributeGObject(GObject.Object):
    """GObject wrapper for the Attribute dataclass."""
    __gtype_name__ = 'AttributeGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    initial_value = GObject.Property(type=int)
    max_value = GObject.Property(type=int)

    def __init__(self, attribute: Attribute):
        super().__init__()
        self.attribute = attribute
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(attribute, prop_name):
                setattr(self, prop_name, getattr(attribute, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.attribute, py_attr_name, getattr(self, py_attr_name))

@dataclass
class Character:
    """Represents an in-game character.

    Attributes:
        id (str): A unique identifier for the character.
        display_name (str): The character's name shown in the game.
        dialogue_start_id (str): ID of the dialogue graph for this character.
        is_merchant (bool): True if the character is a merchant.
        shop_id (Optional[str]): The ID of the shop associated with the character.
        portrait_asset_id (Optional[str]): The asset ID for the character's portrait.
        sprite_sheet_asset_id (Optional[str]): The asset ID for the character's sprite sheet.
        animations (Dict[str, Any]): A dictionary of the character's animations.
    """
    id: str
    display_name: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]
    portrait_asset_id: Optional[str] = None
    sprite_sheet_asset_id: Optional[str] = None
    animations: Dict[str, Any] = field(default_factory=dict)

class CharacterGObject(GObject.Object):
    """GObject wrapper for the Character dataclass."""
    __gtype_name__ = 'CharacterGObject'
    id = GObject.Property(type=str)
    display_name = GObject.Property(type=str)
    dialogue_start_id = GObject.Property(type=str)
    is_merchant = GObject.Property(type=bool, default=False)
    shop_id = GObject.Property(type=str)
    portrait_asset_id = GObject.Property(type=str)
    sprite_sheet_asset_id = GObject.Property(type=str)
    animations = GObject.Property(type=str)

    def __init__(self, character: Character):
        super().__init__()
        self.character = character
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(character, prop_name):
                value = getattr(character, prop_name)
                if prop_name == "animations":
                    value = json.dumps(value)
                setattr(self, prop_name, value)
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        value = getattr(self, py_attr_name)
        if py_attr_name == "animations":
            value = json.loads(value)
        setattr(self.character, py_attr_name, value)

# --- Scene Schemas ---

@dataclass
class Hotspot:
    """Represents a clickable area in a scene.

    Attributes:
        id (str): A unique identifier for the hotspot.
        name (str): The display name of the hotspot.
        x (int): The x-coordinate of the hotspot.
        y (int): The y-coordinate of the hotspot.
        width (int): The width of the hotspot.
        height (int): The height of the hotspot.
    """
    id: str
    name: str
    x: int
    y: int
    width: int
    height: int

class HotspotGObject(GObject.Object):
    """GObject wrapper for the Hotspot dataclass."""
    __gtype_name__ = 'HotspotGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    x = GObject.Property(type=int)
    y = GObject.Property(type=int)
    width = GObject.Property(type=int)
    height = GObject.Property(type=int)

    def __init__(self, hotspot: Hotspot):
        super().__init__()
        self.hotspot = hotspot
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(hotspot, prop_name):
                setattr(self, prop_name, getattr(hotspot, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.hotspot, py_attr_name, getattr(self, py_attr_name))

@dataclass
class Scene:
    """Represents a single scene in the game.

    Attributes:
        id (str): A unique identifier for the scene.
        name (str): The display name of the scene.
        background_image (Optional[str]): The file path of the background image.
        hotspots (List[Hotspot]): A list of hotspots in the scene.
    """
    id: str
    name: str
    background_image: Optional[str] = None
    hotspots: List[Hotspot] = field(default_factory=list)

class SceneGObject(GObject.Object):
    """GObject wrapper for the Scene dataclass."""
    __gtype_name__ = 'SceneGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    background_image = GObject.Property(type=str)

    def __init__(self, scene: Scene):
        super().__init__()
        self.scene = scene
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(scene, prop_name):
                setattr(self, prop_name, getattr(scene, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.scene, py_attr_name, getattr(self, py_attr_name))

# --- Logic Editor Schemas (Node-Based) ---

@dataclass
class LogicNode:
    """Base class for all nodes in a logic graph."""
    id: str
    node_type: str
    x: int
    y: int
    width: int = 240
    height: int = 160
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

@dataclass
class DialogueNode(LogicNode):
    """A node that represents a line of dialogue."""
    character_id: str = ""
    dialogue_text: str = ""
    action_node: Optional["ActionNode"] = None

@dataclass
class ConditionNode(LogicNode):
    """A node that checks a condition in the game world."""
    condition_type: str = ""
    var_name: str = ""
    value: str = ""
    item_id: str = ""
    amount: int = 0
    attribute_id: str = ""
    comparison: str = ""
    hotspot_id: str = ""
    state: bool = False
    entity_id: str = ""
    visible: bool = False
    scene_id: str = ""
    times: int = 0
    check_id: str = ""
    mesh_id: str = ""
    time_state: str = ""

@dataclass
class ActionNode(LogicNode):
    """A node that performs an action in the game world."""
    action_command: str = ""
    var_name: str = ""
    value: str = ""
    item_id: str = ""
    amount: int = 0
    scene_id: str = ""
    spawn_point: str = ""
    shop_id: str = ""
    attribute_id: str = ""
    cinematic_id: str = ""
    sound_id: str = ""
    hotspot_id: str = ""
    target_id: str = ""
    animation_key: str = ""
    loop: bool = False
    entity_id: str = ""
    x: int = 0
    y: int = 0
    mode: str = ""
    mesh_id: str = ""
    dialogue_node_id: str = ""
    quest_id: str = ""
    objective_id: str = ""

@dataclass
class LogicGraph:
    """Represents a graph of logic nodes."""
    id: str
    name: str
    nodes: List[LogicNode] = field(default_factory=list)

# --- Asset Schemas ---

@dataclass
class Asset:
    """Represents a generic game asset."""
    id: str
    name: str
    asset_type: str
    file_path: str

class AssetGObject(GObject.Object):
    """GObject wrapper for the Asset dataclass."""
    __gtype_name__ = 'AssetGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    asset_type = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, asset: Asset):
        super().__init__()
        self.asset = asset
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(asset, prop_name):
                setattr(self, prop_name, getattr(asset, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.asset, py_attr_name, getattr(self, py_attr_name))

@dataclass
class Animation(Asset):
    """Represents an animated asset."""
    frame_count: int
    frame_rate: int
    frames: List[str] = field(default_factory=list)

# --- Audio Schemas ---

@dataclass
class Audio(Asset):
    """Represents an audio asset."""
    duration: float

class AudioGObject(GObject.Object):
    """GObject wrapper for the Audio dataclass."""
    __gtype_name__ = 'AudioGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)
    duration = GObject.Property(type=float)

    def __init__(self, audio: Audio):
        super().__init__()
        self.audio = audio
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(audio, prop_name):
                setattr(self, prop_name, getattr(audio, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.audio, py_attr_name, getattr(self, py_attr_name))

# --- Global State Schema ---

@dataclass
class GlobalVariable:
    """Represents a global variable in the game."""
    id: str
    name: str
    type: str
    initial_value: Any
    category: Optional[str] = "Default"

class GlobalVariableGObject(GObject.Object):
    """GObject wrapper for the GlobalVariable dataclass."""
    __gtype_name__ = 'GlobalVariableGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)
    initial_value_str = GObject.Property(type=str)
    category = GObject.Property(type=str)

    def __init__(self, variable: GlobalVariable):
        super().__init__()
        self.variable = variable
        self.id = variable.id
        self.name = variable.name
        self.type = variable.type
        self.initial_value_str = str(variable.initial_value)
        self.category = variable.category
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        value = getattr(self, py_attr_name)

        if py_attr_name == "initial_value_str":
            data_attr_name = "initial_value"
            if self.type == "int":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = 0
            elif self.type == "bool":
                value = value.lower() in ["true", "1"]
            setattr(self.variable, data_attr_name, value)
        else:
            setattr(self.variable, py_attr_name, value)

# --- Verb Schema ---

@dataclass
class Verb:
    """Represents a verb that the player can use."""
    id: str
    name: str

class VerbGObject(GObject.Object):
    """GObject wrapper for the Verb dataclass."""
    __gtype_name__ = 'VerbGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, verb: Verb):
        super().__init__()
        self.verb = verb
        self.id = verb.id
        self.name = verb.name
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.verb, py_attr_name, getattr(self, py_attr_name))

# --- Interaction Schemas ---

@dataclass
class Interaction:
    """Represents an interaction between a verb and one or two items."""
    id: str
    verb_id: str
    logic_graph_id: str
    primary_item_id: Optional[str] = None
    secondary_item_id: Optional[str] = None
    target_hotspot_id: Optional[str] = None

class InteractionGObject(GObject.Object):
    """GObject wrapper for the Interaction dataclass."""
    __gtype_name__ = 'InteractionGObject'
    id = GObject.Property(type=str)
    verb_id = GObject.Property(type=str)
    primary_item_id = GObject.Property(type=str)
    secondary_item_id = GObject.Property(type=str)
    target_hotspot_id = GObject.Property(type=str)
    logic_graph_id = GObject.Property(type=str)

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(interaction, prop_name):
                setattr(self, prop_name, getattr(interaction, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.interaction, py_attr_name, getattr(self, py_attr_name))

# --- UI and Font Schemas ---

@dataclass
class Font:
    """Represents a font."""
    id: str
    name: str
    file_path: str

class FontGObject(GObject.Object):
    """GObject wrapper for the Font dataclass."""
    __gtype_name__ = 'FontGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, font: Font):
        super().__init__()
        self.font = font
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(font, prop_name):
                setattr(self, prop_name, getattr(font, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.font, py_attr_name, getattr(self, py_attr_name))

@dataclass
class UIElement:
    """Represents a single element in a UI layout."""
    id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UILayout:
    """Represents a layout of UI elements."""
    id: str
    name: str
    elements: List["UIElement"] = field(default_factory=list)

class UILayoutGObject(GObject.Object):
    """GObject wrapper for the UILayout dataclass."""
    __gtype_name__ = 'UILayoutGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, layout: UILayout):
        super().__init__()
        self.layout = layout
        self.id = layout.id
        self.name = layout.name
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.layout, py_attr_name, getattr(self, py_attr_name))

# --- Quest Schemas ---

@dataclass
class Objective:
    """Represents a single objective in a quest."""
    id: str
    name: str
    completed: bool = False

class ObjectiveGObject(GObject.Object):
    """GObject wrapper for the Objective dataclass."""
    __gtype_name__ = 'ObjectiveGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    completed = GObject.Property(type=bool, default=False)

    def __init__(self, objective: Objective):
        super().__init__()
        self.objective = objective
        for prop in self.list_properties():
            prop_name = prop.name.replace('-', '_')
            if hasattr(objective, prop_name):
                setattr(self, prop_name, getattr(objective, prop_name))
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.objective, py_attr_name, getattr(self, py_attr_name))

@dataclass
class Quest:
    """Represents a quest."""
    id: str
    name: str
    objectives: List[Objective] = field(default_factory=list)

class QuestGObject(GObject.Object):
    """GObject wrapper for the Quest dataclass."""
    __gtype_name__ = 'QuestGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, quest: Quest):
        super().__init__()
        self.quest = quest
        self.id = quest.id
        self.name = quest.name
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace('-', '_')
        setattr(self.quest, py_attr_name, getattr(self, py_attr_name))

# --- Search Result Schema ---

@dataclass
class SearchResult:
    """Represents a single search result."""
    id: str
    name: str
    type: str

class SearchResultGObject(GObject.Object):
    """GObject wrapper for the SearchResult dataclass."""
    __gtype_name__ = 'SearchResultGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    type = GObject.Property(type=str)

    def __init__(self, id: str, name: str, type: str):
        super().__init__()
        self.id = id
        self.name = name
        self.type = type

# --- Project Data Container ---

@dataclass
class ProjectData:
    """A container for all data in an AdvEngine project."""
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
    interactions: List[Interaction] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)
    ui_layouts: List["UILayout"] = field(default_factory=list)
    fonts: List["Font"] = field(default_factory=list)

# --- Utility GObject Wrappers ---

class StringGObject(GObject.Object):
    """A GObject wrapper for a simple Python string."""
    __gtype_name__ = 'StringGObject'
    value = GObject.Property(type=str)

    def __init__(self, value):
        super().__init__()
        self.value = value
