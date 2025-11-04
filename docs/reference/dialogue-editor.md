# Editor Reference: Dialogue Editor

The Dialogue Editor is a specialized tool for creating and managing interactive conversations with characters. While the generic Logic Editor is used for gameplay mechanics, the Dialogue Editor is optimized for the unique structure of branching narratives. It uses a tree view, which is a more natural and intuitive way to write and organize conversations than a node graph.

## 1. Purpose

-   **Write Branching Conversations**: Create complex dialogues with multiple player choices and NPC responses.
-   **Structure Narrative**: Organize conversations in a hierarchical, easy-to-read tree format.
-   **Trigger Mid-Dialogue Actions**: Embed actions directly into a conversation, such as giving the player an item or setting a variable after a specific line of dialogue.
-   **Link to Characters**: Associate dialogues with characters and display their portraits.

## 2. Interface Overview

The Dialogue Editor is composed of a dialogue graph list, the main tree view, and a properties panel for editing nodes.

![Dialogue Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Dialogue Graph List

On the left, this list displays all the `DialogueGraph`s in your project. Each graph typically represents a complete conversation with a single character or a set of related conversational topics.

### B. Tree View

This is the central workspace where you build your conversation.
-   **Nodes**: Each item in the tree is a node. The indentation of the nodes shows the parent-child relationships.
-   **Hierarchy**: NPC lines are parents, and the player's possible responses are their children. The NPC's reply to a player choice becomes a child of that choice.
-   **Context Menu**: **Right-clicking** on a node in the tree opens a menu with options to add a new NPC line, add a player choice, add an action, or delete the selected node.

### C. Properties Panel

When a node is selected in the tree, its properties are displayed in the panel on the right, allowing for non-modal editing.

## 3. Node Types

The Dialogue Editor uses two primary node types from the `LogicGraph` schema, but presents them in a unique, hierarchical way.

### A. `DialogueNode` (Represents a line of speech)

This is the most common node type and represents a single line of dialogue spoken by either an NPC or the player.

-   **Properties**:
    -   **ID**: A unique identifier for this node (e.g., `jane_hello`).
    -   **Character ID**: The ID of the `Character` who is speaking this line. Their portrait will be displayed in the properties panel as a preview. If this is a player choice, this field is left empty.
    -   **Dialogue Text**: The line of speech itself.
    -   **Is Player Choice**: A checkbox that designates this line as a selectable option for the player, rather than a line spoken by an NPC.

### B. `ActionNode` (Represents a game event)

You can embed `ActionNode`s directly into the dialogue tree. This allows you to trigger game events as a result of a conversation. These appear as distinct leaf nodes in the tree, often colored differently.

-   **Use Case**: This is incredibly powerful for narrative design. For example, a player might select a dialogue option that pleases an NPC, and you can attach an `ActionNode` right after the NPC's happy response to `INVENTORY_ADD` a reward item to the player's inventory.
-   **Properties**: The properties are identical to the `ActionNode` in the generic Logic Editor (a **Command** and its **Parameters**).

## 4. Workflow: Building a Simple Conversation

This example creates a simple conversation where an NPC asks the player a question, and an item is given based on the player's answer.

1.  **Create the Graph**: In the Dialogue Editor, create a new `DialogueGraph` named `npc_greeting`.
2.  **Add the Opening Line (NPC)**:
    -   Right-click in the empty tree view and select "Add NPC Line."
    -   Select the new node. In the properties panel, set its `ID` to `npc_question`, `Character ID` to the NPC's ID (e.g., `jane_doe`), and `Dialogue Text` to "Hello there. Have you seen my lost widget?"
3.  **Add Player Choices**:
    -   Right-click the `npc_question` node and select "Add Player Choice."
    -   Set this new node's `ID` to `player_yes`, check the `Is Player Choice` box, and set the `Dialogue Text` to "Yes, I have it right here."
    -   Right-click the `npc_question` node again and add a second choice with the `ID` `player_no` and the text "No, I haven't."
4.  **Add NPC Replies**:
    -   Right-click the `player_yes` choice and "Add NPC Line."
    -   Set this reply's `ID` to `npc_thanks`, `Character ID` to `jane_doe`, and `Dialogue Text` to "Oh, thank you so much! Here is a reward."
    -   Right-click the `player_no` choice and "Add NPC Line."
    -   Set this reply's `ID` to `npc_sad`, `Character ID` to `jane_doe`, and `Dialogue Text` to "Oh, that's a shame. Please let me know if you find it."
5.  **Add an Action**:
    -   Right-click the `npc_thanks` reply and select "Add Action."
    -   Select this new `ActionNode`. In the properties panel, set the `Command` to `INVENTORY_ADD` and the `item_id` parameter to `reward_coin`.

You have now created a complete, branching conversation that directly impacts the game state by giving the player an item.
