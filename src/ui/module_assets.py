import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Adw, Gdk
import os
import shutil
from ..core.data_schemas import Asset, Animation, StringGObject, AssetGObject

class AssetEditor(Gtk.Box):
    EDITOR_NAME = "Assets"
    VIEW_NAME = "assets_editor"
    ORDER = 5

    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.selected_asset = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(350, -1)

        self.model = Gio.ListStore(item_type=AssetGObject)
        self.refresh_asset_list()

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_grid_item)
        factory.connect("bind", self._bind_grid_item)

        selection_model = Gtk.SingleSelection(model=self.model)
        selection_model.connect("selection-changed", self.on_asset_selected)

        self.asset_grid_view = Gtk.GridView(model=selection_model, factory=factory)
        self.asset_grid_view.set_max_columns(3)
        self.asset_grid_view.set_min_columns(2)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)

        self.status_page = Adw.StatusPage(title="No Assets", icon_name="image-x-generic-symbolic")

        self.main_stack = Gtk.Stack()
        self.main_stack.add_named(scrolled_window, "grid")
        self.main_stack.add_named(self.status_page, "status")
        left_panel.append(self.main_stack)

        self.asset_grid_view.set_model(selection_model)
        scrolled_window.set_child(self.asset_grid_view)

        import_button = Gtk.Button(label="Import Asset")
        import_button.set_tooltip_text("Import a new image asset into the project")
        import_button.connect("clicked", self.on_import_asset)
        left_panel.append(import_button)
        self.append(left_panel)

        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_panel.set_hexpand(True)
        self.append(right_panel)

        self.preview_image = Gtk.Picture()
        self.preview_image.set_content_fit(Gtk.ContentFit.CONTAIN)
        right_panel.append(self.preview_image)

        # Animation Editor
        self.animation_editor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, visible=False)
        self.animation_editor.append(Gtk.Label(label="Animation Frames"))

        self.animation_frames_model = Gio.ListStore(item_type=StringGObject)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_frame_row)
        factory.connect("bind", self._bind_frame_row)

        self.frame_list_view = Gtk.ListView(model=Gtk.SingleSelection(model=self.animation_frames_model), factory=factory)

        scrolled_frames = Gtk.ScrolledWindow()
        scrolled_frames.set_child(self.frame_list_view)
        self.animation_editor.append(scrolled_frames)
        right_panel.append(self.animation_editor)

    def _setup_grid_item(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        picture = Gtk.Picture()
        picture.set_size_request(100, 100)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        label = Gtk.Label()
        box.append(picture)
        box.append(label)
        list_item.set_child(box)

    def _bind_grid_item(self, factory, list_item):
        box = list_item.get_child()
        children = list(box.observe_children())
        picture = children[0]
        label = children[1]

        asset_gobject = list_item.get_item()
        asset = asset_gobject.asset_data

        label.set_text(asset.name)
        if asset.asset_type in ["sprite", "texture"] and os.path.exists(asset.file_path):
            picture.set_filename(asset.file_path)
        else:
            picture.set_filename(None)

    def _setup_frame_row(self, factory, list_item):
        row = Gtk.Label()
        list_item.set_child(row)

        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self._on_frame_drag_prepare)
        drag_source.connect("drag-begin", self._on_frame_drag_begin)
        row.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(type=StringGObject, actions=Gdk.DragAction.MOVE)
        drop_target.connect("drop", self._on_frame_drop)
        row.add_controller(drop_target)

    def _bind_frame_row(self, factory, list_item):
        label = list_item.get_child()
        frame_path = list_item.get_item().value
        label.set_text(os.path.basename(frame_path))

    def on_asset_selected(self, selection_model, position, n_items):
        selected_asset_gobject = selection_model.get_selected_item()
        if selected_asset_gobject:
            self.selected_asset = selected_asset_gobject.asset_data
            if self.selected_asset.asset_type in ["sprite", "texture"] and os.path.exists(self.selected_asset.file_path):
                self.preview_image.set_filename(self.selected_asset.file_path)
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
        self.animation_frames_model.remove_all()
        if self.selected_asset and isinstance(self.selected_asset, Animation):
            for frame in self.selected_asset.frames:
                self.animation_frames_model.append(StringGObject(frame))


    def refresh_asset_list(self):
        self.model.remove_all()
        for asset in self.project_manager.data.assets:
            self.model.append(AssetGObject(asset))
        self._update_visibility()

    def _update_visibility(self):
        has_assets = self.model.get_n_items() > 0
        if has_assets:
            self.main_stack.set_visible_child_name("grid")
        else:
            self.main_stack.set_visible_child_name("status")

    def on_import_asset(self, button):
        dialog = Gtk.FileChooserNative(title="Import Asset", transient_for=self.get_native(), action=Gtk.FileChooserAction.OPEN)
        dialog.set_select_multiple(True)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Image Files")
        file_filter.add_pixbuf_formats()
        dialog.add_filter(file_filter)

        dialog.connect("response", self.on_import_asset_response)
        dialog.show()

    def on_import_asset_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            files = dialog.get_files()
            try:
                if len(files) > 1: # Create animation
                    asset_name = os.path.basename(files[0].get_path()).split('.')[0]
                    new_anim = Animation(id=f"anim_{len(self.project_manager.data.assets)}", name=asset_name, asset_type="animation", file_path="", frame_count=len(files), frame_rate=10, frames=[])

                    anim_dir = os.path.join(self.project_manager.project_path, "Assets", asset_name)
                    os.makedirs(anim_dir, exist_ok=True)

                    for file in files:
                        filepath = file.get_path()
                        if not self.is_supported_image_file(filepath):
                            self.show_error_dialog(f"Unsupported file type: {os.path.basename(filepath)}")
                            continue
                        new_filepath = os.path.join(anim_dir, os.path.basename(filepath))
                        shutil.copy(filepath, new_filepath)
                        new_anim.frames.append(new_filepath)

                    self.project_manager.data.assets.append(new_anim)
                else: # Import single asset
                    file = files[0]
                    filepath = file.get_path()
                    if not self.is_supported_image_file(filepath):
                        self.show_error_dialog(f"Unsupported file type: {os.path.basename(filepath)}")
                        return
                    asset_name = os.path.basename(filepath)
                    asset_type = "sprite"

                    assets_dir = os.path.join(self.project_manager.project_path, "Assets")
                    os.makedirs(assets_dir, exist_ok=True)
                    new_filepath = os.path.join(assets_dir, asset_name)
                    shutil.copy(filepath, new_filepath)

                    new_asset = Asset(id=f"asset_{len(self.project_manager.data.assets)}", name=asset_name, asset_type=asset_type, file_path=new_filepath)
                    self.project_manager.data.assets.append(new_asset)

                self.project_manager.set_dirty()
                self.refresh_asset_list()
            except Exception as e:
                self.show_error_dialog(f"Error importing asset(s): {e}")

    def _on_frame_drag_prepare(self, source, x, y):
        list_item = source.get_widget().get_parent()
        frame_path_gobject = list_item.get_item()
        return Gdk.ContentProvider.new_for_value(frame_path_gobject)

    def _on_frame_drag_begin(self, source, drag):
        list_item = source.get_widget().get_parent()
        source.set_icon(Gtk.WidgetPaintable.new(list_item), 0, 0)

    def _on_frame_drop(self, target, value, x, y):
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

    def is_supported_image_file(self, filepath):
        supported_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        return any(filepath.lower().endswith(ext) for ext in supported_extensions)

    def show_error_dialog(self, message):
        dialog = Adw.MessageDialog(
            transient_for=self.get_native(),
            modal=True,
            heading="Error",
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: d.close())
        dialog.present()
