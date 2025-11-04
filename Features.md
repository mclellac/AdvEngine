# AdvEngine Feature Checklist

This document outlines the features of the AdvEngine, tracked and updated by the development agent.

## Core Functionality
- [x] **Project Management**: Create, load, and save AdvEngine projects.
- [x] **Manual Save Model**: Tracks unsaved changes (`is_dirty` state) with manual save via button or `Ctrl+S`.
- [x] **Meson Build System**: The project is built and installed using Meson and Ninja.
- [x] **Cross-Platform Support**: Runs on Windows and Linux.
- [x] **UE5 Export**: Exports data to formats compatible with Unreal Engine 5.6.
- [x] **Global Search**: Project-wide search for all data types.

## Main Window & UI
- [x] **Modern UI**: A clean, GNOME HIG-compliant user interface built with Libadwaita.
- [x] **Overlay Split View**: Main layout with a collapsible sidebar for navigation.
- [x] **View Stack**: The central content area dynamically switches between editors.
- [x] **Preferences Window**: A dedicated window for application and project settings.
- [x] **Shortcuts Window**: A dedicated window displaying all keyboard shortcuts.

## Editors
### Logic & Narrative Editors
- [x] **Logic Editor** (Node-Based):
    - [x] Create and manage generic `LogicGraph` data.
    - [x] Add, delete, and connect nodes (Condition, Action).
    - [x] Edit node properties in a non-modal side panel.
    - [x] Multi-node selection via Shift-click and drag-to-select.
    - [x] Multi-node dragging.
    - [x] Resizable nodes.
    - [x] Right-click context menus for quick actions.
    - [x] Interactive mini-map for navigation.
- [x] **Interaction Editor**:
    - [x] Define `Verb + Item` and `Item + Item` interactions.
    - [x] Link interactions to a `LogicGraph`.
- [x] **Dialogue Editor** (Tree-Based):
    - [x] Create and manage branching dialogue trees.
    - [x] Embed `ActionNode`s within dialogue flows.
    - [x] Character portrait preview.
- [x] **Cutscene Editor** (Script-Based):
    - [x] Create and manage `Cutscene` scripts composed of sequential actions.
- [x] **Quest Editor**:
    - [x] Define and manage multi-step quests and objectives.

### World & Asset Editors
- [x] **Scene Editor** (Canvas-Based):
    - [x] Create and manage scenes with background images.
    - [x] Create, select, and delete hotspots.
    - [x] Edit hotspot properties in a non-modal side panel.
    - [x] Manage hotspot Z-ordering with a drag-and-drop layer list.
    - [x] Zoom (Ctrl+Scroll) and pan (middle-mouse drag) the canvas.
- [x] **Asset Manager**:
    - [x] Import and manage sprite and animation assets.
    - [x] Thumbnail grid view for easy browsing.
    - [x] Asset preview panel.
- [x] **Audio Editor**:
    - [x] Manage background music and sound effect files.
    - [x] Embedded audio player for previewing sounds.

### Database-Style Editors
All database-style editors feature a modern, spreadsheet-like interface (`Gtk.ColumnView`) with inline editing, search/filtering, and full CRUD functionality.
- [x] **Item Editor**: Manage in-game items, including their properties and prices.
- [x] **Character Editor**: Manage player and non-player characters, including portraits, sprite sheets, and animations.
- [x] **Attribute Editor**: Manage character attributes (e.g., "Strength", "Intelligence").
- [x] **Global State Editor**: Manage global variables that track the game's state.
- [x] **Verb Editor**: Manage in-game verbs (e.g., "Use", "Look", "Talk to").

### UI & Presentation Editors
- [x] **UI Builder**: A placeholder for a future visual UI layout editor.
- [x] **Font Manager**: Manage fonts for in-game text.
