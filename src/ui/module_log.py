import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw

class LogViewer(Gtk.Box):
    EDITOR_NAME = "Log"
    VIEW_NAME = "log_viewer"
    ORDER = 12

    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.log_view)
        scrolled_window.set_vexpand(True)
        self.append(scrolled_window)

    def add_log_message(self, message):
        buffer = self.log_view.get_buffer()
        buffer.insert(buffer.get_end_iter(), message + "\n")
