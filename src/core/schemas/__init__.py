"""Initializes the schemas module and exposes all data classes."""

from .item import Item, ItemGObject
from .attribute import Attribute, AttributeGObject
from .character import Character, CharacterGObject
from .scene import Scene, SceneGObject, Hotspot, HotspotGObject
from .logic import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph
from .asset import Asset, AssetGObject, Animation, Audio, AudioGObject
from .global_state import GlobalVariable, GlobalVariableGObject
from .verb import Verb, VerbGObject
from .interaction import Interaction, InteractionGObject
from .ui import Font, FontGObject, UIElement, UILayout, UILayoutGObject
from .quest import Quest, QuestGObject, Objective, ObjectiveGObject
from .search import SearchResult, SearchResultGObject
from .project_data import ProjectData
