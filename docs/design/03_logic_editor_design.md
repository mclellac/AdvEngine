# AdvEngine - Logic Editor Design

## 1. Introduction

This document provides a detailed design specification for the Logic Editor in the AdvEngine application. It covers the editor's internal architecture, its data model, and the complete data persistence workflow.

## 2. Architecture

The Logic Editor is a complex component with a clear separation between its UI and its data. The following is a breakdown of its key architectural components:

*   **`LogicEditor` (`module_logic.py`):** The main UI class for the Logic Editor. It is a `Gtk.Box` that contains the canvas, the minimap, and the properties panel. It is responsible for:
    *   Drawing the node graph on the canvas.
    *   Handling all user input, including node selection, dragging, and connecting.
    *   Managing the properties panel and updating it when the selected node changes.
*   **`DynamicNodeEditor` (`module_logic.py`):** A reusable component for creating a properties editor for a given node. It dynamically builds its UI based on the type of the node and the parameters defined in `ue_exporter.py`.
*   **`LogicGraph` (`data_schemas.py`):** The core data model for the Logic Editor. It is a `dataclass` that contains a list of `LogicNode` objects.
*   **`LogicNode` (`data_schemas.py`):** The base `dataclass` for all nodes in the Logic Editor. It has several subclasses (`DialogueNode`, `ConditionNode`, `ActionNode`) that represent the different types of nodes.

## 3. Data Persistence Workflow

The following is a step-by-step description of the data persistence workflow in the Logic Editor:

1.  **Loading:**
    *   When a project is opened, the `ProjectManager` calls the `_load_logic_graphs` method.
    *   This method reads the `LogicGraphs.json` file and deserializes the JSON data into a list of `LogicGraph` objects.
    *   The `LogicEditor` is then initialized with a reference to the loaded `LogicGraph`.

2.  **Editing:**
    *   The user interacts with the `LogicEditor` to create, modify, or delete nodes.
    *   When a node is selected, the `DynamicNodeEditor` is populated with the node's data.
    *   When the user modifies a value in the `DynamicNodeEditor`, the `on_value_changed` method is called.
    *   This method updates the corresponding attribute on the `LogicNode` object in memory.
    *   The `ProjectManager` is then notified that the project has been modified, and the "dirty" state is set to `True`.

3.  **Saving:**
    *   When the user saves the project, the `ProjectManager` calls the `_save_logic_graphs` method.
    *   This method serializes the list of `LogicGraph` objects into JSON data using the `to_dict` method on the `LogicGraph` and `LogicNode` objects.
    *   The JSON data is then written to the `LogicGraphs.json` file.

## 4. Key Design Decisions

*   **`to_dict` for Serialization:** The `LogicGraph` and `LogicNode` classes use a custom `to_dict` method for serialization. This is to ensure that all dynamically added attributes (such as UI-specific data) are correctly persisted.
*   **`DynamicNodeEditor`:** The use of a dynamic properties editor allows for a flexible and extensible design. New node types and parameters can be added simply by updating the definitions in `ue_exporter.py`, without requiring any changes to the UI code.
*   **Separation of Concerns:** The clear separation between the data model (`LogicGraph`, `LogicNode`) and the UI (`LogicEditor`, `DynamicNodeEditor`) makes the code easier to understand, maintain, and test.
