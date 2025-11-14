"""Main entry point for the AdvEngine application.

This module contains the primary application class `AdvEngine`, which handles
the application lifecycle, and the `EditorWindow` class, which is the main UI
for the editor.
"""

import sys
import subprocess
import gi
import os
import logging
import importlib
import inspect
import argparse

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GObject
from .core.project_manager import ProjectManager
from .core.settings_manager import SettingsManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "ui/main_window.ui"))
class EditorWindow(Adw.ApplicationWindow):
    """The main window of the AdvEngine editor.

    This class represents the main editor interface, which is displayed after a
    project is loaded. It is responsible for discovering and loading all editor
    modules, managing the main layout, and handling user interactions such as
    saving the project and searching.

    Attributes:
        project_manager (ProjectManager): An instance of the ProjectManager
            for the currently loaded project.
        base_title (str): The base title for the window.
        logic_editor: A reference to the Logic Editor instance.
        search_results_view: A reference to the search results view.
    """

    __gtype_name__ = "EditorWindow"

    toggle_button: Gtk.ToggleButton = Gtk.Template.Child()
    save_button: Gtk.Button = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    new_project_button: Gtk.Button = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    content_stack: Gtk.Stack = Gtk.Template.Child()
    sidebar_list: Gtk.ListBox = Gtk.Template.Child()
    menu_button: Gtk.MenuButton = Gtk.Template.Child()
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()

    def __init__(self, project_manager: ProjectManager, **kwargs):
        """Initializes a new EditorWindow instance.

        Args:
            project_manager (ProjectManager): The project manager for the
                current project.
            **kwargs: Additional keyword arguments for the parent class.
        """
        from .ui import search_results

        super().__init__(**kwargs)
        logging.debug("EditorWindow.__init__: Initializing main editor window.")
        self.project_manager = project_manager
        self.base_title = "AdvEngine"
        self.set_title(self.base_title)

        self.project_manager.register_dirty_state_callback(self.on_dirty_state_changed)
        self.project_manager.register_error_callback(self.on_error)
        self.project_manager.register_project_saved_callback(self.on_project_saved)

        # Connect signals
        self.save_button.connect("clicked", self.on_save_clicked)
        self.play_button.connect("clicked", self._on_play_clicked)
        self.new_project_button.connect(
            "clicked",
            lambda w: self.get_application()
            .lookup_action("new-project")
            .activate(None),
        )
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)

        menu = Gio.Menu.new()
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu.append("About", "app.about")
        self.menu_button.set_menu_model(menu)

        self.toggle_button.bind_property(
            "active",
            self.split_view,
            "show-sidebar",
            GObject.BindingFlags.BIDIRECTIONAL,
        )

        self.logic_editor = None
        self.discover_and_add_editors()

        self.search_results_view = search_results.SearchResultsView()
        self.content_stack.add_named(self.search_results_view, "search_results")

        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(
            self.sidebar_list, self.sidebar_list.get_selected_row()
        )
        self.split_view.set_show_sidebar(True)

    def on_search_changed(self, search_entry: Gtk.SearchEntry):
        """Handles the search-changed signal from the search entry.

        Args:
            search_entry (Gtk.SearchEntry): The search entry that emitted the
                signal.
        """
        query = search_entry.get_text()
        if not query:
            if self.content_stack.get_visible_child_name() == "search_results":
                # Fallback to the first editor if search is cleared
                first_row = self.sidebar_list.get_row_at_index(0)
                if first_row:
                    self.content_stack.set_visible_child_name(first_row.get_name())
            return
        results = self.project_manager.search(query)
        self.search_results_view.update_results(results)
        self.content_stack.set_visible_child_name("search_results")

    def add_editor(self, name: str, view_name: str, widget: Gtk.Widget):
        """Adds an editor to the sidebar and content stack.

        Args:
            name (str): The display name of the editor.
            view_name (str): A unique identifier for the editor's view.
            widget (Gtk.Widget): The main widget for the editor.
        """
        row = Adw.ActionRow(title=name)
        list_box_row = Gtk.ListBoxRow(name=view_name, child=row)
        self.sidebar_list.append(list_box_row)
        self.content_stack.add_named(widget, view_name)

    def on_sidebar_activated(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        """Handles the row-activated signal from the sidebar list.

        Args:
            listbox (Gtk.ListBox): The listbox that emitted the signal.
            row (Gtk.ListBoxRow): The row that was activated.
        """
        if row:
            view_name = row.get_name()
            logging.debug(
                f"EditorWindow.on_sidebar_activated: Switching to view '{view_name}'."
            )
            self.content_stack.set_visible_child_name(view_name)

    def discover_and_add_editors(self):
        """Discovers and adds all available editors to the UI.

        This method scans the `src/ui` directory for Python modules that define
        an editor class, and then adds each discovered editor to the main
        window.
        """
        logging.debug("EditorWindow.discover_and_add_editors: Starting editor discovery.")
        editors = []
        discovered_view_names = set()
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        for filename in sorted(os.listdir(ui_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f".ui.{filename[:-3]}"
                try:
                    logging.debug(f"  Attempting to import module: {module_name}")
                    module = importlib.import_module(module_name, package="advengine")
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, "EDITOR_NAME"):
                            if obj.VIEW_NAME not in discovered_view_names:
                                logging.debug(f"    Found editor class: {name}")
                                editors.append(obj)
                                discovered_view_names.add(obj.VIEW_NAME)
                except Exception as e:
                    logging.error(f"Error discovering editor in {module_name}: {e}")
                    self.on_error(
                        "Failed to Load Editor",
                        f"An error occurred while loading the editor from {module_name}.\n\n{e}",
                    )

        editors.sort(key=lambda e: getattr(e, "ORDER", 999))

        for editor_class in editors:
            editor_instance = editor_class(
                project_manager=self.project_manager,
                settings_manager=self.get_application().settings_manager,
            )
            self.add_editor(
                editor_class.EDITOR_NAME, editor_class.VIEW_NAME, editor_instance
            )
            if editor_class.VIEW_NAME == "logic_editor":
                self.logic_editor = editor_instance

    def on_dirty_state_changed(self, is_dirty: bool):
        """Handles the dirty-state-changed signal from the project manager.

        Args:
            is_dirty (bool): The new dirty state.
        """
        self.set_title(f"{self.base_title}{'*' if is_dirty else ''}")

    def on_save_clicked(self, button: Gtk.Button):
        """Handles the clicked signal from the save button.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        self.get_application().save_project()

    def on_project_saved(self):
        """Displays a toast notification when the project is saved."""
        self.toast_overlay.add_toast(Adw.Toast.new("Project Saved"))

    def on_error(self, title: str, message: str):
        """Displays an error dialog to the user.

        If the application is in debug mode, the error is also printed to the
        console.

        Args:
            title (str): The title of the error dialog.
            message (str): The body text of the error dialog.
        """
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            print(f"ERROR DIALOG: {title} - {message}", file=sys.stderr)
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=title,
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_play_clicked(self, button: Gtk.Button):
        """Handles the clicked signal from the play button.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        self.get_application().save_project()
        ue_path = self.get_application().settings_manager.get("ue_path")
        if not ue_path:
            self.on_error(
                "Unreal Engine Path Not Set",
                "Please set the path to the Unreal Engine editor in the preferences.",
            )
            return
        project_file = f"{self.project_manager.project_path}/AdvEngine.uproject"
        try:
            subprocess.Popen([ue_path, project_file])
        except FileNotFoundError:
            self.on_error(
                "Unreal Engine Not Found",
                f"Could not find the Unreal Engine editor at the specified path: {ue_path}",
            )
        except Exception as e:
            self.on_error("Error Launching Engine", f"An unexpected error occurred: {e}")


class AdvEngine(Adw.Application):
    """The main application class for AdvEngine.

    This class is the entry point for the application. It is responsible for
    managing the application lifecycle, setting up application-level actions,
    and handling the creation and display of the main application windows.

    Attributes:
        project_manager (ProjectManager): The project manager for the currently
            loaded project.
        settings_manager (SettingsManager): The settings manager for the
            application.
        win (Gtk.Window): The currently active application window.
    """

    def __init__(self, **kwargs):
        """Initializes a new AdvEngine instance."""
        super().__init__(**kwargs)
        self.project_manager = None
        self.settings_manager = SettingsManager()
        self.win = None
        self.connect("activate", self.on_activate)

    def on_activate(self, app: Adw.Application):
        """Handles the activate signal of the application.

        Args:
            app (Adw.Application): The application instance.
        """
        from .ui import welcome

        self.win = welcome.WelcomeWindow(application=app)
        self.win.present()
        self._setup_actions()

    def _setup_actions(self):
        """Creates and sets up all application-level actions and shortcuts."""
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda a, p: self.save_project())
        self.add_action(save_action)
        self.set_accels_for_action("app.save", ["<Primary>s"])

        play_action = Gio.SimpleAction.new("play", None)
        play_action.connect(
            "activate",
            lambda a, p: (
                self.win._on_play_clicked(None)
                if hasattr(self.win, "_on_play_clicked")
                else None
            ),
        )
        self.add_action(play_action)
        self.set_accels_for_action("app.play", ["<Primary>p"])

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_activate)
        self.add_action(preferences_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.on_shortcuts_activate)
        self.add_action(shortcuts_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.add_action(about_action)

        new_project_action = Gio.SimpleAction.new("new-project", None)
        new_project_action.connect("activate", self.on_new_project_activate)
        self.add_action(new_project_action)

        open_project_action = Gio.SimpleAction.new("open-project", None)
        open_project_action.connect("activate", self.on_open_project_activate)
        self.add_action(open_project_action)

        export_localization_action = Gio.SimpleAction.new("export-localization", None)
        export_localization_action.connect("activate", self.on_export_localization)
        self.add_action(export_localization_action)

        import_localization_action = Gio.SimpleAction.new("import-localization", None)
        import_localization_action.connect("activate", self.on_import_localization)
        self.add_action(import_localization_action)

        self.setup_navigation_shortcuts()

    def setup_navigation_shortcuts(self):
        """Creates shortcuts for navigating between the main editor views."""
        shortcuts = {
            "1": "scenes_editor",
            "2": "logic_editor",
            "3": "interaction_editor",
            "4": "dialogue_editor",
            "6": "assets_editor",
            "7": "global_state_editor",
            "8": "character_manager",
            "9": "quest_editor",
            "0": "db_editor",
        }
        for key, view_name in shortcuts.items():
            action = Gio.SimpleAction(name=f"go-to-{view_name}")
            action.connect("activate", self.on_go_to, view_name)
            self.add_action(action)
            self.set_accels_for_action(f"app.go-to-{view_name}", [f"<Primary>{key}"])

    def on_go_to(self, action: Gio.SimpleAction, param: None, view_name: str):
        """Callback for the go-to navigation actions.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
            view_name (str): The name of the view to navigate to.
        """
        if self.win and isinstance(self.win, EditorWindow):
            self.win.content_stack.set_visible_child_name(view_name)
            for row in self.win.sidebar_list:
                if row.get_name() == view_name:
                    self.win.sidebar_list.select_row(row)
                    break

    def on_export_localization(self, action: Gio.SimpleAction, param: None):
        """Handles the export-localization action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export Localization")
        dialog.save(self.win, None, self.on_export_localization_response)

    def on_export_localization_response(self, dialog, result):
        """Handles the response from the export localization file dialog.

        Args:
            dialog: The file dialog.
            result: The result of the dialog.
        """
        try:
            file = dialog.save_finish(result)
            self.project_manager.export_localization(file.get_path())
        except Exception as e:
            logging.error(f"Error exporting localization: {e}")

    def on_import_localization(self, action: Gio.SimpleAction, param: None):
        """Handles the import-localization action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Import Localization")
        dialog.open(self.win, None, self.on_import_localization_response)

    def on_import_localization_response(self, dialog, result):
        """Handles the response from the import localization file dialog.

        Args:
            dialog: The file dialog.
            result: The result of the dialog.
        """
        try:
            file = dialog.open_finish(result)
            self.project_manager.import_localization(file.get_path())
        except Exception as e:
            logging.error(f"Error importing localization: {e}")

    def on_open_project_activate(self, action: Gio.SimpleAction, param: None):
        """Handles the open-project action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Open Project")
        dialog.select_folder(self.win, None, self.on_open_project_response)

    def on_open_project_response(self, dialog, result):
        """Handles the response from the open project folder dialog.

        Args:
            dialog: The file dialog.
            result: The result of the dialog.
        """
        try:
            folder = dialog.select_folder_finish(result)
            self.load_project(folder.get_path())
        except Exception as e:
            logging.error(f"Error opening project: {e}")

    def on_preferences_activate(self, action: Gio.SimpleAction, param: None):
        """Handles the preferences action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        from .ui import preferences

        dialog = preferences.PreferencesDialog(
            parent=self.win,
            project_manager=self.project_manager,
            settings_manager=self.settings_manager,
        )
        dialog.present()

    def on_shortcuts_activate(self, action: Gio.SimpleAction, param: None):
        """Handles the shortcuts action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        from .ui import shortcuts

        dialog = shortcuts.ShortcutsDialog(transient_for=self.win)
        dialog.present()

    def on_about_activate(self, action: Gio.SimpleAction, param: None):
        """Handles the about action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        dialog = Adw.AboutWindow(
            transient_for=self.win,
            application_name="AdvEngine",
            developer_name="Carey McLelland",
            version="0.1.0",
        )
        dialog.present()

    def save_project(self):
        """Saves the currently open project if it has unsaved changes."""
        if self.project_manager and self.project_manager.is_dirty:
            self.project_manager.save_project()

    def load_project(
        self, project_path: str, project_manager: ProjectManager = None
    ):
        """Loads a project and displays it in a new EditorWindow.

        This method closes the current window (if any) and opens a new
        EditorWindow for the specified project.

        Args:
            project_path (str): The path to the project to load.
            project_manager (ProjectManager, optional): An existing project
                manager instance. If not provided, a new one will be
                created. Defaults to None.
        """
        if project_manager:
            self.project_manager = project_manager
        else:
            self.project_manager = ProjectManager(project_path)
            self.project_manager.load_project()
        self.settings_manager.add_recent_project(project_path)
        new_win = EditorWindow(application=self, project_manager=self.project_manager)
        new_win.present()
        if self.win:
            self.win.close()
        self.win = new_win

    def on_new_project_activate(self, action: Gio.SimpleAction, param: None):
        """Handles the new-project action.

        Args:
            action (Gio.SimpleAction): The action that was activated.
            param: The parameter passed to the action (unused).
        """
        from .ui.new_project_dialog import NewProjectDialog

        dialog = NewProjectDialog(self.win)

        def on_response(d, response_id):
            if response_id == "create":
                name = dialog.get_project_name()
                template = dialog.get_selected_template()

                if not name or not template:
                    self.win.on_error(
                        "Error", "Project name and template are required."
                    )
                    return

                file_dialog = Gtk.FileDialog.new()
                file_dialog.set_title("Select Project Location")
                file_dialog.set_modal(True)
                file_dialog.select_folder(
                    self.win, None, self.on_new_project_folder_selected, name, template
                )
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def on_new_project_folder_selected(self, dialog, result, name, template):
        """Handles the response from the new project folder selection dialog.

        Args:
            dialog: The file dialog.
            result: The result of the dialog.
            name (str): The name of the new project.
            template (str): The template to use for the new project.
        """
        try:
            folder = dialog.select_folder_finish(result)
            project_path = os.path.join(folder.get_path(), name)
            project_manager, error = ProjectManager.create_project(
                project_path, template
            )
            if project_manager:
                self.load_project(project_path, project_manager=project_manager)
            else:
                logging.error(f"Error creating project: {error}")
        except Exception as e:
            logging.error(f"Error creating project: {e}")


def main(version: str = "0.1.0") -> int:
    """The main entry point of the application.

    Args:
        version (str): The version of the application.

    Returns:
        int: The exit code of the application.
    """
    parser = argparse.ArgumentParser(description="AdvEngine Game Editor")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging mode."
    )
    args, Gtk_args = parser.parse_known_args()

    log_level = logging.DEBUG if args.debug else logging.ERROR
    logging.basicConfig(level=log_level, format="%(levelname)s:%(name)s: %(message)s")
    logging.debug("Debug mode enabled.")

    app = AdvEngine(
        application_id="com.github.mclellac.AdvEngine",
        flags=Gio.ApplicationFlags.FLAGS_NONE,
    )
    return app.run([sys.argv[0]] + Gtk_args)


if __name__ == "__main__":
    main()
