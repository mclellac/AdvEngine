"""
Handles loading, saving, and managing all project data.
"""

import os
import csv
import json
from dataclasses import asdict
from .data_schemas import (
    ProjectData, Item, Attribute, Character, Scene, Hotspot,
    LogicGraph, LogicNode, DialogueNode, ConditionNode, ActionNode,
    Asset, Animation, Audio
)

class ProjectManager:
    def __init__(self, project_path):
        self.project_path = project_path
        self.data = ProjectData()

    def load_project(self):
        self._load_csv("ItemData.csv", Item, self.data.items)
        self._load_csv("Attributes.csv", Attribute, self.data.attributes)
        self._load_csv("CharacterData.csv", Character, self.data.characters)
        self._load_scenes()
        self._load_logic_graphs()
        self._load_assets()
        self._load_audio()

    def save_project(self):
        if self.data.scenes:
            self._save_scenes()
        if self.data.logic_graphs:
            self._save_logic_graphs()
        if self.data.assets:
            self._save_assets()
        if self.data.audio_files:
            self._save_audio()

    def _load_csv(self, filename, dataclass_type, target_list):
        file_path = os.path.join(self.project_path, "Data", filename)
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Coerce types for dataclass compatibility
                    for key, value in row.items():
                        field_type = dataclass_type.__annotations__.get(key)
                        if field_type == int:
                            row[key] = int(value)
                        elif field_type == bool:
                            row[key] = value.lower() in ['true', '1']
                    target_list.append(dataclass_type(**row))
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _load_scenes(self):
        file_path = os.path.join(self.project_path, "Logic", "Scenes.json")
        try:
            with open(file_path, "r") as f:
                scenes_data = json.load(f)
                for scene_data in scenes_data:
                    hotspots = [Hotspot(**hs) for hs in scene_data.get("hotspots", [])]
                    scene_data["hotspots"] = hotspots
                    self.data.scenes.append(Scene(**scene_data))
        except FileNotFoundError:
            print(f"Warning: {file_path} not found. Starting with an empty scene list.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _save_scenes(self):
        file_path = os.path.join(self.project_path, "Logic", "Scenes.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([asdict(scene) for scene in self.data.scenes], f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_logic_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        try:
            with open(file_path, "r") as f:
                graphs_data = json.load(f)
                for graph_data in graphs_data:
                    nodes = []
                    for node_data in graph_data.get("nodes", []):
                        node_type = node_data.get("node_type")
                        if node_type == "Dialogue":
                            nodes.append(DialogueNode(**node_data))
                        elif node_type == "Condition":
                            nodes.append(ConditionNode(**node_data))
                        elif node_type == "Action":
                            nodes.append(ActionNode(**node_data))
                        else:
                            nodes.append(LogicNode(**node_data))
                    graph_data["nodes"] = nodes
                    self.data.logic_graphs.append(LogicGraph(**graph_data))
        except FileNotFoundError:
            print(f"Warning: {file_path} not found. Starting with an empty logic graph list.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _save_logic_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([asdict(graph) for graph in self.data.logic_graphs], f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_assets(self):
        file_path = os.path.join(self.project_path, "Data", "Assets.json")
        try:
            with open(file_path, "r") as f:
                assets_data = json.load(f)
                for asset_data in assets_data:
                    if asset_data.get("asset_type") == "animation":
                        self.data.assets.append(Animation(**asset_data))
                    else:
                        self.data.assets.append(Asset(**asset_data))
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")

    def _save_assets(self):
        file_path = os.path.join(self.project_path, "Data", "Assets.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump([asdict(asset) for asset in self.data.assets], f, indent=2)

    def _load_audio(self):
        file_path = os.path.join(self.project_path, "Data", "Audio.json")
        try:
            with open(file_path, "r") as f:
                self.data.audio_files = [Audio(**audio_data) for audio_data in json.load(f)]
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")

    def _save_audio(self):
        file_path = os.path.join(self.project_path, "Data", "Audio.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump([asdict(audio) for audio in self.data.audio_files], f, indent=2)

    def create_scene(self, name):
        new_id = f"scene_{len(self.data.scenes) + 1}"
        new_scene = Scene(id=new_id, name=name)
        self.data.scenes.append(new_scene)
        self.save_project()
        return new_scene

    def delete_scene(self, scene_id):
        self.data.scenes = [s for s in self.data.scenes if s.id != scene_id]
        self.save_project()

    def add_hotspot_to_scene(self, scene_id, name, x, y, width, height):
        for scene in self.data.scenes:
            if scene.id == scene_id:
                new_hotspot_id = f"hs_{len(scene.hotspots) + 1}"
                new_hotspot = Hotspot(id=new_hotspot_id, name=name, x=x, y=y, width=width, height=height)
                scene.hotspots.append(new_hotspot)
                self.save_project()
                return new_hotspot
        return None

    @staticmethod
    def create_project(project_path):
        """
        Creates the directory structure and empty data files for a new project.
        """
        try:
            # Create base directories
            data_dir = os.path.join(project_path, "Data")
            logic_dir = os.path.join(project_path, "Logic")
            ui_dir = os.path.join(project_path, "UI")
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(logic_dir, exist_ok=True)
            os.makedirs(ui_dir, exist_ok=True)

            # Create CSV files with headers
            csv_files = {
                "ItemData.csv": ["id", "name", "description", "type", "buy_price", "sell_price"],
                "Attributes.csv": ["id", "name", "initial_value", "max_value"],
                "CharacterData.csv": ["id", "display_name", "dialogue_start_id", "is_merchant", "shop_id"],
            }
            for filename, headers in csv_files.items():
                file_path = os.path.join(data_dir, filename)
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

            # Create empty JSON files
            json_files = [
                os.path.join(data_dir, "Assets.json"),
                os.path.join(data_dir, "Audio.json"),
                os.path.join(logic_dir, "Scenes.json"),
                os.path.join(logic_dir, "LogicGraphs.json"),
                os.path.join(ui_dir, "WindowLayout.json"),
            ]
            for file_path in json_files:
                with open(file_path, "w") as f:
                    json.dump([], f)

            return True, None
        except Exception as e:
            return False, str(e)
