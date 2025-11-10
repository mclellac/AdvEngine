"""The welcome window for the AdvEngine application.

This module defines the WelcomeWindow class, which is the initial window
displayed to the user upon starting the application. It provides options to
create a new project, open an existing one, or select from a list of recent
projects.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "welcome.ui"))
class WelcomeWindow(Adw.ApplicationWindow):
    """The main welcome window for the application.

    This window is the first point of interaction for the user. It presents
    a clean interface for project management before the main editor is shown.

    Attributes:
        settings: A reference to the application's SettingsManager instance.
    """

    __gtype_name__ = "WelcomeWindow"

    new_project_button: Gtk.Button = Gtk.Template.Child()
    open_project_button: Gtk.Button = Gtk.Template.Child()
    recent_projects_list: Gtk.ListBox = Gtk.Template.Child()
    recent_projects_group: Adw.PreferencesGroup = Gtk.Template.Child()
    menu_button: Gtk.MenuButton = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new WelcomeWindow instance."""
        super().__init__(**kwargs)

        menu = Gio.Menu.new()
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu.append("About", "app.about")
        self.menu_button.set_menu_model(menu)

        self.new_project_button.connect(
            "clicked",
            lambda w: self.get_application()
            .lookup_action("new-project")
            .activate(None),
        )
        self.open_project_button.connect(
            "clicked",
            lambda w: self.get_application()
            .lookup_action("open-project")
            .activate(None),
        )

        self.settings = self.get_application().settings_manager
        self.populate_recent_projects()

    def populate_recent_projects(self):
        """Populates the list of recent projects from settings.

        This method reads the list of recent projects from the SettingsManager,
        clears the existing list in the UI, and then repopulates it with
        widgets for each recent project.
        """
        # Clear existing
        while child := self.recent_projects_list.get_first_child():
            self.recent_projects_list.remove(child)

        recent_projects = self.settings.get_app_setting("recent_projects")
        for project_path in recent_projects:
            row = Adw.ActionRow()
            row.set_title(os.path.basename(project_path))
            row.set_subtitle(project_path)

            open_button = Gtk.Button(label="Open")
            open_button.connect("clicked", self.on_open_recent, project_path)
            row.add_suffix(open_button)

            remove_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
            remove_button.connect("clicked", self.on_remove_recent, project_path)
            row.add_suffix(remove_button)

            row.set_activatable_widget(open_button)
            self.recent_projects_list.append(row)

        self.recent_projects_group.set_visible(bool(recent_projects))

    def on_open_recent(self, button: Gtk.Button, project_path: str):
        """Handles the click event for a recent project's 'Open' button.

        Args:
            button (Gtk.Button): The button that was clicked.
            project_path (str): The path of the project to open.
        """
        self.get_application().load_project(project_path)

    def on_remove_recent(self, button: Gtk.Button, project_path: str):
        """Handles the click event for a recent project's 'Remove' button.

        Args:
            button (Gtk.Button): The button that was clicked.
            project_path (str): The path of the project to remove.
        """
        self.settings.remove_recent_project(project_path)
        self.populate_recent_projects()
