import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Item, ItemGObject

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject, Gdk
from ..core.data_schemas import Item, ItemGObject

class ItemEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, item=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Item" if item is None else "Edit Item")
        self.project_manager = project_manager
        self.item = item

        # Add CSS provider for validation styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .error {
            border: 1px solid red;
            border-radius: 6px;
        }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        group = Adw.PreferencesGroup()
        content.append(group)

        self.id_entry = Gtk.Entry(text=item.id if item else "")
        self.id_entry.set_tooltip_text("A unique string identifier for the item (e.g., 'key_01').")
        group.add(self._create_action_row("ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=item.name if item else "")
        self.name_entry.set_tooltip_text("The in-game name of the item.")
        group.add(self._create_action_row("Name", "In-game display name", self.name_entry))

        self.type_entry = Gtk.Entry(text=item.type if item else "")
        self.type_entry.set_tooltip_text("A category for the item (e.g., 'Key', 'Consumable').")
        group.add(self._create_action_row("Type", "Item category", self.type_entry))

        self.buy_price_entry = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=-1, upper=99999, step_increment=1), value=item.buy_price if item else 0)
        self.buy_price_entry.set_tooltip_text("The price to buy this item from a shop. -1 means it cannot be bought.")
        group.add(self._create_action_row("Buy Price", "Price in shops (-1 for not buyable)", self.buy_price_entry))

        self.sell_price_entry = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=-1, upper=99999, step_increment=1), value=item.sell_price if item else 0)
        self.sell_price_entry.set_tooltip_text("The price when selling this item. -1 means it cannot be sold.")
        group.add(self._create_action_row("Sell Price", "Price when selling (-1 for not sellable)", self.sell_price_entry))

        desc_group = Adw.PreferencesGroup(title="Description", description="Flavor text for the 'Look' action.")
        content.append(desc_group)

        self.description_entry = Gtk.TextView()
        self.description_entry.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.description_entry.set_size_request(-1, 100)
        if item and item.description:
            self.description_entry.get_buffer().set_text(item.description)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.description_entry)
        desc_group.add(scrolled_window)

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        # Connect validation signals
        self.id_entry.connect("changed", self._validate)
        self.name_entry.connect("changed", self._validate)

        # Initial validation
        self._validate(None)

    def _validate(self, entry):
        is_valid = True
        # Validate ID
        id_text = self.id_entry.get_text()
        is_new_item = self.item is None
        id_is_duplicate = any(item.id == id_text for item in self.project_manager.data.items if (is_new_item or item.id != self.item.id))

        if not id_text or id_is_duplicate:
            self.id_entry.add_css_class("error")
            if not id_text:
                self.id_entry.set_tooltip_text("ID cannot be empty.")
            else:
                self.id_entry.set_tooltip_text("This ID is already in use.")
            is_valid = False
        else:
            self.id_entry.remove_css_class("error")
            self.id_entry.set_tooltip_text("")

        # Validate Name
        if not self.name_entry.get_text():
            self.name_entry.add_css_class("error")
            self.name_entry.set_tooltip_text("Name cannot be empty.")
            is_valid = False
        else:
            self.name_entry.remove_css_class("error")
            self.name_entry.set_tooltip_text("")

        self.set_response_enabled("ok", is_valid)


    def _create_action_row(self, title, subtitle, widget):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(widget)
        row.set_activatable_widget(widget)
        return row

class ItemEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True, vexpand=True)
        self.append(self.main_box)

        # Title and Toolbar
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title = Gtk.Label(label="Item Editor", halign=Gtk.Align.START, hexpand=True,
                          css_classes=["title-2"])
        header_box.append(title)

        toolbar = Gtk.Box(spacing=5)
        self.add_button = Gtk.Button(label="Add")
        self.add_button.connect("clicked", self._on_add_clicked)
        self.edit_button = Gtk.Button(label="Edit")
        self.edit_button.connect("clicked", self._on_edit_clicked)
        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.connect("clicked", self._on_delete_clicked)

        toolbar.append(self.add_button)
        toolbar.append(self.edit_button)
        toolbar.append(self.delete_button)
        header_box.append(toolbar)

        self.main_box.append(header_box)

        # Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search items...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Column View for Items ---
        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=ItemGObject)
        for item in self.project_manager.data.items:
            self.model.append(ItemGObject(item))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.filter_model)
        self.filter_model.set_filter(self.filter)

        self.sort_model = Gtk.SortListModel(model=self.filter_model)

        self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.column_view.set_model(self.selection)

        # Define columns
        self._create_column("ID", Gtk.StringSorter(), lambda item: item.id)
        self._create_column("Name", Gtk.StringSorter(), lambda item: item.name)
        self._create_column("Type", Gtk.StringSorter(), lambda item: item.type)
        self._create_column("Description", None, lambda item: item.description or "")
        self._create_column("Buy Price", Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(ItemGObject, None, "buy_price")), lambda item: str(item.buy_price))
        self._create_column("Sell Price", Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(ItemGObject, None, "sell_price")), lambda item: str(item.sell_price))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)

        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(title="No Items",
                                          description="Create a new item to begin.",
                                          icon_name="document-new-symbolic")
        self.add_item_button_empty = Gtk.Button(label="Create Item")
        self.add_item_button_empty.connect("clicked", self._on_add_clicked)
        self.empty_state.set_child(self.add_item_button_empty)
        self.append(self.empty_state)

        self.model.connect("items-changed", lambda model, pos, rem, add: self.update_visibility())
        self.update_visibility()


    def update_visibility(self):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)


    def _create_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.column_view.append_column(col)

    def _filter_func(self, item, _):
        search_text = self.search_entry.get_text().lower()
        if not search_text:
            return True
        return (search_text in item.id.lower() or
                search_text in item.name.lower() or
                search_text in item.type.lower())

    def _on_search_changed(self, entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _on_add_clicked(self, button):
        dialog = ItemEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            new_item = Item(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text(),
                type=dialog.type_entry.get_text(),
                description=dialog.description_entry.get_buffer().get_text(
                    dialog.description_entry.get_buffer().get_start_iter(),
                    dialog.description_entry.get_buffer().get_end_iter(),
                    False
                ),
                buy_price=int(dialog.buy_price_entry.get_value()),
                sell_price=int(dialog.sell_price_entry.get_value())
            )
            self.project_manager.add_item(new_item)
            self.model.append(ItemGObject(new_item))
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_item_gobject = self.selection.get_selected_item()
        if selected_item_gobject:
            # Need to get the underlying ItemGObject from the SortListModel
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = ItemEditorDialog(self.get_root(), self.project_manager, item=underlying_item.item)
            dialog.connect("response", self._on_edit_dialog_response, underlying_item)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, item_gobject):
        if response == "ok":
            item_gobject.item.id = dialog.id_entry.get_text()
            item_gobject.item.name = dialog.name_entry.get_text()
            item_gobject.item.type = dialog.type_entry.get_text()
            item_gobject.item.description = dialog.description_entry.get_buffer().get_text(
                dialog.description_entry.get_buffer().get_start_iter(),
                dialog.description_entry.get_buffer().get_end_iter(),
                False
            )
            item_gobject.item.buy_price = int(dialog.buy_price_entry.get_value())
            item_gobject.item.sell_price = int(dialog.sell_price_entry.get_value())
            self.project_manager.set_dirty(True)
            # Find the item in the model and notify it has changed
            pos = self.model.find(item_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)

        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_item_gobject = self.selection.get_selected_item()
        if selected_item_gobject:
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Item?",
                body=f"Are you sure you want to delete '{underlying_item.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, underlying_item)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, item_gobject):
        if response == "delete":
            self.project_manager.remove_item(item_gobject.item)
            pos = self.model.find(item_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
