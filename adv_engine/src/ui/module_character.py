import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, Gdk
from ..core.data_schemas import Character, CharacterGObject

class CharacterEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, character=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Character" if character is None else "Edit Character")
        self.project_manager = project_manager
        self.character = character

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

        self.id_entry = Gtk.Entry(text=character.id if character else "")
        self.id_entry.set_tooltip_text("A unique string identifier for the character (e.g., 'npc_bartender').")
        group.add(self._create_action_row("ID", "Unique string identifier", self.id_entry))

        self.display_name_entry = Gtk.Entry(text=character.display_name if character else "")
        self.display_name_entry.set_tooltip_text("The in-game name of the character.")
        group.add(self._create_action_row("Display Name", "In-game display name", self.display_name_entry))

        self.dialogue_start_id_entry = Gtk.Entry(text=character.dialogue_start_id if character else "")
        self.dialogue_start_id_entry.set_tooltip_text("The ID of the dialogue graph to start when talking to this character.")
        group.add(self._create_action_row("Dialogue Start ID", "Starting dialogue graph ID", self.dialogue_start_id_entry))

        self.is_merchant_check = Gtk.CheckButton(active=character.is_merchant if character else False)
        self.is_merchant_check.set_tooltip_text("Whether this character is a merchant.")
        group.add(self._create_action_row("Is Merchant", "Can this character open a shop?", self.is_merchant_check))

        self.shop_id_entry = Gtk.Entry(text=character.shop_id if character else "")
        self.shop_id_entry.set_tooltip_text("The ID of the shop this character opens.")
        group.add(self._create_action_row("Shop ID", "Shop identifier", self.shop_id_entry))

        # Portrait Asset Dropdown
        self.portrait_asset_id_dropdown = self._create_asset_dropdown(character)
        self.portrait_asset_id_dropdown.set_tooltip_text("The asset to use for the character's portrait.")
        self.portrait_asset_id_dropdown.connect("notify::selected-item", self._on_portrait_selection_changed)
        group.add(self._create_action_row("Portrait Asset", "Asset for the character's portrait", self.portrait_asset_id_dropdown))

        # Portrait Preview
        self.portrait_preview = Gtk.Picture()
        self.portrait_preview.set_size_request(256, 256)
        self._update_portrait_preview(character.portrait_asset_id if character else None)
        content.append(self.portrait_preview)

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        # Connect validation signals
        self.id_entry.connect("changed", self._validate)
        self.display_name_entry.connect("changed", self._validate)
        self._validate(None)

    def _validate(self, entry):
        is_valid = True
        # Validate ID
        id_text = self.id_entry.get_text()
        is_new_char = self.character is None
        id_is_duplicate = any(char.id == id_text for char in self.project_manager.data.characters if (is_new_char or char.id != self.character.id))

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
        if not self.display_name_entry.get_text():
            self.display_name_entry.add_css_class("error")
            self.display_name_entry.set_tooltip_text("Display Name cannot be empty.")
            is_valid = False
        else:
            self.display_name_entry.remove_css_class("error")
            self.display_name_entry.set_tooltip_text("")

        self.set_response_enabled("ok", is_valid)

    def _create_asset_dropdown(self, character):
        image_assets = [asset.id for asset in self.project_manager.data.assets if asset.asset_type in ["sprite", "animation"]]
        dropdown = Gtk.DropDown.new_from_strings(["None"] + image_assets)
        if character and character.portrait_asset_id in image_assets:
            dropdown.set_selected(image_assets.index(character.portrait_asset_id) + 1)
        else:
            dropdown.set_selected(0)
        return dropdown

    def _on_portrait_selection_changed(self, dropdown, _):
        selected_item = dropdown.get_selected_item()
        if selected_item:
            asset_id = selected_item.get_string()
            self._update_portrait_preview(asset_id)

    def _update_portrait_preview(self, asset_id):
        if asset_id and asset_id != "None":
            asset = next((a for a in self.project_manager.data.assets if a.id == asset_id), None)
            if asset:
                full_path = os.path.join(self.project_manager.project_path, asset.file_path)
                if os.path.exists(full_path):
                    self.portrait_preview.set_filename(full_path)
                else:
                    self.portrait_preview.set_filename(None) # Clear preview if path is invalid
            else:
                self.portrait_preview.set_filename(None)
        else:
            self.portrait_preview.set_filename(None)

    def _create_action_row(self, title, subtitle, widget):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(widget)
        row.set_activatable_widget(widget)
        return row

class CharacterManager(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        # Character List
        self.character_list = Gtk.ColumnView()
        self.character_list.set_vexpand(True)
        self.character_list.set_size_request(200, -1)
        self.model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            self.model.append(CharacterGObject(character))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.character_list.set_model(self.selection)

        self._create_column("ID", Gtk.StringSorter(), lambda char: char.id)
        self._create_column("Name", Gtk.StringSorter(), lambda char: char.display_name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.character_list)
        self.append(scrolled_window)

        # Character Details
        self.character_details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.character_details.set_hexpand(True)
        self.append(self.character_details)

        self.selection.connect("selection-changed", self._on_character_selected)
        self._on_character_selected(self.selection, None)

    def _create_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.character_list.append_column(col)

    def _on_character_selected(self, selection, _):
        selected_character_gobject = selection.get_selected_item()
        if selected_character_gobject:
            self._display_character_details(selected_character_gobject.character_data)
        else:
            self._clear_character_details()

    def _display_character_details(self, character):
        self._clear_character_details()

        if not character:
            return

        group = Adw.PreferencesGroup()
        self.character_details.append(group)

        id_entry = Gtk.Entry(text=character.id)
        id_entry.connect("changed", self._on_detail_changed, character, "id")
        group.add(self._create_action_row("ID", "Unique string identifier", id_entry))

        name_entry = Gtk.Entry(text=character.display_name)
        name_entry.connect("changed", self._on_detail_changed, character, "display_name")
        group.add(self._create_action_row("Display Name", "In-game display name", name_entry))

        dialogue_entry = Gtk.Entry(text=character.dialogue_start_id)
        dialogue_entry.connect("changed", self._on_detail_changed, character, "dialogue_start_id")
        group.add(self._create_action_row("Dialogue Start ID", "Starting dialogue graph ID", dialogue_entry))

        merchant_check = Gtk.CheckButton(active=character.is_merchant)
        merchant_check.connect("toggled", self._on_detail_changed, character, "is_merchant")
        group.add(self._create_action_row("Is Merchant", "Can this character open a shop?", merchant_check))

        shop_entry = Gtk.Entry(text=character.shop_id)
        shop_entry.connect("changed", self._on_detail_changed, character, "shop_id")
        group.add(self._create_action_row("Shop ID", "Shop identifier", shop_entry))

        # Add and Delete buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        add_button = Gtk.Button(label="Add")
        add_button.connect("clicked", self._on_add_character)
        button_box.append(add_button)

        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self._on_delete_character)
        button_box.append(delete_button)
        self.character_details.append(button_box)

    def _on_detail_changed(self, widget, character, property_name):
        if isinstance(widget, Gtk.Entry):
            new_value = widget.get_text()
        elif isinstance(widget, Gtk.CheckButton):
            new_value = widget.get_active()
        else:
            return

        original_id = character.id
        self.project_manager.update_character(original_id, {property_name: new_value})

        # If the ID itself was changed, we need to update our reference to it
        if property_name == 'id':
            character.id = new_value

        # Update the list view as well
        for i, item in enumerate(self.model):
            if item.id == original_id:
                setattr(item, property_name, new_value)
                self.model.items_changed(i, 1, 1)
                break

    def _on_add_character(self, button):
        dialog = CharacterEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            portrait_asset_id = dialog.portrait_asset_id_dropdown.get_selected_item().get_string()
            if portrait_asset_id == "None":
                portrait_asset_id = None
            new_char = Character(
                id=dialog.id_entry.get_text(),
                display_name=dialog.display_name_entry.get_text(),
                dialogue_start_id=dialog.dialogue_start_id_entry.get_text(),
                is_merchant=dialog.is_merchant_check.get_active(),
                shop_id=dialog.shop_id_entry.get_text(),
                portrait_asset_id=portrait_asset_id
            )
            self.project_manager.add_character(new_char)
            self.model.append(CharacterGObject(new_char))
        dialog.destroy()

    def _on_delete_character(self, button):
        selected_character_gobject = self.selection.get_selected_item()
        if selected_character_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Character?",
                body=f"Are you sure you want to delete '{selected_character_gobject.display_name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, selected_character_gobject)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        if response == "delete":
            self.project_manager.remove_character(char_gobject.character_data)
            pos = self.model.find(char_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()

    def _clear_character_details(self):
        for child in self.character_details.observe_children():
            self.character_details.remove(child)
