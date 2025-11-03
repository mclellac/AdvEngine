import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class ShortcutsDialog(Adw.ShortcutsWindow):
    """
    A dialog for displaying keyboard shortcuts.
    """
    __gtype_name__ = "ShortcutsDialog"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(kwargs.get("parent"))
        self.set_modal(True)

        # General Section
        section = Adw.ShortcutsSection()
        self.add(section)

        # Logic Editor Group
        group = Adw.ShortcutsGroup(title="Logic Editor")
        section.add(group)

        # Delete Node Shortcut
        shortcut = Adw.ShortcutsShortcut(
            title="Delete Node",
            accelerator="Delete"
        )
        group.add(shortcut)
