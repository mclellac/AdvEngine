import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from .item_editor import ItemEditor
from .character_editor import CharacterEditor
from .attribute_editor import AttributeEditor
from .data_loader import load_items_from_csv

class AdvEngineWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("AdvEngine")
        self.set_default_size(1024, 768)

        # --- Data Loading ---
        self.project_path = "TestGame"
        self.items = load_items_from_csv(self.project_path)

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
        self.character_editor = CharacterEditor()
        self.attribute_editor = AttributeEditor()
        self.content_stack.add_named(self.item_editor, "items")
        self.content_stack.add_named(self.character_editor, "characters")
        self.content_stack.add_named(self.attribute_editor, "attributes")


        self.split_view.set_content(Adw.NavigationPage.new(content_container, "Content"))

        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)

        self.sidebar_list.append(self.create_nav_row("Project", "welcome"))
        self.sidebar_list.append(self.create_nav_row("Items", "items"))
        self.sidebar_list.append(self.create_nav_row("Characters", "characters"))
        self.sidebar_list.append(self.create_nav_row("Attributes", "attributes"))

        self.split_view.set_sidebar(Adw.NavigationPage.new(self.sidebar_list, "Navigation"))
        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())


    def create_nav_row(self, label, view_name):
        row = Gtk.ListBoxRow()
        row.set_child(Gtk.Label(label=label))
        row.view_name = view_name
        return row

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
