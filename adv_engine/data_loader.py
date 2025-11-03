import os
import csv
from .data_models import Item, Attribute, Character

def load_characters_from_csv(project_path):
    """
    Loads all characters from the CharacterData.csv file in the project.
    """
    characters = []
    file_path = os.path.join(project_path, "Data", "CharacterData.csv")

    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                characters.append(Character(
                    id=row["id"],
                    default_animation=row["default_animation"],
                    dialogue_start_id=row["dialogue_start_id"],
                    is_merchant=row["is_merchant"].lower() == "true",
                    shop_id=row["shop_id"] if row["shop_id"] else None
                ))
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No characters will be loaded.")

    return characters

def load_attributes_from_csv(project_path):
    """
    Loads all attributes from the Attributes.csv file in the project.
    """
    attributes = []
    file_path = os.path.join(project_path, "Data", "Attributes.csv")

    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                attributes.append(Attribute(
                    id=row["id"],
                    name=row["name"],
                    initial_value=int(row["initial_value"]),
                    max_value=int(row["max_value"])
                ))
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No attributes will be loaded.")

    return attributes

def load_items_from_csv(project_path):
    """
    Loads all items from the ItemData.csv file in the project.
    """
    items = []
    file_path = os.path.join(project_path, "Data", "ItemData.csv")

    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(Item(
                    id=row["id"],
                    name=row["name"],
                    type=row["type"],
                    buy_price=int(row["buy_price"]),
                    sell_price=int(row["sell_price"])
                ))
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No items will be loaded.")
        # In a real app, you might want to create the file here or show an error.

    return items

if __name__ == "__main__":
    # A simple test to load items from the TestGame project
    test_items = load_items_from_csv("TestGame")
    if test_items:
        print(f"Successfully loaded {len(test_items)} items:")
        for item in test_items:
            print(f" - {item.name} ({item.id})")
    else:
        print("No items were loaded (or the file is empty).")
