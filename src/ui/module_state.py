"""The global state editor for the AdvEngine application.

This module defines the GlobalStateEditor, a widget for managing global
variables that control the game's state.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.schemas.global_state import GlobalVariable, GlobalVariableGObject
from ..core.project_manager import ProjectManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_state.ui"))
class GlobalStateEditor(Gtk.Box):
    """A widget for editing global variables.

    This editor provides a spreadsheet-like interface for creating, editing,
    and deleting global variables used in the game's logic.

    Attributes:
        project_manager (ProjectManager): The main project manager instance.
        settings_manager: The main settings manager instance.
        model (Gio.ListStore): The data store for all global variables.
        filter_model (Gtk.FilterListModel): The filter model for search.
        selection (Gtk.SingleSelection): The selection model for the
            column view.
    """

    __gtype_name__ = "GlobalStateEditor"

    EDITOR_NAME = "Global State"
    VIEW_NAME = "global_state_editor"
    ORDER = 7

    add_button: Gtk.Button = Gtk.Template.Child()
    delete_button: Gtk.Button = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    column_view: Gtk.ColumnView = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()

    def __init__(self, project_manager: ProjectManager, settings_manager, **kwargs):
        """Initializes a new GlobalStateEditor instance.

        Args:
            project_manager (ProjectManager): The project manager instance.
            settings_manager: The settings manager instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager

        self._setup_column_view()
        self._connect_signals()
        self.project_manager.register_project_loaded_callback(self.project_loaded)

    def project_loaded(self):
        """Callback for when the project is loaded."""
        self.model = self._setup_model()
        self.filter_model = self._setup_filter_model()
        self.selection = self._setup_selection_model()
        self.column_view.set_model(self.selection)
        self._update_visibility()

    def _connect_signals(self):
        """Connects widget signals to handlers."""
        self.add_button.connect("clicked", self._on_add_clicked)
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.search_entry.connect("search-changed", self._on_search_changed)

    def _setup_model(self):
        """Sets up the data model for the editor.

        Returns:
            Gio.ListStore: The new list store.
        """
        model = Gio.ListStore(item_type=GlobalVariableGObject)
        for var in self.project_manager.data.global_variables:
            model.append(GlobalVariableGObject(var))
        model.connect("items-changed", self._update_visibility)
        return model

    def _setup_filter_model(self):
        """Sets up the filter model for search functionality.

        Returns:
            Gtk.FilterListModel: The new filter list model.
        """
        filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        filter_model.set_filter(self.filter)
        return filter_model

    def _setup_selection_model(self):
        """Sets up the selection model for the column view.

        Returns:
            Gtk.SingleSelection: The new single selection model.
        """
        selection = Gtk.SingleSelection(model=self.filter_model)
        selection.connect("selection-changed", self._on_selection_changed)
        return selection

    def _setup_column_view(self):
        """Sets up the columns for the Gtk.ColumnView."""
        self._create_columns(self.column_view)

    def _create_columns(self, column_view):
        """Creates and appends all columns to the ColumnView.

        Args:
            column_view (Gtk.ColumnView): The view to add columns to.
        """
        columns_def = {
            "id": {"title": "ID", "expand": True, "type": "text"},
            "name": {"title": "Name", "expand": True, "type": "text"},
            "category": {"title": "Category", "expand": True, "type": "text"},
            "type": {"title": "Type", "expand": False, "type": "combo"},
            "initial_value": {
                "title": "Initial Value",
                "expand": True,
                "type": "text",
            },
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
            column = Gtk.ColumnViewColumn(title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            column_view.append_column(column)

    def _setup_text_cell(self, factory, list_item):
        """Sets up a text cell in the column view.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to set up.
        """
        widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_text_cell(self, factory, list_item, column_id):
        """Binds a text cell to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to bind.
            column_id (str): The ID of the property to bind.
        """
        var_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.bindings = [
            widget.bind_property(
                "text",
                var_gobject,
                column_id,
                GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
            )
        ]
        list_item.handler_id = widget.connect(
            "changed", self._on_value_changed, var_gobject
        )

    def _setup_type_cell(self, factory, list_item):
        """Sets up a type dropdown cell in the column view.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to set up.
        """
        widget = Gtk.DropDown.new_from_strings(["bool", "int", "str"])
        list_item.set_child(widget)

    def _bind_type_cell(self, factory, list_item):
        """Binds a type dropdown cell to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to bind.
        """
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

        handler_id = widget.connect(
            "notify::selected", self._on_type_changed, var_gobject
        )
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell from the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to unbind.
        """
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            del list_item.bindings
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_value_changed(self, widget, var_gobject: GlobalVariableGObject):
        """Handles the value-changed signal from a cell.

        Args:
            widget (Gtk.Widget): The widget that emitted the signal.
            var_gobject (GlobalVariableGObject): The GObject wrapper for the
                variable.
        """
        self.project_manager.set_dirty(True)

    def _on_type_changed(self, dropdown, pspec, var_gobject: GlobalVariableGObject):
        """Handles the 'selected' signal from the type dropdown.

        Args:
            dropdown (Gtk.DropDown): The dropdown that emitted the signal.
            pspec: The GObject property spec (unused).
            var_gobject (GlobalVariableGObject): The GObject wrapper for the
                variable.
        """
        selected_str = dropdown.get_selected_item().get_string()
        var_gobject.set_property("type", selected_str)
        self.project_manager.set_dirty(True)

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry.

        Args:
            search_entry (Gtk.SearchEntry): The search entry.
        """
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query.

        Args:
            item (GlobalVariableGObject): The item to filter.
            search_entry (Gtk.SearchEntry): The search entry.

        Returns:
            bool: True if the item should be visible, False otherwise.
        """
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (
            search_text in item.id.lower()
            or search_text in item.name.lower()
            or search_text in item.category.lower()
        )

    def _update_visibility(self, *args):
        """Switches the view based on whether there are items."""
        if self.model.get_n_items() > 0:
            self.stack.set_visible_child_name("content")
        else:
            self.stack.set_visible_child_name("empty")

    def _on_add_clicked(self, button):
        """Handles the 'Add' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        new_id_base = "new_variable"
        new_id = new_id_base
        count = 1
        existing_ids = {v.id for v in self.project_manager.data.global_variables}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_var_data = GlobalVariable(
            id=new_id,
            name="New Variable",
            type="bool",
            initial_value=False,
            category="Default",
        )
        self.project_manager.add_data_item("global_variables", new_var_data)
        gobject = GlobalVariableGObject(new_var_data)
        self.model.append(gobject)

        for i in range(self.filter_model.get_n_items()):
            if self.filter_model.get_item(i) == gobject:
                self.selection.set_selected(i)
                self.column_view.scroll_to(i, None, False, 0.0, 0.0)
                break

    def _on_delete_clicked(self, button):
        """Handles the 'Delete' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Variable?",
            body=f"Are you sure you want to delete '{selected_item.name}'?",
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, var_gobject):
        """Handles the response from the delete confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog.
            response (str): The response ID.
            var_gobject (GlobalVariableGObject): The variable to delete.
        """
        if response == "delete":
            var_data = var_gobject.variable
            if self.project_manager.remove_data_item("global_variables", var_data):
                is_found, pos = self.model.find(var_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model.

        Args:
            selection_model (Gtk.SingleSelection): The selection model.
            position (int): The position of the selected item.
            n_items (int): The number of items in the model.
        """
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
