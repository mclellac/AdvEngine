"""Defines the main ProjectData container."""

from dataclasses import dataclass, field
from typing import List

from .attribute import Attribute
from .asset import Asset, Audio
from .character import Character
from .global_state import GlobalVariable
from .interaction import Interaction
from .item import Item
from .logic import LogicGraph
from .quest import Quest
from .scene import Scene
from .ui import UILayout, Font
from .verb import Verb


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
    ui_layouts: List[UILayout] = field(default_factory=list)
    fonts: List[Font] = field(default_factory=list)
