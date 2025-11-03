# Tutorial: Your First Adventure Game Level

This tutorial will guide you through creating a simple, single-room puzzle in AdvEngine, inspired by classic Sierra On-Line adventure games like *Space Quest*.

## The Scenario

Our hero, a hapless space janitor, finds himself locked in the ship's storage closet. He needs to find a hidden keycard to unlock the door and escape to the hallway.

**Goal:**
1.  The player can look at the door and a loose wall panel.
2.  The player can click on the wall panel to reveal a hidden keycard.
3.  The player can use the keycard on the door to unlock it and move to the next area.

## Step 1: Create the Scene

First, we need to create the visual space for our puzzle.

1.  Open the **Scenes** module from the main navigation.
2.  Click the "New Scene" button and give it an ID, for example, `StorageCloset`.
3.  With your new scene selected, find the "Background Image" property in the editor panel. Click to import an image of a storage closet.
4.  Next, we need to tell the game where the player can walk. Select the **Walk Mesh** tool.
5.  Click on the image to draw a polygon that covers the floor area. This is the walkable surface for your character.

## Step 2: Add Hotspots

Hotspots are the interactive elements in your scene. We need two: the door and the loose wall panel.

1.  Select the **Hotspot** tool in the Scene Editor.
2.  Draw a rectangle over the door. In the properties panel, give it a unique ID like `ClosetDoor`.
3.  Draw another rectangle over the loose panel on the wall. Give it the ID `LoosePanel`.

Your scene is now visually set up!

## Step 3: Create Verbs and the Keycard Item

First, we need to define the actions the player can take.

1.  Navigate to the **Verbs & Items** module.
2.  Select the "Verbs" tab.
3.  Add a few basic verbs:
    *   `id: "look", name: "Look At"`
    *   `id: "use", name: "Use"`

Now, let's create the keycard.

1.  Select the "Items" tab.
2.  Add a new row and fill out the details:
    *   **id:** `Keycard`
    *   **name:** `Security Keycard`
    *   **description:** `A standard issue level 2 security keycard. Looks slightly worn.`
    *   Leave the other fields at their default values for now.

## Step 4: Script the Puzzle Logic

This is where we bring the scene to life. Go to the **Logic** module. The node graph here defines all the cause-and-effect rules for your game.

### Logic Rule 1: Finding the Keycard

1.  Create a new logic block. We'll use this to define what happens when the player clicks the loose panel.
2.  Set the **Target Hotspot ID** to `LoosePanel`.
3.  Leave the **Used Item ID** empty, as this is a direct click interaction.
4.  **Add a Condition:** We only want this to work once.
    *   Create a condition node: `variable_id: "FoundClosetKey", required_value: "false"`
5.  **Add an Action on Success:** If the condition is met:
    *   Create an action node: `command: "INVENTORY_ADD", parameters: {"ItemID": "Keycard"}`
    *   Create a second action node: `command: "SET_VARIABLE", parameters: {"VarName": "FoundClosetKey", "Value": "true"}`
    *   (Optional) Add a dialogue node to say "You found a keycard!"

### Logic Rule 2: Unlocking the Door

1.  Create another logic block. This will handle using the keycard on the door.
2.  Set the **Target Hotspot ID** to `ClosetDoor`.
3.  Set the **Used Item ID** to `Keycard`.
4.  **Add an Action on Success:** No conditions are needed here. If the player uses the key on the door, it should always work.
    *   Create an action node: `command: "SCENE_TRANSITION", parameters: {"SceneID": "Hallway"}` (Assuming you have another scene with this ID).

### Logic Rule 3: Locked Door Message

1.  Create one more logic block for when the player just clicks on the door.
2.  Set the **Target Hotspot ID** to `ClosetDoor`.
3.  Leave **Used Item ID** empty.
4.  **Add an Action on Success:**
    *   Add a dialogue node that says: `"The door is locked tight."`
5.  **Set Priority:** In the properties for this logic block, set the `priority` to a lower number (e.g., `0`) than the "Unlock Door" logic (e.g., `1`). This ensures the game checks for the keycard interaction *first*.

## Step 5: Export and Play

You've done it! You have created a complete, albeit small, puzzle.

1.  From the main menu, select `File > Export for Unreal Engine`.
2.  Choose a destination folder.

AdvEngine will generate the necessary data files. You can now drop these into the AdvEngine UE Template project, and your storage closet scene will be playable.

From here, you can create the `Hallway` scene, add more items, and build out your game's world and narrative. Congratulations!
