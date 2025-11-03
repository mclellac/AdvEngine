# AdvEngine User Guide

Welcome to the AdvEngine User Guide. This document provides a general overview of how to use AdvEngine to create your own 2.5D adventure games.

## 1. Introduction

AdvEngine is a powerful tool designed to streamline the creation of adventure games. It acts as a central hub for managing all your game's data, from scenes and puzzles to items and characters. The data you create here is then exported in a structured format that can be easily imported and used by our companion Unreal Engine 5.6 template.

The core philosophy of AdvEngine is to separate the creative design process from the complexities of the game engine. You can focus on building your world and puzzles, and let AdvEngine handle the data organization.

## 2. Getting Started: Your First Project

When you first launch AdvEngine, it will automatically load the `TestGame` project included in the repository. The application's core logic is managed by a `ProjectManager` that handles loading all data from the project's subdirectories.

The project is structured as follows:
-   `TestGame/Data/`: Contains all `.csv` files for items, characters, and attributes.
-   `TestGame/Logic/`: Contains `.json` files for game logic, such as the interaction matrix.
-   `TestGame/UI/`: Contains `.json` files for UI layouts.

The application itself is located in the `adv_engine/src` directory. To run it, you'll need to use the following command from the root of the repository:

```bash
python3 -m adv_engine.src.main
```

## 3. The AdvEngine Interface

The main window of AdvEngine is divided into several editor modules, each focusing on a different aspect of game creation:

-   **Scenes:** This is where you'll build the visual world of your game. You can import background art, define areas where the player can walk, and place "hotspots" that the player can interact with.
-   **Logic:** The heart of your game's interactivity. The Logic Editor is a node-based system that lets you create complex puzzle logic, branching dialogues, and quests without writing any code.
-   **Assets:** Manage your game's media, such as character sprites, item icons, and animation sequences.
-   **Verbs & Items (Database):** A spreadsheet-like interface for managing all the "things" in your game. This includes creating items, defining character stats, listing NPCs, and setting up shop inventories.
-   **Audio:** Control the soundscape of your game. Assign background music to scenes, place sound effects in the world, and manage voice-over files.

## 4. Workflow Overview: Creating a Simple Scene

Here's a typical workflow for creating a basic, interactive scene:

1.  **Create a Scene:** In the **Scenes** module, create a new scene. You'll start by importing a background image.
2.  **Define a Walk Mesh:** Draw a polygon on top of your background to define the area where the player character is allowed to walk.
3.  **Place Hotspots:** Create hotspots on objects in the scene that you want the player to be able to interact with (e.g., a door, a computer terminal, another character).
4.  **Create an Item:** Go to the **Verbs & Items** module and define an item that the player might use, for example, a "Keycard".
5.  **Build the Logic:** Switch to the **Logic** module. Here, you'll create a logic flow that says: "WHEN the player uses the `Keycard` on the `Door` hotspot, THEN the door becomes unlocked." This is done by connecting nodes that represent conditions and actions.
6.  **Test and Iterate:** AdvEngine allows for quick iteration. You can easily go back and tweak your scene, logic, or items as you refine your game.

## 5. Exporting Your Game

Once you have created some content, you can export it for use in Unreal Engine. The export process generates a set of organized `.csv` and `.json` files.

-   Navigate to `File > Export for Unreal Engine`.
-   Select an output directory.

These files are designed to be dropped directly into the `Content/ExternalData/` folder of the AdvEngine UE Template project. The template has pre-built systems that know how to read these files and bring your game to life.

This guide provides a high-level overview. For a more hands-on example, please see the `tutorial.md` document.
