# Editor Reference: Database Editors

AdvEngine uses a suite of database editors to manage the various "things" that make up your game world, such as items, characters, and verbs. All of these editors share a consistent, modern, spreadsheet-like interface designed for efficiency.

## 1. Common Interface and Functionality

All database editors are built upon a `Gtk.ColumnView` and provide a consistent set of features for managing data.

![Database Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

-   **Spreadsheet-like View**: Data is presented in a table with rows and columns, which can be sorted by clicking on the column headers.
-   **Inline Editing**: To edit a field, simply click on it and type. Changes are saved automatically as you move to another cell or row. This avoids the need for disruptive modal dialogs.
-   **Search/Filter**: A search bar at the top of the editor allows you to filter the list in real-time. The search will match against all fields for each item.
-   **Add/Remove Buttons**: At the bottom of the editor, "+" and "-" buttons allow you to add new rows (creating new data entries) or delete the currently selected row.
-   **Full CRUD**: The interface provides full Create (Add), Read (View), Update (Edit), and Delete (Remove) functionality for all data types.

## 2. Item Editor

The Item Editor manages all the items that can exist in your game, from key items and puzzle pieces to consumables and equipment.

-   **File**: `[ProjectName]/Data/ItemData.csv`
-   **Purpose**: To define the properties of every item the player can acquire or interact with.

### Schema (Fields)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the item. This is used internally to reference the item in logic graphs and scripts (e.g., `keycard`). **Must be unique.** |
| `name` | String | The display name for the item as it appears to the player in the UI (e.g., "Security Keycard"). |
| `description`| String | The text that appears when the player "looks at" the item in their inventory. |

## 3. Character Editor

The Character Editor manages all the non-player characters (NPCs) in your game.

-   **File**: `[ProjectName]/Data/CharacterData.csv`
-   **Purpose**: To define the properties of every character, including their appearance and basic behavior.

### Schema (Fields)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the character (e.g., `jane_doe`). **Must be unique.** |
| `display_name` | String | The character's name as it appears in dialogue boxes (e.g., "Jane Doe"). |
| `portrait_asset_id` | String | The ID of the asset (from the Asset Manager) to be used as this character's portrait in dialogues. A preview is shown in the editor. |
| `sprite_sheet_asset_id` | String | The ID of the asset to be used for the character's in-game sprite. |
| `animations` | String (JSON) | A JSON string defining the character's animations, mapping animation names (e.g., "idle", "walk") to sprite sheet frames. |

## 4. Attribute Editor

The Attribute Editor manages character attributes or stats.

-   **File**: `[ProjectName]/Data/Attributes.csv` (Note: File not created by default, but is used if present)
-   **Purpose**: To define stats that can be tracked and modified for characters (e.g., Strength, Tech Skill).

### Schema (Fields)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the attribute (e.g., `tech_skill`). **Must be unique.** |
| `name` | String | The display name for the attribute in the UI (e.g., "Tech Skill"). |

## 5. Verb Editor

The Verb Editor manages the actions the player can perform.

-   **File**: `[ProjectName]/Data/Verbs.json`
-   **Purpose**: To define the list of verbs that appear in the game's UI (e.g., on a verb coin or in a right-click menu).

### Schema (Fields)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the verb (e.g., `use`). **Must be unique.** |
| `name` | String | The display name for the verb in the UI (e.g., "Use"). |

## 6. Global State Editor

The Global State Editor manages all the global variables for your game. These variables are used to track story progress, puzzle states, and any other persistent data.

-   **File**: `[ProjectName]/Data/GlobalState.json`
-   **Purpose**: To create a central repository of flags and variables that your logic graphs can check and modify.

### Schema (Fields)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the variable (e.g., `has_found_keycard`). **Must be unique.** |
| `initial_value`| String | The value the variable should have at the start of a new game (e.g., `false`, `0`, or an empty string). |
