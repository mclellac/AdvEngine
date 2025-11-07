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
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from gi.repository import GObject


# Schema for ItemData.csv
@dataclass
class Item:
    """Represents an in-game item.

    Attributes:
        id: A unique identifier for the item.
        name: The display name of the item.
        type: The category or type of the item.
        buy_price: The price to purchase the item.
        sell_price: The price to sell the item.
        description: A description of the item.
    """

    id: str
    name: str
    type: str
    buy_price: int
    sell_price: int
    description: Optional[str] = ""


class ItemGObject(GObject.Object):
    """GObject wrapper for the Item dataclass."""

    __gtype_name__ = "ItemGObject"
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

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::type", self._on_property_changed, "type")
        self.connect("notify::buy_price", self._on_property_changed, "buy_price")
        self.connect("notify::sell_price", self._on_property_changed, "sell_price")
        self.connect("notify::description", self._on_property_changed, "description")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.item, data_key, getattr(self, data_key))


# Schema for Attributes.csv
@dataclass
class Attribute:
    """Represents a character attribute.

    Attributes:
        id: A unique identifier for the attribute.
        name: The display name of the attribute.
        initial_value: The starting value of the attribute.
        max_value: The maximum value of the attribute.
    """

    id: str
    name: str
    initial_value: int
    max_value: int


class AttributeGObject(GObject.Object):
    """GObject wrapper for the Attribute dataclass."""

    __gtype_name__ = "AttributeGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    initial_value = GObject.Property(type=int)
    max_value = GObject.Property(type=int)

    def __init__(self, attribute: Attribute):
        super().__init__()
        self.attribute = attribute
        self.id = attribute.id
        self.name = attribute.name
        self.initial_value = attribute.initial_value
        self.max_value = attribute.max_value

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect(
            "notify::initial_value", self._on_property_changed, "initial_value"
        )
        self.connect("notify::max_value", self._on_property_changed, "max_value")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.attribute, data_key, getattr(self, data_key))


# Schema for CharacterData.csv
@dataclass
class Character:
    """Represents an in-game character.

    Attributes:
        id: A unique identifier for the character.
        display_name: The display name of the character.
        dialogue_start_id: The ID of the dialogue graph to start when
            interacting with this character.
        is_merchant: True if the character is a merchant.
        shop_id: The ID of the shop associated with this character.
        portrait_asset_id: The ID of the asset to use for this character's
            portrait.
    """

    id: str
    display_name: str
    dialogue_start_id: str
    is_merchant: bool
    shop_id: Optional[str]
    portrait_asset_id: Optional[str] = None


class CharacterGObject(GObject.Object):
    """GObject wrapper for the Character dataclass."""

    __gtype_name__ = "CharacterGObject"
    id = GObject.Property(type=str)
    display_name = GObject.Property(type=str)
    dialogue_start_id = GObject.Property(type=str)
    is_merchant = GObject.Property(type=bool, default=False)
    shop_id = GObject.Property(type=str)
    portrait_asset_id = GObject.Property(type=str)

    def __init__(self, character: Character):
        super().__init__()
        self.character = character
        self.id = character.id
        self.display_name = character.display_name
        self.dialogue_start_id = character.dialogue_start_id
        self.is_merchant = character.is_merchant
        self.shop_id = character.shop_id
        self.portrait_asset_id = character.portrait_asset_id

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::display_name", self._on_property_changed, "display_name")
        self.connect(
            "notify::dialogue_start_id", self._on_property_changed, "dialogue_start_id"
        )
        self.connect("notify::is_merchant", self._on_property_changed, "is_merchant")
        self.connect("notify::shop_id", self._on_property_changed, "shop_id")
        self.connect(
            "notify::portrait_asset_id", self._on_property_changed, "portrait_asset_id"
        )

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.character, data_key, getattr(self, data_key))


# --- Scene Schemas ---
@dataclass
class Hotspot:
    """Represents a clickable area in a scene.

    Attributes:
        id: A unique identifier for the hotspot.
        name: The display name of the hotspot.
        x: The x-coordinate of the hotspot.
        y: The y-coordinate of the hotspot.
        width: The width of the hotspot.
        height: The height of the hotspot.
    """

    id: str
    name: str
    x: int
    y: int
    width: int
    height: int


class HotspotGObject(GObject.Object):
    """GObject wrapper for the Hotspot dataclass."""

    __gtype_name__ = "HotspotGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    x = GObject.Property(type=int)
    y = GObject.Property(type=int)
    width = GObject.Property(type=int)
    height = GObject.Property(type=int)

    def __init__(self, hotspot: Hotspot):
        super().__init__()
        self.hotspot = hotspot
        self.id = hotspot.id
        self.name = hotspot.name
        self.x = hotspot.x
        self.y = hotspot.y
        self.width = hotspot.width
        self.height = hotspot.height

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::x", self._on_property_changed, "x")
        self.connect("notify::y", self._on_property_changed, "y")
        self.connect("notify::width", self._on_property_changed, "width")
        self.connect("notify::height", self._on_property_changed, "height")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.hotspot, data_key, getattr(self, data_key))


@dataclass
class Scene:
    """Represents a single scene in the game.

    Attributes:
        id: A unique identifier for the scene.
        name: The display name of the scene.
        background_image: The file path of the background image for the scene.
        hotspots: A list of hotspots in the scene.
    """

    id: str
    name: str
    background_image: Optional[str] = None
    hotspots: List[Hotspot] = field(default_factory=list)


class SceneGObject(GObject.Object):
    """GObject wrapper for the Scene dataclass."""

    __gtype_name__ = "SceneGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    background_image = GObject.Property(type=str)

    def __init__(self, scene: Scene):
        super().__init__()
        self.scene = scene
        self.id = scene.id
        self.name = scene.name
        self.background_image = scene.background_image

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect(
            "notify::background_image", self._on_property_changed, "background_image"
        )

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.scene, data_key, getattr(self, data_key))


# --- Logic Editor Schemas (Node-Based) ---
@dataclass
class LogicNode:
    """Base class for all nodes in a logic graph.

    Attributes:
        id: A unique identifier for the node.
        node_type: The type of the node (e.g., "Dialogue", "Condition").
        x: The x-coordinate of the node on the canvas.
        y: The y-coordinate of the node on the canvas.
        width: The width of the node.
        height: The height of the node.
        inputs: A list of IDs of nodes that connect to this node's inputs.
        outputs: A list of IDs of nodes that this node's outputs connect to.
    """

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
    """A node that represents a line of dialogue.

    Attributes:
        character_id: The ID of the character speaking the dialogue.
        dialogue_text: The text of the dialogue.
        action_node: An optional action to perform when this dialogue is
            triggered.
    """

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


@dataclass
class LogicGraph:
    """Represents a graph of logic nodes.

    Attributes:
        id: A unique identifier for the logic graph.
        name: The display name of the logic graph.
        nodes: A list of nodes in the logic graph.
    """

    id: str
    name: str
    nodes: List[LogicNode] = field(default_factory=list)


# --- Asset Schemas ---
@dataclass
class Asset:
    """Represents a generic game asset.

    Attributes:
        id: A unique identifier for the asset.
        name: The display name of the asset.
        asset_type: The type of the asset (e.g., "image", "sound").
        file_path: The path to the asset file.
    """

    id: str
    name: str
    asset_type: str
    file_path: str


class AssetGObject(GObject.Object):
    """GObject wrapper for the Asset dataclass."""

    __gtype_name__ = "AssetGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    asset_type = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, asset: Asset):
        super().__init__()
        self.asset = asset
        self.id = asset.id
        self.name = asset.name
        self.asset_type = asset.asset_type
        self.file_path = asset.file_path

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::asset_type", self._on_property_changed, "asset_type")
        self.connect("notify::file_path", self._on_property_changed, "file_path")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.asset, data_key, getattr(self, data_key))


@dataclass
class Animation(Asset):
    """Represents an animated asset.

    Attributes:
        frame_count: The number of frames in the animation.
        frame_rate: The frame rate of the animation.
        frames: A list of file paths for each frame of the animation.
    """

    frame_count: int
    frame_rate: int
    frames: List[str] = field(default_factory=list)


# --- Audio Schemas ---
@dataclass
class Audio(Asset):
    """Represents an audio asset.

    Attributes:
        duration: The duration of the audio in seconds.
    """

    duration: float


class AudioGObject(GObject.Object):
    """GObject wrapper for the Audio dataclass."""

    __gtype_name__ = "AudioGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)
    duration = GObject.Property(type=float)

    def __init__(self, audio: Audio):
        super().__init__()
        self.audio = audio
        self.id = audio.id
        self.name = audio.name
        self.file_path = audio.file_path
        self.duration = audio.duration

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::file_path", self._on_property_changed, "file_path")
        self.connect("notify::duration", self._on_property_changed, "duration")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.audio, data_key, getattr(self, data_key))


# --- Global State Schema ---
@dataclass
class GlobalVariable:
    """Represents a global variable in the game.

    Attributes:
        id: A unique identifier for the variable.
        name: The name of the variable.
        type: The data type of the variable (e.g., "int", "bool", "str").
        initial_value: The initial value of the variable.
        category: The category of the variable, for organization.
    """

    id: str
    name: str
    type: str
    initial_value: Any
    category: Optional[str] = "Default"


class GlobalVariableGObject(GObject.Object):
    """GObject wrapper for the GlobalVariable dataclass."""

    __gtype_name__ = "GlobalVariableGObject"
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

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::type", self._on_property_changed, "type")
        self.connect(
            "notify::initial_value_str", self._on_property_changed, "initial_value"
        )
        self.connect("notify::category", self._on_property_changed, "category")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        value = getattr(self, pspec.name)
        if data_key == "initial_value":
            # Coerce the string value from the UI to the correct type
            if self.type == "int":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = 0
            elif self.type == "bool":
                value = value.lower() in ["true", "1"]
        setattr(self.variable, data_key, value)


# --- Verb Schema ---
@dataclass
class Verb:
    """Represents a verb that the player can use.

    Attributes:
        id: A unique identifier for the verb.
        name: The display name of the verb.
    """

    id: str
    name: str


class VerbGObject(GObject.Object):
    """GObject wrapper for the Verb dataclass."""

    __gtype_name__ = "VerbGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, verb: Verb):
        super().__init__()
        self.verb = verb
        self.id = verb.id
        self.name = verb.name

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.verb, data_key, getattr(self, data_key))


# --- Interaction Schemas ---
@dataclass
class Interaction:
    """Represents an interaction between a verb and one or two items.

    Attributes:
        id: A unique identifier for the interaction.
        verb_id: The ID of the verb used in the interaction.
        logic_graph_id: The ID of the logic graph to execute when this
            interaction is triggered.
        primary_item_id: The ID of the primary item in the interaction.
        secondary_item_id: The ID of the secondary item in the interaction.
        target_hotspot_id: The ID of the hotspot that is the target of the
            interaction.
    """

    id: str
    verb_id: str
    logic_graph_id: str
    primary_item_id: Optional[str] = None
    secondary_item_id: Optional[str] = None
    target_hotspot_id: Optional[str] = None


@dataclass
class Font:
    """Represents a font.

    Attributes:
        id: A unique identifier for the font.
        name: The display name of the font.
        file_path: The path to the font file.
    """

    id: str
    name: str
    file_path: str


@dataclass
class UIElement:
    """Represents a single element in a UI layout.

    Attributes:
        id: A unique identifier for the element.
        type: The type of the element (e.g., "button", "label").
        x: The x-coordinate of the element.
        y: The y-coordinate of the element.
        width: The width of the element.
        height: The height of the element.
        properties: A dictionary of properties for the element.
    """

    id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UILayout:
    """Represents a layout of UI elements.

    Attributes:
        id: A unique identifier for the layout.
        name: The display name of the layout.
        elements: A list of UI elements in the layout.
    """

    id: str
    name: str
    elements: List["UIElement"] = field(default_factory=list)


class UILayoutGObject(GObject.Object):
    """GObject wrapper for the UILayout dataclass."""

    __gtype_name__ = "UILayoutGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, layout: UILayout):
        super().__init__()
        self.layout = layout
        self.id = layout.id
        self.name = layout.name

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.layout, data_key, getattr(self, data_key))


class FontGObject(GObject.Object):
    """GObject wrapper for the Font dataclass."""

    __gtype_name__ = "FontGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, font: Font):
        super().__init__()
        self.font = font
        self.id = font.id
        self.name = font.name
        self.file_path = font.file_path

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::file_path", self._on_property_changed, "file_path")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.font, data_key, getattr(self, data_key))


@dataclass
class Objective:
    """Represents a single objective in a quest.

    Attributes:
        id: A unique identifier for the objective.
        name: The display name of the objective.
        completed: True if the objective has been completed.
    """

    id: str
    name: str
    completed: bool = False


@dataclass
class Quest:
    """Represents a quest.

    Attributes:
        id: A unique identifier for the quest.
        name: The display name of the quest.
        objectives: A list of objectives in the quest.
    """

    id: str
    name: str
    objectives: List[Objective] = field(default_factory=list)


class ObjectiveGObject(GObject.Object):
    """GObject wrapper for the Objective dataclass."""

    __gtype_name__ = "ObjectiveGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    completed = GObject.Property(type=bool, default=False)

    def __init__(self, objective: Objective):
        super().__init__()
        self.objective = objective
        self.id = objective.id
        self.name = objective.name
        self.completed = objective.completed

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")
        self.connect("notify::completed", self._on_property_changed, "completed")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.objective, data_key, getattr(self, data_key))


class QuestGObject(GObject.Object):
    """GObject wrapper for the Quest dataclass."""

    __gtype_name__ = "QuestGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, quest: Quest):
        super().__init__()
        self.quest = quest
        self.id = quest.id
        self.name = quest.name

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::name", self._on_property_changed, "name")

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.quest, data_key, getattr(self, data_key))


class InteractionGObject(GObject.Object):
    """GObject wrapper for the Interaction dataclass."""

    __gtype_name__ = "InteractionGObject"
    id = GObject.Property(type=str)
    verb_id = GObject.Property(type=str)
    primary_item_id = GObject.Property(type=str)
    secondary_item_id = GObject.Property(type=str)
    target_hotspot_id = GObject.Property(type=str)
    logic_graph_id = GObject.Property(type=str)

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction
        self.id = interaction.id
        self.verb_id = interaction.verb_id
        self.primary_item_id = interaction.primary_item_id
        self.secondary_item_id = interaction.secondary_item_id
        self.target_hotspot_id = interaction.target_hotspot_id
        self.logic_graph_id = interaction.logic_graph_id

        self.connect("notify::id", self._on_property_changed, "id")
        self.connect("notify::verb_id", self._on_property_changed, "verb_id")
        self.connect(
            "notify::primary_item_id", self._on_property_changed, "primary_item_id"
        )
        self.connect(
            "notify::secondary_item_id", self._on_property_changed, "secondary_item_id"
        )
        self.connect(
            "notify::target_hotspot_id", self._on_property_changed, "target_hotspot_id"
        )
        self.connect(
            "notify::logic_graph_id", self._on_property_changed, "logic_graph_id"
        )

    def _on_property_changed(self, obj, pspec, data_key):
        """Handles the notify signal for a property."""
        setattr(self.interaction, data_key, getattr(self, data_key))


# --- Search Result Schema ---
@dataclass
class SearchResult:
    """Represents a single search result.

    Attributes:
        id: The ID of the search result.
        name: The display name of the search result.
        type: The type of the search result (e.g., "Item", "Character").
    """

    id: str
    name: str
    type: str


class SearchResultGObject(GObject.Object):
    """GObject wrapper for the SearchResult dataclass."""

    __gtype_name__ = "SearchResultGObject"
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


class StringGObject(GObject.Object):
    """A GObject wrapper for a simple Python string."""

    __gtype_name__ = "StringGObject"
    value = GObject.Property(type=str)

    def __init__(self, value):
        super().__init__()
        self.value = value
