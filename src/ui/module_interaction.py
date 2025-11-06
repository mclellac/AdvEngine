"""The interaction editor for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Interaction, InteractionGObject, Item, Verb, Hotspot, LogicGraph, StringGObject


class InteractionEditor(Adw.Bin):
    """A widget for editing interactions.

    This editor provides a table-like interface for creating, editing, and
    deleting interactions.
    """
    EDITOR_NAME = "Interactions"
    VIEW_NAME = "interaction_editor"
    ORDER = 2

    def __init__(self, project_manager, **kwargs):
        """Initializes a new InteractionEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager

        self.main_box = self._build_ui()
        self.set_child(self.main_box)

        self._refresh_model()
        self._update_visibility()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        clamp = Adw.Clamp()
        clamp.set_child(main_box)
        self.set_child(clamp)

        header = Adw.HeaderBar()
        main_box.append(header)

        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Interaction")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Interaction")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.model = Gio.ListStore(item_type=InteractionGObject)
        self.selection = Gtk.SingleSelection(model=self.model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        self.column_view = Gtk.ColumnView(model=self.selection)
        self.column_view.set_vexpand(True)
        self._create_columns()

        self.status_page = Adw.StatusPage(
            title="No Interactions", icon_name="emblem-synchronizing-symbolic")
        main_box.append(self.status_page)
        main_box.append(self.column_view)

        return main_box

    def _update_visibility(self):
        """Updates the visibility of the column view and status page."""
        has_interactions = self.model.get_n_items() > 0
        self.column_view.set_visible(has_interactions)
        self.status_page.set_visible(not has_interactions)

    def _refresh_model(self):
        """Refreshes the data model."""
        self.model.remove_all()
        for interaction in self.project_manager.data.interactions:
            self.model.append(InteractionGObject(interaction))
        self._update_visibility()

    def _create_columns(self):
        """Creates the columns for the column view."""
        columns = {
            "verb_id": "Verb", "primary_item_id": "Primary Item",
            "secondary_item_id": "Secondary Item", "target_hotspot_id": "Target Hotspot",
            "logic_graph_id": "Logic Graph"
        }
        for col_id, title in columns.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell, col_id)
            factory.connect("bind", self._bind_cell, col_id)
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(
                title=title, factory=factory, expand=True)
            self.column_view.append_column(column)

    def _setup_cell(self, factory, list_item, column_id):
        """Sets up a cell in the column view."""
        dropdown = Gtk.DropDown()
        list_item.set_child(dropdown)

    def _bind_cell(self, factory, list_item, column_id):
        """Binds a cell to the data model."""
        interaction_gobject = list_item.get_item()
        dropdown = list_item.get_child()

        if column_id == "verb_id":
            model = Gtk.StringList.new(
                [v.id for v in self.project_manager.data.verbs])
        elif "item_id" in column_id:
            model = Gtk.StringList.new(
                [i.id for i in self.project_manager.data.items])
        elif column_id == "target_hotspot_id":
            model = Gtk.StringList.new(
                [h.id for s in self.project_manager.data.scenes for h in s.hotspots])
        elif column_id == "logic_graph_id":
            model = Gtk.StringList.new(
                [lg.id for lg in self.project_manager.data.logic_graphs])

        dropdown.set_model(model)

        current_value = getattr(interaction_gobject, column_id)
        if current_value:
            is_found, pos = model.find(StringGObject(current_value))
            if is_found:
                dropdown.set_selected(pos)

        list_item.bindings = []
        binding = dropdown.bind_property(
            "selected", interaction_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        list_item.bindings.append(binding)

        handler_id = dropdown.connect(
            "notify::selected", lambda d, p: self.project_manager.set_dirty(True))
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        """Unbinds a cell from the data model."""
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            list_item.bindings = []
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_add_clicked(self, button):
        """Handles the clicked signal from the add button."""
        new_id = f"interaction_{len(self.project_manager.data.interactions)}"
        new_interaction = Interaction(
            id=new_id, verb_id="", primary_item_id="", logic_graph_id="")
        self.project_manager.add_interaction(new_interaction)
        self.model.append(InteractionGObject(new_interaction))
        self.selection.set_selected(self.model.get_n_items() - 1)

    def _on_delete_clicked(self, button):
        """Handles the clicked signal from the delete button."""
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Interaction?",
            body=f"Are you sure you want to delete '{selected_item.id}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response,
                       selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, interaction_gobject):
        """Handles the response from the delete confirmation dialog."""
        if response == "delete":
            if self.project_manager.remove_interaction(interaction_gobject.interaction_data):
                is_found, pos = self.model.find(interaction_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
