"""The scene editor for the AdvEngine application."""

import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Gdk, Adw, GdkPixbuf
from ..core.data_schemas import SceneGObject, Hotspot, HotspotGObject
from ..core.project_manager import ProjectManager


class SceneEditor(Adw.Bin):
    """A widget for editing scenes.

    This editor provides a canvas for placing and manipulating hotspots, a
    list of scenes in the project, and a properties panel for editing the
    selected hotspot.
    """
    EDITOR_NAME = "Scenes"
    VIEW_NAME = "scenes_editor"
    ORDER = 0

    def __init__(self, project_manager: ProjectManager, **kwargs):
        """Initializes a new SceneEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        print("DEBUG: SceneEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.selected_scene_gobject = None
        self.selected_hotspot = None
        self.hotspot_mode = False
        self.show_grid = True
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        root_widget = self._build_ui()
        self.set_child(root_widget)

        self._update_visibility()
        self.project_manager.register_project_loaded_callback(
            self._on_project_loaded)

    def _on_project_loaded(self, *args):
        """Handles the project-loaded signal from the project manager."""
        print("DEBUG: SceneEditor._on_project_loaded")
        self._update_scene_list()
        self._update_visibility()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        print("DEBUG: SceneEditor._build_ui")
        root_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        scene_list_panel = self._create_scene_list_panel()
        root_box.append(scene_list_panel)

        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_hexpand(True)
        self.split_view.set_content(self._create_canvas_area())

        self.props_panel = self._create_properties_panel()
        self.split_view.set_sidebar(self.props_panel)
        self.split_view.set_sidebar_position(Gtk.PackType.END)

        root_box.append(self.split_view)
        return root_box

    def _create_scene_list_panel(self):
        """Creates the panel with the list of scenes."""
        print("DEBUG: SceneEditor._create_scene_list_panel")
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        panel.set_margin_top(12)
        panel.set_margin_bottom(12)
        panel.set_margin_start(12)
        panel.set_margin_end(12)

        header = Adw.HeaderBar()
        panel.append(header)

        add_button = Gtk.Button(icon_name="list-add-symbolic")
        add_button.connect("clicked", self._on_add_scene)
        header.pack_start(add_button)

        self.delete_scene_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_scene_button.connect("clicked", self._on_remove_scene)
        self.delete_scene_button.set_sensitive(False)
        header.pack_end(self.delete_scene_button)

        self.scene_model = Gio.ListStore(item_type=SceneGObject)
        self.scene_selection = Gtk.SingleSelection(model=self.scene_model)
        self.scene_selection.connect("selection-changed", self._on_scene_selected)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_scene_list_item)
        factory.connect("bind", self._bind_scene_list_item)

        list_view = Gtk.ListView(model=self.scene_selection, factory=factory)

        scrolled = Gtk.ScrolledWindow(child=list_view)
        scrolled.set_vexpand(True)
        panel.append(scrolled)
        return panel

    def _setup_scene_list_item(self, factory, list_item):
        """Sets up a scene list item."""
        label = Gtk.Label(
            halign=Gtk.Align.START, margin_start=10, margin_top=10, margin_bottom=10)
        list_item.set_child(label)

    def _bind_scene_list_item(self, factory, list_item):
        """Binds a scene list item to the data model."""
        label = list_item.get_child()
        scene_gobject = list_item.get_item()
        label.set_text(scene_gobject.name)

    def _create_canvas_area(self):
        """Creates the canvas area."""
        print("DEBUG: SceneEditor._create_canvas_area")
        self.content_stack = Gtk.Stack()

        canvas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar()
        canvas_box.append(header)

        hotspot_toggle = Gtk.ToggleButton(
            icon_name="object-select-symbolic", tooltip_text="Add Hotspot")
        hotspot_toggle.connect(
            "toggled", lambda b: setattr(self, 'hotspot_mode', b.get_active()))
        header.pack_start(hotspot_toggle)

        grid_toggle = Gtk.ToggleButton(
            icon_name="view-grid-symbolic", tooltip_text="Show Grid")
        grid_toggle.set_active(True)
        grid_toggle.connect("toggled", lambda b: setattr(
            self, 'show_grid', b.get_active()) or self.canvas.queue_draw())
        header.pack_start(grid_toggle)

        self.canvas = Gtk.DrawingArea(hexpand=True, vexpand=True)
        self.canvas.set_draw_func(self._on_canvas_draw, None)

        click = Gtk.GestureClick.new()
        click.connect("pressed", self._on_canvas_click)
        self.canvas.add_controller(click)

        scroll = Gtk.EventControllerScroll.new(
            flags=Gtk.EventControllerScrollFlags.VERTICAL)
        scroll.connect("scroll", self._on_scroll)
        self.canvas.add_controller(scroll)

        pan = Gtk.GestureDrag.new()
        pan.set_button(Gdk.BUTTON_MIDDLE)
        pan.connect("drag-begin", lambda g, x, y: (setattr(self, 'pan_start_x', self.pan_x), setattr(
            self, 'pan_start_y', self.pan_y)))
        pan.connect("drag-update", self._on_pan_update)
        self.canvas.add_controller(pan)

        canvas_box.append(self.canvas)
        self.content_stack.add_named(canvas_box, "canvas")

        status_page = Adw.StatusPage(
            title="No Scenes", icon_name="video-display-symbolic")
        self.content_stack.add_named(status_page, "status")

        return self.content_stack

    def _create_properties_panel(self):
        """Creates the properties panel."""
        print("DEBUG: SceneEditor._create_properties_panel")
        clamp = Adw.Clamp()
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        panel.set_margin_top(12)
        panel.set_margin_bottom(12)
        panel.set_margin_start(12)
        panel.set_margin_end(12)
        clamp.set_child(panel)

        group = Adw.PreferencesGroup()
        panel.append(group)

        self.background_preview = Gtk.Picture(
            content_fit=Gtk.ContentFit.CONTAIN, height_request=150)
        bg_row = Adw.ActionRow(title="Background Image")
        bg_row.add_suffix(self.background_preview)
        group.add(bg_row)

        set_bg_button = Gtk.Button(label="Choose Image...")
        set_bg_button.connect("clicked", self._on_set_background)
        group.add(set_bg_button)

        self.props_group = Adw.PreferencesGroup(title="Hotspot Properties")
        self.props_group.set_visible(False)
        panel.append(self.props_group)

        self.prop_name = Adw.EntryRow(title="Name")
        self.prop_name.connect("apply", self._on_prop_changed)
        self.props_group.add(self.prop_name)

        adj_x = Gtk.Adjustment(lower=0, upper=8192, step_increment=1)
        self.prop_x = Adw.SpinRow(title="X", adjustment=adj_x)
        self.prop_x.connect("notify::value", self._on_prop_changed)
        self.props_group.add(self.prop_x)

        adj_y = Gtk.Adjustment(lower=0, upper=8192, step_increment=1)
        self.prop_y = Adw.SpinRow(title="Y", adjustment=adj_y)
        self.prop_y.connect("notify::value", self._on_prop_changed)
        self.props_group.add(self.prop_y)

        adj_w = Gtk.Adjustment(lower=1, upper=8192, step_increment=1)
        self.prop_w = Adw.SpinRow(title="Width", adjustment=adj_w)
        self.prop_w.connect("notify::value", self._on_prop_changed)
        self.props_group.add(self.prop_w)

        adj_h = Gtk.Adjustment(lower=1, upper=8192, step_increment=1)
        self.prop_h = Adw.SpinRow(title="Height", adjustment=adj_h)
        self.prop_h.connect("notify::value", self._on_prop_changed)
        self.props_group.add(self.prop_h)

        self.hotspot_model = Gio.ListStore(item_type=HotspotGObject)
        self.hotspot_selection = Gtk.SingleSelection(
            model=self.hotspot_model)
        self.hotspot_selection.connect(
            "selection-changed", self._on_layer_selected)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_layer_item)
        factory.connect("bind", self._bind_layer_item)

        self.layer_list = Gtk.ListView(
            model=self.hotspot_selection, factory=factory)

        scrolled = Gtk.ScrolledWindow(child=self.layer_list)
        scrolled.set_vexpand(True)

        layer_group = Adw.PreferencesGroup(title="Layers")
        layer_group.add(scrolled)
        panel.append(layer_group)

        return clamp

    def _setup_layer_item(self, factory, list_item):
        """Sets up a layer item."""
        label = Gtk.Label(
            halign=Gtk.Align.START, margin_start=10, margin_top=10, margin_bottom=10)
        list_item.set_child(label)

    def _bind_layer_item(self, factory, list_item):
        """Binds a layer item to the data model."""
        label = list_item.get_child()
        hotspot_gobject = list_item.get_item()
        label.set_text(hotspot_gobject.name)

    def _on_layer_selected(self, selection, position, n_items):
        """Handles the selection-changed signal from the layer list."""
        print("DEBUG: SceneEditor._on_layer_selected")
        hotspot_gobject = selection.get_selected_item()
        if hotspot_gobject:
            self.selected_hotspot = hotspot_gobject.hotspot
        else:
            self.selected_hotspot = None
        self._update_props_panel()
        self.canvas.queue_draw()

    def _update_layer_list(self):
        """Updates the layer list."""
        print("DEBUG: SceneEditor._update_layer_list")
        self.hotspot_model.remove_all()
        scene = self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        if scene:
            for hotspot in scene.hotspots:
                self.hotspot_model.append(HotspotGObject(hotspot))

    def _update_visibility(self):
        """Updates the visibility of the main content."""
        has_scenes = self.scene_model.get_n_items() > 0
        print(f"DEBUG: SceneEditor._update_visibility: has_scenes={has_scenes}")
        if has_scenes:
            self.content_stack.set_visible_child_name("canvas")
        else:
            self.content_stack.set_visible_child_name("status")

    def _update_scene_list(self):
        """Updates the scene list."""
        print("DEBUG: SceneEditor._update_scene_list")
        self.scene_model.remove_all()
        for scene in self.project_manager.data.scenes:
            self.scene_model.append(SceneGObject(scene))

    def _on_scene_selected(self, selection, position, n_items):
        """Handles the selection-changed signal from the scene list."""
        print("DEBUG: SceneEditor._on_scene_selected")
        self.selected_scene_gobject = selection.get_selected_item()
        self.delete_scene_button.set_sensitive(
            self.selected_scene_gobject is not None)
        self.selected_hotspot = None
        self._update_props_panel()
        self._update_layer_list()
        self.canvas.queue_draw()

    def _on_add_scene(self, button):
        """Handles the clicked signal from the add scene button."""
        print("DEBUG: SceneEditor._on_add_scene")
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(), modal=True, heading="Create New Scene")
        entry = Adw.EntryRow(title="Scene Name")
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("create", "_Create")
        dialog.set_default_response("create")

        def on_response(d, response_id):
            if response_id == "create":
                name = entry.get_text()
                if name:
                    self.project_manager.create_scene(name)
                    self._update_scene_list()
            d.destroy()
        dialog.connect("response", on_response)
        dialog.present()

    def _on_remove_scene(self, button):
        """Handles the clicked signal from the remove scene button."""
        print("DEBUG: SceneEditor._on_remove_scene")
        if not self.selected_scene_gobject:
            return
        dialog = Adw.MessageDialog(transient_for=self.get_root(), modal=True, heading="Delete Scene?",
                                   body=f"Are you sure you want to delete '{self.selected_scene_gobject.name}'?")
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_scene_response)
        dialog.present()

    def _on_delete_scene_response(self, dialog, response):
        """Handles the response from the delete scene dialog."""
        print(f"DEBUG: SceneEditor._on_delete_scene_response: response={response}")
        if response == "delete":
            self.project_manager.delete_scene(
                self.selected_scene_gobject.scene.id)
            self._update_scene_list()

    def _on_set_background(self, button):
        """Handles the clicked signal from the set background button."""
        print("DEBUG: SceneEditor._on_set_background")
        if not self.selected_scene_gobject:
            return
        dialog = Gtk.FileChooserNative.new(
            "Select a Background Image", self.get_root(), Gtk.FileChooserAction.OPEN)
        file_filter = Gtk.FileFilter()
        file_filter.add_pixbuf_formats()
        dialog.add_filter(file_filter)
        dialog.connect("response", self._on_file_chooser_response)
        dialog.show()

    def _on_file_chooser_response(self, dialog, response_id):
        """Handles the response from the file chooser dialog."""
        print(f"DEBUG: SceneEditor._on_file_chooser_response: response_id={response_id}")
        if response_id == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            relative_path = os.path.relpath(
                file_path, self.project_manager.project_path)
            scene = self.selected_scene_gobject.scene
            scene.background_image = relative_path
            self.project_manager.set_dirty(True)
            self._update_background_preview()
            self.canvas.queue_draw()

    def _update_background_preview(self):
        """Updates the background preview image."""
        print("DEBUG: SceneEditor._update_background_preview")
        scene = self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        if scene and scene.background_image and self.project_manager.project_path:
            full_path = os.path.join(
                self.project_manager.project_path, scene.background_image)
            if os.path.exists(full_path):
                self.background_preview.set_filename(full_path)
                return
        self.background_preview.set_filename(None)

    def _update_props_panel(self):
        """Updates the properties panel."""
        print("DEBUG: SceneEditor._update_props_panel")
        if self.selected_hotspot:
            self.prop_name.set_text(self.selected_hotspot.name)
            self.prop_x.set_value(self.selected_hotspot.x)
            self.prop_y.set_value(self.selected_hotspot.y)
            self.prop_w.set_value(self.selected_hotspot.width)
            self.prop_h.set_value(self.selected_hotspot.height)
            self.props_group.set_visible(True)
        else:
            self.props_group.set_visible(False)
        self._update_background_preview()

    def _on_prop_changed(self, widget, *args):
        """Handles the changed signal from a property widget."""
        print("DEBUG: SceneEditor._on_prop_changed")
        if not self.selected_hotspot:
            return
        self.selected_hotspot.name = self.prop_name.get_text()
        self.selected_hotspot.x = int(self.prop_x.get_value())
        self.selected_hotspot.y = int(self.prop_y.get_value())
        self.selected_hotspot.width = int(self.prop_w.get_value())
        self.selected_hotspot.height = int(self.prop_h.get_value())
        self.project_manager.set_dirty(True)
        self.canvas.queue_draw()

    def _on_canvas_draw(self, area, cr, w, h, _):
        """Draws the canvas."""
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()

        scene = self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        if not scene:
            return

        if scene.background_image and self.project_manager.project_path:
            full_path = os.path.join(
                self.project_manager.project_path, scene.background_image)
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
            cr.set_source_rgba(0.8, 0.8, 0.8, 0.2)
            cr.set_line_width(1 / self.zoom_level)
            grid_size = 50
            for i in range(0, w, grid_size):
                cr.move_to(i, 0)
                cr.line_to(i, h)
                cr.stroke()
            for i in range(0, h, grid_size):
                cr.move_to(0, i)
                cr.line_to(w, i)
                cr.stroke()

        for hotspot in scene.hotspots:
            if hotspot == self.selected_hotspot:
                cr.set_source_rgba(1.0, 1.0, 0.0, 0.6)
            else:
                cr.set_source_rgba(0.2, 0.5, 1.0, 0.5)
            cr.rectangle(hotspot.x, hotspot.y, hotspot.width, hotspot.height)
            cr.fill()
        cr.restore()

    def _on_canvas_click(self, gesture, n_press, x, y):
        """Handles a click on the canvas."""
        print(f"DEBUG: SceneEditor._on_canvas_click at ({x}, {y})")
        world_x = (x - self.pan_x) / self.zoom_level
        world_y = (y - self.pan_y) / self.zoom_level
        scene = self.selected_scene_gobject.scene if self.selected_scene_gobject else None

        if self.hotspot_mode and scene:
            grid_size = 50
            snapped_x = round(world_x / grid_size) * grid_size
            snapped_y = round(world_y / grid_size) * grid_size
            self.project_manager.add_hotspot_to_scene(
                scene.id, "New Hotspot", snapped_x, snapped_y, 100, 50)
            self._update_layer_list()
            self.canvas.queue_draw()
        elif scene:
            for hotspot in reversed(scene.hotspots):
                if world_x >= hotspot.x and world_x <= hotspot.x + hotspot.width and \
                   world_y >= hotspot.y and world_y <= hotspot.y + hotspot.height:
                    self.selected_hotspot = hotspot
                    self._update_props_panel()
                    self.canvas.queue_draw()
                    return
            self.selected_hotspot = None
            self._update_props_panel()
            self.canvas.queue_draw()

    def _on_scroll(self, controller, dx, dy):
        """Handles a scroll event on the canvas."""
        if controller.get_current_event_state() & Gdk.ModifierType.CONTROL_MASK:
            self.zoom_level *= 1.1 if dy < 0 else 1 / 1.1
            self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
            self.canvas.queue_draw()
            return True
        return False

    def _on_pan_update(self, gesture, x, y):
        """Handles a pan event on the canvas."""
        self.pan_x = self.pan_start_x + x
        self.pan_y = self.pan_start_y + y
        self.canvas.queue_draw()
