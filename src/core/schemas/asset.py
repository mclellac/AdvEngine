"""Defines data schemas for game assets.

This module includes schemas for generic assets, animations, and audio files.
"""

import gi

gi.require_version("Gtk", "4.0")
from dataclasses import dataclass, field
from typing import List
from .gobject_factory import create_gobject_wrapper


@dataclass
class Asset:
    """Represents a generic game asset that can be loaded from a file.

    Attributes:
        id (str): The unique identifier for the asset.
        name (str): The display name of the asset.
        asset_type (str): The type of the asset (e.g., "image", "audio").
        file_path (str): The path to the asset file, relative to the project's
            Assets/ directory.
    """

    id: str
    name: str
    asset_type: str
    file_path: str


AssetGObject = create_gobject_wrapper(Asset)


@dataclass
class Animation(Asset):
    """Represents an animated asset, inheriting from the base Asset class.

    Attributes:
        frame_count (int): The total number of frames in the animation.
        frame_rate (int): The playback speed of the animation in frames per
            second.
        frames (List[str]): A list of file paths for each frame of the
            animation.
    """

    frame_count: int
    frame_rate: int
    frames: List[str] = field(default_factory=list)


@dataclass
class Audio(Asset):
    """Represents an audio asset, inheriting from the base Asset class.

    Attributes:
        duration (float): The length of the audio clip in seconds.
    """

    duration: float


AudioGObject = create_gobject_wrapper(Audio)
