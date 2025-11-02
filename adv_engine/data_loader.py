import os
import csv
from .data_models import Item

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
