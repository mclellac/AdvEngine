# AdvEngine

AdvEngine is a data and configuration manager for creating 2.5D point-and-click adventure games, in the style of classic Sierra On-Line titles, that target Unreal Engine 5.6. It provides a modern, cross-platform UI for designing game logic, managing assets, and exporting structured data files for the target game engine to consume at runtime.

## Current Status

**This project is in active development.** Many core features are functional, but some are still under construction or exist as placeholders. Please consult the [TODO.md](./TODO.md) file for a detailed list of planned features and bug fixes.

## Getting Started

When you first launch AdvEngine, you'll be greeted with the Welcome screen. To start creating your game, click the "New Project" button. You will be prompted to give your project a name and choose a **Project Template**. These templates provide a complete, pre-configured starting point with characters, items, and logic to help you get started quickly.

For a detailed walkthrough, see the **[Tutorial](./docs/tutorials/01_locked_room.md)**.

## Features

*   **Project Templates:** Start your project from a pre-configured template based on classic Sierra On-Line adventure games, including *Space Quest*, *Police Quest*, *Hero's Quest*, and more.
*   **Scene Editor:** A canvas-based editor to design game worlds by creating scenes, setting background images, and placing interactive hotspots.
*   **Logic Editor:** A powerful node-graph editor for creating puzzle logic and branching flows.
*   **Interaction Editor:** A dedicated editor to define complex `Verb + Item` and `Item + Item` interactions that trigger logic graphs.
*   **Dialogue Editor:** A tree-based editor for writing and structuring branching character dialogues.
*   **Asset Manager:** Import and manage game assets. Currently supports images, with audio and font management planned for a future release.
*   **Database Editors:** A suite of modern, spreadsheet-style editors for managing game data, including Items, Attributes, Verbs, and Characters.
*   **Global Search:** A project-wide search feature to quickly find any asset, logic node, or database entry.
*   **Modern UI:** A clean, GNOME HIG-compliant user interface built with Libadwaita.
*   **Customizable Preferences:** A robust preferences window to manage your theme and editor settings.

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

Comprehensive documentation is available in the `/docs` directory, including:
- A **[User Guide](./docs/guide/introduction.md)** with a getting-started guide and an interface overview.
- An exhaustive **[Editor Reference](./docs/reference/)** detailing every editor.
- A **[Tutorial](./docs/tutorials/01_locked_room.md)** that walks you through creating a complete puzzle.
