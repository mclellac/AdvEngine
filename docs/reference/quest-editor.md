> **Note:** This document describes the planned functionality of the Quest Editor. As of the current version, this feature is not yet implemented and the editor is a non-functional placeholder.

# Editor Reference: Quest Editor

The Quest Editor is a dedicated tool for defining and managing structured quests for the player to complete. It allows you to create high-level objectives and break them down into smaller, sequential steps.

## 1. Purpose

-   **Structure Player Objectives**: Create formal quests that can be displayed to the player in a journal or log.
-   **Track Progress**: Break down large goals into smaller, manageable steps.
-   **Link to Logic**: Use the quest state in your `LogicGraph`s to create conditional logic (e.g., an NPC only appears after a certain quest step is completed).

## 2. Data Model: `Quest` and `QuestStep`

The quest system is built on two main data structures:

-   **`Quest`**: The high-level container for a single quest. It has a name, a description, and contains one or more `QuestStep`s.
-   **`QuestStep`**: A single, concrete objective within a quest. Steps are ordered and are typically completed sequentially.

## 3. Interface Overview

The Quest Editor uses a two-pane layout.

![Quest Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Quest List

The left pane displays a list of all the `Quest` objects in your project. You can add, select, and delete quests here.

### B. Quest Step Editor

When you select a quest from the list, the right pane displays an editor for its `QuestStep`s.
-   **Step List**: A list of all the steps for the selected quest. You can add, delete, and reorder steps using drag-and-drop.
-   **Step Properties**: When you select a step from the list, you can edit its properties (ID, Display Name, etc.) in a dedicated area.

## 4. Schema

### A. `Quest` Schema

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the quest (e.g., `main_quest_01`). |
| `name` | String | The display name of the quest as it appears in the UI (e.g., "Find a Way Out"). |
| `description`| String | A longer description of the quest's overall goal. |
| `steps` | List[`QuestStep`] | The ordered list of steps that make up this quest. |

### B. `QuestStep` Schema

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for this specific step (e.g., `find_keycard`). |
| `display_name` | String | The text that describes this objective to the player (e.g., "Find a keycard to unlock the door."). |

## 5. Workflow: Creating a Simple Quest

This workflow creates a simple, two-step quest for our "locked room" scenario.

1.  **Create the Quest**:
    -   In the Quest Editor, click the "+" button in the left **Quest List** pane.
    -   Give the new quest the following properties:
        -   `id`: `escape_the_closet`
        -   `name`: "Escape the Closet"
        -   `description`: "I'm locked in this storage closet. I need to find a way to open the door."
2.  **Add the First Step**:
    -   With the "Escape the Closet" quest selected, click the "+" button in the right **Quest Step Editor** pane.
    -   Select the new step and give it the following properties:
        -   `id`: `find_the_keycard`
        -   `display_name`: "Find the keycard."
3.  **Add the Second Step**:
    -   Click the "+" button in the Quest Step Editor again.
    -   Select this second step and give it these properties:
        -   `id`: `unlock_the_door`
        -   `display_name`: "Use the keycard to unlock the door."
4.  **Managing Quest State**:
    -   The quest system automatically creates global variables to track the state of quests. For example, `quest_escape_the_closet` will track the current active step ID.
    -   To advance the quest, you would use an `ActionNode` in a `LogicGraph`. For example, after the player picks up the keycard, you would have an action: `command: "SET_VARIABLE", variable_id: "quest_escape_the_closet", new_value: "unlock_the_door"`. This would mark the first step as complete and activate the second.
