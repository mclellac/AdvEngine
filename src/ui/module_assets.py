"""The asset editor for the AdvEngine application.

This module defines the AssetEditor, a widget for managing all game assets
such as sprites, textures, and animations. It provides a grid view for
browsing assets and a detail view for previewing and editing them.
"""

import gi
import os
import shutil

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Adw, Gdk
from ..core.schemas.asset import Asset, Animation, AssetGObject
from ..core.schemas.gobject_factory import StringGObject


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_assets.ui"))
class AssetEditor(Gtk.Box):
    """A widget for managing game assets.

    This editor allows users to import new assets, view existing assets in a
    grid, preview selected assets, and manage the frames of animation assets.

    Attributes:
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        selected_asset: The currently selected asset object.
        model (Gio.ListStore): The data store for all assets.
        selection_model (Gtk.SingleSelection): The selection model for the
            asset grid view.
        animation_frames_model (Gio.ListStore): The data store for the frames
            of a selected animation.
    """

    __gtype_name__ = "AssetEditor"

    EDITOR_NAME = "Assets"
    VIEW_NAME = "assets_editor"
    ORDER = 5

    asset_grid_view: Gtk.GridView = Gtk.Template.Child()
    main_stack: Gtk.Stack = Gtk.Template.Child()
    import_button: Gtk.Button = Gtk.Template.Child()
    preview_image: Gtk.Picture = Gtk.Template.Child()
    animation_editor: Gtk.Box = Gtk.Template.Child()
    frame_list_view: Gtk.ListView = Gtk.Template.Child()

    def __init__(self, project_manager, settings_manager, **kwargs):
        """Initializes a new AssetEditor instance.

        Args:
            project_manager: The project manager instance.
            settings_manager: The settings manager instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.selected_asset = None
        self.project_manager.register_project_loaded_callback(self.project_loaded)

        self._setup_models()
        self._setup_grid_view()
        self._setup_animation_editor()
        self._connect_signals()

        self.refresh_asset_list()

    def project_loaded(self):
        """Callback executed when a project is finished loading."""
        self.refresh_asset_list()

    def _setup_models(self):
        """Sets up the data models for the asset lists."""
        self.model = Gio.ListStore(item_type=AssetGObject)
        self.selection_model = Gtk.SingleSelection(model=self.model)
        self.animation_frames_model = Gio.ListStore(item_type=StringGObject)

    def _setup_grid_view(self):
        """Sets up the factory and model for the asset grid view."""
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_grid_item)
        factory.connect("bind", self._bind_grid_item)
        self.asset_grid_view.set_model(self.selection_model)
        self.asset_grid_view.set_factory(factory)

    def _setup_animation_editor(self):
        """Sets up the factory and model for the animation frame list view."""
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_frame_row)
        factory.connect("bind", self._bind_frame_row)
        self.frame_list_view.set_model(
            Gtk.SingleSelection(model=self.animation_frames_model)
        )
        self.frame_list_view.set_factory(factory)

    def _connect_signals(self):
        """Connects widget signals to their corresponding handlers."""
        self.selection_model.connect("selection-changed", self._on_asset_selected)
        self.import_button.connect("clicked", self._on_import_asset)

    def _setup_grid_item(self, factory, list_item):
        """Constructs the widget for a single item in the asset grid.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to set up.
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        picture = Gtk.Picture()
        picture.set_size_request(100, 100)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        label = Gtk.Label()
        box.append(picture)
        box.append(label)
        list_item.set_child(box)

    def _bind_grid_item(self, factory, list_item):
        """Binds data from the model to the asset grid item's widgets.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to bind.
        """
        box = list_item.get_child()
        children = list(box.observe_children())
        picture = children[0]
        label = children[1]

        asset_gobject = list_item.get_item()
        asset = asset_gobject.asset

        label.set_text(asset.name)
        if asset.asset_type in ["sprite", "texture"] and os.path.exists(
            os.path.join(self.project_manager.project_path, asset.file_path)
        ):
            picture.set_filename(
                os.path.join(self.project_manager.project_path, asset.file_path)
            )
        else:
            picture.set_filename(None)

    def _setup_frame_row(self, factory, list_item):
        """Constructs the widget for a single animation frame row.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to set up.
        """
        row = Gtk.Label()
        list_item.set_child(row)

        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self._on_frame_drag_prepare)
        drag_source.connect("drag-begin", self._on_frame_drag_begin)
        row.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(
            type=StringGObject, actions=Gdk.DragAction.MOVE
        )
        drop_target.connect("drop", self._on_frame_drop)
        row.add_controller(drop_target)

    def _bind_frame_row(self, factory, list_item):
        """Binds data to an animation frame row widget.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to bind.
        """
        label = list_item.get_child()
        frame_path = list_item.get_item().value
        label.set_text(os.path.basename(frame_path))

    def _on_asset_selected(self, selection_model, position, n_items):
        """Handles the selection of an asset in the grid view.

        Args:
            selection_model (Gtk.SingleSelection): The selection model.
            position (int): The position of the selected item.
            n_items (int): The number of items in the model.
        """
        selected_asset_gobject = selection_model.get_selected_item()
        if selected_asset_gobject:
            self.selected_asset = selected_asset_gobject.asset
            asset_path = os.path.join(
                self.project_manager.project_path, self.selected_asset.file_path
            )
            if self.selected_asset.asset_type in [
                "sprite",
                "texture",
            ] and os.path.exists(asset_path):
                self.preview_image.set_filename(asset_path)
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
        self.animation_frames_model.remove_all()
        if self.selected_asset and isinstance(self.selected_asset, Animation):
            for frame in self.selected_asset.frames:
                self.animation_frames_model.append(StringGObject(frame))

    def refresh_asset_list(self):
        """Refreshes the list of assets in the asset grid view from the
        project manager."""
        self.model.remove_all()
        for asset in self.project_manager.data.assets:
            self.model.append(AssetGObject(asset))
        self._update_visibility()

    def _update_visibility(self):
        """Updates the visibility of the main stack based on whether there
        are any assets."""
        has_assets = self.model.get_n_items() > 0
        self.main_stack.set_visible_child_name("grid" if has_assets else "status")

    def _on_import_asset(self, button):
        """Handles the 'Import' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Import Asset")

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Image Files")
        file_filter.add_pixbuf_formats()
        dialog.set_default_filter(file_filter)

        dialog.open_multiple(self.get_native(), None, self._on_import_asset_response)

    def _on_import_asset_response(self, dialog, result):
        """Handles the response from the import asset file dialog.

        Args:
            dialog: The file dialog.
            result: The result of the file dialog.
        """
        try:
            files = dialog.open_multiple_finish(result)
            if files:
                if len(files) > 1:
                    self._import_animation(files)
                else:
                    self._import_single_asset(files[0])

                self.project_manager.set_dirty()
                self.refresh_asset_list()
        except Exception as e:
            self._show_error_dialog(f"Error importing asset(s): {e}")

    def _import_animation(self, files):
        """Imports a sequence of files as a single animation.

        Args:
            files (list): A list of Gio.File objects to import.
        """
        asset_name = os.path.basename(files[0].get_path()).split(".")[0]
        new_anim = Animation(
            id=f"anim_{len(self.project_manager.data.assets)}",
            name=asset_name,
            asset_type="animation",
            file_path="",
            frame_count=len(files),
            frame_rate=10,
            frames=[],
        )

        anim_dir = os.path.join(self.project_manager.project_path, "Assets", asset_name)
        os.makedirs(anim_dir, exist_ok=True)

        for file in files:
            filepath = file.get_path()
            if not self._is_supported_image_file(filepath):
                self._show_error_dialog(
                    f"Unsupported file type: {os.path.basename(filepath)}"
                )
                continue
            new_filepath = os.path.join(anim_dir, os.path.basename(filepath))
            shutil.copy(filepath, new_filepath)
            new_anim.frames.append(
                os.path.relpath(new_filepath, self.project_manager.project_path)
            )

        self.project_manager.data.assets.append(new_anim)

    def _import_single_asset(self, file):
        """Imports a single file as a sprite asset.

        Args:
            file (Gio.File): The file to import.
        """
        filepath = file.get_path()
        if not self._is_supported_image_file(filepath):
            self._show_error_dialog(
                f"Unsupported file type: {os.path.basename(filepath)}"
            )
            return
        asset_name = os.path.basename(filepath)
        asset_type = "sprite"

        assets_dir = os.path.join(self.project_manager.project_path, "Assets")
        os.makedirs(assets_dir, exist_ok=True)
        new_filepath = os.path.join(assets_dir, asset_name)
        shutil.copy(filepath, new_filepath)

        new_asset = Asset(
            id=f"asset_{len(self.project_manager.data.assets)}",
            name=asset_name,
            asset_type=asset_type,
            file_path=os.path.relpath(new_filepath, self.project_manager.project_path),
        )
        self.project_manager.data.assets.append(new_asset)

    def _on_frame_drag_prepare(self, source, x, y):
        """Prepares the content for a drag-and-drop operation.

        Args:
            source (Gtk.DragSource): The drag source.
            x (int): The x-coordinate of the drag operation.
            y (int): The y-coordinate of the drag operation.

        Returns:
            Gdk.ContentProvider: The content provider for the drag operation.
        """
        list_item = source.get_widget().get_parent()
        frame_path_gobject = list_item.get_item()
        return Gdk.ContentProvider.new_for_value(frame_path_gobject)

    def _on_frame_drag_begin(self, source, drag):
        """Handles the beginning of a drag operation.

        Args:
            source (Gtk.DragSource): The drag source.
            drag (Gdk.Drag): The drag object.
        """
        list_item = source.get_widget().get_parent()
        source.set_icon(Gtk.WidgetPaintable.new(list_item), 0, 0)

    def _on_frame_drop(self, target, value, x, y):
        """Handles a drop operation for reordering animation frames.

        Args:
            target (Gtk.DropTarget): The drop target.
            value: The value being dropped.
            x (int): The x-coordinate of the drop.
            y (int): The y-coordinate of the drop.

        Returns:
            bool: True if the drop was successful, False otherwise.
        """
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
        """Checks if a file is a supported image type based on its extension.

        Args:
            filepath (str): The path to the file.

        Returns:
            bool: True if the file is a supported image, False otherwise.
        """
        supported_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        return any(filepath.lower().endswith(ext) for ext in supported_extensions)

    def _show_error_dialog(self, message):
        """Shows a simple error dialog.

        Args:
            message (str): The error message to display.
        """
        dialog = Adw.MessageDialog(
            heading="Error",
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present(self.get_native())
