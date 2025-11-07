# AdvEngine User Guide

Welcome to the AdvEngine User Guide. This document provides a comprehensive overview of how to use AdvEngine to create your own 2.5D point-and-click adventure games.

## 1. Introduction

AdvEngine is a powerful tool designed to streamline the creation of adventure games. It acts as a central hub for managing all your game's data—from scenes and puzzles to items and characters. The data you create here is then exported in a structured format that can be easily used by a companion Unreal Engine 5.6 template.

The core philosophy of AdvEngine is to separate the creative design process from the complexities of the game engine. You can focus on building your world, writing your story, and designing puzzles, and let AdvEngine handle the data organization.

## 2. Getting Started: Your First Project

When you first launch AdvEngine, it automatically loads the `TestGame` project included in the repository. This sample project demonstrates the expected file structure and provides examples of various data types.

A project directory contains the following subdirectories:

- **`Data/`**: Contains `.csv` and `.json` files for database-style data like items, characters, attributes, verbs, and global state.
- **`Logic/`**: Contains `.json` files for all logic-based assets, including scenes, logic graphs, dialogues, interactions, and quests.

To build and run the application, please follow the instructions in the main `README.md` file.

## 3. The AdvEngine Interface

The main window of AdvEngine is built using Libadwaita to provide a modern, clean, and consistent user experience.

- **Header Bar**: At the top of the window, the header bar contains the sidebar toggle, a "Save" button to persist project changes, a "Play" button to launch the game, and a global search bar. The application menu provides access to preferences, shortcuts, and the "about" dialog.
- **Sidebar**: On the left, a collapsible sidebar lists all the available editor modules. Clicking an item in this list will open the corresponding editor in the main content area.
- **Content Area**: This is the main workspace where the selected editor is displayed. The application uses a `ViewStack` to seamlessly switch between different editors.

## 4. The Editor Modules

AdvEngine is divided into several editor modules, each tailored to a specific aspect of game creation.

- **Scenes:** A canvas-based editor where you build the visual world of your game. You can import background art and place "hotspots" that the player can interact with.
- **Logic:** The heart of your game's interactivity. The Logic Editor is a general-purpose, node-based system that lets you create complex puzzle logic and gameplay flows.
- **Interactions:** This editor allows you to define what happens when the player uses a verb or item on something in the world. Each interaction is linked to a logic graph.
- **Dialogue:** A specialized tree-based editor for writing branching conversations with characters.
- **Assets:** Manage your game's media, such as character sprites, item icons, and animation sequences.
- **Database (Items, Verbs, Attributes, Characters):** A collection of spreadsheet-like editors for managing all the "things" in your game.
- **Global State:** Manage the state of your game by creating and editing global variables (e.g., quest flags, story progress).
- **Quests:** Define and track multi-step quests and objectives for the player to complete.
- **Audio:** Control the soundscape of your game by assigning background music and managing sound effects.

## 5. Workflow Overview: Creating a Simple Puzzle

Here's a typical workflow for creating a basic, interactive puzzle in AdvEngine:

1. **Create the Database Entries:** In the **Database** module, create the necessary `Verb` (e.g., "Use") and `Item` (e.g., "Keycard") that will be part of your puzzle.
2. **Create the Scene:** In the **Scenes** module, create a new scene and import a background image. Place hotspots on the interactive elements of the scene (e.g., a locked door).
3. **Build the Logic Graph:** In the **Logic** module, create a new `LogicGraph`. Here, you will visually script the outcome of the puzzle. For example, you can create a simple graph that plays an "unlock" animation and then transitions to a new scene.
4. **Define the Interaction:** Go to the **Interactions** module. Create a new interaction that links everything together: "When the player **Uses** the **Keycard** on the **Door** hotspot, execute the **UnlockDoorLogic** graph."
5. **Test and Iterate:** AdvEngine allows for quick iteration. You can easily switch between the editors to tweak your scene, logic, or items as you refine your game.

This guide provides a high-level overview. For a more hands-on example, please see the `tutorial.md` document, which will walk you through creating a complete puzzle from start to finish.
