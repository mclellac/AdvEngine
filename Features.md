# AdvEngine Feature Checklist

This document tracks the status of major features and refactoring efforts.

## UI Refactoring (GtkBuilder XML)

The primary goal is to move all UI layout definitions from procedural Python code to declarative `.ui` files.

- [x] **Main Application Window (`EditorWindow`)**
- [x] **Scene Editor (`module_scene.py`)**
- [x] **Logic Editor (`module_logic.py`)**
- [x] **Dialogue Editor (`module_dialogue.py`)**
- [x] **Interaction Editor (`module_interaction.py`)**
- [ ] **Quest Editor (`module_quest.py`)**
- [x] **Asset Manager (`module_assets.py`)**
- [x] **Database Editor (`module_database.py`)**
- [x] **Character Editor (`module_character.py`)**
- [ ] **Global State Editor (`module_state.py`)**
- [x] **Welcome Window (`welcome.py`)**
- [x] **Preferences Dialog (`preferences.py`)**
- [x] **Shortcuts Dialog (`shortcuts.py`)**

## Core Features

- [x] Project Creation, Loading, Saving
- [x] Scene Editor with Hotspot manipulation
- [x] Node-based Logic Editor
- [x] Tree-based Dialogue Editor
- [ ] **Asset Manager (Images: Implemented, Audio/Fonts: Not Implemented)**
- [x] Character Manager
- [ ] **Quest System (Not Implemented)**
- [x] Interaction System (Verb + Item, Item + Item)
- [ ] **Global State Management (Not Implemented)**
- [x] Database Editors (Items, Attributes, Verbs)
- [x] Localization Support (Import/Export)
- [x] Application-wide Search
- [x] Unreal Engine Integration (Play button)
- [x] Settings/Preferences Management
- [x] Keyboard Shortcuts
- [x] Recent Projects on Welcome Screen
- [x] Project Templates
