import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Interaction, InteractionGObject, Item, Verb

class InteractionEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, interaction=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Interaction" if interaction is None else "Edit Interaction")

        self.project_manager = project_manager
        self.interaction = interaction

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        self.verb_model = Gio.ListStore(item_type=Verb)
        for verb in self.project_manager.data.verbs:
            self.verb_model.append(verb)

        self.item_model = Gio.ListStore(item_type=Item)
        for item in self.project_manager.data.items:
            self.item_model.append(item)

        self.logic_graph_model = Gio.ListStore(item_type=GObject.TYPE_STRING)
        for graph in self.project_manager.data.logic_graphs:
            self.logic_graph_model.append(graph.id)

        self.verb_dropdown = Gtk.DropDown(model=self.verb_model, expression=Gtk.PropertyExpression(Verb, None, "name"))
        self.primary_item_dropdown = Gtk.DropDown(model=self.item_model, expression=Gtk.PropertyExpression(Item, None, "name"))
        self.secondary_item_dropdown = Gtk.DropDown(model=self.item_model, expression=Gtk.PropertyExpression(Item, None, "name"))
        self.logic_graph_dropdown = Gtk.DropDown(model=self.logic_graph_model)

        self.hotspot_model = Gio.ListStore(item_type=Hotspot)
        for scene in self.project_manager.data.scenes:
            for hotspot in scene.hotspots:
                self.hotspot_model.append(hotspot)

        self.hotspot_dropdown = Gtk.DropDown(model=self.hotspot_model, expression=Gtk.PropertyExpression(Hotspot, None, "name"))

        content.append(self._create_row("Verb:", self.verb_dropdown))
        content.append(self._create_row("Primary Item:", self.primary_item_dropdown))
        content.append(self._create_row("Secondary Item:", self.secondary_item_dropdown))
        content.append(self._create_row("Target Hotspot:", self.hotspot_dropdown))
        content.append(self._create_row("Logic Graph:", self.logic_graph_dropdown))

        if interaction:
            self.verb_dropdown.set_selected(self.project_manager.get_verb_index(interaction.verb_id))
            self.primary_item_dropdown.set_selected(self.project_manager.get_item_index(interaction.primary_item_id))
            self.secondary_item_dropdown.set_selected(self.project_manager.get_item_index(interaction.secondary_item_id))
            self.logic_graph_dropdown.set_selected(self.project_manager.get_logic_graph_index(interaction.logic_graph_id))
            self.hotspot_dropdown.set_selected(self.project_manager.get_hotspot_index(interaction.target_hotspot_id))

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

class InteractionEditor(Gtk.Box):
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
        title = Gtk.Label(label="Interaction Editor", halign=Gtk.Align.START, hexpand=True,
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

        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=InteractionGObject)
        for interaction in self.project_manager.data.interactions:
            self.model.append(InteractionGObject(interaction))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

        self._create_column("ID", lambda item: item.id)
        self._create_column("Verb", lambda item: self.project_manager.get_verb_name(item.verb_id))
        self._create_column("Primary Item", lambda item: self.project_manager.get_item_name(item.primary_item_id))
        self._create_column("Secondary Item", lambda item: self.project_manager.get_item_name(item.secondary_item_id))
        self._create_column("Logic Graph", lambda item: item.logic_graph_id)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)

        self.main_box.append(scrolled_window)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.column_view.append_column(col)

    def _on_add_clicked(self, button):
        dialog = InteractionEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            verb = dialog.verb_dropdown.get_selected_item()
            primary_item = dialog.primary_item_dropdown.get_selected_item()
            secondary_item = dialog.secondary_item_dropdown.get_selected_item()
            hotspot = dialog.hotspot_dropdown.get_selected_item()
            logic_graph_id = dialog.logic_graph_dropdown.get_selected_item()

            new_id = f"{verb.id}_{primary_item.id}"
            if secondary_item:
                new_id += f"_{secondary_item.id}"
            if hotspot:
                new_id += f"_{hotspot.id}"


            new_interaction = Interaction(
                id=new_id,
                verb_id=verb.id,
                primary_item_id=primary_item.id,
                secondary_item_id=secondary_item.id if secondary_item else None,
                target_hotspot_id=hotspot.id if hotspot else None,
                logic_graph_id=logic_graph_id
            )
            self.project_manager.add_interaction(new_interaction)
            self.model.append(InteractionGObject(new_interaction))
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if selected_item:
            dialog = InteractionEditorDialog(self.get_root(), self.project_manager, interaction=selected_item.interaction_data)
            dialog.connect("response", self._on_edit_dialog_response, selected_item)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, interaction_gobject):
        if response == "ok":
            verb = dialog.verb_dropdown.get_selected_item()
            primary_item = dialog.primary_item_dropdown.get_selected_item()
            secondary_item = dialog.secondary_item_dropdown.get_selected_item()
            hotspot = dialog.hotspot_dropdown.get_selected_item()
            logic_graph_id = dialog.logic_graph_dropdown.get_selected_item()

            interaction_gobject.interaction_data.verb_id = verb.id
            interaction_gobject.interaction_data.primary_item_id = primary_item.id
            interaction_gobject.interaction_data.secondary_item_id = secondary_item.id if secondary_item else None
            interaction_gobject.interaction_data.target_hotspot_id = hotspot.id if hotspot else None
            interaction_gobject.interaction_data.logic_graph_id = logic_graph_id
            self.project_manager.set_dirty(True)
            pos = self.model.find(interaction_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)

        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if selected_item:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Interaction?",
                body=f"Are you sure you want to delete the interaction '{selected_item.id}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, selected_item)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, interaction_gobject):
        if response == "delete":
            self.project_manager.remove_interaction(interaction_gobject.interaction_data)
            pos = self.model.find(interaction_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
