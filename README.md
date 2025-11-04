# AdvEngine

AdvEngine is a data and configuration manager used to create 2.5D cyberpunk
adventure games that target Unreal Engine 5.6. It provides a modern,
cross-platform UI for designing and exporting structured data files for the
target game engine to consume at runtime.

## Features

*   **Scene Editor:** Design your game world by creating scenes, defining walk
    meshes, placing hotspots, and setting up camera safe areas.
*   **Logic Editor:** A powerful node-graph editor for creating puzzle logic,
    dialogue trees, and quest branching.
*   **Asset Manager:** Import and manage game assets like sprites and
    animations.
*   **Global State Manager:** Define and manage global game variables.
*   **Database Editor:** Easily edit game data such as items, character
    attributes, NPCs, and shops.
*   **Audio Manager:** Assign background music, ambient sounds, and localized
    sound effects.
*   **Quest Editor:** A dedicated editor for creating and managing quests and
    their objectives.
*   **Global Search:** A powerful search feature to quickly find assets, logic
    nodes, and database entries.
*   **Modern UI:** A modern, HIG-compliant user interface built with Libadwaita
    for a polished and consistent look and feel.

## Installation

To run AdvEngine, you need Python 3.10+ and GTK4.

**System Dependencies:**

```bash
sudo apt-get update && sudo apt-get install -y \\
    python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

**Python Dependencies:**

```bash
pip install PyGObject
```

## Launching

To launch the application, run the following command from the root of the project:

```bash
python3 -m adv_engine.src.main
```
