# Editor Reference: Cutscene Editor

The Cutscene Editor provides a simple, script-based method for creating cinematic sequences in your game. Unlike the node-based Logic Editor, the Cutscene Editor is designed for linear, sequential events, making it ideal for moments where you want to take control away from the player to show a character performing a series of actions.

## 1. Purpose

-   **Create Linear Sequences**: Script events that happen in a predefined order.
-   **Control Characters**: Make characters walk to specific points, turn, or play animations.
-   **Display Dialogue**: Have characters speak lines of dialogue outside of an interactive conversation.
-   **Manage Game State**: Trigger actions like giving items or setting variables during a cutscene.

## 2. Interface Overview

The Cutscene Editor has a very straightforward interface consisting of a cutscene list and a text editor.

![Cutscene Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Cutscene List

On the left, this list displays all the cutscenes in your project. You can create, select, and delete cutscenes.

### B. Script Editor

The main area is a simple text editor where you write the script for the selected cutscene. Each line in the script represents a single `CutsceneAction`.

## 3. The `CutsceneAction` Scripting Format

A cutscene is simply a list of actions that are executed one after another. Each action is written on a new line and follows a `COMMAND: parameters` format. The parameters are provided as a comma-separated list of `key=value` pairs.

### Example Script

```
# This is a comment. It will be ignored.
WALK: character_id=player, x=150, y=200
SAY: character_id=player, dialogue_text="I need to get through that door."
WAIT: duration=2.0
SET_VARIABLE: variable_id=door_is_unlocked, new_value=true
```

## 4. Common Commands

The following commands are available for use in the Cutscene Editor.

| Command | Description | Parameters |
| :--- | :--- | :--- |
| `WALK` | Moves a character to a specific coordinate on the scene. | `character_id`, `x`, `y` |
| `SAY` | Makes a character speak a line of dialogue. | `character_id`, `dialogue_text` |
| `TURN` | Changes the direction a character is facing. | `character_id`, `direction` (e.g., "left", "right", "up", "down") |
| `WAIT` | Pauses the cutscene for a specified duration. | `duration` (in seconds) |
| `PLAY_ANIMATION` | Plays a specific animation on a character. | `character_id`, `animation_name` |
| `SET_VARIABLE` | Updates a global game state variable. | `variable_id`, `new_value` |
| `INVENTORY_ADD`| Adds an item to the player's inventory. | `item_id` |
| `PLAY_SFX` | Plays a sound effect. | `sfx_id` |

## 5. Workflow: Creating a Simple Cutscene

This workflow creates a cutscene where the player character walks to a door and says something.

1.  **Create the Cutscene**: In the Cutscene Editor, click "+" to create a new cutscene and give it the ID `player_approaches_door`.
2.  **Write the Script**: In the text editor for the new cutscene, type the following:
    ```
    # Player walks to the door's location
    WALK: character_id=player, x=250, y=180

    # Player turns to face the door
    TURN: character_id=player, direction=up

    # Player says a line
    SAY: character_id=player, dialogue_text="It seems to be locked."
    ```
3.  **Trigger the Cutscene**: To make this cutscene play in the game, you would typically create an `Interaction` (e.g., when the player clicks on the door) that executes a `LogicGraph` containing a single `ActionNode` with the command `PLAY_CINEMATIC` and the `cutscene_id` parameter set to `player_approaches_door`.
