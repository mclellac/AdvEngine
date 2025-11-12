"""Core component for managing AdvEngine project data.

This module provides the ProjectManager class, which is the central hub for
all project data. It is responsible for loading, saving, and providing access
to all project data, as well as managing the "dirty" state of the project.
"""

import os
import sys
import csv
import json
import logging
import tempfile
import shutil
from dataclasses import asdict
from .schemas import (
    ProjectData,
    Item,
    Attribute,
    Character,
    Scene,
    Hotspot,
    LogicGraph,
    LogicNode,
    DialogueNode,
    ConditionNode,
    ActionNode,
    Asset,
    Animation,
    Audio,
    GlobalVariable,
    Verb,
    Interaction,
    Quest,
    Objective,
    UILayout,
    UIElement,
    SearchResult,
)
from .settings_manager import SettingsManager


class ProjectManager:
    """Manages all data for a single AdvEngine project.

    This class is responsible for all project-related data management,
    including loading data from files, saving data to files, and providing

    access to the data to the rest of the application. It also tracks the
    "dirty" state of the project, which is used to determine if there are
    unsaved changes.

    Attributes:
        project_path (str): The absolute path to the project directory.
        data (ProjectData): A dataclass containing all project data.
        settings (SettingsManager): Manages project-specific settings.
        is_dirty (bool): True if the project has unsaved changes.
        is_new_project (bool): True if the project was just created.
    """

    def __init__(self, project_path: str):
        """Initializes a new ProjectManager instance.

        Args:
            project_path (str): The absolute path to the project directory.
        """
        self.project_path = project_path
        self.data = ProjectData()
        self.settings = SettingsManager(project_path)
        self.is_dirty = False
        self.is_new_project = False
        self.dirty_state_changed_callbacks = []
        self.project_loaded_callbacks = []
        self.error_callbacks = []
        self.project_saved_callbacks = []

        self._data_files = {
            "items": ("Data/ItemData.csv", Item, self._load_csv, self._save_csv),
            "attributes": (
                "Data/Attributes.csv",
                Attribute,
                self._load_csv,
                self._save_csv,
            ),
            "characters": (
                "Data/CharacterData.csv",
                Character,
                self._load_csv,
                self._save_csv,
            ),
            "scenes": (
                "Logic/Scenes.json",
                Scene,
                self._load_json,
                self._save_json,
                self._scene_object_hook,
            ),
            "logic_graphs": (
                "Logic/LogicGraphs.json",
                LogicGraph,
                self._load_graph_data,
                self._save_graph_data,
            ),
            "assets": (
                "Data/Assets.json",
                Asset,
                self._load_json,
                self._save_json,
                self._asset_object_hook,
            ),
            "audio_files": (
                "Data/Audio.json",
                Audio,
                self._load_json,
                self._save_json,
                lambda data: Audio(**data),
            ),
            "global_variables": (
                "Data/GlobalState.json",
                GlobalVariable,
                self._load_json,
                self._save_json,
                lambda data: GlobalVariable(**data),
            ),
            "verbs": (
                "Data/Verbs.json",
                Verb,
                self._load_json,
                self._save_json,
                lambda data: Verb(**data),
            ),
            "dialogue_graphs": (
                "Logic/DialogueGraphs.json",
                LogicGraph,
                self._load_graph_data,
                self._save_graph_data,
            ),
            "interactions": (
                "Logic/Interactions.json",
                Interaction,
                self._load_json,
                self._save_json,
                lambda data: Interaction(**data),
            ),
            "quests": (
                "Logic/Quests.json",
                Quest,
                self._load_json,
                self._save_json,
                self._quest_object_hook,
            ),
            "ui_layouts": (
                "UI/WindowLayout.json",
                UILayout,
                self._load_json,
                self._save_json,
                self._ui_layout_object_hook,
            ),
        }

    def load_project(self):
        """Loads all project data from files into memory.

        This method reads all of the project's data files (both CSV and JSON)
        and populates the `self.data` attribute with the loaded data. It is
        called once when a project is opened.
        """
        # Clear existing data to ensure a clean load
        for key in self._data_files:
            getattr(self.data, key).clear()

        for key, config in self._data_files.items():
            loader = config[2]
            target_list = getattr(self.data, key)
            if len(config) > 4:  # Has object hook
                loader(config[0], target_list, config[4])
            elif loader == self._load_csv:
                loader(config[0], config[1], target_list)
            else:
                loader(config[0], target_list)

        self.is_new_project = False
        self.set_dirty(False)
        self._notify_project_loaded()

    def save_project(self):
        """Saves all project data from memory to their respective files.

        This method writes all data from the `self.data` attribute to the
        project's data files. It is called when the user saves the project.
        """
        for key, config in self._data_files.items():
            saver = config[3]
            data_list = getattr(self.data, key)
            if saver == self._save_csv:
                saver(config[0], data_list, config[1])
            else:
                saver(config[0], data_list)
        self.set_dirty(False)
        self._notify_project_saved()

    def register_project_saved_callback(self, callback: callable):
        """Registers a callback to be called when the project is saved."""
        self.project_saved_callbacks.append(callback)

    def _notify_project_saved(self):
        """Notifies all registered callbacks that the project has been saved."""
        for callback in self.project_saved_callbacks:
            callback()

    def register_project_loaded_callback(self, callback: callable):
        """Registers a callback to be called when the project is loaded.

        Args:
            callback (callable): A callable that takes no arguments.
        """
        self.project_loaded_callbacks.append(callback)

    def _notify_project_loaded(self):
        """Notifies all registered callbacks that the project has been loaded."""
        for callback in self.project_loaded_callbacks:
            callback()

    def register_dirty_state_callback(self, callback: callable):
        """Registers a callback to be called when the dirty state changes.

        Args:
            callback (callable): A callable that takes a single boolean argument,
                which is the new dirty state.
        """
        self.dirty_state_changed_callbacks.append(callback)

    def register_error_callback(self, callback: callable):
        """Registers a callback to be called when a critical error occurs.

        Args:
            callback (callable): A callable that takes two string arguments,
                which are the title and message of the error.
        """
        self.error_callbacks.append(callback)

    def _notify_error(self, title: str, message: str):
        """Notifies all registered error callbacks.

        Args:
            title (str): The title of the error.
            message (str): The message of the error.
        """
        for callback in self.error_callbacks:
            callback(title, message)

    def _notify_dirty_state_changed(self):
        """Notifies all registered callbacks of a change in the dirty state."""
        for callback in self.dirty_state_changed_callbacks:
            callback(self.is_dirty)

    def set_dirty(self, state: bool = True):
        """Sets the project's dirty state and notifies listeners.

        This method should be called whenever any data in the project is
        modified.

        Args:
            state (bool): The new dirty state. Defaults to True.
        """
        if self.is_dirty != state:
            self.is_dirty = state
            self._notify_dirty_state_changed()

    def _save_csv(self, filename: str, data_list: list, dataclass_type: type):
        """Saves a list of dataclass objects to a CSV file.

        Args:
            filename (str): The name of the CSV file.
            data_list (list): A list of dataclass objects to save.
            dataclass_type (type): The type of the dataclass objects.
        """
        file_path = os.path.join(self.project_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=os.path.dirname(file_path)
        )
        try:
            with temp_file as f:
                if not data_list:
                    fieldnames = asdict(
                        dataclass_type(*[None] * len(dataclass_type.__annotations__))
                    ).keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                else:
                    writer = csv.DictWriter(f, fieldnames=asdict(data_list[0]).keys())
                    writer.writeheader()
                    for item in data_list:
                        writer.writerow(asdict(item))
            shutil.move(temp_file.name, file_path)
        except (IOError, csv.Error) as e:
            logging.error(f"Error saving {file_path}: {e}")
            self._notify_error(
                f"Failed to Save {filename}",
                f"Could not write to file at {file_path}.\n\n{e}",
            )
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    def _load_csv(self, filename: str, dataclass_type: type, target_list: list):
        """Loads data from a CSV file into a list of dataclass objects.

        Args:
            filename (str): The name of the CSV file.
            dataclass_type (type): The type of the dataclass objects to create.
            target_list (list): The list to which the loaded objects will be appended.
        """
        file_path = os.path.join(self.project_path, filename)
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    for key, value in row.items():
                        field_type = dataclass_type.__annotations__.get(key)
                        if field_type == int:
                            row[key] = int(value) if value else 0
                        elif field_type == bool:
                            row[key] = value.lower() in ["true", "1"]
                        elif field_type == dict:
                            row[key] = json.loads(value) if value else {}
                    new_item = dataclass_type(**row)
                    target_list.append(new_item)
                    logging.debug(f"  Created object: {new_item}")
                    count += 1
                logging.debug(f"Loaded {count} items from {filename}")
        except FileNotFoundError:
            if not self.is_new_project:
                logging.warning(f"Warning: {file_path} not found.")
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
            self._notify_error(
                f"Failed to Load {filename}",
                f"Could not read file at {file_path}.\n\n{e}",
            )

    def _load_json(
        self, filename: str, target_list: list, object_hook: callable = None
    ):
        """Loads data from a JSON file.

        Args:
            filename (str): The path to the JSON file, relative to the project root.
            target_list (list): The list to which the loaded objects will be appended.
            object_hook (callable): An optional function to process each loaded object.
        """
        file_path = os.path.join(self.project_path, filename)
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if not content:
                    logging.debug(f"File {filename} is empty.")
                    return
                data = json.loads(content)
                count = 0
                if object_hook:
                    for item_data in data:
                        new_item = object_hook(item_data)
                        target_list.append(new_item)
                        logging.debug(f"  Created object: {new_item}")
                        count += 1
                else:
                    target_list.extend(data)
                    count = len(data)
                logging.debug(f"Loaded {count} items from {filename}")
        except FileNotFoundError:
            if not self.is_new_project:
                logging.warning(f"Warning: {file_path} not found.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {file_path}: {e}")
            self._notify_error(
                f"Failed to Load {filename}",
                f"Could not parse JSON from {file_path}.\n\n{e}",
            )
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
            self._notify_error(
                f"Failed to Load {filename}",
                f"An unexpected error occurred while reading {file_path}.\n\n{e}",
            )

    def _save_json(self, filename: str, data_list: list):
        """Saves a list of dataclass objects to a JSON file.

        Args:
            filename (str): The path to the JSON file, relative to the project root.
            data_list (list): A list of dataclass objects to save.
        """
        file_path = os.path.join(self.project_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=os.path.dirname(file_path)
        )
        try:
            with temp_file as f:
                json.dump([asdict(item) for item in data_list], f, indent=2)
            shutil.move(temp_file.name, file_path)
        except (IOError, TypeError) as e:
            logging.error(f"Error saving {file_path}: {e}")
            self._notify_error(
                f"Failed to Save {filename}",
                f"Could not write to file at {file_path}.\n\n{e}",
            )
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    def _scene_object_hook(self, data):
        """Object hook for loading scenes from JSON."""
        hotspots = [Hotspot(**hs) for hs in data.get("hotspots", [])]
        data["hotspots"] = hotspots
        return Scene(**data)

    def _quest_object_hook(self, data):
        """Object hook for loading quests from JSON."""
        objectives = [Objective(**obj) for obj in data.get("objectives", [])]
        data["objectives"] = objectives
        return Quest(**data)

    def _ui_layout_object_hook(self, data):
        """Object hook for loading UI layouts from JSON."""
        elements = [UIElement(**elem) for elem in data.get("elements", [])]
        data["elements"] = elements
        return UILayout(**data)

    def _asset_object_hook(self, data):
        """Object hook for loading assets from JSON."""
        return (
            Animation(**data)
            if data.get("asset_type") == "animation"
            else Asset(**data)
        )

    def _load_graph_data(self, file_path, target_list):
        """Loads graph data from a JSON file.

        Args:
            file_path (str): The path to the JSON file.
            target_list (list): The list to which the loaded objects will be appended.
        """

        def graph_object_hook(data):
            nodes = []
            for node_data in data.get("nodes", []):
                node_data.pop("parent_id", None)
                node_data.pop("children_ids", None)
                node_type = node_data.get("node_type")
                if "parameters" in node_data:
                    for key, value in node_data["parameters"].items():
                        snake_key = pascal_to_snake(key)
                        if snake_key not in node_data:
                            node_data[snake_key] = value
                    del node_data["parameters"]

                node_class = {
                    "Dialogue": DialogueNode,
                    "Condition": ConditionNode,
                    "Action": ActionNode,
                }.get(node_type, LogicNode)
                nodes.append(node_class(**node_data))
            data["nodes"] = nodes
            return LogicGraph(**data)

        self._load_json(file_path, target_list, graph_object_hook)

    def _save_graph_data(self, file_path, graph_list):
        """Saves graph data to a JSON file.

        Args:
            file_path (str): The path to the JSON file.
            graph_list (list): A list of LogicGraph objects to save.
        """
        self._save_json(file_path, graph_list)

    def add_data_item(self, collection_name: str, item: object):
        """Adds an item to the specified data collection.

        Args:
            collection_name (str): The name of the collection to add the item to.
            item (object): The item to add to the collection.
        """
        collection = getattr(self.data, collection_name, None)
        if collection is not None:
            collection.append(item)
            self.set_dirty()
        else:
            logging.error(f"Error: Collection '{collection_name}' not found.")

    def remove_data_item(self, collection_name: str, item: object):
        """Removes an item from the specified data collection.

        Args:
            collection_name (str): The name of the collection to remove the item from.
            item (object): The item to remove from the collection.
        """
        collection = getattr(self.data, collection_name, None)
        if collection is not None:
            if item in collection:
                collection.remove(item)
                self.set_dirty()
                return True
            return False
        else:
            logging.error(f"Error: Collection '{collection_name}' not found.")
            return False

    @staticmethod
    def get_templates():
        """Returns a list of available project templates."""
        local_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        installed_path = os.path.join(sys.prefix, "share", "advengine", "templates")
        template_dir = installed_path if os.path.exists(installed_path) else local_path

        if template_dir and os.path.exists(template_dir):
            return [
                d
                for d in os.listdir(template_dir)
                if os.path.isdir(os.path.join(template_dir, d))
            ]
        return []

    @staticmethod
    def create_project(project_path: str, template: str = None):
        """Creates the directory structure and data files for a new project.

        Args:
            project_path (str): The absolute path where the project will be created.
            template (str): The name of an optional project template to use.

        Returns:
            A tuple containing a new ProjectManager instance and an error
            string. If the project is created successfully, the error string
            will be None.
        """
        try:
            if not template:
                return None, "A template must be specified."

            local_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "templates", template
            )
            installed_path = os.path.join(
                sys.prefix, "share", "advengine", "templates", template
            )
            template_dir = (
                installed_path if os.path.exists(installed_path) else local_path
            )

            if not os.path.exists(template_dir):
                return None, f"Template '{template}' not found."

            shutil.copytree(template_dir, project_path, dirs_exist_ok=True)
            logging.debug(f"Copied template '{template}' to '{project_path}'")

            project_manager = ProjectManager(project_path)
            project_manager.is_new_project = True
            project_manager.load_project()
            return project_manager, None
        except Exception as e:
            logging.error(f"Failed to create project from template '{template}': {e}")
            return None, str(e)

    def search(self, query: str) -> list[SearchResult]:
        """Searches all project data for a given query.

        Args:
            query (str): The search term.

        Returns:
            A list of SearchResult objects that match the query.
        """
        results = []
        query_lower = query.lower()

        searchable_data = [
            ("Item", self.data.items, "name"),
            ("Character", self.data.characters, "display_name"),
            ("Scene", self.data.scenes, "name"),
            ("Quest", self.data.quests, "name"),
            ("Asset", self.data.assets, "name"),
        ]

        for data_type, data_list, name_field in searchable_data:
            for item in data_list:
                if (
                    query_lower in getattr(item, name_field).lower()
                    or query_lower in item.id.lower()
                ):
                    results.append(
                        SearchResult(
                            id=item.id, name=getattr(item, name_field), type=data_type
                        )
                    )
        return results
