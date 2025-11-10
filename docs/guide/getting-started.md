# Getting Started with AdvEngine

This guide provides a detailed walkthrough of creating, loading, and managing projects in AdvEngine.

## 1. Building and Launching the Application

Before you can create a project, you need to build and run AdvEngine. Please follow the detailed instructions in the main `README.md` file at the root of the repository to install dependencies and compile the application using the Meson build system.

Once built, you can launch the application from your specified installation directory (e.g., `/tmp/advengine-install/bin/advengine`).

## 2. The Project Structure

An AdvEngine project is a directory on your filesystem that contains a standardized structure of subdirectories and files. When you launch AdvEngine for the first time, it loads the included `TestGame` project, which serves as a helpful example.

A typical project directory looks like this:

-   **`/` (Project Root)**
    -   **`Data/`**: This directory holds all your database-style data.
        -   `ItemData.csv`: A list of all in-game items.
        -   `CharacterData.csv`: A list of all characters.
        -   `GlobalState.json`: A list of all global variables.
        -   `Verbs.json`: A list of all verbs.
        -   `...` (and other `.csv` or `.json` files)
    -   **`Logic/`**: This directory holds all your logic-based assets.
        -   `Scenes.json`: Contains the data for all your scenes and hotspots.
        -   `LogicGraphs.json`: Contains all your general-purpose logic graphs.
        -   `DialogueGraphs.json`: Contains all your dialogue trees.
        -   `Interactions.json`: The definitions for all verb/item interactions.
        -   `...` (and other `.json` files for quests, etc.)
    -   **`Assets.json`**: A manifest of all your imported assets.
    -   **`Audio.json`**: A manifest of all your audio files.
    -   **`settings.json`**: Project-specific settings.

## 3. Creating a New Project

To create your own game, you'll start by creating a new project.

1.  Click the **"New Project"** button in the Header Bar.
2.  A file chooser dialog will appear, prompting you to select a location for your new project. Choose an **empty directory**.
3.  Give your project a name by typing it into the "Name" field at the top of the dialog and click the **"Create"** button.
4.  AdvEngine will then automatically generate the complete project structure (`Data/`, `Logic/`, etc.) and all the necessary empty `.json` and `.csv` files inside the directory you selected.
5.  The application will then automatically load this new, empty project, and you can begin creating your game.

## 4. Saving a Project

AdvEngine uses a **manual save model**. This means you must explicitly save your work.

-   **Unsaved Changes**: The application will add an asterisk (`*`) to the main window title whenever you have unsaved changes.
-   **Saving**: To save your work, you can either:
    -   Click the **"Save"** button in the Header Bar.
    -   Use the `Ctrl+S` keyboard shortcut.
-   Upon saving, AdvEngine will write all the in-memory data to the corresponding `.json` and `.csv` files in your project directory.

It is good practice to save frequently to avoid losing your work.
