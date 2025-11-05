import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Verb, VerbGObject
from ..core.project_manager import ProjectManager

class VerbEditor(Gtk.Box):
    """A widget for editing verbs in a project, using a ColumnView for a more
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
        self.add_button.set_tooltip_text("Add New Verb")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Verb")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Search ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Verbs")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Model ---
        self.model = Gio.ListStore(item_type=VerbGObject)
        for verb in self.project_manager.data.verbs:
            self.model.append(VerbGObject(verb))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.search_entry)
        self.filter_model.set_filter(self.filter)

        self.selection = Gtk.SingleSelection(model=self.filter_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        # --- Column View ---
        self.column_view = Gtk.ColumnView(model=self.selection)
        self.column_view.set_vexpand(True)

        # Define columns
        columns_def = {
            "id": {"title": "ID", "expand": True},
            "name": {"title": "Name", "expand": True}
        }

        for col_id, col_info in columns_def.items():
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._setup_cell)
            factory.connect("bind", self._bind_cell, col_id)
            factory.connect("unbind", self._unbind_cell)
            column = Gtk.ColumnViewColumn(title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            self.column_view.append_column(column)

        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Verbs",
            description="Create a new verb to get started.",
            icon_name="input-gaming-symbolic"
        )
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _setup_cell(self, factory, list_item):
        widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id):
        verb_gobject = list_item.get_item()
        widget = list_item.get_child()

        list_item.bindings = []
        binding = widget.bind_property("text", verb_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        list_item.bindings.append(binding)

        handler_id = widget.connect("changed", lambda w: self.project_manager.set_dirty(True))
        list_item.handler_id = handler_id

    def _unbind_cell(self, factory, list_item):
        if hasattr(list_item, "bindings"):
            for binding in list_item.bindings:
                binding.unbind()
            list_item.bindings = []
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_search_changed(self, search_entry):
        """Called when the search text changes. Invalidates the filter."""
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        """The actual filter function."""
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return search_text in item.id.lower() or search_text in item.name.lower()

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        """Add a new, empty verb to the list."""
        new_id_base = "new_verb"
        new_id = new_id_base
        count = 1
        existing_ids = {v.id for v in self.project_manager.data.verbs}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_verb = self.project_manager.add_verb(id=new_id, name="New Verb")
        gobject = VerbGObject(new_verb)
        self.model.append(gobject)

        # Find the position in the filter model and select it
        is_found, pos = self.filter_model.get_model().find(gobject)
        if is_found:
             self.selection.set_selected(pos)


    def _on_delete_clicked(self, button):
        """Delete the selected verb."""
        selected_pos = self.selection.get_selected()
        if selected_pos == Gtk.INVALID_LIST_POSITION:
            return

        verb_gobject = self.selection.get_selected_item()
        if not verb_gobject:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Verb?",
            body=f"Are you sure you want to delete '{verb_gobject.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, verb_gobject)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, verb_gobject):
        if response == "delete":
            if self.project_manager.remove_verb(verb_gobject.verb_data):
                is_found, pos = self.model.find(verb_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        """Enable or disable the delete button based on selection."""
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
