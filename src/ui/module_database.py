import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from .item_editor import ItemEditor
from .attribute_editor import AttributeEditor
from .verb_editor import VerbEditor

class DatabaseEditor(Gtk.Box):
    EDITOR_NAME = "Database"
    VIEW_NAME = "db_editor"
    ORDER = 13

    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        db_stack = Adw.ViewStack()
        db_switcher = Adw.ViewSwitcher(stack=db_stack)

        self.append(db_switcher)
        self.append(db_stack)

        db_stack.add_titled_with_icon(ItemEditor(project_manager), "items", "Items", "edit-find-replace-symbolic")
        db_stack.add_titled_with_icon(AttributeEditor(project_manager), "attributes", "Attributes", "document-properties-symbolic")
        db_stack.add_titled_with_icon(VerbEditor(project_manager), "verbs", "Verbs", "input-gaming-symbolic")
