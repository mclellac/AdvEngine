import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class CharacterEditor(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, valign=Gtk.Align.CENTER)

        label = Gtk.Label(label="Character Editor - Coming Soon")
        label.add_css_class("title-1")
        self.append(label)
