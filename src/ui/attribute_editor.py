import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Attribute, AttributeGObject
from ..core.project_manager import ProjectManager

class AttributeEditor(Gtk.Box):
    """A widget for editing attributes in a project, using a ColumnView for a
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
        self.add_button.set_tooltip_text("Add New Attribute")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Attribute")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Search ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Attributes")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Model ---
        self.model = Gio.ListStore(item_type=AttributeGObject)
        for attribute in self.project_manager.data.attributes:
            self.model.append(AttributeGObject(attribute))

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
            column = Gtk.ColumnViewColumn(title=col_info["title"], factory=factory)
            column.set_expand(col_info["expand"])
            self.column_view.append_column(column)

        scrolled_window = Gtk.ScrolledWindow(child=self.column_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Attributes",
            description="Create a new attribute to get started.",
            icon_name="document-properties-symbolic"
        )
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _setup_cell(self, factory, list_item, column_id):
        if column_id in ["initial_value", "max_value"]:
            widget = Gtk.SpinButton(
                adjustment=Gtk.Adjustment(
                    lower=0, upper=99999, step_increment=1
                )
            )
        else:
            widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_cell(self, factory, list_item, column_id):
        attr_gobject = list_item.get_item()
        widget = list_item.get_child()

        list_item.bindings = []
        if isinstance(widget, Gtk.SpinButton):
            binding = widget.bind_property("value", attr_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            list_item.bindings.append(binding)

            handler_id = widget.connect("value-changed", lambda w: self.project_manager.set_dirty(True))
            list_item.handler_id = handler_id
        else:
            binding = widget.bind_property("text", attr_gobject, column_id, GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
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
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _filter_func(self, item, search_entry):
        search_text = search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower())

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _on_add_clicked(self, button):
        new_id_base = "new_attribute"
        new_id = new_id_base
        count = 1
        existing_ids = {a.id for a in self.project_manager.data.attributes}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_attr_data = Attribute(id=new_id, name="New Attribute", initial_value=10, max_value=100)
        self.project_manager.add_attribute(new_attr_data)
        gobject = AttributeGObject(new_attr_data)
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
            heading="Delete Attribute?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, attr_gobject):
        if response == "delete":
            if self.project_manager.remove_attribute(attr_gobject.attribute_data):
                is_found, pos = self.model.find(attr_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        is_selected = selection_model.get_selected() != Gtk.INVALID_LIST_POSITION
        self.delete_button.set_sensitive(is_selected)
