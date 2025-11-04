# AdvEngine UI/UX Improvement TODO List

This document tracks planned improvements to the user interface and user experience of the AdvEngine application.

## 1. High-Priority UI/UX Enhancements

These tasks directly impact the core user experience and should be addressed first.

- [X] **Improve Application Startup**:
  - Replace the hardcoded "TestGame" loading with a proper welcome screen.
  - The welcome screen should offer options to:
    - Create a new project.
    - Open an existing project via a file chooser.
    - Open a project from a list of recent projects.

- [ ] **Refine New Project Workflow**:
  - Implement a two-step project creation process:
        1. Show a dialog to get the project name.
        2. Use the name in the `Gtk.FileChooserNative` dialog to create a new folder.

- [ ] **Enhance Logic Editor Readability**:
  - Display key information (e.g., command, parameters, character ID, dialogue text) directly on the nodes in the canvas to make graphs easier to understand at a glance.
  - Make the mini-map interactive (click/drag to pan the main canvas).

- [ ] **Complete Feature Implementation**:
  - Make the "Play" button functional by adding a setting in the Preferences window to configure the path to the Unreal Engine editor executable.
  - Add a "Theme" (Light/Dark/System) setting to the Preferences window.
  - Add a "Language" selector to the Preferences window to support localization.

---

## 2. Code Quality & Refactoring

These tasks will improve the maintainability and stability of the codebase.

- [x] **Refactor `module_logic.py`**:
  - Eliminate code duplication by creating a single, parameterized `on_add_node` method.
  - Remove the redundant `on_add_condition_node` and `on_add_action_node` methods.
  - Simplify the `get_values` method in the `DynamicNodeEditor` class.
  - Move hardcoded values (colors, sizes) to named constants.

- [x] **Refactor Database Editors**:
  - Address the final unchecked item from the old TODO list: Implement real-time **input validation** in the `Gtk.ColumnView`-based editors.

- [x] **Clean up `main.py`**:
  - Refactor the database editor tabs (`Items`, `Attributes`, `Verbs`) for better clarity in the UI. A more prominent `Adw.ViewSwitcher` or similar widget could help.

---

## 3. Build System & Packaging

These tasks are crucial for ensuring the application can be reliably built and distributed.

- [ ] **Fix `TestGame` Installation**:
  - Modify the Meson build scripts to install the `TestGame/` directory and all its contents to the application's shared data directory (`pkgdatadir`).

- [ ] **Automate Source File Discovery**:
  - Update `src/meson.build` to use a glob (e.g., `find_files('*.py')`) to automatically include all Python source files, rather than listing them manually.

---

## 4. Documentation

These tasks will ensure the user and developer documentation is accurate and helpful.

- [ ] **Update All Editor Documentation**:
  - Review every file in `docs/reference/` to ensure it matches the current UI and functionality.
  - Replace all placeholder images with actual screenshots of the application.
  - Specifically update `logic-editor.md` to:
    - Correct the description of node types, colors, and the creation process.
    - Add documentation for the `DialogueNode`.
    - Document the multi-select and node resizing features.
    - Ensure terminology is consistent with the application's UI.

## Global / Application-Wide Enhancements

- [x] **Unified Save Status Indicator**: Implement a global indicator (e.g., an asterisk `*` in the window title or a dot on the save button) to clearly show when there are unsaved changes.
- [x] **Comprehensive Tooltips**: Add `tooltip_text` to all toolbar buttons, icon-only buttons, and complex input fields across all modules to improve discoverability.
- [x] **Keyboard Shortcut System**: Implement and document keyboard shortcuts for common global actions (e.g., `Ctrl+S` for Save, `Ctrl+O` for Open, `Ctrl+N` for New Project).
- [x] **Consistent Empty States**: Design and implement informative "empty state" placeholders for all lists, views, and canvases. For example, when no scenes exist, the Scene Editor should display a message like "No Scenes Found. Click 'Add Scene' to Begin."
- [x] **Improved Error/Confirmation Dialogs**: Replace generic dialogs with more specific and helpful `Adw.MessageDialog`s that clearly explain the action, error, or confirmation.
- [x] **Application-Wide Search**: Consider a global search feature to quickly find assets, logic nodes, or database entries by name or ID.

## Module-Specific UI/UX Tasks

### Scene Editor (`module_scene.py`)

- [x] **Canvas Zoom & Pan**: Implement intuitive zoom (Ctrl+Scroll) and pan (Middle-mouse drag) controls for the scene canvas to handle large scenes.
- [x] **Visible Grid & Snapping**: Add an optional, toggleable grid to the canvas and enable snapping for precise placement of hotspots and props.
- [x] **Properties Panel**: When a hotspot is selected, display its coordinates (X, Y) and dimensions (Width, Height) in a dedicated properties sidebar for precise editing.
- [x] **Layer Management**: Add a simple list view to manage the Z-order (layering) of hotspots and props within a scene.

### Logic Editor (`module_logic.py`)

- [x] **Visual Node Distinction**: Enhance the visual differentiation between node types (Action, Condition, Dialogue) using unique icons or more distinct header colors.
- [x] **Canvas Mini-Map**: For large graphs, add an interactive mini-map that allows for quick navigation of the entire logic canvas.
- [x] **Curved Connectors**: Switch from straight-line connectors to Bézier curves for node connections to improve readability and reduce visual clutter.
- [x] **Right-Click Context Menus**: Add context-sensitive right-click menus on nodes (for actions like "Delete", "Duplicate", "Edit") and on the canvas (for "Add Node...").
- [x] **Node Information Displayed**: Nodes should be resizable, and also display the information set in them. There is no way to distingush between multiple nodes of the same type and what information they contain without clicking on them. This is not helpful. Nodes should show what they do to the user better without opening them.

### Asset Manager (`module_assets.py`)

- [x] **Thumbnail Previews**: Display image thumbnails in the asset list for quick visual identification instead of just filenames.
- [x] **Asset Preview Panel**: Add a dedicated panel that shows a larger preview of the selected sprite, texture, or animation sequence.
- [x] **Drag-and-Drop Reordering**: Allow users to reorder animation frames within a sequence using drag-and-drop.

### Audio Manager (`module_audio.py`)

- [x] **Embedded Audio Preview**: Integrate a simple audio player widget to allow users to preview sound effects and music tracks directly within the editor.
- [x] **Waveform Visualization**: For selected audio files, display a small waveform graphic to provide a visual representation of the sound.

### Database Editors (`item_editor.py`, `character_editor.py`, etc.)

- [x] **Use `Gtk.ColumnView`**: Replace the current `Adw.PreferencesGroup` or `Gtk.ListBox` with a more appropriate `Gtk.ColumnView` to provide a more traditional and efficient table/spreadsheet-like editing experience.
- [x] **List Filtering & Sorting**: Add controls to filter the database lists by name/ID and sort columns alphabetically or numerically.
- [ ] **Input Validation**: Implement real-time input validation on entry fields to prevent errors (e.g., ensuring a "price" field only accepts numeric input).
