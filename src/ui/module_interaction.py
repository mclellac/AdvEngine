"""The interaction editor for the AdvEngine application.

This module defines the InteractionEditor, a widget for defining the outcomes
of player actions, such as combining items or using an item on a hotspot.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.schemas.gobject_factory import StringGObject
from ..core.schemas.interaction import Interaction, InteractionGObject
from ..core.schemas.item import Item
from ..core.schemas.logic import LogicGraph
from ..core.schemas.scene import Hotspot
from ..core.schemas.verb import Verb


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_interaction.ui"))
class InteractionEditor(Gtk.Box):
    """A widget for editing verb and item interactions.

    This editor provides a spreadsheet-like interface for creating and managing
    all game interactions. Each interaction links a verb, items, and/or
    hotspots to a specific logic graph that will be executed when the
    interaction occurs.

    Attributes:
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        model (Gio.ListStore): The data store for all interactions.
        selection (Gtk.SingleSelection): The selection model for the
            column view.
    """

    __gtype_name__ = "InteractionEditor"

    EDITOR_NAME = "Interactions"
    VIEW_NAME = "interaction_editor"
    ORDER = 2

    add_button: Gtk.Button = Gtk.Template.Child()
    delete_button: Gtk.Button = Gtk.Template.Child()
    column_view: Gtk.ColumnView = Gtk.Template.Child()
    status_page: Adw.StatusPage = Gtk.Template.Child()
    scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()

    def __init__(self, project_manager, settings_manager, **kwargs):
        """Initializes a new InteractionEditor instance.

        Args:
            project_manager: The project manager instance.
            settings_manager: The settings manager instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.project_manager.register_project_loaded_callback(self.project_loaded)

        self._setup_model()
        self._create_columns()
        self._connect_signals()

        self._update_visibility()

    def project_loaded(self):
        """Callback executed when a project is finished loading."""
        self._setup_model()
        self._create_columns()
        self._update_visibility()

    def _setup_model(self):
        """Sets up the data model and selection model."""
        self.model = Gio.ListStore(item_type=InteractionGObject)
        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

    def _connect_signals(self):
        """Connects widget signals to their corresponding handlers."""
        self.add_button.connect("clicked", self._on_add_clicked)
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.selection.connect("selection-changed", self._on_selection_changed)

    def _update_visibility(self):
        """Updates the visibility of the column view vs. the status page."""
        has_interactions = self.model.get_n_items() > 0
        self.scrolled_window.set_visible(has_interactions)
        self.status_page.set_visible(not has_interactions)

    def refresh_model(self):
        """Refreshes the data model from the project manager."""
        self.model.remove_all()
        for interaction in self.project_manager.data.interactions:
            self.model.append(InteractionGObject(interaction))
        self._update_visibility()

    def _create_columns(self):
        """Creates and configures the columns for the column view."""
        columns = {
            "verb_id": "Verb",
            "primary_item_id": "Primary Item",
            "secondary_item_id": "Secondary Item",
            "target_hotspot_id": "Target Hotspot",
            "logic_graph_id": "Logic Graph",
        }
        for col_id, title in columns.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_id)
            factory.connect("bind", self._bind_cell, col_id)
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(title=title, factory=factory, expand=True)
            self.column_view.append_column(column)

    def _setup_cell(self, factory, list_item, column_id):
        """Sets up a cell widget for the column view.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to set up.
            column_id (str): The ID of the column being set up.
        """
        dropdown = Gtk.DropDown()
        list_item.set_child(dropdown)

    def _bind_cell(self, factory, list_item, column_id):
        """Binds a cell widget to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to bind.
            column_id (str): The ID of the column to bind to.
        """
        interaction_gobject = list_item.get_item()
        dropdown = list_item.get_child()

        if column_id == "verb_id":
            model = Gtk.StringList.new(
                [""] + [v.id for v in self.project_manager.data.verbs]
            )
        elif "item_id" in column_id:
            model = Gtk.StringList.new(
                [""] + [i.id for i in self.project_manager.data.items]
            )
        elif column_id == "target_hotspot_id":
            model = Gtk.StringList.new(
                [""]
                + [h.id for s in self.project_manager.data.scenes for h in s.hotspots]
            )
        elif column_id == "logic_graph_id":
            model = Gtk.StringList.new(
                [""] + [lg.id for lg in self.project_manager.data.logic_graphs]
            )

        dropdown.set_model(model)

        current_value = getattr(interaction_gobject, column_id)
        if current_value:
            for i, item_str in enumerate(model):
                if item_str == current_value:
                    dropdown.set_selected(i)
                    break
        else:
            dropdown.set_selected(0)

        handler_id = dropdown.connect(
            "notify::selected",
            self._on_dropdown_changed,
            interaction_gobject,
            column_id,
        )
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell widget from the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to unbind.
        """
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_dropdown_changed(self, dropdown, _, interaction_gobject, column_id):
        """Handles the changed signal from a dropdown in the column view.

        Args:
            dropdown (Gtk.DropDown): The dropdown that emitted the signal.
            _: Unused parameter.
            interaction_gobject (InteractionGObject): The GObject wrapper for the
                interaction.
            column_id (str): The ID of the column that changed.
        """
        selected_item = dropdown.get_selected_item()
        new_value = selected_item.get_string() if selected_item else ""
        setattr(interaction_gobject.interaction, column_id, new_value)
        self.project_manager.set_dirty(True)

    def _on_add_clicked(self, button):
        """Handles the 'Add' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        new_id = f"interaction_{len(self.project_manager.data.interactions)}"
        new_interaction = Interaction(
            id=new_id, verb_id="", primary_item_id="", logic_graph_id=""
        )
        self.project_manager.add_data_item("interactions", new_interaction)
        self.refresh_model()
        self.selection.set_selected(self.model.get_n_items() - 1)
        self._update_visibility()

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
            heading="Delete Interaction?",
            body=f"Are you sure you want to delete '{selected_item.id}'?",
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, interaction_gobject):
        """Handles the response from the delete confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog that emitted the signal.
            response (str): The response ID.
            interaction_gobject (InteractionGObject): The interaction to delete.
        """
        if response == "delete":
            interaction_data = interaction_gobject.interaction
            if self.project_manager.remove_data_item("interactions", interaction_data):
                is_found, pos = self.model.find(interaction_gobject)
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
