# AdvEngine Interface Overview

The AdvEngine main window is designed to provide a clean, organized, and efficient workspace. It is built with modern Libadwaita components and follows the GNOME Human Interface Guidelines. The interface is composed of three main areas: the Header Bar, the Sidebar, and the Content Area.

## 1. Header Bar

The Header Bar is located at the top of the application window and provides access to global actions and navigation tools.

![Header Bar](placeholder.png) <!-- TODO: Add screenshot -->

-   **Toggle Sidebar Button**: Located on the far left, this button shows or hides the main sidebar. This is useful for maximizing the content area when working in a detailed editor.
-   **Save Button**: Saves all unsaved changes in the current project. The main window title will display an asterisk (`*`) whenever there are unsaved changes. The `Ctrl+S` keyboard shortcut also triggers this action.
-   **Play Button**: Saves the project and then attempts to launch the Unreal Engine editor with the current project. The path to the Unreal Engine executable can be configured in the application preferences. The `Ctrl+P` keyboard shortcut also triggers this action.
-   **New Project Button**: Opens a dialog to create a new AdvEngine project in a selected directory.
-   **Global Search Bar**: Located on the right, this search entry allows you to search for any data entry across the entire project. Results are displayed in a dedicated search results view.
-   **Application Menu**: On the far right, this menu contains several application-level actions:
    -   **Preferences**: Opens the application preferences window, where you can configure settings like the theme and the path to the Unreal Engine editor.
    -   **Keyboard Shortcuts**: Opens a window that displays all available keyboard shortcuts for the application.
    -   **Export/Import Localization**: Provides tools for exporting all user-facing text to a file for translation, and importing it back into the project.
    -   **About**: Displays the application's "About" window with version and credit information.

## 2. Sidebar

The Sidebar is the primary navigation tool for AdvEngine. It lists all the available editor modules.

-   **Navigation List**: The sidebar contains a list of all editors. Clicking on an editor's name (e.g., "Scenes", "Logic", "Database") will open that editor in the Content Area.
-   **Collapsible**: The sidebar can be hidden using the toggle button in the Header Bar to provide more space for the content area.

## 3. Content Area

The Content Area is the main workspace where the currently selected editor is displayed.

-   **View Stack**: The content area is managed by a `Adw.ViewStack`, which allows for seamlessly switching between different editors without losing their state.
-   **Welcome Page**: When no project is loaded or no editor is selected, a welcome page is displayed.
-   **Status Pages**: If an editor has no data to display (e.g., no scenes have been created yet), it will show a status page with a helpful message and often a button to create the first item.
