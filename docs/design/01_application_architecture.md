# AdvEngine - Application Architecture

## 1. Introduction

This document provides a high-level overview of the AdvEngine application's architecture. It is intended to guide developers in understanding the core components of the application, their responsibilities, and how they interact with one another.

## 2. Core Principles

The architecture of AdvEngine is guided by the following principles:

*   **Data-Driven Design:** The application is fundamentally a data editor. The core logic and game mechanics are defined by the data created and managed within the editor.
*   **Separation of Concerns:** The application is divided into distinct layers, with a clear separation between the data model, the business logic, and the user interface.
*   **Modularity:** The editor is composed of modular, interchangeable components, allowing for easy extension and maintenance.

## 3. High-Level Architecture

The AdvEngine application is composed of three primary layers:

1.  **Core Layer:** This layer is responsible for all data management, including loading, saving, and manipulation of project data. It also contains the data schemas that define the structure of the game's data.
2.  **UI Layer:** This layer is responsible for presenting the data to the user and for capturing user input. It is built using GTK4 and Libadwaita.
3.  **Application Layer:** This layer is the entry point of the application and is responsible for initializing the core and UI layers, and for managing the application's lifecycle.

## 4. Component Breakdown

### 4.1. Core Layer

*   **`ProjectManager` (`project_manager.py`):** The central hub for all project data. It is responsible for:
    *   Loading and saving all project files (`.json`, `.csv`).
    *   Providing a unified interface for accessing and manipulating project data.
    *   Tracking the "dirty" state of the project to manage unsaved changes.
*   **Data Schemas (`data_schemas.py`):** A collection of Python `dataclasses` that define the structure of all game data. These schemas are the single source of truth for the application's data model.

### 4.2. UI Layer

*   **`EditorWindow` (`main.py`):** The main window of the application. It is responsible for:
    *   Housing the main application layout, including the header bar, sidebar, and content area.
    *   Discovering and loading all editor modules.
    *   Managing the navigation between different editors.
*   **Editor Modules (`module_*.py`):** A collection of modules that each implement a specific editor for a particular type of game data (e.g., `module_logic.py` for the Logic Editor, `module_scene.py` for the Scene Editor).

### 4.3. Application Layer

*   **`AdvEngine` (`main.py`):** The main application class. It is responsible for:
    *   Initializing the GTK application.
    *   Managing the application's lifecycle, including activation and shutdown.
    *   Handling application-level actions, such as creating a new project or opening an existing one.

## 5. Data Flow

The following diagram illustrates the high-level data flow within the application:

```
[ User Interaction ] -> [ UI Layer ] -> [ ProjectManager ] -> [ Data Schemas ]
       ^                                                              |
       |--------------------------------------------------------------|
```

1.  The user interacts with the UI Layer (e.g., by editing a value in an editor).
2.  The UI Layer captures the user's input and calls the appropriate method in the `ProjectManager` to update the data.
3.  The `ProjectManager` updates the in-memory data model, which is composed of instances of the data schemas.
4.  The `ProjectManager` notifies the UI Layer that the data has changed.
5.  The UI Layer updates to reflect the new state of the data.
