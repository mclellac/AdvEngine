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
    recent_projects_group = Gtk.Template.Child()
    quit_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new WelcomeWindow instance."""
        super().__init__(**kwargs)

        self.new_project_button.connect("clicked", lambda w: self.get_application().lookup_action("new-project").activate(None))
        self.open_project_button.connect("clicked", lambda w: self.get_application().lookup_action("open-project").activate(None))
        self.quit_button.connect("clicked", lambda w: self.close())

        self.settings = self.get_application().settings_manager
        self.populate_recent_projects()

    def populate_recent_projects(self):
        """Populates the recent projects list."""
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
        """Handles the clicked signal from a recent project's open button."""
        self.get_application().load_project(project_path)

    def on_remove_recent(self, button: Gtk.Button, project_path: str):
        """Handles the clicked signal from a recent project's remove button."""
        self.settings.remove_recent_project(project_path)
        self.populate_recent_projects()
