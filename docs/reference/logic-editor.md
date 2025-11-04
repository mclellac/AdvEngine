# Editor Reference: Logic Editor

The Logic Editor is the most powerful and complex tool in AdvEngine. It is a general-purpose, node-based visual scripting interface that allows you to create the underlying mechanics for all interactivity in your game, from simple puzzles to complex, branching quests.

## 1. Purpose

The Logic Editor is used to create **Logic Graphs**. A Logic Graph is a collection of nodes that define a flow of events, conditions, and actions. These graphs are the "brains" behind your game's interactivity. They are executed by other systems, most commonly the **Interaction Editor**, which triggers a specific Logic Graph when the player interacts with the world.

## 2. Interface Overview

The Logic Editor interface consists of a graph list, the main canvas, and a properties panel.

![Logic Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Graph List

On the left, a list displays all the generic Logic Graphs in your project. You can create, select, and delete graphs from this list.

### B. Canvas

This is the main visual workspace where you build your logic.
-   **Nodes**: Each box on the canvas is a node, representing a step in your logic. Different colors denote different node types.
-   **Connections**: The lines between nodes represent the flow of logic. The output of one node is connected to the input of another.
-   **Navigation**: Zoom with `Ctrl + Mouse Wheel` and pan with a **middle-mouse click and drag**.
-   **Context Menu**: **Right-clicking** on the canvas opens a menu that allows you to add new nodes to the graph.

### C. Properties Panel

When a node is selected on the canvas, the panel on the right displays its properties, allowing you to edit its parameters without a disruptive dialog.

## 3. Node Types

There are three main types of nodes you can create in the Logic Editor.

### A. `StartNode` (Implicit)

Every logic graph has an implicit "Start" point. The flow of logic begins at the first node that has no inputs connected to it. It's best practice to design your graph with a clear starting node.

### B. `ConditionNode` (Green Header)

A Condition Node checks if a certain state in the game is true. It has two outputs: one for **Success** (the condition is met) and one for **Failure** (the condition is not met). This allows you to create branching logic.

-   **To Create**: Right-click on the canvas and select "Add Condition Node."
-   **Properties**:
    -   **Variable ID**: The ID of the `GlobalVariable` (from the Global State Editor) to check.
    -   **Operator**: The comparison to perform (e.g., `==`, `!=`, `>`, `<`).
    -   **Required Value**: The value to compare against the variable's current value.

**Example**: A `ConditionNode` could check if `has_found_keycard` is `==` to `true`.

### C. `ActionNode` (Blue Header)

An Action Node performs a specific action in the game, suchas giving an item to the player, transitioning to another scene, or displaying dialogue.

-   **To Create**: Right-click on the canvas and select "Add Action Node."
-   **Properties**:
    -   **Command**: A dropdown list of all available commands in the game engine.
    -   **Parameters**: A set of fields for the arguments required by the selected command.

## 4. Core Action Commands

The following is a reference of the most common `ActionNode` commands. For a complete and definitive list, refer to the `COMMAND_DEFINITIONS` in `src/core/ue_exporter.py`.

| Command | Description | Parameters |
| :--- | :--- | :--- |
| `SET_VARIABLE` | Updates a global game state variable. | `variable_id` (String), `new_value` (String) |
| `INVENTORY_ADD`| Adds an item to the player's inventory. | `item_id` (String) |
| `INVENTORY_REMOVE` | Removes an item from the player's inventory. | `item_id` (String) |
| `SCENE_TRANSITION`| Moves the player to a new scene. | `scene_id` (String) |
| `SHOW_DIALOGUE` | Displays a line or tree of dialogue. | `dialogue_graph_id` (String), `initial_node_id` (String) |
| `PLAY_CINEMATIC`| Triggers a cutscene. | `cutscene_id` (String) |
| `PLAY_SFX` | Plays a sound effect. | `sfx_id` (String) |

## 5. Workflow: Building a Simple Logic Graph

This example creates a graph that checks if the player has a "coin" and, if so, takes the coin and unlocks a door (by setting a variable).

1.  **Create the Graph**: In the Logic Editor, create a new graph named `vending_machine_logic`.
2.  **Add a Condition Node**:
    -   Right-click the canvas and add a `ConditionNode`.
    -   Set its properties: `variable_id`: `player_has_coin`, `Operator`: `==`, `Required Value`: `true`.
3.  **Add an Action Node (Success Path)**:
    -   Add an `ActionNode`.
    -   Set its command to `INVENTORY_REMOVE` and its `item_id` to `coin`.
4.  **Add a Second Action Node (Success Path)**:
    -   Add another `ActionNode`.
    -   Set its command to `SET_VARIABLE`, `variable_id` to `door_is_unlocked`, and `new_value` to `true`.
5.  **Connect the Nodes**:
    -   Click and drag from the `Success` output of the `ConditionNode` to the input of the `INVENTORY_REMOVE` node.
    -   Click and drag from the output of the `INVENTORY_REMOVE` node to the input of the `SET_VARIABLE` node.

Now, when this graph is triggered, it will correctly check for the coin and update the game state, demonstrating a complete, conditional logic flow.
