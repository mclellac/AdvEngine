> **Note:** This document describes the planned functionality of the Asset Manager. As of the current version, only the **Images** section is functional. The Audio and Fonts sections are not yet implemented.

# Editor Reference: Asset Manager

The Asset Manager is the central hub for importing and organizing all the visual assets for your game, such as character sprite sheets, item icons, and background images.

## 1. Purpose

-   **Import Media**: Provides a simple interface for importing image files into the project.
-   **Organize Assets**: Gives each imported asset a unique ID that can be referenced by other editors (e.g., the Character Editor).
-   **Preview Assets**: Allows you to view imported images and animations.
-   **Define Animations**: Includes a simple editor for defining frame-based animations from a sprite sheet.

## 2. Interface Overview

The Asset Manager is divided into an asset list, a thumbnail grid, and a preview panel.

![Asset Manager Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Asset List

A simple list on the left displays all the assets in the project, organized by type (e.g., Sprites, Animations).

### B. Thumbnail Grid View

The central area displays thumbnails of all imported assets, providing a quick visual overview of your asset library. Clicking on a thumbnail selects the asset and displays its details in the Preview Panel.

### C. Preview Panel

Located on the right, this panel displays a larger preview of the selected asset.
-   **Image Preview**: For static images, it shows the full image.
-   **Animation Editor**: If the selected asset is a sprite sheet designated for animations, this panel will transform into an animation editor, allowing you to define sequences of frames.
-   **Properties**: Displays the asset's ID and file path.

## 3. Workflows

### A. Importing an Asset

1.  Click the "Import Asset" button.
2.  A file chooser will appear. Select one or more image files to import.
3.  For each file, you will be prompted to provide a unique **Asset ID**. This ID is how you will refer to this asset in other parts of the engine (e.g., in a `Character`'s `portrait_asset_id` field).
4.  The imported asset will now appear in the thumbnail grid.

### B. Defining an Animation from a Sprite Sheet

1.  Import a sprite sheet that contains multiple frames of an animation.
2.  Select the imported sprite sheet in the grid.
3.  In the Preview Panel, which now shows the animation editor, you can define an animation sequence.
4.  Click "Add Animation" and give the new animation a name (e.g., "walk_down").
5.  Click and drag frames from the main sprite sheet view into the animation timeline at the bottom.
6.  You can reorder frames by dragging them in the timeline.
7.  Click the "Play" button to preview the animation.
8.  This animation can now be referenced by its name (e.g., "walk_down") in the `animations` field of a `Character`.
