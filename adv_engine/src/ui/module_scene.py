import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Gdk, Adw, GdkPixbuf
from ..core.data_schemas import SceneGObject, Scene, Hotspot, HotspotGObject

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

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=True, vexpand=True)
        self.append(self.main_box)

        # --- Left Panel ---
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(200, -1)
        self.main_box.append(left_panel)

        # Scene List
        left_panel.append(Gtk.Label(label="Scenes", css_classes=["title-3"]))
        self.scene_list_box = Gtk.ListBox()
        self.scene_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.scene_list_box.connect("row-activated", self.on_scene_selected)

        scrolled_scenes = Gtk.ScrolledWindow()
        scrolled_scenes.set_child(self.scene_list_box)
        scrolled_scenes.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_scenes.set_vexpand(True)
        left_panel.append(scrolled_scenes)

        self.model = Gio.ListStore(item_type=SceneGObject)

        self.scene_list_box.bind_model(self.model, self.create_scene_row)

        scene_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.add_scene_button = Gtk.Button(label="Add")
        self.add_scene_button.set_tooltip_text("Create a new scene")
        self.add_scene_button.connect("clicked", self.on_add_scene)
        remove_scene_button = Gtk.Button(label="Remove")
        remove_scene_button.set_tooltip_text("Delete the selected scene")
        remove_scene_button.connect("clicked", self.on_remove_scene)
        scene_button_box.append(self.add_scene_button)
        scene_button_box.append(remove_scene_button)
        left_panel.append(scene_button_box)

        left_panel.append(Gtk.Separator())

        self.background_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, visible=False)
        self.background_box.append(Gtk.Label(label="Background", css_classes=["title-4"]))

        self.background_preview = Gtk.Image(width_request=150, height_request=100, icon_name="image-missing-symbolic", css_classes=["card"])
        self.background_box.append(self.background_preview)

        set_background_button = Gtk.Button(label="Set Background...")
        set_background_button.connect("clicked", self.on_set_background_clicked)
        self.background_box.append(set_background_button)
        left_panel.append(self.background_box)

        # Tools
        left_panel.append(Gtk.Separator())
        hotspot_toggle = Gtk.ToggleButton(label="Add Hotspot")
        hotspot_toggle.set_tooltip_text("Enable/disable hotspot creation mode")
        hotspot_toggle.connect("toggled", self.on_hotspot_toggled)
        left_panel.append(hotspot_toggle)

        grid_toggle = Gtk.CheckButton(label="Show Grid")
        grid_toggle.set_active(self.show_grid)
        grid_toggle.set_tooltip_text("Toggle grid visibility")
        grid_toggle.connect("toggled", self.on_grid_toggled)
        left_panel.append(grid_toggle)

        # --- Canvas ---
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

        self.main_box.append(self.canvas)

        # --- Right Panel ---
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_panel.set_size_request(200, -1)
        self.main_box.append(right_panel)

        # Properties Panel
        self.props_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.props_panel.set_visible(False)
        right_panel.append(self.props_panel)

        group = Adw.PreferencesGroup()
        self.props_panel.append(group)

        self.prop_x = self._create_property_row("X", "X coordinate", 0, 8192)
        self.prop_y = self._create_property_row("Y", "Y coordinate", 0, 8192)
        self.prop_width = self._create_property_row("Width", "Width of the hotspot", 1, 8192)
        self.prop_height = self._create_property_row("Height", "Height of the hotspot", 1, 8192)

        # Layer Management
        right_panel.append(Gtk.Separator())
        right_panel.append(Gtk.Label(label="Layers", css_classes=["title-3"]))

        self.layer_list_box = Gtk.ListBox()
        self.layer_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.layer_list_box.connect("row-activated", self.on_layer_selected)

        scrolled_layers = Gtk.ScrolledWindow()
        scrolled_layers.set_child(self.layer_list_box)
        scrolled_layers.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_layers.set_vexpand(True)
        right_panel.append(scrolled_layers)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(title="No Scenes",
                                          description="Create a new scene to begin.",
                                          icon_name="document-new-symbolic")
        self.add_scene_button_empty = Gtk.Button(label="Create Scene")
        self.add_scene_button_empty.connect("clicked", self.on_add_scene)
        self.empty_state.set_child(self.add_scene_button_empty)
        self.append(self.empty_state)

        self.refresh_scene_list()


    def _create_property_row(self, title, subtitle, lower, upper):
        adj = Gtk.Adjustment(lower=lower, upper=upper, step_increment=1, page_increment=10)
        spin_button = Gtk.SpinButton(adjustment=adj)
        spin_button.connect("value-changed", self.on_prop_changed)
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(spin_button)
        row.set_activatable_widget(spin_button)
        self.props_panel.append(row)
        return spin_button

    def refresh_scene_list(self):
        self.model.remove_all()
        for scene in self.project_manager.data.scenes:
            self.model.append(SceneGObject(scene))
        self.update_visibility()

    def update_visibility(self):
        has_scenes = self.model.get_n_items() > 0
        self.main_box.set_visible(has_scenes)
        self.empty_state.set_visible(not has_scenes)

    def create_scene_row(self, scene_gobject):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=scene_gobject.name, halign=Gtk.Align.START, margin_start=10)
        row.set_child(label)
        return row

    def refresh_layer_list(self):
        # Clear existing rows
        while child := self.layer_list_box.get_first_child():
            self.layer_list_box.remove(child)

        if self.selected_scene:
            for hotspot in self.selected_scene.hotspots:
                row = self._create_layer_row(HotspotGObject(hotspot))
                self.layer_list_box.append(row)

    def _create_layer_row(self, hotspot_gobject):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=hotspot_gobject.name, halign=Gtk.Align.START, margin_start=10)
        row.set_child(label)

        # Add Drag and Drop controllers to the ROW
        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self._on_layer_drag_prepare, hotspot_gobject)
        drag_source.connect("drag-begin", self._on_layer_drag_begin)
        row.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(type=HotspotGObject, actions=Gdk.DragAction.MOVE)
        drop_target.connect("drop", self._on_layer_drop, hotspot_gobject)
        row.add_controller(drop_target)
        return row


    def on_scene_selected(self, listbox, row):
        if row:
            scene_gobject = self.model.get_item(row.get_index())
            self.selected_scene = scene_gobject.scene_data
            self.background_box.set_visible(True)
        else:
            self.selected_scene = None
            self.background_box.set_visible(False)

        self.update_background_preview()
        self.selected_hotspot = None
        self.props_panel.set_visible(False)
        self.refresh_layer_list()
        self.canvas.queue_draw()

    def on_set_background_clicked(self, button):
        if not self.selected_scene:
            return

        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            transient_for=self.get_native(),
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.OK
        )

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Image files")
        file_filter.add_pixbuf_formats()
        dialog.add_filter(file_filter)

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                file_path = dialog.get_file().get_path()
                try:
                    # Make path relative to the project directory
                    relative_path = os.path.relpath(file_path, self.project_manager.project_path)
                    self.selected_scene.background_image = relative_path
                    self.project_manager.set_dirty()
                    self.update_background_preview()
                    self.canvas.queue_draw()
                except ValueError:
                    # This can happen if the file is on a different drive on Windows
                    # In this case, we'll have to store the absolute path. A better solution
                    # would be to copy the asset into the project folder. For now, we'll warn.
                    error_dialog = Adw.MessageDialog(
                        transient_for=self.get_native(),
                        modal=True,
                        heading="Cannot create relative path",
                        body="The selected image is outside of the project directory. The absolute path will be stored, but this may cause issues with project portability."
                    )
                    error_dialog.add_response("ok", "_OK")
                    error_dialog.connect("response", lambda d, r: d.destroy())
                    error_dialog.present()
                    self.selected_scene.background_image = file_path
                    self.project_manager.set_dirty()
                    self.update_background_preview()
                    self.canvas.queue_draw()


            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def update_background_preview(self):
        if self.selected_scene and self.selected_scene.background_image:
            full_path = os.path.join(self.project_manager.project_path, self.selected_scene.background_image)
            if os.path.exists(full_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(full_path, 150, 100, True)
                self.background_preview.set_from_pixbuf(pixbuf)
            else:
                self.background_preview.set_from_icon_name("image-missing-symbolic")
        else:
            self.background_preview.set_from_icon_name("image-missing-symbolic")

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        if self.selected_scene and self.selected_scene.background_image:
            full_path = os.path.join(self.project_manager.project_path, self.selected_scene.background_image)
            if os.path.exists(full_path):
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(full_path)
                    Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
                    cr.paint()
                except Exception as e:
                    print(f"Error loading background image: {e}")

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
            # Draw all hotspots in order
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
            self.refresh_layer_list()
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
            self.selected_hotspot.x = int(self.prop_x.get_value())
            self.selected_hotspot.y = int(self.prop_y.get_value())
            self.selected_hotspot.width = int(self.prop_width.get_value())
            self.selected_hotspot.height = int(self.prop_height.get_value())
            self.project_manager.set_dirty()
            self.canvas.queue_draw()

    def on_add_scene(self, button):
        dialog = Adw.MessageDialog(transient_for=self.get_native(), modal=True,
                                   heading="Create New Scene")

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        entry = Gtk.Entry(placeholder_text="Enter scene name...")
        content.append(entry)
        dialog.set_extra_child(content)

        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("ok", "_OK")
        dialog.set_default_response("ok")

        def response(dialog, response_id):
            if response_id == "ok":
                scene_name = entry.get_text()
                if scene_name:
                    self.project_manager.create_scene(scene_name)
                    self.refresh_scene_list()
            dialog.destroy()
        dialog.connect("response", response)
        dialog.present()


    def on_remove_scene(self, button):
        selected_row = self.scene_list_box.get_selected_row()
        if selected_row:
            scene_gobject = self.model.get_item(selected_row.get_index())

            dialog = Adw.MessageDialog(
                transient_for=self.get_native(),
                modal=True,
                heading="Delete Scene?",
                body=f"Are you sure you want to delete '{scene_gobject.name}'? This action cannot be undone."
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

            def on_response(dialog, response_id):
                if response_id == "delete":
                    self.project_manager.delete_scene(scene_gobject.scene_data.id)
                    self.refresh_scene_list()
                    self.on_scene_selected(self.scene_list_box, None)
                dialog.destroy()

            dialog.connect("response", on_response)
            dialog.present()

    def on_layer_selected(self, listbox, row):
        if row:
            self.selected_hotspot = row.get_child().get_data("hotspot_obj").hotspot_data
        else:
            self.selected_hotspot = None
        self.update_props_panel()
        self.canvas.queue_draw()

    def _on_layer_drag_prepare(self, source, x, y, hotspot_gobject):
        return Gdk.ContentProvider.new_for_value(hotspot_gobject)

    def _on_layer_drag_begin(self, source, drag):
        list_row = source.get_widget()
        source.set_icon(Gtk.WidgetPaintable.new(list_row), 0, 0)

    def _on_layer_drop(self, target, value, x, y, target_hotspot_gobject):
        dragged_hotspot_gobject = value

        if dragged_hotspot_gobject and target_hotspot_gobject and dragged_hotspot_gobject != target_hotspot_gobject:
            # Reorder the list in the project data
            dragged_index = self.selected_scene.hotspots.index(dragged_hotspot_gobject.hotspot_data)
            target_index = self.selected_scene.hotspots.index(target_hotspot_gobject.hotspot_data)

            self.selected_scene.hotspots.pop(dragged_index)
            self.selected_scene.hotspots.insert(target_index, dragged_hotspot_gobject.hotspot_data)

            self.project_manager.set_dirty()
            self.refresh_layer_list()
            self.canvas.queue_draw()
            return True
        return False
