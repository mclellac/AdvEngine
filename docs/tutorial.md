# Tutorial: Your First Adventure Game Puzzle

This tutorial will guide you through creating a simple, single-room puzzle in AdvEngine, inspired by classic Sierra On-Line adventure games like *Space Quest*.

## The Scenario

Our hero finds themselves locked in a storage closet. They need to find a hidden keycard to unlock the door and escape to the hallway.

**Goals:**
1.  The player can "look at" the door to see that it's locked.
2.  The player can "look at" a loose wall panel to get a hint.
3.  The player can "use" the loose wall panel to reveal a hidden keycard, which is added to their inventory.
4.  The player can "use" the keycard on the door to unlock it and transition to the next scene.

## Step 1: Create the Database Entries

First, we need to define the verbs and items for our puzzle.

1.  Navigate to the **Database** editor from the sidebar. This view contains tabs for Items, Attributes, and Verbs.
2.  Select the **Verbs** tab and create two new verbs:
    *   `id: "look", name: "Look At"`
    *   `id: "use", name: "Use"`
3.  Select the **Items** tab and create the keycard:
    *   **id:** `keycard`
    *   **name:** `Security Keycard`
    *   **description:** `A standard issue level 2 security keycard.`

## Step 2: Set up the Scene

Now, let's create the visual space for our puzzle.

1.  Open the **Scenes** editor from the sidebar.
2.  Create a new scene with the ID `StorageCloset`.
3.  With the new scene selected, use the properties panel on the right to set a background image.
4.  Create two hotspots by clicking and dragging on the canvas:
    *   One over the door, with the ID `closet_door`.
    *   One over the loose wall panel, with the ID `loose_panel`.

## Step 3: Create the Dialogue and Logic

We need to create the text that will be displayed to the player and the logic that will control the puzzle.

1.  Navigate to the **Dialogue** editor. Create a new dialogue graph with the ID `closet_dialogue`.
2.  Add the following dialogue nodes to this graph:
    *   `door_locked_text`: "The door is locked tight."
    *   `panel_hint_text`: "The wall panel looks loose."
    *   `found_keycard_text`: "You pry open the panel and find a keycard!"
3.  Navigate to the **Logic** editor. Create a new logic graph with the ID `unlock_door_logic`.
4.  In this graph, create a single **Action Node**:
    *   **Command:** `SCENE_TRANSITION`
    *   **Parameters:** `{"scene_id": "Hallway"}` (This assumes you've created a "Hallway" scene to transition to).

## Step 4: Define the Interactions

This is where we connect all the pieces.

1.  Navigate to the **Interactions** editor. This is where you'll define the rules of your puzzle.

2.  **Interaction 1: Look at the locked door.**
    *   Create a new interaction.
    *   **Verb:** `look`
    *   **Primary Item:** (Leave empty)
    *   **Target Hotspot:** `closet_door`
    *   **Logic Graph:** `closet_dialogue`
    *   **Initial Node:** `door_locked_text`

3.  **Interaction 2: Look at the loose panel.**
    *   Create a new interaction.
    *   **Verb:** `look`
    *   **Primary Item:** (Leave empty)
    *   **Target Hotspot:** `loose_panel`
    *   **Logic Graph:** `closet_dialogue`
    *   **Initial Node:** `panel_hint_text`

4.  **Interaction 3: Find the keycard.**
    *   We need a logic graph for this. Go back to the **Logic** editor and create a new graph called `get_keycard_logic`.
    *   Inside this graph, create two **Action Nodes** and connect them in sequence:
        1.  `command: "INVENTORY_ADD", parameters: {"item_id": "keycard"}`
        2.  `command: "SHOW_DIALOGUE", parameters: {"dialogue_graph_id": "closet_dialogue", "initial_node_id": "found_keycard_text"}`
    *   Now, back in the **Interactions** editor, create the interaction:
        *   **Verb:** `use`
        *   **Target Hotspot:** `loose_panel`
        *   **Logic Graph:** `get_keycard_logic`

5.  **Interaction 4: Unlock the door.**
    *   Create the final interaction:
    *   **Verb:** `use`
    *   **Primary Item:** `keycard`
    *   **Target Hotspot:** `closet_door`
    *   **Logic Graph:** `unlock_door_logic`

## Step 5: Save and Play!

You've done it! You have created a complete, fully functional puzzle.

1.  Click the **Save** button in the header bar to save your project.
2.  Click the **Play** button to launch the game and test your puzzle.

From here, you can create the `Hallway` scene, add more items and characters, and build out your game's world and narrative. Congratulations!
