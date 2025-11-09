"""Defines data schemas for game assets, including generic assets, animations, and audio."""

import gi
gi.require_version('Gtk', '4.0')
from dataclasses import dataclass, field
from typing import List
from .gobject_factory import create_gobject_wrapper

@dataclass
class Asset:
    """Represents a generic game asset."""
    id: str
    name: str
    asset_type: str
    file_path: str

AssetGObject = create_gobject_wrapper(Asset)

@dataclass
class Animation(Asset):
    """Represents an animated asset."""
    frame_count: int
    frame_rate: int
    frames: List[str] = field(default_factory=list)

@dataclass
class Audio(Asset):
    """Represents an audio asset."""
    duration: float

AudioGObject = create_gobject_wrapper(Audio)
