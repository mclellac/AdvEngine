# AdvEngine Agent Protocol

This document outlines the guidelines and standards for AI agents working on the AdvEngine project. Adherence to these protocols is crucial for maintaining code quality, consistency, and alignment with the project's goals.

## 0. Mandatory Design and Coding Standards

**ATTENTION: ALL AGENTS MUST READ AND FOLLOW THE CODING AND DESIGN STANDARDS SET OUT IN `docs/design`.**

This is not a suggestion. The application **MUST** follow the documentation. Before making any changes, you are required to read the following documents in their entirety:

1.  [`docs/design/01_application_architecture.md`](./docs/design/01_application_architecture.md)
2.  [`docs/design/02_coding_standards.md`](./docs/design/02_coding_standards.md)
3.  [`docs/design/03_logic_editor_design.md`](./docs/design/03_logic_editor_design.md)

Failure to adhere to these standards will result in the rejection of your work. You are expected to understand and apply these principles in all of your contributions.

## 1. Core Principles

- **User-Centric Design**: The primary goal is to create a powerful, intuitive, and stable tool for game developers. All technical decisions should ultimately serve this goal. The user's frustration with bugs and inconsistent UI is a top priority to resolve.
- **GNOME HIG Adherence**: The application MUST follow the GNOME Human Interface Guidelines. The UI should be clean, modern, and consistent. Use Adwaita widgets and layouts wherever possible. **Custom CSS is forbidden.**
- **UI-First Development**: The user interface will be defined declaratively using GtkBuilder `.ui` files, not programmatically in Python. This enforces a separation of concerns and is the standard for this project going forward. *(Note: This is an ongoing refactoring effort. While this is the standard for all new work, some legacy modules may still contain procedurally generated UI.)*
- **Data-Driven Architecture**: The core of the engine is the separation of data (`.dataclasses` in `data_schemas.py`) from the UI (`GObject` wrappers and GTK widgets). The UI should be a reflection of the data, and all data manipulation should happen through the `ProjectManager`.
- **Atomic Commits**: Each submission should represent a single, complete, and logical change. Do not bundle unrelated features or bug fixes.

## 2. Technical Standards

- **Code Style**: All Python code MUST adhere strictly to PEP8. Docstrings MUST be in the Google style and be comprehensive.
- **Error Handling**: All file I/O and other potentially failing operations must be wrapped in `try...except` blocks with robust error handling and user-facing feedback.
- **Dependencies**: The project is built on Python 3.10+, GTK4, and Libadwaita. All dependencies required to build and run the project are documented in memory.
- **Testing**: While there is no formal test suite yet, manual "smoke testing" is required. After any significant change, run the application in a headless environment to ensure it starts without critical errors.

## 3. Workflow

1.  **Understand the Goal**: Before writing code, fully understand the user's request and the existing codebase. Consult this file and the `docs/design` directory.
2.  **Plan the Work**: Create a detailed, step-by-step plan using the `set_plan` tool. The plan must be approved before implementation begins.
3.  **Implement Declaratively**: For all UI work, start by creating or modifying the `.ui` file. Then, load this file in the corresponding Python module and connect signals and logic.
4.  **Verify Changes**: After each modification, use tools like `read_file` to confirm the change was written correctly. After a set of changes, run the application to visually or functionally verify the results.
5.  **Pre-Commit Checks**: Before submitting, run all required pre-commit checks. This includes linting, formatting, and any other verification steps.

## 4. Key Architectural Patterns

- **`Gtk.Builder`**: This is the **only** approved method for creating UI layouts. The `ui_loader.py` module will provide a helper function to load these files.
- **`Adw.OverlaySplitView`**: This is the standard top-level layout for main editor views, providing a sidebar and a content area.
- **`Gtk.ListView` / `Gtk.ColumnView`**: These are the preferred widgets for displaying lists of data. Inline editing is the required pattern, replacing the old "select then click edit" modal dialogs.
- **`ProjectManager`**: This is the single source of truth for all project data. The UI must not store its own state but should instead reflect the state of the `ProjectManager`.
- **`GObject` Wrappers**: To display dataclasses in GTK views, they must be wrapped in a `GObject.Object` subclass. This is a critical pattern for connecting the data model to the UI.
- **`SettingsManager`**: The `SettingsManager` class in `src/core/settings_manager.py` handles all application and project settings. Use the generic `get` and `set` methods to access and modify settings.
- **Project Templates**: New projects are created from a template located in the top-level `templates/` directory. Each template is a complete, self-contained project folder. When adding new features that require default data (e.g., a new type of asset or logic), ensure this data is added to all relevant templates to provide a consistent user experience.
- **`@Gtk.Template`**: The established architectural pattern for UI files is to use the `@Gtk.Template` decorator on a widget class, pointing to a corresponding `.ui` file. Child widgets from the UI file are then connected to class attributes using `Gtk.Template.Child()`.
- **CRITICAL: `Adw.Dialog` Parenting**: `Adw.Dialog` is a `Gtk.Widget`, not a `Gtk.Window`. It does **not** have the `set_transient_for` method or the `transient_for` property. Using either will cause a crash.
    *   **Correct Pattern**: To create and show a custom, template-based `Adw.Dialog` with a parent, the following two steps are required:
        1.  The dialog class's `__init__` method must be a simple `def __init__(self, **kwargs): super().__init__(**kwargs)`. It should not take any special arguments.
        2.  The dialog is instantiated with no arguments (`dialog = MyDialog()`) and then shown by calling `dialog.present(parent_window)`. The `present()` method handles both showing the dialog and setting its parent.
    *   **DO NOT** attempt to pass `transient_for` to the constructor.
    *   **DO NOT** attempt to call `set_transient_for()` on the dialog object.

- **CRITICAL: `Adw.Dialog` GtkBuilder Template Structure**: When defining a custom class that inherits from `Adw.Dialog` in a `.ui` file using `@Gtk.Template`, the layout structure is strict and unforgiving.
    *   **Correct Pattern**:
        - The main content widget (e.g., an `Adw.PreferencesPage` or `Gtk.Box`) MUST be defined as a direct `<child>` of the `<template>` tag.
        - The titlebar widget (e.g., an `Adw.HeaderBar`) MUST be assigned using `<property name="titlebar">`.
    *   **DO NOT** use `<property name="content">` to set the main widget. This property is invalid for `Adw.Dialog` templates and will cause the template instantiation to fail, resulting in a crash (typically an `AttributeError` on a `NoneType` object because the `@Gtk.Template.Child` widgets were never created).
