import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from .item_editor import ItemEditor
from .character_editor import CharacterEditor
from .attribute_editor import AttributeEditor
from .data_loader import load_items_from_csv, load_characters_from_csv, load_attributes_from_csv

class AdvEngineWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("AdvEngine")
        self.set_default_size(1024, 768)

        # --- Data Loading ---
        self.project_path = "TestGame"
        self.items = load_items_from_csv(self.project_path)
        self.characters = load_characters_from_csv(self.project_path)
        self.attributes = load_attributes_from_csv(self.project_path)

        # --- UI Setup ---
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

        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
        welcome_box.append(Gtk.Label(label="Select an editor from the sidebar.", css_classes=["title-1"]))
        self.content_stack.add_named(welcome_box, "welcome")

        # --- Editors ---
        self.item_editor = ItemEditor(self.items)
        self.character_editor = CharacterEditor(self.characters)
        self.attribute_editor = AttributeEditor(self.attributes)


        self.split_view.set_content(Adw.NavigationPage.new(content_container, "Content"))

        # --- Sidebar ---
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)
        self.split_view.set_sidebar(Adw.NavigationPage.new(self.sidebar_list, "Editors"))

        # --- Add editors to sidebar and stack ---
        self.add_editor("Scenes", "scenes_editor", Gtk.Label(label="This is the Scenes editor."))
        self.add_editor("Logic", "logic_editor", Gtk.Label(label="This is the Logic editor."))
        self.add_editor("Assets", "assets_editor", Gtk.Label(label="This is the Assets editor."))

        # Create a container for the Verbs & Items editors
        verbs_items_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        verbs_items_stack = Adw.ViewStack()
        verbs_items_switcher = Adw.ViewSwitcher(stack=verbs_items_stack)
        verbs_items_container.append(verbs_items_switcher)
        verbs_items_container.append(verbs_items_stack)

        verbs_items_stack.add_titled(self.item_editor, "items", "Items")
        verbs_items_stack.add_titled(self.character_editor, "characters", "Characters")
        verbs_items_stack.add_titled(self.attribute_editor, "attributes", "Attributes")

        self.add_editor("Verbs & Items", "verbs_items_editor", verbs_items_container)
        self.add_editor("Audio", "audio_editor", Gtk.Label(label="This is the Audio editor."))

        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())


    def add_editor(self, name, view_name, widget):
        row = Gtk.ListBoxRow()
        row.set_child(Gtk.Label(label=name))
        row.view_name = view_name
        self.sidebar_list.append(row)
        self.content_stack.add_named(widget, view_name)

    def on_sidebar_activated(self, listbox, row):
        if row:
            self.content_stack.set_visible_child_name(row.view_name)


class AdvEngine(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = AdvEngineWindow(application=app)
        self.win.present()


if __name__ == "__main__":
    app = AdvEngine(application_id="com.example.advengine")
    app.run(sys.argv)
