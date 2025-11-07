"""The welcome window for the AdvEngine application."""

import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "welcome.ui"))
class WelcomeWindow(Adw.ApplicationWindow):
    """The main welcome window for the application."""
    __gtype_name__ = "WelcomeWindow"

    new_project_button = Gtk.Template.Child()
    open_project_button = Gtk.Template.Child()
    recent_projects_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new WelcomeWindow instance."""
        super().__init__(**kwargs)

        self.new_project_button.connect("clicked", lambda w: self.get_application().lookup_action("new-project").activate(None))
        self.open_project_button.connect("clicked", lambda w: self.get_application().lookup_action("open-project").activate(None))

        settings = self.get_application().settings_manager
        recent_projects = settings.get_app_setting("recent_projects")
        self.populate_recent_projects(recent_projects)

    def populate_recent_projects(self, recent_projects: list[str]):
        """Populates the recent projects list.

        Args:
            recent_projects: A list of paths to recent projects.
        """
        # Clear existing
        while self.recent_projects_list.get_first_child():
            self.recent_projects_list.remove(
                self.recent_projects_list.get_first_child())

        for project_path in recent_projects:
            row = Adw.ActionRow(title=project_path)
            button = Gtk.Button(label="Open")
            button.connect("clicked", self.on_open_recent, project_path)
            row.add_suffix(button)
            row.set_activatable_widget(button)
            self.recent_projects_list.append(row)

    def on_open_recent(self, button: Gtk.Button, project_path: str):
        """Handles the clicked signal from a recent project's open button.

        Args:
            button: The button that was clicked.
            project_path: The path of the project to open.
        """
        self.get_application().load_project(project_path)
