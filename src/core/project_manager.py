"""Core component for managing AdvEngine project data.

This module provides the ProjectManager class, which is the central hub for
all project data. It is responsible for loading, saving, and providing access
to all project data, as well as managing the "dirty" state of the project.
"""

import os
import sys
import csv
import json
from dataclasses import asdict
from .data_schemas import (
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
    Font,
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

    def load_project(self):
        """Loads all project data from files into memory.

        This method reads all of the project's data files (both CSV and JSON)
        and populates the `self.data` attribute with the loaded data. It is
        called once when a project is opened.
        """
        self._load_csv("ItemData.csv", Item, self.data.items)
        self._load_csv("Attributes.csv", Attribute, self.data.attributes)
        self._load_csv("CharacterData.csv", Character, self.data.characters)
        self._load_scenes()
        self._load_logic_graphs()
        self._load_assets()
        self._load_audio()
        self._load_global_variables()
        self._load_verbs()
        self._load_dialogue_graphs()
        self._load_interactions()
        self._load_quests()
        self._load_ui_layouts()
        self._load_fonts()
        self.is_new_project = False
        self.set_dirty(False)
        self._notify_project_loaded()

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

    def save_project(self):
        """Saves all project data from memory to their respective files.

        This method writes all data from the `self.data` attribute to the
        project's data files. It is called when the user saves the project.
        """
        self._save_csv("ItemData.csv", self.data.items, Item)
        self._save_csv("Attributes.csv", self.data.attributes, Attribute)
        self._save_global_variables()
        self._save_verbs()
        self._save_interactions()
        self._save_scenes()
        self._save_logic_graphs()
        self._save_assets()
        self._save_audio()
        self._save_characters()
        self._save_dialogue_graphs()
        self._save_quests()
        self._save_ui_layouts()
        self._save_fonts()
        self.set_dirty(False)

    def register_dirty_state_callback(self, callback: callable):
        """Registers a callback to be called when the dirty state changes.

        Args:
            callback (callable): A callable that takes a single boolean argument,
                which is the new dirty state.
        """
        self.dirty_state_changed_callbacks.append(callback)

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
        file_path = os.path.join(self.project_path, "Data", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w", newline="") as f:
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
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_csv(self, filename: str, dataclass_type: type, target_list: list):
        """Loads data from a CSV file into a list of dataclass objects.

        Args:
            filename (str): The name of the CSV file.
            dataclass_type (type): The type of the dataclass objects to create.
            target_list (list): The list to which the loaded objects will be appended.
        """
        file_path = os.path.join(self.project_path, "Data", filename)
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key, value in row.items():
                        field_type = dataclass_type.__annotations__.get(key)
                        if field_type == int:
                            row[key] = int(value)
                        elif field_type == bool:
                            row[key] = value.lower() in ["true", "1"]
                    target_list.append(dataclass_type(**row))
        except FileNotFoundError:
            if not self.is_new_project:
                print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _load_json(self, filename: str, target_list: list, object_hook: callable = None):
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
                    return
                data = json.loads(content)
                if object_hook:
                    for item_data in data:
                        target_list.append(object_hook(item_data))
                else:
                    target_list.extend(data)
        except FileNotFoundError:
            if not self.is_new_project:
                print(f"Warning: {file_path} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _save_json(self, filename: str, data_list: list):
        """Saves a list of dataclass objects to a JSON file.

        Args:
            filename (str): The path to the JSON file, relative to the project root.
            data_list (list): A list of dataclass objects to save.
        """
        file_path = os.path.join(self.project_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([asdict(item) for item in data_list], f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_scenes(self):
        """Loads scenes from Logic/Scenes.json."""
        def scene_object_hook(data):
            hotspots = [Hotspot(**hs) for hs in data.get("hotspots", [])]
            data["hotspots"] = hotspots
            return Scene(**data)
        self._load_json(os.path.join("Logic", "Scenes.json"), self.data.scenes, scene_object_hook)

    def _save_scenes(self):
        """Saves scenes to Logic/Scenes.json."""
        self._save_json(os.path.join("Logic", "Scenes.json"), self.data.scenes)

    def _load_graph_data(self, file_path, target_list):
        """Loads graph data from a JSON file.

        Args:
            file_path (str): The path to the JSON file.
            target_list (list): The list to which the loaded objects will be appended.
        """
        def pascal_to_snake(name):
            import re
            name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
            return "var_name" if name == "varname" else name

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
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([asdict(graph) for graph in graph_list], f, indent=4)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_logic_graphs(self):
        """Loads logic graphs from Logic/LogicGraphs.json."""
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        self._load_graph_data(file_path, self.data.logic_graphs)

    def _save_logic_graphs(self):
        """Saves logic graphs to Logic/LogicGraphs.json."""
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        self._save_graph_data(file_path, self.data.logic_graphs)

    def _load_dialogue_graphs(self):
        """Loads dialogue graphs from Logic/DialogueGraphs.json."""
        file_path = os.path.join(self.project_path, "Logic", "DialogueGraphs.json")
        self._load_graph_data(file_path, self.data.dialogue_graphs)

    def _save_dialogue_graphs(self):
        """Saves dialogue graphs to Logic/DialogueGraphs.json."""
        file_path = os.path.join(self.project_path, "Logic", "DialogueGraphs.json")
        self._save_graph_data(file_path, self.data.dialogue_graphs)

    def _load_assets(self):
        """Loads assets from Data/Assets.json."""
        def asset_object_hook(data):
            return Animation(**data) if data.get("asset_type") == "animation" else Asset(**data)
        self._load_json(os.path.join("Data", "Assets.json"), self.data.assets, asset_object_hook)

    def _save_assets(self):
        """Saves assets to Data/Assets.json."""
        self._save_json(os.path.join("Data", "Assets.json"), self.data.assets)

    def _load_audio(self):
        """Loads audio files from Data/Audio.json."""
        self._load_json(os.path.join("Data", "Audio.json"), self.data.audio_files, lambda data: Audio(**data))

    def _save_audio(self):
        """Saves audio files to Data/Audio.json."""
        self._save_json(os.path.join("Data", "Audio.json"), self.data.audio_files)

    def _load_global_variables(self):
        """Loads global variables from Data/GlobalState.json."""
        self._load_json(os.path.join("Data", "GlobalState.json"), self.data.global_variables, lambda data: GlobalVariable(**data))

    def _save_global_variables(self):
        """Saves global variables to Data/GlobalState.json."""
        self._save_json(os.path.join("Data", "GlobalState.json"), self.data.global_variables)

    def _load_verbs(self):
        """Loads verbs from Data/Verbs.json."""
        self._load_json(os.path.join("Data", "Verbs.json"), self.data.verbs, lambda data: Verb(**data))

    def _save_verbs(self):
        """Saves verbs to Data/Verbs.json."""
        self._save_json(os.path.join("Data", "Verbs.json"), self.data.verbs)

    def _save_characters(self):
        """Saves characters to Data/CharacterData.csv."""
        self._save_csv("CharacterData.csv", self.data.characters, Character)

    def _load_interactions(self):
        """Loads interactions from Logic/Interactions.json."""
        self._load_json(os.path.join("Logic", "Interactions.json"), self.data.interactions, lambda data: Interaction(**data))

    def _save_interactions(self):
        """Saves interactions to Logic/Interactions.json."""
        self._save_json(os.path.join("Logic", "Interactions.json"), self.data.interactions)

    def _load_quests(self):
        """Loads quests from Logic/Quests.json."""
        def quest_object_hook(data):
            objectives = [Objective(**obj) for obj in data.get("objectives", [])]
            data["objectives"] = objectives
            return Quest(**data)
        self._load_json(os.path.join("Logic", "Quests.json"), self.data.quests, quest_object_hook)

    def _save_quests(self):
        """Saves quests to Logic/Quests.json."""
        self._save_json(os.path.join("Logic", "Quests.json"), self.data.quests)

    def _load_ui_layouts(self):
        """Loads UI layouts from UI/WindowLayout.json."""
        def ui_layout_object_hook(data):
            elements = [UIElement(**elem) for elem in data.get("elements", [])]
            data["elements"] = elements
            return UILayout(**data)
        self._load_json(os.path.join("UI", "WindowLayout.json"), self.data.ui_layouts, ui_layout_object_hook)

    def _save_ui_layouts(self):
        """Saves UI layouts to UI/WindowLayout.json."""
        self._save_json(os.path.join("UI", "WindowLayout.json"), self.data.ui_layouts)

    def _load_fonts(self):
        """Loads fonts from Data/Fonts.json."""
        self._load_json(os.path.join("Data", "Fonts.json"), self.data.fonts, lambda data: Font(**data))

    def _save_fonts(self):
        """Saves fonts to Data/Fonts.json."""
        self._save_json(os.path.join("Data", "Fonts.json"), self.data.fonts)

    def add_item(self, item: Item):
        """Adds a new item to the project."""
        self.data.items.append(item)
        self.set_dirty()

    def remove_item(self, item: Item):
        """Removes an item from the project."""
        if item in self.data.items:
            self.data.items.remove(item)
            self.set_dirty()
            return True
        return False

    def add_attribute(self, attribute: Attribute):
        """Adds a new attribute to the project."""
        self.data.attributes.append(attribute)
        self.set_dirty()

    def remove_attribute(self, attribute: Attribute):
        """Removes an attribute from the project."""
        if attribute in self.data.attributes:
            self.data.attributes.remove(attribute)
            self.set_dirty()
            return True
        return False

    def add_character(self, character: Character):
        """Adds a new character to the project."""
        self.data.characters.append(character)
        self.set_dirty()

    def remove_character(self, character: Character):
        """Removes a character from the project."""
        if character in self.data.characters:
            self.data.characters.remove(character)
            self.set_dirty()
            return True
        return False

    def add_global_variable(self, variable: GlobalVariable):
        """Adds a new global variable to the project."""
        self.data.global_variables.append(variable)
        self.set_dirty()

    def remove_global_variable(self, variable: GlobalVariable):
        """Removes a global variable from the project."""
        if variable in self.data.global_variables:
            self.data.global_variables.remove(variable)
            self.set_dirty()
            return True
        return False

    def add_verb(self, verb: Verb):
        """Adds a new verb to the project."""
        self.data.verbs.append(verb)
        self.set_dirty()

    def remove_verb(self, verb: Verb):
        """Removes a verb from the project."""
        if verb in self.data.verbs:
            self.data.verbs.remove(verb)
            self.set_dirty()
            return True
        return False

    def add_interaction(self, interaction: Interaction):
        """Adds a new interaction to the project."""
        self.data.interactions.append(interaction)
        self.set_dirty()

    def remove_interaction(self, interaction: Interaction):
        """Removes an interaction from the project."""
        if interaction in self.data.interactions:
            self.data.interactions.remove(interaction)
            self.set_dirty()

    def add_quest(self, quest: Quest):
        """Adds a new quest to the project."""
        self.data.quests.append(quest)
        self.set_dirty()

    def remove_quest(self, quest: Quest):
        """Removes a quest from the project."""
        if quest in self.data.quests:
            self.data.quests.remove(quest)
            self.set_dirty()

    def add_dialogue_graph(self, graph: LogicGraph):
        """Adds a new dialogue graph to the project."""
        self.data.dialogue_graphs.append(graph)
        self.set_dirty()

    def remove_dialogue_graph(self, graph: LogicGraph):
        """Removes a dialogue graph from the project."""
        if graph in self.data.dialogue_graphs:
            self.data.dialogue_graphs.remove(graph)
            self.set_dirty()

    def add_ui_layout(self, layout: UILayout):
        """Adds a new UI layout to the project."""
        self.data.ui_layouts.append(layout)
        self.set_dirty()

    def remove_ui_layout(self, layout: UILayout):
        """Removes a UI layout from the project."""
        if layout in self.data.ui_layouts:
            self.data.ui_layouts.remove(layout)
            self.set_dirty()

    def add_font(self, font: Font):
        """Adds a new font to the project."""
        self.data.fonts.append(font)
        self.set_dirty()

    def remove_font(self, font: Font):
        """Removes a font from the project."""
        if font in self.data.fonts:
            self.data.fonts.remove(font)
            self.set_dirty()

    @staticmethod
    def get_templates():
        """Returns a list of available project templates."""
        local_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        installed_path = os.path.join(sys.prefix, 'share', 'advengine', 'templates')
        template_dir = installed_path if os.path.exists(installed_path) else local_path

        if template_dir and os.path.exists(template_dir):
            return [d for d in os.listdir(template_dir) if os.path.isdir(os.path.join(template_dir, d))]
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
            if template and template != "Blank":
                local_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", template)
                installed_path = os.path.join(sys.prefix, "share", "advengine", "templates", template)
                template_dir = installed_path if os.path.exists(installed_path) else local_path

                if template_dir:
                    import shutil
                    shutil.copytree(template_dir, project_path, dirs_exist_ok=True)
                else:
                    return None, f"Template '{template}' not found."
            else:
                # Create a blank project
                for subdir in ["Data", "Logic", "UI"]:
                    os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

                # Create CSV files
                csv_files = {
                    "ItemData.csv": ["id", "name", "description", "type", "buy_price", "sell_price"],
                    "Attributes.csv": ["id", "name", "initial_value", "max_value"],
                    "CharacterData.csv": ["id", "display_name", "dialogue_start_id", "is_merchant", "shop_id", "portrait_asset_id", "sprite_sheet_asset_id", "animations"],
                }
                for filename, headers in csv_files.items():
                    with open(os.path.join(project_path, "Data", filename), "w", newline="") as f:
                        csv.writer(f).writerow(headers)

                # Add a default player character
                with open(os.path.join(project_path, "Data", "CharacterData.csv"), "a", newline="") as f:
                    csv.writer(f).writerow(["player", "Player", "", "False", "", "", "", "{}"])

                # Create JSON files
                default_verbs = [{"id": f, "name": f.replace("_", " ").title()} for f in ["walk_to", "look_at", "take", "use", "talk_to", "open", "close", "push", "pull"]]
                default_global_vars = [{"id": "score", "name": "Score", "type": "int", "initial_value": 0, "category": "Default"}]
                json_files = {
                    os.path.join("Data", "Assets.json"): [],
                    os.path.join("Data", "Audio.json"): [],
                    os.path.join("Data", "GlobalState.json"): default_global_vars,
                    os.path.join("Data", "Verbs.json"): default_verbs,
                    os.path.join("Data", "Fonts.json"): [],
                    os.path.join("Logic", "Scenes.json"): [],
                    os.path.join("Logic", "LogicGraphs.json"): [],
                    os.path.join("Logic", "DialogueGraphs.json"): [],
                    os.path.join("Logic", "Interactions.json"): [],
                    os.path.join("Logic", "Quests.json"): [],
                    os.path.join("UI", "WindowLayout.json"): [],
                }
                for file_path, default_content in json_files.items():
                    with open(os.path.join(project_path, file_path), "w") as f:
                        json.dump(default_content, f, indent=2)

            project_manager = ProjectManager(project_path)
            project_manager.is_new_project = True
            return project_manager, None
        except Exception as e:
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
                if query_lower in getattr(item, name_field).lower() or query_lower in item.id.lower():
                    results.append(SearchResult(id=item.id, name=getattr(item, name_field), type=data_type))
        return results
