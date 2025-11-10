"""Defines data schemas for quests and objectives."""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import List
from .gobject_factory import create_gobject_wrapper


@dataclass
class Objective:
    """Represents a single objective in a quest."""

    id: str
    name: str
    completed: bool = False


ObjectiveGObject = create_gobject_wrapper(Objective)


@dataclass
class Quest:
    """Represents a quest."""

    id: str
    name: str
    objectives: List[Objective] = field(default_factory=list)


QuestGObject = create_gobject_wrapper(Quest)
