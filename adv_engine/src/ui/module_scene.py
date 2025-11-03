import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject
from ..core.data_schemas import SceneGObject, Scene

class SceneEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.selected_scene = None
        self.selected_hotspot = None
        self.hotspot_mode = False
        self.show_grid = True
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

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
        add_button.set_tooltip_text("Create a new scene")
        add_button.connect("clicked", self.on_add_scene)
        remove_button = Gtk.Button(label="Remove")
        remove_button.set_tooltip_text("Delete the selected scene")
        remove_button.connect("clicked", self.on_remove_scene)
        button_box.append(add_button)
        button_box.append(remove_button)
        left_panel.append(button_box)

        hotspot_toggle = Gtk.ToggleButton(label="Add Hotspot")
        hotspot_toggle.set_tooltip_text("Enable/disable hotspot creation mode")
        hotspot_toggle.connect("toggled", self.on_hotspot_toggled)
        left_panel.append(hotspot_toggle)

        grid_toggle = Gtk.CheckButton(label="Show Grid")
        grid_toggle.set_active(self.show_grid)
        grid_toggle.set_tooltip_text("Toggle grid visibility")
        grid_toggle.connect("toggled", self.on_grid_toggled)
        left_panel.append(grid_toggle)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.on_canvas_click)
        self.canvas.add_controller(click_gesture)

        scroll_controller = Gtk.EventControllerScroll.new(flags=Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self.on_scroll)
        self.canvas.add_controller(scroll_controller)

        pan_gesture = Gtk.GestureDrag.new()
        pan_gesture.set_button(Gdk.BUTTON_MIDDLE)
        pan_gesture.connect("drag-begin", self.on_pan_begin)
        pan_gesture.connect("drag-update", self.on_pan_update)
        self.canvas.add_controller(pan_gesture)

        self.append(self.canvas)

        # --- Properties Panel ---
        self.props_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.props_panel.set_size_request(200, -1)
        self.props_panel.set_visible(False)
        self.append(self.props_panel)

        self.props_panel.append(Gtk.Label(label="Hotspot Properties", css_classes=["title-3"]))

        self.prop_x = self.create_spin_button("X:")
        self.prop_y = self.create_spin_button("Y:")
        self.prop_width = self.create_spin_button("Width:")
        self.prop_height = self.create_spin_button("Height:")

    def create_spin_button(self, label):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.append(Gtk.Label(label=label))
        adj = Gtk.Adjustment(lower=0, upper=2000, step_increment=1, page_increment=10)
        spin_button = Gtk.SpinButton(adjustment=adj)
        spin_button.connect("value-changed", self.on_prop_changed)
        box.append(spin_button)
        self.props_panel.append(box)
        return spin_button

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
        self.selected_hotspot = None
        self.props_panel.set_visible(False)
        self.canvas.queue_draw()

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        cr.save()
        cr.translate(self.pan_x, self.pan_y)
        cr.scale(self.zoom_level, self.zoom_level)

        if self.show_grid:
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.set_line_width(1 / self.zoom_level)
            grid_size = 50
            # TODO: Only draw grid for the visible area
            for i in range(-10, 40):
                cr.move_to(i * grid_size, -10 * grid_size)
                cr.line_to(i * grid_size, 40 * grid_size)
                cr.stroke()
            for i in range(-10, 40):
                cr.move_to(-10 * grid_size, i * grid_size)
                cr.line_to(40 * grid_size, i * grid_size)
                cr.stroke()

        if self.selected_scene:
            # Draw all hotspots
            for hotspot in self.selected_scene.hotspots:
                if hotspot == self.selected_hotspot:
                    cr.set_source_rgba(1.0, 1.0, 0.0, 0.6)  # Yellow for selected
                else:
                    cr.set_source_rgba(0.5, 0.5, 1.0, 0.5)  # Blue for others
                cr.rectangle(hotspot.x, hotspot.y, hotspot.width, hotspot.height)
                cr.fill()

        cr.restore()

        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(14)
        text = f"Zoom: {self.zoom_level:.2f}"
        cr.move_to(10, 20)
        cr.show_text(text)

    def on_grid_toggled(self, button):
        self.show_grid = button.get_active()
        self.canvas.queue_draw()

    def on_hotspot_toggled(self, button):
        self.hotspot_mode = button.get_active()

    def on_canvas_click(self, gesture, n_press, x, y):
        world_x = (x - self.pan_x) / self.zoom_level
        world_y = (y - self.pan_y) / self.zoom_level

        if self.hotspot_mode and self.selected_scene:
            grid_size = 50
            hotspot_width = 50
            hotspot_height = 50

            # Snap to grid and center on cursor
            snapped_x = round((world_x - hotspot_width / 2) / grid_size) * grid_size
            snapped_y = round((world_y - hotspot_height / 2) / grid_size) * grid_size

            self.project_manager.add_hotspot_to_scene(self.selected_scene.id, "New Hotspot", int(snapped_x), int(snapped_y), hotspot_width, hotspot_height)
            self.canvas.queue_draw()
        elif self.selected_scene:
            # Check if a hotspot was clicked
            for hotspot in reversed(self.selected_scene.hotspots):
                if world_x >= hotspot.x and world_x <= hotspot.x + hotspot.width and world_y >= hotspot.y and world_y <= hotspot.y + hotspot.height:
                    self.selected_hotspot = hotspot
                    self.update_props_panel()
                    self.canvas.queue_draw()
                    return

            # If no hotspot was clicked, deselect
            self.selected_hotspot = None
            self.props_panel.set_visible(False)
            self.canvas.queue_draw()

    def on_scroll(self, controller, dx, dy):
        if controller.get_current_event_state() & Gdk.ModifierType.CONTROL_MASK:
            # Zoom
            self.zoom_level *= 1.1 if dy < 0 else 1 / 1.1
            self.zoom_level = max(0.1, min(self.zoom_level, 5.0)) # Clamp zoom
            self.canvas.queue_draw()
            return True
        return False

    def on_pan_begin(self, gesture, x, y):
        self.pan_start_x = self.pan_x
        self.pan_start_y = self.pan_y
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def on_pan_update(self, gesture, x, y):
        self.pan_x = self.pan_start_x + x
        self.pan_y = self.pan_start_y + y
        self.canvas.queue_draw()

    def update_props_panel(self):
        if self.selected_hotspot:
            self.prop_x.set_value(self.selected_hotspot.x)
            self.prop_y.set_value(self.selected_hotspot.y)
            self.prop_width.set_value(self.selected_hotspot.width)
            self.prop_height.set_value(self.selected_hotspot.height)
            self.props_panel.set_visible(True)
        else:
            self.props_panel.set_visible(False)

    def on_prop_changed(self, spin_button):
        if self.selected_hotspot:
            self.selected_hotspot.x = self.prop_x.get_value()
            self.selected_hotspot.y = self.prop_y.get_value()
            self.selected_hotspot.width = self.prop_width.get_value()
            self.selected_hotspot.height = self.prop_height.get_value()
            self.project_manager.set_dirty()
            self.canvas.queue_draw()

    def on_add_scene(self, button):
        dialog = Gtk.Dialog(title="Create New Scene", transient_for=self.get_native(), modal=True)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Ok", Gtk.ResponseType.OK)
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
