# Editor Reference: Scene Editor

The Scene Editor is a powerful, canvas-based tool for creating the visual environments of your game. Here, you will import background art, define interactive areas (hotspots), and manage their layering.

## 1. Purpose

The primary purpose of the Scene Editor is to:
-   **Create and Manage Scenes**: Each distinct location in your game is a "scene."
-   **Define Interactivity**: Designate which parts of the scene the player can interact with by creating "hotspots."
-   **Control Visuals**: Set the background artwork for each scene.
-   **Manage Layering**: Control the draw order (Z-order) of hotspots to ensure they appear correctly in front of or behind each other.

## 2. Interface Overview

The Scene Editor is divided into three main parts: the Scene List, the Canvas, and the Properties Panel.

![Scene Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Scene List

Located on the far left, this list displays all the scenes in your project.
-   **Creating a Scene**: Click the "+" button at the bottom of the list to create a new scene. You will be prompted to provide a unique ID.
-   **Selecting a Scene**: Click on a scene's name in the list to open it for editing in the canvas.
-   **Deleting a Scene**: Select a scene and click the "-" button to delete it.

### B. Canvas

The canvas is the main visual workspace where you will build your scene.
-   **Background**: The background of the canvas displays the image you've set for the current scene.
-   **Hotspots**: Hotspots are displayed as colored rectangles overlaid on the background image.
    -   **Blue Rectangles**: Unselected hotspots.
    -   **Yellow Rectangle**: The currently selected hotspot.
-   **Navigation**:
    -   **Zoom**: Use `Ctrl + Mouse Wheel` to zoom in and out of the canvas.
    -   **Pan**: Click and drag with the **middle mouse button** to pan the canvas.

### C. Properties Panel

Located on the right, this panel is context-sensitive and displays the properties of the currently selected item (either the scene itself or a hotspot).

#### Scene Properties

When no hotspot is selected, the panel displays properties for the scene:
-   **ID**: The unique identifier for the scene. (Read-only)
-   **Background Image**: A file path to the background image for the scene. Click the "..." button to open a file chooser and select an image.
-   **Show Grid**: Toggles the visibility of a grid on the canvas to help with alignment.

#### Hotspot Properties

When a hotspot is selected, the panel displays its properties:
-   **ID**: The unique identifier for the hotspot. This is crucial for linking the hotspot to logic in the Interaction Editor.
-   **Name**: A user-friendly name for the hotspot (optional).
-   **Position & Size**: The X and Y coordinates and the Width and Height of the hotspot. These can be adjusted numerically here, or by dragging and resizing the hotspot on the canvas.

#### Layer List

At the bottom of the properties panel is the Layer List, which controls the Z-order of the hotspots.
-   **Drag-and-Drop**: You can click and drag hotspots in this list to reorder them.
-   **Render Order**: Hotspots at the **top** of the list are drawn **first** (appearing in the back), while hotspots at the **bottom** are drawn **last** (appearing in the front).

## 3. Workflows

### A. Creating a New Scene

1.  Open the Scene Editor from the main sidebar.
2.  Click the "+" button in the Scene List.
3.  Enter a unique ID for your scene (e.g., `storage_closet`) and click "OK."
4.  With the new scene selected, go to the Properties Panel.
5.  Click the "..." button next to "Background Image" and select an image file from your computer.

### B. Adding and Editing Hotspots

1.  Select the scene you want to edit from the Scene List.
2.  Click and drag on the canvas to draw a new hotspot rectangle.
3.  The new hotspot will appear as a blue rectangle and will be automatically selected (turning it yellow).
4.  In the Properties Panel, give the hotspot a unique **ID** (e.g., `closet_door`).
5.  You can resize the hotspot by clicking and dragging its corners and edges, or move it by clicking and dragging its center.

### C. Managing Hotspot Layers

1.  Create two or more hotspots that overlap.
2.  In the Layer List in the Properties Panel, observe their order.
3.  Click and drag one hotspot above or below another in the list.
4.  Notice how their drawing order changes on the canvas, with the one lower in the list appearing on top.
