import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject
import os
import shutil
from ..core.data_schemas import Asset

class AssetGObject(GObject.Object):
    __gtype_name__ = 'AssetGObject'
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    asset_type = GObject.Property(type=str)
    file_path = GObject.Property(type=str)

    def __init__(self, asset):
        super().__init__()
        self.id = asset.id
        self.name = asset.name
        self.asset_type = asset.asset_type
        self.file_path = asset.file_path
        self.asset_data = asset

class AssetEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(250, -1)

        self.model = Gio.ListStore(item_type=AssetGObject)
        self.refresh_asset_list()

        self.asset_list_view = Gtk.ColumnView()
        self.asset_list_view.set_model(Gtk.SingleSelection(model=self.model))
        self._create_column("ID", lambda asset: asset.id)
        self._create_column("Name", lambda asset: asset.name)
        self._create_column("Type", lambda asset: asset.asset_type)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.asset_list_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        left_panel.append(scrolled_window)

        import_button = Gtk.Button(label="Import Asset")
        import_button.set_tooltip_text("Import a new image asset into the project")
        import_button.connect("clicked", self.on_import_asset)
        left_panel.append(import_button)
        self.append(left_panel)

        preview_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        preview_pane.set_hexpand(True)

        self.append(preview_pane)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.asset_list_view.append_column(col)

    def refresh_asset_list(self):
        self.model.remove_all()
        for asset in self.project_manager.data.assets:
            self.model.append(AssetGObject(asset))

    def on_import_asset(self, button):
        dialog = Gtk.FileChooserDialog(title="Import Asset", transient_for=self.get_native(), action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.OK)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Image Files")
        file_filter.add_pixbuf_formats()
        dialog.add_filter(file_filter)

        dialog.show()

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                file = dialog.get_file()
                filepath = file.get_path()
                asset_name = os.path.basename(filepath)
                asset_type = "sprite" # Simple assumption for now

                # Copy file to project's assets directory
                assets_dir = os.path.join(self.project_manager.project_path, "Assets")
                os.makedirs(assets_dir, exist_ok=True)
                new_filepath = os.path.join(assets_dir, asset_name)
                shutil.copy(filepath, new_filepath)

                new_asset = Asset(id=f"asset_{len(self.project_manager.data.assets)}", name=asset_name, asset_type=asset_type, file_path=new_filepath)
                self.project_manager.data.assets.append(new_asset)
                self.project_manager.set_dirty()
                self.refresh_asset_list()
            dialog.destroy()

        dialog.connect("response", on_response)
