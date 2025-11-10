# AdvEngine - Application Architecture

## 1. Introduction

This document provides a high-level overview of the AdvEngine application's
architecture. It is intended to guide developers in understanding the core
components of the application, their responsibilities, and how they interact with
one another.

## 2. Core Principles

The architecture of AdvEngine is guided by the following principles:

*   **Data-Driven Design:** The application is fundamentally a data editor. The
    core logic and game mechanics are defined by the data created and managed
    within the editor.
*   **Separation of Concerns:** The application is divided into distinct layers,
    with a clear separation between the data model, the business logic, and the
    user interface.
*   **Modularity:** The editor is composed of modular, interchangeable
    components, allowing for easy extension and maintenance.

## 3. High-Level Architecture

The AdvEngine application is composed of three primary layers:

1.  **Core Layer:** This layer is responsible for all data management, including
    loading, saving, and manipulation of project data. It also contains the data
    schemas that define the structure of the game's data.
2.  **UI Layer:** This layer is responsible for presenting the data to the user
    and for capturing user input. It is built using GTK4 and Libadwaita.
3.  **Application Layer:** This layer is the entry point of the application and
    is responsible for initializing the core and UI layers, and for managing the
    application's lifecycle.

## 4. Component Breakdown

### 4.1. Core Layer

The Core Layer forms the foundation of the application, handling all data
modeling, persistence, and business logic. It is designed to be completely
independent of the UI layer.

*   **`ProjectManager` (`src/core/project_manager.py`):** This class is the
    singleton controller for all project-related data. It acts as the single
    source of truth and the primary interface for the UI layer to interact with
    project data. Its responsibilities include:
    *   Loading and saving all project files from the `Data/` and `Logic/`
        directories using a transactional save model to prevent data
        corruption.
    *   Managing the project's in-memory data, which is a collection of
        dataclass objects.
    *   Tracking the `is_dirty` state of the project to notify the user of
        unsaved changes.
    *   Handling the creation of new projects from the templates stored in the
        root `templates/` directory.

*   **Data Schemas (`src/core/schemas/`):** This package defines the entire data
    model for the application using Python's `dataclasses`. Each file (e.g.,
    `item.py`, `character.py`, `scene.py`) defines a specific piece of game
    data. This approach ensures a strong, clear data structure that is decoupled
    from any UI logic.

*   **GObject Wrapper Factory (`src/core/schemas/gobject_factory.py`):** To
    bridge the gap between the plain Python dataclasses of the Core Layer and
    the GTK-based UI Layer, a factory pattern is used. This factory dynamically
    creates `GObject.Object` subclasses that wrap the dataclasses. This allows
    the data to be used directly in GTK models (like `Gio.ListStore`) and
    enables property binding, which automatically syncs the UI with changes in
    the underlying data.

*   **`SettingsManager` (`src/core/settings_manager.py`):** This class manages
    the loading and saving of settings. It handles two types of settings:
    *   **Application Settings:** Stored in the user's home configuration
        directory (e.g., `~/.config/adv_engine/settings.json`), these are
        global settings like the window size or the list of recent projects.
    *   **Project-Specific Settings:** Stored in `settings.json` within the
        project's root directory, these settings are specific to the currently
        loaded project.

*   **Unreal Engine Exporter (`src/core/ue_exporter.py`):** This module contains
    definitions (`COMMAND_DEFINITIONS`) for the various nodes and commands
    available in the Logic Editor. It effectively defines the "language" or
    instruction set that the game engine can understand, ensuring that the data
    created in AdvEngine is compatible with the target game engine.

### 4.2. UI Layer

The UI Layer is built with GTK4 and Libadwaita, following GNOME HIG principles.
It enforces a strict separation of presentation and logic by defining all UI
layouts declaratively in GtkBuilder `.ui` files.

*   **`EditorWindow` (`src/main.py`):** The main application window, which
    serves as the primary container for all the individual editor modules. It
    sets up the main `Adw.OverlaySplitView` and dynamically loads the editor
    modules into the sidebar and content areas.

*   **Dynamic Module Loading (`src/main.py`):** The application does not
    hardcode its editors. Instead, upon startup, it scans the `src/ui`
    directory for modules that export a class containing `EDITOR_NAME`,
    `VIEW_NAME`, and `ORDER` attributes. These modules are then dynamically
    imported and instantiated, allowing for a flexible and extensible editor
    system.

*   **Declarative UI with `@Gtk.Template` (`src/ui/`):** The established
    architectural pattern is to define a custom widget class in Python that
    inherits from a GTK or Adwaita widget (e.g., `Adw.Bin`). This class is
    decorated with `@Gtk.Template`, which points to a corresponding `.ui` file.
    Child widgets defined in the `.ui` file are connected to attributes in the
    Python class using `Gtk.Template.Child()`. This approach creates a clean,
    maintainable separation between the UI layout (XML) and the interactive
    logic (Python).

*   **Standard Layouts and Widgets:** To ensure consistency, the UI layer
    relies on a set of standard architectural patterns:
    *   **`Adw.OverlaySplitView`:** Used as the top-level container for most
        editors, providing a main content canvas and a collapsible properties
        sidebar.
    *   **`Gtk.ListView` and `Gtk.ColumnView`:** These modern list widgets are
        used for all database-style editors, implementing an inline-editing
        workflow that is more direct and intuitive than previous modal dialogs.
    *   **`Adw.StatusPage`:** Used to provide consistent and user-friendly
        "empty state" placeholders when no data is available to be shown in an
        editor.

*   **Application Startup Sequence:** The application follows a two-window model:
    1.  On first launch, the `WelcomeWindow` (`src/ui/welcome.py`) is
        displayed, allowing the user to create a new project or open an existing
        one.
    2.  Once a project is opened, the `WelcomeWindow` is hidden and a new
        `EditorWindow` instance is created, loading the selected project's data
        and displaying the full editor interface.

### 4.3. Application Layer

*   **`AdvEngine` (`main.py`):** The main application class. It is responsible
    for:
    *   Initializing the GTK application.
    *   Managing the application's lifecycle, including activation and shutdown.
    *   Handling application-level actions, such as creating a new project or
        opening an existing one.

## 5. Project Structure

### 5.1. On-Disk Format

An AdvEngine project is a self-contained directory with a standardized internal
structure. This ensures portability and consistency.

*   **`Assets/`:** Contains all binary assets for the project, such as images
    and audio files.
*   **`Data/`:** Contains all "database-style" data, typically stored in
    `.json` or `.csv` files. This includes definitions for items, characters,
    attributes, verbs, and global state variables.
*   **`Logic/`:** Contains all graph-based data, which defines the game's logic
    and narrative. This includes scenes, interaction logic, dialogue trees, and
    quests.
*   **`settings.json`:** A file containing project-specific settings that
    override the global application settings.

### 5.2. Project Templates

New projects are created by copying a template from the root `templates/`
directory. This system allows for the creation of different "starter kits" for
various game genres (e.g., `SpaceQuest`, `PoliceQuest`) and ensures that all new
projects begin with a valid and complete set of data files, preventing errors
on load.

## 6. Data Flow

The application's data flow is designed to be unidirectional, ensuring a clear
and predictable state management model.

```
 [ 1. User Interaction ]
           |
           v
 [ 2. GTK Widget (UI Layer) ] ---fires-signal---> [ 3. Python Callback ]
           ^                                                   |
           |                                                   |
 (GObject Property Binding)                                    v
           |                                     [ 4. ProjectManager API Call ]
           |                                                   |
           |                                                   |
 [ 7. GObject Wrapper ] <---notifies-via-signal--- [ 5. Dataclass Instance ]
           ^                                                   ^
           |                                                   |
           +---------------------------------------------------+
                         ( 6. Data is Updated )
```

1.  **User Interaction:** The user performs an action in the UI, such as typing
    in a `Gtk.Entry` or clicking a button.
2.  **GTK Widget Signal:** The widget emits a signal (e.g., `notify::text` or
    `clicked`).
3.  **Python Callback:** A callback function in the UI module's Python code is
    triggered by the signal.
4.  **`ProjectManager` API Call:** The callback function calls a method on the
    `ProjectManager` instance (e.g.,
    `project_manager.update_item(item_id, ...)`), passing the new data.
5.  **Dataclass Update:** The `ProjectManager` finds the corresponding Python
    `dataclass` instance in its in-memory store and updates its attributes.
6.  **GObject Notification:** The `GObject` wrapper that contains the
    `dataclass` instance is notified of the change.
7.  **UI Update via Binding:** The `GObject` wrapper emits a `notify::` signal
    for the property that changed. Any GTK widget whose property is bound to
    this `GObject` property is then automatically updated to reflect the new
    data, completing the cycle.
