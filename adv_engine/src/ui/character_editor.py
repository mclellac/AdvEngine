import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw
from ..core.data_schemas import Character, CharacterGObject

class CharacterEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, character=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Character" if character is None else "Edit Character")

        self.character = character

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        self.id_entry = Gtk.Entry(text=character.id if character else "")
        self.display_name_entry = Gtk.Entry(text=character.display_name if character else "")
        self.dialogue_start_id_entry = Gtk.Entry(text=character.dialogue_start_id if character else "")
        self.is_merchant_check = Gtk.CheckButton(active=character.is_merchant if character else False)
        self.shop_id_entry = Gtk.Entry(text=character.shop_id if character else "")

        content.append(self._create_row("ID:", self.id_entry))
        content.append(self._create_row("Display Name:", self.display_name_entry))
        content.append(self._create_row("Dialogue Start ID:", self.dialogue_start_id_entry))
        content.append(self._create_row("Is Merchant:", self.is_merchant_check))
        content.append(self._create_row("Shop ID:", self.shop_id_entry))

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

    def _create_row(self, label_text, widget):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text, halign=Gtk.Align.START, hexpand=True)
        box.append(label)
        box.append(widget)
        return box

class CharacterEditor(Gtk.Box):
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
        title = Gtk.Label(label="Character Editor", halign=Gtk.Align.START, hexpand=True,
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
        self.search_entry.set_placeholder_text("Search characters...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Column View for Characters ---
        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            self.model.append(CharacterGObject(character))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.filter_model)
        self.filter_model.set_filter(self.filter)

        self.sort_model = Gtk.SortListModel(model=self.filter_model)

        self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.column_view.set_model(self.selection)

        # Define columns
        self._create_column("ID", Gtk.StringSorter(), lambda char: char.id)
        self._create_column("Display Name", Gtk.StringSorter(), lambda char: char.display_name)
        self._create_column("Dialogue Start ID", Gtk.StringSorter(), lambda char: char.dialogue_start_id)
        self._create_column("Is Merchant", None, lambda char: "Yes" if char.is_merchant else "No")
        self._create_column("Shop ID", Gtk.StringSorter(), lambda char: char.shop_id or "")

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)

        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(title="No Characters",
                                          description="Create a new character to begin.",
                                          icon_name="document-new-symbolic")
        self.add_char_button_empty = Gtk.Button(label="Create Character")
        self.add_char_button_empty.connect("clicked", self._on_add_clicked)
        self.empty_state.set_child(self.add_char_button_empty)
        self.append(self.empty_state)

        self.model.connect("items-changed", lambda model, pos, rem, add: self.update_visibility())
        self.update_visibility()

    def update_visibility(self):
        has_chars = self.model.get_n_items() > 0
        self.main_box.set_visible(has_chars)
        self.empty_state.set_visible(not has_chars)

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
                search_text in item.display_name.lower())

    def _on_search_changed(self, entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _on_add_clicked(self, button):
        dialog = CharacterEditorDialog(self.get_root())
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            new_char = Character(
                id=dialog.id_entry.get_text(),
                display_name=dialog.display_name_entry.get_text(),
                dialogue_start_id=dialog.dialogue_start_id_entry.get_text(),
                is_merchant=dialog.is_merchant_check.get_active(),
                shop_id=dialog.shop_id_entry.get_text()
            )
            self.project_manager.add_character(new_char)
            self.model.append(CharacterGObject(new_char))
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_char_gobject = self.selection.get_selected_item()
        if selected_char_gobject:
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = CharacterEditorDialog(self.get_root(), character=underlying_item.character_data)
            dialog.connect("response", self._on_edit_dialog_response, underlying_item)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, char_gobject):
        if response == "ok":
            char_gobject.character_data.id = dialog.id_entry.get_text()
            char_gobject.character_data.display_name = dialog.display_name_entry.get_text()
            char_gobject.character_data.dialogue_start_id = dialog.dialogue_start_id_entry.get_text()
            char_gobject.character_data.is_merchant = dialog.is_merchant_check.get_active()
            char_gobject.character_data.shop_id = dialog.shop_id_entry.get_text()
            self.project_manager.set_dirty(True)
            pos = self.model.find(char_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_char_gobject = self.selection.get_selected_item()
        if selected_char_gobject:
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Character?",
                body=f"Are you sure you want to delete '{underlying_item.display_name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, underlying_item)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        if response == "delete":
            self.project_manager.remove_character(char_gobject.character_data)
            pos = self.model.find(char_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
