"""The quest editor for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Quest, QuestGObject, Objective, ObjectiveGObject


class QuestEditorDialog(Adw.MessageDialog):
    """A dialog for adding and editing quests."""

    def __init__(self, parent, project_manager, quest=None, **kwargs):
        """Initializes a new QuestEditorDialog instance."""
        super().__init__(transient_for=parent, modal=True, **kwargs)
        self.set_heading("Add New Quest" if quest is None else "Edit Quest")
        self.project_manager = project_manager
        self.quest = quest

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        group = Adw.PreferencesGroup()
        content.append(group)

        self.id_entry = Gtk.Entry(text=quest.id if quest else "")
        self.id_entry.set_tooltip_text(
            "A unique string identifier for the quest (e.g., 'main_quest_01').")
        group.add(self._create_action_row(
            "ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=quest.name if quest else "")
        self.name_entry.set_tooltip_text("The in-game name of the quest.")
        group.add(self._create_action_row(
            "Name", "In-game display name", self.name_entry))

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        self.id_entry.connect("changed", self._validate)
        self.name_entry.connect("changed", self._validate)
        self._validate(None)

    def _validate(self, entry):
        """Validates the input fields."""
        is_valid = True
        id_text = self.id_entry.get_text()
        is_new_quest = self.quest is None
        id_is_duplicate = any(q.id == id_text for q in self.project_manager.data.quests if (
            is_new_quest or q.id != self.quest.id))

        if not id_text or id_is_duplicate:
            if not id_text:
                self.id_entry.set_tooltip_text("ID cannot be empty.")
            else:
                self.id_entry.set_tooltip_text("This ID is already in use.")
            is_valid = False
        else:
            self.id_entry.set_tooltip_text("")

        if not self.name_entry.get_text():
            self.name_entry.set_tooltip_text("Name cannot be empty.")
            is_valid = False
        else:
            self.name_entry.set_tooltip_text("")

        self.set_response_enabled("ok", is_valid)

    def _create_action_row(self, title, subtitle, widget):
        """Creates an Adw.ActionRow."""
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(widget)
        row.set_activatable_widget(widget)
        return row


class ObjectiveEditorDialog(Adw.MessageDialog):
    """A dialog for adding and editing objectives."""

    def __init__(self, parent, project_manager, quest, objective=None, **kwargs):
        """Initializes a new ObjectiveEditorDialog instance."""
        super().__init__(transient_for=parent, modal=True, **kwargs)
        self.set_heading(
            "Add New Objective" if objective is None else "Edit Objective")
        self.project_manager = project_manager
        self.quest = quest
        self.objective = objective

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        group = Adw.PreferencesGroup()
        content.append(group)

        self.id_entry = Gtk.Entry(text=objective.id if objective else "")
        self.id_entry.set_tooltip_text(
            "A unique string identifier for the objective (e.g., 'obj_01').")
        group.add(self._create_action_row(
            "ID", "Unique string identifier", self.id_entry))

        self.name_entry = Gtk.Entry(text=objective.name if objective else "")
        self.name_entry.set_tooltip_text("The in-game name of the objective.")
        group.add(self._create_action_row(
            "Name", "In-game display name", self.name_entry))

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        self.id_entry.connect("changed", self._validate)
        self.name_entry.connect("changed", self._validate)
        self._validate(None)

    def _validate(self, entry):
        """Validates the input fields."""
        is_valid = True
        id_text = self.id_entry.get_text()
        is_new_objective = self.objective is None
        id_is_duplicate = any(obj.id == id_text for obj in self.quest.objectives if (
            is_new_objective or obj.id != self.objective.id))

        if not id_text or id_is_duplicate:
            if not id_text:
                self.id_entry.set_tooltip_text("ID cannot be empty.")
            else:
                self.id_entry.set_tooltip_text("This ID is already in use.")
            is_valid = False
        else:
            self.id_entry.set_tooltip_text("")

        if not self.name_entry.get_text():
            self.name_entry.set_tooltip_text("Name cannot be empty.")
            is_valid = False
        else:
            self.name_entry.set_tooltip_text("")

        self.set_response_enabled("ok", is_valid)

    def _create_action_row(self, title, subtitle, widget):
        """Creates an Adw.ActionRow."""
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(widget)
        row.set_activatable_widget(widget)
        return row


class QuestEditor(Adw.Bin):
    """A widget for editing quests.

    This editor provides a list of quests and a detail view for editing the
    selected quest's properties and objectives.
    """
    EDITOR_NAME = "Quests"
    VIEW_NAME = "quest_editor"
    ORDER = 9

    def __init__(self, project_manager, **kwargs):
        """Initializes a new QuestEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        print("DEBUG: QuestEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager

        self.main_box = self._build_ui()
        self.set_child(self.main_box)

        self._update_visibility()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        print("DEBUG: QuestEditor._build_ui")
        paned = Adw.OverlaySplitView()
        paned.set_sidebar(self._create_quest_list_panel())
        paned.set_content(self._create_quest_details_panel())
        return paned

    def _create_quest_list_panel(self):
        """Creates the panel with the list of quests."""
        print("DEBUG: QuestEditor._create_quest_list_panel")
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        header = Adw.HeaderBar()
        panel.append(header)

        add_button = Gtk.Button(icon_name="list-add-symbolic")
        add_button.connect("clicked", self._on_add_quest)
        header.pack_start(add_button)

        self.delete_quest_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_quest_button.set_sensitive(False)
        self.delete_quest_button.connect("clicked", self._on_delete_quest)
        header.pack_end(self.delete_quest_button)

        self.model = Gio.ListStore(item_type=QuestGObject)
        for quest in self.project_manager.data.quests:
            self.model.append(QuestGObject(quest))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.selection.connect("selection-changed", self._on_quest_selected)

        factory = Gtk.SignalListItemFactory()
        factory.connect(
            "setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect(
            "bind", self._bind_quest_list_item)

        self.quest_list_view = Gtk.ListView(
            model=self.selection, factory=factory)

        scrolled = Gtk.ScrolledWindow(child=self.quest_list_view)
        scrolled.set_vexpand(True)
        panel.append(scrolled)
        return panel

    def _bind_quest_list_item(self, factory, list_item):
        """Binds a quest list item to the data model."""
        label = list_item.get_child()
        quest_gobject = list_item.get_item()
        label.set_text(quest_gobject.name)

        # Two-way binding
        quest_gobject.bind_property("name", label, "label", GObject.BindingFlags.BIDIRECTIONAL)


    def _create_quest_details_panel(self):
        """Creates the panel for editing the quest details."""
        print("DEBUG: QuestEditor._create_quest_details_panel")
        self.quest_details = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.quest_details.set_margin_top(10)
        self.quest_details.set_margin_bottom(10)
        self.quest_details.set_margin_start(10)
        self.quest_details.set_margin_end(10)

        self.status_page = Adw.StatusPage(
            title="No Quest Selected", icon_name="dialog-question-symbolic")
        self.quest_details.append(self.status_page)

        return self.quest_details

    def _update_visibility(self):
        """Updates the visibility of the quest list and status page."""
        has_quests = self.model.get_n_items() > 0
        print(f"DEBUG: QuestEditor._update_visibility: has_quests={has_quests}")
        self.quest_list_view.get_parent().set_visible(has_quests)
        self.status_page.set_visible(not has_quests or self.selection.get_selected() == Gtk.INVALID_LIST_POSITION)


    def _on_quest_selected(self, selection, _):
        """Handles the selection-changed signal from the quest list."""
        print("DEBUG: QuestEditor._on_quest_selected")
        selected_quest_gobject = selection.get_selected_item()
        self.delete_quest_button.set_sensitive(selected_quest_gobject is not None)
        if selected_quest_gobject:
            self._display_quest_details(selected_quest_gobject.quest)
        else:
            self._clear_quest_details()
        self._update_visibility()

    def _display_quest_details(self, quest):
        """Displays the details of the selected quest."""
        print(f"DEBUG: QuestEditor._display_quest_details for quest: {quest.id}")
        self._clear_quest_details()

        if not quest:
            return

        clamp = Adw.Clamp()
        self.quest_details.append(clamp)

        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        clamp.set_child(details_box)

        group = Adw.PreferencesGroup()
        details_box.append(group)

        self.id_entry = Adw.EntryRow(title="ID", text=quest.id)
        self.id_entry.connect("apply", self._on_detail_changed, quest, "id")
        group.add(self.id_entry)

        self.name_entry = Adw.EntryRow(title="Name", text=quest.name)
        self.name_entry.connect("apply", self._on_detail_changed, quest, "name")
        group.add(self.name_entry)

        objective_group = Adw.PreferencesGroup(title="Objectives")
        details_box.append(objective_group)

        self.objective_list = self._setup_objective_list(quest)
        scrolled_window = Gtk.ScrolledWindow(child=self.objective_list)
        scrolled_window.set_min_content_height(200)
        objective_group.add(scrolled_window)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        details_box.append(button_box)

        add_obj_button = Gtk.Button(label="Add Objective")
        add_obj_button.connect("clicked", self._on_add_objective, quest)
        button_box.append(add_obj_button)

        edit_obj_button = Gtk.Button(label="Edit Objective")
        edit_obj_button.connect("clicked", self._on_edit_objective, quest)
        button_box.append(edit_obj_button)

        delete_obj_button = Gtk.Button(label="Delete Objective")
        delete_obj_button.connect("clicked", self._on_delete_objective, quest)
        button_box.append(delete_obj_button)

    def _setup_objective_list(self, quest):
        """Sets up the list of objectives for the selected quest."""
        print("DEBUG: QuestEditor._setup_objective_list")
        objective_list = Gtk.ColumnView()
        self.objective_model = Gio.ListStore(item_type=ObjectiveGObject)
        for objective in quest.objectives:
            self.objective_model.append(ObjectiveGObject(objective))

        self.objective_selection = Gtk.SingleSelection(
            model=self.objective_model)
        objective_list.set_model(self.objective_selection)

        self._create_objective_column(objective_list, "ID", "id")
        self._create_objective_column(objective_list, "Name", "name")

        return objective_list

    def _create_objective_column(self, objective_list, title, col_id):
        """Creates a column for the objective list."""
        factory = Gtk.SignalListItemFactory()
        factory.connect(
            "setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect(
            "bind", lambda _, list_item: list_item.get_child().set_text(getattr(list_item.get_item(), col_id)))

        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        objective_list.append_column(col)

    def _on_detail_changed(self, widget, quest, property_name):
        """Handles the changed signal from a detail entry."""
        print(f"DEBUG: QuestEditor._on_detail_changed: {property_name}")
        new_value = widget.get_text()
        original_id = quest.id

        # Update the model before changing the ID property
        if property_name == 'id':
            self.project_manager.update_quest(original_id, {property_name: new_value})
            quest.id = new_value
        else:
             setattr(quest, property_name, new_value)
             self.project_manager.set_dirty()

        # Refresh the main quest list view
        for i, item in enumerate(self.model):
            if item.quest == quest:
                self.model.items_changed(i, 1, 1)
                break

    def _on_add_quest(self, button):
        """Handles the clicked signal from the add quest button."""
        print("DEBUG: QuestEditor._on_add_quest")
        dialog = QuestEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_quest_dialog_response)
        dialog.present()

    def _on_add_quest_dialog_response(self, dialog, response):
        """Handles the response from the add quest dialog."""
        print(f"DEBUG: QuestEditor._on_add_quest_dialog_response: {response}")
        if response == "ok":
            new_quest = self.project_manager.add_quest(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text()
            )
            self.model.append(QuestGObject(new_quest))
            self._update_visibility()
        dialog.destroy()

    def _on_delete_quest(self, button):
        """Handles the clicked signal from the delete quest button."""
        print("DEBUG: QuestEditor._on_delete_quest")
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
            dialog.set_response_appearance(
                "delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect(
                "response", self._on_delete_quest_dialog_response, selected_quest_gobject)
            dialog.present()

    def _on_delete_quest_dialog_response(self, dialog, response, quest_gobject):
        """Handles the response from the delete quest dialog."""
        print(f"DEBUG: QuestEditor._on_delete_quest_dialog_response: {response}")
        if response == "delete":
            self.project_manager.remove_quest(quest_gobject.id)
            is_found, pos = self.model.find(quest_gobject)
            if is_found:
                self.model.remove(pos)
            self._update_visibility()
        dialog.destroy()

    def _on_add_objective(self, button, quest):
        """Handles the clicked signal from the add objective button."""
        print("DEBUG: QuestEditor._on_add_objective")
        dialog = ObjectiveEditorDialog(
            self.get_root(), self.project_manager, quest)
        dialog.connect(
            "response", self._on_add_objective_dialog_response, quest)
        dialog.present()

    def _on_add_objective_dialog_response(self, dialog, response, quest):
        """Handles the response from the add objective dialog."""
        print(f"DEBUG: QuestEditor._on_add_objective_dialog_response: {response}")
        if response == "ok":
            new_objective = self.project_manager.add_objective_to_quest(
                quest.id,
                dialog.id_entry.get_text(),
                dialog.name_entry.get_text()
            )
            if new_objective:
                self.objective_model.append(ObjectiveGObject(new_objective))
        dialog.destroy()

    def _on_edit_objective(self, button, quest):
        """Handles the clicked signal from the edit objective button."""
        print("DEBUG: QuestEditor._on_edit_objective")
        selected_objective_gobject = self.objective_selection.get_selected_item()
        if selected_objective_gobject:
            dialog = ObjectiveEditorDialog(
                self.get_root(), self.project_manager, quest, objective=selected_objective_gobject.objective)
            dialog.connect(
                "response", self._on_edit_objective_dialog_response, quest, selected_objective_gobject)
            dialog.present()

    def _on_edit_objective_dialog_response(self, dialog, response, quest, objective_gobject):
        """Handles the response from the edit objective dialog."""
        print(f"DEBUG: QuestEditor._on_edit_objective_dialog_response: {response}")
        if response == "ok":
            self.project_manager.update_objective(quest.id, objective_gobject.id, {
                'id': dialog.id_entry.get_text(),
                'name': dialog.name_entry.get_text()
            })
            is_found, pos = self.objective_model.find(objective_gobject)
            if is_found:
                self.objective_model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_objective(self, button, quest):
        """Handles the clicked signal from the delete objective button."""
        print("DEBUG: QuestEditor._on_delete_objective")
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
            dialog.set_response_appearance(
                "delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect(
                "response", self._on_delete_objective_dialog_response, quest, selected_objective_gobject)
            dialog.present()

    def _on_delete_objective_dialog_response(self, dialog, response, quest, objective_gobject):
        """Handles the response from the delete objective dialog."""
        print(f"DEBUG: QuestEditor._on_delete_objective_dialog_response: {response}")
        if response == "delete":
            self.project_manager.remove_objective_from_quest(
                quest.id, objective_gobject.id)
            is_found, pos = self.objective_model.find(objective_gobject)
            if is_found:
                self.objective_model.remove(pos)
        dialog.destroy()

    def _clear_quest_details(self):
        """Clears the quest details panel."""
        print("DEBUG: QuestEditor._clear_quest_details")
        while child := self.quest_details.get_first_child():
            self.quest_details.remove(child)
        self.quest_details.append(self.status_page)
