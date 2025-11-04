# Editor Reference: Interaction Editor

The Interaction Editor is the critical link between the player's actions, the game world, and the underlying game logic. Its purpose is to define what happens when the player attempts to use a verb or an inventory item on a hotspot or another item. Each of these definitions, or "Interactions," triggers a **Logic Graph**.

## 1. Purpose

The Interaction Editor answers the core question of adventure games: "What happens when I do this?"
-   **Define Player Actions**: It allows you to script the outcome of actions like `Use keycard on door` or `Look at strange device`.
-   **Connect Assets**: It connects `Verbs` and `Items` (from the Database) with `Hotspots` (from the Scene Editor).
-   **Trigger Logic**: It serves as the primary trigger for executing the complex `LogicGraph`s you build in the Logic Editor.

Without the Interaction Editor, the scenes and logic graphs would be disconnected islands of data. This editor builds the bridges between them.

## 2. Interface Overview

The Interaction Editor uses a spreadsheet-like interface, similar to the database editors, to display a list of all interactions in the project.

![Interaction Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

-   **Interaction List**: The main view is a table where each row represents one unique interaction.
-   **Inline Editing**: All fields can be edited directly in the table by clicking on them. Dropdown menus are provided for selecting Verbs, Items, Hotspots, and Logic Graphs, which prevents typos and ensures you are using valid IDs.
-   **Add/Remove Buttons**: Use the "+" and "-" buttons at the bottom to create or delete interactions.

## 3. Interaction Schema (Fields)

Each interaction is defined by a set of properties that specify the conditions for it to trigger and the logic it should execute.

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | A unique identifier for the interaction itself (e.g., `unlock_closet_door`). |
| `verb_id` | String (Dropdown)| The `Verb` the player must use. For direct clicks, this is typically left empty or set to a default "use" verb. |
| `primary_item_id`| String (Dropdown)| The `Item` from the player's inventory that must be used. This is often left empty for interactions that don't require an item (like "Look At"). |
| `secondary_item_id` | String (Dropdown)| For `Item + Item` combinations. The second item the player must use. |
| `target_hotspot_id` | String (Dropdown)| The `Hotspot` in a scene that the interaction applies to. |
| `logic_graph_id`| String (Dropdown)| The `LogicGraph` to execute when this interaction is triggered. **This is the most important field.** |
| `initial_node_id`| String (Dropdown)| **(For Dialogue)** If the `logic_graph_id` points to a `DialogueGraph`, this field specifies which `DialogueNode` should be displayed first. |

## 4. Workflows

### A. Creating a "Use Item on Hotspot" Interaction

This is the most common type of interaction for puzzles. The example creates the interaction for using a keycard on a locked door.

1.  **Prerequisites**: Before creating the interaction, ensure you have already created:
    -   The `use` verb in the **Verb Editor**.
    -   The `keycard` item in the **Item Editor**.
    -   The `closet_door` hotspot in the **Scene Editor**.
    -   The `unlock_door_logic` graph in the **Logic Editor**.
2.  **Navigate**: Open the **Interaction Editor**.
3.  **Create Interaction**: Click the "+" button to add a new row.
4.  **Fill the Fields**:
    -   `id`: `unlock_closet_door_with_keycard`
    -   `verb_id`: `use`
    -   `primary_item_id`: `keycard`
    -   `target_hotspot_id`: `closet_door`
    -   `logic_graph_id`: `unlock_door_logic`

Now, when the player is in the scene with the "closet_door" and uses the "keycard" on it, the "unlock_door_logic" graph will run.

### B. Creating a "Look At Hotspot" Interaction

This workflow defines what happens when the player simply looks at an object.

1.  **Prerequisites**:
    -   The `look` verb.
    -   The `closet_door` hotspot.
    -   A `DialogueGraph` named `general_descriptions` with a `DialogueNode` inside it with the ID `door_is_locked_desc` and the text "The door appears to be locked."
2.  **Create Interaction**: Add a new interaction.
3.  **Fill the Fields**:
    -   `id`: `look_at_locked_door`
    -   `verb_id`: `look`
    -   `target_hotspot_id`: `closet_door`
    -   `logic_graph_id`: `general_descriptions`
    -   `initial_node_id`: `door_is_locked_desc`

This interaction will trigger the dialogue system to display a simple text description when the player looks at the door.
