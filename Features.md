# AdvEngine Feature Checklist

This document tracks the status of major features and refactoring efforts.

## UI Refactoring (GtkBuilder XML)

The primary goal is to move all UI layout definitions from procedural Python code to declarative `.ui` files.

- [ ] **Main Application Window (`EditorWindow`)**
    - [ ] Create `main_window.ui`
    - [ ] Refactor `main.py` to load `main_window.ui`
- [ ] **Scene Editor (`module_scene.py`)**
    - [ ] Create `module_scene.ui`
    - [ ] Refactor `module_scene.py` to load `module_scene.ui`
- [ ] **Logic Editor (`module_logic.py`)**
    - [ ] Create `module_logic.ui`
    - [ ] Refactor `module_logic.py` to load `module_logic.ui`
- [ ] **Dialogue Editor (`module_dialogue.py`)**
    - [ ] Create `module_dialogue.ui`
    - [ ] Refactor `module_dialogue.py` to load `module_dialogue.ui`
- [ ] **Interaction Editor (`module_interaction.py`)**
    - [ ] Create `module_interaction.ui`
    - [ ] Refactor `module_interaction.py` to load `module_interaction.ui`
- [ ] **Quest Editor (`module_quest.py`)**
    - [ ] Create `module_quest.ui`
    - [ ] Refactor `module_quest.py` to load `module_quest.ui`
- [ ] **Asset Manager (`module_assets.py`)**
    - [ ] Create `module_assets.ui`
    - [ ] Refactor `module_assets.py` to load `module_assets.ui`
- [ ] **Database Editor (`module_database.py`)**
    - [ ] Create `module_database.ui`
    - [ ] Refactor `module_database.py` to load `module_database.ui`
- [ ] **Character Editor (`module_character.py`)**
    - [ ] Create `module_character.ui`
    - [ ] Refactor `module_character.py` to load `module_character.ui`
- [ ] **Global State Editor (`module_state.py`)**
    - [ ] Create `module_state.ui`
    - [ ] Refactor `module_state.py` to load `module_state.ui`
- [ ] **Item Editor (`item_editor.py`)**
    - [ ] Create `item_editor.ui`
    - [ ] Refactor `item_editor.py` to load `item_editor.ui`
- [ ] **Attribute Editor (`attribute_editor.py`)**
    - [ ] Create `attribute_editor.ui`
    - [ ] Refactor `attribute_editor.py` to load `attribute_editor.ui`
- [ ] **Verb Editor (`verb_editor.py`)**
    - [ ] Create `verb_editor.ui`
    - [ ] Refactor `verb_editor.py` to load `verb_editor.ui`
- [ ] **Welcome Window (`welcome.py`)**
    - [ ] Create `welcome.ui`
    - [ ] Refactor `welcome.py` to load `welcome.ui`
- [ ] **Preferences Dialog (`preferences.py`)**
    - [ ] Create `preferences.ui`
    - [ ] Refactor `preferences.py` to load `preferences.ui`
- [ ] **Shortcuts Dialog (`shortcuts.py`)**
    - [ ] Create `shortcuts.ui`
    - [ ] Refactor `shortcuts.py` to load `shortcuts.ui`

## Core Features

- [x] Project Creation, Loading, Saving
- [x] Scene Editor with Hotspot manipulation
- [x] Node-based Logic Editor
- [x] Tree-based Dialogue Editor
- [ ] Asset Manager (Images, Audio, Fonts)
- [ ] Character Manager
- [ ] Quest System
- [ ] Interaction System (Verb + Item, Item + Item)
- [ ] Global State Management
- [ ] Database Editors (Items, Attributes, Verbs)
- [ ] Localization Support (Import/Export)
- [ ] Application-wide Search
- [ ] Unreal Engine Integration (Play button)
- [ ] Settings/Preferences Management
- [ ] Keyboard Shortcuts
- [ ] Recent Projects on Welcome Screen
- [ ] Project Templates
