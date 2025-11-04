import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject

from ..core.data_schemas import Character, CharacterGObject
from ..core.project_manager import ProjectManager

class CharacterManager(Gtk.Box):
    """A widget for editing characters in a project, following HIG for inline editing."""

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
        self.add_button.set_tooltip_text("Add New Character")
        self.add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(self.add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_tooltip_text("Delete Selected Character")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        header.pack_end(self.delete_button)

        # --- Data Models ---
        self.model = Gio.ListStore(item_type=CharacterGObject)
        for character in self.project_manager.data.characters:
            self.model.append(CharacterGObject(character))

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

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(
            title="No Characters",
            description="Create a new character to get started.",
            icon_name="user-info-symbolic"
        )
        self.append(self.empty_state)

        self.model.connect("items-changed", self._update_visibility)
        self._update_visibility()

    def _update_visibility(self, *args):
        has_items = self.model.get_n_items() > 0
        self.main_box.set_visible(has_items)
        self.empty_state.set_visible(not has_items)

    def _setup_list_item(self, factory, list_item):
        """Set up the structure of a character editor 'card'."""
        group = Adw.PreferencesGroup()

        id_entry = Adw.EntryRow(title="ID")
        name_entry = Adw.EntryRow(title="Display Name")
        dialogue_entry = Adw.EntryRow(title="Dialogue Start ID")
        merchant_switch = Adw.SwitchRow(title="Is Merchant")
        shop_entry = Adw.EntryRow(title="Shop ID")

        image_assets = ["None"] + [asset.id for asset in self.project_manager.data.assets if asset.asset_type in ["sprite", "animation"]]
        portrait_combo = Adw.ComboRow(title="Portrait Asset", model=Gtk.StringList.new(image_assets))

        portrait_preview = Gtk.Picture(width_request=128, height_request=128, content_fit=Gtk.ContentFit.CONTAIN)

        group.add(id_entry)
        group.add(name_entry)
        group.add(dialogue_entry)
        group.add(merchant_switch)
        group.add(shop_entry)
        group.add(portrait_combo)
        group.add(portrait_preview)

        list_item._widgets = {
            "id": id_entry, "display_name": name_entry, "dialogue_start_id": dialogue_entry,
            "is_merchant": merchant_switch, "shop_id": shop_entry,
            "portrait_asset_id": portrait_combo, "preview": portrait_preview
        }
        list_item._bindings = []
        list_item._handler_ids = []
        list_item.set_child(group)

    def _bind_list_item(self, factory, list_item):
        """Bind a CharacterGObject to the widgets."""
        char_gobject = list_item.get_item()
        widgets = list_item._widgets

        bindings = [
            widgets["id"].bind_property("text", char_gobject, "id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            widgets["display_name"].bind_property("text", char_gobject, "display_name", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            widgets["dialogue_start_id"].bind_property("text", char_gobject, "dialogue_start_id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            widgets["is_merchant"].bind_property("active", char_gobject, "is_merchant", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
            widgets["shop_id"].bind_property("text", char_gobject, "shop_id", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE),
        ]
        list_item._bindings.extend(bindings)

        # Handle ComboRow selection
        combo = widgets["portrait_asset_id"]
        model = combo.get_model()

        # Find and set initial selection
        for i in range(model.get_n_items()):
            if model.get_string(i) == char_gobject.portrait_asset_id:
                combo.set_selected(i)
                break

        def on_combo_changed(*args):
            selected_item = combo.get_selected_item()
            char_gobject.portrait_asset_id = selected_item.get_string() if selected_item else "None"
            self.project_manager.set_dirty(True)

        # Handle preview update
        def update_preview(*args):
            asset_id = char_gobject.portrait_asset_id
            preview = widgets["preview"]
            if asset_id and asset_id != "None":
                asset = next((a for a in self.project_manager.data.assets if a.id == asset_id), None)
                if asset and os.path.exists(os.path.join(self.project_manager.project_path, asset.file_path)):
                    preview.set_filename(os.path.join(self.project_manager.project_path, asset.file_path))
                else:
                    preview.set_filename(None)
            else:
                preview.set_filename(None)

        update_preview() # Initial update

        handlers = [
            widgets["id"].connect("apply", lambda w: self.project_manager.set_dirty(True)),
            widgets["display_name"].connect("apply", lambda w: self.project_manager.set_dirty(True)),
            widgets["shop_id"].connect("apply", lambda w: self.project_manager.set_dirty(True)),
            char_gobject.connect("notify::is-merchant", lambda *args: self.project_manager.set_dirty(True)),
            char_gobject.connect("notify::portrait-asset-id", update_preview),
            combo.connect("notify::selected", on_combo_changed),
        ]
        list_item._handler_ids.extend(handlers)


    def _unbind_list_item(self, factory, list_item):
        """Disconnect all handlers and unbind all properties."""
        for binding in list_item._bindings:
            binding.unbind()
        list_item._bindings.clear()

        char_gobject = list_item.get_item()
        widgets = list_item._widgets
        for handler_id in list_item._handler_ids:
            # Disconnect from all widgets and the gobject itself
            for widget in widgets.values():
                if isinstance(widget, Gtk.Widget) and widget.is_connected(handler_id):
                    widget.disconnect(handler_id)
            if char_gobject and char_gobject.is_connected(handler_id):
                char_gobject.disconnect(handler_id)
        list_item._handler_ids.clear()


    def _on_add_clicked(self, button):
        new_id_base = "new_char"
        new_id = new_id_base
        count = 1
        existing_ids = {c.id for c in self.project_manager.data.characters}
        while new_id in existing_ids:
            new_id = f"{new_id_base}_{count}"
            count += 1

        new_char_data = Character(id=new_id, display_name="New Character", dialogue_start_id="", is_merchant=False, shop_id="", portrait_asset_id=None)
        self.project_manager.add_character(new_char_data)
        gobject = CharacterGObject(new_char_data)
        self.model.append(gobject)
        self.selection.set_selected(self.model.get_n_items() - 1)

    def _on_delete_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            heading="Delete Character?",
            body=f"Are you sure you want to delete '{selected_item.display_name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self._on_delete_dialog_response, selected_item)
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response, char_gobject):
        if response == "delete":
            if self.project_manager.remove_character(char_gobject.character_data):
                is_found, pos = self.model.find(char_gobject)
                if is_found:
                    self.model.remove(pos)
        dialog.destroy()

    def _on_selection_changed(self, selection_model, position, n_items):
        self.delete_button.set_sensitive(selection_model.get_selected() != Gtk.INVALID_LIST_POSITION)
