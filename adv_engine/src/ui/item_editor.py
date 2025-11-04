import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Item, ItemGObject
from ..core.project_manager import ProjectManager

class ItemEditor(Gtk.Box):
    """A widget for editing items in a project, following HIG for inline editing."""

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
        self.add_button.set_tooltip_text("Add New Item")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Item")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search items...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Data Models ---
        self.model = Gio.ListStore(item_type=ItemGObject)
        for item in self.project_manager.data.items:
            self.model.append(ItemGObject(item))

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
            title="No Items",
            description="Create a new item to get started.",
            icon_name="edit-find-replace-symbolic"
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
        type_entry = Adw.EntryRow(title="Type")
        buy_price_entry = Adw.SpinRow(title="Buy Price", subtitle="Price in shops (-1 for not buyable)")
        sell_price_entry = Adw.SpinRow(title="Sell Price", subtitle="Price when selling (-1 for not sellable)")

        buy_price_entry.set_adjustment(Gtk.Adjustment(lower=-1, upper=99999, step_increment=1))
        sell_price_entry.set_adjustment(Gtk.Adjustment(lower=-1, upper=99999, step_increment=1))

        desc_view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR, height_request=100)
        desc_scroll = Gtk.ScrolledWindow(child=desc_view)
        desc_row = Adw.ExpanderRow(title="Description", subtitle="Flavor text for the 'Look' action.")
        desc_row.add_row(desc_scroll)

        group.add(id_entry)
        group.add(name_entry)
        group.add(type_entry)
        group.add(buy_price_entry)
        group.add(sell_price_entry)
        group.add(desc_row)

        list_item._id_entry = id_entry
        list_item._name_entry = name_entry
        list_item._type_entry = type_entry
        list_item._buy_row = buy_price_entry
        list_item._sell_row = sell_price_entry
        list_item._desc_view = desc_view
        list_item._handler_ids = []

        list_item.set_child(group)

    def _bind_list_item(self, factory, list_item):
        """Bind an ItemGObject to the stored widgets for inline editing."""
        item_gobject = list_item.get_item()

        id_entry = list_item._id_entry
        name_entry = list_item._name_entry
        type_entry = list_item._type_entry
        buy_row = list_item._buy_row
        sell_row = list_item._sell_row
        desc_view = list_item._desc_view

        id_entry.bind_property("text", item_gobject, "id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        name_entry.bind_property("text", item_gobject, "name", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        type_entry.bind_property("text", item_gobject, "type", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        buy_row.bind_property("value", item_gobject, "buy_price", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        sell_row.bind_property("value", item_gobject, "sell_price", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        desc_view.get_buffer().bind_property("text", item_gobject, "description", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        def on_applied(*args):
            if list_item.get_item():
                self.project_manager.set_dirty(True)

        list_item._handler_ids.extend([
            id_entry.connect("apply", on_applied),
            name_entry.connect("apply", on_applied),
            type_entry.connect("apply", on_applied),
            buy_row.connect("notify::value", on_applied),
            sell_row.connect("notify::value", on_applied),
            desc_view.get_buffer().connect("changed", on_applied)
        ])

    def _unbind_list_item(self, factory, list_item):
        """Disconnect all handlers on unbind."""
        widgets = [
            list_item._id_entry,
            list_item._name_entry,
            list_item._type_entry,
            list_item._buy_row,
            list_item._sell_row,
            list_item._desc_view.get_buffer()
        ]
        for i, widget in enumerate(widgets):
            handler_id = list_item._handler_ids[i]
            if widget.is_connected(handler_id):
                widget.disconnect(handler_id)
        list_item._handler_ids = []

    def _on_add_clicked(self, button):
        """Add a new, empty item."""
        new_id_base = "new_item"
        new_id = new_id_base
        count = 1
        existing_ids = {i.id for i in self.project_manager.data.items}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_item_data = Item(id=new_id, name="New Item", type="Misc", description="", buy_price=0, sell_price=0)
        self.project_manager.add_item(new_item_data)
        gobject = ItemGObject(new_item_data)
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
            heading="Delete Item?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, item_gobject):
        if response == "delete":
            if self.project_manager.remove_item(item_gobject.item):
                is_found, pos = self.model.find(item_gobject)
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
                search_text in item.name.lower() or
                search_text in item.type.lower())

    def _on_search_changed(self, entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)
