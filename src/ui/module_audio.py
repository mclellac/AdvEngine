import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gtk, Gio, GObject, Gst
import os
import shutil
from ..core.data_schemas import Audio, AudioGObject
import cairo

class AudioEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        Gst.init(None)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(300, -1)
        self.append(left_panel)

        self.model = Gio.ListStore(item_type=AudioGObject)
        self.refresh_audio_list()

        self.audio_list_view = Gtk.ColumnView()
        selection_model = Gtk.SingleSelection(model=self.model)
        selection_model.connect("selection-changed", self.on_audio_selected)
        self.audio_list_view.set_model(selection_model)
        self._create_column("ID", lambda audio: audio.id)
        self._create_column("Name", lambda audio: audio.name)
        self._create_column("Duration (s)", lambda audio: str(round(audio.duration, 2)))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.audio_list_view)
        scrolled_window.set_vexpand(True)
        left_panel.append(scrolled_window)

        import_button = Gtk.Button(label="Import Audio")
        import_button.connect("clicked", self.on_import_audio)
        left_panel.append(import_button)

        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        self.append(right_panel)

        self.media_stream = None
        self.media_controls = Gtk.MediaControls()
        right_panel.append(self.media_controls)

        self.waveform_drawing_area = Gtk.DrawingArea()
        self.waveform_drawing_area.set_draw_func(self.on_waveform_draw, None)
        self.waveform_drawing_area.set_size_request(-1, 100)
        right_panel.append(self.waveform_drawing_area)
        self.waveform_data = []

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.audio_list_view.append_column(col)

    def on_audio_selected(self, selection_model, position, n_items):
        selected_audio_gobject = selection_model.get_selected_item()
        if selected_audio_gobject:
            audio = selected_audio_gobject.audio_data
            if os.path.exists(audio.file_path):
                self.media_stream = Gtk.MediaFile.new_for_filename(audio.file_path)
                self.media_controls.set_media_stream(self.media_stream)
                self.generate_waveform_data(audio.file_path)
            else:
                self.media_controls.set_media_stream(None)
                self.waveform_data = []
        else:
            self.media_controls.set_media_stream(None)
            self.waveform_data = []
        self.waveform_drawing_area.queue_draw()

    def refresh_audio_list(self):
        self.model.remove_all()
        for audio in self.project_manager.data.audio_files:
            self.model.append(AudioGObject(audio))

    def on_import_audio(self, button):
        dialog = Gtk.FileChooserNative(title="Import Audio", transient_for=self.get_native(), action=Gtk.FileChooserAction.OPEN)
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Audio Files")
        file_filter.add_mime_type("audio/*")
        dialog.add_filter(file_filter)
        dialog.connect("response", self.on_import_audio_response)
        dialog.show()

    def on_import_audio_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            try:
                file = dialog.get_file()
                filepath = file.get_path()
                audio_name = os.path.basename(filepath)

                audio_dir = os.path.join(self.project_manager.project_path, "Audio")
                os.makedirs(audio_dir, exist_ok=True)
                new_filepath = os.path.join(audio_dir, audio_name)
                shutil.copy(filepath, new_filepath)

                duration = 0.0
                discoverer = Gst.Discoverer.new(5 * Gst.SECOND)
                info = discoverer.discover_uri(f"file://{new_filepath}")
                if info:
                    duration = info.get_duration() / Gst.SECOND

                new_audio = Audio(id=f"audio_{len(self.project_manager.data.audio_files)}", name=audio_name, asset_type="sound", file_path=new_filepath, duration=duration)
                self.project_manager.data.audio_files.append(new_audio)
                self.project_manager.set_dirty()
                self.refresh_audio_list()
            except Exception as e:
                print(f"Error importing audio: {e}")

    def generate_waveform_data(self, file_path):
        import random
        self.waveform_data = [random.uniform(-1.0, 1.0) for _ in range(200)]

    def on_waveform_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.paint()

        if not self.waveform_data:
            return

        cr.set_source_rgb(0.4, 0.6, 0.8)
        cr.set_line_width(2)

        center_y = height / 2
        step_x = width / len(self.waveform_data)

        for i, sample in enumerate(self.waveform_data):
            x = i * step_x
            y = center_y + (sample * center_y)
            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()
