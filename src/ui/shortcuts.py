import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk

class ShortcutsDialog(Gtk.ShortcutsWindow):
    """A window that displays the application's keyboard shortcuts."""
    __gtype_name__ = "ShortcutsDialog"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_modal(True)
        self.set_title("Keyboard Shortcuts")

        # Main Section for General Shortcuts
        main_section = Gtk.ShortcutsSection(title="General")
        self.set_child(main_section)

        # -- General Group --
        general_group = Gtk.ShortcutsGroup(title="Application")
        main_section.append(general_group)

        general_group.append(Gtk.ShortcutsShortcut(
            title="Save Project",
            accelerator="<Primary>S"
        ))
        general_group.append(Gtk.ShortcutsShortcut(
            title="Launch Game",
            accelerator="<Primary>P"
        ))
        general_group.append(Gtk.ShortcutsShortcut(
            title="New Project",
            accelerator="<Primary>N"
        ))
        general_group.append(Gtk.ShortcutsShortcut(
            title="Preferences",
            accelerator="<Primary>,"
        ))

        # -- Navigation Group --
        nav_group = Gtk.ShortcutsGroup(title="Navigation")
        main_section.append(nav_group)

        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Scenes",
            accelerator="<Primary>1"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Logic",
            accelerator="<Primary>2"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Interactions",
            accelerator="<Primary>3"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Dialogue",
            accelerator="<Primary>4"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Cutscenes",
            accelerator="<Primary>5"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Assets",
            accelerator="<Primary>6"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Global State",
            accelerator="<Primary>7"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Characters",
            accelerator="<Primary>8"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Quests",
            accelerator="<Primary>9"
        ))
        nav_group.append(Gtk.ShortcutsShortcut(
            title="Go to Database (Items, etc.)",
            accelerator="<Primary>0"
        ))

        # Editor Section
        editor_section = Gtk.ShortcutsSection(title="Editors")
        main_section.append(editor_section)

        # -- Logic Editor Group --
        logic_group = Gtk.ShortcutsGroup(title="Logic Editor")
        editor_section.append(logic_group)

        logic_group.append(Gtk.ShortcutsShortcut(
            title="Delete Selected Node(s)",
            accelerator="Delete"
        ))
