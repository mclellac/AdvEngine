"""The character editor for the AdvEngine application."""

import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Character, CharacterGObject
from ..core.project_manager import ProjectManager


class CharacterManager(Adw.Bin):
    """A widget for editing characters in a project.

    This editor provides a table-like interface for creating, editing, and
    deleting characters, and includes a preview of the character's portrait.
    """
    EDITOR_NAME = "Characters"
    VIEW_NAME = "character_manager"
    ORDER = 8

    def __init__(self, project_manager: ProjectManager, **kwargs):
        """Initializes a new CharacterManager instance.

        Args:
            project_manager: The project manager instance.
        """
        print("DEBUG: CharacterManager.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager

        root_widget = self._build_ui()
        self.set_child(root_widget)

        self.model = self._setup_model()
        self.filter_model = self._setup_filter_model()
        self.selection = self._setup_selection_model()
        self.column_view.set_model(self.selection)

        self._update_visibility()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        print("DEBUG: CharacterManager._build_ui")
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.content_box.set_margin_top(12)
        self.content_box.set_margin_bottom(12)
        self.content_box.set_margin_start(12)
        self.content_box.set_margin_end(12)
        root_box.append(self.content_box)

        list_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=12, hexpand=True)
        self.content_box.append(list_box)

        header = Adw.HeaderBar()
        list_box.append(header)

        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Character")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Character")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Characters")
        self.search_entry.connect("search-changed", self._on_search_changed)
        list_box.append(self.search_entry)

        self.column_view = self._setup_column_view()
        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        list_box.append(scrolled_window)

        preview_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6, vexpand=False, hexpand=False)
        preview_box.set_size_request(256, -1)
        self.content_box.append(preview_box)

        preview_label = Gtk.Label(
            label="<b>Portrait Preview</b>", use_markup=True)
        preview_box.append(preview_label)

        self.portrait_preview = Gtk.Picture(content_fit=Gtk.ContentFit.CONTAIN)
        self.portrait_preview.set_size_request(-1, 256)
        preview_box.append(self.portrait_preview)

        self.empty_state = Adw.StatusPage(
            title="No Characters",
            description="Create a new character to get started.",
            icon_name="user-info-symbolic"
        )
        root_box.append(self.empty_state)

        return root_box

    def _setup_model(self):
        """Sets up the data model for the editor."""
        print("DEBUG: CharacterManager._setup_model")
        model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            model.append(CharacterGObject(character))
        model.connect("items-changed", self._update_visibility)
        return model

    def _setup_filter_model(self):
        """Sets up the filter model for the editor."""
        print("DEBUG: CharacterManager._setup_filter_model")
        filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(
            self._filter_func, self.search_entry)
        filter_model.set_filter(self.filter)
        return filter_model

    def _setup_selection_model(self):
        """Sets up the selection model for the editor."""
        print("DEBUG: CharacterManager._setup_selection_model")
        selection = Gtk.SingleSelection(model=self.filter_model)
        selection.connect("selection-changed", self._on_selection_changed)
        return selection

    def _setup_column_view(self):
        """Sets up the column view for the editor."""
        print("DEBUG: CharacterManager._setup_column_view")
        column_view = Gtk.ColumnView()
        self._create_columns(column_view)
        return column_view

    def _create_columns(self, column_view):
        """Creates and appends all columns to the ColumnView."""
        columns_def = {
            "id": {"title": "ID", "expand": True, "type": "text"},
            "display_name": {"title": "Display Name", "expand": True, "type": "text"},
            "is_merchant": {"title": "Is Merchant", "expand": False, "type": "switch"},
            "portrait_asset_id": {"title": "Portrait Asset", "expand": True, "type": "combo"}
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_info["type"])
            factory.connect("bind", self._bind_cell, col_id, col_info["type"])
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(
                title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            column_view.append_column(column)

    def _setup_cell(self, factory, list_item, cell_type):
        """Sets up a cell in the column view."""
        if cell_type == "switch":
            widget = Gtk.Switch(valign=Gtk.Align.CENTER)
        elif cell_type == "combo":
            image_assets = ["None"] + [asset.id for asset in self.project_manager.data.assets if asset.asset_type in [
                "sprite", "animation"]]
            widget = Gtk.DropDown.new_from_strings(image_assets)
        else:
            widget = Gtk.Entry(valign=Gtk.Align.CENTER)
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id, cell_type):
        """Binds a cell to the data model."""
        char_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.bindings = []

        if cell_type == "switch":
            binding = widget.bind_property("active", char_gobject, column_id,
                                 GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            handler_id = widget.connect(
                "notify::active", lambda w, _: self.project_manager.set_dirty(True))
        elif cell_type == "combo":
            model = widget.get_model()
            for i in range(model.get_n_items()):
                if model.get_string(i) == getattr(char_gobject, column_id, "None"):
                    widget.set_selected(i)
                    break
            handler_id = widget.connect(
                "notify::selected-item", self._on_combo_changed, char_gobject, column_id)
        else:
            binding = widget.bind_property("text", char_gobject, column_id,
                                 GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            handler_id = widget.connect(
                "changed", lambda w: self.project_manager.set_dirty(True))

        list_item.bindings.append(binding)
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell from the data model."""
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            del list_item.bindings
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_combo_changed(self, combo, _, char_gobject, column_id):
        """Handles the changed signal from a combo box cell."""
        selected_str = combo.get_selected_item().get_string() if combo.get_selected_item() else "None"
        setattr(char_gobject, column_id, selected_str)
        self.project_manager.set_dirty(True)
        self._update_preview()

    def _update_preview(self):
        """Updates the portrait preview."""
        print("DEBUG: CharacterManager._update_preview")
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            self.portrait_preview.set_filename(None)
            return

        asset_id = selected_item.portrait_asset_id
        if asset_id and asset_id != "None":
            asset = next(
                (a for a in self.project_manager.data.assets if a.id == asset_id), None)
            if asset and self.project_manager.project_path and os.path.exists(os.path.join(self.project_manager.project_path, asset.file_path)):
                print(f"DEBUG: Setting preview image to {asset.file_path}")
                self.portrait_preview.set_filename(os.path.join(
                    self.project_manager.project_path, asset.file_path))
            else:
                print("DEBUG: Asset not found or file path does not exist, clearing preview.")
                self.portrait_preview.set_filename(None)
        else:
            print("DEBUG: No asset ID, clearing preview.")
            self.portrait_preview.set_filename(None)

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry."""
        print(f"DEBUG: CharacterManager._on_search_changed: {search_entry.get_text()}")
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query."""
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.display_name.lower())

    def _update_visibility(self, *args):
        """Updates the visibility of the main content and empty state."""
        has_items = self.model.get_n_items() > 0
        print(f"DEBUG: CharacterManager._update_visibility: has_items={has_items}")
        self.content_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button."""
        print("DEBUG: CharacterManager._on_add_clicked")
        new_id_base = "new_char"
        new_id = new_id_base
        count = 1
        existing_ids = {c.id for c in self.project_manager.data.characters}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_char_data = Character(id=new_id, display_name="New Character",
                                  dialogue_start_id="", is_merchant=False, shop_id="", portrait_asset_id="None")
        self.project_manager.add_character(new_char_data)
        gobject = CharacterGObject(new_char_data)
        self.model.append(gobject)

        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
            self.selection.set_selected(pos)

    def _on_delete_clicked(self, button):
        """Handles the clicked signal from the delete button."""
        print("DEBUG: CharacterManager._on_delete_clicked")
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Character?",
            body=f"Are you sure you want to delete '{selected_item.display_name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response,
                       selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        """Handles the response from the delete confirmation dialog."""
        print(f"DEBUG: CharacterManager._on_delete_dialog_response: response={response}")
        if response == "delete":
            if self.project_manager.remove_character(char_gobject.character):
                is_found, pos = self.model.find(char_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        print(f"DEBUG: CharacterManager._on_selection_changed: is_selected={is_selected}")
        self.delete_button.set_sensitive(is_selected)
        self._update_preview()
