import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

from .core.project_manager import ProjectManager
from .ui.item_editor import ItemEditor
from .ui.character_editor import CharacterEditor
from .ui.attribute_editor import AttributeEditor
from .ui.module_scene import SceneEditor
from .ui.module_logic import LogicEditor
from .ui.module_assets import AssetEditor
from .ui.module_audio import AudioEditor


class AdvEngineWindow(Gtk.ApplicationWindow):
    def __init__(self, project_manager, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.set_title("AdvEngine")
        self.set_default_size(1024, 768)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.header = Gtk.HeaderBar()
        self.main_box.append(self.header)

        self.split_view = Adw.NavigationSplitView()
        self.split_view.set_vexpand(True)
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
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)
        self.split_view.set_sidebar(Adw.NavigationPage.new(self.sidebar_list, "Editors"))

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

        self.add_editor("Verbs & Items", "verbs_items_editor", verbs_items_container)
        self.add_editor("Audio", "audio_editor", self.audio_editor)

        # Set initial state
        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())


    def add_editor(self, name, view_name, widget):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=name, halign=Gtk.Align.START, margin_start=10)
        row.set_child(label)
        row.view_name = view_name
        self.sidebar_list.append(row)
        self.content_stack.add_named(widget, view_name)

    def on_sidebar_activated(self, listbox, row):
        if row:
            self.content_stack.set_visible_child_name(row.view_name)


class AdvEngine(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = None
        self.win = None
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.project_manager = ProjectManager("TestGame")
        self.project_manager.load_project()

        self.win = AdvEngineWindow(application=app, project_manager=self.project_manager)
        self.win.present()

def main():
    app = AdvEngine(application_id="com.example.advengine")
    app.run(sys.argv)

if __name__ == "__main__":
    main()
