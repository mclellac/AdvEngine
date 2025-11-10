"""The scene editor for the AdvEngine application.

This module defines the SceneEditor, a graphical interface for creating and
managing game scenes. It includes a canvas for placing and manipulating
hotspots, a properties panel, and a layer list.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Gdk, Adw, GdkPixbuf
from ..core.schemas.scene import Scene, SceneGObject, Hotspot, HotspotGObject
from ..core.project_manager import ProjectManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_scene.ui"))
class SceneEditor(Gtk.Box):
    """A widget for editing game scenes and their hotspots.

    This editor provides a visual canvas for placing hotspots on a scene's
    background image. It supports panning, zooming, and grid snapping.

    Attributes:
        project_manager (ProjectManager): The main project manager instance.
        settings_manager: The main settings manager instance.
        selected_scene_gobject (SceneGObject): The currently selected scene.
        selected_hotspot (Hotspot): The currently selected hotspot.
    """

    __gtype_name__ = "SceneEditor"

    EDITOR_NAME = "Scenes"
    VIEW_NAME = "scenes_editor"
    ORDER = 0

    add_scene_button: Gtk.Button = Gtk.Template.Child()
    delete_scene_button: Gtk.Button = Gtk.Template.Child()
    scene_list_view: Gtk.ListView = Gtk.Template.Child()
    content_stack: Gtk.Stack = Gtk.Template.Child()
    hotspot_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    grid_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    canvas: Gtk.DrawingArea = Gtk.Template.Child()
    background_preview: Gtk.Picture = Gtk.Template.Child()
    set_bg_button: Gtk.Button = Gtk.Template.Child()
    props_group: Adw.PreferencesGroup = Gtk.Template.Child()
    prop_name: Adw.EntryRow = Gtk.Template.Child()
    prop_x: Adw.SpinRow = Gtk.Template.Child()
    prop_y: Adw.SpinRow = Gtk.Template.Child()
    prop_w: Adw.SpinRow = Gtk.Template.Child()
    prop_h: Adw.SpinRow = Gtk.Template.Child()
    layer_list: Gtk.ListView = Gtk.Template.Child()

    def __init__(self, project_manager: ProjectManager, settings_manager, **kwargs):
        """Initializes a new SceneEditor instance.

        Args:
            project_manager (ProjectManager): The project manager instance.
            settings_manager: The settings manager instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.selected_scene_gobject = None
        self.selected_hotspot = None
        self.hotspot_mode = False
        self.show_grid = True
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0

        self._setup_models()
        self._connect_signals()
        self._setup_canvas()

        self.project_manager.register_project_loaded_callback(self._on_project_loaded)

    def _setup_models(self):
        """Sets up the data models and list views for scenes and layers."""
        # Scene List
        self.scene_model = Gio.ListStore(item_type=SceneGObject)
        self.scene_selection = Gtk.SingleSelection(model=self.scene_model)
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_scene_list_item)
        factory.connect("bind", self._bind_scene_list_item)
        self.scene_list_view.set_model(self.scene_selection)
        self.scene_list_view.set_factory(factory)

        # Layer (Hotspot) List
        self.hotspot_model = Gio.ListStore(item_type=HotspotGObject)
        self.hotspot_selection = Gtk.SingleSelection(model=self.hotspot_model)
        layer_factory = Gtk.SignalListItemFactory()
        layer_factory.connect("setup", self._setup_layer_item)
        layer_factory.connect("bind", self._bind_layer_item)
        self.layer_list.set_model(self.hotspot_selection)
        self.layer_list.set_factory(layer_factory)

    def _connect_signals(self):
        """Connects widget signals to handler methods."""
        self.add_scene_button.connect("clicked", self._on_add_scene)
        self.delete_scene_button.connect("clicked", self._on_remove_scene)
        self.scene_selection.connect("selection-changed", self._on_scene_selected)
        self.hotspot_toggle.connect(
            "toggled", lambda b: setattr(self, "hotspot_mode", b.get_active())
        )
        self.grid_toggle.connect(
            "toggled",
            lambda b: setattr(self, "show_grid", b.get_active())
            or self.canvas.queue_draw(),
        )
        self.set_bg_button.connect("clicked", self._on_set_background)
        self.prop_name.connect("apply", self._on_prop_changed)
        self.prop_x.connect("notify::value", self._on_prop_changed)
        self.prop_y.connect("notify::value", self._on_prop_changed)
        self.prop_w.connect("notify::value", self._on_prop_changed)
        self.prop_h.connect("notify::value", self._on_prop_changed)
        self.hotspot_selection.connect("selection-changed", self._on_layer_selected)

    def _setup_canvas(self):
        """Sets up the drawing area and its event controllers."""
        self.canvas.set_draw_func(self._on_canvas_draw, None)
        click = Gtk.GestureClick.new()
        click.connect("pressed", self._on_canvas_click)
        self.canvas.add_controller(click)
        scroll = Gtk.EventControllerScroll.new(
            flags=Gtk.EventControllerScrollFlags.VERTICAL
        )
        scroll.connect("scroll", self._on_scroll)
        self.canvas.add_controller(scroll)
        pan = Gtk.GestureDrag.new()
        pan.set_button(Gdk.BUTTON_MIDDLE)
        pan.connect("drag-begin", self._on_pan_begin)
        pan.connect("drag-update", self._on_pan_update)
        self.canvas.add_controller(pan)

    def _on_project_loaded(self, *args):
        """Handles the project-loaded signal from the project manager."""
        self._update_scene_list()
        self._update_visibility()

    def _setup_scene_list_item(self, factory, list_item):
        """Sets up a widget for an item in the scene list.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to set up.
        """
        label = Gtk.Label(
            halign=Gtk.Align.START, margin_start=10, margin_top=10, margin_bottom=10
        )
        list_item.set_child(label)

    def _bind_scene_list_item(self, factory, list_item):
        """Binds a scene list item to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to bind.
        """
        label = list_item.get_child()
        scene_gobject = list_item.get_item()
        label.set_text(scene_gobject.name)

    def _setup_layer_item(self, factory, list_item):
        """Sets up a widget for an item in the layer (hotspot) list.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to set up.
        """
        label = Gtk.Label(
            halign=Gtk.Align.START, margin_start=10, margin_top=10, margin_bottom=10
        )
        list_item.set_child(label)

    def _bind_layer_item(self, factory, list_item):
        """Binds a layer list item to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to bind.
        """
        label = list_item.get_child()
        hotspot_gobject = list_item.get_item()
        label.set_text(hotspot_gobject.name)

    def _on_layer_selected(self, selection, position, n_items):
        """Handles selection changes in the layer list.

        Args:
            selection (Gtk.SingleSelection): The selection model.
            position (int): The position of the selected item.
            n_items (int): The number of items in the model.
        """
        hotspot_gobject = selection.get_selected_item()
        if hotspot_gobject:
            self.selected_hotspot = hotspot_gobject.hotspot
        else:
            self.selected_hotspot = None
        self._update_props_panel()
        self.canvas.queue_draw()

    def _update_layer_list(self):
        """Updates the layer list from the currently selected scene."""
        self.hotspot_model.remove_all()
        scene = (
            self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        )
        if scene:
            for hotspot in scene.hotspots:
                self.hotspot_model.append(HotspotGObject(hotspot))

    def _update_visibility(self):
        """Updates the visibility of the main content stack."""
        has_scenes = self.scene_model.get_n_items() > 0
        self.content_stack.set_visible_child_name("canvas" if has_scenes else "status")

    def _update_scene_list(self):
        """Updates the scene list from the project manager."""
        self.scene_model.remove_all()
        for scene in self.project_manager.data.scenes:
            self.scene_model.append(SceneGObject(scene))

    def _on_scene_selected(self, selection, position, n_items):
        """Handles selection changes in the scene list.

        Args:
            selection (Gtk.SingleSelection): The selection model.
            position (int): The position of the selected item.
            n_items (int): The number of items in the model.
        """
        self.selected_scene_gobject = selection.get_selected_item()
        self.delete_scene_button.set_sensitive(self.selected_scene_gobject is not None)
        self.selected_hotspot = None
        self._update_props_panel()
        self._update_layer_list()
        self.canvas.queue_draw()

    def _on_add_scene(self, button):
        """Handles the 'Add Scene' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(), modal=True, heading="Create New Scene"
        )
        entry = Adw.EntryRow(title="Scene Name")
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("create", "_Create")
        dialog.set_default_response("create")

        def on_response(d, response_id):
            if response_id == "create":
                name = entry.get_text()
                if name:
                    new_scene = Scene(id=name.lower(), name=name)
                    self.project_manager.add_data_item("scenes", new_scene)
                    self._update_scene_list()
                    self._update_visibility()
            d.close()

        dialog.connect("response", on_response)
        dialog.present()

    def _on_remove_scene(self, button):
        """Handles the 'Remove Scene' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        if not self.selected_scene_gobject:
            return
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Scene?",
            body=f"Are you sure you want to delete '{self.selected_scene_gobject.name}'?",
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_scene_response)
        dialog.present()

    def _on_delete_scene_response(self, dialog, response):
        """Handles the response from the delete scene confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog.
            response (str): The response ID.
        """
        if response == "delete":
            self.project_manager.remove_data_item(
                "scenes", self.selected_scene_gobject.scene
            )
            self._update_scene_list()
            self._update_visibility()
        dialog.close()

    def _on_set_background(self, button):
        """Handles the 'Set Background' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        if not self.selected_scene_gobject:
            return
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Select a Background Image")
        file_filter = Gtk.FileFilter()
        file_filter.add_pixbuf_formats()
        dialog.set_default_filter(file_filter)
        dialog.open(self.get_root(), None, self._on_file_chooser_response)

    def _on_file_chooser_response(self, dialog, result):
        """Handles the response from the background image file chooser.

        Args:
            dialog: The file dialog.
            result: The result of the dialog.
        """
        try:
            file = dialog.open_finish(result)
            file_path = file.get_path()
            relative_path = os.path.relpath(
                file_path, self.project_manager.project_path
            )
            scene = self.selected_scene_gobject.scene
            scene.background_image = relative_path
            self.project_manager.set_dirty(True)
            self._update_background_preview()
            self.canvas.queue_draw()
        except Exception as e:
            print(f"Error selecting background image: {e}")

    def _update_background_preview(self):
        """Updates the background image preview in the properties panel."""
        scene = (
            self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        )
        if scene and scene.background_image and self.project_manager.project_path:
            full_path = os.path.join(
                self.project_manager.project_path, scene.background_image
            )
            if os.path.exists(full_path):
                self.background_preview.set_filename(full_path)
                return
        self.background_preview.set_filename(None)

    def _update_props_panel(self):
        """Updates the properties panel with the selected hotspot's data."""
        is_visible = self.selected_hotspot is not None
        self.props_group.set_visible(is_visible)
        if is_visible:
            self.prop_name.set_text(self.selected_hotspot.name)
            self.prop_x.set_value(self.selected_hotspot.x)
            self.prop_y.set_value(self.selected_hotspot.y)
            self.prop_w.set_value(self.selected_hotspot.width)
            self.prop_h.set_value(self.selected_hotspot.height)
        self._update_background_preview()

    def _on_prop_changed(self, widget, *args):
        """Handles value changes from the properties panel.

        Args:
            widget: The widget that emitted the signal.
            *args: Additional arguments from the signal.
        """
        if not self.selected_hotspot:
            return
        self.selected_hotspot.name = self.prop_name.get_text()
        self.selected_hotspot.x = int(self.prop_x.get_value())
        self.selected_hotspot.y = int(self.prop_y.get_value())
        self.selected_hotspot.width = int(self.prop_w.get_value())
        self.selected_hotspot.height = int(self.prop_h.get_value())
        self.project_manager.set_dirty(True)
        self.canvas.queue_draw()
        self._update_layer_list()  # To refresh the name in the list

    def _on_canvas_draw(self, area, cr, w, h, _):
        """Draws the content of the scene editor canvas.

        Args:
            area (Gtk.DrawingArea): The drawing area.
            cr: The Cairo context.
            w (int): The width of the drawing area.
            h (int): The height of the drawing area.
            _: User data (unused).
        """
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()
        scene = (
            self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        )
        if not scene:
            return
        if scene.background_image and self.project_manager.project_path:
            full_path = os.path.join(
                self.project_manager.project_path, scene.background_image
            )
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
            for i in range(0, int(w / self.zoom_level), grid_size):
                cr.move_to(i, 0)
                cr.line_to(i, int(h / self.zoom_level))
                cr.stroke()
            for i in range(0, int(h / self.zoom_level), grid_size):
                cr.move_to(0, i)
                cr.line_to(int(w / self.zoom_level), i)
                cr.stroke()
        for hotspot in scene.hotspots:
            (
                cr.set_source_rgba(1.0, 1.0, 0.0, 0.6)
                if hotspot == self.selected_hotspot
                else cr.set_source_rgba(0.2, 0.5, 1.0, 0.5)
            )
            cr.rectangle(hotspot.x, hotspot.y, hotspot.width, hotspot.height)
            cr.fill()
        cr.restore()

    def _on_canvas_click(self, gesture, n_press, x, y):
        """Handles a click event on the canvas.

        Args:
            gesture (Gtk.GestureClick): The click gesture.
            n_press (int): The number of presses.
            x (float): The x-coordinate of the click.
            y (float): The y-coordinate of the click.
        """
        world_x, world_y = (x - self.pan_x) / self.zoom_level, (
            y - self.pan_y
        ) / self.zoom_level
        scene = (
            self.selected_scene_gobject.scene if self.selected_scene_gobject else None
        )
        if not scene:
            return
        if self.hotspot_mode:
            grid_size = 50
            snapped_x = round(world_x / grid_size) * grid_size
            snapped_y = round(world_y / grid_size) * grid_size
            new_hotspot = Hotspot(
                name="New Hotspot",
                x=snapped_x,
                y=snapped_y,
                width=100,
                height=50,
            )
            scene.hotspots.append(new_hotspot)
            self.project_manager.set_dirty(True)
            self._update_layer_list()
            self.canvas.queue_draw()
        else:
            clicked_hotspot = None
            for hotspot in reversed(scene.hotspots):
                if (
                    world_x >= hotspot.x
                    and world_x <= hotspot.x + hotspot.width
                    and world_y >= hotspot.y
                    and world_y <= hotspot.y + hotspot.height
                ):
                    clicked_hotspot = hotspot
                    break
            self.selected_hotspot = clicked_hotspot
            self._update_props_panel()
            self.canvas.queue_draw()

    def _on_scroll(self, controller, dx, dy):
        """Handles scroll events for zooming.

        Args:
            controller: The event controller.
            dx (float): The scroll delta on the x-axis.
            dy (float): The scroll delta on the y-axis.

        Returns:
            bool: True to indicate the event was handled.
        """
        if controller.get_current_event_state() & Gdk.ModifierType.CONTROL_MASK:
            self.zoom_level *= 1.1 if dy < 0 else 1 / 1.1
            self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
            self.canvas.queue_draw()
            return True
        return False

    def _on_pan_begin(self, gesture, x, y):
        """Handles the beginning of a pan drag.

        Args:
            gesture (Gtk.GestureDrag): The drag gesture.
            x (float): The starting x-coordinate.
            y (float): The starting y-coordinate.
        """
        self.pan_start_x = self.pan_x
        self.pan_start_y = self.pan_y

    def _on_pan_update(self, gesture, x, y):
        """Handles the update of a pan drag.

        Args:
            gesture (Gtk.GestureDrag): The drag gesture.
            x (float): The x-offset of the drag.
            y (float): The y-offset of the drag.
        """
        self.pan_x = self.pan_start_x + x
        self.pan_y = self.pan_start_y + y
        self.canvas.queue_draw()
