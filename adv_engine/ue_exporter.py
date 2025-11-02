import os
import json
import csv

def export_project(project_path):
    """
    Exports all data files to the specified project path.
    For now, it just creates empty placeholder files with headers.
    """
    data_dir = os.path.join(project_path, "Data")
    logic_dir = os.path.join(project_path, "Logic")
    dialogues_dir = os.path.join(project_path, "Dialogues")
    ui_dir = os.path.join(project_path, "UI")

    # Create CSV files
    with open(os.path.join(data_dir, "ItemData.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type", "buy_price", "sell_price"])

    with open(os.path.join(data_dir, "CharacterData.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "default_animation", "dialogue_start_id", "is_merchant", "shop_id"])

    with open(os.path.join(data_dir, "Attributes.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "initial_value", "max_value"])

    # Create JSON files
    with open(os.path.join(logic_dir, "InteractionMatrix.json"), "w") as f:
        json.dump([], f, indent=2)

    with open(os.path.join(dialogues_dir, "Graph_Placeholder.json"), "w") as f:
        json.dump({}, f, indent=2)

    with open(os.path.join(ui_dir, "WindowLayout.json"), "w") as f:
        json.dump({}, f, indent=2)

if __name__ == "__main__":
    # This is a simple test to run the exporter on the TestGame directory
    export_project("TestGame")
    print("Exported data files to TestGame/")
