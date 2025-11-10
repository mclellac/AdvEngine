# Core Concepts

This document explains the core concepts of the AdvEngine and how the different editors work together to create a game.

## The Big Picture: Cause and Effect

The easiest way to think about the AdvEngine is in terms of **cause and effect**. The player does something (**cause**), and the game responds (**effect**). The AdvEngine provides different editors to define these causes and effects.

- **Cause:** The player's action. This is defined in the **Interaction Editor**.
- **Effect:** The game's response. This is scripted in the **Logic Editor**.

## The Editors

### 1. Interaction Editor

The **Interaction Editor** is where you define the **player's actions**. These are the "verbs" of your game. For example:

- `Use` `Keycard` on `Door`
- `Talk to` `Sparky`
- `Look at` `Alien Artifact`

Each interaction you define here is a potential **cause**. When the player performs one of these actions, the game will trigger the **effect** you've associated with it. That effect is a **Logic Graph**.

### 2. Logic Editor

The **Logic Editor** is where you script the **consequences** of the player's actions. Each **Logic Graph** is a flowchart of events that happens when an interaction is triggered. The Logic Editor has three main types of nodes:

- **Condition Nodes:** These check the state of the game. For example, "Does the player have the `alien_artifact`?" or "Is the `power_on` variable `true`?".
- **Action Nodes:** These make something happen in the game. For example, "Start the `repair_droid` quest", "Set the `door_open` variable to `true`", or "Play the `explosion` sound".
- **Dialogue Nodes:** These are for simple, one-off lines of dialogue, usually from an NPC or the narrator. For example, "The door is locked." or "You can't do that right now.".

### 3. Dialogue Editor

The **Dialogue Editor** is a specialized tool for creating and managing complex, branching conversations. While you can use Dialogue Nodes in the Logic Editor for simple barks, the Dialogue Editor is where you'll write the rich, interactive conversations that are the heart of an adventure game.

The Dialogue Editor uses a tree structure to make it easy to see the flow of a conversation and create different branches based on the player's choices.

### Summary

| Editor | Purpose | Analogy |
|---|---|---|
| **Interaction Editor** | Defines the player's actions (the "cause"). | The "if" part of an "if/then" statement. |
| **Logic Editor** | Scripts the game's response (the "effect"). | The "then" part of an "if/then" statement. |
| **Dialogue Editor** | Manages complex, branching conversations. | A dedicated tool for writing a screenplay. |

By using these three editors together, you can create a rich and interactive adventure game.
