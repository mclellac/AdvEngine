"""The cutscene editor for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio
from ..core.data_schemas import Cutscene, CutsceneAction, CutsceneGObject


class CutsceneActionGObject(GObject.Object):
    """GObject wrapper for the CutsceneAction dataclass."""
    __gtype_name__ = "CutsceneActionGObject"
    command = GObject.Property(type=str)
    parameters = GObject.Property(type=str)

    def __init__(self, action: CutsceneAction):
        """Initializes a new CutsceneActionGObject instance."""
        super().__init__()
        self.action_data = action
        self.command = action.command
        self.parameters = " ".join(action.parameters)


class CutsceneEditor(Adw.Bin):
    """A widget for editing cutscenes.

    This editor provides a list of cutscenes, a text editor for the cutscene
    script, and a view of the parsed actions.
    """
    EDITOR_NAME = "Cutscenes"
    VIEW_NAME = "cutscene_editor"
    ORDER = 4

    def __init__(self, project_manager, **kwargs):
        """Initializes a new CutsceneEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager

        root_widget = self._build_ui()
        self.set_child(root_widget)

        self._update_visibility()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        root_box = Gtk.Box()
        paned = Adw.OverlaySplitView()
        paned.set_sidebar(self._create_cutscene_list_panel())
        paned.set_content(self._create_editor_panel())
        root_box.append(paned)
        return root_box

    def _create_cutscene_list_panel(self):
        """Creates the panel with the list of cutscenes."""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        header = Adw.HeaderBar()
        panel.append(header)

        add_button = Gtk.Button(icon_name="list-add-symbolic")
        add_button.connect("clicked", self._on_add_cutscene)
        header.pack_start(add_button)

        self.delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self._on_delete_cutscene)
        header.pack_end(self.delete_button)

        self.cutscene_store = Gio.ListStore(item_type=CutsceneGObject)
        for cs in self.project_manager.data.cutscenes:
            self.cutscene_store.append(CutsceneGObject(cs))

        factory = Gtk.SignalListItemFactory()
        factory.connect(
            "setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect(
            "bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().name))

        self.cutscene_list_view = Gtk.ListView(
            model=Gtk.SingleSelection(model=self.cutscene_store), factory=factory)
        self.cutscene_list_view.get_model().connect(
            "selection-changed", self._on_cutscene_selected)

        scrolled = Gtk.ScrolledWindow(child=self.cutscene_list_view)
        scrolled.set_vexpand(True)
        panel.append(scrolled)
        return panel

    def _create_editor_panel(self):
        """Creates the panel for editing the cutscene script."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)

        main_box.append(
            Gtk.Label(label="Cutscene Script", halign=Gtk.Align.START))

        script_view_scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.script_view = Gtk.TextView()
        script_view_scrolled.set_child(self.script_view)
        main_box.append(script_view_scrolled)

        parse_button = Gtk.Button(label="Parse Script")
        parse_button.connect("clicked", self._on_parse_script)
        main_box.append(parse_button)

        main_box.append(
            Gtk.Label(label="Parsed Actions", halign=Gtk.Align.START))

        self.action_store = Gio.ListStore(item_type=CutsceneActionGObject)
        self.action_view = self._setup_action_view()
        action_scrolled = Gtk.ScrolledWindow(
            child=self.action_view, vexpand=True)

        self.status_page = Adw.StatusPage(
            title="No Cutscenes", icon_name="video-x-generic-symbolic")

        self.editor_stack = Gtk.Stack()
        self.editor_stack.add_named(action_scrolled, "actions")
        self.editor_stack.add_named(self.status_page, "status")
        main_box.append(self.editor_stack)

        return main_box

    def _setup_action_view(self):
        """Sets up the view for the parsed actions."""
        action_view = Gtk.ColumnView(
            model=Gtk.SingleSelection(model=self.action_store))

        cmd_factory = Gtk.SignalListItemFactory()
        cmd_factory.connect(
            "setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        cmd_factory.connect(
            "bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().command))
        cmd_col = Gtk.ColumnViewColumn(title="Command", factory=cmd_factory)
        action_view.append_column(cmd_col)

        param_factory = Gtk.SignalListItemFactory()
        param_factory.connect(
            "setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        param_factory.connect(
            "bind", lambda _, list_item: list_item.get_child().set_label(list_item.get_item().parameters))
        param_col = Gtk.ColumnViewColumn(
            title="Parameters", factory=param_factory)
        action_view.append_column(param_col)

        return action_view

    def _update_visibility(self):
        """Updates the visibility of the action view and status page."""
        has_cutscenes = self.cutscene_store.get_n_items() > 0
        if has_cutscenes:
            self.editor_stack.set_visible_child_name("actions")
        else:
            self.editor_stack.set_visible_child_name("status")

    def _on_cutscene_selected(self, selection_model, position, n_items):
        """Handles the selection-changed signal from the cutscene list."""
        selected_item = selection_model.get_selected_item()
        if selected_item:
            self.script_view.get_buffer().set_text(
                selected_item.cutscene_data.script)
            self._update_action_list(selected_item.cutscene_data)
            self.delete_button.set_sensitive(True)
        else:
            self.script_view.get_buffer().set_text("")
            self.action_store.clear()
            self.delete_button.set_sensitive(False)
        self._update_visibility()

    def _on_add_cutscene(self, button):
        """Handles the clicked signal from the add button."""
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(), modal=True, heading="Create New Cutscene")
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

    def _on_delete_cutscene(self, button):
        """Handles the clicked signal from the delete button."""
        selection = self.cutscene_list_view.get_model()
        selected_item = selection.get_selected_item()
        if selected_item:
            self.project_manager.remove_cutscene(selected_item.id)
            pos = selection.get_selected()
            self.cutscene_store.remove(pos)

    def _on_parse_script(self, button):
        """Handles the clicked signal from the parse button."""
        selection = self.cutscene_list_view.get_model()
        selected_item = selection.get_selected_item()
        if not selected_item:
            return

        buffer = self.script_view.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        script_text = buffer.get_text(start_iter, end_iter, False)
        selected_item.cutscene_data.script = script_text

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
        self._update_action_list(selected_item.cutscene_data)

    def _update_action_list(self, cutscene):
        """Updates the list of parsed actions."""
        self.action_store.remove_all()
        for action in cutscene.actions:
            self.action_store.append(CutsceneActionGObject(action))
