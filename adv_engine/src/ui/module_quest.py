import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw
from ..core.data_schemas import Quest, QuestGObject, Objective, ObjectiveGObject

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

        delete_button = Gtk.Button(label="Delete Quest")
        delete_button.connect("clicked", self._on_delete_quest)
        button_box.append(delete_button)
        self.quest_details.append(button_box)

        obj_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        add_obj_button = Gtk.Button(label="Add Objective")
        add_obj_button.connect("clicked", self._on_add_objective, quest)
        obj_button_box.append(add_obj_button)

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
        # You would typically open a dialog here to get the new quest's details
        new_quest = self.project_manager.add_quest(id=f"quest_{len(self.model) + 1}", name="New Quest")
        self.model.append(QuestGObject(new_quest))

    def _on_delete_quest(self, button):
        selected_quest_gobject = self.selection.get_selected_item()
        if selected_quest_gobject:
            self.project_manager.remove_quest(selected_quest_gobject.id)
            for i, item in enumerate(self.model):
                if item.id == selected_quest_gobject.id:
                    self.model.remove(i)
                    break

    def _on_add_objective(self, button, quest):
        # You would typically open a dialog here to get the new objective's details
        new_objective = self.project_manager.add_objective_to_quest(quest.id, f"obj_{len(self.objective_model) + 1}", "New Objective")
        self.objective_model.append(ObjectiveGObject(new_objective))

    def _on_delete_objective(self, button, quest):
        selected_objective_gobject = self.objective_selection.get_selected_item()
        if selected_objective_gobject:
            self.project_manager.remove_objective_from_quest(quest.id, selected_objective_gobject.id)
            for i, item in enumerate(self.objective_model):
                if item.id == selected_objective_gobject.id:
                    self.objective_model.remove(i)
                    break

    def _clear_quest_details(self):
        for child in self.quest_details.observe_children():
            self.quest_details.remove(child)
