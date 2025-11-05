import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

class WelcomeWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(600, 400)
        self.set_title("AdvEngine - Welcome")

        self.content = WelcomeWidget()
        self.set_content(self.content)

        settings = self.get_application().settings_manager
        recent_projects = settings.get_app_setting("recent_projects")
        self.content.populate_recent_projects(recent_projects)


class WelcomeWidget(Adw.Bin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.set_halign(Gtk.Align.CENTER)
        self.set_child(main_box)

        status_page = Adw.StatusPage.new()
        status_page.set_title("AdvEngine")
        status_page.set_icon_name("dialog-information-symbolic")
        status_page.set_description("Welcome to the Adventure Game Engine.")
        main_box.append(status_page)

        # --- Main Action Buttons ---
        button_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        main_box.append(button_box)

        new_project_button = Gtk.Button(label="New Project")
        new_project_button.connect("clicked", self.on_new_project)
        button_box.append(new_project_button)

        open_project_button = Gtk.Button(label="Open Project")
        open_project_button.connect("clicked", self.on_open_project)
        button_box.append(open_project_button)

        # --- Recent Projects List ---
        recent_projects_group = Adw.PreferencesGroup()
        recent_projects_group.set_title("Recent Projects")
        recent_projects_group.set_margin_top(20)
        main_box.append(recent_projects_group)

        self.recent_projects_list = Gtk.ListBox()
        self.recent_projects_list.set_selection_mode(Gtk.SelectionMode.NONE)
        recent_projects_group.add(self.recent_projects_list)

    def populate_recent_projects(self, recent_projects):
        # Clear existing
        while self.recent_projects_list.get_first_child():
            self.recent_projects_list.remove(self.recent_projects_list.get_first_child())

        for project_path in recent_projects:
            row = Adw.ActionRow(title=project_path)
            button = Gtk.Button(label="Open")
            button.connect("clicked", self.on_open_recent, project_path)
            row.add_suffix(button)
            row.set_activatable_widget(button)
            self.recent_projects_list.append(row)

    def on_new_project(self, button):
        self.get_ancestor(Adw.ApplicationWindow).get_application().lookup_action("new-project").activate(None)

    def on_open_project(self, button):
        self.get_ancestor(Adw.ApplicationWindow).get_application().lookup_action("open-project").activate(None)

    def on_open_recent(self, button, project_path):
        self.get_ancestor(Adw.ApplicationWindow).get_application().load_project(project_path)
