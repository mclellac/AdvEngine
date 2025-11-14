"""The shortcuts window for the AdvEngine application."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk


class ShortcutsDialog(Gtk.ShortcutsWindow):
    """A window that displays the application's keyboard shortcuts.

    This window is organized into sections and groups to make it easy for
    users to find the shortcuts they are looking for.
    """

    __gtype_name__ = "ShortcutsDialog"

    def __init__(self, transient_for=None, **kwargs):
        """Initializes a new ShortcutsDialog instance."""
        super().__init__(transient_for=transient_for, **kwargs)
        self.set_title("Keyboard Shortcuts")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(box)

        main_section = self._create_main_section()
        box.append(main_section)

        editor_section = self._create_editor_section()
        box.append(editor_section)

    def _create_main_section(self):
        """Adds the main section for general and navigation shortcuts."""
        main_section = Gtk.ShortcutsSection(title="General")

        general_group = Gtk.ShortcutsGroup(title="Application")
        main_section.append(general_group)
        self._add_shortcut(general_group, "<Primary>S", "Save Project")
        self._add_shortcut(general_group, "<Primary>P", "Launch Game")
        self._add_shortcut(general_group, "<Primary>N", "New Project")
        self._add_shortcut(general_group, "<Primary>comma", "Preferences")

        nav_group = Gtk.ShortcutsGroup(title="Navigation")
        main_section.append(nav_group)
        self._add_shortcut(nav_group, "<Primary>1", "Go to Scenes")
        self._add_shortcut(nav_group, "<Primary>2", "Go to Logic")
        self._add_shortcut(nav_group, "<Primary>3", "Go to Interactions")
        self._add_shortcut(nav_group, "<Primary>4", "Go to Dialogue")
        self._add_shortcut(nav_group, "<Primary>6", "Go to Assets")
        self._add_shortcut(nav_group, "<Primary>7", "Go to Global State")
        self._add_shortcut(nav_group, "<Primary>8", "Go to Characters")
        self._add_shortcut(nav_group, "<Primary>9", "Go to Quests")
        self._add_shortcut(nav_group, "<Primary>0", "Go to Database (Items, etc.)")
        return main_section

    def _create_editor_section(self):
        """Adds the section for editor-specific shortcuts."""
        editor_section = Gtk.ShortcutsSection(title="Editors")

        logic_group = Gtk.ShortcutsGroup(title="Logic Editor")
        editor_section.append(logic_group)
        self._add_shortcut(logic_group, "Delete", "Delete Selected Node(s)")
        return editor_section

    def _add_shortcut(self, group, accelerator, title):
        """Adds a new shortcut to a group.

        Args:
            group: The Gtk.ShortcutsGroup to add the shortcut to.
            accelerator: The accelerator for the shortcut.
            title: The title of the shortcut.
        """
        group.append(Gtk.ShortcutsShortcut(accelerator=accelerator, title=title))
