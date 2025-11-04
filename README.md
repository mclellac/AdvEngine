# AdvEngine

AdvEngine is a data and configuration manager for creating 2.5D point-and-click adventure games, in the style of classic Sierra On-Line titles, that target Unreal Engine 5.6. It provides a modern, cross-platform UI for designing game logic, managing assets, and exporting structured data files for the target game engine to consume at runtime.

## Features

*   **Scene Editor:** A canvas-based editor to design game worlds by creating scenes, setting background images, placing interactive hotspots, and managing their Z-order.
*   **Logic Editor:** A powerful node-graph editor for creating puzzle logic and branching flows using conditions and actions.
*   **Interaction Editor:** A dedicated editor to define complex `Verb + Item` and `Item + Item` interactions that trigger logic graphs.
*   **Dialogue Editor:** A tree-based editor for writing and structuring branching character dialogues.
*   **Cutscene Editor:** A simple, script-based editor for creating and managing in-game cutscenes.
*   **Asset Manager:** Import and manage game assets like sprites and animations, with a built-in preview panel.
*   **Database Editors:** A suite of modern, spreadsheet-style editors for managing game data, with full inline editing and search capabilities:
    *   Items
    *   Character Attributes
    *   Verbs
    *   Characters (with portrait previews)
*   **Global State Manager:** Define and manage global variables that track the game's state throughout the player's journey.
*   **Quest Editor:** A dedicated editor for creating and managing multi-step quests and their objectives.
*   **Audio Editor:** Manage and preview background music and sound effects.
*   **UI Builder & Font Manager:** Tools for designing the in-game UI and managing fonts.
*   **Global Search:** A project-wide search feature to quickly find any asset, logic node, or database entry.
*   **Modern UI:** A clean, GNOME HIG-compliant user interface built with Libadwaita for a polished and consistent cross-platform experience.

## Building and Running

AdvEngine uses the Meson build system.

### 1. System Dependencies

First, install the necessary system libraries for your platform.

For **Debian/Ubuntu**:
```bash
sudo apt-get install -y gettext libglib2.0-dev desktop-file-utils xvfb \\
python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 libcairo2-dev \\
pkg-config python3-dev libgirepository1.0-dev gir1.2-gst-plugins-base-1.0 \\
gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

### 2. Python Dependencies

Install Meson and Ninja:
```bash
pip install meson ninja
```

### 3. Compile and Install

Configure, compile, and install the application into a local directory:
```bash
meson setup build --prefix=/tmp/advengine-install
meson compile -C build
meson install -C build
```

### 4. Launching

Run the application from the installation directory:
```bash
/tmp/advengine-install/bin/advengine
```

## Documentation

For a detailed guide on how to use the editors and a step-by-step tutorial, please see the documents in the `/docs` directory.
