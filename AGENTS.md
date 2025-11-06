# AGENTS.md: AdvEngine

---

## 1. Project Overview & Context

*   **Project Name (Tool):** AdvEngine
*   **Purpose:** A modern adventure game editor for the rapid creation and iteration of 2.5D point-and-click adventure games, inspired by classic Sierra On-Line titles.
*   **Function:** AdvEngine is a **Data and Configuration Manager**. It provides a cross-platform UI for designing game logic, managing data, and exporting structured files for the target game engine.
*   **Target Game Engine:** Unreal Engine 5.6
*   **Core Principle:** Abstraction—hide Unreal Engine's complexity behind a clean, data-driven Python interface.

---

## 2. Technology Stack & Dependencies

### A. Core Tool Stack (AdvEngine Application)

| Component | Role | Required Version | Notes |
| :--- | :--- | :--- | :--- |
| **Language** | Front-end logic, data management. | **Python 3.10+** | |
| **GUI Framework** | Cross-platform UI toolkit. | **GTK4 (via PyGObject)** | Provides the core application structure. |
| **Design Library** | Modern, responsive UI components. | **Libadwaita** | Ensures a clean, HIG-compliant aesthetic. |
| **Build System** | Project compilation and installation. | **Meson & Ninja** | Replaces previous direct script execution. |
| **Graphing** | Node drawing and rendering. | **Custom GTK Widget** | Uses **cairo** for canvas rendering. |
| **Serialization**| Data processing for project files. | **json**, **csv** | Standard libraries for all I/O. |

---

## 3. AdvEngine Internal Tool Architecture

### A. Directory Structure

The project has a split source structure. Python modules are in `adv_engine/src/`, while GTK UI definition files, resources, and Meson build scripts are in a separate top-level `src/`.

```text
/
|-- src/                      # Top-level source for build system and resources
|   |-- core/
|   |   |-- project_manager.py     # Handles project loading, saving, and data access.
|   |   |-- data_schemas.py        # Python dataclass definitions for all game data.
|   |   |-- settings_manager.py    # Manages application and project settings.
|   |   |-- ue_exporter.py         # Defines node commands and parameters.
|   |-- ui/
|   |   |-- main.py                # Application entry point and main window class.
|   |   |-- module_scene.py        # Scene Editor
|   |   |-- module_logic.py        # Logic Graph Editor
|   |   |-- module_dialogue.py     # Dialogue Tree Editor
|   |   |-- module_interaction.py  # Interaction Editor
|   |   |-- module_character.py    # Character Manager
|   |   |-- module_quest.py        # Quest Editor
|   |   |-- item_editor.py         # Item Database Editor
|   |   |-- ... (other editors)
|   |-- advengine.gresource.xml # GResource bundle definition.
|   |-- main.py                 # Application entry point.
|-- TestGame/                 # Example project data.
|-- docs/                     # User guide and tutorial.
|-- meson.build               # Main Meson build script.
```

### B. Module Responsibilities

*   **`src/core/project_manager.py`**: The central data hub. Manages loading all project files (`.json`, `.csv`) into memory, provides data access to UI modules, tracks unsaved changes (`is_dirty` state), and handles saving operations.
*   **`src/core/data_schemas.py`**: Defines the application's entire data model using Python `dataclasses`. This includes structures for `Item`, `Character`, `Scene`, `LogicGraph`, `Quest`, etc.
*   **`src/ui/main.py`**: The application entry point. Initializes the `Adw.Application`, builds the main `AdvEngineWindow`, instantiates all editor modules, and wires them into the `Adw.ViewStack`.
*   **`src/ui/module_logic.py`**: Implements the generic node-based editor for creating and visualizing `LogicGraph` data structures. It handles canvas drawing, user input (selection, dragging, connecting), and context menus.
*   **`src/ui/module_dialogue.py`**: A specialized editor that uses a tree view to manage `DialogueGraph` data, which is a specific type of `LogicGraph`.
*   **Database Editors (`item_editor.py`, etc.)**: These modules implement a consistent, spreadsheet-like UI using `Gtk.ColumnView` for all database-style data (Items, Verbs, Attributes, etc.), providing full inline CRUD functionality.

---

## 4. Design and Architectural Documentation

For a complete understanding of the application's architecture, coding standards, and the design of its core components, consult the comprehensive design documentation located in the `docs/design/` directory.

-   **`01_application_architecture.md`**: Provides a high-level overview of the application's architecture, data flow, and the role of core components.
-   **`02_coding_standards.md`**: Defines the project's coding conventions, including PEP8, docstring format, and UI guidelines.
-   **`03_logic_editor_design.md`**: Provides a detailed breakdown of the Logic Editor's internal architecture, its interaction with data schemas, and the complete data persistence workflow.

## 5. Feature and Data Model Documentation

For a complete and exhaustive understanding of the application's features, editor workflows, and data schemas, consult the comprehensive user documentation located in the `/docs` directory.

-   The **`/docs/reference/`** directory contains detailed, up-to-date guides for every editor and data model. This should be considered the primary source of truth.
-   The Python dataclasses in **`src/core/data_schemas.py`** are the definitive source for the structure of all data models.

---

## 7. Coding Style and Conventions

*   **PEP8 Compliance**: All Python code must adhere to the PEP8 style guide.
*   **Docstrings**: All modules, classes, and functions must have Google-style docstrings.
*   **Error Handling**: Use `try...except` blocks for all file I/O operations. Provide clear user feedback for errors.
*   **GNOME HIG**: The UI must follow the GNOME Human Interface Guidelines, using Libadwaita widgets and patterns wherever possible.
*   **No Custom CSS**: Do not add custom CSS styling. The application should rely entirely on the default Libadwaita theme to ensure a consistent user experience, including support for light and dark modes.
*   **Atomic Commits**: Submit work as focused, atomic changes. Avoid bundling unrelated features or bug fixes.
