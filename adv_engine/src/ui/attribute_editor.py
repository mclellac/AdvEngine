import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Attribute, AttributeGObject
from ..core.project_manager import ProjectManager

class AttributeEditor(Gtk.Box):
    """A widget for editing attributes in a project, following HIG for inline editing."""

    def __init__(self, project_manager: ProjectManager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.project_manager = project_manager

        clamp = Adw.Clamp()
        self.append(clamp)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        clamp.set_child(self.main_box)

        header = Adw.HeaderBar()
        self.main_box.append(header)

        self.add_button = Gtk.Button(icon_name="list-add-symbolic")
        self.add_button.set_tooltip_text("Add New Attribute")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Attribute")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search attributes...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Models ---
        self.model = Gio.ListStore(item_type=AttributeGObject)
        for attribute in self.project_manager.data.attributes:
            self.model.append(AttributeGObject(attribute))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func)
        self.filter_model.set_filter(self.filter)

        self.selection = Gtk.SingleSelection(model=self.filter_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)
        factory.connect("unbind", self._unbind_list_item)

        self.list_view = Gtk.ListView(model=self.selection, factory=factory)
        self.list_view.set_vexpand(True)
        self.list_view.set_css_classes(["boxed-list"])

        scrolled_window = Gtk.ScrolledWindow(child=self.list_view)
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

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _setup_list_item(self, factory, list_item):
        """Set up the structure of a list item and store widget references."""
        group = Adw.PreferencesGroup()

        id_entry = Adw.EntryRow(title="ID")
        name_entry = Adw.EntryRow(title="Name")
        initial_value_entry = Adw.SpinRow(title="Initial Value", subtitle="The starting value of the attribute.")
        max_value_entry = Adw.SpinRow(title="Max Value", subtitle="The maximum value of the attribute.")

        initial_value_entry.set_adjustment(Gtk.Adjustment(lower=0, upper=99999, step_increment=1))
        max_value_entry.set_adjustment(Gtk.Adjustment(lower=0, upper=99999, step_increment=1))

        group.add(id_entry)
        group.add(name_entry)
        group.add(initial_value_entry)
        group.add(max_value_entry)

        list_item._id_entry = id_entry
        list_item._name_entry = name_entry
        list_item._initial_value_row = initial_value_entry
        list_item._max_value_row = max_value_entry
        list_item._bindings = []
        list_item._handler_ids = []

        list_item.set_child(group)

    def _bind_list_item(self, factory, list_item):
        """Bind an AttributeGObject to the stored widgets for inline editing."""
        attr_gobject = list_item.get_item()

        id_entry = list_item._id_entry
        name_entry = list_item._name_entry
        initial_value_row = list_item._initial_value_row
        max_value_row = list_item._max_value_row

        bindings = [
            id_entry.bind_property("text", attr_gobject, "id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            name_entry.bind_property("text", attr_gobject, "name", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            initial_value_row.bind_property("value", attr_gobject, "initial_value", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            max_value_row.bind_property("value", attr_gobject, "max_value", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        ]
        list_item._bindings.extend(bindings)

        def on_applied(*args):
            if list_item.get_item():
                self.project_manager.set_dirty(True)

        list_item._handler_ids.extend([
            id_entry.connect("apply", on_applied),
            name_entry.connect("apply", on_applied),
            initial_value_row.connect("notify::value", on_applied),
            max_value_row.connect("notify::value", on_applied)
        ])

    def _unbind_list_item(self, factory, list_item):
        """Disconnect all handlers and unbind all properties on unbind."""
        for binding in list_item._bindings:
            binding.unbind()
        list_item._bindings = []

        id_entry = list_item._id_entry
        name_entry = list_item._name_entry
        initial_value_row = list_item._initial_value_row
        max_value_row = list_item._max_value_row

        for handler_id in list_item._handler_ids:
            if id_entry.is_connected(handler_id): id_entry.disconnect(handler_id)
            if name_entry.is_connected(handler_id): name_entry.disconnect(handler_id)
            if initial_value_row.is_connected(handler_id): initial_value_row.disconnect(handler_id)
            if max_value_row.is_connected(handler_id): max_value_row.disconnect(handler_id)
        list_item._handler_ids = []


    def _on_add_clicked(self, button):
        """Add a new, empty attribute."""
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

        self.filter.changed(Gtk.FilterChange.DIFFERENT)

        for i in range(self.filter_model.get_n_items()):
            if self.filter_model.get_item(i) == gobject:
                self.selection.set_selected(i)
                break

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

    def _filter_func(self, item):
        search_text = self.search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower())

    def _on_search_changed(self, entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)
