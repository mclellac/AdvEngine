import os
import json
import csv
from dataclasses import asdict

COMMAND_DEFINITIONS = {
    "actions": {
        "SET_VARIABLE": {"params": {"VarName": "str", "Value": "any"}},
        "INVENTORY_ADD": {"params": {"ItemID": "str", "Amount": "int"}},
        "INVENTORY_REMOVE": {"params": {"ItemID": "str", "Amount": "int"}},
        "SCENE_TRANSITION": {"params": {"SceneID": "str", "SpawnPoint": "str"}},
        "SHOP_OPEN": {"params": {"ShopID": "str"}},
        "MODIFY_ATTRIBUTE": {"params": {"AttributeID": "str", "Value": "int"}},
        "PLAY_CINEMATIC": {"params": {"CinematicID": "str"}},
        "PLAY_SFX": {"params": {"SoundID": "str"}},
        "UNLOCK_HOTSPOT": {"params": {"HotspotID": "str"}},
        "LOCK_HOTSPOT": {"params": {"HotspotID": "str"}},
        "SET_ANIMATION": {
            "params": {"TargetID": "str", "AnimationKey": "str", "Loop": "bool"}
        },
        "HIDE_ENTITY": {"params": {"EntityID": "str"}},
        "SHOW_ENTITY": {"params": {"EntityID": "str", "X": "int", "Y": "int"}},
        "SET_CURSOR_MODE": {"params": {"Mode": ["Contextual", "Classic"]}},
        "SET_WALK_MESH": {"params": {"SceneID": "str", "MeshID": "str"}},
        # Extended Actions:
        "SET_PLAYER_POS": {"params": {"X": "int", "Y": "int"}},
        "GIVE_CURRENCY": {"params": {"Amount": "int"}},
        "TAKE_CURRENCY": {"params": {"Amount": "int"}},
        "PLAY_SOUND_2D": {"params": {"SoundID": "str"}},
        "SHOW_DIALOGUE_CHOICES": {"params": {"DialogueNodeID": "str"}},
        "FORCE_SAVE": {"params": {}},
    },
    "conditions": {
        "VARIABLE_EQUALS": {"params": {"VarName": "str", "Value": "any"}},
        "HAS_ITEM": {"params": {"ItemID": "str", "Amount": "int"}},
        "ATTRIBUTE_CHECK": {
            "params": {
                "AttributeID": "str",
                "Value": "int",
                "Comparison": ["==", ">", "<", ">=", "<="],
            }
        },
        "HOTSPOT_LOCKED": {"params": {"HotspotID": "str", "State": "bool"}},
        "ENTITY_VISIBLE": {"params": {"EntityID": "str", "Visible": "bool"}},
        "SCENE_VISITED": {"params": {"SceneID": "str", "Times": "int"}},
        # Extended Conditions:
        "CURRENCY_GE": {"params": {"Amount": "int"}},
        "HAS_FAILED_CHECK": {"params": {"CheckID": "str"}},
        "ENTITY_HAS_ITEM": {"params": {"EntityID": "str", "ItemID": "str"}},
        "WALK_MESH_ACTIVE": {"params": {"MeshID": "str", "State": "bool"}},
        "TIME_OF_DAY_IS": {
            "params": {"TimeState": ["Night", "Morning", "Day", "Evening"]}
        },
    },
}


def get_command_definitions():
    return COMMAND_DEFINITIONS


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
        writer = csv.DictWriter(
            f, fieldnames=["id", "name", "type", "buy_price", "sell_price"]
        )
        writer.writeheader()
        for item in data.items:
            writer.writerow(asdict(item))

    # --- Export Characters to CharacterData.csv ---
    with open(os.path.join(data_dir, "CharacterData.csv"), "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "display_name",
                "dialogue_start_id",
                "is_merchant",
                "shop_id",
            ],
        )
        writer.writeheader()
        for char in data.characters:
            writer.writerow(asdict(char))

    # --- Export Attributes to Attributes.csv ---
    with open(os.path.join(data_dir, "Attributes.csv"), "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "name", "initial_value", "max_value"]
        )
        writer.writeheader()
        for attr in data.attributes:
            writer.writerow(asdict(attr))

    # --- Export Logic Graphs to LogicGraphs.json ---
    with open(os.path.join(logic_dir, "LogicGraphs.json"), "w") as f:
        json.dump([asdict(graph) for graph in data.logic_graphs], f, indent=2)

    # --- Export Interactions to Interactions.json ---
    with open(os.path.join(logic_dir, "Interactions.json"), "w") as f:
        json.dump(
            [asdict(interaction) for interaction in data.interactions], f, indent=2
        )

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
