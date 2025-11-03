import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject
from ..core.data_schemas import SceneGObject, Scene

class SceneEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.selected_scene = None
        self.hotspot_mode = False

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.append(left_panel)

        self.scene_list_box = Gtk.ListBox()
        self.scene_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.scene_list_box.connect("row-activated", self.on_scene_selected)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.scene_list_box)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_size_request(200, -1)
        left_panel.append(scrolled_window)

        self.model = Gio.ListStore(item_type=SceneGObject)
        self.refresh_scene_list()
        self.scene_list_box.bind_model(self.model, self.create_scene_row)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        add_button = Gtk.Button(label="Add")
        add_button.connect("clicked", self.on_add_scene)
        remove_button = Gtk.Button(label="Remove")
        remove_button.connect("clicked", self.on_remove_scene)
        button_box.append(add_button)
        button_box.append(remove_button)
        left_panel.append(button_box)

        hotspot_toggle = Gtk.ToggleButton(label="Add Hotspot")
        hotspot_toggle.connect("toggled", self.on_hotspot_toggled)
        left_panel.append(hotspot_toggle)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.on_canvas_click)
        self.canvas.add_controller(click_gesture)

        self.append(self.canvas)

    def refresh_scene_list(self):
        self.model.remove_all()
        for scene in self.project_manager.data.scenes:
            self.model.append(SceneGObject(scene))

    def create_scene_row(self, scene_gobject):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=scene_gobject.name, halign=Gtk.Align.START, margin_start=10)
        row.set_child(label)
        return row

    def on_scene_selected(self, listbox, row):
        if row:
            scene_gobject = self.model.get_item(row.get_index())
            self.selected_scene = scene_gobject.scene_data
        else:
            self.selected_scene = None
        self.canvas.queue_draw()

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.set_line_width(1)
        grid_size = 50
        for i in range(0, int(width), grid_size):
            cr.move_to(i, 0)
            cr.line_to(i, height)
            cr.stroke()
        for i in range(0, int(height), grid_size):
            cr.move_to(0, i)
            cr.line_to(width, i)
            cr.stroke()

        if self.selected_scene:
            cr.set_source_rgb(0.5, 0.5, 1.0, 0.5) # Semi-transparent blue
            for hotspot in self.selected_scene.hotspots:
                cr.rectangle(hotspot.x, hotspot.y, hotspot.width, hotspot.height)
                cr.fill()

            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.select_font_face("Sans", "normal", "bold")
            cr.set_font_size(24)
            text = f"Editing: {self.selected_scene.name}"
            cr.move_to(10, 30)
            cr.show_text(text)

    def on_hotspot_toggled(self, button):
        self.hotspot_mode = button.get_active()

    def on_canvas_click(self, gesture, n_press, x, y):
        if self.hotspot_mode and self.selected_scene:
            self.project_manager.add_hotspot_to_scene(self.selected_scene.id, "New Hotspot", int(x), int(y), 50, 50)
            self.canvas.queue_draw()

    def on_add_scene(self, button):
        dialog = Gtk.Dialog(title="Create New Scene", transient_for=self.get_native(), modal=True)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        content_area = dialog.get_content_area()
        entry = Gtk.Entry(placeholder_text="Enter scene name...")
        content_area.append(entry)
        dialog.show()

        def response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                scene_name = entry.get_text()
                if scene_name:
                    self.project_manager.create_scene(scene_name)
                    self.refresh_scene_list()
            dialog.destroy()
        dialog.connect("response", response)

    def on_remove_scene(self, button):
        selected_row = self.scene_list_box.get_selected_row()
        if selected_row:
            scene_gobject = self.model.get_item(selected_row.get_index())
            self.project_manager.delete_scene(scene_gobject.scene_data.id)
            self.refresh_scene_list()
            self.on_scene_selected(self.scene_list_box, None)
