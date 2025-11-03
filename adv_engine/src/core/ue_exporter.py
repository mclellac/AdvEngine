import os
import json
import csv
from dataclasses import asdict

def export_project(project_manager):
    """
    Exports all data files to the specified project path using data from the project_manager.
    """
    project_path = project_manager.project_path
    data = project_manager.data

    # --- Create directories if they don't exist ---
    data_dir = os.path.join(project_path, "Data")
    logic_dir = os.path.join(project_path, "Logic")
    dialogues_dir = os.path.join(project_path, "Dialogues")
    ui_dir = os.path.join(project_path, "UI")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logic_dir, exist_ok=True)
    os.makedirs(dialogues_dir, exist_ok=True)
    os.makedirs(ui_dir, exist_ok=True)

    # --- Export Items to ItemData.csv ---
    with open(os.path.join(data_dir, "ItemData.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "type", "buy_price", "sell_price"])
        writer.writeheader()
        for item in data.items:
            writer.writerow(asdict(item))

    # --- Export Characters to CharacterData.csv ---
    with open(os.path.join(data_dir, "CharacterData.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "display_name", "dialogue_start_id", "is_merchant", "shop_id"])
        writer.writeheader()
        for char in data.characters:
            writer.writerow(asdict(char))

    # --- Export Attributes to Attributes.csv ---
    with open(os.path.join(data_dir, "Attributes.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "initial_value", "max_value"])
        writer.writeheader()
        for attr in data.attributes:
            writer.writerow(asdict(attr))

    # --- Export Logic Graphs to LogicGraphs.json ---
    with open(os.path.join(logic_dir, "LogicGraphs.json"), "w") as f:
        json.dump([asdict(graph) for graph in data.logic_graphs], f, indent=2)

    # --- Placeholder JSON files ---
    with open(os.path.join(dialogues_dir, "Graph_Placeholder.json"), "w") as f:
        json.dump({}, f, indent=2)

    with open(os.path.join(ui_dir, "WindowLayout.json"), "w") as f:
        json.dump({}, f, indent=2)

if __name__ == "__main__":
    from project_manager import ProjectManager
    # This is a simple test to run the exporter on the TestGame directory
    pm = ProjectManager("TestGame")
    pm.load_project()
    export_project(pm)
    print(f"Exported data files to {pm.project_path}/")
