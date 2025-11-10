"""The database editor for the AdvEngine application.

This module defines the DatabaseEditor, a container widget that uses a
ViewStack to manage several individual database-style editors, such as the
ItemEditor, AttributeEditor, and VerbEditor.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from .item_editor import ItemEditor
from .attribute_editor import AttributeEditor
from .verb_editor import VerbEditor


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_database.ui"))
class DatabaseEditor(Gtk.Box):
    """A container for the various database-style editors.

    This widget acts as a central hub for managing core game data like items,
    attributes, and verbs, presenting each in a separate tab.
    """

    __gtype_name__ = "DatabaseEditor"

    EDITOR_NAME = "Database"
    VIEW_NAME = "db_editor"
    ORDER = 13

    view_stack: Gtk.Stack = Gtk.Template.Child()
    view_switcher: Adw.ViewSwitcher = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new DatabaseEditor instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        project_manager = kwargs.pop("project_manager")
        settings_manager = kwargs.pop("settings_manager")
        super().__init__(**kwargs)

        self.view_switcher.set_stack(self.view_stack)

        self.view_stack.add_titled_with_icon(
            ItemEditor(
                project_manager=project_manager, settings_manager=settings_manager
            ),
            "items",
            "Items",
            "edit-find-replace-symbolic",
        )
        self.view_stack.add_titled_with_icon(
            AttributeEditor(
                project_manager=project_manager, settings_manager=settings_manager
            ),
            "attributes",
            "Attributes",
            "document-properties-symbolic",
        )
        self.view_stack.add_titled_with_icon(
            VerbEditor(
                project_manager=project_manager, settings_manager=settings_manager
            ),
            "verbs",
            "Verbs",
            "input-gaming-symbolic",
        )
