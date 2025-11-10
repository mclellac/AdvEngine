"""The item editor for the AdvEngine application."""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.schemas.item import Item, ItemGObject
from ..core.project_manager import ProjectManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "item_editor.ui"))
class ItemEditor(Gtk.Box):
    """A widget for editing items in a project.

    This editor provides a user interface for creating, editing, and deleting
    items within an AdvEngine project. It uses a Gtk.ColumnView to display
    the items in a table format, with inline editing capabilities.

    Attributes:
        add_button (Gtk.Button): The button for adding a new item.
        delete_button (Gtk.Button): The button for deleting the selected item.
        search_entry (Gtk.SearchEntry): The entry for filtering items.
        column_view (Gtk.ColumnView): The view for displaying the items.
        stack (Gtk.Stack): The stack for switching between the content and empty view.
    """

    __gtype_name__ = "ItemEditor"

    add_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    column_view = Gtk.Template.Child()
    stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new ItemEditor instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        project_manager = kwargs.pop("project_manager")
        settings_manager = kwargs.pop("settings_manager")
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager

        self.model = self._setup_model()
        self.filter_model = self._setup_filter_model()
        self.selection = self._setup_selection_model()
        self._setup_column_view()
        self.column_view.set_model(self.selection)

        self._connect_signals()
        self._update_visibility()
        self.project_manager.register_project_loaded_callback(self.project_loaded)

    def project_loaded(self):
        """Callback for when the project is loaded."""
        self.model = self._setup_model()
        self.filter_model.set_model(self.model)
        self._update_visibility()

    def _connect_signals(self):
        """Connects widget signals to their respective handlers."""
        self.add_button.connect("clicked", self._on_add_clicked)
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.search_entry.connect("search-changed", self._on_search_changed)

    def _setup_model(self):
        """Sets up the data model for the editor.

        Returns:
            Gio.ListStore: The list store for the items.
        """
        model = Gio.ListStore(item_type=ItemGObject)
        for item in self.project_manager.data.items:
            model.append(ItemGObject(item))
        model.connect("items-changed", self._update_visibility)
        return model

    def _setup_filter_model(self):
        """Sets up the filter model for the editor.

        Returns:
            Gtk.FilterListModel: The filter list model for the items.
        """
        filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        filter_model.set_filter(self.filter)
        return filter_model

    def _setup_selection_model(self):
        """Sets up the selection model for the editor.

        Returns:
            Gtk.SingleSelection: The single selection model for the items.
        """
        selection = Gtk.SingleSelection(model=self.filter_model)
        selection.connect("selection-changed", self._on_selection_changed)
        return selection

    def _setup_column_view(self):
        """Sets up the column view for the editor."""
        columns_def = {
            "id": {"title": "ID", "expand": True, "type": "text"},
            "name": {"title": "Name", "expand": True, "type": "text"},
            "type": {"title": "Type", "expand": True, "type": "text"},
            "buy_price": {"title": "Buy Price", "expand": False, "type": "spin"},
            "sell_price": {"title": "Sell Price", "expand": False, "type": "spin"},
            "description": {"title": "Description", "expand": True, "type": "text"},
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_info["type"])
            factory.connect("bind", self._bind_cell, col_id, col_info["type"])
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(
                title=col_info["title"], factory=factory, expand=col_info["expand"]
            )
            self.column_view.append_column(column)

    def _setup_cell(self, factory, list_item, cell_type):
        """Sets up a cell in the column view.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the signal.
            list_item (Gtk.ListItem): The list item to set up.
            cell_type (str): The type of the cell to create.
        """
        if cell_type == "spin":
            widget = Gtk.SpinButton(
                adjustment=Gtk.Adjustment(lower=0, upper=99999, step_increment=1)
            )
        else:
            widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id, cell_type):
        """Binds a cell to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the signal.
            list_item (Gtk.ListItem): The list item to bind.
            column_id (str): The ID of the column to bind.
            cell_type (str): The type of the cell to bind.
        """
        item_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.bindings = []

        if cell_type == "spin":
            prop_name = "value"
            signal_name = "value-changed"
        else:
            prop_name = "text"
            signal_name = "changed"

        binding = widget.bind_property(
            prop_name,
            item_gobject,
            column_id,
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        handler_id = widget.connect(
            signal_name, lambda w: self.project_manager.set_dirty(True)
        )
        list_item.bindings.append(binding)
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell from the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the signal.
            list_item (Gtk.ListItem): The list item to unbind.
        """
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            del list_item.bindings
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry.

        Args:
            search_entry (Gtk.SearchEntry): The search entry that emitted the signal.
        """
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query.

        Args:
            item (ItemGObject): The item to filter.
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
            or search_text in item.type.lower()
        )

    def _update_visibility(self, *args):
        """Switches the view based on whether there are items."""
        self.stack.set_visible_child_name(
            "content" if self.model.get_n_items() > 0 else "empty"
        )

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        new_id_base = "new_item"
        new_id = new_id_base
        count = 1
        existing_ids = {i.id for i in self.project_manager.data.items}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_item_data = Item(
            id=new_id,
            name="New Item",
            type="Misc",
            description="",
            buy_price=0,
            sell_price=0,
        )
        self.project_manager.add_data_item("items", new_item_data)
        gobject = ItemGObject(new_item_data)
        self.model.append(gobject)

        for i in range(self.filter_model.get_n_items()):
            if self.filter_model.get_item(i) == gobject:
                self.selection.set_selected(i)
                self.column_view.scroll_to(i, Gtk.ListScrollFlags.NONE, None)
                break

    def _on_delete_clicked(self, button):
        """Handles the clicked signal from the delete button.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Item?",
            body=f"Are you sure you want to delete '{selected_item.name}'?",
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, item_gobject):
        """Handles the response from the delete confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog that emitted the signal.
            response (str): The response from the dialog.
            item_gobject (ItemGObject): The item to delete.
        """
        if response == "delete":
            if self.project_manager.remove_data_item("items", item_gobject.item):
                is_found, pos = self.model.find(item_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.close()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model.

        Args:
            selection_model (Gtk.SingleSelection): The selection model.
            position (int): The new selected position.
            n_items (int): The number of items in the model.
        """
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
