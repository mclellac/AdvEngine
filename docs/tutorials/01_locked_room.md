# Tutorial: Creating Your First Puzzle

This tutorial will guide you through creating a complete, interactive puzzle in AdvEngine. We will build the classic "locked room" scenario from start to finish, touching on almost every major editor in the application.

## 1. Scenario

Our hero is locked in a storage closet. To escape, they must:
1.  Realize the door is locked.
2.  Find a hidden keycard behind a loose wall panel.
3.  Unlock the door with the keycard and move to the next scene.

This tutorial will guide you through setting up the required quest, all the interactive elements, and the underlying logic.

## 2. Step 1: Setting up the Database

First, we need to define the raw data for our puzzle.

1.  Navigate to the **Database** editor.
2.  In the **Verbs** tab, create two verbs: `look` ("Look At") and `use` ("Use").
3.  In the **Items** tab, create one item: `id: keycard`, `name: Security Keycard`, `description: A standard issue security keycard.`
4.  In the **Global State** editor, create one variable: `id: panel_is_open`, `initial_value: false`.

> **Learn More**: For a detailed explanation of each field, see the [Database Editors Reference](../reference/database-editors.md).

## 3. Step 2: Creating the Quest

Let's define the quest that will track the player's progress.

1.  Navigate to the **Quest Editor**.
2.  Create a new quest with the ID `escape_the_closet` and the name "Escape the Closet".
3.  Add two steps to this quest:
    1.  `id: find_keycard`, `display_name: "I need to find a way to unlock the door."`
    2.  `id: unlock_door`, `display_name: "I have the keycard. Now I can unlock the door."`

> **Learn More**: For details on how the quest system works, see the [Quest Editor Reference](../reference/quest-editor.md).

## 4. Step 3: Building the Scene

Now, we'll create the visual environment.

1.  Navigate to the **Scene Editor**.
2.  Create two new scenes: `storage_closet` and `hallway`.
3.  For the `storage_closet` scene, import a background image.
4.  In the `storage_closet` scene, create two hotspots: `closet_door` and `loose_panel`.

> **Learn More**: For a full guide on canvas controls and layers, see the [Scene Editor Reference](../reference/scene-editor.md).

## 5. Step 4: Writing the Dialogue and Logic

This is the most involved step. We need to create the text and the logic graphs that will drive the puzzle.

### A. Dialogue

1.  Navigate to the **Dialogue Editor**.
2.  Create a new `DialogueGraph` called `closet_text`.
3.  Add the following `DialogueNode`s to this graph:
    *   `door_locked`: "The door is locked."
    *   `panel_closed`: "A wall panel. It looks loose."
    *   `panel_open`: "I've already opened this panel."
    *   `found_keycard`: "I pried the panel open and found a keycard!"

### B. Logic Graphs

Navigate to the **Logic Editor** and create the following three graphs.

1.  **`look_at_panel_logic`**:
    -   This graph will decide which line of dialogue to show when the player looks at the panel.
    -   **Nodes**:
        1.  A `ConditionNode` that checks if `panel_is_open == false`.
        2.  An `ActionNode` (on Success) with `command: SHOW_DIALOGUE`, `dialogue_graph_id: closet_text`, `initial_node_id: panel_closed`.
        3.  An `ActionNode` (on Failure) with `command: SHOW_DIALOGUE`, `dialogue_graph_id: closet_text`, `initial_node_id: panel_open`.

2.  **`use_panel_logic`**:
    -   This graph will handle the logic for opening the panel and getting the keycard.
    -   **Nodes**:
        1.  A `ConditionNode` that checks if `panel_is_open == false`.
        2.  An `ActionNode` (on Success) with `command: SET_VARIABLE`, `variable_id: panel_is_open`, `new_value: true`.
        3.  A second `ActionNode` (connected after the first) with `command: INVENTORY_ADD`, `item_id: keycard`.
        4.  A third `ActionNode` to show dialogue: `command: SHOW_DIALOGUE`, `dialogue_graph_id: closet_text`, `initial_node_id: found_keycard`.
        5.  A fourth `ActionNode` to update the quest: `command: SET_VARIABLE`, `variable_id: quest_escape_the_closet`, `new_value: unlock_door`.
        6.  An `ActionNode` (on Failure) to show the "already open" dialogue, same as in the graph above.

3.  **`unlock_door_logic`**:
    -   This graph will simply transition to the next scene.
    -   **Nodes**:
        1.  A single `ActionNode` with `command: SCENE_TRANSITION`, `scene_id: hallway`.

> **Learn More**: For a list of all commands and node types, see the [Logic Editor Reference](../reference/logic-editor.md).

## 6. Step 5: Defining the Interactions

Finally, let's wire everything together.

1.  Navigate to the **Interaction Editor**.
2.  Create the following interactions:
    *   **Look at door**: `verb: look`, `hotspot: closet_door`, `logic: closet_text`, `initial_node: door_locked`.
    *   **Look at panel**: `verb: look`, `hotspot: loose_panel`, `logic: look_at_panel_logic`.
    *   **Use panel**: `verb: use`, `hotspot: loose_panel`, `logic: use_panel_logic`.
    *   **Use keycard on door**: `verb: use`, `item: keycard`, `hotspot: closet_door`, `logic: unlock_door_logic`.

> **Learn More**: For details on how interactions work, see the [Interaction Editor Reference](../reference/interaction-editor.md).

## 7. Conclusion

You have now created a complete, multi-step puzzle that uses a wide variety of AdvEngine's features. Click the **Save** button, then **Play** to test your work.

From here, you can flesh out the `hallway` scene, add more complex logic, and continue to build your game. Congratulations!
