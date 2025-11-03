import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class AssetEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        label = Gtk.Label(label="Asset Editor (Placeholder)")
        self.append(label)
