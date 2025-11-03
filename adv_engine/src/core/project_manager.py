"""
Handles loading, saving, and managing all project data.
"""

import os
import csv
from .data_schemas import ProjectData, Item, Attribute, Character

class ProjectManager:
    def __init__(self, project_path):
        self.project_path = project_path
        self.data = ProjectData()

    def load_project(self):
        """
        Loads all data from the project path.
        """
        self._load_items()
        self._load_attributes()
        self._load_characters()

    def _load_items(self):
        """
        Loads items from ItemData.csv.
        """
        file_path = os.path.join(self.project_path, "Data", "ItemData.csv")
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    item = Item(
                        id=row["id"],
                        name=row["name"],
                        type=row["type"],
                        buy_price=int(row["buy_price"]),
                        sell_price=int(row["sell_price"]),
                    )
                    self.data.items.append(item)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _load_attributes(self):
        """
        Loads attributes from Attributes.csv.
        """
        file_path = os.path.join(self.project_path, "Data", "Attributes.csv")
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    attribute = Attribute(
                        id=row["id"],
                        name=row["name"],
                        initial_value=int(row["initial_value"]),
                        max_value=int(row["max_value"]),
                    )
                    self.data.attributes.append(attribute)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    def _load_characters(self):
        """
        Loads characters from CharacterData.csv.
        """
        file_path = os.path.join(self.project_path, "Data", "CharacterData.csv")
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    character = Character(
                        id=row["id"],
                        display_name=row["display_name"],
                        dialogue_start_id=row["dialogue_start_id"],
                        is_merchant=row["is_merchant"].lower() == "true",
                        shop_id=row["shop_id"] if row["shop_id"] else None,
                    )
                    self.data.characters.append(character)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
