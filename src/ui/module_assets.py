"""The asset editor for the AdvEngine application."""

import gi
import os
import shutil
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Adw, Gdk
from ..core.data_schemas import Asset, Animation, StringGObject, AssetGObject


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_assets.ui"))
class AssetEditor(Gtk.Box):
    """A widget for managing game assets."""
    __gtype_name__ = 'AssetEditor'

    EDITOR_NAME = "Assets"
    VIEW_NAME = "assets_editor"
    ORDER = 5

    asset_grid_view = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    import_button = Gtk.Template.Child()
    preview_image = Gtk.Template.Child()
    animation_editor = Gtk.Template.Child()
    frame_list_view = Gtk.Template.Child()

    def __init__(self, project_manager, **kwargs):
        """Initializes a new AssetEditor instance."""
        print("DEBUG: AssetEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.selected_asset = None

        self._setup_models()
        self._setup_grid_view()
        self._setup_animation_editor()
        self._connect_signals()

        self.refresh_asset_list()

    def _setup_models(self):
        """Sets up the data models."""
        self.model = Gio.ListStore(item_type=AssetGObject)
        self.selection_model = Gtk.SingleSelection(model=self.model)
        self.animation_frames_model = Gio.ListStore(item_type=StringGObject)

    def _setup_grid_view(self):
        """Sets up the asset grid view."""
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_grid_item)
        factory.connect("bind", self._bind_grid_item)
        self.asset_grid_view.set_model(self.selection_model)
        self.asset_grid_view.set_factory(factory)

    def _setup_animation_editor(self):
        """Sets up the animation editor."""
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_frame_row)
        factory.connect("bind", self._bind_frame_row)
        self.frame_list_view.set_model(Gtk.SingleSelection(model=self.animation_frames_model))
        self.frame_list_view.set_factory(factory)

    def _connect_signals(self):
        """Connects widget signals to handlers."""
        self.selection_model.connect("selection-changed", self._on_asset_selected)
        self.import_button.connect("clicked", self._on_import_asset)

    def _setup_grid_item(self, factory, list_item):
        """Sets up a grid item in the asset grid view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        picture = Gtk.Picture()
        picture.set_size_request(100, 100)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        label = Gtk.Label()
        box.append(picture)
        box.append(label)
        list_item.set_child(box)

    def _bind_grid_item(self, factory, list_item):
        """Binds a grid item to the data model."""
        box = list_item.get_child()
        children = list(box.observe_children())
        picture = children[0]
        label = children[1]

        asset_gobject = list_item.get_item()
        asset = asset_gobject.asset

        label.set_text(asset.name)
        if asset.asset_type in ["sprite", "texture"] and os.path.exists(os.path.join(self.project_manager.project_path, asset.file_path)):
            picture.set_filename(os.path.join(
                self.project_manager.project_path, asset.file_path))
        else:
            picture.set_filename(None)

    def _setup_frame_row(self, factory, list_item):
        """Sets up a frame row in the animation editor."""
        row = Gtk.Label()
        list_item.set_child(row)

        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self._on_frame_drag_prepare)
        drag_source.connect("drag-begin", self._on_frame_drag_begin)
        row.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(
            type=StringGObject, actions=Gdk.DragAction.MOVE)
        drop_target.connect("drop", self._on_frame_drop)
        row.add_controller(drop_target)

    def _bind_frame_row(self, factory, list_item):
        """Binds a frame row to the data model."""
        label = list_item.get_child()
        frame_path = list_item.get_item().value
        label.set_text(os.path.basename(frame_path))

    def _on_asset_selected(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        print("DEBUG: AssetEditor._on_asset_selected")
        selected_asset_gobject = selection_model.get_selected_item()
        if selected_asset_gobject:
            self.selected_asset = selected_asset_gobject.asset
            if self.selected_asset.asset_type in ["sprite", "texture"] and os.path.exists(os.path.join(self.project_manager.project_path, self.selected_asset.file_path)):
                self.preview_image.set_filename(os.path.join(
                    self.project_manager.project_path, self.selected_asset.file_path))
                self.animation_editor.set_visible(False)
            elif self.selected_asset.asset_type == "animation":
                self.animation_editor.set_visible(True)
                self.preview_image.set_filename(None)
                self.refresh_frame_list()
            else:
                self.preview_image.set_filename(None)
                self.animation_editor.set_visible(False)
        else:
            self.selected_asset = None
            self.preview_image.set_filename(None)
            self.animation_editor.set_visible(False)

    def refresh_frame_list(self):
        """Refreshes the list of frames in the animation editor."""
        print("DEBUG: AssetEditor.refresh_frame_list")
        self.animation_frames_model.remove_all()
        if self.selected_asset and isinstance(self.selected_asset, Animation):
            for frame in self.selected_asset.frames:
                self.animation_frames_model.append(StringGObject(frame))

    def refresh_asset_list(self):
        """Refreshes the list of assets in the asset grid view."""
        print("DEBUG: AssetEditor.refresh_asset_list")
        self.model.remove_all()
        for asset in self.project_manager.data.assets:
            self.model.append(AssetGObject(asset))
        self._update_visibility()

    def _update_visibility(self):
        """Updates the visibility of the main stack."""
        has_assets = self.model.get_n_items() > 0
        print(f"DEBUG: AssetEditor._update_visibility: has_assets={has_assets}")
        self.main_stack.set_visible_child_name("grid" if has_assets else "status")

    def _on_import_asset(self, button):
        """Handles the clicked signal from the import button."""
        print("DEBUG: AssetEditor._on_import_asset")
        dialog = Gtk.FileChooserNative(
            title="Import Asset", transient_for=self.get_native(), action=Gtk.FileChooserAction.OPEN)
        dialog.set_select_multiple(True)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Image Files")
        file_filter.add_pixbuf_formats()
        dialog.add_filter(file_filter)

        dialog.connect("response", self._on_import_asset_response)
        dialog.show()

    def _on_import_asset_response(self, dialog, response_id):
        """Handles the response from the import asset file chooser."""
        print(f"DEBUG: AssetEditor._on_import_asset_response: {response_id}")
        if response_id == Gtk.ResponseType.ACCEPT:
            files = dialog.get_files()
            try:
                if len(files) > 1:
                    self._import_animation(files)
                else:
                    self._import_single_asset(files[0])

                self.project_manager.set_dirty()
                self.refresh_asset_list()
            except Exception as e:
                self._show_error_dialog(f"Error importing asset(s): {e}")

    def _import_animation(self, files):
        """Imports a sequence of files as an animation."""
        print("DEBUG: AssetEditor._import_animation")
        asset_name = os.path.basename(files[0].get_path()).split('.')[0]
        new_anim = Animation(id=f"anim_{len(self.project_manager.data.assets)}",
                             name=asset_name, asset_type="animation", file_path="", frame_count=len(files), frame_rate=10, frames=[])

        anim_dir = os.path.join(
            self.project_manager.project_path, "Assets", asset_name)
        os.makedirs(anim_dir, exist_ok=True)

        for file in files:
            filepath = file.get_path()
            if not self._is_supported_image_file(filepath):
                self._show_error_dialog(
                    f"Unsupported file type: {os.path.basename(filepath)}")
                continue
            new_filepath = os.path.join(anim_dir, os.path.basename(filepath))
            shutil.copy(filepath, new_filepath)
            new_anim.frames.append(os.path.relpath(new_filepath, self.project_manager.project_path))

        self.project_manager.data.assets.append(new_anim)

    def _import_single_asset(self, file):
        """Imports a single file as an asset."""
        print("DEBUG: AssetEditor._import_single_asset")
        filepath = file.get_path()
        if not self._is_supported_image_file(filepath):
            self._show_error_dialog(
                f"Unsupported file type: {os.path.basename(filepath)}")
            return
        asset_name = os.path.basename(filepath)
        asset_type = "sprite"

        assets_dir = os.path.join(self.project_manager.project_path, "Assets")
        os.makedirs(assets_dir, exist_ok=True)
        new_filepath = os.path.join(assets_dir, asset_name)
        shutil.copy(filepath, new_filepath)

        new_asset = Asset(
            id=f"asset_{len(self.project_manager.data.assets)}", name=asset_name, asset_type=asset_type, file_path=os.path.relpath(new_filepath, self.project_manager.project_path))
        self.project_manager.data.assets.append(new_asset)

    def _on_frame_drag_prepare(self, source, x, y):
        """Prepares a frame for dragging."""
        list_item = source.get_widget().get_parent()
        frame_path_gobject = list_item.get_item()
        return Gdk.ContentProvider.new_for_value(frame_path_gobject)

    def _on_frame_drag_begin(self, source, drag):
        """Begins a frame drag operation."""
        list_item = source.get_widget().get_parent()
        source.set_icon(Gtk.WidgetPaintable.new(list_item), 0, 0)

    def _on_frame_drop(self, target, value, x, y):
        """Handles a frame drop operation."""
        print("DEBUG: AssetEditor._on_frame_drop")
        dragged_frame_gobject = value
        widget = target.get_widget()
        list_item = widget.get_ancestor(Gtk.ListItem)
        if not list_item:
            return False
        target_frame_gobject = list_item.get_item()

        if dragged_frame_gobject and target_frame_gobject and self.selected_asset:
            dragged_frame = dragged_frame_gobject.value
            target_frame = target_frame_gobject.value
            dragged_index = self.selected_asset.frames.index(dragged_frame)
            target_index = self.selected_asset.frames.index(target_frame)
            self.selected_asset.frames.pop(dragged_index)
            self.selected_asset.frames.insert(target_index, dragged_frame)
            self.project_manager.set_dirty()
            self.refresh_frame_list()
            return True
        return False

    def _is_supported_image_file(self, filepath):
        """Checks if a file is a supported image file."""
        supported_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        return any(filepath.lower().endswith(ext) for ext in supported_extensions)

    def _show_error_dialog(self, message):
        """Shows an error dialog."""
        dialog = Adw.MessageDialog(
            transient_for=self.get_native(),
            modal=True,
            heading="Error",
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: d.close())
        dialog.present()
