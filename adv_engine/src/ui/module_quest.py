import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from ..core.data_schemas import Quest, QuestGObject, QuestStep

class QuestEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, quest=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Quest" if quest is None else "Edit Quest")

        self.quest = quest

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        self.id_entry = Gtk.Entry(text=quest.id if quest else "")
        self.name_entry = Gtk.Entry(text=quest.name if quest else "")
        self.description_entry = Gtk.TextView()
        if quest and quest.description:
            self.description_entry.get_buffer().set_text(quest.description)

        content.append(self._create_row("ID:", self.id_entry))
        content.append(self._create_row("Name:", self.name_entry))

        desc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        desc_box.append(Gtk.Label(label="Description:", halign=Gtk.Align.START))
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.description_entry)
        scrolled_window.set_size_request(-1, 100)
        desc_box.append(scrolled_window)
        content.append(desc_box)

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        # --- Quest Steps ---
        steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        steps_label = Gtk.Label(label="Quest Steps", halign=Gtk.Align.START, css_classes=["title-4"])
        steps_box.append(steps_label)

        self.steps_model = Gio.ListStore(item_type=QuestStep)
        if quest:
            for step in quest.steps:
                self.steps_model.append(step)

        self.steps_view = Gtk.ColumnView()
        self.steps_view.set_model(Gtk.SingleSelection(model=self.steps_model))
        self.steps_view.set_size_request(-1, 200)

        self._create_step_column("ID", lambda step: step.id)
        self._create_step_column("Description", lambda step: step.description)
        self._create_step_column("Logic Graph ID", lambda step: step.completion_logic_graph_id or "")

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.steps_view)
        steps_box.append(scrolled_window)

        steps_toolbar = Gtk.Box(spacing=5)
        add_step_button = Gtk.Button(label="Add Step")
        add_step_button.connect("clicked", self._on_add_step_clicked)
        edit_step_button = Gtk.Button(label="Edit Step")
        edit_step_button.connect("clicked", self._on_edit_step_clicked)
        remove_step_button = Gtk.Button(label="Remove Step")
        remove_step_button.connect("clicked", self._on_remove_step_clicked)
        steps_toolbar.append(add_step_button)
        steps_toolbar.append(edit_step_button)
        steps_toolbar.append(remove_step_button)
        steps_box.append(steps_toolbar)

        content.append(steps_box)

    def _create_step_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.steps_view.append_column(col)

    def _on_add_step_clicked(self, button):
        # In a real implementation, this would open a dialog to edit the new step
        step_id = f"step_{self.steps_model.get_n_items() + 1}"
        new_step = QuestStep(id=step_id, description="New step")
        self.steps_model.append(new_step)

    def _on_edit_step_clicked(self, button):
        # In a real implementation, this would open a dialog to edit the selected step
        pass

    def _on_remove_step_clicked(self, button):
        selected_item = self.steps_view.get_model().get_selected_item()
        if selected_item:
            pos = self.steps_view.get_model().get_selected()
            self.steps_model.remove(pos)


    def _create_row(self, label_text, widget):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text, halign=Gtk.Align.START, hexpand=True)
        box.append(label)
        box.append(widget)
        return box

class QuestEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True, vexpand=True)
        self.append(self.main_box)

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title = Gtk.Label(label="Quest Editor", halign=Gtk.Align.START, hexpand=True,
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

        self.model = Gio.ListStore(item_type=QuestGObject)
        for quest in self.project_manager.data.quests:
            self.model.append(QuestGObject(quest))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

        self._create_column("ID", lambda item: item.id)
        self._create_column("Name", lambda item: item.name)
        self._create_column("Description", lambda item: item.description)

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
        dialog = QuestEditorDialog(self.get_root())
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            new_quest = Quest(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text(),
                description=dialog.description_entry.get_buffer().get_text(
                    dialog.description_entry.get_buffer().get_start_iter(),
                    dialog.description_entry.get_buffer().get_end_iter(),
                    False
                )
            )
            self.project_manager.add_quest(new_quest)
            self.model.append(QuestGObject(new_quest))
            new_quest.steps = [step for step in dialog.steps_model]
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if selected_item:
            dialog = QuestEditorDialog(self.get_root(), quest=selected_item.quest_data)
            dialog.connect("response", self._on_edit_dialog_response, selected_item)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, quest_gobject):
        if response == "ok":
            quest_gobject.quest_data.id = dialog.id_entry.get_text()
            quest_gobject.quest_data.name = dialog.name_entry.get_text()
            quest_gobject.quest_data.description = dialog.description_entry.get_buffer().get_text(
                dialog.description_entry.get_buffer().get_start_iter(),
                dialog.description_entry.get_buffer().get_end_iter(),
                False
            )
            quest_gobject.quest_data.steps = [step for step in dialog.steps_model]
            self.project_manager.set_dirty(True)
            pos = self.model.find(quest_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)

        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_item = self.selection.get_selected_item()
        if selected_item:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Quest?",
                body=f"Are you sure you want to delete the quest '{selected_item.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, selected_item)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, quest_gobject):
        if response == "delete":
            self.project_manager.remove_quest(quest_gobject.quest_data)
            pos = self.model.find(quest_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
