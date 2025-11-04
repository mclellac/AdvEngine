import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio
from ..core.data_schemas import Cutscene, CutsceneAction


class CutsceneGObject(GObject.Object):
    __gtype_name__ = "CutsceneGObject"
    id = GObject.Property(type=str)
    name = GObject.Property(type=str)

    def __init__(self, cutscene: Cutscene):
        super().__init__()
        self.cutscene_data = cutscene
        self.id = cutscene.id
        self.name = cutscene.name


class CutsceneEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(paned)

        # Left side: List of cutscenes
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        paned.set_start_child(left_box)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        left_box.append(toolbar)

        add_button = Gtk.Button(label="Add")
        add_button.connect("clicked", self.on_add_cutscene)
        toolbar.append(add_button)

        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self.on_delete_cutscene)
        toolbar.append(self.delete_button)

        cutscene_list_scrolled = Gtk.ScrolledWindow()
        cutscene_list_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        cutscene_list_scrolled.set_hexpand(True)
        cutscene_list_scrolled.set_vexpand(True)
        left_box.append(cutscene_list_scrolled)

        self.cutscene_store = Gio.ListStore(item_type=CutsceneGObject)
        for cs in self.project_manager.data.cutscenes:
            self.cutscene_store.append(CutsceneGObject(cs))

        factory = Gtk.SignalListItemFactory()
        factory.connect(
            "setup",
            lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)),
        )
        factory.connect(
            "bind",
            lambda _, list_item: list_item.get_child().set_label(
                list_item.get_item().name
            ),
        )

        self.cutscene_list_view = Gtk.ListView(
            model=Gtk.SingleSelection(model=self.cutscene_store), factory=factory
        )
        cutscene_list_scrolled.set_child(self.cutscene_list_view)

        # Right side: Script editor and action list
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_box.set_size_request(400, -1)
        paned.set_end_child(right_box)

        right_box.append(
            Gtk.Label(
                label="Cutscene Script", halign=Gtk.Align.START, css_classes=["title-3"]
            )
        )

        script_view_scrolled = Gtk.ScrolledWindow()
        script_view_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        script_view_scrolled.set_vexpand(True)
        right_box.append(script_view_scrolled)

        self.script_view = Gtk.TextView()
        script_view_scrolled.set_child(self.script_view)

        parse_button = Gtk.Button(label="Parse Script")
        parse_button.connect("clicked", self.on_parse_script)
        right_box.append(parse_button)

        right_box.append(
            Gtk.Label(
                label="Parsed Actions", halign=Gtk.Align.START, css_classes=["title-3"]
            )
        )

        action_list_scrolled = Gtk.ScrolledWindow()
        action_list_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        action_list_scrolled.set_vexpand(True)
        right_box.append(action_list_scrolled)

        self.action_store = Gtk.TreeStore(str, str)  # Command, Parameters
        self.action_tree_view = Gtk.TreeView(model=self.action_store)
        action_list_scrolled.set_child(self.action_tree_view)

        renderer = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn("Command", renderer, text=0)
        column2 = Gtk.TreeViewColumn("Parameters", renderer, text=1)
        self.action_tree_view.append_column(column1)
        self.action_tree_view.append_column(column2)

        self.cutscene_list_view.get_model().connect(
            "selection-changed", self.on_cutscene_selected
        )

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
        # In a real app, this would open a dialog to get a name
        new_cutscene = self.project_manager.add_cutscene("New Cutscene")
        self.cutscene_store.append(CutsceneGObject(new_cutscene))

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
        if not selected_item:
            return

        buffer = self.script_view.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        script_text = buffer.get_text(start_iter, end_iter, False)
        selected_item.cutscene_data.script = script_text

        # Simple parsing logic
        actions = []
        for line in script_text.splitlines():
            if not line.strip():
                continue
            parts = line.split()
            command = parts[0].upper()
            params = parts[1:]
            actions.append(CutsceneAction(command=command, parameters=params))

        selected_item.cutscene_data.actions = actions
        self.project_manager.set_dirty()
        self.update_action_list(selected_item.cutscene_data)

    def update_action_list(self, cutscene):
        self.action_store.clear()
        for action in cutscene.actions:
            self.action_store.append(
                None, [action.command, " ".join(action.parameters)]
            )
