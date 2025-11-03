import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject
import os
import shutil
from ..core.data_schemas import Audio

class AudioGObject(GObject.Object):
    __gtype_name__ = 'AudioGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    file_path = GObject.Property(type=str)
    duration = GObject.Property(type=float)

    def __init__(self, audio):
        super().__init__()
        self.id = audio.id
        self.name = audio.name
        self.file_path = audio.file_path
        self.duration = audio.duration
        self.audio_data = audio

class AudioEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.model = Gio.ListStore(item_type=AudioGObject)
        self.refresh_audio_list()

        self.audio_list_view = Gtk.ColumnView()
        self.audio_list_view.set_model(Gtk.SingleSelection(model=self.model))
        self._create_column("ID", lambda audio: audio.id)
        self._create_column("Name", lambda audio: audio.name)
        self._create_column("Duration (s)", lambda audio: str(audio.duration))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.audio_list_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        self.append(scrolled_window)

        import_button = Gtk.Button(label="Import Audio")
        import_button.set_tooltip_text("Import a new audio file into the project")
        import_button.connect("clicked", self.on_import_audio)
        self.append(import_button)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.audio_list_view.append_column(col)

    def refresh_audio_list(self):
        self.model.remove_all()
        for audio in self.project_manager.data.audio_files:
            self.model.append(AudioGObject(audio))

    def on_import_audio(self, button):
        dialog = Gtk.FileChooserDialog(title="Import Audio", transient_for=self.get_native(), action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.OK)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Audio Files")
        file_filter.add_mime_type("audio/*")
        dialog.add_filter(file_filter)

        dialog.show()

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                file = dialog.get_file()
                filepath = file.get_path()
                audio_name = os.path.basename(filepath)

                audio_dir = os.path.join(self.project_manager.project_path, "Audio")
                os.makedirs(audio_dir, exist_ok=True)
                new_filepath = os.path.join(audio_dir, audio_name)
                shutil.copy(filepath, new_filepath)

                new_audio = Audio(id=f"audio_{len(self.project_manager.data.audio_files)}", name=audio_name, asset_type="sound", file_path=new_filepath, duration=0.0)
                self.project_manager.data.audio_files.append(new_audio)
                self.project_manager.set_dirty()
                self.refresh_audio_list()
            dialog.destroy()

        dialog.connect("response", on_response)
