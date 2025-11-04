# AdvEngine Feature Checklist

This document outlines the features of the AdvEngine, tracked and updated by the development agent.

## Core Functionality
- [x] **Project Management**: Create, load, and save AdvEngine projects.
- [x] **Cross-Platform Support**: Runs on Windows, macOS, and Linux.
- [x] **UE5 Export**: Exports data to formats compatible with Unreal Engine 5.6.

## Editors
### Database-Style Editors
All database-style editors feature a modern, spreadsheet-like interface with inline editing, search/filtering, and full CRUD (Create, Read, Update, Delete) functionality.
- [x] **Verb Editor**: Manage in-game verbs (e.g., "Use", "Look", "Talk to").
- [x] **Attribute Editor**: Manage character attributes (e.g., "Strength", "Intelligence").
- [x] **Item Editor**: Manage in-game items, including their properties and prices.
- [x] **Global State Editor**: Manage global variables that track the game's state.
- [x] **Character Editor**: Manage player and non-player characters, with a portrait preview.

### Canvas-Based Editors
- [x] **Scene Editor**:
    - [x] Create and manage scenes.
    - [x] Set background images.
    - [x] Create, select, and delete hotspots.
    - [x] Edit hotspot properties in a dedicated panel.
    - [x] Manage hotspot Z-ordering with a layer list.
    - [x] Zoom and pan the canvas.
- [x] **Logic Editor**:
    - [x] Create and manage logic graphs.
    - [x] Add, delete, and connect nodes (Dialogue, Condition, Action).
    - [x] Edit node properties in a dedicated panel.
    - [x] Multi-node selection via Shift-click and drag-to-select.
    - [x] Multi-node dragging.
    - [x] Resizable nodes.
    - [x] Right-click context menus for quick actions.
    - [x] Interactive mini-map for navigation.
