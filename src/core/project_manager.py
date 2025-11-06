"""Core component for managing AdvEngine project data.

This module provides the ProjectManager class, which is the central hub for
all project data. It is responsible for loading, saving, and providing access
to all project data, as well as managing the "dirty" state of the project.
"""

import os
import csv
import json
from dataclasses import asdict
from .data_schemas import (
    ProjectData, Item, Attribute, Character, Scene, Hotspot,
    LogicGraph, LogicNode, DialogueNode, ConditionNode, ActionNode,
    Asset, Animation, Audio, GlobalVariable, Verb, Cutscene, Interaction,
    Quest, Objective, UILayout, UIElement, Font, SearchResult
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
            project_path: The absolute path to the project directory.
        """
        print(f"DEBUG: ProjectManager.__init__: {project_path}")
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
        print("DEBUG: ProjectManager.load_project: Starting project load.")
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
        self._load_cutscenes()
        self._load_interactions()
        self._load_quests()
        self._load_ui_layouts()
        self._load_fonts()
        self.is_new_project = False
        self.set_dirty(False)  # Project is clean after loading
        print("DEBUG: ProjectManager.load_project: Project load complete.")
        self._notify_project_loaded()

    def register_project_loaded_callback(self, callback: callable):
        """Registers a callback to be called when the project is loaded.

        Args:
            callback: A callable that takes no arguments.
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
        print("DEBUG: ProjectManager.save_project: Starting project save.")
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
        self._save_cutscenes()
        self._save_quests()
        self._save_ui_layouts()
        self._save_fonts()
        self.set_dirty(False)
        print("DEBUG: ProjectManager.save_project: Project save complete.")

    def register_dirty_state_callback(self, callback: callable):
        """Registers a callback to be called when the dirty state changes.

        Args:
            callback: A callable that takes a single boolean argument, which
                is the new dirty state.
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
            state: The new dirty state. Defaults to True.
        """
        if self.is_dirty != state:
            print(f"DEBUG: ProjectManager.set_dirty: Changing dirty state to {state}")
            self.is_dirty = state
            self._notify_dirty_state_changed()

    def _save_csv(self, filename: str, data_list: list, dataclass_type: type):
        """Saves a list of dataclass objects to a CSV file.

        Args:
            filename: The name of the CSV file.
            data_list: A list of dataclass objects to save.
            dataclass_type: The type of the dataclass objects.
        """
        file_path = os.path.join(self.project_path, "Data", filename)
        print(f"DEBUG: ProjectManager._save_csv: Saving to {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w", newline="") as f:
                if not data_list:
                    # Get field names from an empty instance of the dataclass
                    fieldnames = asdict(dataclass_type(
                        *[None] * len(dataclass_type.__annotations__))).keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                else:
                    writer = csv.DictWriter(
                        f, fieldnames=asdict(data_list[0]).keys())
                    writer.writeheader()
                    for item in data_list:
                        writer.writerow(asdict(item))
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_csv(self, filename: str, dataclass_type: type, target_list: list):
        """Loads data from a CSV file into a list of dataclass objects.

        Args:
            filename: The name of the CSV file.
            dataclass_type: The type of the dataclass objects to create.
            target_list: The list to which the loaded objects will be appended.
        """
        file_path = os.path.join(self.project_path, "Data", filename)
        print(f"DEBUG: ProjectManager._load_csv: Loading from {file_path}")
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
            if not self.is_new_project:
                print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _load_json(self, filename: str, target_list: list, object_hook: callable = None):
        """Loads data from a JSON file.

        Args:
            filename: The path to the JSON file, relative to the project root.
            target_list: The list to which the loaded objects will be appended.
            object_hook: An optional function to process each loaded object.
        """
        file_path = os.path.join(self.project_path, filename)
        print(f"DEBUG: ProjectManager._load_json: Loading from {file_path}")
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if object_hook:
                    for item_data in data:
                        target_list.append(object_hook(item_data))
                else:
                    target_list.extend(data)
        except FileNotFoundError:
            if not self.is_new_project:
                print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _save_json(self, filename: str, data_list: list):
        """Saves a list of dataclass objects to a JSON file.

        Args:
            filename: The path to the JSON file, relative to the project root.
            data_list: A list of dataclass objects to save.
        """
        file_path = os.path.join(self.project_path, filename)
        print(f"DEBUG: ProjectManager._save_json: Saving to {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([asdict(item) for item in data_list], f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _load_scenes(self):
        def scene_object_hook(data):
            hotspots = [Hotspot(**hs) for hs in data.get("hotspots", [])]
            data["hotspots"] = hotspots
            return Scene(**data)
        self._load_json(os.path.join("Logic", "Scenes.json"), self.data.scenes, scene_object_hook)

    def _save_scenes(self):
        self._save_json(os.path.join("Logic", "Scenes.json"), self.data.scenes)

    def _load_graph_data(self, file_path, target_list):
        def pascal_to_snake(name):
            import re
            name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            if name == "varname":
                return "var_name"
            return name

        def graph_object_hook(data):
            nodes = []
            for node_data in data.get("nodes", []):
                node_type = node_data.get("node_type")
                if "parameters" in node_data:
                    for key, value in node_data["parameters"].items():
                        snake_key = pascal_to_snake(key)
                        if snake_key not in node_data:
                            node_data[snake_key] = value
                    del node_data["parameters"]

                if node_type == "Dialogue":
                    nodes.append(DialogueNode(**node_data))
                elif node_type == "Condition":
                    nodes.append(ConditionNode(**node_data))
                elif node_type == "Action":
                    nodes.append(ActionNode(**node_data))
                else:
                    nodes.append(LogicNode(**node_data))
            data["nodes"] = nodes
            return LogicGraph(**data)

        self._load_json(file_path, target_list, graph_object_hook)

    def _load_logic_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        self._load_graph_data(file_path, self.data.logic_graphs)

    def _load_dialogue_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "DialogueGraphs.json")
        self._load_graph_data(file_path, self.data.dialogue_graphs)

    def _save_graph_data(self, file_path, graph_list):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump([graph.to_dict() for graph in graph_list], f, indent=4)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _save_logic_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "LogicGraphs.json")
        self._save_graph_data(file_path, self.data.logic_graphs)

    def _load_assets(self):
        def asset_object_hook(data):
            if data.get("asset_type") == "animation":
                return Animation(**data)
            return Asset(**data)
        self._load_json(os.path.join("Data", "Assets.json"), self.data.assets, asset_object_hook)

    def _save_assets(self):
        self._save_json(os.path.join("Data", "Assets.json"), self.data.assets)

    def _load_audio(self):
        self._load_json(os.path.join("Data", "Audio.json"), self.data.audio_files, lambda data: Audio(**data))

    def _save_audio(self):
        self._save_json(os.path.join("Data", "Audio.json"), self.data.audio_files)

    def _load_global_variables(self):
        self._load_json(os.path.join("Data", "GlobalState.json"), self.data.global_variables, lambda data: GlobalVariable(**data))

    def _save_global_variables(self):
        self._save_json(os.path.join("Data", "GlobalState.json"), self.data.global_variables)

    def add_global_variable(self, variable):
        """Adds a new global variable to the project."""
        self.data.global_variables.append(variable)
        self.set_dirty()

    def remove_global_variable(self, variable):
        """Removes a global variable from the project."""
        if variable in self.data.global_variables:
            self.data.global_variables.remove(variable)
            self.set_dirty()
            return True
        return False

    def update_global_variable(self, variable, gobject):
        """Updates a global variable."""
        variable.name = gobject.name
        variable.type = gobject.type
        variable.category = gobject.category
        # Handle type conversion for initial_value
        if gobject.type == "int":
            try:
                variable.initial_value = int(gobject.initial_value_str)
            except ValueError:
                variable.initial_value = 0
        elif gobject.type == "bool":
            variable.initial_value = gobject.initial_value_str.lower() in ['true', '1']
        else:
            variable.initial_value = gobject.initial_value_str
        self.set_dirty()

    def _load_verbs(self):
        self._load_json(os.path.join("Data", "Verbs.json"), self.data.verbs, lambda data: Verb(**data))

    def _save_verbs(self):
        self._save_json(os.path.join("Data", "Verbs.json"), self.data.verbs)

    def _save_characters(self):
        self._save_csv("CharacterData.csv", self.data.characters, Character)

    def add_verb(self, id, name):
        new_verb = Verb(id=id, name=name)
        self.data.verbs.append(new_verb)
        self.set_dirty()
        return new_verb

    def create_scene(self, name):
        new_id = f"scene_{len(self.data.scenes) + 1}"
        new_scene = Scene(id=new_id, name=name)
        self.data.scenes.append(new_scene)
        self.set_dirty()
        return new_scene

    def delete_scene(self, scene_id):
        self.data.scenes = [s for s in self.data.scenes if s.id != scene_id]
        self.set_dirty()

    def add_hotspot_to_scene(self, scene_id, name, x, y, width, height):
        for scene in self.data.scenes:
            if scene.id == scene_id:
                new_hotspot_id = f"hs_{len(scene.hotspots) + 1}"
                new_hotspot = Hotspot(id=new_hotspot_id, name=name, x=x, y=y, width=width, height=height)
                scene.hotspots.append(new_hotspot)
                self.set_dirty()
                return new_hotspot
        return None

    def add_item(self, item):
        """Adds a new item to the project."""
        self.data.items.append(item)
        self.set_dirty()

    def remove_item(self, item):
        """Removes an item from the project."""
        if item in self.data.items:
            self.data.items.remove(item)
            self.set_dirty()
            return True
        return False

    def add_character(self, character):
        """Adds a new character to the project."""
        self.data.characters.append(character)
        self.set_dirty()

    def remove_character(self, character):
        """Removes a character from the project."""
        if character in self.data.characters:
            self.data.characters.remove(character)
            self.set_dirty()
            return True
        return False

    def update_character(self, character_id, new_data):
        """Updates an existing character."""
        for character in self.data.characters:
            if character.id == character_id:
                for key, value in new_data.items():
                    setattr(character, key, value)
                self.set_dirty()
                return True
        return False

    def add_attribute(self, attribute):
        """Adds a new attribute to the project."""
        self.data.attributes.append(attribute)
        self.set_dirty()

    def remove_attribute(self, attribute):
        """Removes an attribute from the project."""
        if attribute in self.data.attributes:
            self.data.attributes.remove(attribute)
            self.set_dirty()
            return True
        return False

    def add_dialogue_graph(self, id, name):
        new_graph = LogicGraph(id=id, name=name)
        self.data.dialogue_graphs.append(new_graph)
        self.set_dirty()
        return new_graph

    def remove_dialogue_graph(self, graph_id):
        self.data.dialogue_graphs = [g for g in self.data.dialogue_graphs if g.id != graph_id]
        self.set_dirty()

    def _load_dialogue_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "DialogueGraphs.json")
        self._load_graph_data(file_path, self.data.dialogue_graphs)

    def _save_dialogue_graphs(self):
        file_path = os.path.join(self.project_path, "Logic", "DialogueGraphs.json")
        self._save_graph_data(file_path, self.data.dialogue_graphs)

    def _load_cutscenes(self):
        self._load_json(os.path.join("Logic", "Cutscenes.json"), self.data.cutscenes, lambda data: Cutscene(**data))

    def _save_cutscenes(self):
        self._save_json(os.path.join("Logic", "Cutscenes.json"), self.data.cutscenes)

    def _load_interactions(self):
        self._load_json(os.path.join("Logic", "Interactions.json"), self.data.interactions, lambda data: Interaction(**data))

    def _save_interactions(self):
        self._save_json(os.path.join("Logic", "Interactions.json"), self.data.interactions)

    def add_interaction(self, interaction):
        self.data.interactions.append(interaction)
        self.set_dirty()

    def remove_interaction(self, interaction):
        if interaction in self.data.interactions:
            self.data.interactions.remove(interaction)
            self.set_dirty()

    def _load_quests(self):
        def quest_object_hook(data):
            objectives = [Objective(**obj) for obj in data.get("objectives", [])]
            data["objectives"] = objectives
            return Quest(**data)
        self._load_json(os.path.join("Logic", "Quests.json"), self.data.quests, quest_object_hook)

    def _save_quests(self):
        self._save_json(os.path.join("Logic", "Quests.json"), self.data.quests)

    def add_quest(self, id, name):
        new_quest = Quest(id=id, name=name)
        self.data.quests.append(new_quest)
        self.set_dirty()
        return new_quest

    def remove_quest(self, quest_id):
        self.data.quests = [q for q in self.data.quests if q.id != quest_id]
        self.set_dirty()

    def update_quest(self, quest_id, new_data):
        for quest in self.data.quests:
            if quest.id == quest_id:
                for key, value in new_data.items():
                    setattr(quest, key, value)
                self.set_dirty()
                return True
        return False

    def add_objective_to_quest(self, quest_id, objective_id, objective_name):
        for quest in self.data.quests:
            if quest.id == quest_id:
                new_objective = Objective(id=objective_id, name=objective_name)
                quest.objectives.append(new_objective)
                self.set_dirty()
                return new_objective
        return None

    def remove_objective_from_quest(self, quest_id, objective_id):
        for quest in self.data.quests:
            if quest.id == quest_id:
                quest.objectives = [obj for obj in quest.objectives if obj.id != objective_id]
                self.set_dirty()
                return True
        return False

    def update_objective(self, quest_id, objective_id, new_data):
        for quest in self.data.quests:
            if quest.id == quest_id:
                for objective in quest.objectives:
                    if objective.id == objective_id:
                        for key, value in new_data.items():
                            setattr(objective, key, value)
                        self.set_dirty()
                        return True
        return False

    def _load_ui_layouts(self):
        def ui_layout_object_hook(data):
            elements = [UIElement(**elem) for elem in data.get("elements", [])]
            data["elements"] = elements
            return UILayout(**data)
        self._load_json(os.path.join("UI", "WindowLayout.json"), self.data.ui_layouts, ui_layout_object_hook)

    def _save_ui_layouts(self):
        self._save_json(os.path.join("UI", "WindowLayout.json"), self.data.ui_layouts)

    def add_ui_layout(self, id, name):
        new_layout = UILayout(id=id, name=name)
        self.data.ui_layouts.append(new_layout)
        self.set_dirty()
        return new_layout

    def remove_ui_layout(self, layout_id):
        self.data.ui_layouts = [layout for layout in self.data.ui_layouts if layout.id != layout_id]
        self.set_dirty()

    def update_ui_layout(self, layout_id, new_data):
        for layout in self.data.ui_layouts:
            if layout.id == layout_id:
                for key, value in new_data.items():
                    setattr(layout, key, value)
                self.set_dirty()
                return True
        return False

    def add_element_to_layout(self, layout_id, element_id, element_type, x, y, width, height):
        for layout in self.data.ui_layouts:
            if layout.id == layout_id:
                new_element = UIElement(id=element_id, type=element_type, x=x, y=y, width=width, height=height)
                layout.elements.append(new_element)
                self.set_dirty()
                return new_element
        return None

    def remove_element_from_layout(self, layout_id, element_id):
        for layout in self.data.ui_layouts:
            if layout.id == layout_id:
                layout.elements = [elem for elem in layout.elements if elem.id != element_id]
                self.set_dirty()
                return True
        return False

    def update_element(self, layout_id, element_id, new_data):
        for layout in self.data.ui_layouts:
            if layout.id == layout_id:
                for element in layout.elements:
                    if element.id == element_id:
                        for key, value in new_data.items():
                            setattr(element, key, value)
                        self.set_dirty()
                        return True
        return False

    def _load_fonts(self):
        self._load_json(os.path.join("Data", "Fonts.json"), self.data.fonts, lambda data: Font(**data))

    def _save_fonts(self):
        self._save_json(os.path.join("Data", "Fonts.json"), self.data.fonts)

    def add_font(self, id, name, file_path):
        new_font = Font(id=id, name=name, file_path=file_path)
        self.data.fonts.append(new_font)
        self.set_dirty()
        return new_font

    def remove_font(self, font_id):
        self.data.fonts = [font for font in self.data.fonts if font.id != font_id]
        self.set_dirty()

    def update_font(self, font_id, new_data):
        for font in self.data.fonts:
            if font.id == font_id:
                for key, value in new_data.items():
                    setattr(font, key, value)
                self.set_dirty()
                return True
        return False

    def export_localization(self, file_path):
        """Exports all user-facing text to a CSV file."""
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Source Text", "Translated Text"])

            for item in self.data.items:
                writer.writerow([f"item_{item.id}_name", item.name, ""])
                writer.writerow([f"item_{item.id}_description", item.description, ""])

            for character in self.data.characters:
                writer.writerow([f"character_{character.id}_display_name", character.display_name, ""])

            for dialogue_node in [node for graph in self.data.dialogue_graphs for node in graph.nodes if isinstance(node, DialogueNode)]:
                writer.writerow([f"dialogue_{dialogue_node.id}_dialogue_text", dialogue_node.dialogue_text, ""])

            for quest in self.data.quests:
                writer.writerow([f"quest_{quest.id}_name", quest.name, ""])
                for objective in quest.objectives:
                    writer.writerow([f"objective_{objective.id}_name", objective.name, ""])

    def import_localization(self, file_path):
        """Imports translated text from a CSV file."""
        with open(file_path, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                id_parts = row[0].split("_")
                text_type = id_parts[0]
                item_id = id_parts[1]
                property_name = id_parts[2]
                translated_text = row[2]

                if text_type == "item":
                    for item in self.data.items:
                        if item.id == item_id:
                            setattr(item, property_name, translated_text)
                elif text_type == "character":
                    for character in self.data.characters:
                        if character.id == item_id:
                            setattr(character, property_name, translated_text)
                elif text_type == "dialogue":
                    for graph in self.data.dialogue_graphs:
                        for node in graph.nodes:
                            if node.id == item_id:
                                setattr(node, property_name, translated_text)
                elif text_type == "quest":
                    for quest in self.data.quests:
                        if quest.id == item_id:
                            setattr(quest, property_name, translated_text)
                elif text_type == "objective":
                    for quest in self.data.quests:
                        for objective in quest.objectives:
                            if objective.id == item_id:
                                setattr(objective, property_name, translated_text)
        self.set_dirty()

    def add_cutscene(self, name):
        new_id = f"cutscene_{len(self.data.cutscenes) + 1}"
        new_cutscene = Cutscene(id=new_id, name=name)
        self.data.cutscenes.append(new_cutscene)
        self.set_dirty()
        return new_cutscene

    def remove_cutscene(self, cutscene_id):
        self.data.cutscenes = [cs for cs in self.data.cutscenes if cs.id != cutscene_id]
        self.set_dirty()

    def get_verb_index(self, verb_id):
        for i, verb in enumerate(self.data.verbs):
            if verb.id == verb_id:
                return i
        return -1

    def get_item_index(self, item_id):
        for i, item in enumerate(self.data.items):
            if item.id == item_id:
                return i
        return -1

    def get_logic_graph_index(self, graph_id):
        for i, graph in enumerate(self.data.logic_graphs):
            if graph.id == graph_id:
                return i
        return -1

    def get_verb_name(self, verb_id):
        for verb in self.data.verbs:
            if verb.id == verb_id:
                return verb.name
        return ""

    def get_item_name(self, item_id):
        for item in self.data.items:
            if item.id == item_id:
                return item.name
        return ""

    def get_hotspot_index(self, hotspot_id):
        for i, scene in enumerate(self.data.scenes):
            for j, hotspot in enumerate(scene.hotspots):
                if hotspot.id == hotspot_id:
                    return i * 1000 + j # A bit of a hack to get a unique index
        return -1

    @staticmethod
    def get_templates():
        """Returns a list of available project templates."""
        template_dir = os.path.join(os.path.dirname(
            __file__), "..", "..", "templates")
        if os.path.exists(template_dir):
            return [d for d in os.listdir(template_dir) if os.path.isdir(os.path.join(template_dir, d))]
        return []

    @staticmethod
    def create_project(project_path: str, template: str = None):
        """Creates the directory structure and data files for a new project.

        This static method is used to initialize a new project on the
        filesystem. It creates the necessary subdirectories and populates them
        with empty or template-based data files.

        Args:
            project_path: The absolute path where the project will be created.
            template: The name of an optional project template to use.

        Returns:
            A tuple containing a new ProjectManager instance and an error
            string. If the project is created successfully, the error string
            will be None.
        """
        print(f"DEBUG: ProjectManager.create_project: Creating new project at {project_path} with template {template}")
        if template:
            template_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "templates", template)
            if os.path.exists(template_dir):
                import shutil
                shutil.copytree(template_dir, project_path,
                                dirs_exist_ok=True)

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
                "CharacterData.csv": ["id", "display_name", "dialogue_start_id", "is_merchant", "shop_id", "portrait_asset_id", "sprite_sheet_asset_id", "animations"],
            }
            for filename, headers in csv_files.items():
                file_path = os.path.join(data_dir, filename)
                if not os.path.exists(file_path):
                    with open(file_path, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)

            # Create empty JSON files
            json_files = {
                os.path.join(data_dir, "Assets.json"): [],
                os.path.join(data_dir, "Audio.json"): [],
                os.path.join(data_dir, "GlobalState.json"): [],
                os.path.join(data_dir, "Verbs.json"): [],
                os.path.join(data_dir, "Fonts.json"): [],
                os.path.join(logic_dir, "Scenes.json"): [],
                os.path.join(logic_dir, "LogicGraphs.json"): [],
                os.path.join(logic_dir, "DialogueGraphs.json"): [],
                os.path.join(logic_dir, "Cutscenes.json"): [],
                os.path.join(logic_dir, "Interactions.json"): [],
                os.path.join(logic_dir, "Quests.json"): [],
                os.path.join(ui_dir, "WindowLayout.json"): [],
            }
            for file_path, default_content in json_files.items():
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        json.dump(default_content, f)

            project_manager = ProjectManager(project_path)
            project_manager.is_new_project = True
            return project_manager, None
        except Exception as e:
            return None, str(e)

    def search(self, query: str) -> list[SearchResult]:
        """Searches all project data for a given query.

        This method performs a case-insensitive search across various data
        types in the project, including items, characters, scenes, quests,
        and assets.

        Args:
            query: The search term.

        Returns:
            A list of SearchResult objects that match the query.
        """
        results = []
        query_lower = query.lower()

        # Search Items
        for item in self.data.items:
            if query_lower in item.name.lower() or query_lower in item.id.lower():
                results.append(
                    SearchResult(id=item.id, name=item.name, type="Item"))

        # Search Characters
        for char in self.data.characters:
            if query_lower in char.display_name.lower() or query_lower in char.id.lower():
                results.append(SearchResult(
                    id=char.id, name=char.display_name, type="Character"))

        # Search Scenes
        for scene in self.data.scenes:
            if query_lower in scene.name.lower() or query_lower in scene.id.lower():
                results.append(
                    SearchResult(id=scene.id, name=scene.name, type="Scene"))

        # Search Quests
        for quest in self.data.quests:
            if query_lower in quest.name.lower() or query_lower in quest.id.lower():
                results.append(
                    SearchResult(id=quest.id, name=quest.name, type="Quest"))

        # Search Assets
        for asset in self.data.assets:
            if query_lower in asset.name.lower() or query_lower in asset.id.lower():
                results.append(
                    SearchResult(id=asset.id, name=asset.name, type="Asset"))

        return results
