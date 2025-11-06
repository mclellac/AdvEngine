# AdvEngine TODO

This document outlines the necessary fixes and improvements to make AdvEngine a functional and reliable tool.

## I. Critical: Data Persistence Bugs

These issues cause data loss and must be fixed first.

-   [x] **Fix Logic Node Data Saving:**
    -   Modify the `_save_logic_graphs` method in `src/core/project_manager.py` to correctly serialize all node attributes, including dynamic parameters from the `DynamicNodeEditor`.
    -   Ensure that `DialogueNode`, `ConditionNode`, and `ActionNode` attributes are saved to the `LogicGraphs.json` and `DialogueGraphs.json` files.

-   [ ] **Fix Database Editor Functionality:**
    -   In `src/ui/*_editor.py` (Item, Attribute, Verb, etc.), ensure that the correct data objects (the raw dataclass, not the `GObject` wrapper) are passed to the `ProjectManager` for add, update, and delete operations.
    -   Modify the `ProjectManager`'s `save_project` method to correctly overwrite files even when the corresponding data list is empty (e.g., if all items are deleted).

## II. Editor Functionality

-   [x] **Fix Logic Node Resizing:**
    -   In `src/ui/module_logic.py`, correct the calculation in `on_resize_drag_update` to properly account for the drag offset, ensuring that node resizing is smooth and predictable.

-   [ ] **Implement Global State Editor:**
    -   In `src/ui/module_state.py`, add UI elements (buttons, a `Gtk.ColumnView`) to allow users to add, update, and delete global variables.
    -   Connect these UI elements to the corresponding methods in the `ProjectManager`.

## III. Code Quality and Refactoring

-   [x] **Refactor `ProjectManager` Loading:**
    -   Combine the duplicated `_load_logic_graphs` and `_load_dialogue_graphs` methods into a single, reusable `_load_graph_data` method.

-   [x] **Refactor `module_logic.py`:**
    -   Refactor the repetitive `on_add_*_node` methods into a single, parameterized method to reduce code duplication.

## IV. Feature Completeness

-   [ ] **Implement Remaining "TODO.md" Items:**
    -   Work through the remaining unchecked items in the original `TODO.md` file, such as making the "Play" button functional and adding a theme selector.

-   [ ] **Address "TOBEFIXED.md" Items:**
    -   Address the remaining issues outlined in the `TOBEFIXED.md` file, such as the placeholder audio and asset editors.
