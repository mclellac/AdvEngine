"""The attribute editor for the AdvEngine application."""

import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Attribute, AttributeGObject
from ..core.project_manager import ProjectManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "attribute_editor.ui"))
class AttributeEditor(Gtk.Box):
    """A widget for editing attributes in a project."""
    __gtype_name__ = "AttributeEditor"

    add_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    column_view = Gtk.Template.Child()
    empty_state = Gtk.Template.Child()
    content_clamp = Gtk.Template.Child()

    def __init__(self, project_manager: ProjectManager, **kwargs):
        """Initializes a new AttributeEditor instance."""
        print("DEBUG: AttributeEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager

        self.model = self._setup_model()
        self.filter_model = self._setup_filter_model()
        self.selection = self._setup_selection_model()
        self._setup_column_view()
        self.column_view.set_model(self.selection)

        self._connect_signals()
        self._update_visibility()

    def _connect_signals(self):
        """Connects widget signals to handlers."""
        self.add_button.connect("clicked", self._on_add_clicked)
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.search_entry.connect("search-changed", self._on_search_changed)

    def _setup_model(self):
        """Sets up the data model for the editor."""
        print("DEBUG: AttributeEditor._setup_model")
        model = Gio.ListStore(item_type=AttributeGObject)
        for attribute in self.project_manager.data.attributes:
            model.append(AttributeGObject(attribute))
        model.connect("items-changed", self._update_visibility)
        return model

    def _setup_filter_model(self):
        """Sets up the filter model for the editor."""
        print("DEBUG: AttributeEditor._setup_filter_model")
        filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        filter_model.set_filter(self.filter)
        return filter_model

    def _setup_selection_model(self):
        """Sets up the selection model for the editor."""
        print("DEBUG: AttributeEditor._setup_selection_model")
        selection = Gtk.SingleSelection(model=self.filter_model)
        selection.connect("selection-changed", self._on_selection_changed)
        return selection

    def _setup_column_view(self):
        """Sets up the column view for the editor."""
        print("DEBUG: AttributeEditor._setup_column_view")
        columns_def = {
            "id": {"title": "ID", "expand": True},
            "name": {"title": "Name", "expand": True},
            "initial_value": {"title": "Initial Value", "expand": False},
            "max_value": {"title": "Max Value", "expand": False}
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_id)
            factory.connect("bind", self._bind_cell, col_id)
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(
                title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            self.column_view.append_column(column)

    def _setup_cell(self, factory, list_item, column_id):
        """Sets up a cell in the column view."""
        print(f"DEBUG: AttributeEditor._setup_cell: column_id={column_id}")
        if column_id in ["initial_value", "max_value"]:
            widget = Gtk.SpinButton(
                adjustment=Gtk.Adjustment(
                    lower=0, upper=99999, step_increment=1)
            )
        else:
            widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id):
        """Binds a cell to the data model."""
        attr_gobject = list_item.get_item()
        widget = list_item.get_child()
        print(f"DEBUG: AttributeEditor._bind_cell: column_id={column_id}, attr_id={attr_gobject.id}")

        list_item.bindings = []
        if isinstance(widget, Gtk.SpinButton):
            binding = widget.bind_property(
                "value", attr_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            list_item.bindings.append(binding)
            handler_id = widget.connect(
                "value-changed", lambda w: self.project_manager.set_dirty(True))
            list_item.handler_id = handler_id
        else:
            binding = widget.bind_property(
                "text", attr_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            list_item.bindings.append(binding)
            handler_id = widget.connect(
                "changed", lambda w: self.project_manager.set_dirty(True))
            list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell from the data model."""
        attr_gobject = list_item.get_item()
        print(f"DEBUG: AttributeEditor._unbind_cell: attr_id={attr_gobject.id if attr_gobject else 'N/A'}")
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            list_item.bindings = []
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry."""
        print(f"DEBUG: AttributeEditor._on_search_changed: {search_entry.get_text()}")
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query."""
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower())

    def _update_visibility(self, *args):
        """Updates the visibility of the main content and empty state."""
        has_items = self.model.get_n_items() > 0
        print(f"DEBUG: AttributeEditor._update_visibility: has_items={has_items}")
        self.content_clamp.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button."""
        print("DEBUG: AttributeEditor._on_add_clicked")
        new_id_base = "new_attribute"
        new_id = new_id_base
        count = 1
        existing_ids = {a.id for a in self.project_manager.data.attributes}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_attr_data = Attribute(
            id=new_id, name="New Attribute", initial_value=10, max_value=100)
        self.project_manager.add_attribute(new_attr_data)
        gobject = AttributeGObject(new_attr_data)
        self.model.append(gobject)

        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
            self.selection.set_selected(pos)

    def _on_delete_clicked(self, button):
        """Handles the clicked signal from the delete button."""
        print("DEBUG: AttributeEditor._on_delete_clicked")
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Attribute?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response,
                       selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, attr_gobject):
        """Handles the response from the delete confirmation dialog."""
        print(f"DEBUG: AttributeEditor._on_delete_dialog_response: response={response}")
        if response == "delete":
            if self.project_manager.remove_attribute(attr_gobject.attribute):
                is_found, pos = self.model.find(attr_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        print(f"DEBUG: AttributeEditor._on_selection_changed: is_selected={is_selected}")
        self.delete_button.set_sensitive(is_selected)
