import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class AdvEngineWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("AdvEngine")
        self.set_default_size(800, 600)

        self.label = Gtk.Label(label="Welcome to AdvEngine!")
        self.set_child(self.label)


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
