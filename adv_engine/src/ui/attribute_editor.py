import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw
from ..core.data_schemas import Attribute, AttributeGObject

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, Gdk
from ..core.data_schemas import Attribute, AttributeGObject

class AttributeEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, attribute=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Attribute" if attribute is None else "Edit Attribute")
        self.project_manager = project_manager
        self.attribute = attribute

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

        self.id_entry = Gtk.Entry(text=attribute.id if attribute else "")
        self.id_entry.set_tooltip_text("A unique string identifier for the attribute (e.g., 'strength').")
        group.add(self._create_action_row("ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=attribute.name if attribute else "")
        self.name_entry.set_tooltip_text("The in-game name of the attribute.")
        group.add(self._create_action_row("Name", "In-game display name", self.name_entry))

        self.initial_value_entry = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=99999, step_increment=1), value=attribute.initial_value if attribute else 0)
        self.initial_value_entry.set_tooltip_text("The starting value of the attribute.")
        group.add(self._create_action_row("Initial Value", "Starting value", self.initial_value_entry))

        self.max_value_entry = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=99999, step_increment=1), value=attribute.max_value if attribute else 100)
        self.max_value_entry.set_tooltip_text("The maximum value of the attribute.")
        group.add(self._create_action_row("Max Value", "Maximum value", self.max_value_entry))

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        self.id_entry.connect("changed", self._validate)
        self.name_entry.connect("changed", self._validate)
        self._validate(None)

    def _validate(self, entry):
        is_valid = True
        id_text = self.id_entry.get_text()
        is_new_attr = self.attribute is None
        id_is_duplicate = any(attr.id == id_text for attr in self.project_manager.data.attributes if (is_new_attr or attr.id != self.attribute.id))

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

class AttributeEditor(Gtk.Box):
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
        title = Gtk.Label(label="Attribute Editor", halign=Gtk.Align.START, hexpand=True,
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
        self.search_entry.set_placeholder_text("Search attributes...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.main_box.append(self.search_entry)

        # --- Column View for Attributes ---
        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=AttributeGObject)
        for attribute in self.project_manager.data.attributes:
            self.model.append(AttributeGObject(attribute))

        self.filter_model = Gtk.FilterListModel(model=self.model)
        self.filter = Gtk.CustomFilter.new(self._filter_func, self.filter_model)
        self.filter_model.set_filter(self.filter)

        self.sort_model = Gtk.SortListModel(model=self.filter_model)

        self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.column_view.set_model(self.selection)

        # Define columns
        self._create_column("ID", Gtk.StringSorter(), lambda attr: attr.id)
        self._create_column("Name", Gtk.StringSorter(), lambda attr: attr.name)
        self._create_column("Initial Value", Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(AttributeGObject, None, "initial_value")), lambda attr: str(attr.initial_value))
        self._create_column("Max Value", Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(AttributeGObject, None, "max_value")), lambda attr: str(attr.max_value))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)

        self.main_box.append(scrolled_window)

        # --- Empty State ---
        self.empty_state = Adw.StatusPage(title="No Attributes",
                                          description="Create a new attribute to begin.",
                                          icon_name="document-new-symbolic")
        self.add_attr_button_empty = Gtk.Button(label="Create Attribute")
        self.add_attr_button_empty.connect("clicked", self._on_add_clicked)
        self.empty_state.set_child(self.add_attr_button_empty)
        self.append(self.empty_state)

        self.model.connect("items-changed", lambda model, pos, rem, add: self.update_visibility())
        self.update_visibility()

    def update_visibility(self):
        has_attrs = self.model.get_n_items() > 0
        self.main_box.set_visible(has_attrs)
        self.empty_state.set_visible(not has_attrs)


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
                search_text in item.name.lower())

    def _on_search_changed(self, entry):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def _on_add_clicked(self, button):
        dialog = AttributeEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            new_attr = Attribute(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text(),
                initial_value=int(dialog.initial_value_entry.get_value()),
                max_value=int(dialog.max_value_entry.get_value())
            )
            self.project_manager.add_attribute(new_attr)
            self.model.append(AttributeGObject(new_attr))
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_attr_gobject = self.selection.get_selected_item()
        if selected_attr_gobject:
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = AttributeEditorDialog(self.get_root(), self.project_manager, attribute=underlying_item.attribute_data)
            dialog.connect("response", self._on_edit_dialog_response, underlying_item)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, attr_gobject):
        if response == "ok":
            attr_gobject.attribute_data.id = dialog.id_entry.get_text()
            attr_gobject.attribute_data.name = dialog.name_entry.get_text()
            attr_gobject.attribute_data.initial_value = int(dialog.initial_value_entry.get_value())
            attr_gobject.attribute_data.max_value = int(dialog.max_value_entry.get_value())
            self.project_manager.set_dirty(True)
            pos = self.model.find(attr_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_attr_gobject = self.selection.get_selected_item()
        if selected_attr_gobject:
            underlying_item = self.sort_model.get_item(self.selection.get_selected())
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Attribute?",
                body=f"Are you sure you want to delete '{underlying_item.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, underlying_item)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, attr_gobject):
        if response == "delete":
            self.project_manager.remove_attribute(attr_gobject.attribute_data)
            pos = self.model.find(attr_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
