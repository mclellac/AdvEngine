import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import GlobalVariable, GlobalVariableGObject
from ..core.project_manager import ProjectManager

class GlobalStateEditor(Gtk.Box):
    """A widget for editing global variables, using a ColumnView for a
    structured, inline editing experience."""
    EDITOR_NAME = "Global State"
    VIEW_NAME = "global_state_editor"
    ORDER = 7

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
        self.add_button.set_tooltip_text("Add New Variable")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Variable")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Search ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Variables")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Model ---
        self.model = Gio.ListStore(item_type=GlobalVariableGObject)
        for var in self.project_manager.data.global_variables:
            self.model.append(GlobalVariableGObject(var))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        self.filter_model.set_filter(self.filter)

        self.selection = Gtk.SingleSelection(model=self.filter_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        # --- Column View ---
        self.column_view = Gtk.ColumnView(model=self.selection)
        self.column_view.set_vexpand(True)
        self._create_columns()

        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Global Variables",
            description="Create a new variable to manage game state.",
            icon_name="preferences-system-symbolic"
        )
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _create_columns(self):
        """Create and append all columns to the ColumnView."""
        # ID Column
        id_factory = Gtk.SignalListItemFactory()
        id_factory.connect("setup", self._setup_text_cell)
        id_factory.connect("bind", self._bind_text_cell, "id")
        id_column = Gtk.ColumnViewColumn(title="ID", factory=id_factory)
        id_column.set_expand(True)
        self.column_view.append_column(id_column)

        # Name Column
        name_factory = Gtk.SignalListItemFactory()
        name_factory.connect("setup", self._setup_text_cell)
        name_factory.connect("bind", self._bind_text_cell, "name")
        name_column = Gtk.ColumnViewColumn(title="Name", factory=name_factory)
        name_column.set_expand(True)
        self.column_view.append_column(name_column)

        # Category Column
        category_factory = Gtk.SignalListItemFactory()
        category_factory.connect("setup", self._setup_text_cell)
        category_factory.connect("bind", self._bind_text_cell, "category")
        category_column = Gtk.ColumnViewColumn(title="Category", factory=category_factory)
        category_column.set_expand(True)
        self.column_view.append_column(category_column)

        # Type Column
        type_factory = Gtk.SignalListItemFactory()
        type_factory.connect("setup", self._setup_type_cell)
        type_factory.connect("bind", self._bind_type_cell)
        type_column = Gtk.ColumnViewColumn(title="Type", factory=type_factory)
        self.column_view.append_column(type_column)

        # Initial Value Column
        value_factory = Gtk.SignalListItemFactory()
        value_factory.connect("setup", self._setup_text_cell)
        value_factory.connect("bind", self._bind_text_cell, "initial_value_str")
        value_column = Gtk.ColumnViewColumn(title="Initial Value", factory=value_factory)
        value_column.set_expand(True)
        self.column_view.append_column(value_column)

    def _setup_text_cell(self, factory, list_item):
        entry = Adw.EntryRow()
        entry.set_show_apply_button(True)
        list_item.set_child(entry)

    def _bind_text_cell(self, factory, list_item, column_id):
        var_gobject = list_item.get_item()
        entry = list_item.get_child()
        entry.bind_property("text", var_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        handler_id = entry.connect("apply", self._on_value_changed, var_gobject)
        list_item.disconnect_handler = handler_id

    def _setup_type_cell(self, factory, list_item):
        combo = Adw.ComboRow(model=Gtk.StringList.new(["bool", "int", "str"]))
        list_item.set_child(combo)

    def _bind_type_cell(self, factory, list_item):
        var_gobject = list_item.get_item()
        combo = list_item.get_child()

        # Custom binding for ComboRow
        def update_combo_from_gobject(*args):
            type_str = var_gobject.get_property("type")
            if type_str == "bool": combo.set_selected(0)
            elif type_str == "int": combo.set_selected(1)
            else: combo.set_selected(2)

        def update_gobject_from_combo(*args):
            selected_str = combo.get_selected_item().get_string()
            var_gobject.set_property("type", selected_str)
            self._on_value_changed(combo, var_gobject)

        update_combo_from_gobject()
        gobject_handler_id = var_gobject.connect("notify::type", update_combo_from_gobject)
        combo_handler_id = combo.connect("notify::selected", update_gobject_from_combo)

        list_item.disconnect_handlers = [
            (var_gobject, gobject_handler_id),
            (combo, combo_handler_id)
        ]

    def _on_value_changed(self, widget, var_gobject: GlobalVariableGObject):
        """Callback to update the underlying data and mark project as dirty."""
        self.project_manager.update_global_variable(var_gobject.variable_data, var_gobject)
        self.project_manager.set_dirty(True)

    def _on_search_changed(self, search_entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower() or
                search_text in item.category.lower())

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        new_id_base = "new_variable"
        new_id = new_id_base
        count = 1
        existing_ids = {v.id for v in self.project_manager.data.global_variables}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_var_data = GlobalVariable(id=new_id, name="New Variable", type="bool", initial_value=False, category="Default")
        self.project_manager.add_global_variable(new_var_data)
        gobject = GlobalVariableGObject(new_var_data)
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
            heading="Delete Variable?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, var_gobject):
        if response == "delete":
            if self.project_manager.remove_global_variable(var_gobject.variable_data):
                is_found, pos = self.model.find(var_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
