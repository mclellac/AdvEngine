"""The quest editor for the AdvEngine application."""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Quest, QuestGObject, Objective, ObjectiveGObject


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_quest.ui"))
class QuestEditor(Adw.Bin):
    """A widget for editing quests."""

    __gtype_name__ = "QuestEditor"

    EDITOR_NAME = "Quests"
    VIEW_NAME = "quest_editor"
    ORDER = 9

    add_quest_button = Gtk.Template.Child()
    delete_quest_button = Gtk.Template.Child()
    quest_list_view = Gtk.Template.Child()
    quest_details_panel = Gtk.Template.Child()
    status_page = Gtk.Template.Child()

    def __init__(self, project_manager, settings_manager, **kwargs):
        """Initializes a new QuestEditor instance."""
        print("DEBUG: QuestEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager

        self._setup_quest_list()
        self._connect_signals()
        self._update_visibility()

    def _setup_quest_list(self):
        """Sets up the quest list and its model."""
        self.model = Gio.ListStore(item_type=QuestGObject)
        for quest in self.project_manager.data.quests:
            self.model.append(QuestGObject(quest))

        self.selection = Gtk.SingleSelection(model=self.model)

        factory = Gtk.SignalListItemFactory()
        factory.connect(
            "setup",
            lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)),
        )
        factory.connect("bind", self._bind_quest_list_item)

        self.quest_list_view.set_model(self.selection)
        self.quest_list_view.set_factory(factory)

    def _connect_signals(self):
        """Connects widget signals to handlers."""
        self.add_quest_button.connect("clicked", self._on_add_quest)
        self.delete_quest_button.connect("clicked", self._on_delete_quest)
        self.selection.connect("selection-changed", self._on_quest_selected)

    def _bind_quest_list_item(self, factory, list_item):
        """Binds a quest list item to the data model."""
        label = list_item.get_child()
        quest_gobject = list_item.get_item()
        label.set_text(quest_gobject.name)
        quest_gobject.bind_property(
            "name", label, "label", GObject.BindingFlags.BIDIRECTIONAL
        )

    def _update_visibility(self):
        """Updates the visibility of the quest list and status page."""
        has_quests = self.model.get_n_items() > 0
        is_quest_selected = self.selection.get_selected() != Gtk.INVALID_LIST_POSITION
        print(
            f"DEBUG: QuestEditor._update_visibility: has_quests={has_quests}, is_quest_selected={is_quest_selected}"
        )
        self.status_page.set_visible(not has_quests or not is_quest_selected)

    def _on_quest_selected(self, selection, _):
        """Handles the selection-changed signal from the quest list."""
        print("DEBUG: QuestEditor._on_quest_selected")
        selected_quest_gobject = selection.get_selected_item()
        self.delete_quest_button.set_sensitive(selected_quest_gobject is not None)
        self._display_quest_details(
            selected_quest_gobject.quest if selected_quest_gobject else None
        )
        self._update_visibility()

    def _display_quest_details(self, quest):
        """Displays the details of the selected quest."""
        print(
            f"DEBUG: QuestEditor._display_quest_details for quest: {quest.id if quest else 'None'}"
        )
        while child := self.quest_details_panel.get_first_child():
            if child != self.status_page:
                self.quest_details_panel.remove(child)

        if not quest:
            self.status_page.set_visible(True)
            return

        self.status_page.set_visible(False)

        clamp = Adw.Clamp()
        self.quest_details_panel.append(clamp)

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

        self.objective_selection = Gtk.SingleSelection(model=self.objective_model)
        objective_list.set_model(self.objective_selection)

        self._create_objective_column(objective_list, "ID", "id")
        self._create_objective_column(objective_list, "Name", "name")

        return objective_list

    def _create_objective_column(self, objective_list, title, col_id):
        """Creates a column for the objective list."""
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_objective_cell)
        factory.connect("bind", self._bind_objective_cell, col_id)
        factory.connect("unbind", self._unbind_objective_cell)
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        objective_list.append_column(col)

    def _setup_objective_cell(self, factory, list_item):
        """Sets up a cell for the objective list."""
        widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_objective_cell(self, factory, list_item, column_id):
        """Binds a cell for the objective list."""
        objective_gobject = list_item.get_item()
        widget = list_item.get_child()
        list_item.binding = widget.bind_property(
            "text",
            objective_gobject,
            column_id,
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        list_item.handler_id = widget.connect(
            "changed", lambda w: self.project_manager.set_dirty(True)
        )

    def _unbind_objective_cell(self, factory, list_item):
        """Unbinds a cell for the objective list."""
        if hasattr(list_item, "binding"):
            list_item.binding.unbind()
            del list_item.binding
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_detail_changed(self, widget, quest, property_name):
        """Handles the changed signal from a detail entry."""
        print(f"DEBUG: QuestEditor._on_detail_changed: {property_name}")
        new_value = widget.get_text()
        original_id = quest.id

        setattr(quest, property_name, new_value)
        self.project_manager.set_dirty(True)

        for i, item in enumerate(self.model):
            if item.quest.id == original_id:
                self.model.items_changed(i, 1, 1)
                break

    def _on_add_quest(self, button):
        """Handles the clicked signal from the add quest button."""
        new_id = f"quest_{len(self.project_manager.data.quests)}"
        new_quest = self.project_manager.add_quest(id=new_id, name="New Quest")
        self.model.append(QuestGObject(new_quest))
        self._update_visibility()

    def _on_delete_quest(self, button):
        """Handles the clicked signal from the delete quest button."""
        selected_quest_gobject = self.selection.get_selected_item()
        if selected_quest_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Quest?",
                body=f"Are you sure you want to delete '{selected_quest_gobject.name}'?",
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect(
                "response",
                self._on_delete_quest_dialog_response,
                selected_quest_gobject,
            )
            dialog.present()

    def _on_delete_quest_dialog_response(self, dialog, response, quest_gobject):
        """Handles the response from the delete quest dialog."""
        if response == "delete":
            self.project_manager.remove_quest(quest_gobject.quest.id)
            is_found, pos = self.model.find(quest_gobject)
            if is_found:
                self.model.remove(pos)
            self._update_visibility()
        dialog.destroy()

    def _on_add_objective(self, button, quest):
        """Handles the clicked signal from the add objective button."""
        new_id = f"objective_{len(quest.objectives)}"
        new_objective = self.project_manager.add_objective_to_quest(
            quest.id, new_id, "New Objective"
        )
        if new_objective:
            self.objective_model.append(ObjectiveGObject(new_objective))

    def _on_delete_objective(self, button, quest):
        """Handles the clicked signal from the delete objective button."""
        selected_objective_gobject = self.objective_selection.get_selected_item()
        if selected_objective_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Objective?",
                body=f"Are you sure you want to delete '{selected_objective_gobject.name}'?",
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect(
                "response",
                self._on_delete_objective_dialog_response,
                quest,
                selected_objective_gobject,
            )
            dialog.present()

    def _on_delete_objective_dialog_response(
        self, dialog, response, quest, objective_gobject
    ):
        """Handles the response from the delete objective dialog."""
        if response == "delete":
            self.project_manager.remove_objective_from_quest(
                quest.id, objective_gobject.objective.id
            )
            is_found, pos = self.objective_model.find(objective_gobject)
            if is_found:
                self.objective_model.remove(pos)
        dialog.destroy()
