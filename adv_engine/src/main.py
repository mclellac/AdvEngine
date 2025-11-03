import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio

from .core.project_manager import ProjectManager
from .ui.item_editor import ItemEditor
from .ui.character_editor import CharacterEditor
from .ui.attribute_editor import AttributeEditor
from .ui.module_scene import SceneEditor
from .ui.module_logic import LogicEditor
from .ui.module_assets import AssetEditor
from .ui.module_audio import AudioEditor
from .ui.preferences import PreferencesDialog
from .ui.shortcuts import ShortcutsDialog


class AdvEngineWindow(Adw.ApplicationWindow):
    def __init__(self, project_manager, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.base_title = "AdvEngine"
        self.set_title(self.base_title)
        self.set_default_size(1024, 768)

        self.project_manager.register_dirty_state_callback(self.on_dirty_state_changed)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        self.header = Adw.HeaderBar()
        self.main_box.append(self.header)

        save_button = Gtk.Button(label="Save")
        save_button.set_tooltip_text("Save project (Ctrl+S)")
        save_button.connect("clicked", self.on_save_clicked)
        self.header.pack_start(save_button)

        # Add a menu button to the header
        menu = Gio.Menu.new()
        menu.append("New Project", "app.new-project")
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu.append("About", "app.about")

        menu_button = Gtk.MenuButton(menu_model=menu)
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text("Application Menu")
        self.header.pack_end(menu_button)

        self.split_view = Adw.NavigationSplitView(vexpand=True)
        self.main_box.append(self.split_view)

        self.content_stack = Adw.ViewStack()
        content_container = Adw.ToolbarView()
        content_container.set_content(self.content_stack)

        self.split_view.set_content(Adw.NavigationPage.new(content_container, "Content"))

        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
        welcome_box.append(Gtk.Label(label="Select an editor from the sidebar.", css_classes=["title-1"]))
        self.content_stack.add_named(welcome_box, "welcome")

        # --- Instantiate editors with project_manager ---
        self.scene_editor = SceneEditor(self.project_manager)
        self.logic_editor = LogicEditor(self.project_manager)
        self.asset_editor = AssetEditor(self.project_manager)
        self.audio_editor = AudioEditor(self.project_manager)

        # --- Sidebar setup ---
        sidebar_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)
        sidebar_content.append(self.sidebar_list)

        sidebar_page = Adw.NavigationPage.new(sidebar_content, "Editors")
        self.split_view.set_sidebar(sidebar_page)
        self.split_view.set_property("collapsed", False)
        # --- Add actual editor widgets to sidebar and stack ---
        self.add_editor("Scenes", "scenes_editor", self.scene_editor)
        self.add_editor("Logic", "logic_editor", self.logic_editor)
        self.add_editor("Assets", "assets_editor", self.asset_editor)

        # Verbs & Items container
        verbs_items_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        verbs_items_stack = Adw.ViewStack()
        verbs_items_switcher = Adw.ViewSwitcher(stack=verbs_items_stack)
        verbs_items_container.append(verbs_items_switcher)
        verbs_items_container.append(verbs_items_stack)

        verbs_items_stack.add_titled(ItemEditor(self.project_manager), "items", "Items")
        verbs_items_stack.add_titled(CharacterEditor(self.project_manager), "characters", "Characters")
        verbs_items_stack.add_titled(AttributeEditor(self.project_manager), "attributes", "Attributes")

        self.add_editor("Verbs &amp; Items", "verbs_items_editor", verbs_items_container)
        self.add_editor("Audio", "audio_editor", self.audio_editor)

        # Set initial state
        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())

        self.setup_logic_editor_actions()


    def setup_logic_editor_actions(self):
        add_dialogue_action = Gio.SimpleAction.new("add-dialogue-node", None)
        add_dialogue_action.connect("activate", lambda a, p: self.logic_editor.on_add_dialogue_node(None))
        self.add_action(add_dialogue_action)

        add_condition_action = Gio.SimpleAction.new("add-condition-node", None)
        add_condition_action.connect("activate", lambda a, p: self.logic_editor.on_add_condition_node(None))
        self.add_action(add_condition_action)

        add_action_action = Gio.SimpleAction.new("add-action-node", None)
        add_action_action.connect("activate", lambda a, p: self.logic_editor.on_add_action_node(None))
        self.add_action(add_action_action)

        edit_node_action = Gio.SimpleAction.new("edit-node", None)
        edit_node_action.connect("activate", lambda a, p: self.logic_editor.edit_node_dialog(self.logic_editor.selected_nodes[0]))
        self.add_action(edit_node_action)

        delete_node_action = Gio.SimpleAction.new("delete-node", None)
        delete_node_action.connect("activate", lambda a, p: self.logic_editor.on_delete_node(None))
        self.add_action(delete_node_action)

    def add_editor(self, name, view_name, widget):
        action_row = Adw.ActionRow(title=name)
        list_box_row = Gtk.ListBoxRow()
        list_box_row.set_child(action_row)
        list_box_row.set_name(view_name)
        self.sidebar_list.append(list_box_row)
        self.content_stack.add_named(widget, view_name)

    def on_sidebar_activated(self, listbox, row):
        if row:
            view_name = row.get_name()
            self.content_stack.set_visible_child_name(view_name)

    def on_dirty_state_changed(self, is_dirty):
        """Updates the window title to reflect the unsaved changes status."""
        if is_dirty:
            self.set_title(f"{self.base_title}*")
        else:
            self.set_title(self.base_title)

    def on_save_clicked(self, button):
        """Handler for the save button click."""
        self.get_application().save_project()



class AdvEngine(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = None
        self.win = None
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # This is called when the application is first launched
        self.load_project("TestGame")

        save_action = Gio.SimpleAction.new("save-project", None)
        save_action.connect("activate", lambda a, p: self.save_project())
        self.add_action(save_action)
        self.set_accels_for_action("app.save-project", ["<Primary>s"])

        new_project_action = Gio.SimpleAction.new("new-project", None)
        new_project_action.connect("activate", self.on_new_project_activate)
        self.add_action(new_project_action)

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_activate)
        self.add_action(preferences_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.on_shortcuts_activate)
        self.add_action(shortcuts_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.add_action(about_action)

    def save_project(self):
        """Saves the current project if it's dirty."""
        if self.project_manager and self.project_manager.is_dirty:
            self.project_manager.save_project()

    def load_project(self, project_path):
        """Loads a project and shows its window."""
        self.project_manager = ProjectManager(project_path)
        self.project_manager.load_project()

        # Create a new window for the project
        new_win = AdvEngineWindow(application=self, project_manager=self.project_manager)
        new_win.present()

        # If there was an old window, close it.
        if self.win:
            self.win.close()

        self.win = new_win

    def on_new_project_activate(self, action, param):
        dialog = Gtk.FileChooserDialog(
            title="Create a New Project",
            parent=self.win,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Ok", Gtk.ResponseType.OK)

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                folder = dialog.get_file().get_path()
                success, error = ProjectManager.create_project(folder)
                if success:
                    self.load_project(folder)
                else:
                    # You might want to show an error dialog here
                    print(f"Error creating project: {error}")
            dialog.destroy()

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def on_preferences_activate(self, action, param):
        dialog = PreferencesDialog(parent=self.win)
        dialog.present()

    def on_shortcuts_activate(self, action, param):
        dialog = ShortcutsDialog(parent=self.win)
        dialog.present()

    def on_about_activate(self, action, param):
        dialog = Adw.AboutWindow(
            transient_for=self.win,
            application_name="AdvEngine",
            developer_name="Your Name",
            version="0.1.0",
            comments="A modern adventure game editor.",
            website="https://example.com",
        )
        dialog.present()

def main():
    app = AdvEngine(application_id="com.example.advengine")
    app.run(sys.argv)

if __name__ == "__main__":
    main()
