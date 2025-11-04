import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, Gdk
from ..core.data_schemas import Quest, QuestGObject, Objective, ObjectiveGObject

class QuestEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, quest=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Quest" if quest is None else "Edit Quest")
        self.project_manager = project_manager
        self.quest = quest

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

        self.id_entry = Gtk.Entry(text=quest.id if quest else "")
        self.id_entry.set_tooltip_text("A unique string identifier for the quest (e.g., 'main_quest_01').")
        group.add(self._create_action_row("ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=quest.name if quest else "")
        self.name_entry.set_tooltip_text("The in-game name of the quest.")
        group.add(self._create_action_row("Name", "In-game display name", self.name_entry))

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
        is_new_quest = self.quest is None
        id_is_duplicate = any(q.id == id_text for q in self.project_manager.data.quests if (is_new_quest or q.id != self.quest.id))

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

class ObjectiveEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, quest, objective=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Objective" if objective is None else "Edit Objective")
        self.project_manager = project_manager
        self.quest = quest
        self.objective = objective

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

        self.id_entry = Gtk.Entry(text=objective.id if objective else "")
        self.id_entry.set_tooltip_text("A unique string identifier for the objective (e.g., 'obj_01').")
        group.add(self._create_action_row("ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=objective.name if objective else "")
        self.name_entry.set_tooltip_text("The in-game name of the objective.")
        group.add(self._create_action_row("Name", "In-game display name", self.name_entry))

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
        is_new_objective = self.objective is None
        id_is_duplicate = any(obj.id == id_text for obj in self.quest.objectives if (is_new_objective or obj.id != self.objective.id))

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

class QuestEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        # Quest List
        self.quest_list = Gtk.ColumnView()
        self.quest_list.set_vexpand(True)
        self.model = Gio.ListStore(item_type=QuestGObject)
        for quest in self.project_manager.data.quests:
            self.model.append(QuestGObject(quest))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.quest_list.set_model(self.selection)

        self._create_column("ID", Gtk.StringSorter(), lambda quest: quest.id)
        self._create_column("Name", Gtk.StringSorter(), lambda quest: quest.name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.quest_list)
        self.append(scrolled_window)

        # Quest Details
        self.quest_details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.quest_details.set_hexpand(True)
        self.append(self.quest_details)

        self.selection.connect("selection-changed", self._on_quest_selected)
        self._on_quest_selected(self.selection, None)

    def _create_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.quest_list.append_column(col)

    def _on_quest_selected(self, selection, _):
        selected_quest_gobject = selection.get_selected_item()
        if selected_quest_gobject:
            self._display_quest_details(selected_quest_gobject.quest_data)
        else:
            self._clear_quest_details()

    def _display_quest_details(self, quest):
        self._clear_quest_details()

        if not quest:
            return

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.quest_details.append(grid)

        grid.attach(Gtk.Label(label="ID:"), 0, 0, 1, 1)
        id_entry = Gtk.Entry(text=quest.id)
        id_entry.connect("changed", self._on_detail_changed, quest, "id")
        grid.attach(id_entry, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Name:"), 0, 1, 1, 1)
        name_entry = Gtk.Entry(text=quest.name)
        name_entry.connect("changed", self._on_detail_changed, quest, "name")
        grid.attach(name_entry, 1, 1, 1, 1)

        # Objectives List
        self.objective_list = Gtk.ColumnView()
        self.objective_list.set_vexpand(True)
        self.objective_model = Gio.ListStore(item_type=ObjectiveGObject)
        for objective in quest.objectives:
            self.objective_model.append(ObjectiveGObject(objective))

        self.objective_selection = Gtk.SingleSelection(model=self.objective_model)
        self.objective_list.set_model(self.objective_selection)

        self._create_objective_column("ID", Gtk.StringSorter(), lambda obj: obj.id)
        self._create_objective_column("Name", Gtk.StringSorter(), lambda obj: obj.name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.objective_list)
        self.quest_details.append(scrolled_window)

        # Add and Delete buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        add_button = Gtk.Button(label="Add Quest")
        add_button.connect("clicked", self._on_add_quest)
        button_box.append(add_button)

        edit_button = Gtk.Button(label="Edit Quest")
        edit_button.connect("clicked", self._on_edit_quest)
        button_box.append(edit_button)

        delete_button = Gtk.Button(label="Delete Quest")
        delete_button.connect("clicked", self._on_delete_quest)
        button_box.append(delete_button)
        self.quest_details.append(button_box)

        obj_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        add_obj_button = Gtk.Button(label="Add Objective")
        add_obj_button.connect("clicked", self._on_add_objective, quest)
        obj_button_box.append(add_obj_button)

        edit_obj_button = Gtk.Button(label="Edit Objective")
        edit_obj_button.connect("clicked", self._on_edit_objective, quest)
        obj_button_box.append(edit_obj_button)

        delete_obj_button = Gtk.Button(label="Delete Objective")
        delete_obj_button.connect("clicked", self._on_delete_objective, quest)
        obj_button_box.append(delete_obj_button)
        self.quest_details.append(obj_button_box)

    def _create_objective_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.objective_list.append_column(col)

    def _on_detail_changed(self, widget, quest, property_name):
        if isinstance(widget, Gtk.Entry):
            new_value = widget.get_text()
        else:
            return

        original_id = quest.id
        self.project_manager.update_quest(original_id, {property_name: new_value})
        if property_name == 'id':
            quest.id = new_value

        for i, item in enumerate(self.model):
            if item.id == original_id:
                setattr(item, property_name, new_value)
                self.model.items_changed(i, 1, 1)
                break

    def _on_add_quest(self, button):
        dialog = QuestEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_quest_dialog_response)
        dialog.present()

    def _on_add_quest_dialog_response(self, dialog, response):
        if response == "ok":
            new_quest = self.project_manager.add_quest(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text()
            )
            self.model.append(QuestGObject(new_quest))
        dialog.destroy()

    def _on_edit_quest(self, button):
        selected_quest_gobject = self.selection.get_selected_item()
        if selected_quest_gobject:
            dialog = QuestEditorDialog(self.get_root(), self.project_manager, quest=selected_quest_gobject.quest_data)
            dialog.connect("response", self._on_edit_quest_dialog_response, selected_quest_gobject)
            dialog.present()

    def _on_edit_quest_dialog_response(self, dialog, response, quest_gobject):
        if response == "ok":
            quest_gobject.quest_data.id = dialog.id_entry.get_text()
            quest_gobject.quest_data.name = dialog.name_entry.get_text()
            self.project_manager.set_dirty(True)
            pos = self.model.find(quest_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_quest(self, button):
        selected_quest_gobject = self.selection.get_selected_item()
        if selected_quest_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Quest?",
                body=f"Are you sure you want to delete '{selected_quest_gobject.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_quest_dialog_response, selected_quest_gobject)
            dialog.present()

    def _on_delete_quest_dialog_response(self, dialog, response, quest_gobject):
        if response == "delete":
            self.project_manager.remove_quest(quest_gobject.id)
            pos = self.model.find(quest_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()

    def _on_add_objective(self, button, quest):
        dialog = ObjectiveEditorDialog(self.get_root(), self.project_manager, quest)
        dialog.connect("response", self._on_add_objective_dialog_response, quest)
        dialog.present()

    def _on_add_objective_dialog_response(self, dialog, response, quest):
        if response == "ok":
            new_objective = self.project_manager.add_objective_to_quest(
                quest.id,
                dialog.id_entry.get_text(),
                dialog.name_entry.get_text()
            )
            self.objective_model.append(ObjectiveGObject(new_objective))
        dialog.destroy()

    def _on_edit_objective(self, button, quest):
        selected_objective_gobject = self.objective_selection.get_selected_item()
        if selected_objective_gobject:
            dialog = ObjectiveEditorDialog(self.get_root(), self.project_manager, quest, objective=selected_objective_gobject.objective_data)
            dialog.connect("response", self._on_edit_objective_dialog_response, quest, selected_objective_gobject)
            dialog.present()

    def _on_edit_objective_dialog_response(self, dialog, response, quest, objective_gobject):
        if response == "ok":
            objective_gobject.objective_data.id = dialog.id_entry.get_text()
            objective_gobject.objective_data.name = dialog.name_entry.get_text()
            self.project_manager.set_dirty(True)
            pos = self.objective_model.find(objective_gobject)[1]
            if pos >= 0:
                self.objective_model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_objective(self, button, quest):
        selected_objective_gobject = self.objective_selection.get_selected_item()
        if selected_objective_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Objective?",
                body=f"Are you sure you want to delete '{selected_objective_gobject.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_objective_dialog_response, quest, selected_objective_gobject)
            dialog.present()

    def _on_delete_objective_dialog_response(self, dialog, response, quest, objective_gobject):
        if response == "delete":
            self.project_manager.remove_objective_from_quest(quest.id, objective_gobject.id)
            pos = self.objective_model.find(objective_gobject)[1]
            if pos >= 0:
                self.objective_model.remove(pos)
        dialog.destroy()

    def _clear_quest_details(self):
        while child := self.quest_details.get_first_child():
            self.quest_details.remove(child)
