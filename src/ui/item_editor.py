import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Item, ItemGObject
from ..core.project_manager import ProjectManager

class ItemEditor(Gtk.Box):
    """A widget for editing items in a project, using a ColumnView for a
    structured editing experience."""

    def __init__(self, project_manager: ProjectManager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.project_manager = project_manager

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)

        clamp = Adw.Clamp()
        clamp.set_child(self.main_box)
        self.append(clamp)

        header = Adw.HeaderBar()
        self.main_box.append(header)

        # --- Toolbar ---
        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Item")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Item")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Search ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Items")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Model ---
        self.model = Gio.ListStore(item_type=ItemGObject)
        for item in self.project_manager.data.items:
            self.model.append(ItemGObject(item))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        self.filter_model.set_filter(self.filter)

        self.selection = Gtk.SingleSelection(model=self.filter_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        # --- Column View ---
        self.column_view = Gtk.ColumnView(model=self.selection)
        self.column_view.set_vexpand(True)
        self.column_view.set_css_classes(["boxed-list"])

        # Define columns
        columns_def = {
            "id": {"title": "ID", "expand": True, "type": "text"},
            "name": {"title": "Name", "expand": True, "type": "text"},
            "type": {"title": "Type", "expand": True, "type": "text"},
            "buy_price": {"title": "Buy Price", "expand": False, "type": "numeric"},
            "sell_price": {"title": "Sell Price", "expand": False, "type": "numeric"},
            "description": {"title": "Description", "expand": True, "type": "text"}
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_info["type"])
            factory.connect("bind", self._bind_cell, col_id, col_info["type"])
            column = Gtk.ColumnViewColumn(title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            self.column_view.append_column(column)

        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Items",
            description="Create a new item to get started.",
            icon_name="edit-find-replace-symbolic"
        )
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _setup_cell(self, factory, list_item, cell_type):
        if cell_type == "numeric":
            widget = Adw.SpinRow()
            widget.set_adjustment(Gtk.Adjustment(lower=-1, upper=99999, step_increment=1))
        else: # text
            widget = Adw.EntryRow()
            widget.set_show_apply_button(True)
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id, cell_type):
        item_gobject = list_item.get_item()
        widget = list_item.get_child()

        prop_name = "value" if cell_type == "numeric" else "text"
        binding = widget.bind_property(prop_name, item_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        handler_id = None
        if isinstance(widget, Adw.EntryRow):
            validation_handler = lambda w, _: self._validate_entry(w, item_gobject, column_id)
            handler_id = widget.connect("notify::text", validation_handler)
            widget.connect("apply", lambda w: self.project_manager.set_dirty(True))
            self._validate_entry(widget, item_gobject, column_id) # Initial validation
        elif isinstance(widget, Adw.SpinRow):
            handler_id = widget.connect("notify::value", lambda w, _: self.project_manager.set_dirty(True))

        # Store bindings and handlers to manage their lifecycle
        if not hasattr(list_item, 'bindings'):
            list_item.bindings = []
            list_item.handler_ids = []
        list_item.bindings.append(binding)
        list_item.handler_ids.append(handler_id)

    def _validate_entry(self, entry_row, item_gobject, column_id):
        is_valid = True
        text = entry_row.get_text()

        if not text.strip():
            is_valid = False
        elif column_id == "id":
             # Check for duplicates, ignoring the current item
             is_duplicate = any(item.id == text for item in self.project_manager.data.items if item != item_gobject.item)
             if is_duplicate:
                 is_valid = False

        if is_valid:
            entry_row.remove_css_class("error")
        else:
            entry_row.add_css_class("error")
        entry_row.set_property("show_apply_button", is_valid)

    def _on_search_changed(self, search_entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower() or
                search_text in item.type.lower())

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        new_id_base = "new_item"
        new_id = new_id_base
        count = 1
        existing_ids = {i.id for i in self.project_manager.data.items}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_item_data = Item(id=new_id, name="New Item", type="Misc", description="", buy_price=0, sell_price=0)
        self.project_manager.add_item(new_item_data)
        gobject = ItemGObject(new_item_data)
        self.model.append(gobject)

        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
             self.selection.set_selected(pos)

    def _on_delete_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Item?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, item_gobject):
        if response == "delete":
            if self.project_manager.remove_item(item_gobject.item):
                is_found, pos = self.model.find(item_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
