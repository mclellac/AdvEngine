import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Character, CharacterGObject
from ..core.project_manager import ProjectManager

class CharacterManager(Gtk.Box):
    """A widget for editing characters in a project, using a ColumnView for a
    structured editing experience and including a portrait preview."""

    def __init__(self, project_manager: ProjectManager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.project_manager = project_manager

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        # --- Main content box ---
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, hexpand=True)
        self.append(self.main_box)

        header = Adw.HeaderBar()
        self.main_box.append(header)

        # --- Toolbar ---
        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Character")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Character")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Search ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Characters")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Model ---
        self.model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            self.model.append(CharacterGObject(character))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        self.filter_model.set_filter(self.filter)

        self.selection = Gtk.SingleSelection(model=self.filter_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        # --- Column View ---
        self.column_view = Gtk.ColumnView(model=self.selection)
        self.column_view.set_vexpand(True)
        self.column_view.set_css_classes(["boxed-list"])
        self._create_columns()

        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scrolled_window)

        # --- Portrait Preview ---
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, vexpand=False, hexpand=False)
        preview_box.set_size_request(256, -1)
        self.append(preview_box)

        preview_label = Gtk.Label(label="<b>Portrait Preview</b>", use_markup=True)
        preview_box.append(preview_label)

        self.portrait_preview = Gtk.Picture(content_fit=Gtk.ContentFit.CONTAIN)
        self.portrait_preview.set_size_request(-1, 256)
        preview_box.append(self.portrait_preview)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Characters",
            description="Create a new character to get started.",
            icon_name="user-info-symbolic"
        )
        # This will be shown/hidden by swapping the main content box
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _create_columns(self):
        # ID Column
        id_factory = Gtk.SignalListItemFactory()
        id_factory.connect("setup", self._setup_cell, "text")
        id_factory.connect("bind", self._bind_cell, "id", "text")
        id_column = Gtk.ColumnViewColumn(title="ID", factory=id_factory)
        self.column_view.append_column(id_column)

        # Display Name Column
        name_factory = Gtk.SignalListItemFactory()
        name_factory.connect("setup", self._setup_cell, "text")
        name_factory.connect("bind", self._bind_cell, "display_name", "text")
        name_column = Gtk.ColumnViewColumn(title="Display Name", factory=name_factory)
        name_column.set_expand(True)
        self.column_view.append_column(name_column)

        # Is Merchant Column
        merchant_factory = Gtk.SignalListItemFactory()
        merchant_factory.connect("setup", self._setup_cell, "switch")
        merchant_factory.connect("bind", self._bind_cell, "is_merchant", "switch")
        merchant_column = Gtk.ColumnViewColumn(title="Is Merchant", factory=merchant_factory)
        self.column_view.append_column(merchant_column)

        # Portrait Asset Column
        portrait_factory = Gtk.SignalListItemFactory()
        portrait_factory.connect("setup", self._setup_cell, "combo")
        portrait_factory.connect("bind", self._bind_cell, "portrait_asset_id", "combo")
        portrait_column = Gtk.ColumnViewColumn(title="Portrait Asset", factory=portrait_factory)
        portrait_column.set_expand(True)
        self.column_view.append_column(portrait_column)

    def _setup_cell(self, factory, list_item, cell_type):
        if cell_type == "switch":
            widget = Gtk.Switch(valign=Gtk.Align.CENTER)
        elif cell_type == "combo":
            image_assets = ["None"] + [asset.id for asset in self.project_manager.data.assets if asset.asset_type in ["sprite", "animation"]]
            widget = Gtk.DropDown.new_from_strings(image_assets)
        else: # text
            widget = Gtk.Entry(valign=Gtk.Align.CENTER)
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id, cell_type):
        char_gobject = list_item.get_item()
        widget = list_item.get_child()

        if cell_type == "switch":
            widget.bind_property("active", char_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            handler_id = widget.connect("notify::active", lambda w, _: self.project_manager.set_dirty(True))
        elif cell_type == "combo":
            model = widget.get_model()
            for i in range(model.get_n_items()):
                if model.get_string(i) == getattr(char_gobject, column_id, "None"):
                    widget.set_selected(i)
                    break
            handler_id = widget.connect("notify::selected-item", self._on_combo_changed, char_gobject, column_id)
        else: # text
            widget.bind_property("text", char_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            handler_id = widget.connect("changed", lambda w: self.project_manager.set_dirty(True))

        list_item.disconnect_handler = handler_id

    def _on_combo_changed(self, combo, _, char_gobject, column_id):
        selected_str = combo.get_selected_item().get_string() if combo.get_selected_item() else "None"
        setattr(char_gobject, column_id, selected_str)
        self.project_manager.set_dirty(True)

    def _update_preview(self):
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            self.portrait_preview.set_filename(None)
            return

        asset_id = selected_item.portrait_asset_id
        if asset_id and asset_id != "None":
            asset = next((a for a in self.project_manager.data.assets if a.id == asset_id), None)
            if asset and self.project_manager.project_path and os.path.exists(os.path.join(self.project_manager.project_path, asset.file_path)):
                self.portrait_preview.set_filename(os.path.join(self.project_manager.project_path, asset.file_path))
            else:
                self.portrait_preview.set_filename(None)
        else:
            self.portrait_preview.set_filename(None)

    def _on_search_changed(self, search_entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        search_text = search_entry.get_text().lower()
        if not search_text: return True
        return (search_text in item.id.lower() or
                search_text in item.display_name.lower())

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.get_parent().set_visible(has_items) # The HBox
        self.empty_state.set_visible(not has_items)


    def _on_add_clicked(self, button):
        new_id_base = "new_char"
        new_id = new_id_base
        count = 1
        existing_ids = {c.id for c in self.project_manager.data.characters}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_char_data = Character(id=new_id, display_name="New Character", dialogue_start_id="", is_merchant=False, shop_id="", portrait_asset_id="None")
        self.project_manager.add_character(new_char_data)
        gobject = CharacterGObject(new_char_data)
        self.model.append(gobject)

        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
             self.selection.set_selected(pos)

    def _on_delete_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if not selected_item: return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Character?",
            body=f"Are you sure you want to delete '{selected_item.display_name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        if response == "delete":
            if self.project_manager.remove_character(char_gobject.character_data):
                is_found, pos = self.model.find(char_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        self.delete_button.set_sensitive(selection_model.get_selected() != Gtk.INVALID_LIST_POSITION)
        self._update_preview()
