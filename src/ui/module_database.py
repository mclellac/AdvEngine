"""The database editor for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from .item_editor import ItemEditor
from .attribute_editor import AttributeEditor
from .verb_editor import VerbEditor


class DatabaseEditor(Adw.Bin):
    """A container for the various database-style editors.

    This widget uses an Adw.ViewStack to manage the different editors,
    with an Adw.ViewSwitcher in the header bar to navigate between them.
    """
    EDITOR_NAME = "Database"
    VIEW_NAME = "db_editor"
    ORDER = 13

    def __init__(self, project_manager, **kwargs):
        """Initializes a new DatabaseEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        super().__init__(**kwargs)

        self.view_stack = Adw.ViewStack()
        view_switcher = Adw.ViewSwitcher(stack=self.view_stack)

        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(view_switcher)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(header_bar)
        main_box.append(self.view_stack)

        self.set_child(main_box)

        self.view_stack.add_titled_with_icon(
            ItemEditor(project_manager), "items", "Items", "edit-find-replace-symbolic")
        self.view_stack.add_titled_with_icon(
            AttributeEditor(project_manager), "attributes", "Attributes", "document-properties-symbolic")
        self.view_stack.add_titled_with_icon(
            VerbEditor(project_manager), "verbs", "Verbs", "input-gaming-symbolic")
