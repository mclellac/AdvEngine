"""Defines the data schemas for the node-based logic editor."""

from dataclasses import dataclass, field
from typing import List, Optional

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
