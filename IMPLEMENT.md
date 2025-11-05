# AdvEngine Implementation and Refactoring Plan

This document outlines the necessary implementations, updates, changes, and refactors required to bring the AdvEngine application to a fully functional and polished state.

## General Audit Findings

- **Code Quality:**
  - **Architectural Flaw:** `LogicNode` in `data_schemas.py` holds a `parent_editor` reference, violating Model-View separation. This should be refactored to remove the dependency of the data model on the UI.
  - **Inconsistent GObject Wrappers:** Several dataclasses (`Cutscene`, `Asset`, `Animation`, `Audio`) lack the `GObject.Object` wrapper needed for integration with GTK models. This should be implemented for all data types displayed in lists or tables.
  - **Missing Error Handling:** File I/O operations (e.g., in the `AssetManager`) are performed without `try...except` blocks, which can lead to application crashes.

- **UI/UX Consistency:**
  - **Incomplete Features:** Core user-facing features are incomplete. For example, the "Play" button in `main.py` uses a hardcoded, non-functional path and should be linked to a configurable setting in the Preferences window. The "New Project" dialog has a `TODO` for template selection that needs to be implemented.
  - **Placeholder Widgets:** Some modules, like the UI Builder, are placeholders and need to be fully implemented or removed.

- **HIG Compliance:**
  - **Dialogs:** The application correctly uses `Adw.MessageDialog` and `Gtk.FileChooserNative`, which aligns with modern GNOME HIG.
  - **Layout:** The main window's use of `Adw.ToolbarView` and `Adw.OverlaySplitView` is correct and follows HIG.

## Editor-Specific Audit

### Database Editors (Item, Attribute, Verb, etc.)
- **Architectural Flaw:** The `ItemEditor` and `AttributeEditor` (and likely others) incorrectly use full-width `Adw.EntryRow` and `Adw.SpinRow` widgets within `Gtk.ColumnView` cells. This is a misuse of the widgets, causing severe layout and rendering issues. The correct approach is to use lightweight widgets like `Gtk.Entry` and `Gtk.SpinButton`.
- **Memory Leak:** None of the audited database editors implement the `unbind` signal handler for their `Gtk.SignalListItemFactory`. This is a critical bug that will lead to memory leaks and unpredictable behavior, as old signal connections and property bindings are not being cleaned up when list items are recycled. All factories must be updated to include a corresponding `unbind` handler.

### Canvas-Based Editors (Scene, Logic)

- **Scene Editor:**
  - **Inefficient UI Construction:** The editor's UI is built imperatively, leading to complex and inefficient state management. Widgets are frequently recreated (e.g., on scene selection), which is poor practice and can cause performance issues.
  - **Confusing UX Flow:** The main sidebar containing the scene list is hidden upon selection and replaced with the properties panel. This creates an unstable and non-standard UI that makes it difficult to navigate between scenes. The layout should be refactored to use a stable three-pane view (list, canvas, properties).
  - **Missing Empty State:** The canvas area does not have a proper `Adw.StatusPage` when no scene is selected, leading to a blank and uninformative view.

- **Logic Editor:**
  - **Critical Widget Handling Error:** The `DynamicNodeEditor` incorrectly calls `destroy()` on `Adw.PreferencesGroup` widgets when rebuilding its UI. The correct GTK4 method is to remove the widget from its parent. This bug is a likely source of `Adwaita-CRITICAL` warnings and application instability.
  - **Flawed Resizing Logic:** The drag-to-resize implementation in `on_resize_drag_update` is mathematically incorrect, resulting in erratic and unusable node resizing. It needs to be rewritten to correctly calculate the new dimensions based on the gesture's offset from the start point.
  - **Code Duplication:** The `on_add_*_node` methods are heavily duplicated and should be refactored into a single, parameterized function to improve maintainability.

### Other Editors

- **Interaction Editor:**
  - **Forbidden UI Pattern:** The editor uses a modal dialog (`Adw.MessageDialog`) for creating and editing interactions. This is a direct violation of the user's explicit instruction to use inline editing and avoid the "select then click edit" pattern. The entire module needs to be refactored to use a `Gtk.ColumnView` with inline editing, consistent with the other database editors.

- **Dialogue Editor:**
  - **Use of Deprecated Widget:** The editor is built using a `Gtk.TreeView`, a complex and outdated widget that is not recommended for modern GTK4 applications. It should be completely refactored to use a `Gtk.ListView` or a similar modern widget.
  - **Broken Workflow:** Editing an `ActionNode` opens a blocking modal dialog that re-uses the flawed `DynamicNodeEditor`. This workflow is both non-functional (due to the editor's bugs) and contrary to the desired non-modal, inline editing pattern.

- **Cutscene Editor:**
  - **Use of Deprecated Widget:** Like the `DialogueEditor`, this module uses a `Gtk.TreeView` to display parsed actions and should be updated to use a modern `Gtk.ColumnView`.
  - **Placeholder Functionality:** The script parsing is simplistic and lacks robust error handling. The "Add" button has hardcoded values instead of prompting for user input.

- **Asset Manager:**
  - **Use of Deprecated Widget:** The editor uses the deprecated `Gtk.FileChooserDialog` instead of `Gtk.FileChooserNative`.
  - **Broken Drag-and-Drop:** The logic for reordering animation frames is non-functional due to incorrect method calls (`get_row_at_y`).
  - **Missing Error Handling:** File I/O operations for importing assets are performed without `try...except` blocks, making the editor fragile.

- **Audio Editor:**
  - **Incorrect Widget Usage:** The editor misuses `Gtk.Video` for audio playback and fails to correctly link it to the `Gtk.MediaControls`.
  - **Placeholder Functionality:** The waveform display generates random data instead of analyzing the audio file, making it a purely cosmetic placeholder.
  - **Use of Deprecated Widget:** Also uses the deprecated `Gtk.FileChooserDialog`.

## Build System and Documentation

- **Meson Build:**
  - **Hardcoded Python Path:** The `src/meson.build` file finds and hardcodes the absolute path to the `python3` executable. This is a major portability regression that will cause the application to fail in environments with different Python installations (e.g., pyenv, virtualenv). The build script should be modified to use a relative path or a more robust method of locating the interpreter at runtime.

- **Documentation:**
  - **Outdated Content:** The documentation in the `docs/` directory is likely inconsistent with the current state of the application, especially given the number of non-functional or placeholder editors. It will need a thorough review and update after the required refactoring is complete.
