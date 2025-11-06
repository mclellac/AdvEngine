"""The global state editor for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import GlobalVariable, GlobalVariableGObject
from ..core.project_manager import ProjectManager


class GlobalStateEditor(Adw.Bin):
    """A widget for editing global variables.

    This editor provides a table-like interface for creating, editing, and
    deleting global variables. It includes features for searching and
    sorting.
    """
    EDITOR_NAME = "Global State"
    VIEW_NAME = "global_state_editor"
    ORDER = 7

    def __init__(self, project_manager: ProjectManager, **kwargs):
        """Initializes a new GlobalStateEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        print("DEBUG: GlobalStateEditor.__init__")
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
        print("DEBUG: GlobalStateEditor._build_ui")
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.content_clamp = Adw.Clamp()
        root_box.append(self.content_clamp)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        self.content_clamp.set_child(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Variable")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Variable")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Variables")
        self.search_entry.connect("search-changed", self._on_search_changed)
        main_box.append(self.search_entry)

        self.column_view = self._setup_column_view()
        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(scrolled_window)

        self.empty_state = Adw.StatusPage(
            title="No Global Variables",
            description="Create a new variable to manage game state.",
            icon_name="preferences-system-symbolic"
        )
        root_box.append(self.empty_state)

        return root_box

    def _setup_model(self):
        """Sets up the data model for the editor."""
        print("DEBUG: GlobalStateEditor._setup_model")
        model = Gio.ListStore(item_type=GlobalVariableGObject)
        for var in self.project_manager.data.global_variables:
            model.append(GlobalVariableGObject(var))
        model.connect("items-changed", self._update_visibility)
        return model

    def _setup_filter_model(self):
        """Sets up the filter model for the editor."""
        print("DEBUG: GlobalStateEditor._setup_filter_model")
        filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        filter_model.set_filter(self.filter)
        return filter_model

    def _setup_selection_model(self):
        """Sets up the selection model for the editor."""
        print("DEBUG: GlobalStateEditor._setup_selection_model")
        selection = Gtk.SingleSelection(model=self.filter_model)
        selection.connect("selection-changed", self._on_selection_changed)
        return selection

    def _setup_column_view(self):
        """Sets up the column view for the editor."""
        print("DEBUG: GlobalStateEditor._setup_column_view")
        column_view = Gtk.ColumnView()
        self._create_columns(column_view)
        return column_view

    def _create_columns(self, column_view):
        """Creates and appends all columns to the ColumnView."""
        columns_def = {
            "id": {"title": "ID", "expand": True, "type": "text"},
            "name": {"title": "Name", "expand": True, "type": "text"},
            "category": {"title": "Category", "expand": True, "type": "text"},
            "type": {"title": "Type", "expand": False, "type": "combo"},
            "initial_value_str": {"title": "Initial Value", "expand": True, "type": "text"}
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            if col_info["type"] == "combo":
                factory.connect("setup", self._setup_type_cell)
                factory.connect("bind", self._bind_type_cell)
            else:
                factory.connect("setup", self._setup_text_cell)
                factory.connect("bind", self._bind_text_cell, col_id)
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(
                title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            column_view.append_column(column)

    def _setup_text_cell(self, factory, list_item):
        """Sets up a text cell in the column view."""
        widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_text_cell(self, factory, list_item, column_id):
        """Binds a text cell to the data model."""
        var_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.bindings = [
            widget.bind_property(
                "text", var_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        ]
        list_item.handler_id = widget.connect(
            "changed", self._on_value_changed, var_gobject)

    def _setup_type_cell(self, factory, list_item):
        """Sets up a type cell in the column view."""
        widget = Gtk.DropDown.new_from_strings(["bool", "int", "str"])
        list_item.set_child(widget)

    def _bind_type_cell(self, factory, list_item):
        """Binds a type cell to the data model."""
        var_gobject = list_item.get_item()
        widget = list_item.get_child()

        def update_combo_from_gobject(*args):
            type_str = var_gobject.get_property("type")
            if type_str == "bool":
                widget.set_selected(0)
            elif type_str == "int":
                widget.set_selected(1)
            else:
                widget.set_selected(2)

        update_combo_from_gobject()

        handler_id = widget.connect("notify::selected", self._on_type_changed, var_gobject)
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

    def _on_value_changed(self, widget, var_gobject: GlobalVariableGObject):
        """Handles the value-changed signal from a cell."""
        self.project_manager.update_global_variable(
            var_gobject.variable, var_gobject)

    def _on_type_changed(self, dropdown, pspec, var_gobject: GlobalVariableGObject):
        """Handles the selected signal from the type dropdown."""
        selected_str = dropdown.get_selected_item().get_string()
        var_gobject.set_property("type", selected_str)
        self.project_manager.update_global_variable(
            var_gobject.variable, var_gobject)

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry."""
        print(f"DEBUG: GlobalStateEditor._on_search_changed: {search_entry.get_text()}")
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query."""
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower() or
                search_text in item.category.lower())

    def _update_visibility(self, *args):
        """Updates the visibility of the main content and empty state."""
        has_items = self.model.get_n_items() > 0
        print(f"DEBUG: GlobalStateEditor._update_visibility: has_items={has_items}")
        self.content_clamp.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button."""
        print("DEBUG: GlobalStateEditor._on_add_clicked")
        new_id_base = "new_variable"
        new_id = new_id_base
        count = 1
        existing_ids = {
            v.id for v in self.project_manager.data.global_variables}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_var_data = GlobalVariable(
            id=new_id, name="New Variable", type="bool", initial_value=False, category="Default")
        self.project_manager.add_global_variable(new_var_data)
        gobject = GlobalVariableGObject(new_var_data)
        self.model.append(gobject)

        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
            self.selection.set_selected(pos)

    def _on_delete_clicked(self, button):
        """Handles the clicked signal from the delete button."""
        print("DEBUG: GlobalStateEditor._on_delete_clicked")
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Variable?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response,
                       selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, var_gobject):
        """Handles the response from the delete confirmation dialog."""
        print(f"DEBUG: GlobalStateEditor._on_delete_dialog_response: response={response}")
        if response == "delete":
            if self.project_manager.remove_global_variable(var_gobject.variable):
                is_found, pos = self.model.find(var_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        print(f"DEBUG: GlobalStateEditor._on_selection_changed: is_selected={is_selected}")
        self.delete_button.set_sensitive(is_selected)
