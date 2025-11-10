# AdvEngine TODO

This document outlines the necessary fixes and improvements to make AdvEngine a functional and reliable tool.

## I. Critical: Implement Core Editor Functionality

The following editors are currently non-functional placeholders. Implementing them is the highest priority.

- [ ] **Implement Global State Editor:**
    - The `Global State` editor currently shows a placeholder.
    - **Task:** In `src/ui/module_state.py`, add UI controls (e.g., an `Adw.HeaderBar` with an "Add" button, and a `Gtk.ColumnView`) to allow users to add, update, and delete global variables. Connect these controls to the `ProjectManager`.

- [ ] **Implement Quest Editor:**
    - The `Quests` editor is currently a placeholder.
    - **Task:** In `src/ui/module_quest.py`, design and implement a UI for creating, editing, and deleting quests and their associated steps. This will likely involve a master-detail view using a `Gtk.ListBox` and a custom widget for editing quest details.

- [ ] **Implement Full Asset Manager Functionality:**
    - The `Assets` manager only supports images.
    - **Task:** In `src/ui/module_assets.py`, implement the "Audio" and "Fonts" sections. This will involve adding `Gtk.GridView`s and preview widgets for audio files and font files.

## II. High: Data Persistence Bugs

These issues cause data loss and must be fixed to ensure user trust.

- [ ] **Fix Database Editor Deletion:**
    - Deleting all entries in a database editor (e.g., all Items) and saving the project does not update the corresponding data file, causing the deleted items to reappear on next load.
    - **Task:** Modify the `ProjectManager`'s `save_project` method to correctly overwrite data files with an empty list when all items have been deleted.

## III. Medium: UI Polish & Minor Bugs

- [ ] **Add "Add" button to empty placeholders:**
    - The `Global State` and `Quest` editors lack a way to add the first item.
    - **Task:** Ensure that all editors with placeholder `Adw.StatusPage` views include a prominent "Add" or "New" button within the placeholder itself, providing a clear call to action for the user.
