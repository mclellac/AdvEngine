# AdvEngine Feature Roadmap

This document outlines planned features to expand the capabilities of AdvEngine, with a focus on streamlining the development of classic Sierra-style point-and-click adventure games.

## Core Systems & Gameplay

- [x] **Global Game State Manager**
    - A dedicated UI to create, edit, and delete global game variables (booleans, integers, strings).
    - Ability to set initial values and group variables by category (e.g., "Chapter 1 Quest Flags", "Player Stats").
    - Provides a live-debug view to watch variable changes when the game is running.

- [x] **Advanced Dialogue & Cutscene System**
    - [x] A dedicated tree-based editor for writing branching dialogue.
    - [ ] Support for displaying character portraits next to dialogue text.
    - Ability to embed simple commands within dialogue nodes (e.g., `give_item key_01`, `set_variable door_unlocked true`).
    - A simple timeline or script-based tool for creating in-game cutscenes (e.g., `CHARACTER walkto 100,200`, `PLAY_ANIMATION idle_sad`, `WAIT 2.0`, `SAY "I can't believe it's gone."`).

- [ ] **Complex Inventory & Item Interactions**
    - A dedicated interface for defining `Verb + Item` or `Item + Item` interactions.
    - Moves beyond the generic `InteractionMatrix` to a more intuitive system (e.g., a matrix view with verbs as columns and items as rows).
    - Support for item combination logic (`COMBINE item_a WITH item_b TO CREATE item_c`).

- [ ] **Quest & Objective Tracker**
    - A simple system to define high-level quests or tasks (e.g., "Find a way into the abandoned warehouse").
    - Ability to link quest steps to the completion of specific logic graph actions or variable changes.
    - An in-game UI element to show the player their current objectives (exportable).

## Content & Asset Management

- [ ] **Character Manager**
    - A central place to define player characters (PCs) and non-player characters (NPCs).
    - Assign sprite sheets for different animations (e.g., walk cycles, talk animations, idle loops).
    - Define character properties like walk speed, dialogue color, and default inventory.

- [ ] **Point-and-Click UI Builder**
    - A visual editor to design the main in-game user interface.
    - Support for classic Sierra-style verb bars or verb coins (Walk, Look, Talk, Use).
    - Define the layout and appearance of the inventory window, dialogue boxes, and menus.
    - Anchor points and scaling rules for modern widescreen resolutions.

- [ ] **Font Management**
    - A system to import and manage bitmap fonts for in-game text, preserving the retro aesthetic.
    - Ability to assign different fonts to UI elements like dialogue, descriptions, and menu buttons.

## Development & Debugging Tools

- [ ] **Integrated Game Launcher & Debugger**
    - A "Play" button in the AdvEngine toolbar that automatically exports the latest data and runs the Unreal Engine project.
    - An "Interaction Log" panel that streams real-time data from the running game back into the tool (e.g., `[GAME] Player clicked on Hotspot 'Door'`, `[LOGIC] Condition 'player_has_key' is FALSE`).

- [ ] **Localization Support**
    - A utility to export all user-facing text (dialogue, item names, UI labels) to a CSV or PO file for easy translation.
    - A corresponding import function to load translated text back into the project.

- [ ] **Project Templates**
    - Ability to create new projects from a template (e.g., "Sierra Style", "Modern Minimalist") that comes with pre-configured UI, verbs, and example structures.
