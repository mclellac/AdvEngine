import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Verb, VerbGObject
from ..core.project_manager import ProjectManager

class VerbEditor(Gtk.Box):
    """A widget for editing verbs in a project, following HIG."""

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
        self.add_button.set_tooltip_text("Add New Verb")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Verb")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.model = Gio.ListStore(item_type=VerbGObject)
        for verb in self.project_manager.data.verbs:
            self.model.append(VerbGObject(verb))

        self.selection = Gtk.SingleSelection(model=self.model)
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

        self.empty_state = Adw.StatusPage(
            title="No Verbs",
            description="Create a new verb to get started.",
            icon_name="input-gaming-symbolic"
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

        group.add(id_entry)
        group.add(name_entry)

        list_item._id_entry = id_entry
        list_item._name_entry = name_entry
        list_item._bindings = []
        list_item._handler_ids = []
        list_item.set_child(group)

    def _bind_list_item(self, factory, list_item):
        """Bind a verb object to the stored widgets for inline editing."""
        verb_gobject = list_item.get_item()

        id_entry = list_item._id_entry
        name_entry = list_item._name_entry

        id_binding = id_entry.bind_property("text", verb_gobject, "id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        name_binding = name_entry.bind_property("text", verb_gobject, "name", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        list_item._bindings.extend([id_binding, name_binding])

        def on_applied(*args):
            if list_item.get_item():
                self.project_manager.set_dirty(True)

        list_item._handler_ids.extend([
            id_entry.connect("apply", on_applied),
            name_entry.connect("apply", on_applied)
        ])

    def _unbind_list_item(self, factory, list_item):
        """Disconnect all handlers and unbind all properties on unbind."""
        id_entry = list_item._id_entry
        name_entry = list_item._name_entry

        for binding in list_item._bindings:
            binding.unbind()
        list_item._bindings = []

        for handler_id in list_item._handler_ids:
            if id_entry.is_connected(handler_id): id_entry.disconnect(handler_id)
            if name_entry.is_connected(handler_id): name_entry.disconnect(handler_id)
        list_item._handler_ids = []

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

        self.selection.set_selected(self.model.get_n_items() - 1)

    def _on_delete_clicked(self, button):
        """Delete the selected verb."""
        selected_pos = self.selection.get_selected()
        if selected_pos == Gtk.INVALID_LIST_POSITION:
            return

        verb_gobject = self.model.get_item(selected_pos)

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
