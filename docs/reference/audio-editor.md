# Editor Reference: Audio Editor

The Audio Editor is used to manage all the sound files for your project, including background music (BGM) and sound effects (SFX).

## 1. Purpose

-   **Import Audio Files**: Provides an interface for importing audio files (e.g., `.mp3`, `.wav`, `.ogg`) into the project.
-   **Organize Audio**: Assigns a unique ID to each imported audio file, which can be used to trigger them from logic graphs or cutscenes.
-   **Preview Audio**: Includes an embedded media player to listen to imported audio files directly within the editor.

## 2. Interface Overview

The Audio Editor has a simple layout with an audio file list and a preview panel.

![Audio Editor Layout](placeholder.png) <!-- TODO: Add screenshot -->

### A. Audio File List

The main part of the editor is a list of all the audio files in the project.
-   **Columns**: The list displays the `ID` of the audio file, its file path, and its type (BGM or SFX).
-   **Add/Remove**: Use the "+" and "-" buttons at the bottom to import new audio files or delete existing entries.

### B. Preview Panel

When you select an audio file from the list, the preview panel at the bottom of the editor becomes active.
-   **Media Controls**: The panel contains standard media controls, including a play/pause button, a progress bar, and a volume control.
-   **Functionality**: This allows you to quickly preview any sound without leaving AdvEngine.

## 3. Schema

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | String | The unique identifier for the audio file (e.g., `main_theme`, `door_unlock_sfx`). This is the ID you will use to play the sound. |
| `path` | String | The path to the audio file on your filesystem. |
| `type` | String (Dropdown)| The category of the audio file. Can be either `BGM` (for long, looping tracks) or `SFX` (for short, one-shot effects). |
| `volume` | Float | The default volume for the sound, from 0.0 to 1.0. |
| `loop` | Boolean | If `true`, the audio will loop indefinitely when played (typically used for BGM). |

## 4. Workflow

### A. Importing a Sound Effect

1.  Open the Audio Editor from the main sidebar.
2.  Click the "+" button.
3.  A file chooser will appear. Select the sound effect file you want to import.
4.  A new row will be added to the list. Fill out its properties:
    -   `id`: `door_unlock_sfx`
    -   `type`: `SFX`
    -   `volume`: `0.8`
    -   `loop`: `false`
5.  Select the new row and click the play button in the preview panel to confirm it works.

### B. Triggering the Sound Effect in the Game

To play this sound effect, you would use an `ActionNode` in a `LogicGraph` (or a command in a cutscene).

-   **Example**: In your `unlock_door_logic` graph, you would add an `ActionNode` with the following properties:
    -   **Command**: `PLAY_SFX`
    -   **Parameters**: `sfx_id: "door_unlock_sfx"`

Now, when that logic graph is executed, the `door_unlock_sfx` sound will play.
