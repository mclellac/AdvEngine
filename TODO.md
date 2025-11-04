# AdvEngine Improvement TODO List

This document tracks planned improvements to the AdvEngine application, categorized by area.

---

## 1. High-Priority UI/UX Enhancements

These tasks directly impact the core user experience and should be addressed first.

- [ ] **Improve Application Startup**:
    -   Replace the hardcoded "TestGame" loading with a proper welcome screen.
    -   The welcome screen should offer options to:
        -   Create a new project.
        -   Open an existing project via a file chooser.
        -   Open a project from a list of recent projects.

- [ ] **Refine New Project Workflow**:
    -   Implement a two-step project creation process:
        1.  Show a dialog to get the project name.
        2.  Use the name in the `Gtk.FileChooserNative` dialog to create a new folder.

- [ ] **Enhance Logic Editor Readability**:
    -   Display key information (e.g., command, parameters, character ID, dialogue text) directly on the nodes in the canvas to make graphs easier to understand at a glance.
    -   Make the mini-map interactive (click/drag to pan the main canvas).

- [ ] **Complete Feature Implementation**:
    -   Make the "Play" button functional by adding a setting in the Preferences window to configure the path to the Unreal Engine editor executable.
    -   Add a "Theme" (Light/Dark/System) setting to the Preferences window.
    -   Add a "Language" selector to the Preferences window to support localization.

---

## 2. Code Quality & Refactoring

These tasks will improve the maintainability and stability of the codebase.

- [ ] **Refactor `module_logic.py`**:
    -   Eliminate code duplication by creating a single, parameterized `on_add_node` method.
    -   Remove the redundant `on_add_condition_node` and `on_add_action_node` methods.
    -   Simplify the `get_values` method in the `DynamicNodeEditor` class.
    -   Move hardcoded values (colors, sizes) to named constants.

- [ ] **Refactor Database Editors**:
    -   Address the final unchecked item from the old TODO list: Implement real-time **input validation** in the `Gtk.ColumnView`-based editors.

- [ ] **Clean up `main.py`**:
    -   Refactor the database editor tabs (`Items`, `Attributes`, `Verbs`) for better clarity in the UI. A more prominent `Adw.ViewSwitcher` or similar widget could help.

---

## 3. Build System & Packaging

These tasks are crucial for ensuring the application can be reliably built and distributed.

- [ ] **Fix `TestGame` Installation**:
    -   Modify the Meson build scripts to install the `TestGame/` directory and all its contents to the application's shared data directory (`pkgdatadir`).

- [ ] **Automate Source File Discovery**:
    -   Update `src/meson.build` to use a glob (e.g., `find_files('*.py')`) to automatically include all Python source files, rather than listing them manually.

---

## 4. Documentation

These tasks will ensure the user and developer documentation is accurate and helpful.

- [ ] **Update All Editor Documentation**:
    -   Review every file in `docs/reference/` to ensure it matches the current UI and functionality.
    -   Replace all placeholder images with actual screenshots of the application.
    -   Specifically update `logic-editor.md` to:
        -   Correct the description of node types, colors, and the creation process.
        -   Add documentation for the `DialogueNode`.
        -   Document the multi-select and node resizing features.
        -   Ensure terminology is consistent with the application's UI.
