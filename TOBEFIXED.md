# AdvEngine: Items to be Fixed

This document outlines a comprehensive list of bugs, incomplete features, and architectural issues identified in the AdvEngine application.

## I. Core Architectural Issues

### 1. Data Persistence & Management (`ProjectManager`)

*   **Incomplete Save Logic:** The `ProjectManager` is missing save functionality for several data types, most notably CSV-based data like `CharacterData.csv`. The `_save_csv` method is implemented but never called. This is a critical bug.
*   **Inconsistent Error Handling:** File I/O operations lack consistent `try...except` blocks, making the application fragile.
*   **Redundant Load Logic:** The code for loading `LogicGraph` data is duplicated between `_load_logic_graphs` and `_load_dialogue_graphs`. This should be refactored into a single, reusable method.

### 2. Data Schemas (`data_schemas.py`)

*   **Insufficient Logic Node Schemas:** The `LogicNode`, `DialogueNode`, `ConditionNode`, and `ActionNode` dataclasses do not have the necessary fields to store the data entered in the UI. They rely on a generic `parameters` dictionary, which is not being correctly serialized and deserialized, leading to data loss.

## II. Editor-Specific Issues

### 1. Logic Editor (`module_logic.py`)

*   **Data Not Saving:** User input in the `DynamicNodeEditor` is not persisted. While the UI updates the in-memory `LogicNode` objects, these changes are lost because the `ProjectManager` does not serialize the updated attributes to JSON.
*   **Flawed Resizing Logic:** The drag-to-resize functionality for nodes is implemented incorrectly. The calculation does not properly use the drag offset, resulting in erratic and unpredictable resizing behavior.
*   **Redundant Node Creation Code:** The `on_add_node` methods in the sidebar are repetitive. This could be refactored into a single, parameterized method.

### 2. Asset Manager (`module_assets.py`)

*   **No File Type Validation:** The asset import functionality does not validate file types. Although the file chooser dialog uses a filter, the handler code does not check if the selected files are of a supported image or animation format.
*   **Placeholder Animation Editor:** The animation editor is largely non-functional. The drag-and-drop reordering of frames is a placeholder and does not work.

### 3. Audio Editor (`module_audio.py`)

*   **Placeholder Functionality:** The entire editor is a placeholder.
*   **Fake Waveform Display:** The waveform visualization is generated with random data and does not represent the actual audio content.
*   **Missing Features:** Basic audio playback controls are present, but there is no functionality for trimming, looping, or otherwise editing audio clips.

### 4. General UI/UX Issues

*   **Hardcoded Editor List:** The list of editor modules in `main.py` is hardcoded. A more robust solution would be to discover and load modules dynamically.
*   **Missing "Empty State" Placeholders:** Many editors lack `Adw.StatusPage` widgets to guide the user when no data is present.
*   **Inconsistent Localization Support:** The `ProjectManager` includes placeholder methods for localization import/export, but the functionality is incomplete and not integrated into the UI.
