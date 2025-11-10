"""The quest editor for the AdvEngine application.

This module defines the QuestEditor, a widget for managing the game's quests
and their objectives.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.schemas.quest import Quest, QuestGObject, Objective, ObjectiveGObject


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_quest.ui"))
class QuestEditor(Adw.Bin):
    """A widget for creating, editing, and deleting quests.

    This editor uses a master-detail layout, with a list of all quests on the
    left and a detailed view of the selected quest on the right. The detail
    view includes the quest's properties and a list of its objectives.

    Attributes:
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        model (Gio.ListStore): The data store for the quest list.
        selection (Gtk.SingleSelection): The selection model for the quest
            list.
    """

    __gtype_name__ = "QuestEditor"

    EDITOR_NAME = "Quests"
    VIEW_NAME = "quest_editor"
    ORDER = 9

    add_quest_button: Gtk.Button = Gtk.Template.Child()
    delete_quest_button: Gtk.Button = Gtk.Template.Child()
    quest_list_view: Gtk.ListView = Gtk.Template.Child()
    quest_details_panel: Gtk.Box = Gtk.Template.Child()
    status_page: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, project_manager, settings_manager, **kwargs):
        """Initializes a new QuestEditor instance.

        Args:
            project_manager: The project manager instance.
            settings_manager: The settings manager instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.project_manager.register_project_loaded_callback(self.refresh_model)

        self._setup_quest_list()
        self._connect_signals()
        self.refresh_model()

    def refresh_model(self, *args):
        """Refreshes the data model from the project manager."""
        self.model.remove_all()
        for quest in self.project_manager.data.quests:
            self.model.append(QuestGObject(quest))
        self._update_visibility()

    def _setup_quest_list(self):
        """Sets up the quest list and its underlying models."""
        self.model = Gio.ListStore(item_type=QuestGObject)
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
        """Connects widget signals to their corresponding handlers."""
        self.add_quest_button.connect("clicked", self._on_add_quest)
        self.delete_quest_button.connect("clicked", self._on_delete_quest)
        self.selection.connect("selection-changed", self._on_quest_selected)

    def _bind_quest_list_item(self, factory, list_item):
        """Binds a quest list item to the data model.

        Args:
            factory (Gtk.SignalListItemFactory): The factory that emitted the
                signal.
            list_item (Gtk.ListItem): The list item to bind.
        """
        label = list_item.get_child()
        quest_gobject = list_item.get_item()
        label.set_text(quest_gobject.name)
        quest_gobject.bind_property(
            "name", label, "label", GObject.BindingFlags.BIDIRECTIONAL
        )

    def _update_visibility(self):
        """Updates the visibility of the quest list vs. the status page."""
        has_quests = self.model.get_n_items() > 0
        is_quest_selected = self.selection.get_selected() != Gtk.INVALID_LIST_POSITION
        self.status_page.set_visible(not has_quests or not is_quest_selected)

    def _on_quest_selected(self, selection, _):
        """Handles selection changes in the quest list.

        Args:
            selection (Gtk.SingleSelection): The selection model.
            _: Unused parameter.
        """
        selected_quest_gobject = selection.get_selected_item()
        self.delete_quest_button.set_sensitive(selected_quest_gobject is not None)
        self._display_quest_details(
            selected_quest_gobject.quest if selected_quest_gobject else None
        )
        self._update_visibility()

    def _display_quest_details(self, quest: Quest):
        """Displays the details of the selected quest in the properties panel.

        Args:
            quest (Quest): The quest to display.
        """
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

    def _setup_objective_list(self, quest: Quest) -> Gtk.ColumnView:
        """Sets up the list of objectives for the selected quest.

        Args:
            quest (Quest): The quest whose objectives are to be displayed.

        Returns:
            Gtk.ColumnView: The configured column view for the objectives.
        """
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
        """Creates a column for the objective list.

        Args:
            objective_list (Gtk.ColumnView): The view to add the column to.
            title (str): The title of the column.
            col_id (str): The ID of the property to display in the column.
        """
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_objective_cell)
        factory.connect("bind", self._bind_objective_cell, col_id)
        factory.connect("unbind", self._unbind_objective_cell)
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        objective_list.append_column(col)

    def _setup_objective_cell(self, factory, list_item):
        """Sets up a cell for the objective list.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to set up.
        """
        widget = Gtk.Entry()
        list_item.set_child(widget)

    def _bind_objective_cell(self, factory, list_item, column_id):
        """Binds a cell for the objective list.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to bind.
            column_id (str): The ID of the property to bind.
        """
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
        """Unbinds a cell for the objective list.

        Args:
            factory (Gtk.SignalListItemFactory): The factory.
            list_item (Gtk.ListItem): The list item to unbind.
        """
        if hasattr(list_item, "binding"):
            list_item.binding.unbind()
            del list_item.binding
        if hasattr(list_item, "handler_id"):
            list_item.get_child().disconnect(list_item.handler_id)
            del list_item.handler_id

    def _on_detail_changed(self, widget, quest, property_name):
        """Handles changes to the main quest detail entries.

        Args:
            widget (Gtk.Widget): The widget that emitted the signal.
            quest (Quest): The quest being edited.
            property_name (str): The name of the property that changed.
        """
        new_value = widget.get_text()
        original_id = quest.id

        setattr(quest, property_name, new_value)
        self.project_manager.set_dirty(True)

        for i, item in enumerate(self.model):
            if item.quest.id == original_id:
                self.model.items_changed(i, 1, 1)
                break

    def _on_add_quest(self, button):
        """Handles the 'Add Quest' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
        new_id = f"quest_{len(self.project_manager.data.quests)}"
        new_quest = Quest(id=new_id, name="New Quest")
        self.project_manager.add_data_item("quests", new_quest)
        self.model.append(QuestGObject(new_quest))
        self._update_visibility()

    def _on_delete_quest(self, button):
        """Handles the 'Delete Quest' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
        """
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
        """Handles the response from the delete quest confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog.
            response (str): The response ID.
            quest_gobject (QuestGObject): The quest to delete.
        """
        if response == "delete":
            quest_data = quest_gobject.quest
            if self.project_manager.remove_data_item("quests", quest_data):
                is_found, pos = self.model.find(quest_gobject)
                if is_found:
                    self.model.remove(pos)
            self._update_visibility()
        dialog.close()

    def _on_add_objective(self, button, quest):
        """Handles the 'Add Objective' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
            quest (Quest): The quest to add the objective to.
        """
        new_id = f"objective_{len(quest.objectives)}"
        new_objective = Objective(id=new_id, name="New Objective")
        quest.objectives.append(new_objective)
        self.project_manager.set_dirty(True)
        self.objective_model.append(ObjectiveGObject(new_objective))

    def _on_delete_objective(self, button, quest):
        """Handles the 'Delete Objective' button click event.

        Args:
            button (Gtk.Button): The button that was clicked.
            quest (Quest): The quest the objective belongs to.
        """
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
        """Handles the response from the delete objective confirmation dialog.

        Args:
            dialog (Adw.MessageDialog): The dialog.
            response (str): The response ID.
            quest (Quest): The parent quest.
            objective_gobject (ObjectiveGObject): The objective to delete.
        """
        if response == "delete":
            objective_data = objective_gobject.objective
            quest.objectives.remove(objective_data)
            self.project_manager.set_dirty(True)
            is_found, pos = self.objective_model.find(objective_gobject)
            if is_found:
                self.objective_model.remove(pos)
        dialog.close()
