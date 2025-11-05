import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio
from ..core.data_schemas import Cutscene, CutsceneAction, CutsceneGObject

class CutsceneActionGObject(GObject.Object):
    __gtype_name__ = "CutsceneActionGObject"
    command = GObject.Property(type=str)
    parameters = GObject.Property(type=str)
    def __init__(self, action: CutsceneAction):
        super().__init__()
        self.action_data = action
        self.command = action.command
        self.parameters = " ".join(action.parameters)

class CutsceneEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.project_manager = project_manager

        paned = Adw.OverlaySplitView()
        self.append(paned)

        paned.set_sidebar(self._create_cutscene_list_panel())
        paned.set_content(self._create_editor_panel())

    def _create_cutscene_list_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        header = Adw.HeaderBar()
        panel.append(header)

        add_button = Gtk.Button(icon_name="list-add-symbolic")
        add_button.connect("clicked", self.on_add_cutscene)
        header.pack_start(add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self.on_delete_cutscene)
        header.pack_end(self.delete_button)

        self.cutscene_store = Gio.ListStore(item_type=CutsceneGObject)
        for cs in self.project_manager.data.cutscenes:
            self.cutscene_store.append(CutsceneGObject(cs))

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().name))

        self.cutscene_list_view = Gtk.ListView(model=Gtk.SingleSelection(model=self.cutscene_store), factory=factory)
        self.cutscene_list_view.get_model().connect("selection-changed", self.on_cutscene_selected)

        scrolled = Gtk.ScrolledWindow(child=self.cutscene_list_view)
        scrolled.set_vexpand(True)
        panel.append(scrolled)
        return panel

    def _create_editor_panel(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)

        main_box.append(Gtk.Label(label="Cutscene Script", halign=Gtk.Align.START, css_classes=["title-3"]))

        script_view_scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.script_view = Gtk.TextView()
        script_view_scrolled.set_child(self.script_view)
        main_box.append(script_view_scrolled)

        parse_button = Gtk.Button(label="Parse Script")
        parse_button.connect("clicked", self.on_parse_script)
        main_box.append(parse_button)

        main_box.append(Gtk.Label(label="Parsed Actions", halign=Gtk.Align.START, css_classes=["title-3"]))

        self.action_store = Gio.ListStore(item_type=CutsceneActionGObject)
        self.action_view = Gtk.ColumnView(model=self.action_store)

        cmd_factory = Gtk.SignalListItemFactory()
        cmd_factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        cmd_factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().command))
        cmd_col = Gtk.ColumnViewColumn(title="Command", factory=cmd_factory)
        self.action_view.append_column(cmd_col)

        param_factory = Gtk.SignalListItemFactory()
        param_factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        param_factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().parameters))
        param_col = Gtk.ColumnViewColumn(title="Parameters", factory=param_factory)
        self.action_view.append_column(param_col)

        action_scrolled = Gtk.ScrolledWindow(child=self.action_view, vexpand=True)
        main_box.append(action_scrolled)
        return main_box

    def on_cutscene_selected(self, selection_model, position, n_items):
        selected_item = selection_model.get_selected_item()
        if selected_item:
            self.script_view.get_buffer().set_text(selected_item.cutscene_data.script)
            self.update_action_list(selected_item.cutscene_data)
            self.delete_button.set_sensitive(True)
        else:
            self.script_view.get_buffer().set_text("")
            self.action_store.clear()
            self.delete_button.set_sensitive(False)

    def on_add_cutscene(self, button):
        dialog = Adw.MessageDialog(transient_for=self.get_root(), modal=True, heading="Create New Cutscene")
        entry = Adw.EntryRow(title="Cutscene Name")
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("create", "_Create")
        def on_response(d, response):
            if response == "create":
                name = entry.get_text()
                if name:
                    new_cutscene = self.project_manager.add_cutscene(name)
                    self.cutscene_store.append(CutsceneGObject(new_cutscene))
            d.destroy()
        dialog.connect("response", on_response)
        dialog.present()

    def on_delete_cutscene(self, button):
        selection = self.cutscene_list_view.get_model()
        selected_item = selection.get_selected_item()
        if selected_item:
            self.project_manager.remove_cutscene(selected_item.id)
            pos = selection.get_selected()
            self.cutscene_store.remove(pos)

    def on_parse_script(self, button):
        selection = self.cutscene_list_view.get_model()
        selected_item = selection.get_selected_item()
        if not selected_item: return

        buffer = self.script_view.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        script_text = buffer.get_text(start_iter, end_iter, False)
        selected_item.cutscene_data.script = script_text

        actions = []
        for line in script_text.splitlines():
            if not line.strip(): continue
            parts = line.split()
            command = parts[0].upper()
            params = parts[1:]
            actions.append(CutsceneAction(command=command, parameters=params))

        selected_item.cutscene_data.actions = actions
        self.project_manager.set_dirty()
        self.update_action_list(selected_item.cutscene_data)

    def update_action_list(self, cutscene):
        self.action_store.remove_all()
        for action in cutscene.actions:
            self.action_store.append(CutsceneActionGObject(action))
