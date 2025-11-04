# AGENTS.md: AdvEngine

---

## 1. Project Overview & Context

*   Project Name (Tool): **AdvEngine**
*   Purpose: A modern adventure game editor focused on **rapid creation and
    iteration** of atmospheric 2.5D cyberpunk detective/noir adventure games
    by a one-man team.
*   Function: AdvEngine is a **Data and Configuration Manager**. It provides a
    superior, cross-platform UI/UX for design and exports structured data files
    for the target game engine to consume at runtime.
*   Target Game Engine: **Unreal Engine 5.6**
*   Core Principle: Abstraction—hide all UE complexity behind a clean,
    data-driven Python interface.
*   Output Goal: Game must support modern resolutions (2K, 4K, Ultrawide) via
    intelligent scaling and UI anchoring.

---

## 2. Technology Stack & Dependencies

### A. Core Tool Stack (AdvEngine Application)

| Component      | Role                                                  | Required Version      | Notes                                                              |
| -------------- | ----------------------------------------------------- | --------------------- | ------------------------------------------------------------------ |
| **Language**   | Front-end logic, data management, and export scripting. | **Python 3.10+**      |                                                                    |
| **GUI Framework**| Cross-platform UI toolkit.                            | **GTK4 (via PyGObject)** | Provides the core application structure and widgets.               |
| **Design Library**| Modern, responsive UI/UX components.                  | **Libadwaita**        | Ensures a clean, polished aesthetic on all platforms.              |
| **Packaging**  | Bundling the Python app into standalone executables.    | **PyInstaller**       | Critical for Windows/macOS distribution. Must bundle all GTK/Libadwaita dependencies. |
| **Graphing**   | Node drawing and connection management.               | **Custom GTK Widget** | Will use **cairo** or similar library for canvas rendering (Logic Editor). |
| **Serialization**| Data processing.                                      | **json**, **csv**, **os** | Standard Python libraries for project I/O and export contract files. |

### B. Target Game Engine & API Contract (The Connection)

| Component          | Role                      | Critical Detail                                                                                                |
| ------------------ | ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Engine Project** | **AdvEngine UE Template** | Pre-built UE project with fixed Blueprints/C++ for movement, inventory, and scene loading.                       |
| **Data Contract**  | **Schema Alignment**      | Exported JSON/CSV structures **must** match the **UE Custom Structs** (e.g., FS_InteractionRule) and **Data Table Blueprints** exactly. |
| **Data Location**  | Filesystem Write          | Python tool writes data files directly into the UE project's Content/ExternalData/ directory.                    |
| **Runtime Data Load** | **AdvEngine Game Instance** | All parsing is handled by the UE **Game Instance Blueprint** or dedicated C++ service during game startup. |
| **Visuals**        | **Modern Rendering**      | Template must leverage UE5's **Lumen** (GI) and **Control Rig/Animation Blueprints** for fluid character movement/lighting. |

---

## 3. AdvEngine Internal Tool Architecture (Python Source)

The architecture is strictly modular to isolate UI logic from data logic.

### A. Directory Structure

```text
/AdvEngine/
|-- src/
|   |-- core/
|   |   |-- __init__.py
|   |   |-- project_manager.py     # Handles native project serialization
|   |   |-- data_schemas.py        # Python dataclass definitions
|   |   |-- ue_exporter.py         # **CRITICAL:** Handles CSV/JSON formatting
|   |-- ui/
|   |   |-- __init__.py
|   |   |-- main_window.py         # Main Adw.ApplicationWindow setup
|   |   |-- module_scene.py        # Scene Editor canvas
|   |   |-- module_logic.py        # Dialogue/Interaction node graph
|   |   |-- module_character.py    # Character Manager
|   |   |-- module_quest.py        # Quest & Objective Tracker
|   |   |-- module_ui_builder.py   # Point-and-Click UI Builder
|   |   |-- module_font.py         # Font Management
|   |   |-- module_log.py          # Interaction Log
|   |   |-- item_editor.py         # Spreadsheet-like editor for Items
|   |   |-- attribute_editor.py    # Spreadsheet-like editor for Attributes
|   |   |-- verb_editor.py         # Spreadsheet-like editor for Verbs
|   |   |-- widgets/               # Reusable GTK components
|   |-- resources/                 # Libadwaita UI/CSS files and icons
|   |-- main.py                    # Application entry point
|-- build/                         # PyInstaller output directories
|-- data/                          # Runtime project files and configuration
```

### B. Module Responsibilities

*   **core/project_manager.py**: Manages loading and saving of the native .adv
    project format. It tracks unsaved changes ("dirty" state) and provides
    notifications to the UI.
*   **core/ue_exporter.py**: The API Gatekeeper. Converts Python object lists
    into validated JSON/CSV strings that adhere precisely to the UE Data Table
    specification.
*   **ui/module_logic.py**: Handles mouse events (drag, select, connect) on the
    custom drawing canvas. Serializes the visual node layout into the
    InteractionMatrix.json structure.
*   **ui/**: The UI is built using Libadwaita widgets to ensure a modern,
    HIG-compliant user experience. Dialogs and forms are built using
    `Adw.PreferencesGroup` and `Adw.ActionRow` for a consistent look and feel.
*   **main.py**: The main application window, which includes a global search
    bar for finding assets, logic nodes, and database entries.

---

## 4. AdvEngine Feature Specification

### A. Core Editor Modules (Tabs)

| Module Name    | Functionality Focus | Key Feature                                                                                              |
| -------------- | ------------------- | -------------------------------------------------------------------------------------------------------- |
| **Scenes**     | World Design        | A canvas-based editor with an `Adw.OverlaySplitView` layout. Features include hotspot creation, a properties panel for editing, a layer list for Z-ordering, and zoom/pan functionality. |
| **Logic**      | Puzzle & Narrative  | A node-graph editor with an `Adw.OverlaySplitView` layout. Features include multi-node selection and dragging, resizable nodes, a properties panel for non-modal editing, and context menus. |
| **Characters** | Character Creation  | A modern, spreadsheet-style editor for managing characters, with a portrait preview. Features full inline editing and search. |
| **Quests**     | Quest & Objective   | A simple system to define high-level quests or tasks.                                                     |
| **UI Builder** | UI Design           | A visual editor to design the main in-game user interface.                                                |
| **Fonts**      | Font Management     | A system to import and manage bitmap fonts for in-game text.                                              |
| **Assets**     | Media Management    | Sprite import, Animation sequence definition, asset preview panel, Normal Map texture pairing (for UE lighting). |
| **Global State** | State Management    | A modern, spreadsheet-style editor for managing global variables, with full inline editing and search. |
| **Verbs & Items**| Database            | Modern, spreadsheet-style editors for managing verbs, items, and attributes, with full inline editing and search. |
| **Audio**      | Sound & Ambiance    | Assignment of background music and ambient loops to scenes. Placement of localized 3D SFX emitters.        |

### B. Rapid Development & Debugging Features

| Feature Name           | Integration Point       | Purpose                                                                                                 |
| ---------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------- |
| **Batch Processing**   | Asset & Logic Modules   | CSV import for dialogue scripts; Template system for repetitive animated environment assets.            |
| **Interaction Trace Log** | Debug Window            | Streams puzzle failure/success conditions from the UE game back to the AdvEngine UI.                    |
| **Contextual Fallbacks** | Logic Editor            | Global or scene-specific default responses for non-programmed interactions (e.g., "That doesn't work here."). |
| **Task/Note Attachment** | All Editors             | Allows attaching simple to-do items directly to Hotspots or Logic Nodes.                                |
| **Save Status Indicator**| Main Window             | The window title displays an asterisk (*) when there are unsaved changes. Project saving is handled manually via a "Save" button or `Ctrl+S`. |

### C. Window/Menu Manager Details

*   **UI Anchoring**: Provides a visual editor to define how UI elements
    (Inventory Panel, Stat HUD) scale and anchor across different aspect ratios
    (16:9, 21:9).
*   **Layout Definition**: Defines the grid size (e.g., 5x4 inventory grid) and
    sprite key for currency indicators.

---

## 5. Export Contract Data (API Specification)

### A. File Structure & Paths

| Path                                     | Purpose                                           | Format | Notes (UE Consumer)                               |
| ---------------------------------------- | ------------------------------------------------- | ------ | ------------------------------------------------- |
| `[ProjectName]/Data/ItemData.csv`        | List of all items, prices, and properties.        | CSV    | Loaded into the `BP_ItemData` Data Table.         |
| `[ProjectName]/Data/Verbs.json`          | Defines the verbs available to the player.        | JSON   | Used to build the in-game UI and parse interactions. |
| `[ProjectName]/Data/GlobalState.json`    | Defines all global game variables and their initial values. | JSON   | Parsed by a global state manager in UE.           |
| `[ProjectName]/Logic/Interactions.json`      | Defines all verb/item interactions.               | JSON   | Parsed by the `BP_InteractionComponent` at runtime. |
| `[ProjectName]/UI/WindowLayout.json`     | Defines the anchoring and contents of all custom menus. | JSON   | Used by the `BP_UIManager` to dynamically build the UI. |

### B. Core Action Commands (Mapped to UE Blueprint Functions)

These commands are the fixed API contract between AdvEngine and the UE runtime.

| Command                | Purpose                                                              |
| ---------------------- | -------------------------------------------------------------------- |
| `SET_VARIABLE`         | Update a global game state variable or quest flag.                   |
| `INVENTORY_ADD`        | Adds an item to the player's inventory.                              |
| `INVENTORY_REMOVE`     | Removes an item from the player's inventory.                         |
| `SCENE_TRANSITION`     | Warps the player to a new scene and spawn point.                     |
| `SHOP_OPEN`            | Triggers the Shop UI, referencing a specific Shop ID.                |
| `MODIFY_ATTRIBUTE`     | Changes a character's attribute value (e.g., Tech Skill +1).         |
| `PLAY_CINEMATIC`       | Triggers a pre-built UE Sequencer asset for cutscenes.               |
| `PLAY_SFX`             | Triggers a sound effect event defined in the Audio Manifest.         |

### C. Interaction Structure (Interactions.json)

The central logic file, an array of Interaction Objects.

```json
[
  {
    "id": "String",
    "verb_id": "String",
    "primary_item_id": "String/Null",
    "secondary_item_id": "String/Null",
    "target_hotspot_id": "String/Null",
    "logic_graph_id": "String"
  }
]
```

---

## 6. Database Schema Documentation

#### A. Item Database Schema (Export: ItemData.csv)

| Field Name  | Data Type | Description                                           |
|-------------|-----------|-------------------------------------------------------|
| id          | String    | Unique identifier for inventory and logic checks.     |
| name        | String    | Display name for the player.                          |
| description | String    | Flavor text for the Look action.                      |
| type        | String    | Categorization: Key Item, Consumable, Currency, Equip.|
| buy_price   | Integer   | Price to buy the item (-1 if non-purchasable).        |
| sell_price  | Integer   | Price to sell the item (-1 if unsellable).            |

#### B. Character Attribute (Stat) Schema (Export: Attributes.csv)

| Field Name    | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | String    | Unique stat identifier.                   |
| name          | String    | Display name on the player stat screen.   |
| initial_value | Integer   | Starting value for the player.            |
| max_value     | Integer   | Upper limit for the attribute.            |

#### C. NPC Schema (Export: CharacterData.csv)

| Field Name        | Data Type   | Description                                           |
|-------------------|-------------|-------------------------------------------------------|
| id                | String      | Unique character identifier.                          |
| display_name      | String      | The name shown in dialogue boxes.                     |
| dialogue_start_id | String      | The ID of the first node for conversation start.      |
| is_merchant       | Boolean     | If True, this NPC can open the shop interface.        |
| shop_id           | String/Null | The ID of the specific shop inventory they sell.      |
| portrait_asset_id | String/Null | The ID of the asset for the character's portrait.     |

#### D. Verb Database Schema (Export: Verbs.json)

| Field Name | Data Type | Description                                           |
|------------|-----------|-------------------------------------------------------|
| id         | String    | Unique identifier for the verb (e.g., "use").         |
| name       | String    | Display name for the verb in the UI (e.g., "Use").    |

#### E. Shop Database Schema (Implicit in CharacterData/ItemData)

*   **Definition**: Defined by the `shop_id` in the NPC schema and the
    `buy_price`/`sell_price` in the Item schema.
*   **Stock Data**: An additional simple table/list is required

---

## 7. Coding Style and Conventions

### A. Python Code Style

*   **PEP8 Compliance**: All Python code must adhere to the
    [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/).
*   **Docstrings**: All modules, classes, and functions must have clear and
    concise docstrings. Use the
    [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
    for formatting.
*   **Idiomatic Python**: Write clean, readable, and Pythonic code.

### B. Error Handling

*   **Robustness**: The application must be resilient to common errors, such as
    missing files or invalid data formats.
*   **Exception Handling**: Use `try...except` blocks for all file I/O
    operations and data parsing.
*   **User Feedback**: When an error occurs, provide clear and informative
    feedback to the user via a dialog or a message in the UI.
