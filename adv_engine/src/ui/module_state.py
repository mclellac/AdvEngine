import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject
from ..core.data_schemas import GlobalVariableGObject

class GlobalStateEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.model = Gio.ListStore(item_type=GlobalVariableGObject)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_setup)
        factory.connect("bind", self._on_factory_bind)

        self.list_view = Gtk.ListView(model=Gtk.SingleSelection(model=self.model), factory=factory)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.list_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        self.append(scrolled_window)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        add_button = Gtk.Button(label="Add")
        add_button.connect("clicked", self.on_add_clicked)
        edit_button = Gtk.Button(label="Edit")
        edit_button.connect("clicked", self.on_edit_clicked)
        remove_button = Gtk.Button(label="Remove")
        remove_button.connect("clicked", self.on_remove_clicked)
        button_box.append(add_button)
        button_box.append(edit_button)
        button_box.append(remove_button)
        self.append(button_box)

        self.refresh_variables()

    def refresh_variables(self):
        self.model.remove_all()
        for var in self.project_manager.data.global_variables:
            self.model.append(GlobalVariableGObject(var))

    def _on_factory_setup(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(5)
        box.set_margin_end(5)

        box.append(Gtk.Label(width_request=100, xalign=0)) # ID
        box.append(Gtk.Label(hexpand=True, xalign=0)) # Name
        box.append(Gtk.Label(width_request=80, xalign=0)) # Type
        box.append(Gtk.Label(width_request=100, xalign=0)) # Initial Value
        box.append(Gtk.Label(width_request=150, xalign=0)) # Category
        list_item.set_child(box)

    def _on_factory_bind(self, factory, list_item):
        box = list_item.get_child()
        gobj = list_item.get_item()

        box.get_first_child().set_text(gobj.id)
        box.get_children()[1].set_text(gobj.name)
        box.get_children()[2].set_text(gobj.type)
        box.get_children()[3].set_text(gobj.initial_value_str)
        box.get_children()[4].set_text(gobj.category)

    def on_add_clicked(self, button):
        dialog = self.create_variable_dialog("Create New Variable")

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                name, type, value, category = self.get_dialog_values(dialog)
                if name:
                    self.project_manager.add_global_variable(name, type, value, category)
                    self.refresh_variables()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def on_edit_clicked(self, button):
        selected_item = self.list_view.get_model().get_selected_item()
        if not selected_item:
            return

        dialog = self.create_variable_dialog("Edit Variable", variable=selected_item.variable_data)

        # Populate dialog with existing data
        widgets = dialog.get_data("widgets")
        widgets[0].set_text(selected_item.name)
        widgets[1].set_selected(0 if selected_item.type == "bool" else 1 if selected_item.type == "int" else 2)
        widgets[2].set_text(selected_item.initial_value_str)
        widgets[3].set_text(selected_item.category)

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                name, type, value, category = self.get_dialog_values(dialog)
                if name:
                    selected_item.variable_data.name = name
                    selected_item.variable_data.type = type
                    selected_item.variable_data.initial_value = value
                    selected_item.variable_data.category = category
                    self.project_manager.set_dirty()
                    self.refresh_variables() # This is inefficient, but will work for now
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()


    def on_remove_clicked(self, button):
        selected_item = self.list_view.get_model().get_selected_item()
        if not selected_item:
            return

        dialog = Adw.MessageDialog(
            transient_for=self.get_native(),
            modal=True,
            heading="Delete Variable?",
            body=f"Are you sure you want to delete '{selected_item.name}'?"
        )
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("delete", "_Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dialog, response_id):
            if response_id == "delete":
                self.project_manager.data.global_variables.remove(selected_item.variable_data)
                self.project_manager.set_dirty()
                self.refresh_variables()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def create_variable_dialog(self, title, variable=None):
        dialog = Adw.MessageDialog(
            transient_for=self.get_native(),
            modal=True,
            heading=title
        )

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        name_entry = Gtk.Entry(placeholder_text="Variable Name")
        type_dropdown = Gtk.DropDown.new_from_strings(["bool", "int", "str"])
        value_entry = Gtk.Entry(placeholder_text="Initial Value")
        category_entry = Gtk.Entry(placeholder_text="Category (optional)")

        content.append(name_entry)
        content.append(type_dropdown)
        content.append(value_entry)
        content.append(category_entry)

        dialog.set_extra_child(content)
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("ok", "_OK")
        dialog.set_default_response("ok")

        # Store widgets for later access
        dialog.set_data("widgets", [name_entry, type_dropdown, value_entry, category_entry])

        return dialog

    def get_dialog_values(self, dialog):
        widgets = dialog.get_data("widgets")
        name = widgets[0].get_text()
        type = widgets[1].get_selected_item().get_string()
        value_str = widgets[2].get_text()
        category = widgets[3].get_text() or "Default"

        # Coerce value to the correct type
        if type == "bool":
            value = value_str.lower() in ["true", "1"]
        elif type == "int":
            value = int(value_str) if value_str else 0
        else:
            value = value_str

        return name, type, value, category
