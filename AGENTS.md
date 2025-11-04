# AGENTS.md: AdvEngine

---

## 1. Project Overview & Context

*   **Project Name (Tool):** AdvEngine
*   **Purpose:** A modern adventure game editor for the rapid creation and iteration of 2.5D point-and-click adventure games, inspired by classic Sierra On-Line titles.
*   **Function:** AdvEngine is a **Data and Configuration Manager**. It provides a cross-platform UI for designing game logic, managing data, and exporting structured files for the target game engine.
*   **Target Game Engine:** Unreal Engine 5.6
*   **Core Principle:** Abstraction—hide Unreal Engine's complexity behind a clean, data-driven Python interface.

---

## 2. Technology Stack & Dependencies

### A. Core Tool Stack (AdvEngine Application)

| Component | Role | Required Version | Notes |
| :--- | :--- | :--- | :--- |
| **Language** | Front-end logic, data management. | **Python 3.10+** | |
| **GUI Framework** | Cross-platform UI toolkit. | **GTK4 (via PyGObject)** | Provides the core application structure. |
| **Design Library** | Modern, responsive UI components. | **Libadwaita** | Ensures a clean, HIG-compliant aesthetic. |
| **Build System** | Project compilation and installation. | **Meson & Ninja** | Replaces previous direct script execution. |
| **Graphing** | Node drawing and rendering. | **Custom GTK Widget** | Uses **cairo** for canvas rendering. |
| **Serialization**| Data processing for project files. | **json**, **csv** | Standard libraries for all I/O. |

---

## 3. AdvEngine Internal Tool Architecture

### A. Directory Structure

The project has a split source structure. Python modules are in `adv_engine/src/`, while GTK UI definition files, resources, and Meson build scripts are in a separate top-level `src/`.

```text
/
|-- src/                      # Top-level source for build system and resources
|   |-- core/
|   |   |-- project_manager.py     # Handles project loading, saving, and data access.
|   |   |-- data_schemas.py        # Python dataclass definitions for all game data.
|   |   |-- settings_manager.py    # Manages application and project settings.
|   |   |-- ue_exporter.py         # Defines node commands and parameters.
|   |-- ui/
|   |   |-- main.py                # Application entry point and main window class.
|   |   |-- module_scene.py        # Scene Editor
|   |   |-- module_logic.py        # Logic Graph Editor
|   |   |-- module_dialogue.py     # Dialogue Tree Editor
|   |   |-- module_interaction.py  # Interaction Editor
|   |   |-- module_character.py    # Character Manager
|   |   |-- module_quest.py        # Quest Editor
|   |   |-- item_editor.py         # Item Database Editor
|   |   |-- ... (other editors)
|   |-- advengine.gresource.xml # GResource bundle definition.
|   |-- main.py                 # Application entry point.
|-- TestGame/                 # Example project data.
|-- docs/                     # User guide and tutorial.
|-- meson.build               # Main Meson build script.
```

### B. Module Responsibilities

*   **`src/core/project_manager.py`**: The central data hub. Manages loading all project files (`.json`, `.csv`) into memory, provides data access to UI modules, tracks unsaved changes (`is_dirty` state), and handles saving operations.
*   **`src/core/data_schemas.py`**: Defines the application's entire data model using Python `dataclasses`. This includes structures for `Item`, `Character`, `Scene`, `LogicGraph`, `Quest`, etc.
*   **`src/ui/main.py`**: The application entry point. Initializes the `Adw.Application`, builds the main `AdvEngineWindow`, instantiates all editor modules, and wires them into the `Adw.ViewStack`.
*   **`src/ui/module_logic.py`**: Implements the generic node-based editor for creating and visualizing `LogicGraph` data structures. It handles canvas drawing, user input (selection, dragging, connecting), and context menus.
*   **`src/ui/module_dialogue.py`**: A specialized editor that uses a tree view to manage `DialogueGraph` data, which is a specific type of `LogicGraph`.
*   **Database Editors (`item_editor.py`, etc.)**: These modules implement a consistent, spreadsheet-like UI using `Gtk.ColumnView` for all database-style data (Items, Verbs, Attributes, etc.), providing full inline CRUD functionality.

---

## 4. AdvEngine Feature Specification

### A. Core Editor Modules

| Module Name | Functionality Focus | Key Feature |
| :--- | :--- | :--- |
| **Scenes** | World Design | Canvas editor with hotspot creation, properties panel, and layer list. |
| **Logic** | Puzzle & Narrative | General-purpose node-graph editor for `LogicGraph` data. |
| **Interactions** | Gameplay Logic | Defines `Verb + Item` and `Item + Item` interactions, linking them to a `LogicGraph`. |
| **Dialogue** | Narrative Design | A tree-based editor for creating branching conversations. |
| **Cutscenes** | Cinematic Scripting| A simple, text-based editor for creating sequential `CutsceneAction` scripts. |
| **Characters** | Character Creation | Spreadsheet-style editor for characters with a portrait preview. |
| **Quests** | Objective Tracking | Editor for defining multi-step quests. |
| **Assets** | Media Management | Manages sprites and animations with a preview panel. |
| **Global State** | State Management | Spreadsheet-style editor for global variables. |
| **Database** | Core Game Data | A combined view for Items, Attributes, and Verbs editors. |
| **Audio** | Sound & Ambiance | Manages background music and sound effects, with an embedded player. |

---

## 5. Data Persistence & File Formats

Project data is saved into a series of JSON and CSV files within the project directory.

### A. Project File Structure

| Path | Purpose | Format |
| :--- | :--- | :--- |
| `[ProjectName]/Logic/Scenes.json` | All scene definitions and hotspot data. | JSON |
| `[ProjectName]/Logic/LogicGraphs.json` | All generic logic graphs. | JSON |
| `[ProjectName]/Logic/DialogueGraphs.json` | All dialogue trees. | JSON |
| `[ProjectName]/Logic/Interactions.json` | All verb/item interaction rules. | JSON |
| `[ProjectName]/Logic/Quests.json` | All quest and quest step definitions. | JSON |
| `[ProjectName]/Logic/Cutscenes.json` | All cutscene scripts. | JSON |
| `[ProjectName]/Data/ItemData.csv` | List of all game items. | CSV |
| `[ProjectName]/Data/CharacterData.csv` | List of all characters. | CSV |
| `[ProjectName]/Data/GlobalState.json` | Global variable definitions. | JSON |
| `[ProjectName]/Data/Verbs.json` | All defined verbs. | JSON |
| `[ProjectName]/Assets.json` | Asset library metadata. | JSON |
| `[ProjectName]/Audio.json` | Audio library metadata. | JSON |
| `[ProjectName]/settings.json` | Project-specific settings. | JSON |


### B. Core `LogicGraph` Structure (JSON)

The `LogicGraph` is the central data structure for all node-based logic. It consists of a list of nodes and connections.

```json
{
  "id": "String",
  "nodes": [
    {
      "id": "String",
      "type": "NodeType", // e.g., DialogueNode, ConditionNode, ActionNode
      "x": "float",
      "y": "float",
      "width": "float",
      "height": "float",
      "inputs": ["String"], // List of connected node IDs
      "outputs": ["String"], // List of connected node IDs
      // ... other node-specific properties
    }
  ]
}
```

---

## 6. Database Schema Documentation

#### A. Character Schema (`CharacterData.csv`)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| id | String | Unique character identifier. |
| display_name | String | Name shown in dialogue. |
| portrait_asset_id | String | ID of the asset for the character's portrait. |
| sprite_sheet_asset_id| String | ID of the asset for the character's sprite sheet. |
| animations | String (JSON) | A JSON string defining character animations. |

#### B. Other Schemas

Refer to `src/core/data_schemas.py` for the definitive structure of all other data types, including `Item`, `Attribute`, `Verb`, `Quest`, `Interaction`, etc. The dataclasses in this file are the source of truth for all data models.

---

## 7. Coding Style and Conventions

*   **PEP8 Compliance**: All Python code must adhere to the PEP8 style guide.
*   **Docstrings**: All modules, classes, and functions must have Google-style docstrings.
*   **Error Handling**: Use `try...except` blocks for all file I/O operations. Provide clear user feedback for errors.
*   **GNOME HIG**: The UI must follow the GNOME Human Interface Guidelines, using Libadwaita widgets and patterns wherever possible.
*   **Atomic Commits**: Submit work as focused, atomic changes. Avoid bundling unrelated features or bug fixes.
