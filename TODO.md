# AdvEngine UI/UX Improvement TODO List

This document tracks planned improvements to the user interface and user experience of the AdvEngine application.

## Global / Application-Wide Enhancements

- [x] **Unified Save Status Indicator**: Implement a global indicator (e.g., an asterisk `*` in the window title or a dot on the save button) to clearly show when there are unsaved changes.
- [x] **Comprehensive Tooltips**: Add `tooltip_text` to all toolbar buttons, icon-only buttons, and complex input fields across all modules to improve discoverability.
- [x] **Keyboard Shortcut System**: Implement and document keyboard shortcuts for common global actions (e.g., `Ctrl+S` for Save, `Ctrl+O` for Open, `Ctrl+N` for New Project).
- [x] **Consistent Empty States**: Design and implement informative "empty state" placeholders for all lists, views, and canvases. For example, when no scenes exist, the Scene Editor should display a message like "No Scenes Found. Click 'Add Scene' to Begin."
- [x] **Improved Error/Confirmation Dialogs**: Replace generic dialogs with more specific and helpful `Adw.MessageDialog`s that clearly explain the action, error, or confirmation.
- [x] **Application-Wide Search**: Consider a global search feature to quickly find assets, logic nodes, or database entries by name or ID.

## Module-Specific UI/UX Tasks

### Scene Editor (`module_scene.py`)

- [x] **Canvas Zoom & Pan**: Implement intuitive zoom (Ctrl+Scroll) and pan (Middle-mouse drag) controls for the scene canvas to handle large scenes.
- [x] **Visible Grid & Snapping**: Add an optional, toggleable grid to the canvas and enable snapping for precise placement of hotspots and props.
- [x] **Properties Panel**: When a hotspot is selected, display its coordinates (X, Y) and dimensions (Width, Height) in a dedicated properties sidebar for precise editing.
- [x] **Layer Management**: Add a simple list view to manage the Z-order (layering) of hotspots and props within a scene.

### Logic Editor (`module_logic.py`)

- [x] **Visual Node Distinction**: Enhance the visual differentiation between node types (Action, Condition, Dialogue) using unique icons or more distinct header colors.
- [x] **Canvas Mini-Map**: For large graphs, add an interactive mini-map that allows for quick navigation of the entire logic canvas.
- [x] **Curved Connectors**: Switch from straight-line connectors to Bézier curves for node connections to improve readability and reduce visual clutter.
- [x] **Right-Click Context Menus**: Add context-sensitive right-click menus on nodes (for actions like "Delete", "Duplicate", "Edit") and on the canvas (for "Add Node...").
- [x] **Node Information Displayed**: Nodes should be resizable, and also display the information set in them. There is no way to distingush between multiple nodes of the same type and what information they contain without clicking on them. This is not helpful. Nodes should show what they do to the user better without opening them.

### Asset Manager (`module_assets.py`)

- [x] **Thumbnail Previews**: Display image thumbnails in the asset list for quick visual identification instead of just filenames.
- [x] **Asset Preview Panel**: Add a dedicated panel that shows a larger preview of the selected sprite, texture, or animation sequence.
- [x] **Drag-and-Drop Reordering**: Allow users to reorder animation frames within a sequence using drag-and-drop.

### Audio Manager (`module_audio.py`)

- [x] **Embedded Audio Preview**: Integrate a simple audio player widget to allow users to preview sound effects and music tracks directly within the editor.
- [x] **Waveform Visualization**: For selected audio files, display a small waveform graphic to provide a visual representation of the sound.

### Database Editors (`item_editor.py`, `character_editor.py`, etc.)

- [x] **Use `Gtk.ColumnView`**: Replace the current `Adw.PreferencesGroup` or `Gtk.ListBox` with a more appropriate `Gtk.ColumnView` to provide a more traditional and efficient table/spreadsheet-like editing experience.
- [x] **List Filtering & Sorting**: Add controls to filter the database lists by name/ID and sort columns alphabetically or numerically.
- [ ] **Input Validation**: Implement real-time input validation on entry fields to prevent errors (e.g., ensuring a "price" field only accepts numeric input).
