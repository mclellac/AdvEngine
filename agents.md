## agents.md: AdvEngine Project Documentation (Complete)

---
## 1. Project Overview & Context

* Project Name (Tool): **AdvEngine**
* Purpose: A modern adventure game editor focused on **rapid creation and iteration** of atmospheric 2.5D cyberpunk detective/noir adventure games.
* Function: AdvEngine is a **Data and Configuration Manager**. It provides a superior, cross-platform UI/UX for design and exports structured data files for the target game engine to consume at runtime.
* Target Game Engine: **Unreal Engine 5.6**

---
## 2. Technology Stack & Dependencies

### A. Core Tool Stack (AdvEngine Application)

| Component | Role | Notes |
|---|---|---|
| Language | Front-end logic, data management, and export scripting. | Python 3.10+ |
| GUI Framework | Cross-platform UI toolkit. | GTK4 (via PyGObject) |
| Design Library | Modern, responsive UI/UX components. | Libadwaita |
| Operating Systems| Linux, macOS, and Windows | Packaging via PyInstaller. |

### B. Target Game Engine & API Contract (The Connection)

| Component | Role | Critical Detail |
|---|---|---|
| Engine | Unreal Engine 5.6 | Requires a dedicated **AdvEngine UE Template** project. |
| Data Contract| Schema Alignment | JSON/CSV structures must match the **UE Custom Structs** and **Data Table Blueprints** exactly. |
| Export Method | Filesystem Write | Python tool writes data files directly into the UE project's Content/ExternalData/ directory. |
| Runtime Data Load | UE Game Instance | All data loading and parsing is handled by the UE **Game Instance Blueprint** during game startup. |

---
## 3. AdvEngine Architectural Workflow

The tool facilitates a data-driven pipeline:

1.  **Input:** Designer places entities and defines logic in AdvEngine (Python/GTK4).
2.  **Serialization:** Python tool serializes changes (e.g., entity placement, dialogue graphs).
3.  **Export:** User hits **Run Game**, and ue_exporter.py writes the updated JSON/CSV files to the target UE project.
4.  **UE Startup:** The custom **AdvEngine Game Instance** reads all exported files.
5.  **Instantiation:** The engine uses the parsed data (e.g., InteractionMatrix) to set up scene logic and dynamically instance objects.

---
## 4. File Structure & Export Paths (API Contract)

### A. Project Export Directory (Data for UE 5.6)

| Path | Purpose | Format | Notes (UE Consumer) |
|---|---|---|---|
| [ProjectName]/Data/ItemData.csv | List of all items, prices, and properties. | **CSV** | Loaded into the **BP_ItemData** Data Table. |
| [ProjectName]/Data/CharacterData.csv| Defines all NPCs, initial dialogue points, and merchant status. | **CSV** | Loaded into the **BP_CharacterData** Data Table. |
| [ProjectName]/Data/Attributes.csv | Defines all trackable character stats (e.g., Charisma). | **CSV** | Loaded into the **BP_AttributeData** Data Table. |
| [ProjectName]/Logic/InteractionMatrix.json| **CRITICAL:** Full list of all puzzle logic. | **JSON** | Parsed by the **BP_InteractionComponent**. |
| [ProjectName]/Dialogues/Graph_[ID].json| The exported node-graph for a specific conversation. | **JSON** | Parsed by the **BP_DialogueManager**. |
| [ProjectName]/UI/WindowLayout.json | Defines the anchoring and contents of all custom menus (Inventory, Stats, Shop). | **JSON** | Used by the **BP_UIManager**. |

---
## 5. Database Schema Documentation

### A. Item Database Schema (Export: ItemData.csv)

| Field Name | Data Type | Description |
|---|---|---|
| id | String | Unique identifier for inventory and logic checks. |
| name | String | Display name for the player. |
| type | String | Categorization: Key Item, Consumable, Currency, Equip. |
| buy_price | Integer | Price to buy the item (set to -1 if non-purchasable). |
| sell_price | Integer | Price to sell the item (set to -1 if unsellable). |

### B. Character Attribute (Stat) Schema (Export: Attributes.csv)

| Field Name | Data Type | Description |
|---|---|---|
| id | String | Unique stat identifier. |
| name | String | Display name on the player stat screen. |
| initial_value | Integer | Starting value for the player. |
| max_value | Integer | Upper limit for the attribute. |

### C. NPC Schema (Export: CharacterData.csv)

| Field Name | Data Type | Description |
|---|---|---|
| id | String | Unique character identifier. |
| default_animation | String | Animation to play when character is idle. |
| dialogue_start_id | String | The ID of the first node in the Logic Graph for conversation start. |
| is_merchant | Boolean | If True, this NPC can open the shop interface. |
| shop_id | String/Null | If a merchant, the ID of the specific shop inventory they sell. |

---
## 6. Interaction Matrix Structure (InteractionMatrix.json)

The Interaction Matrix is an array of objects, where each object defines a possible interaction in the game. The UE Interaction Component iterates through these until it finds a match.

### A. Interaction Object Schema

```json
{
  "scene_id": "String",                 // The scene where this rule applies ("*" for global)
  "target_hotspot_id": "String",        // The object being clicked (e.g., "Door_Office")
  "used_item_id": "String/Null",        // The item dragged onto the hotspot (e.g., "itm_rusty_key", Null if direct click)
  "priority": "Integer",                // Higher number means checked first (used for overrides)
  "conditions": [                       // LIST of Conditions that MUST be TRUE
    {
      "variable_id": "String",          // Global variable/flag (e.g., "Door_State")
      "required_value": "String/Integer"// The required value (e.g., "Locked")
    },
    {
      "check_type": "AttributeCheck",   // Special condition for stats
      "attribute_id": "attr_tech_skill",
      "required_level": "Integer",      // e.g., 5
      "comparison": "String"            // "GE" (Greater than or Equal to)
    }
  ],
  "actions_on_success": [               // LIST of Actions to execute if all conditions are met
    {
      "command": "String",              // See Core Action Commands below
      "parameters": {}                  // Key-value arguments for the command
    }
  ],
  "fallback_dialogue_id": "String/Null" // Dialogue to play if conditions fail (e.g., "dia_door_locked_fail")
}

B. Core Action Commands (Mapped to UE Blueprint Functions)

CommandPurposeExample Parameters (JSON)
SET_VARIABLE Update a global game state variable:{"VarName": "Door_State", "Value": "Unlocked"}
INVENTORY_ADD Gives the player an item:{"ItemID": "itm_wrench", "Quantity": 1}
SCENE_TRANSITION Warps the player to a new scene: {"SceneID": "map_alley_exit", "SpawnPoint": "ExitDoor"}
PLAY_SFX Triggers a sound effect event: {"SoundID": "sfx_door_click", "Volume": 0.8}
SHOP_OPEN Triggers the Shop UI: {"ShopID": "shop_ricky_wares"}
MODIFY_ATTRIBUTE Changes a character's attribute value: {"Attribute": "attr_charisma", "Value": 1, "Operation": "Add"}
