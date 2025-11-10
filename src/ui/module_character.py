"""The character editor for the AdvEngine application.

This module defines the CharacterManager, a widget for creating, editing, and
deleting all in-game characters using a spreadsheet-style interface.
"""

import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.schemas import Character, CharacterGObject
from ..core.project_manager import ProjectManager


@Gtk.Template(
    filename=os.path.join(os.path.dirname(__file__), "module_character.ui")
)
class CharacterManager(Gtk.Box):
    """A widget for editing characters in a project.

    This editor provides a Gtk.ColumnView for inline editing of character
    properties, including their ID, name, merchant status, and portrait asset.
    It also includes search and delete functionality.

    Attributes:
        project_manager (ProjectManager): The main project manager instance.
        settings_manager: The main settings manager instance.
        model (Gio.ListStore): The data store for all characters.
        filter_model (Gtk.FilterListModel): The filter model for search.
        selection (Gtk.SingleSelection): The selection model for the
            column view.
    """

    __gtype_name__ = "CharacterManager"

    EDITOR_NAME = "Characters"
    VIEW_NAME = "character_manager"
    ORDER = 8

    add_button: Gtk.Button = Gtk.Template.Child()
    delete_button: Gtk.Button = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    column_view: Gtk.ColumnView = Gtk.Template.Child()
    portrait_preview: Gtk.Picture = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new CharacterManager instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        project_manager = kwargs.pop("project_manager")
        settings_manager = kwargs.pop("settings_manager")

        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.project_manager.register_project_loaded_callback(self.project_loaded)

        self.model = self._setup_model()
        self.filter_model = self._setup_filter_model()
        self.selection = self._setup_selection_model()
        self._setup_column_view()
        self.column_view.set_model(self.selection)

        self._connect_signals()
        self._update_visibility()

    def project_loaded(self):
        """Callback for when the project is loaded."""
        self.refresh_model()

    def refresh_model(self):
        """Clears and repopulates the model from the project manager."""
        self.model.remove_all()
        for character in self.project_manager.data.characters:
            self.model.append(CharacterGObject(character))
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
        model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            model.append(CharacterGObject(character))
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
            "display_name": {"title": "Display Name", "expand": True, "type": "text"},
            "is_merchant": {"title": "Is Merchant", "expand": False, "type": "switch"},
            "portrait_asset_id": {
                "title": "Portrait Asset",
                "expand": True,
                "type": "combo",
            },
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_info["type"])
            factory.connect("bind", self._bind_cell, col_id, col_info["type"])
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            column_view.append_column(column)

    def _setup_cell(self, factory, list_item, cell_type):
        """Sets up a cell widget for the column view.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to set up.
            cell_type (str): The type of widget to create ('text', 'switch',
                'combo').
        """
        if cell_type == "switch":
            widget = Gtk.Switch(valign=Gtk.Align.CENTER)
        elif cell_type == "combo":
            image_assets = ["None"] + [
                asset.id
                for asset in self.project_manager.data.assets
                if asset.asset_type in ["sprite", "animation"]
            ]
            widget = Gtk.DropDown.new_from_strings(image_assets)
        else:
            widget = Gtk.Entry(valign=Gtk.Align.CENTER)
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id, cell_type):
        """Binds a cell widget to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to bind.
            column_id (str): The ID of the column to bind to.
            cell_type (str): The type of the cell widget.
        """
        char_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.bindings = []

        if cell_type == "switch":
            binding = widget.bind_property(
                "active",
                char_gobject,
                column_id,
                GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
            )
            handler_id = widget.connect(
                "notify::active", lambda w, _: self.project_manager.set_dirty(True)
            )
        elif cell_type == "combo":
            model = widget.get_model()
            for i in range(model.get_n_items()):
                if model.get_string(i) == getattr(char_gobject, column_id, "None"):
                    widget.set_selected(i)
                    break
            handler_id = widget.connect(
                "notify::selected-item", self._on_combo_changed, char_gobject, column_id
            )
        else:  # "text"
            binding = widget.bind_property(
                "text",
                char_gobject,
                column_id,
                GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
            )
            list_item.bindings.append(binding)
            handler_id = widget.connect(
                "changed", lambda w: self.project_manager.set_dirty(True)
            )

        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell widget from the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to unbind.
        """
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            del list_item.bindings
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_combo_changed(self, combo, _, char_gobject, column_id):
        """Handles the changed signal from a combo box cell.

        Args:
            combo (Gtk.DropDown): The dropdown that emitted the signal.
            _: Unused parameter.
            char_gobject (CharacterGObject): The GObject wrapper for the
                character.
            column_id (str): The ID of the column that changed.
        """
        selected_str = (
            combo.get_selected_item().get_string()
            if combo.get_selected_item()
            else "None"
        )
        setattr(char_gobject, column_id, selected_str)
        self.project_manager.set_dirty(True)
        self._update_preview()

    def _update_preview(self):
        """Updates the portrait preview image based on the current selection."""
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            self.portrait_preview.set_filename(None)
            return

        asset_id = selected_item.portrait_asset_id
        if asset_id and asset_id != "None":
            asset = next(
                (a for a in self.project_manager.data.assets if a.id == asset_id), None
            )
            if (
                asset
                and self.project_manager.project_path
                and os.path.exists(
                    os.path.join(self.project_manager.project_path, asset.file_path)
                )
            ):
                self.portrait_preview.set_filename(
                    os.path.join(self.project_manager.project_path, asset.file_path)
                )
            else:
                self.portrait_preview.set_filename(None)
        else:
            self.portrait_preview.set_filename(None)

    def _on_search_changed(self, search_entry):
        """Handles the search-changed signal from the search entry.

        Args:
            search_entry (Gtk.SearchEntry): The search entry that emitted the
                signal.
        """
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """Filters items based on the search query.

        Args:
            item (CharacterGObject): The item to filter.
            search_entry (Gtk.SearchEntry): The search entry.

        Returns:
            bool: True if the item should be visible, False otherwise.
        """
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (
            search_text in item.id.lower() or search_text in item.display_name.lower()
        )

    def _update_visibility(self, *args):
        """Switches the view based on whether there are items."""
        if self.model.get_n_items() > 0:
            self.stack.set_visible_child_name("content")
        else:
            self.stack.set_visible_child_name("empty")

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        new_id_base = "new_char"
        new_id = new_id_base
        count = 1
        existing_ids = {c.id for c in self.project_manager.data.characters}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_char_data = Character(
            id=new_id,
            display_name="New Character",
            dialogue_start_id="",
            is_merchant=False,
            shop_id="",
            portrait_asset_id="None",
        )
        self.project_manager.add_data_item("characters", new_char_data)
        gobject = CharacterGObject(new_char_data)
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
            heading="Delete Character?",
            body=f"Are you sure you want to delete '{selected_item.display_name}'?",
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        """Handles the response from the delete confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog that emitted the signal.
            response (str): The response ID.
            char_gobject (CharacterGObject): The character to delete.
        """
        if response == "delete":
            char_data = char_gobject.character
            if self.project_manager.remove_data_item("characters", char_data):
                is_found, pos = self.model.find(char_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.close()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model.

        Args:
            selection_model (Gtk.SingleSelection): The selection model.
            position (int): The position of the selected item.
            n_items (int): The number of items in the model.
        """
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
        self._update_preview()
